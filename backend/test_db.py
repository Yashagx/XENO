import sys
sys.path.insert(0, '.')
import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./xeno_oracle.db'
os.environ['DATABASE_URL_SYNC'] = 'sqlite:///./xeno_oracle.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['GEMINI_API_KEY'] = 'test-key'

from app.models.customer import Customer, CustomerTwin, TwinAuditLog
from app.models.order import Order, Product, OrderItem
from app.models.campaign import Campaign, Segment, SegmentCustomer
from app.models.message import Message, CampaignEvent
from app.models.insight import Insight
from app.database import Base, sync_engine

print("Creating tables...")
Base.metadata.create_all(sync_engine)
print("Tables created!")

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
s = sessionmaker(bind=sync_engine)()
tables = s.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
print("Tables:", [t[0] for t in tables])
s.close()
print("SUCCESS")
