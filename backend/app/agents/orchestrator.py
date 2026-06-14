import logging
import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.agents import (
    memory_agent, segmentation_agent, persona_agent,
    strategy_agent, copywriter_agent, simulator_agent,
    execution_agent, learning_agent, insight_agent
)
from app.agents.state import CampaignState
from app.agents.llm_client import call_llm, embed_text
from app.models.campaign import Campaign, Segment, SegmentCustomer
from app.models.insight import Insight
from app.redis_client import sync_redis_client
import uuid

logger = logging.getLogger(__name__)


async def parse_intent(intent: str) -> dict:
    """Use LLM to parse marketer intent into structured filters."""
    prompt = f"""
Parse this marketing intent into structured components:
"{intent}"

Output JSON:
{{
  "goal": "<primary goal: re-engage|acquire|upsell|winback|loyalty>",
  "churn_window_days": <int or null>,
  "value_tier": "<high|medium|low|null>",
  "occasion": "<event or null>",
  "channel_preference": "<email|sms|whatsapp|null>",
  "min_ltv": <float or null>,
  "keywords": ["<keyword1>", "<keyword2>"]
}}
"""
    return await call_llm(prompt, temperature=0.2)


def publish_step(campaign_id: str, step_data: dict):
    """Publish agent step to Redis for SSE streaming."""
    try:
        channel = f"campaign:{campaign_id}:events"
        message = json.dumps({
            "type": "agent_step",
            "campaign_id": campaign_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **step_data
        })
        sync_redis_client.publish(channel, message)
        # Also store in stream for replay
        sync_redis_client.xadd(
            f"stream:campaign:{campaign_id}",
            {"data": message},
            maxlen=1000
        )
    except Exception as e:
        logger.warning(f"Failed to publish step event: {e}")


