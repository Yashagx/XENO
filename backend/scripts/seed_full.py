"""
Comprehensive seed script for Xeno Oracle demo data.
Seeds: Campaigns, Segments, Messages (channel data), Insights (Learning Console)
Run inside backend container:
  python /app/seed_full.py
"""
import os, sys, uuid, random, asyncio, json
from datetime import datetime, timedelta
from faker import Faker

sys.path.insert(0, '/app')
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:////app/data/xeno_oracle.db')

from app.database import AsyncSessionLocal
from app.models.campaign import Campaign, Segment, SegmentCustomer
from app.models.message import Message
from app.models.insight import Insight
from app.models.customer import Customer
from sqlalchemy import select

fake = Faker()
Faker.seed(42)

CAMPAIGNS_DATA = [
    {
        "name": "Diwali Mega Sale — VIP Customers",
        "intent": "Re-engage VIP customers who haven't purchased in 60+ days with Diwali exclusive offers, 30% off premium electronics",
        "status": "completed",
        "days_ago": 2.9,
        "open_rate": 0.47, "click_rate": 0.28, "conversion_rate": 0.14, "roi": 3.8,
        "channel": "email", "segment_name": "VIP Lapsed Customers",
        "strategy": {"primary_channel": "email", "tone": "exclusive", "offer_type": "percentage_discount", "discount": "30%"},
        "simulation_result": {"predicted_open_rate": 0.42, "predicted_click_rate": 0.24, "roi": 3.2, "segment_size": 1240},
    },
    {
        "name": "Summer Monsoon Clearance — WhatsApp",
        "intent": "Drive clearance sale for fashion category via WhatsApp, target mid-tier customers in Tier-1 cities",
        "status": "completed",
        "days_ago": 2.5,
        "open_rate": 0.68, "click_rate": 0.42, "conversion_rate": 0.19, "roi": 4.6,
        "channel": "whatsapp", "segment_name": "Fashion Mid-Tier Urban",
        "strategy": {"primary_channel": "whatsapp", "tone": "urgent", "offer_type": "flash_sale", "discount": "Up to 50%"},
        "simulation_result": {"predicted_open_rate": 0.60, "predicted_click_rate": 0.38, "roi": 4.0, "segment_size": 3200},
    },
    {
        "name": "Cart Abandonment Recovery — SMS",
        "intent": "Recover abandoned carts from last 7 days with a limited-time 10% discount coupon",
        "status": "completed",
        "days_ago": 2.1,
        "open_rate": 0.72, "click_rate": 0.34, "conversion_rate": 0.22, "roi": 5.1,
        "channel": "sms", "segment_name": "Cart Abandoners 7D",
        "strategy": {"primary_channel": "sms", "tone": "urgency", "offer_type": "coupon", "discount": "10%"},
        "simulation_result": {"predicted_open_rate": 0.68, "predicted_click_rate": 0.30, "roi": 4.5, "segment_size": 890},
    },
    {
        "name": "New User Onboarding Flow — Email",
        "intent": "Welcome new users who signed up in last 30 days, educate on product features, drive first purchase",
        "status": "completed",
        "days_ago": 1.8,
        "open_rate": 0.55, "click_rate": 0.31, "conversion_rate": 0.18, "roi": 2.9,
        "channel": "email", "segment_name": "New Users 30D",
        "strategy": {"primary_channel": "email", "tone": "friendly", "offer_type": "welcome_bonus", "discount": "15%"},
        "simulation_result": {"predicted_open_rate": 0.50, "predicted_click_rate": 0.28, "roi": 2.5, "segment_size": 567},
    },
    {
        "name": "Churn Prevention — High Risk Customers",
        "intent": "Retain customers with churn probability > 70% by offering personalized win-back incentives",
        "status": "completed",
        "days_ago": 1.4,
        "open_rate": 0.38, "click_rate": 0.19, "conversion_rate": 0.09, "roi": 2.1,
        "channel": "email", "segment_name": "High Churn Risk",
        "strategy": {"primary_channel": "email", "tone": "empathetic", "offer_type": "loyalty_reward", "discount": "20%"},
        "simulation_result": {"predicted_open_rate": 0.35, "predicted_click_rate": 0.16, "roi": 1.8, "segment_size": 421},
    },
    {
        "name": "Weekend Flash Sale — Electronics",
        "intent": "48-hour flash sale on electronics for high-spend customers, push via WhatsApp and SMS combo",
        "status": "completed",
        "days_ago": 1.0,
        "open_rate": 0.64, "click_rate": 0.39, "conversion_rate": 0.21, "roi": 6.2,
        "channel": "whatsapp", "segment_name": "Electronics Enthusiasts",
        "strategy": {"primary_channel": "whatsapp", "tone": "exciting", "offer_type": "flash_sale", "discount": "Up to 40%"},
        "simulation_result": {"predicted_open_rate": 0.58, "predicted_click_rate": 0.35, "roi": 5.5, "segment_size": 1890},
    },
    {
        "name": "Birthday Loyalty Rewards",
        "intent": "Send personalized birthday offers to customers celebrating this month, exclusive 25% off + free gift",
        "status": "running",
        "days_ago": 0.5,
        "open_rate": 0.81, "click_rate": 0.54, "conversion_rate": 0.31, "roi": 7.4,
        "channel": "email", "segment_name": "Birthday Month Customers",
        "strategy": {"primary_channel": "email", "tone": "celebratory", "offer_type": "birthday_special", "discount": "25% + gift"},
        "simulation_result": {"predicted_open_rate": 0.75, "predicted_click_rate": 0.48, "roi": 6.8, "segment_size": 234},
    },
    {
        "name": "Re-engagement — 90D Inactive",
        "intent": "Win back customers inactive for 90+ days with a 'We miss you' campaign, strong incentive",
        "status": "approved",
        "days_ago": 0.2,
        "open_rate": 0.0, "click_rate": 0.0, "conversion_rate": 0.0, "roi": 0.0,
        "channel": "email", "segment_name": "90D Inactive Customers",
        "strategy": {"primary_channel": "email", "tone": "nostalgic", "offer_type": "win_back", "discount": "35%"},
        "simulation_result": {"predicted_open_rate": 0.32, "predicted_click_rate": 0.15, "roi": 2.0, "segment_size": 678},
    },
]

