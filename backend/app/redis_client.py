import redis.asyncio as aioredis
import redis as sync_redis
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Async Redis client
try:
    async_redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
except Exception as e:
    logger.warning(f"Redis async client init error: {e}")
    async_redis = None

# Sync Redis client
try:
    sync_redis_client = sync_redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
except Exception as e:
    logger.warning(f"Redis sync client init error: {e}")
    sync_redis_client = None


async def publish_event(channel: str, message: str):
    """Publish event to Redis pub/sub channel. No-op if Redis unavailable."""
    if async_redis is None:
        return
    try:
        await async_redis.publish(channel, message)
    except Exception as e:
        logger.debug(f"Redis publish failed (no Redis?): {e}")


async def get_redis():
    return async_redis
