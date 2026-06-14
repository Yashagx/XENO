import logging
import json
import random
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Campaign Performance Simulator.
You predict campaign outcomes using historical data and copy quality assessment.
Output ONLY valid JSON with precise numeric predictions.
"""

# Default channel benchmarks (INR market)
CHANNEL_BENCHMARKS = {
    "email": {"open_rate": 0.28, "click_rate": 0.08, "conversion_rate": 0.025},
    "sms": {"open_rate": 0.62, "click_rate": 0.09, "conversion_rate": 0.030},
    "whatsapp": {"open_rate": 0.70, "click_rate": 0.12, "conversion_rate": 0.035},
    "rcs": {"open_rate": 0.55, "click_rate": 0.10, "conversion_rate": 0.028},
}


async def run(
    campaign_id: str,
    intent: str,
    strategy: dict,
    segment: dict,
    copies: list[dict],
    db: AsyncSession
) -> tuple[dict, AgentStep]:
    """Predict campaign outcomes before execution using Time Machine."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    # Get recent historical campaigns
    result = await db.execute(
        select(Campaign)
        .where(Campaign.status == "completed")
        .order_by(desc(Campaign.completed_at))
        .limit(20)
    )
    historical = result.scalars().all()
    
    hist_data = []
    for c in historical:
        if c.actual_stats:
            hist_data.append({
                "intent_snippet": c.intent[:80] if c.intent else "",
                "channel": json.dumps(c.strategy.get("channel_allocation", {})) if c.strategy else "{}",
                "open_rate": c.actual_stats.get("open_rate", 0),
                "click_rate": c.actual_stats.get("click_rate", 0),
                "conversion_rate": c.actual_stats.get("conversion_rate", 0),
                "roi": c.actual_stats.get("roi", 0),
            })
    
    # Compute weighted channel benchmarks
    alloc = strategy.get("channel_allocation", {"email": 1.0})
    weighted_open = sum(
        CHANNEL_BENCHMARKS.get(ch, CHANNEL_BENCHMARKS["email"])["open_rate"] * weight
        for ch, weight in alloc.items()
    )
    weighted_click = sum(
        CHANNEL_BENCHMARKS.get(ch, CHANNEL_BENCHMARKS["email"])["click_rate"] * weight
        for ch, weight in alloc.items()
    )
    weighted_conv = sum(
        CHANNEL_BENCHMARKS.get(ch, CHANNEL_BENCHMARKS["email"])["conversion_rate"] * weight
        for ch, weight in alloc.items()
    )
    
    prompt = f"""
Campaign intent: "{intent}"
Channel mix: {json.dumps(alloc)}
Segment size: {segment['customer_count']} customers
Avg spend per customer: ₹{sum(c.get('total_spend', 0) for c in segment.get('customers', [])[:100]) / max(len(segment.get('customers', [])), 1):.2f}

Channel benchmarks for this mix:
- Weighted open rate benchmark: {weighted_open:.3f}
- Weighted click rate benchmark: {weighted_click:.3f}
- Weighted conversion rate benchmark: {weighted_conv:.3f}

Historical similar campaigns: {json.dumps(hist_data[:5], indent=2) if hist_data else 'None yet (first campaigns)'}

Number of message copies: {len(copies)}
Copy quality indicators: {len(copies)} variants across {len(set(c.get('persona_name') for c in copies))} personas

Simulate campaign outcomes. Output JSON:
{{
  "open_rate": {{"p10": <float>, "p50": <float>, "p90": <float>}},
  "click_rate": {{"p10": <float>, "p50": <float>, "p90": <float>}},
  "conversion_rate": {{"p10": <float>, "p50": <float>, "p90": <float>}},
  "revenue_inr": {{"p10": <float>, "p50": <float>, "p90": <float>}},
  "roi": <float>,
  "confidence": <float 0-1>,
  "confidence_reason": "<why this confidence level>",
  "copy_quality_score": <float 0-1>,
  "alternatives": [
    {{
      "strategy": "<alternative approach>",
      "predicted_uplift_pct": <float>,
      "tradeoff": "<what's the cost or risk>"
    }}
  ]
}}
"""
    
    result_llm = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.2)
    
    # Apply segment size multiplier to revenue
    n = segment['customer_count']
    avg_order = 1500  # INR average order value estimate
    
    sim = {
        "open_rate": result_llm.get("open_rate", {"p10": 0.20, "p50": 0.30, "p90": 0.40}),
        "click_rate": result_llm.get("click_rate", {"p10": 0.06, "p50": 0.09, "p90": 0.14}),
        "conversion_rate": result_llm.get("conversion_rate", {"p10": 0.02, "p50": 0.03, "p90": 0.05}),
        "revenue_inr": result_llm.get("revenue_inr", {
            "p10": n * 0.02 * avg_order,
            "p50": n * 0.03 * avg_order,
            "p90": n * 0.05 * avg_order
        }),
        "roi": result_llm.get("roi", 4.5),
        "confidence": result_llm.get("confidence", 0.65),
        "confidence_reason": result_llm.get("confidence_reason", "Based on channel benchmarks"),
        "copy_quality_score": result_llm.get("copy_quality_score", 0.75),
        "alternatives": result_llm.get("alternatives", []),
        "segment_size": n,
        "channel_mix": alloc,
    }
    
    step = AgentStep(
        agent_id="simulator_agent",
        agent_name="Campaign Simulator (Time Machine)",
        status="completed",
        input_summary=f"Segment: {n} customers, channels: {list(alloc.keys())}",
        output_summary=f"Predicted open rate: {sim['open_rate']['p50']:.1%}, conversion: {sim['conversion_rate']['p50']:.1%}, ROI: {sim['roi']:.1f}x, confidence: {sim['confidence']:.0%}",
        reasoning=result_llm.get("confidence_reason", ""),
        confidence=sim['confidence'],
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return sim, step
