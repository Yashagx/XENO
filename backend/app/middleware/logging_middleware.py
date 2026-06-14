import time
import json
import logging
import asyncio
from datetime import datetime
from fastapi import Request

logger = logging.getLogger("xeno_oracle")


async def structured_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "client_ip": request.client.host if request.client else None,
    }
    logger.info(json.dumps(log_entry))
    # Push latency to CloudWatch (async, non-blocking)
    try:
        from app.services.cloudwatch_service import metric_api_latency
        asyncio.create_task(metric_api_latency(request.url.path, duration_ms))
    except Exception:
        pass
    return response
