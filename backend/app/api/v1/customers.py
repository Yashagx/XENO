from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_, text
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid
import csv
import io
from datetime import datetime

from app.database import get_db
from app.models.customer import Customer, CustomerTwin
from app.models.order import Order

router = APIRouter()


@router.post("/import-csv")
async def import_customers_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Admin endpoint: Upload CSV and bulk-insert customers.
    CSV format: name,email,phone,city,total_spend,order_count
    Also uploads to S3 for audit trail (graceful-fallback).
    """
    contents = await file.read()

    # Upload to S3 for audit (non-blocking, graceful)
    s3_key = None
    try:
        from app.services.s3_service import upload_customers_csv_to_s3
        s3_key = await upload_customers_csv_to_s3(contents, file.filename or "upload.csv")
    except Exception:
        pass

    # Parse CSV
    try:
        text_content = contents.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text_content))
        rows = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    imported = 0
    for row in rows:
        email = row.get("email", "").strip()
        if not email:
            continue
        # Skip if already exists
        existing = await db.execute(select(Customer).where(Customer.email == email))
        if existing.scalar_one_or_none():
            continue
        cust = Customer(
            id=str(uuid.uuid4()),
            name=row.get("name", "Unknown").strip(),
            email=email,
            phone=row.get("phone", "").strip() or None,
            city=row.get("city", "").strip() or None,
            total_spend=float(row.get("total_spend", 0) or 0),
            order_count=int(row.get("order_count", 0) or 0),
            created_at=datetime.utcnow(),
        )
        db.add(cust)
        await db.flush()
        # Create basic twin
        twin = CustomerTwin(
            id=str(uuid.uuid4()),
            customer_id=cust.id,
            churn_probability=0.3,
            purchase_intent_score=0.5,
            predicted_ltv_90d=cust.total_spend * 0.3,
            channel_affinity={"email": 0.5, "sms": 0.3, "whatsapp": 0.2},
            communication_style="casual",
            price_sensitivity=0.5,
            version=1,
            updated_at=datetime.utcnow(),
        )
        db.add(twin)
        imported += 1

    await db.commit()
    return {"imported": imported, "s3_key": s3_key}




@router.get("")
async def list_customers(
    search: Optional[str] = None,
    min_spend: Optional[float] = None,
    max_spend: Optional[float] = None,
    min_churn: Optional[float] = None,
    max_churn: Optional[float] = None,
    city: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Customer, CustomerTwin)
        .join(CustomerTwin, Customer.id == CustomerTwin.customer_id, isouter=True)
        .order_by(desc(Customer.total_spend))
        .offset(offset)
        .limit(limit)
    )

    if search:
        query = query.where(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.city.ilike(f"%{search}%")
            )
        )
    if min_spend is not None:
        query = query.where(Customer.total_spend >= min_spend)
    if max_spend is not None:
        query = query.where(Customer.total_spend <= max_spend)
    if min_churn is not None:
        query = query.where(CustomerTwin.churn_probability >= min_churn)
    if max_churn is not None:
        query = query.where(CustomerTwin.churn_probability <= max_churn)
    if city:
        query = query.where(Customer.city.ilike(f"%{city}%"))

    result = await db.execute(query)
    rows = result.all()

    # Count
    count_q = select(func.count(Customer.id))
    count_result = await db.execute(count_q)
    total = count_result.scalar()

    customers_data = []
    now = datetime.utcnow()
    for row in rows:
        cust, twin = row[0], row[1]
        lo = cust.last_order_at
        last_order_days = (now - lo.replace(tzinfo=None)).days if lo else None
        customers_data.append(_customer_to_dict(cust, twin, last_order_days))

    return {"customers": customers_data, "total": total, "limit": limit, "offset": offset}


@router.get("/stats")
async def customer_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(Customer.id)))
    total = total_result.scalar()

    spend_result = await db.execute(select(func.avg(Customer.total_spend)))
    avg_spend = spend_result.scalar() or 0

    churn_result = await db.execute(select(func.avg(CustomerTwin.churn_probability)))
    avg_churn = churn_result.scalar() or 0

    high_churn_result = await db.execute(
        select(func.count(CustomerTwin.id)).where(CustomerTwin.churn_probability > 0.7)
    )
    high_churn = high_churn_result.scalar()

    return {
        "total_customers": total,
        "avg_total_spend": round(avg_spend, 2),
        "avg_churn_probability": round(avg_churn, 4),
        "high_churn_count": high_churn,
    }


@router.get("/{customer_id}")
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Customer, CustomerTwin)
        .join(CustomerTwin, Customer.id == CustomerTwin.customer_id, isouter=True)
        .where(Customer.id == customer_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    cust, twin = row[0], row[1]
    now = datetime.utcnow()
    lo = cust.last_order_at
    last_order_days = (now - lo.replace(tzinfo=None)).days if lo else None

    # Get recent orders
    orders_result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(desc(Order.ordered_at))
        .limit(10)
    )
    orders = orders_result.scalars().all()

    customer_dict = _customer_to_dict(cust, twin, last_order_days)
    customer_dict["recent_orders"] = [
        {
            "id": str(o.id),
            "order_number": o.order_number,
            "total": o.total,
            "channel": o.channel,
            "ordered_at": o.ordered_at.isoformat() if o.ordered_at else None
        }
        for o in orders
    ]
    return customer_dict


def _customer_to_dict(cust: Customer, twin, last_order_days) -> dict:
    return {
        "id": str(cust.id),
        "name": cust.name,
        "email": cust.email,
        "phone": cust.phone,
        "city": cust.city,
        "total_spend": cust.total_spend,
        "order_count": cust.order_count,
        "last_order_at": cust.last_order_at.isoformat() if cust.last_order_at else None,
        "last_order_days": last_order_days,
        "created_at": cust.created_at.isoformat() if cust.created_at else None,
        "twin": {
            "churn_probability": twin.churn_probability if twin else 0.5,
            "purchase_intent_score": twin.purchase_intent_score if twin else 0.5,
            "predicted_ltv_90d": twin.predicted_ltv_90d if twin else 0,
            "channel_affinity": twin.channel_affinity if twin else {},
            "category_affinity": twin.category_affinity if twin else {},
            "communication_style": twin.communication_style if twin else "casual",
            "price_sensitivity": twin.price_sensitivity if twin else 0.5,
            "urgency_responsiveness": twin.urgency_responsiveness if twin else 0.5,
            "narrative_summary": twin.narrative_summary if twin else "",
            "confidence_score": twin.confidence_score if twin else 0,
            "version": twin.version if twin else 1,
            "updated_at": twin.updated_at.isoformat() if twin and twin.updated_at else None,
        } if twin else None
    }
