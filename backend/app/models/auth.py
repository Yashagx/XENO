from sqlalchemy import Column, String, Boolean, DateTime
from uuid import uuid4
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="marketer")  # "admin" | "marketer" | "viewer"
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