INSIGHT_TEMPLATES = [
    {
        "title": "WhatsApp Outperforms Email by 44% on Open Rate",
        "summary": "WhatsApp campaigns consistently achieve 44% higher open rates vs email. Flash sales on WhatsApp deliver 4.6x ROI vs 3.2x for email. Recommend WhatsApp-first strategy for time-sensitive offers.",
        "type": "channel_insight",
        "impact": "high",
        "recommendation": "Shift 40% of email campaign budget to WhatsApp for flash sales",
    },
    {
        "title": "Cart Abandonment Recovery Shows Highest ROI",
        "summary": "Cart abandonment SMS campaigns achieved 5.1x ROI — the highest of all campaign types. 72% open rate in under 15 minutes of delivery. Suggest automating this as a triggered flow.",
        "type": "performance_insight",
        "impact": "high",
        "recommendation": "Implement real-time cart abandonment trigger within 30 minutes of abandonment",
    },
    {
        "title": "Birthday Campaigns: 31% Conversion Rate",
        "summary": "Birthday personalization drives 31% conversion — 2.2x higher than average (14%). High emotional relevance reduces price sensitivity. Birthday customers spend 1.8x more per transaction.",
        "type": "personalization_insight",
        "impact": "high",
        "recommendation": "Expand birthday program to include anniversary-of-first-purchase campaigns",
    },
    {
        "title": "Simulation Accuracy: 92% for WhatsApp, 88% for Email",
        "summary": "AI simulation predictions are within 6% of actual results for WhatsApp campaigns. Email simulation variance is 8%. Churn campaigns showed highest variance (21%) — improve churn model training.",
        "type": "model_insight",
        "impact": "medium",
        "recommendation": "Feed completed campaign data back into churn prediction model monthly",
    },
    {
        "title": "High Churn Risk Segment Responds to Empathetic Tone",
        "summary": "Empathetic copy achieved 38% open rate vs 29% for discount-first approach in churn prevention. Personalized acknowledgment of lapse reason increases click rate by 18%.",
        "type": "copy_insight",
        "impact": "medium",
        "recommendation": "A/B test 3 copy variants on all churn prevention campaigns before full launch",
    },
    {
        "title": "Tier-1 Cities Drive 67% of Total Revenue",
        "summary": "Mumbai, Delhi, Bangalore, Hyderabad account for 67% of campaign revenue despite being 43% of customer base. Average order value is ₹2.1L higher in Tier-1. Tier-2 growth rate is 34% — fast emerging.",
        "type": "geo_insight",
        "impact": "medium",
        "recommendation": "Launch Tier-2 city expansion campaigns targeting emerging markets in Pune, Ahmedabad",
    },
    {
        "title": "Optimal Send Time: 7-9 PM Weekdays",
        "summary": "Messages sent between 7-9 PM on weekdays achieve 2.3x higher open rates than morning sends. Saturday 11 AM is peak for WhatsApp. Sunday campaigns underperform by 31%.",
        "type": "timing_insight",
        "impact": "medium",
        "recommendation": "Implement ML-based send time optimization using individual customer activity patterns",
    },
    {
        "title": "Electronics Category: Highest LTV Customers",
        "summary": "Electronics buyers have 3.4x higher LTV vs fashion buyers. Average order value ₹18,400 vs ₹4,200. But churn rate is also 2x higher after 6 months if not re-engaged.",
        "type": "category_insight",
        "impact": "high",
        "recommendation": "Create electronics loyalty program with tier-based rewards to reduce 6-month churn",
    },
]


