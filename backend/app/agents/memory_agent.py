import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer, CustomerTwin
from app.agents.llm_client import call_llm, embed_text
from app.agents.state import CustomerSummary, AgentStep

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are Xeno Oracle's Customer Memory Retrieval Agent.
Given a marketer's intent, determine the optimal SQL filter strategy to retrieve relevant customers.
Output ONLY valid JSON.
"""


async def run(campaign_id: str, intent: str, db: AsyncSession) -> tuple[list[dict], AgentStep]:
    """Retrieve relevant customer memory objects for a given intent."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    try:
        # Ask LLM for retrieval strategy
        strategy_prompt = f"""
Marketer intent: "{intent}"

Determine SQL filter strategy. Output JSON:
{{
  "max_recency_days": <int or null, days since last order>,
  "min_total_spend": <float or null>,
  "max_churn_probability": <float or null>,
  "min_churn_probability": <float or null>,
  "min_order_count": <int or null>,
  "max_results": <int, 50-500>,
  "reasoning": "<why these filters>"
}}
"""
        strategy = await call_llm(strategy_prompt, SYSTEM_PROMPT)
        
        # Build query
        query = select(Customer, CustomerTwin).join(
            CustomerTwin, Customer.id == CustomerTwin.customer_id, isouter=True
        )
        
        filters = []
        if strategy.get("max_recency_days"):
            cutoff = datetime.utcnow()
            from datetime import timedelta
            cutoff = cutoff.replace(tzinfo=None)
            # filter customers whose last order is older than recency days
            cutoff_date = datetime.utcnow().replace(tzinfo=None)
            import datetime as dt
            days = strategy["max_recency_days"]
            # customers with last_order older than N days
            # We want customers who haven't ordered in N days
            from sqlalchemy import or_
            from datetime import timedelta
            cutoff_dt = datetime.utcnow() - timedelta(days=days)
            filters.append(
                or_(
                    Customer.last_order_at < cutoff_dt,
                    Customer.last_order_at.is_(None)
                )
            )
        
        if strategy.get("min_total_spend"):
            filters.append(Customer.total_spend >= strategy["min_total_spend"])
        
        if strategy.get("min_order_count"):
            filters.append(Customer.order_count >= strategy["min_order_count"])
        
        if filters:
            query = query.where(and_(*filters))
        
        max_results = min(strategy.get("max_results", 200), 500)
        query = query.limit(max_results)
        
        result = await db.execute(query)
        rows = result.all()
        
        customers = []
        now = datetime.utcnow()
        for row in rows:
            customer, twin = row[0], row[1]
            last_order_days = 0
            if customer.last_order_at:
                lo = customer.last_order_at.replace(tzinfo=None) if customer.last_order_at.tzinfo else customer.last_order_at
                last_order_days = (now - lo).days
            
            c_dict = {
                "id": str(customer.id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "city": customer.city,
                "total_spend": customer.total_spend,
                "order_count": customer.order_count,
                "last_order_days": last_order_days,
                "churn_probability": twin.churn_probability if twin else 0.5,
                "channel_affinity": twin.channel_affinity if twin else {},
                "category_affinity": twin.category_affinity if twin else {},
                "narrative": twin.narrative_summary if twin else "",
                "communication_style": twin.communication_style if twin else "casual",
                "price_sensitivity": twin.price_sensitivity if twin else 0.5,
                "urgency_responsiveness": twin.urgency_responsiveness if twin else 0.5,
                "purchase_intent_score": twin.purchase_intent_score if twin else 0.5,
                "predicted_ltv_90d": twin.predicted_ltv_90d if twin else 0.0,
            }
            customers.append(c_dict)
        
        step = AgentStep(
            agent_id="memory_agent",
            agent_name="Customer Memory Agent",
            status="completed",
            input_summary=f"Intent: {intent[:100]}",
            output_summary=f"Retrieved {len(customers)} customers using filters: {strategy.get('reasoning', 'N/A')[:200]}",
            reasoning=strategy.get("reasoning", ""),
            confidence=min(1.0, len(customers) / 100),
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
        
        return customers, step
    
    except Exception as e:
        logger.error(f"Memory agent error: {e}")
        # Fallback: return all customers up to 200
        result = await db.execute(select(Customer, CustomerTwin).join(CustomerTwin, isouter=True).limit(200))
        rows = result.all()
        customers = []
        now = datetime.utcnow()
        for row in rows:
            customer, twin = row[0], row[1]
            last_order_days = 0
            if customer.last_order_at:
                lo = customer.last_order_at.replace(tzinfo=None) if customer.last_order_at.tzinfo else customer.last_order_at
                last_order_days = (now - lo).days
            customers.append({
                "id": str(customer.id),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone or "",
                "city": customer.city or "",
                "total_spend": customer.total_spend,
                "order_count": customer.order_count,
                "last_order_days": last_order_days,
                "churn_probability": twin.churn_probability if twin else 0.5,
                "channel_affinity": twin.channel_affinity if twin else {},
                "category_affinity": twin.category_affinity if twin else {},
                "narrative": twin.narrative_summary if twin else "",
                "communication_style": twin.communication_style if twin else "casual",
                "price_sensitivity": twin.price_sensitivity if twin else 0.5,
                "urgency_responsiveness": twin.urgency_responsiveness if twin else 0.5,
                "purchase_intent_score": twin.purchase_intent_score if twin else 0.5,
                "predicted_ltv_90d": twin.predicted_ltv_90d if twin else 0.0,
            })
        
        step = AgentStep(
            agent_id="memory_agent",
            agent_name="Customer Memory Agent",
            status="completed",
            input_summary=intent[:100],
            output_summary=f"Fallback retrieval: {len(customers)} customers",
            reasoning=f"Error in LLM strategy, used fallback: {str(e)}",
            confidence=0.4,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
        return customers, step
