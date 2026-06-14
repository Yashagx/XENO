import logging
import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.agents.llm_client import call_llm
from app.agents.state import AgentStep
from app.models.customer import CustomerTwin, TwinAuditLog
from app.models.message import Message
import uuid

logger = logging.getLogger(__name__)

EWMA_ALPHA = 0.3  # Learning rate for affinity updates


async def run(campaign_id: str, segment: dict, db: AsyncSession) -> tuple[dict, AgentStep]:
    """Update Digital Twins after campaign completion."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    # Get all messages for this campaign
    result = await db.execute(
        select(Message).where(Message.campaign_id == campaign_id)
    )
    messages = result.scalars().all()
    
    if not messages:
        step = AgentStep(
            agent_id="learning_agent",
            agent_name="Learning Agent",
            status="completed",
            input_summary=f"Campaign {campaign_id}",
            output_summary="No messages found, nothing to learn",
            reasoning="Campaign had no messages",
            confidence=0.0,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
        return {}, step
    
    # Compute actual stats
    total = len(messages)
    delivered = sum(1 for m in messages if m.status not in ("failed", "bounced", "pending"))
    opened = sum(1 for m in messages if m.opened_at is not None)
    clicked = sum(1 for m in messages if m.clicked_at is not None)
    converted = sum(1 for m in messages if m.converted_at is not None)
    
    actual_stats = {
        "total_sent": total,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "open_rate": opened / max(delivered, 1),
        "click_rate": clicked / max(opened, 1),
        "conversion_rate": converted / max(total, 1),
        "delivery_rate": delivered / max(total, 1),
        "roi": (converted * 1500) / max(segment.get("customer_count", 1) * 0.5, 1),
    }
    
    # Update twins for each customer based on engagement
    twins_updated = 0
    for msg in messages[:200]:  # cap for performance
        # Get twin
        twin_result = await db.execute(
            select(CustomerTwin).where(CustomerTwin.customer_id == msg.customer_id)
        )
        twin = twin_result.scalar_one_or_none()
        
        if not twin:
            continue
        
        # Update channel affinity via EWMA
        channel = msg.channel
        current_affinity = twin.channel_affinity or {}
        current_val = current_affinity.get(channel, 0.5)
        
        if msg.opened_at or msg.clicked_at:
            # Positive signal — increase affinity
            new_val = current_val + EWMA_ALPHA * (1.0 - current_val)
        elif msg.delivered_at and not msg.opened_at:
            # Delivered but no open — small negative signal
            new_val = current_val + EWMA_ALPHA * (0.2 - current_val)
        else:
            new_val = current_val
        
        new_affinity = {**current_affinity, channel: round(new_val, 4)}
        
        # Update twin
        old_version = twin.version
        twin.channel_affinity = new_affinity
        twin.version = old_version + 1
        twin.updated_at = datetime.now(timezone.utc)
        
        # Log audit
        audit = TwinAuditLog(
            customer_id=msg.customer_id,
            version=twin.version,
            snapshot={"channel_affinity": new_affinity},
            change_reason=f"campaign_{campaign_id}_learning"
        )
        db.add(audit)
        twins_updated += 1
    
    await db.flush()
    
    step = AgentStep(
        agent_id="learning_agent",
        agent_name="Learning Agent",
        status="completed",
        input_summary=f"{total} messages from campaign {campaign_id}",
        output_summary=f"Updated {twins_updated} customer twins. Open rate: {actual_stats['open_rate']:.1%}, Conversion: {actual_stats['conversion_rate']:.1%}",
        reasoning=f"Applied EWMA channel affinity updates (α={EWMA_ALPHA}) based on engagement signals",
        confidence=min(1.0, total / 100),
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )

    # ─── AWS Integrations (non-blocking, graceful-fallback) ─────────────────
    import asyncio as _asyncio

    # CloudWatch: push campaign ROI + messages sent metrics
    try:
        from app.services.cloudwatch_service import metric_campaign_completed, metric_messages_sent
        _asyncio.create_task(metric_campaign_completed(actual_stats.get("roi", 0)))
        _asyncio.create_task(metric_messages_sent(total))
    except Exception:
        pass

    # SNS: notify campaign completed
    try:
        from app.services.sns_service import notify_campaign_completed as _sns_done
        _asyncio.create_task(_sns_done(
            campaign_id=campaign_id,
            campaign_name=segment.get("name", campaign_id),
            actual_stats=actual_stats
        ))
    except Exception:
        pass

    # SES: send completion email to marketer (if campaign has created_by_email)
    try:
        from app.services.ses_service import send_campaign_completion_email as _ses_email
        marketer_email = segment.get("created_by_email", "")
        if marketer_email:
            _asyncio.create_task(_ses_email(
                marketer_email=marketer_email,
                campaign_name=segment.get("name", campaign_id),
                stats=actual_stats
            ))
    except Exception:
        pass

    return actual_stats, step

