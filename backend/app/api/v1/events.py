from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory fallback event bus when Redis is unavailable
_event_queues: dict[str, list[asyncio.Queue]] = {}


def _dispatch_event(campaign_id: str, data: str):
    """Dispatch to all listeners for a campaign."""
    for q in _event_queues.get(campaign_id, []):
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            pass


async def event_stream(campaign_id: str) -> AsyncGenerator[str, None]:
    """SSE stream for a specific campaign — Redis or in-memory fallback."""
    # Try Redis first
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True,
                              socket_connect_timeout=2, socket_timeout=2)
        pubsub = r.pubsub()
        channel = f"campaign:{campaign_id}:events"
        await pubsub.subscribe(channel)
        yield f"data: {json.dumps({'type': 'connected', 'campaign_id': campaign_id})}\n\n"
        try:
            entries = await r.xrange(f"stream:campaign:{campaign_id}", count=50)
            for _, entry_data in entries:
                yield f"data: {entry_data.get('data', '{}')}\n\n"
        except Exception:
            pass
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield f"data: {message['data']}\n\n"
            await asyncio.sleep(0.01)
    except Exception:
        # Fallback: in-memory queue
        q: asyncio.Queue = asyncio.Queue(maxsize=200)
        _event_queues.setdefault(campaign_id, []).append(q)
        yield f"data: {json.dumps({'type': 'connected', 'campaign_id': campaign_id, 'mode': 'polling'})}\n\n"
        try:
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=25)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            try:
                _event_queues[campaign_id].remove(q)
            except (KeyError, ValueError):
                pass


async def global_event_stream() -> AsyncGenerator[str, None]:
    """Global SSE stream for all campaign events."""
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True,
                              socket_connect_timeout=2, socket_timeout=2)
        pubsub = r.pubsub()
        await pubsub.psubscribe("campaign:*:events")
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"
        async for message in pubsub.listen():
            if message["type"] in ("message", "pmessage"):
                yield f"data: {message['data']}\n\n"
            await asyncio.sleep(0.01)
    except Exception:
        yield f"data: {json.dumps({'type': 'connected', 'mode': 'no-redis'})}\n\n"
        while True:
            try:
                await asyncio.sleep(20)
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            except asyncio.CancelledError:
                break


@router.get("/stream")
async def stream_all_events():
    return StreamingResponse(
        global_event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@router.get("/stream/{campaign_id}")
async def stream_campaign_events(campaign_id: str):
    return StreamingResponse(
        event_stream(campaign_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )
