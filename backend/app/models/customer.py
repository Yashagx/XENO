import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Text,
    ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    city = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    total_spend = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    last_order_at = Column(DateTime)
    metadata_ = Column("metadata", JSON, default={})

    # Relationships
    orders = relationship("Order", back_populates="customer", lazy="select")
    twin = relationship("CustomerTwin", back_populates="customer", uselist=False, lazy="select")
    messages = relationship("Message", back_populates="customer", lazy="select")


class CustomerTwin(Base):
    __tablename__ = "customer_twins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)
    version = Column(Integer, default=1)

    # Affinity scores
    channel_affinity = Column(JSON, default={"email": 0.5, "sms": 0.3, "whatsapp": 0.4})
    category_affinity = Column(JSON, default={})
    brand_affinity = Column(Float, default=0.5)

    # Predicted states
    churn_probability = Column(Float, default=0.0)
    predicted_ltv_90d = Column(Float, default=0.0)
    predicted_next_purchase_days = Column(Integer, default=30)
    purchase_intent_score = Column(Float, default=0.5)

    # Personality
    price_sensitivity = Column(Float, default=0.5)
    urgency_responsiveness = Column(Float, default=0.5)
    social_proof_affinity = Column(Float, default=0.5)
    communication_style = Column(String(20), default="casual")

    # Narrative
    narrative_summary = Column(Text)

    # Vector embedding (stored as text for SQLite dev)
    embedding = Column(Text)

    # Meta
    confidence_score = Column(Float, default=0.5)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="twin")


class TwinAuditLog(Base):
    __tablename__ = "twin_audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    version = Column(Integer, nullable=False)
    snapshot = Column(JSON)
    change_reason = Column(String(255))
    changed_at = Column(DateTime, default=datetime.utcnow)
