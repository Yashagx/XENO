import logging
import json
from datetime import datetime, timezone
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Segmentation Intelligence Agent. Your role is to analyse customer data
and construct precise, explainable audience segments for marketing campaigns.

Constraints:
1. Every inclusion/exclusion decision must have a cited reason
2. Segment size must be between 10 and 10,000 customers
3. You must identify and flag data quality issues
4. Output ONLY valid JSON conforming exactly to the specified schema
"""


async def run(campaign_id: str, intent: str, customers: list[dict]) -> tuple[dict, AgentStep]:
    """Build a precise, named, explainable segment from retrieved customers."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    # Compute stats
    total = len(customers)
    avg_spend = sum(c["total_spend"] for c in customers) / max(total, 1)
    avg_recency = sum(c["last_order_days"] for c in customers) / max(total, 1)
    high_churn = sum(1 for c in customers if c["churn_probability"] > 0.6)
    
    stats = {
        "total_retrieved": total,
        "avg_total_spend": round(avg_spend, 2),
        "avg_last_order_days": round(avg_recency, 1),
        "high_churn_count": high_churn,
        "cities": list(set(c.get("city", "") for c in customers[:50])),
    }
    
    # Sample 20 customers for LLM context
    sample = customers[:20]
    sample_text = json.dumps([
        {"id": c["id"], "spend": c["total_spend"], "orders": c["order_count"],
         "recency_days": c["last_order_days"], "churn": c["churn_probability"],
         "style": c["communication_style"]}
        for c in sample
    ], indent=2)
    
    prompt = f"""
Marketer intent: "{intent}"

Customer pool stats: {json.dumps(stats, indent=2)}

Sample customers (first 20):
{sample_text}

Build an optimal segment. Output JSON:
{{
  "segment_name": "<memorable marketer-friendly name>",
  "description": "<2-3 sentences about who this segment is>",
  "inclusion_criteria": {{"field": "condition description"}},
  "exclusion_criteria": {{"field": "condition description"}},
  "qualifying_customer_ids": ["<id1>", "<id2>", "..."],
  "estimated_size": <int>,
  "performance_baseline": {{"open_rate": <float>, "click_rate": <float>, "conversion_rate": <float>}},
  "confidence": <float 0-1>,
  "reasoning": "<detailed explanation>"
}}

IMPORTANT: qualifying_customer_ids must be a subset of these IDs: {json.dumps([c['id'] for c in customers])}
Include ALL customers that match the intent criteria.
"""
    
    result = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.3)
    
    # Validate and fill in qualifying customers
    qualifying_ids = result.get("qualifying_customer_ids", [])
    # If LLM returned empty or too few, include all customers
    if len(qualifying_ids) < 10:
        qualifying_ids = [c["id"] for c in customers]
    
    segment = {
        "name": result.get("segment_name", f"Segment from: {intent[:50]}"),
        "description": result.get("description", ""),
        "inclusion_criteria": result.get("inclusion_criteria", {}),
        "exclusion_criteria": result.get("exclusion_criteria", {}),
        "customer_ids": qualifying_ids,
        "customer_count": len(qualifying_ids),
        "performance_baseline": result.get("performance_baseline", {
            "open_rate": 0.28, "click_rate": 0.08, "conversion_rate": 0.03
        }),
        "confidence": result.get("confidence", 0.7),
        "reasoning": result.get("reasoning", ""),
        "customers": [c for c in customers if c["id"] in set(qualifying_ids)]
    }
    
    step = AgentStep(
        agent_id="segmentation_agent",
        agent_name="Segmentation Agent",
        status="completed",
        input_summary=f"{total} customers retrieved for intent: {intent[:80]}",
        output_summary=f"Segment '{segment['name']}' with {segment['customer_count']} customers",
        reasoning=result.get("reasoning", ""),
        confidence=result.get("confidence", 0.7),
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return segment, step
