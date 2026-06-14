import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    channel = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    subject = Column(String(500))
    personalisation_tokens = Column(JSON, default={})
    status = Column(String(50), default="pending")
    channel_job_id = Column(String(255))
    idempotency_key = Column(String(255), unique=True)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    converted_at = Column(DateTime)
    failed_at = Column(DateTime)
    fail_reason = Column(Text)

    campaign = relationship("Campaign", back_populates="messages")
    customer = relationship("Customer", back_populates="messages")


class CampaignEvent(Base):
    __tablename__ = "campaign_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    message_id = Column(String(36), ForeignKey("messages.id"))
    customer_id = Column(String(36), ForeignKey("customers.id"))
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default={})
    received_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="events")
