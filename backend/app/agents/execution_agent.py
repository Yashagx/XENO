import logging
import json
import hashlib
import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.state import AgentStep
from app.models.message import Message
from app.config import settings
import uuid

logger = logging.getLogger(__name__)


async def run(
    campaign_id: str,
    segment: dict,
    strategy: dict,
    copies: list[dict],
    db: AsyncSession
) -> tuple[list[dict], AgentStep]:
    """Fire the campaign by calling the Channel Service API."""
    started_at = datetime.now(timezone.utc).isoformat()
    
    customers = segment.get("customers", [])
    alloc = strategy.get("channel_allocation", {"email": 1.0})
    
    # Sort channels by allocation weight for assignment
    sorted_channels = sorted(alloc.items(), key=lambda x: x[1], reverse=True)
    channels_list = [ch for ch, _ in sorted_channels]
    
    # Build copy lookup: best copy per channel
    copy_lookup = {}
    for copy in copies:
        key = (copy["channel"], copy["variant"])
        if copy["channel"] not in copy_lookup:
            copy_lookup[copy["channel"]] = copy
    
    # Assign channels to customers round-robin weighted
    def assign_channel(idx: int) -> str:
        # Use allocation weights to assign channels
        cumulative = 0
        r = (idx % 100) / 100.0
        for ch, weight in sorted_channels:
            cumulative += weight
            if r < cumulative:
                return ch
        return channels_list[0]
    
    messages_created = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, customer in enumerate(customers):
            channel = assign_channel(idx)
            copy = copy_lookup.get(channel, list(copy_lookup.values())[0] if copy_lookup else None)
            
            if not copy:
                continue
            
            # Personalize content
            content = copy["body"]
            content = content.replace("{first_name}", customer["name"].split()[0])
            content = content.replace("{{first_name}}", customer["name"].split()[0])
            content = content.replace("{city}", customer.get("city", "your city"))
            
            subject = copy.get("subject", "")
            if subject:
                subject = subject.replace("{first_name}", customer["name"].split()[0])
                subject = subject.replace("{{first_name}}", customer["name"].split()[0])
            
            # Idempotency key
            idem_key = hashlib.sha256(f"{campaign_id}:{customer['id']}".encode()).hexdigest()
            
            # Create message record in DB
            msg = Message(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                customer_id=str(customer["id"]),
                channel=channel,
                content=content,
                subject=subject,
                status="sent",
                idempotency_key=idem_key,
                sent_at=datetime.now(timezone.utc),
                personalisation_tokens={"first_name": customer["name"].split()[0]}
            )
            db.add(msg)
            
            # Call channel service asynchronously
            try:
                recipient = customer.get("email", "") if channel == "email" else customer.get("phone", customer.get("email", ""))
                payload = {
                    "message_id": str(msg.id),
                    "campaign_id": campaign_id,
                    "customer_id": customer["id"],
                    "channel": channel,
                    "content": content,
                    "subject": subject,
                    "recipient": recipient,
                    "idempotency_key": idem_key
                }
                response = await client.post(
                    f"{settings.CHANNEL_SERVICE_URL}/send",
                    json=payload
                )
                if response.status_code == 200:
                    data = response.json()
                    msg.channel_job_id = data.get("job_id", "")
            except Exception as e:
                logger.warning(f"Channel service call failed for {customer['id']}: {e}")
                msg.status = "failed"
                msg.fail_reason = str(e)
            
            messages_created.append({
                "message_id": str(msg.id),
                "customer_id": customer["id"],
                "channel": channel,
                "status": msg.status,
            })
        
        await db.flush()
    
    step = AgentStep(
        agent_id="execution_agent",
        agent_name="Execution Agent",
        status="completed",
        input_summary=f"{len(customers)} customers, channels: {list(alloc.keys())}",
        output_summary=f"Dispatched {len(messages_created)} messages via Channel Service",
        reasoning=f"Messages sent in batches with idempotency keys. Channel service handles async delivery.",
        confidence=0.95,
        started_at=started_at,
        completed_at=datetime.now(timezone.utc).isoformat()
    )
    
    return messages_created, step
