from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
import uuid

from app.database import get_db
from app.models.customer import Customer, CustomerTwin, TwinAuditLog

router = APIRouter()


@router.get("/{customer_id}")
async def get_twin(customer_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CustomerTwin, Customer)
        .join(Customer, Customer.id == CustomerTwin.customer_id)
        .where(CustomerTwin.customer_id == customer_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Twin not found")
    twin, customer = row[0], row[1]
    return _twin_to_dict(twin, customer)


@router.get("/{customer_id}/history")
async def get_twin_history(customer_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TwinAuditLog)
        .where(TwinAuditLog.customer_id == customer_id)
        .order_by(desc(TwinAuditLog.changed_at))
        .limit(20)
    )
    logs = result.scalars().all()
    return {
        "customer_id": customer_id,
        "history": [
            {
                "version": l.version,
                "snapshot": l.snapshot,
                "change_reason": l.change_reason,
                "changed_at": l.changed_at.isoformat() if l.changed_at else None
            }
            for l in logs
        ]
    }


def _twin_to_dict(twin: CustomerTwin, customer: Customer) -> dict:
    return {
        "customer_id": str(twin.customer_id),
        "customer_name": customer.name,
        "customer_email": customer.email,
        "version": twin.version,
        "channel_affinity": twin.channel_affinity,
        "category_affinity": twin.category_affinity,
        "churn_probability": twin.churn_probability,
        "purchase_intent_score": twin.purchase_intent_score,
        "predicted_ltv_90d": twin.predicted_ltv_90d,
        "price_sensitivity": twin.price_sensitivity,
        "urgency_responsiveness": twin.urgency_responsiveness,
        "social_proof_affinity": twin.social_proof_affinity,
        "communication_style": twin.communication_style,
        "narrative_summary": twin.narrative_summary,
        "confidence_score": twin.confidence_score,
        "updated_at": twin.updated_at.isoformat() if twin.updated_at else None,
    }
