from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import json
import logging

from app.database import get_db
from app.models.message import Message, CampaignEvent
from app.redis_client import async_redis

router = APIRouter()
logger = logging.getLogger(__name__)


class CallbackRequest(BaseModel):
    message_id: str
    event_type: str  # delivered | opened | clicked | converted | failed | bounced
    timestamp: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/callbacks")
async def receive_callback(request: CallbackRequest, db: AsyncSession = Depends(get_db)):
    """Receive delivery/engagement callbacks from Channel Service."""
    msg_id = request.message_id

    result = await db.execute(select(Message).where(Message.id == msg_id))
    message = result.scalar_one_or_none()
    if not message:
        return {"acknowledged": True, "note": "Message not found, ignoring"}

    now = datetime.now(timezone.utc)
    event_type = request.event_type

    # Update message status (only move forward, never backward)
    status_order = ["pending", "sent", "delivered", "opened", "clicked", "converted"]
    current_idx = status_order.index(message.status) if message.status in status_order else 0

    updates = {}
    if event_type == "delivered" and current_idx < status_order.index("delivered"):
        updates["status"] = "delivered"
        updates["delivered_at"] = now
    elif event_type == "opened" and current_idx < status_order.index("opened"):
        updates["status"] = "opened"
        updates["opened_at"] = now
        if not message.delivered_at:
            updates["delivered_at"] = now
    elif event_type == "clicked" and current_idx < status_order.index("clicked"):
        updates["status"] = "clicked"
        updates["clicked_at"] = now
        if not message.opened_at:
            updates["opened_at"] = now
    elif event_type == "converted" and current_idx < status_order.index("converted"):
        updates["status"] = "converted"
        updates["converted_at"] = now
    elif event_type in ("failed", "bounced"):
        updates["status"] = event_type
        updates["failed_at"] = now
        updates["fail_reason"] = str(request.metadata or {})

    if updates:
        await db.execute(update(Message).where(Message.id == msg_id).values(**updates))

    # Log event
    event = CampaignEvent(
        campaign_id=message.campaign_id,
        message_id=message.id,
        customer_id=message.customer_id,
        event_type=event_type,
        payload=request.metadata or {}
    )
    db.add(event)
    await db.flush()

    # Publish to Redis for SSE stream (if Redis available)
    campaign_id = str(message.campaign_id)
    event_data = json.dumps({
        "type": "message_event",
        "campaign_id": campaign_id,
        "message_id": request.message_id,
        "customer_id": str(message.customer_id),
        "event_type": event_type,
        "channel": message.channel,
        "timestamp": now.isoformat()
    })
    try:
        if async_redis:
            await async_redis.publish(f"campaign:{campaign_id}:events", event_data)
            await async_redis.xadd(f"stream:campaign:{campaign_id}", {"data": event_data}, maxlen=5000)
    except Exception as e:
        logger.debug(f"Redis publish skipped: {e}")

    return {"acknowledged": True}
