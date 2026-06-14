"""
XENO ORACLE — Channel Service Microservice
Simulates message delivery with realistic probability models.
Fires callbacks to the main CRM backend.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import random
import httpx
import uuid
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv('../.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CRM_CALLBACK_URL = os.getenv("CRM_CALLBACK_URL", "http://localhost:8000/api/v1/campaigns/callbacks")

DELIVERY_PROBS = {
    "email":    {"delivered": 0.92, "bounced": 0.05, "failed": 0.03},
    "sms":      {"delivered": 0.95, "failed": 0.05},
    "whatsapp": {"delivered": 0.88, "failed": 0.12},
    "rcs":      {"delivered": 0.85, "failed": 0.15},
}

ENGAGEMENT_PROBS = {
    "email":    {"opened": 0.34, "clicked": 0.11, "converted": 0.04},
    "sms":      {"opened": 0.62, "clicked": 0.09, "converted": 0.03},
    "whatsapp": {"opened": 0.70, "clicked": 0.12, "converted": 0.04},
    "rcs":      {"opened": 0.55, "clicked": 0.10, "converted": 0.03},
}

app = FastAPI(title="XENO Channel Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs: dict = {}


class SendRequest(BaseModel):
    message_id: str
    campaign_id: str
    customer_id: str
    channel: str
    content: str
    subject: Optional[str] = None
    recipient: str
    idempotency_key: Optional[str] = None


class InjectFailureRequest(BaseModel):
    message_id: str
    failure_type: str


async def fire_callback(message_id: str, event_type: str, delay: float = 0, metadata: dict = None):
    if delay > 0:
        await asyncio.sleep(delay)
    payload = {
        "message_id": message_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(CRM_CALLBACK_URL, json=payload)
    except Exception as e:
        logger.error(f"Callback error for {message_id} ({event_type}): {e}")


async def simulate_delivery(job_id: str, request: SendRequest):
    channel = request.channel.lower()
    message_id = request.message_id
    jobs[job_id]["status"] = "processing"
    await asyncio.sleep(random.uniform(0.5, 5.0))
    forced = jobs[job_id].get("forced_failure")
    if forced == "failed":
        await fire_callback(message_id, "failed", metadata={"reason": "injected_failure"})
        jobs[job_id]["status"] = "failed"
        return
    if forced == "bounced":
        await fire_callback(message_id, "bounced", metadata={"reason": "invalid_address"})
        jobs[job_id]["status"] = "bounced"
        return
    delivery = DELIVERY_PROBS.get(channel, DELIVERY_PROBS["email"])
    r = random.random()
    if r < delivery.get("delivered", 0.92):
        await fire_callback(message_id, "delivered")
        jobs[job_id]["status"] = "delivered"
        jobs[job_id]["events"].append({"type": "delivered", "at": datetime.now(timezone.utc).isoformat()})
        if forced == "no_open":
            return
        engagement = ENGAGEMENT_PROBS.get(channel, ENGAGEMENT_PROBS["email"])
        p_open = min(0.95, engagement.get("opened", 0.35) * random.uniform(0.6, 1.6))
        if random.random() < p_open:
            await fire_callback(message_id, "opened", delay=random.uniform(2, 30))
            jobs[job_id]["status"] = "opened"
            jobs[job_id]["events"].append({"type": "opened", "at": datetime.now(timezone.utc).isoformat()})
            if forced == "no_click":
                return
            p_click = min(0.95, engagement.get("clicked", 0.11) * random.uniform(0.5, 1.8))
            if random.random() < p_click:
                await fire_callback(message_id, "clicked", delay=random.uniform(2, 15))
                jobs[job_id]["status"] = "clicked"
                jobs[job_id]["events"].append({"type": "clicked", "at": datetime.now(timezone.utc).isoformat()})
                p_convert = min(0.5, engagement.get("converted", 0.04) * random.uniform(0.5, 2.0))
                if random.random() < p_convert:
                    await fire_callback(message_id, "converted", delay=random.uniform(5, 20))
                    jobs[job_id]["status"] = "converted"
                    jobs[job_id]["events"].append({"type": "converted", "at": datetime.now(timezone.utc).isoformat()})
    elif r < delivery.get("delivered", 0.92) + delivery.get("bounced", 0.05):
        await fire_callback(message_id, "bounced", metadata={"reason": "mailbox_full"})
        jobs[job_id]["status"] = "bounced"
    else:
        await fire_callback(message_id, "failed", metadata={"reason": "network_error"})
        jobs[job_id]["status"] = "failed"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "xeno-channel-service", "jobs_tracked": len(jobs)}


@app.post("/send")
async def send_message(request: SendRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"job_id": job_id, "message_id": request.message_id, "channel": request.channel, "status": "queued", "events": [], "created_at": datetime.now(timezone.utc).isoformat()}
    background_tasks.add_task(simulate_delivery, job_id, request)
    return {"job_id": job_id, "accepted": True}


@app.get("/status/{message_id}")
async def get_status(message_id: str):
    for job in jobs.values():
        if job["message_id"] == message_id:
            return job
    return {"message_id": message_id, "status": "not_found"}


@app.post("/inject-failure")
async def inject_failure(request: InjectFailureRequest):
    for job in jobs.values():
        if job["message_id"] == request.message_id:
            job["forced_failure"] = request.failure_type
            return {"message": f"Failure '{request.failure_type}' injected"}
    return {"message": "Job not found"}


@app.get("/jobs")
async def list_jobs(limit: int = 20):
    recent = list(jobs.values())[-limit:]
    return {"jobs": recent, "total": len(jobs)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