async def run_campaign_pipeline(campaign_id: str, db: AsyncSession) -> dict:
    """
    Main agent orchestrator. Runs all 10 agents sequentially.
    Publishes real-time events to Redis after each step.
    """
    logger.info(f"Starting agent pipeline for campaign {campaign_id}")

    # Load campaign
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")

    intent = campaign.intent
    state: CampaignState = {
        "campaign_id": campaign_id,
        "intent": intent,
        "parsed_intent": None,
        "customers": None,
        "segment": None,
        "personas": None,
        "strategy": None,
        "copies": None,
        "channel_assignments": None,
        "simulation": None,
        "explanation": None,
        "agent_trace": [],
        "status": "running",
        "errors": [],
        "confidence": 0.0
    }

    async def update_status(status: str):
        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(status=status)
        )
        await db.flush()

    # ─── Step 1: Parse Intent ──────────────────────────────────────────
    await update_status("segmenting")
    publish_step(campaign_id, {
        "agent": "intent_parser",
        "agent_name": "Intent Parser",
        "status": "running",
        "message": f"Parsing intent: \"{intent[:100]}...\""
    })

    parsed = await parse_intent(intent)
    state["parsed_intent"] = parsed

    publish_step(campaign_id, {
        "agent": "intent_parser",
        "agent_name": "Intent Parser",
        "status": "completed",
        "message": f"Goal: {parsed.get('goal', 'unknown')}, churn window: {parsed.get('churn_window_days', 'N/A')} days"
    })

    # ─── Step 2: Memory Agent ─────────────────────────────────────────
    publish_step(campaign_id, {
        "agent": "memory_agent",
        "agent_name": "Customer Memory Agent",
        "status": "running",
        "message": "Querying customer database with semantic + structured filters..."
    })

    customers, mem_step = await memory_agent.run(campaign_id, intent, db)
    state["customers"] = customers
    state["agent_trace"].append(vars(mem_step))

    publish_step(campaign_id, {
        "agent": "memory_agent",
        "agent_name": "Customer Memory Agent",
        "status": "completed",
        "message": mem_step.output_summary,
        "confidence": mem_step.confidence,
        "reasoning": mem_step.reasoning
    })

    # ─── Step 3: Segmentation Agent ──────────────────────────────────
    await update_status("segmenting")
    publish_step(campaign_id, {
        "agent": "segmentation_agent",
        "agent_name": "Segmentation Agent",
        "status": "running",
        "message": f"Building precise segment from {len(customers)} candidates..."
    })

    segment, seg_step = await segmentation_agent.run(campaign_id, intent, customers)
    state["segment"] = segment
    state["agent_trace"].append(vars(seg_step))

    # Persist segment to DB
    db_segment = Segment(
        name=segment["name"],
        description=segment["description"],
        filter_config=segment.get("inclusion_criteria", {}),
        customer_count=segment["customer_count"],
        created_by_intent=intent
    )
    db.add(db_segment)
    await db.flush()

    for cid in segment.get("customer_ids", []):
        sc = SegmentCustomer(
            segment_id=db_segment.id,
            customer_id=cid,
            inclusion_reason=segment.get("reasoning", "")[:500]
        )
        db.add(sc)

    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(segment_id=db_segment.id, name=f"Campaign: {segment['name'][:100]}")
    )
    await db.flush()

    publish_step(campaign_id, {
        "agent": "segmentation_agent",
        "agent_name": "Segmentation Agent",
        "status": "completed",
        "message": seg_step.output_summary,
        "confidence": seg_step.confidence,
        "reasoning": seg_step.reasoning
    })

    # ─── Step 4: Persona Agent ────────────────────────────────────────
    await update_status("strategizing")
    publish_step(campaign_id, {
        "agent": "persona_agent",
        "agent_name": "Persona Agent",
        "status": "running",
        "message": f"Clustering {segment['customer_count']} customers into behavioral personas..."
    })

    personas, per_step = await persona_agent.run(campaign_id, segment)
    state["personas"] = personas
    state["agent_trace"].append(vars(per_step))

    publish_step(campaign_id, {
        "agent": "persona_agent",
        "agent_name": "Persona Agent",
        "status": "completed",
        "message": per_step.output_summary,
        "confidence": per_step.confidence,
        "reasoning": per_step.reasoning
    })

    # ─── Step 5: Strategy Agent ───────────────────────────────────────
    publish_step(campaign_id, {
        "agent": "strategy_agent",
        "agent_name": "Strategy Agent",
        "status": "running",
        "message": "Designing channel mix, timing, and campaign structure..."
    })

    strategy, str_step = await strategy_agent.run(campaign_id, intent, personas, segment)
    state["strategy"] = strategy
    state["agent_trace"].append(vars(str_step))

    publish_step(campaign_id, {
        "agent": "strategy_agent",
        "agent_name": "Strategy Agent",
        "status": "completed",
        "message": str_step.output_summary,
        "confidence": str_step.confidence,
        "reasoning": str_step.reasoning
    })

    # ─── Step 6: Copywriter Agent ─────────────────────────────────────
    await update_status("writing")
    publish_step(campaign_id, {
        "agent": "copywriter_agent",
        "agent_name": "Copywriter Agent",
        "status": "running",
        "message": f"Writing persona-specific messages for {len(personas)} personas..."
    })

    copies, copy_step = await copywriter_agent.run(campaign_id, intent, personas, strategy)
    state["copies"] = copies
    state["agent_trace"].append(vars(copy_step))

    publish_step(campaign_id, {
        "agent": "copywriter_agent",
        "agent_name": "Copywriter Agent",
        "status": "completed",
        "message": copy_step.output_summary,
        "confidence": copy_step.confidence,
        "reasoning": copy_step.reasoning
    })

    # ─── Step 7: Simulator Agent (Time Machine) ───────────────────────
    await update_status("simulating")
    publish_step(campaign_id, {
        "agent": "simulator_agent",
        "agent_name": "Campaign Simulator (Time Machine)",
        "status": "running",
        "message": "Running pre-execution simulation with historical data..."
    })

    simulation, sim_step = await simulator_agent.run(campaign_id, intent, strategy, segment, copies, db)
    state["simulation"] = simulation
    state["agent_trace"].append(vars(sim_step))

    # Build explanation block
    explanation = {
        "recommendation": f"Launch '{segment['name']}' campaign via {list(strategy['channel_allocation'].keys())}",
        "reasoning": strategy.get("rationale", ""),
        "evidence": [
            f"Segment contains {segment['customer_count']} qualifying customers",
            f"Predicted open rate: {simulation.get('open_rate', {}).get('p50', 0):.1%}",
            f"Predicted ROI: {simulation.get('roi', 0):.1f}x",
            f"Confidence: {simulation.get('confidence', 0):.0%}",
        ],
        "confidence": simulation.get("confidence", 0.7),
        "confidence_label": "high" if simulation.get("confidence", 0) > 0.75 else "medium" if simulation.get("confidence", 0) > 0.5 else "low",
        "expected_impact": sim_step.output_summary,
        "alternative": simulation.get("alternatives", [{}])[0] if simulation.get("alternatives") else {},
        "risk_factors": strategy.get("risk_factors", []),
        "agent_id": "orchestrator"
    }
    state["explanation"] = explanation

    # Save everything to campaign
    trace_serializable = []
    for step in state["agent_trace"]:
        trace_serializable.append({k: str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v for k, v in step.items()})

    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(
            status="ready",
            strategy=strategy,
            simulation_result=simulation,
            personas=personas,
            copies=copies,
            agent_trace=trace_serializable,
            explanation=explanation
        )
    )
    await db.flush()

    # SNS: notify campaign ready (graceful-fallback, non-blocking)
    try:
        import asyncio as _asyncio
        from app.services.sns_service import notify_campaign_ready as _sns_ready
        _asyncio.create_task(_sns_ready(
            campaign_id=campaign_id,
            campaign_name=state.get("name", campaign_id),
            segment_size=segment.get("customer_count", 0),
            predicted_revenue=float(simulation.get("estimated_revenue", 0) or 0)
        ))
    except Exception:
        pass

    publish_step(campaign_id, {
        "agent": "simulator_agent",
        "agent_name": "Campaign Simulator (Time Machine)",
        "status": "completed",
        "message": sim_step.output_summary,
        "confidence": sim_step.confidence,
        "reasoning": sim_step.reasoning
    })

    publish_step(campaign_id, {
        "agent": "orchestrator",
        "agent_name": "Orchestrator",
        "status": "ready_for_approval",
        "message": f"Campaign ready for your approval. Predicted ROI: {simulation.get('roi', 0):.1f}x with {simulation.get('confidence', 0):.0%} confidence."
    })

    logger.info(f"Pipeline complete for campaign {campaign_id}. Status: ready")
    return state


