"""
XenoPilot: NL → DB query → LLM insight pipeline.
Uses same Groq client as other agents (llm_client.py).
"""
import json
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.agents.llm_client import get_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are XenoPilot, an AI data analyst for Xeno Oracle CRM.
You have access to real CRM data passed as JSON context.

Rules:
1. Only use numbers from the provided context — never invent data
2. Format currency in Indian style: ₹1.2L, ₹86.3K
3. Keep answers to 3-5 sentences unless a list is clearer
4. End with one actionable recommendation when relevant
5. If data is insufficient, say what data would help
"""


async def run_xenopilot(question: str, history: List[dict], db: AsyncSession) -> dict:
    """Main XenoPilot entry point."""
    context = await fetch_context(question, db)
    messages = [
        *history[-8:],  # last 4 turns (8 messages) to control tokens
        {
            "role": "user",
            "content": f"Question: {question}\n\nLive CRM Data:\n{json.dumps(context, default=str)}"
        }
    ]
    answer = await _call_with_history(SYSTEM_PROMPT, messages)
    actions = extract_suggested_actions(answer)
    return {
        "answer": answer,
        "data_used": list(context.keys()),
        "suggested_actions": actions
    }


async def _call_with_history(system_prompt: str, messages: list) -> str:
    """Call LLM with conversation history."""
    from app.config import settings
    try:
        client = get_client()
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=all_messages,
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"XenoPilot LLM error: {e}")
        return "I encountered an error while analyzing the data. Please try again."


async def fetch_context(question: str, db: AsyncSession) -> dict:
    """Fetch relevant CRM data based on question keywords."""
    q = question.lower()
    ctx = {}
    try:
        if any(w in q for w in ["customer", "total", "how many", "count", "all", "overview"]):
            result = await db.execute(text("""
                SELECT COUNT(*) as total,
                       ROUND(AVG(total_spend), 0) as avg_ltv,
                       SUM(CASE WHEN last_order_at < datetime('now', '-60 days') THEN 1 ELSE 0 END) as lapsed_60d,
                       COUNT(DISTINCT city) as cities
                FROM customers
            """))
            row = result.mappings().one()
            ctx["customer_stats"] = dict(row)

        if any(w in q for w in ["churn", "risk", "inactive", "lapsed", "lost", "at risk"]):
            result = await db.execute(text("""
                SELECT c.name, c.email, c.city, ROUND(c.total_spend, 0) as total_spend,
                       ROUND(t.churn_probability, 3) as churn_probability, t.narrative_summary
                FROM customers c
                JOIN customer_twins t ON c.id = t.customer_id
                ORDER BY t.churn_probability DESC LIMIT 10
            """))
            ctx["high_churn_customers"] = [dict(r) for r in result.mappings()]

        if any(w in q for w in ["campaign", "performance", "open", "click", "roi", "result", "marketing"]):
            result = await db.execute(text("""
                SELECT name, status,
                       json_extract(actual_stats, '$.open_rate') as open_rate,
                       json_extract(actual_stats, '$.click_rate') as click_rate,
                       json_extract(actual_stats, '$.roi') as roi,
                       json_extract(simulation_result, '$.roi') as predicted_roi,
                       created_at
                FROM campaigns ORDER BY created_at DESC LIMIT 10
            """))
            ctx["campaigns"] = [dict(r) for r in result.mappings()]

        if any(w in q for w in ["top", "best", "revenue", "ltv", "spend", "vip", "high value"]):
            result = await db.execute(text("""
                SELECT name, city, ROUND(total_spend, 0) as total_spend, order_count,
                       ROUND(total_spend / MAX(order_count, 1), 0) as avg_order_value
                FROM customers ORDER BY total_spend DESC LIMIT 10
            """))
            ctx["top_customers"] = [dict(r) for r in result.mappings()]

        if any(w in q for w in ["channel", "email", "sms", "whatsapp", "rcs", "message"]):
            result = await db.execute(text("""
                SELECT channel,
                       COUNT(*) as total_sent,
                       SUM(CASE WHEN status='opened' THEN 1 ELSE 0 END) as opened,
                       SUM(CASE WHEN status='clicked' THEN 1 ELSE 0 END) as clicked,
                       SUM(CASE WHEN status='converted' THEN 1 ELSE 0 END) as converted
                FROM messages GROUP BY channel
            """))
            ctx["channel_stats"] = [dict(r) for r in result.mappings()]

        if any(w in q for w in ["city", "region", "location", "mumbai", "delhi", "bangalore", "hyderabad", "pune"]):
            result = await db.execute(text("""
                SELECT city, COUNT(*) as customer_count,
                       ROUND(AVG(total_spend), 0) as avg_ltv,
                       ROUND(SUM(total_spend), 0) as total_revenue
                FROM customers GROUP BY city ORDER BY total_revenue DESC LIMIT 10
            """))
            ctx["city_stats"] = [dict(r) for r in result.mappings()]

        if not ctx:
            # Default: return customer overview
            result = await db.execute(text("""
                SELECT COUNT(*) as total_customers,
                       ROUND(AVG(total_spend), 0) as avg_spend,
                       COUNT(DISTINCT city) as cities
                FROM customers
            """))
            row = result.mappings().one()
            ctx["overview"] = dict(row)
    except Exception as e:
        logger.error(f"XenoPilot context fetch error: {e}")
        ctx["error"] = str(e)
    return ctx


def extract_suggested_actions(answer: str) -> list:
    """Extract action suggestions from AI answer."""
    actions = []
    al = answer.lower()
    if any(w in al for w in ["campaign", "reach out", "target", "send", "launch"]):
        actions.append({"label": "→ Create Campaign", "href": "/"})
    if any(w in al for w in ["customer", "twin", "profile", "persona"]):
        actions.append({"label": "→ View Twins", "href": "/twins"})
    if any(w in al for w in ["insight", "learning", "result", "analysis"]):
        actions.append({"label": "→ Learning Console", "href": "/insights"})
    return actions[:2]