async def seed_campaigns_and_insights():
    async with AsyncSessionLocal() as db:
        # Get some customer IDs
        result = await db.execute(select(Customer).limit(100))
        customers = result.scalars().all()
        if not customers:
            print("No customers found. Run seed_customers.py first.")
            return

        print(f"Found {len(customers)} customers. Seeding campaigns...")
        
        seeded_campaigns = []
        
        for idx, camp_data in enumerate(CAMPAIGNS_DATA):
            days_ago = camp_data["days_ago"]
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            executed_at = created_at + timedelta(hours=2) if camp_data["status"] in ("completed", "running") else None
            completed_at = executed_at + timedelta(hours=6) if camp_data["status"] == "completed" else None

            # Create segment
            seg_size = camp_data["simulation_result"]["segment_size"]
            segment = Segment(
                name=camp_data["segment_name"],
                description=f"Auto-generated segment for {camp_data['name']}",
                filter_config={"intent": camp_data["intent"][:100]},
                customer_count=min(seg_size, len(customers)),
                created_by_intent=camp_data["intent"],
                created_at=created_at,
            )
            db.add(segment)
            await db.flush()

            # Attach some customers to segment
            used_customers = random.sample(customers, min(20, len(customers)))
            for cust in used_customers:
                sc = SegmentCustomer(
                    segment_id=segment.id,
                    customer_id=cust.id,
                    inclusion_reason="High intent match via AI segmentation"
                )
                db.add(sc)

            actual_stats = {}
            if camp_data["status"] in ("completed", "running"):
                actual_stats = {
                    "open_rate": camp_data["open_rate"],
                    "click_rate": camp_data["click_rate"],
                    "conversion_rate": camp_data["conversion_rate"],
                    "roi": camp_data["roi"],
                    "revenue_inr": round(random.uniform(50000, 800000), 0),
                    "total_sent": min(seg_size, len(customers) * 3),
                    "converted": int(min(seg_size, len(customers) * 3) * camp_data["conversion_rate"]),
                }

            agent_trace = [
                {"agent": "intent_agent", "status": "done", "output": {"intent": camp_data["intent"][:80], "confidence": 0.92}},
                {"agent": "segment_agent", "status": "done", "output": {"segment_size": seg_size, "filter_logic": "LTV > median AND recency < 60d"}},
                {"agent": "persona_agent", "status": "done", "output": {"personas": ["Price-Conscious Millennial", "Brand Loyalist", "Occasion Buyer"]}},
                {"agent": "strategy_agent", "status": "done", "output": camp_data["strategy"]},
                {"agent": "copy_agent", "status": "done", "output": {"copies_generated": 3, "selected": "Variant B (highest predicted CTR)"}},
                {"agent": "simulate_agent", "status": "done", "output": camp_data["simulation_result"]},
                {"agent": "execute_agent", "status": "done", "output": {"messages_queued": seg_size, "channel": camp_data["channel"]}},
                {"agent": "learn_agent", "status": "done", "output": {"insight_generated": True, "model_updated": True}},
                {"agent": "insight_agent", "status": "done", "output": {"recommendations": 3}},
            ]

            campaign = Campaign(
                name=camp_data["name"],
                intent=camp_data["intent"],
                segment_id=segment.id,
                status=camp_data["status"],
                strategy=camp_data["strategy"],
                simulation_result=camp_data["simulation_result"],
                personas=[
                    {"name": "Price-Conscious Millennial", "age_range": "22-30", "motivation": "Best deals, FOMO", "channel_pref": camp_data["channel"]},
                    {"name": "Brand Loyalist", "age_range": "30-45", "motivation": "Quality, trust", "channel_pref": "email"},
                    {"name": "Occasion Buyer", "age_range": "25-40", "motivation": "Gifting, events", "channel_pref": "whatsapp"},
                ],
                copies=[
                    {"variant": "A", "subject": f"🎯 {camp_data['name'][:40]} — Exclusive for You", "body": f"Dear {{name}}, {fake.sentence(nb_words=20)}", "predicted_ctr": 0.22},
                    {"variant": "B", "subject": f"⚡ Limited Time: {camp_data['strategy'].get('discount','Special Offer')} OFF", "body": f"Hi {{name}}! {fake.sentence(nb_words=20)}", "predicted_ctr": 0.28},
                    {"variant": "C", "subject": f"Your exclusive {camp_data['strategy'].get('offer_type','offer')} inside", "body": f"Hello {{name}}, {fake.sentence(nb_words=20)}", "predicted_ctr": 0.24},
                ],
                agent_trace=agent_trace,
                actual_stats=actual_stats,
                created_at=created_at,
                executed_at=executed_at,
                completed_at=completed_at,
                created_by_email="marketer@xeno.in",
            )
            db.add(campaign)
            await db.flush()
            seeded_campaigns.append(campaign)

            # Seed messages for completed campaigns
            if camp_data["status"] in ("completed", "running"):
                statuses_pool = (
                    ["opened"] * int(camp_data["open_rate"] * 100) +
                    ["clicked"] * int(camp_data["click_rate"] * 100) +
                    ["converted"] * int(camp_data["conversion_rate"] * 100) +
                    ["sent"] * max(0, 100 - int(camp_data["open_rate"] * 100) - int(camp_data["click_rate"] * 100))
                )
                for cust in used_customers[:15]:
                    msg = Message(
                        campaign_id=campaign.id,
                        customer_id=cust.id,
                        channel=camp_data["channel"],
                        content=f"Hi {cust.name.split()[0]}, {fake.sentence(nb_words=15)}",
                        status=random.choice(statuses_pool),
                        idempotency_key=str(uuid.uuid4()),
                        sent_at=executed_at + timedelta(minutes=random.randint(1, 120)),
                        delivered_at=executed_at + timedelta(minutes=random.randint(2, 130)),
                    )
                    db.add(msg)

            # Seed insight for completed campaigns
            if camp_data["status"] == "completed" and idx < len(INSIGHT_TEMPLATES):
                tmpl = INSIGHT_TEMPLATES[idx]
                insight = Insight(
                    campaign_id=campaign.id,
                    content={
                        "title": tmpl["title"],
                        "summary": tmpl["summary"],
                        "type": tmpl["type"],
                        "impact": tmpl["impact"],
                        "recommendation": tmpl["recommendation"],
                        "metrics": actual_stats,
                        "vs_simulation": {
                            "open_rate_accuracy": f"{round(abs(camp_data['open_rate'] - camp_data['simulation_result']['predicted_open_rate']) / camp_data['simulation_result']['predicted_open_rate'] * 100, 1)}% variance",
                            "roi_accuracy": f"{round(abs(camp_data['roi'] - camp_data['simulation_result']['roi']) / camp_data['simulation_result']['roi'] * 100, 1)}% variance",
                        },
                    },
                    generated_at=completed_at or created_at,
                )
                db.add(insight)

        # Seed extra insights (non-campaign-specific — for Learning Console)
        for i, tmpl in enumerate(INSIGHT_TEMPLATES[len(CAMPAIGNS_DATA):] + INSIGHT_TEMPLATES[-2:]):
            if seeded_campaigns:
                ref_campaign = seeded_campaigns[i % len(seeded_campaigns)]
                insight = Insight(
                    campaign_id=ref_campaign.id,
                    content={
                        "title": tmpl["title"],
                        "summary": tmpl["summary"],
                        "type": tmpl["type"],
                        "impact": tmpl["impact"],
                        "recommendation": tmpl["recommendation"],
                        "generated_by": "learn_agent",
                        "confidence": round(random.uniform(0.82, 0.97), 2),
                    },
                    generated_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                )
                db.add(insight)

        await db.commit()
        print(f"✅ Seeded {len(CAMPAIGNS_DATA)} campaigns, segments, messages, and {len(INSIGHT_TEMPLATES)} insights!")
        print("   → Learning Console now has rich data!")
        print("   → Campaign list has completed/running/approved entries!")


if __name__ == "__main__":
    asyncio.run(seed_campaigns_and_insights())
