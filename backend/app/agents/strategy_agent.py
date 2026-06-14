import logging
import json
from datetime import datetime, timezone
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Marketing Strategy Director.
You design optimal campaign strategies based on customer personas and historical performance.
Output ONLY valid JSON.
"""


async def run(campaign_id: str, intent: str, personas: list[dict], segment: dict) -> tuple[dict, AgentStep]:
    """Choose channel mix, timing, and campaign structure."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    personas_text = json.dumps([
        {"name": p["name"], "pct": p["pct_of_segment"],
         "channel": p["preferred_channel"], "timing": p["preferred_timing"],
         "tone": p["message_tone"], "price_sensitive": p["price_sensitive"]}
        for p in personas
    ], indent=2)
    
    now = datetime.now()
    
    prompt = f"""
Campaign goal: "{intent}"

Personas:
{personas_text}

Segment: {segment['name']} ({segment['customer_count']} customers)
Current date: {now.strftime('%Y-%m-%d %A %H:%M IST')}

Design optimal campaign strategy. Output JSON:
{{
  "channel_allocation": {{"email": <float 0-1>, "sms": <float 0-1>, "whatsapp": <float 0-1>}},
  "send_time": "<e.g. Thursday 7:00 PM IST>",
  "campaign_structure": "single_blast|drip|ab_test",
  "estimated_cost_inr": <float>,
  "rationale": "<clear explanation of why this strategy>",
  "risk_factors": ["risk1", "risk2"],
  "key_actions": ["action1", "action2", "action3"],
  "persona_channel_map": {{"<persona_name>": "<channel>"}},
  "budget_breakdown": {{"email": <cost_inr>, "sms": <cost_inr>, "whatsapp": <cost_inr>}},
  "ab_test_hypothesis": "<only if campaign_structure is ab_test>"
}}

Note: channel_allocation values must sum to 1.0. Consider Indian market timing.
"""
    
    result = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.4)
    
    strategy = {
        "channel_allocation": result.get("channel_allocation", {"email": 0.6, "sms": 0.4}),
        "send_time": result.get("send_time", "Thursday 7:00 PM IST"),
        "campaign_structure": result.get("campaign_structure", "single_blast"),
        "estimated_cost_inr": result.get("estimated_cost_inr", segment['customer_count'] * 0.5),
        "rationale": result.get("rationale", ""),
        "risk_factors": result.get("risk_factors", []),
        "key_actions": result.get("key_actions", []),
        "persona_channel_map": result.get("persona_channel_map", {}),
        "budget_breakdown": result.get("budget_breakdown", {}),
        "ab_test_hypothesis": result.get("ab_test_hypothesis", "")
    }
    
    # Normalize channel allocation
    alloc = strategy["channel_allocation"]
    total = sum(alloc.values())
    if total > 0:
        strategy["channel_allocation"] = {k: round(v/total, 3) for k, v in alloc.items()}
    
    step = AgentStep(
        agent_id="strategy_agent",
        agent_name="Strategy Agent",
        status="completed",
        input_summary=f"{len(personas)} personas, segment size {segment['customer_count']}",
        output_summary=f"Strategy: {strategy['campaign_structure']} via {strategy['channel_allocation']}, send at {strategy['send_time']}",
        reasoning=result.get("rationale", ""),
        confidence=0.78,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return strategy, step
