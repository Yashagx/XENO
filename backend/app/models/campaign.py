import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Segment(Base):
    __tablename__ = "segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    filter_config = Column(JSON, default={})
    customer_count = Column(Integer, default=0)
    created_by_intent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_dynamic = Column(Boolean, default=True)
    embedding = Column(Text)  # stored as text for SQLite dev

    customers = relationship("SegmentCustomer", back_populates="segment", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="segment")


class SegmentCustomer(Base):
    __tablename__ = "segment_customers"

    segment_id = Column(String(36), ForeignKey("segments.id", ondelete="CASCADE"), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), primary_key=True)
    inclusion_reason = Column(Text)

    segment = relationship("Segment", back_populates="customers")
    customer = relationship("Customer")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    intent = Column(Text, nullable=False)
    segment_id = Column(String(36), ForeignKey("segments.id"))
    status = Column(String(50), default="draft")
    strategy = Column(JSON, default={})
    simulation_result = Column(JSON, default={})
    personas = Column(JSON, default=[])
    copies = Column(JSON, default=[])
    agent_trace = Column(JSON, default=[])
    explanation = Column(JSON, default={})
    actual_stats = Column(JSON, default={})
    scheduled_at = Column(DateTime)
    executed_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Text)  # stored as text for SQLite dev
    # Auth / notification fields (v2.0)
    created_by_user_id = Column(String(36), nullable=True)
    created_by_email = Column(String(255), nullable=True)

    segment = relationship("Segment", back_populates="campaigns")
    messages = relationship("Message", back_populates="campaign", cascade="all, delete-orphan")
    events = relationship("CampaignEvent", back_populates="campaign", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="campaign")
