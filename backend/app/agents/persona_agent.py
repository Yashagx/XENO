import logging
import json
from datetime import datetime, timezone
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Customer Persona Architect.
You cluster customers into distinct, named personas for targeted marketing messaging.
Output ONLY valid JSON.
"""


async def run(campaign_id: str, segment: dict) -> tuple[list[dict], AgentStep]:
    """Cluster segment into 2-5 named personas."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    customers = segment.get("customers", [])
    total = len(customers)
    
    # Anonymized customer profiles for LLM
    profiles = [
        {
            "spend": c["total_spend"],
            "orders": c["order_count"],
            "recency_days": c["last_order_days"],
            "churn": c["churn_probability"],
            "channel_top": max(c.get("channel_affinity", {"email": 0.5}), key=c.get("channel_affinity", {"email": 0.5}).get) if c.get("channel_affinity") else "email",
            "price_sensitive": c["price_sensitivity"] > 0.6,
            "urgency_responsive": c["urgency_responsiveness"] > 0.6,
            "style": c["communication_style"]
        }
        for c in customers[:100]  # limit for context
    ]
    
    prompt = f"""
Segment: "{segment['name']}" ({total} customers)
Description: {segment['description']}

Customer profiles sample:
{json.dumps(profiles[:30], indent=2)}

Identify 3-4 distinct personas. Output JSON:
{{
  "personas": [
    {{
      "name": "<e.g. Weekend Browser, Deal Hunter, Brand Loyalist>",
      "traits": ["trait1", "trait2", "trait3"],
      "preferred_channel": "email|sms|whatsapp",
      "preferred_timing": "<e.g. Thursday 7PM, Weekend mornings>",
      "message_tone": "urgent|warm|aspirational|casual|minimal",
      "communication_style": "formal|casual|friendly|minimal",
      "pct_of_segment": <float 0-1>,
      "price_sensitive": <bool>,
      "urgency_responsive": <bool>,
      "key_motivation": "<what drives them to purchase>",
      "customer_indices": [<indices from profile list, 0-based>]
    }}
  ]
}}

Make sure pct_of_segment values sum to 1.0.
"""
    
    result = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.5)
    raw_personas = result.get("personas", [])
    
    # Map indices back to customer IDs
    personas = []
    for p in raw_personas:
        indices = p.get("customer_indices", [])
        assigned_ids = [customers[i]["id"] for i in indices if i < len(customers)]
        # If no assignments, distribute evenly
        if not assigned_ids:
            assigned_ids = [c["id"] for c in customers[:max(1, total // len(raw_personas))]]
        
        personas.append({
            "name": p.get("name", "Unknown Persona"),
            "traits": p.get("traits", []),
            "preferred_channel": p.get("preferred_channel", "email"),
            "preferred_timing": p.get("preferred_timing", "Thursday 7PM"),
            "message_tone": p.get("message_tone", "warm"),
            "communication_style": p.get("communication_style", "casual"),
            "pct_of_segment": p.get("pct_of_segment", 1.0 / len(raw_personas)),
            "price_sensitive": p.get("price_sensitive", False),
            "urgency_responsive": p.get("urgency_responsive", False),
            "key_motivation": p.get("key_motivation", ""),
            "customer_ids": assigned_ids,
            "customer_count": len(assigned_ids)
        })
    
    # Ensure all segment customers are in some persona
    assigned = set()
    for p in personas:
        assigned.update(p["customer_ids"])
    unassigned = [c["id"] for c in customers if c["id"] not in assigned]
    if unassigned and personas:
        personas[0]["customer_ids"].extend(unassigned)
        personas[0]["customer_count"] = len(personas[0]["customer_ids"])
    
    step = AgentStep(
        agent_id="persona_agent",
        agent_name="Persona Agent",
        status="completed",
        input_summary=f"Segment: {segment['name']} ({total} customers)",
        output_summary=f"Created {len(personas)} personas: {', '.join(p['name'] for p in personas)}",
        reasoning=f"Clustered {total} customers into {len(personas)} distinct behavioral groups",
        confidence=0.75,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return personas, step
