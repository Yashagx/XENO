from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from app.database import get_db
from app.models.campaign import Campaign, Segment
from app.models.message import Message
from app.agents.orchestrator import run_campaign_pipeline, execute_campaign, complete_campaign
from app.api.v1.auth import get_current_user, require_role
from app.models.auth import User
import asyncio

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    intent: str
    name: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ApproveCampaignRequest(BaseModel):
    modifications: Optional[dict] = None


async def _run_pipeline(campaign_id: str, db_url: str):
    """Background task to run agent pipeline."""
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            await run_campaign_pipeline(campaign_id, db)
            await db.commit()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Pipeline error: {e}")
            from sqlalchemy import update
            from app.models.campaign import Campaign
            import uuid
            await db.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(status="failed")
            )
            await db.commit()


async def _execute_campaign_bg(campaign_id: str):
    """Background task to execute campaign."""
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            await execute_campaign(campaign_id, db)
            await db.commit()
            # Schedule completion after 60 seconds (simulated delivery time)
            await asyncio.sleep(60)
            await complete_campaign(campaign_id, db)
            await db.commit()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Execution error: {e}")


@router.post("", status_code=201)
async def create_campaign(
    request: CreateCampaignRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    """Create a new campaign and immediately start the agent pipeline."""
    campaign = Campaign(
        id=str(uuid.uuid4()),
        intent=request.intent,
        name=request.name or f"Campaign - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        status="segmenting",
        scheduled_at=request.scheduled_at,
        created_by_user_id=str(current_user.id),
        created_by_email=current_user.email,
    )
    db.add(campaign)
    await db.flush()
    campaign_id = str(campaign.id)
    await db.commit()

    # CloudWatch: campaign created metric (non-blocking, graceful)
    try:
        from app.services.cloudwatch_service import metric_campaign_created
        asyncio.create_task(metric_campaign_created())
    except Exception:
        pass

    # Run agent pipeline in background
    background_tasks.add_task(_run_pipeline, campaign_id, "")

    return {
        "campaign_id": campaign_id,
        "status": "segmenting",
        "message": "Agent pipeline started. Watch the live event stream for progress."
    }


@router.get("")
async def list_campaigns(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer", "viewer"))
):
    query = select(Campaign).order_by(desc(Campaign.created_at)).offset(offset).limit(limit)
    if status:
        query = query.where(Campaign.status == status)
    result = await db.execute(query)
    campaigns = result.scalars().all()

    count_q = select(func.count(Campaign.id))
    if status:
        count_q = count_q.where(Campaign.status == status)
    count_result = await db.execute(count_q)
    total = count_result.scalar()

    return {
        "campaigns": [_campaign_to_dict(c) for c in campaigns],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer", "viewer"))
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _campaign_to_dict(campaign)


@router.post("/{campaign_id}/approve")
async def approve_campaign(
    campaign_id: str,
    request: ApproveCampaignRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    """Approve a ready campaign for execution."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in ("ready", "simulating"):
        raise HTTPException(status_code=400, detail=f"Campaign status is '{campaign.status}', must be 'ready' to approve")

    # Execute in background
    background_tasks.add_task(_execute_campaign_bg, campaign_id)

    return {"message": "Campaign approved. Execution started.", "campaign_id": campaign_id}


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer", "viewer"))
):
    """Get real-time campaign statistics."""
    result = await db.execute(
        select(Message).where(Message.campaign_id == campaign_id)
    )
    messages = result.scalars().all()

    total = len(messages)
    delivered = sum(1 for m in messages if m.status not in ("failed", "bounced", "pending", "sent"))
    opened = sum(1 for m in messages if m.opened_at)
    clicked = sum(1 for m in messages if m.clicked_at)
    converted = sum(1 for m in messages if m.converted_at)
    failed = sum(1 for m in messages if m.status in ("failed", "bounced"))

    by_channel = {}
    for m in messages:
        ch = m.channel
        if ch not in by_channel:
            by_channel[ch] = {"sent": 0, "delivered": 0, "opened": 0, "clicked": 0}
        by_channel[ch]["sent"] += 1
        if m.status not in ("failed", "bounced", "pending"):
            by_channel[ch]["delivered"] += 1
        if m.opened_at:
            by_channel[ch]["opened"] += 1
        if m.clicked_at:
            by_channel[ch]["clicked"] += 1

    return {
        "total_sent": total,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "failed": failed,
        "open_rate": round(opened / max(delivered, 1), 4),
        "click_rate": round(clicked / max(opened, 1), 4),
        "conversion_rate": round(converted / max(total, 1), 4),
        "by_channel": by_channel,
    }


@router.post("/{campaign_id}/export")
async def export_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer", "viewer"))
):
    """Export campaign report to S3. Returns presigned URL or None if S3 not configured."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Build export payload
    campaign_data = _campaign_to_dict(campaign)

    # Get messages stats
    msgs_result = await db.execute(select(Message).where(Message.campaign_id == campaign_id))
    messages = msgs_result.scalars().all()
    campaign_data["message_count"] = len(messages)
    campaign_data["exported_at"] = datetime.now(timezone.utc).isoformat()

    from app.services.s3_service import export_campaign_to_s3
    s3_url = await export_campaign_to_s3(campaign_id, campaign_data)

    return {
        "s3_url": s3_url,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "campaign_id": campaign_id,
        "aws_configured": s3_url is not None
    }


def _campaign_to_dict(c: Campaign) -> dict:
    return {
        "id": str(c.id),
        "name": c.name,
        "intent": c.intent,
        "status": c.status,
        "segment_id": str(c.segment_id) if c.segment_id else None,
        "strategy": c.strategy,
        "simulation_result": c.simulation_result,
        "personas": c.personas,
        "copies": c.copies,
        "agent_trace": c.agent_trace,
        "explanation": c.explanation,
        "actual_stats": c.actual_stats,
        "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
        "executed_at": c.executed_at.isoformat() if c.executed_at else None,
        "completed_at": c.completed_at.isoformat() if c.completed_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
