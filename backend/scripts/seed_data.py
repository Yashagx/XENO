#!/usr/bin/env python3
import sys, os, random, uuid
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))
from dotenv import load_dotenv
load_dotenv()
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.config import settings
from app.database import Base
from app.models.customer import Customer, CustomerTwin
from app.models.order import Order, Product

fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

PRODUCTS = [
    {"sku": "SHOE-001", "name": "Nike Air Max 270", "category": "Footwear", "subcategory": "Sneakers", "price": 12995, "brand": "Nike"},
    {"sku": "SHOE-002", "name": "Puma RS-X", "category": "Footwear", "subcategory": "Sneakers", "price": 9999, "brand": "Puma"},
    {"sku": "SHOE-003", "name": "Adidas Ultraboost 22", "category": "Footwear", "subcategory": "Running", "price": 15999, "brand": "Adidas"},
    {"sku": "SHOE-004", "name": "Bata Derby Classic", "category": "Footwear", "subcategory": "Formal", "price": 3499, "brand": "Bata"},
    {"sku": "CLTH-001", "name": "Allen Solly Formal Shirt", "category": "Clothing", "subcategory": "Shirts", "price": 1799, "brand": "Allen Solly"},
    {"sku": "CLTH-002", "name": "Van Heusen Polo", "category": "Clothing", "subcategory": "T-Shirts", "price": 999, "brand": "Van Heusen"},
    {"sku": "CLTH-003", "name": "Levi's 511 Slim Jeans", "category": "Clothing", "subcategory": "Denim", "price": 3799, "brand": "Levi's"},
    {"sku": "CLTH-004", "name": "Fabindia Kurta", "category": "Clothing", "subcategory": "Ethnic", "price": 2499, "brand": "Fabindia"},
    {"sku": "CLTH-005", "name": "Manyavar Sherwani", "category": "Clothing", "subcategory": "Ethnic", "price": 8999, "brand": "Manyavar"},
    {"sku": "ACC-001", "name": "Fossil Chronograph Watch", "category": "Accessories", "subcategory": "Watches", "price": 14999, "brand": "Fossil"},
    {"sku": "ACC-002", "name": "Hidesign Leather Wallet", "category": "Accessories", "subcategory": "Wallets", "price": 2999, "brand": "Hidesign"},
    {"sku": "ACC-003", "name": "Wildcraft Backpack 30L", "category": "Accessories", "subcategory": "Bags", "price": 2499, "brand": "Wildcraft"},
    {"sku": "SPRT-001", "name": "Yonex Badminton Racket", "category": "Sports", "subcategory": "Badminton", "price": 1999, "brand": "Yonex"},
    {"sku": "ELEC-001", "name": "boAt Rockerz 450", "category": "Electronics", "subcategory": "Audio", "price": 1999, "brand": "boAt"},
    {"sku": "ELEC-002", "name": "MI Power Bank 20000mAh", "category": "Electronics", "subcategory": "Power", "price": 1499, "brand": "Xiaomi"},
]

INDIAN_CITIES = ["Mumbai","Delhi","Bengaluru","Hyderabad","Chennai","Kolkata","Pune","Ahmedabad","Jaipur","Surat","Lucknow","Kanpur","Nagpur","Indore","Bhopal","Patna","Vadodara","Ludhiana","Agra","Nashik"]
COMM_STYLES = ["casual", "formal", "friendly", "minimal"]

