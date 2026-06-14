import logging
import json
from datetime import datetime, timezone
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Insight Agent. You generate actionable marketing intelligence from campaign data.

You speak to marketing teams, not data scientists. Use plain language.
Never say: 'statistically significant', 'p-value', 'regression'
Always say: 'worked better than expected', 'customers in this segment responded 2x better'

Output ONLY valid JSON.
"""


async def run(
    campaign_id: str,
    intent: str,
    simulation: dict,
    actual_stats: dict,
    segment: dict,
    personas: list[dict]
) -> tuple[dict, AgentStep]:
    """Generate natural-language insights from campaign results."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    predicted = {
        "open_rate": simulation.get("open_rate", {}).get("p50", 0),
        "click_rate": simulation.get("click_rate", {}).get("p50", 0),
        "conversion_rate": simulation.get("conversion_rate", {}).get("p50", 0),
        "revenue_p50": simulation.get("revenue_inr", {}).get("p50", 0),
        "roi": simulation.get("roi", 0),
    }
    
    actual = {
        "open_rate": actual_stats.get("open_rate", 0),
        "click_rate": actual_stats.get("click_rate", 0),
        "conversion_rate": actual_stats.get("conversion_rate", 0),
        "total_sent": actual_stats.get("total_sent", 0),
        "converted": actual_stats.get("converted", 0),
        "roi": actual_stats.get("roi", 0),
    }
    
    personas_summary = [
        {"name": p["name"], "size": p["customer_count"], "channel": p["preferred_channel"]}
        for p in personas
    ]
    
    prompt = f"""
Campaign goal: "{intent}"
Segment: {segment['name']} ({segment['customer_count']} customers)

PREDICTED (Time Machine):
{json.dumps(predicted, indent=2)}

ACTUAL RESULTS:
{json.dumps(actual, indent=2)}

Personas in this campaign:
{json.dumps(personas_summary, indent=2)}

Generate insights. Output JSON:
{{
  "key_insights": [
    "<insight 1 — plain English, specific numbers>",
    "<insight 2>",
    "<insight 3>"
  ],
  "prediction_accuracy": {{
    "overall": "<good/fair/poor>",
    "open_rate_accuracy": "<over/under/accurate> by X%",
    "conversion_accuracy": "<over/under/accurate> by X%",
    "summary": "<1-2 sentences on prediction quality>"
  }},
  "next_campaign_recommendations": [
    "<recommendation 1 — specific and actionable>",
    "<recommendation 2>",
    "<recommendation 3>"
  ],
  "anomalies": ["<anything unexpected, or empty list>"],
  "executive_summary": "<1 sentence that a CEO would read>",
  "winning_element": "<what single thing worked best>",
  "improvement_area": "<single biggest area to improve next time>"
}}
"""
    
    result = await call_llm(prompt, SYSTEM_PROMPT, temperature=0.5)
    
    insight = {
        "key_insights": result.get("key_insights", ["Campaign completed successfully."]),
        "prediction_accuracy": result.get("prediction_accuracy", {}),
        "next_campaign_recommendations": result.get("next_campaign_recommendations", []),
        "anomalies": result.get("anomalies", []),
        "executive_summary": result.get("executive_summary", ""),
        "winning_element": result.get("winning_element", ""),
        "improvement_area": result.get("improvement_area", ""),
        "actual_stats": actual,
        "predicted_stats": predicted,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    step = AgentStep(
        agent_id="insight_agent",
        agent_name="Insight Agent",
        status="completed",
        input_summary=f"Campaign: {intent[:80]}, actual open rate: {actual.get('open_rate', 0):.1%}",
        output_summary=f"{len(insight['key_insights'])} insights generated. Executive summary: {insight['executive_summary'][:100]}",
        reasoning="Compared predicted vs actual performance across all key metrics",
        confidence=0.85,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return insight, step
