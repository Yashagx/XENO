from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import uuid

from app.database import get_db
from app.models.insight import Insight
from app.models.campaign import Campaign

router = APIRouter()


@router.get("")
async def list_insights(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Insight, Campaign)
        .join(Campaign, Campaign.id == Insight.campaign_id)
        .order_by(desc(Insight.generated_at))
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    return {
        "insights": [
            {
                "id": str(ins.id),
                "campaign_id": str(ins.campaign_id),
                "campaign_name": cam.name,
                "campaign_intent": cam.intent,
                "content": ins.content,
                "generated_at": ins.generated_at.isoformat() if ins.generated_at else None
            }
            for ins, cam in rows
        ]
    }


@router.get("/{insight_id}")
async def get_insight(insight_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Insight).where(Insight.id == insight_id)
    )
    insight = result.scalar_one_or_none()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {
        "id": str(insight.id),
        "campaign_id": str(insight.campaign_id),
        "content": insight.content,
        "generated_at": insight.generated_at.isoformat() if insight.generated_at else None
    }
