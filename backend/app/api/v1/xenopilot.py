from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from collections import defaultdict

from app.database import get_db
from app.agents.xenopilot_agent import run_xenopilot
from app.api.v1.auth import get_current_user
from app.models.auth import User

router = APIRouter()

# Simple in-memory rate limiter
_rate_limits: dict = defaultdict(list)
RATE_LIMIT = 20  # requests per minute


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


@router.post("/chat")
async def xenopilot_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Rate limiting
    now = datetime.utcnow()
    user_reqs = _rate_limits[current_user.id]
    # Keep only last minute
    user_reqs[:] = [t for t in user_reqs if (now - t).total_seconds() < 60]
    if len(user_reqs) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 20 requests per minute.")
    user_reqs.append(now)

    history = [{"role": m.role, "content": m.content} for m in (request.conversation_history or [])]
    result = await run_xenopilot(request.message, history, db)
    return result