def generate_twin(customer_id, orders, name, city):
    now = datetime.utcnow()
    if orders:
        last_order = max(o['ordered_at'] for o in orders)
        recency_days = (now - last_order).days
        frequency = len(orders)
        monetary = sum(o['total'] for o in orders)
    else:
        recency_days, frequency, monetary = 999, 0, 0
    
    churn = min(0.98, max(0.02, recency_days / 365.0))
    if frequency > 5: churn *= 0.7
    if monetary > 20000: churn *= 0.8
    churn = round(churn, 4)
    
    cat_counts = {}
    for o in orders:
        for cat in o.get('categories', []):
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    total_items = sum(cat_counts.values()) or 1
    cat_affinity = {cat: round(count/total_items, 3) for cat, count in cat_counts.items()}
    
    top_cat = max(cat_counts, key=cat_counts.get) if cat_counts else "fashion"
    spend_tier = "premium" if monetary > 15000 else "mid-range" if monetary > 5000 else "value"
    active = "recently active" if recency_days < 30 else "lapsed" if recency_days > 90 else "moderately active"
    first = name.split()[0]
    narrative = (f"{first} is a {spend_tier} shopper from {city} with {frequency} orders totalling Rs {monetary:,.0f}. "
                 f"Primarily interested in {top_cat}. {active.capitalize()} with {'high' if churn > 0.6 else 'low'} churn risk.")
    
    avg_order = monetary / max(frequency, 1)
    ltv_90d = min(avg_order * 3, 50000)
    
    return {
        "customer_id": customer_id, "version": 1,
        "channel_affinity": {"email": round(random.uniform(0.3,0.9),3), "sms": round(random.uniform(0.2,0.8),3), "whatsapp": round(random.uniform(0.3,0.85),3)},
        "category_affinity": cat_affinity,
        "brand_affinity": round(random.uniform(0.3,0.9),3),
        "churn_probability": churn,
        "predicted_ltv_90d": round(ltv_90d, 2),
        "predicted_next_purchase_days": max(1, recency_days // 2) if recency_days < 180 else 90,
        "purchase_intent_score": round(max(0.05, min(0.99, 1.0 - churn + random.uniform(-0.1,0.2))), 4),
        "price_sensitivity": round(random.uniform(0.1,0.9),3),
        "urgency_responsiveness": round(random.uniform(0.1,0.9),3),
        "social_proof_affinity": round(random.uniform(0.2,0.8),3),
        "communication_style": random.choice(COMM_STYLES),
        "narrative_summary": narrative,
        "confidence_score": round(min(0.95, 0.4 + frequency*0.05), 3),
    }

def seed():
    print("Seeding XENO ORACLE data...")
    is_sqlite = "sqlite" in settings.DATABASE_URL_SYNC
    engine_kwargs = {"echo": False, "connect_args": {"check_same_thread": False}} if is_sqlite else {"echo": False}
    engine = create_engine(settings.DATABASE_URL_SYNC, **engine_kwargs)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        if count > 100:
            print(f"Already seeded ({count} customers). Skipping.")
            return
        
        # Products
        prod_objs = []
        for p in PRODUCTS:
            prod = Product(id=str(uuid.uuid4()), sku=p['sku'], name=p['name'], category=p['category'], subcategory=p['subcategory'], price=p['price'], brand=p['brand'])
            session.add(prod)
            prod_objs.append({'id': prod.id, 'category': p['category'], 'price': float(p['price'])})
        session.commit()
        print(f"Created {len(prod_objs)} products")
        
        now = datetime.utcnow()
        for i in range(500):
            first = fake.first_name()
            last = fake.last_name()
            city = random.choice(INDIAN_CITIES)
            cid = str(uuid.uuid4())
            
            r = random.random()
            num_orders = 0 if r < 0.20 else random.randint(1,3) if r < 0.60 else random.randint(4,10) if r < 0.88 else random.randint(11,30)
            
            recency_buckets = [(0,30,0.15),(31,60,0.15),(61,90,0.15),(91,180,0.25),(181,365,0.20),(366,730,0.10)]
            br = random.random(); cumul = 0; min_d, max_d = 30, 90
            for mn, mx, prob in recency_buckets:
                cumul += prob
                if br < cumul: min_d, max_d = mn, mx; break
            
            last_order_days = random.randint(min_d, max_d) if num_orders > 0 else random.randint(200,730)
            orders_data = []
            total_spend = 0.0
            
            for j in range(num_orders):
                days_ago = last_order_days + random.randint(j*30, max(j*30+1, j*90))
                order_date = now - timedelta(days=min(days_ago, 730))
                items = random.sample(prod_objs, random.randint(1,3))
                subtotal = sum(it['price'] * random.randint(1,2) for it in items)
                discount = subtotal * random.uniform(0, 0.2)
                total = subtotal - discount
                total_spend += total
                orders_data.append({'ordered_at': order_date, 'total': total, 'categories': [it['category'] for it in items]})
            
            last_order_at = max((o['ordered_at'] for o in orders_data), default=None)
            
            cust = Customer(id=cid, name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{random.choice(['gmail.com','yahoo.com','outlook.com','rediffmail.com'])}",
                phone=f"9{random.randint(100000000,999999999)}",
                city=city, total_spend=round(total_spend,2), order_count=num_orders,
                last_order_at=last_order_at, created_at=now-timedelta(days=random.randint(100,1000)))
            session.add(cust)
            
            for od in orders_data:
                o = Order(id=str(uuid.uuid4()), customer_id=cid,
                    order_number=f"XENO-{str(uuid.uuid4())[:8].upper()}",
                    status="completed", subtotal=round(od['total']*1.1,2),
                    discount=round(od['total']*0.1,2), total=round(od['total'],2),
                    channel=random.choice(["online","app","store"]), ordered_at=od['ordered_at'])
                session.add(o)
            
            td = generate_twin(cid, orders_data, f"{first} {last}", city)
            twin = CustomerTwin(id=str(uuid.uuid4()), **{k: v for k,v in td.items()})
            twin.updated_at = now
            session.add(twin)
            
            if (i+1) % 100 == 0:
                session.commit()
                print(f"  {i+1}/500 customers...")
        
        session.commit()
        c = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        t = session.execute(text("SELECT COUNT(*) FROM customer_twins")).scalar()
        o = session.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        print(f"Done! Customers: {c}, Twins: {t}, Orders: {o}")
    except Exception as e:
        session.rollback()
        import traceback; traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    seed()