async def execute_campaign(campaign_id: str, db: AsyncSession):
    """Execute an approved campaign by dispatching to Channel Service."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")

    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="executing", executed_at=datetime.now(timezone.utc))
    )
    await db.flush()

    publish_step(campaign_id, {
        "agent": "execution_agent",
        "agent_name": "Execution Agent",
        "status": "running",
        "message": f"Dispatching messages to Channel Service..."
    })

    # Rebuild segment from campaign data
    segment_data = {
        "name": campaign.name,
        "customer_count": 0,
        "customers": []
    }

    # Load segment customers
    if campaign.segment_id:
        from app.models.campaign import SegmentCustomer
        from app.models.customer import Customer, CustomerTwin
        sc_result = await db.execute(
            select(Customer, CustomerTwin)
            .join(SegmentCustomer, SegmentCustomer.customer_id == Customer.id)
            .join(CustomerTwin, CustomerTwin.customer_id == Customer.id, isouter=True)
            .where(SegmentCustomer.segment_id == campaign.segment_id)
        )
        rows = sc_result.all()
        from datetime import datetime as dt
        now = dt.utcnow()
        customers = []
        for row in rows:
            cust, twin = row[0], row[1]
            lo = cust.last_order_at
            last_days = (now - lo.replace(tzinfo=None)).days if lo else 999
            customers.append({
                "id": str(cust.id),
                "name": cust.name,
                "email": cust.email,
                "phone": cust.phone or "",
                "city": cust.city or "",
                "total_spend": cust.total_spend,
                "channel_affinity": twin.channel_affinity if twin else {},
            })
        segment_data["customers"] = customers
        segment_data["customer_count"] = len(customers)

    strategy = campaign.strategy or {"channel_allocation": {"email": 1.0}}
    copies = campaign.copies or []

    messages, exec_step = await execution_agent.run(
        campaign_id, segment_data, strategy, copies, db
    )

    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="executing")
    )
    await db.flush()

    publish_step(campaign_id, {
        "agent": "execution_agent",
        "agent_name": "Execution Agent",
        "status": "completed",
        "message": exec_step.output_summary,
        "confidence": exec_step.confidence
    })

    return messages


async def complete_campaign(campaign_id: str, db: AsyncSession):
    """Run Learning + Insight agents after campaign completion."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        return

    segment = {
        "name": campaign.name or "",
        "customer_count": 0,
        "customers": []
    }
    if campaign.segment_id:
        from app.models.campaign import Segment as SegmentModel
        seg_result = await db.execute(select(SegmentModel).where(SegmentModel.id == campaign.segment_id))
        seg = seg_result.scalar_one_or_none()
        if seg:
            segment["name"] = seg.name
            segment["customer_count"] = seg.customer_count

    # Learning Agent
    actual_stats, learn_step = await learning_agent.run(campaign_id, segment, db)

    # Insight Agent
    simulation = campaign.simulation_result or {}
    personas = campaign.personas or []
    insight_data, ins_step = await insight_agent.run(
        campaign_id, campaign.intent, simulation, actual_stats, segment, personas
    )

    # Save
    db_insight = Insight(
        campaign_id=campaign_id,
        content=insight_data
    )
    db.add(db_insight)

    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(
            status="completed",
            completed_at=datetime.now(timezone.utc),
            actual_stats=actual_stats
        )
    )
    await db.flush()

    publish_step(campaign_id, {
        "agent": "insight_agent",
        "agent_name": "Insight Agent",
        "status": "completed",
        "message": ins_step.output_summary,
        "confidence": ins_step.confidence
    })

    return insight_data
