import os
import sys
import uuid
import random
from datetime import datetime, timedelta
import asyncio
from faker import Faker
import json

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.customer import Customer, CustomerTwin

fake = Faker()

def generate_fake_customer():
    name = fake.name()
    return {
        "name": name,
        "email": f"{name.lower().replace(' ', '.')}@example.com",
        "phone": fake.phone_number()[:20],
        "city": fake.city(),
        "total_spend": round(random.uniform(50.0, 5000.0), 2),
        "order_count": random.randint(1, 50),
        "last_order_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
        "metadata_": {}
    }

def generate_fake_twin(customer_id):
    return {
        "customer_id": customer_id,
        "channel_affinity": {
            "email": round(random.uniform(0.1, 0.9), 2),
            "sms": round(random.uniform(0.1, 0.9), 2),
            "whatsapp": round(random.uniform(0.1, 0.9), 2)
        },
        "category_affinity": {
            "electronics": round(random.uniform(0.1, 0.9), 2),
            "fashion": round(random.uniform(0.1, 0.9), 2)
        },
        "brand_affinity": round(random.uniform(0.1, 0.9), 2),
        "churn_probability": round(random.uniform(0.01, 0.99), 2),
        "predicted_ltv_90d": round(random.uniform(10.0, 1000.0), 2),
        "predicted_next_purchase_days": random.randint(1, 90),
        "purchase_intent_score": round(random.uniform(0.1, 0.9), 2),
        "price_sensitivity": round(random.uniform(0.1, 0.9), 2),
        "urgency_responsiveness": round(random.uniform(0.1, 0.9), 2),
        "social_proof_affinity": round(random.uniform(0.1, 0.9), 2),
        "communication_style": random.choice(["casual", "formal", "urgent"]),
        "narrative_summary": fake.paragraph(nb_sentences=3),
        "confidence_score": round(random.uniform(0.5, 0.99), 2)
    }

async def seed_db(num_records=50):
    async with AsyncSessionLocal() as db:
        print(f"Seeding {num_records} customers...")
        for _ in range(num_records):
            c_data = generate_fake_customer()
            customer = Customer(**c_data)
            db.add(customer)
            await db.flush()  # To generate customer.id
            
            t_data = generate_fake_twin(customer.id)
            twin = CustomerTwin(**t_data)
            db.add(twin)
            
        await db.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    count = 100
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    asyncio.run(seed_db(count))
