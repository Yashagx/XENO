"""
XENO Oracle — Full Demo Data Seeder v2
Seeds campaigns with correct actual_stats + simulation_result schemas
Seeds insights with full learning console schema
Run: python /app/seed_demo.py
"""
import os, sys, uuid, random, asyncio
from datetime import datetime, timedelta
from faker import Faker

sys.path.insert(0, '/app')
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:////app/data/xeno_oracle.db')

from app.database import AsyncSessionLocal
from app.models.campaign import Campaign, Segment, SegmentCustomer
from app.models.message import Message
from app.models.insight import Insight
from app.models.customer import Customer
from sqlalchemy import select, delete

fake = Faker()
Faker.seed(99)

CAMPAIGNS = [
    {
        "name": "Diwali Mega Sale — VIP Customers",
        "intent": "Re-engage VIP customers who haven't purchased in 60+ days with Diwali exclusive offers, 30% off premium electronics",
        "status": "completed", "days_ago": 2.9, "channel": "email",
        "segment_name": "VIP Lapsed Customers", "seg_size": 1240,
        "actual": {"open_rate": 0.47, "click_rate": 0.28, "conversion_rate": 0.14, "roi": 3.8, "revenue_inr": 684000, "total_sent": 1240, "converted": 174},
        "sim":    {"open_rate": {"p50": 0.42, "p10": 0.30, "p90": 0.54}, "click_rate": {"p50": 0.24}, "revenue_inr": {"p50": 580000}, "roi": 3.2, "predicted_open_rate": 0.42, "predicted_click_rate": 0.24, "segment_size": 1240},
        "strategy": {"primary_channel": "email", "tone": "exclusive", "offer_type": "percentage_discount", "discount": "30%"},
        "insight": {
            "executive_summary": "Diwali VIP campaign exceeded predictions with 47% open rate (+5pp vs forecast). Personalized subject lines with customer name drove 12% higher CTR. ₹6.84L revenue generated — 119% of target. Festival timing proved optimal.",
            "key_insights": [
                "Personalized subject lines ('Priya, your exclusive Diwali gift awaits') outperformed generic by 31%",
                "Evening sends (7–9 PM) achieved 2.1x open rate vs morning sends in same campaign",
                "Electronics category drove 68% of revenue despite being 40% of catalog",
                "Customers with 2+ prior purchases converted at 3.4x rate vs single-purchase customers"
            ],
            "next_campaign_recommendations": [
                "Launch VIP tier programme — top 15% generate 58% of revenue",
                "Test WhatsApp for next festival campaign — predicted +44% open rate",
                "Create electronics-first segment for Q1 re-engagement"
            ],
            "winning_element": "Personalized festival subject line + evening send time",
            "improvement_area": "Click-to-conversion gap — add urgency timer in email body",
            "actual_stats": {"open_rate": 0.47, "click_rate": 0.28, "conversion_rate": 0.14, "total_sent": 1240, "revenue_inr": 684000},
            "vs_simulation": {"open_rate_variance": "+11.9%", "roi_variance": "+18.8%", "revenue_variance": "+17.9%"},
            "trend_data": {
                "hourly_opens": [12, 28, 45, 62, 89, 134, 201, 312, 289, 245, 198, 156, 134, 112, 98, 89, 234, 445, 389, 312, 256, 189, 134, 89],
                "daily_conversions": [42, 38, 29, 22, 18, 15, 10],
                "channel_split": {"email": 100}
            }
        }
    },
    {
        "name": "Summer Monsoon Clearance — WhatsApp",
        "intent": "Drive clearance sale for fashion category via WhatsApp, target mid-tier customers in Tier-1 cities",
        "status": "completed", "days_ago": 2.5, "channel": "whatsapp",
        "segment_name": "Fashion Mid-Tier Urban", "seg_size": 3200,
        "actual": {"open_rate": 0.68, "click_rate": 0.42, "conversion_rate": 0.19, "roi": 4.6, "revenue_inr": 1280000, "total_sent": 3200, "converted": 608},
        "sim":    {"open_rate": {"p50": 0.60, "p10": 0.48, "p90": 0.72}, "click_rate": {"p50": 0.38}, "revenue_inr": {"p50": 1050000}, "roi": 4.0, "predicted_open_rate": 0.60, "predicted_click_rate": 0.38, "segment_size": 3200},
        "strategy": {"primary_channel": "whatsapp", "tone": "urgent", "offer_type": "flash_sale", "discount": "Up to 50%"},
        "insight": {
            "executive_summary": "WhatsApp flash sale delivered highest volume campaign ever — ₹12.8L revenue, 4.6x ROI. 68% open rate confirms WhatsApp as primary channel for time-sensitive offers. Mumbai + Delhi drove 71% of conversions.",
            "key_insights": [
                "WhatsApp open rate (68%) was 44% higher than email benchmark (47%) for comparable segments",
                "Countdown timer GIF increased click-to-conversion rate by 28% vs static image",
                "Mumbai customers converted at 23% vs 17% national average — Tier-1 preference confirmed",
                "Fashion category shows highest urgency-responsiveness — flash format ideal"
            ],
            "next_campaign_recommendations": [
                "Scale WhatsApp to all flash/clearance campaigns — 44% open rate advantage is significant",
                "Create Mumbai/Delhi premium micro-segment for higher-AOV fashion drops",
                "A/B test video vs GIF creative in next WhatsApp campaign"
            ],
            "winning_element": "Countdown timer GIF + WhatsApp native format",
            "improvement_area": "Tier-2 city conversion lag — needs city-specific offers",
            "actual_stats": {"open_rate": 0.68, "click_rate": 0.42, "conversion_rate": 0.19, "total_sent": 3200, "revenue_inr": 1280000},
            "vs_simulation": {"open_rate_variance": "+13.3%", "roi_variance": "+15.0%", "revenue_variance": "+21.9%"},
            "trend_data": {
                "hourly_opens": [8, 15, 22, 34, 48, 89, 156, 423, 567, 489, 378, 312, 289, 256, 234, 312, 489, 712, 634, 512, 389, 278, 189, 112],
                "daily_conversions": [189, 156, 112, 78, 45, 18, 10],
                "channel_split": {"whatsapp": 100}
            }
        }
    },
    {
        "name": "Cart Abandonment Recovery — SMS",
        "intent": "Recover abandoned carts from last 7 days with a limited-time 10% discount coupon via SMS",
        "status": "completed", "days_ago": 2.1, "channel": "sms",
        "segment_name": "Cart Abandoners 7D", "seg_size": 890,
        "actual": {"open_rate": 0.72, "click_rate": 0.34, "conversion_rate": 0.22, "roi": 5.1, "revenue_inr": 412000, "total_sent": 890, "converted": 196},
        "sim":    {"open_rate": {"p50": 0.68, "p10": 0.55, "p90": 0.80}, "click_rate": {"p50": 0.30}, "revenue_inr": {"p50": 360000}, "roi": 4.5, "predicted_open_rate": 0.68, "predicted_click_rate": 0.30, "segment_size": 890},
        "strategy": {"primary_channel": "sms", "tone": "urgency", "offer_type": "coupon", "discount": "10%"},
        "insight": {
            "executive_summary": "Cart abandonment SMS achieved best-in-class 5.1x ROI — highest of all campaign types this quarter. 22% conversion rate is 1.6x the benchmark. SMS urgency format proves optimal for recovery flows.",
            "key_insights": [
                "SMS delivered within 15 minutes of cart abandonment achieved 31% conversion vs 18% for 1-hour delay",
                "Single-item carts converted 2.4x better than multi-item — simplify recovery message per item",
                "Coupon code format 'CART10' outperformed generic '10% off' in CTR by 22%",
                "Electronics abandoners had highest cart value (avg ₹8,400) — segment for premium recovery flow"
            ],
            "next_campaign_recommendations": [
                "Automate cart abandonment as real-time trigger within 10–30 minute window",
                "Create tiered recovery: 10% off at 15 min → 15% off at 1 hr → 20% off at 24 hrs",
                "Build electronics-specific cart recovery with product image in WhatsApp"
            ],
            "winning_element": "15-minute SMS trigger with single clear CTA",
            "improvement_area": "Multi-item cart complexity — needs item-specific personalisation",
            "actual_stats": {"open_rate": 0.72, "click_rate": 0.34, "conversion_rate": 0.22, "total_sent": 890, "revenue_inr": 412000},
            "vs_simulation": {"open_rate_variance": "+5.9%", "roi_variance": "+13.3%", "revenue_variance": "+14.4%"},
            "trend_data": {
                "hourly_opens": [0, 0, 0, 0, 0, 0, 12, 34, 89, 134, 112, 89, 67, 56, 45, 38, 34, 45, 56, 67, 45, 34, 22, 12],
                "daily_conversions": [98, 56, 24, 12, 4, 2, 0],
                "channel_split": {"sms": 100}
            }
        }
    },
    {
        "name": "New User Onboarding Flow — Email",
        "intent": "Welcome new users who signed up in last 30 days, educate on product features, drive first purchase",
        "status": "completed", "days_ago": 1.8, "channel": "email",
        "segment_name": "New Users 30D", "seg_size": 567,
        "actual": {"open_rate": 0.55, "click_rate": 0.31, "conversion_rate": 0.18, "roi": 2.9, "revenue_inr": 198000, "total_sent": 567, "converted": 102},
        "sim":    {"open_rate": {"p50": 0.50, "p10": 0.38, "p90": 0.62}, "click_rate": {"p50": 0.28}, "revenue_inr": {"p50": 175000}, "roi": 2.5, "predicted_open_rate": 0.50, "predicted_click_rate": 0.28, "segment_size": 567},
        "strategy": {"primary_channel": "email", "tone": "friendly", "offer_type": "welcome_bonus", "discount": "15%"},
        "insight": {
            "executive_summary": "New user onboarding email beat forecast by 10pp open rate (55% actual vs 50% predicted). First-purchase conversion at 18% confirms welcome bonus is effective activation lever. ₹1.98L revenue from 102 first-time buyers.",
            "key_insights": [
                "Users who clicked product recommendations converted 3.2x more than those who clicked generic homepage CTA",
                "3-email drip (Day 0, Day 3, Day 7) showed 45% higher lifetime engagement vs single welcome email",
                "Mobile-first users (67% of segment) preferred simple single-column layout with large CTA button",
                "Category preference from signup form predicted first purchase with 74% accuracy"
            ],
            "next_campaign_recommendations": [
                "Implement automated 5-step onboarding drip sequence for all new signups",
                "Personalise product recommendations based on signup category preference",
                "Add SMS backup for users who don't open email within 48 hours"
            ],
            "winning_element": "Category-personalised product recommendations in email body",
            "improvement_area": "Day 7 drop-off — needs stronger re-engagement hook at end of onboarding",
            "actual_stats": {"open_rate": 0.55, "click_rate": 0.31, "conversion_rate": 0.18, "total_sent": 567, "revenue_inr": 198000},
            "vs_simulation": {"open_rate_variance": "+10.0%", "roi_variance": "+16.0%", "revenue_variance": "+13.1%"},
            "trend_data": {
                "hourly_opens": [56, 89, 123, 145, 134, 112, 89, 78, 67, 56, 45, 38, 34, 29, 25, 22, 34, 45, 56, 67, 45, 34, 22, 12],
                "daily_conversions": [45, 28, 15, 8, 4, 2, 0],
                "channel_split": {"email": 100}
            }
        }
    },
    {
        "name": "Churn Prevention — High Risk Customers",
        "intent": "Retain customers with churn probability > 70% by offering personalized win-back incentives via email",
        "status": "completed", "days_ago": 1.4, "channel": "email",
        "segment_name": "High Churn Risk >70%", "seg_size": 421,
        "actual": {"open_rate": 0.38, "click_rate": 0.19, "conversion_rate": 0.09, "roi": 2.1, "revenue_inr": 94000, "total_sent": 421, "converted": 38},
        "sim":    {"open_rate": {"p50": 0.35, "p10": 0.24, "p90": 0.46}, "click_rate": {"p50": 0.16}, "revenue_inr": {"p50": 82000}, "roi": 1.8, "predicted_open_rate": 0.35, "predicted_click_rate": 0.16, "segment_size": 421},
        "strategy": {"primary_channel": "email", "tone": "empathetic", "offer_type": "loyalty_reward", "discount": "20%"},
        "insight": {
            "executive_summary": "Churn prevention campaign retained 38 high-risk customers (9% conversion). Empathetic tone significantly outperformed discount-first approach in open rate. ₹94K revenue from customers who would have churned — LTV preservation estimated ₹4.7L.",
            "key_insights": [
                "Empathetic subject line ('We miss you, Priya') achieved 38% open vs 29% for discount-first subject",
                "Customers with 3+ previous orders were 2.8x more likely to re-engage than single-purchase customers",
                "Offering loyalty points instead of discount had 18% higher perceived value in A/B test",
                "Churn model accuracy: 84% of predicted churners actually hadn't purchased in 90+ days"
            ],
            "next_campaign_recommendations": [
                "Launch predictive churn prevention at 60% probability threshold — earlier intervention",
                "Test loyalty points vs cash discount — points show 18% higher engagement",
                "Add phone call outreach for ultra-high-value customers (top 5% LTV) at risk"
            ],
            "winning_element": "Empathetic tone + acknowledgment of customer absence",
            "improvement_area": "Low conversion (9%) — needs stronger incentive or multi-touch approach",
            "actual_stats": {"open_rate": 0.38, "click_rate": 0.19, "conversion_rate": 0.09, "total_sent": 421, "revenue_inr": 94000},
            "vs_simulation": {"open_rate_variance": "+8.6%", "roi_variance": "+16.7%", "revenue_variance": "+14.6%"},
            "trend_data": {
                "hourly_opens": [34, 56, 78, 89, 82, 74, 67, 59, 52, 45, 38, 34, 29, 25, 22, 19, 23, 28, 34, 38, 29, 22, 15, 9],
                "daily_conversions": [18, 12, 5, 2, 1, 0, 0],
                "channel_split": {"email": 100}
            }
        }
    },
    {
        "name": "Weekend Flash Sale — Electronics",
        "intent": "48-hour flash sale on electronics for high-spend customers, push via WhatsApp and SMS combo",
        "status": "completed", "days_ago": 1.0, "channel": "whatsapp",
        "segment_name": "Electronics High-Spend", "seg_size": 1890,
        "actual": {"open_rate": 0.64, "click_rate": 0.39, "conversion_rate": 0.21, "roi": 6.2, "revenue_inr": 2340000, "total_sent": 1890, "converted": 397},
        "sim":    {"open_rate": {"p50": 0.58, "p10": 0.44, "p90": 0.72}, "click_rate": {"p50": 0.35}, "revenue_inr": {"p50": 1980000}, "roi": 5.5, "predicted_open_rate": 0.58, "predicted_click_rate": 0.35, "segment_size": 1890},
        "strategy": {"primary_channel": "whatsapp", "tone": "exciting", "offer_type": "flash_sale", "discount": "Up to 40%"},
        "insight": {
            "executive_summary": "Best revenue campaign this quarter — ₹23.4L in 48 hours, 6.2x ROI. Electronics + WhatsApp combination proves highest-value pairing. Average order value ₹5,894 vs ₹3,200 platform average. Exceeded forecast by ₹3.6L.",
            "key_insights": [
                "WhatsApp + SMS dual-channel reach increased total conversion by 34% vs WhatsApp-only estimate",
                "Average order value ₹5,894 — 84% higher than platform average, confirming high-intent segment quality",
                "Saturday 11 AM send peaked at 712 opens/hour — optimal weekend electronics send time",
                "Product-specific messages (e.g., 'Your saved iPhone is now ₹8,000 cheaper') converted 4.1x better"
            ],
            "next_campaign_recommendations": [
                "Run monthly electronics flash sale on last weekend of month — demand pattern confirmed",
                "Implement saved-product triggered messages for personalised flash alerts",
                "Expand dual-channel (WhatsApp + SMS) to all high-value campaigns"
            ],
            "winning_element": "Product-specific personalisation + dual-channel reach",
            "improvement_area": "Post-purchase upsell opportunity missed — add accessory recommendation",
            "actual_stats": {"open_rate": 0.64, "click_rate": 0.39, "conversion_rate": 0.21, "total_sent": 1890, "revenue_inr": 2340000},
            "vs_simulation": {"open_rate_variance": "+10.3%", "roi_variance": "+12.7%", "revenue_variance": "+18.2%"},
            "trend_data": {
                "hourly_opens": [34, 22, 12, 8, 6, 4, 89, 234, 512, 712, 634, 512, 423, 378, 312, 289, 456, 634, 589, 512, 423, 312, 234, 156],
                "daily_conversions": [189, 134, 45, 18, 8, 3, 0],
                "channel_split": {"whatsapp": 70, "sms": 30}
            }
        }
    },
    {
        "name": "Birthday Loyalty Rewards",
        "intent": "Send personalized birthday offers to customers celebrating this month — exclusive 25% off + free gift",
        "status": "running", "days_ago": 0.5, "channel": "email",
        "segment_name": "Birthday Month Customers", "seg_size": 234,
        "actual": {"open_rate": 0.81, "click_rate": 0.54, "conversion_rate": 0.31, "roi": 7.4, "revenue_inr": 189000, "total_sent": 234, "converted": 72},
        "sim":    {"open_rate": {"p50": 0.75, "p10": 0.62, "p90": 0.88}, "click_rate": {"p50": 0.48}, "revenue_inr": {"p50": 162000}, "roi": 6.8, "predicted_open_rate": 0.75, "predicted_click_rate": 0.48, "segment_size": 234},
        "strategy": {"primary_channel": "email", "tone": "celebratory", "offer_type": "birthday_special", "discount": "25% + free gift"},
        "insight": None
    },
    {
        "name": "Re-engagement — 90D Inactive",
        "intent": "Win back customers inactive for 90+ days with a 'We miss you' campaign and strong incentive",
        "status": "approved", "days_ago": 0.2, "channel": "email",
        "segment_name": "90D Inactive Customers", "seg_size": 678,
        "actual": {"open_rate": 0.0, "click_rate": 0.0, "conversion_rate": 0.0, "roi": 0.0, "revenue_inr": 0, "total_sent": 0, "converted": 0},
        "sim":    {"open_rate": {"p50": 0.32, "p10": 0.22, "p90": 0.42}, "click_rate": {"p50": 0.15}, "revenue_inr": {"p50": 245000}, "roi": 2.0, "predicted_open_rate": 0.32, "predicted_click_rate": 0.15, "segment_size": 678},
        "strategy": {"primary_channel": "email", "tone": "nostalgic", "offer_type": "win_back", "discount": "35%"},
        "insight": None
    },
]


async def clear_and_reseed():
    async with AsyncSessionLocal() as db:
        # Get customers
        result = await db.execute(select(Customer).limit(100))
        customers = result.scalars().all()
        if not customers:
            print("ERROR: No customers found. Run seed_customers.py first.")
            return

        # Clear existing campaigns/insights (keep customers)
        await db.execute(delete(Insight))
        await db.execute(delete(Message))
        await db.execute(delete(SegmentCustomer))
        await db.execute(delete(Campaign))
        await db.execute(delete(Segment))
        await db.commit()
        print(f"Cleared old campaign data. Seeding with {len(customers)} customers...")

        seeded = []
        for camp_data in CAMPAIGNS:
            days_ago = camp_data["days_ago"]
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            executed_at = created_at + timedelta(hours=2) if camp_data["status"] in ("completed", "running") else None
            completed_at = executed_at + timedelta(hours=48) if camp_data["status"] == "completed" else None

            # Segment
            segment = Segment(
                name=camp_data["segment_name"],
                description=f"AI-generated segment for {camp_data['name']}",
                filter_config={"intent_keywords": camp_data["intent"][:80]},
                customer_count=min(camp_data["seg_size"], len(customers)),
                created_by_intent=camp_data["intent"],
                created_at=created_at,
            )
            db.add(segment)
            await db.flush()

            used_customers = random.sample(customers, min(20, len(customers)))
            for cust in used_customers:
                db.add(SegmentCustomer(segment_id=segment.id, customer_id=cust.id, inclusion_reason="AI segmentation match"))

            campaign = Campaign(
                name=camp_data["name"],
                intent=camp_data["intent"],
                segment_id=segment.id,
                status=camp_data["status"],
                strategy=camp_data["strategy"],
                simulation_result=camp_data["sim"],
                actual_stats=camp_data["actual"],
                personas=[
                    {"name": "Price-Conscious Millennial", "age_range": "22-30", "motivation": "Best value, FOMO urgency", "channel_pref": camp_data["channel"]},
                    {"name": "Brand Loyalist", "age_range": "30-45", "motivation": "Quality, trust, exclusivity", "channel_pref": "email"},
                    {"name": "Occasion Buyer", "age_range": "25-40", "motivation": "Gifting, events, occasions", "channel_pref": "whatsapp"},
                ],
                copies=[
                    {"variant": "A", "subject": f"🎯 {camp_data['name'][:40]} — Exclusive for You", "predicted_ctr": 0.22, "selected": False},
                    {"variant": "B", "subject": f"⚡ {camp_data['strategy'].get('discount','Special Offer')} OFF — Limited Time", "predicted_ctr": 0.28, "selected": True},
                    {"variant": "C", "subject": f"Your personal {camp_data['strategy'].get('offer_type','offer')} is waiting", "predicted_ctr": 0.24, "selected": False},
                ],
                agent_trace=[
                    {"agent": "intent_agent",   "status": "done", "output": {"intent": camp_data["intent"][:80], "confidence": round(random.uniform(0.88, 0.97), 2)}},
                    {"agent": "segment_agent",  "status": "done", "output": {"segment_size": camp_data["seg_size"], "filter_logic": "LTV + recency + category affinity"}},
                    {"agent": "persona_agent",  "status": "done", "output": {"personas_identified": 3}},
                    {"agent": "strategy_agent", "status": "done", "output": camp_data["strategy"]},
                    {"agent": "copy_agent",     "status": "done", "output": {"copies_generated": 3, "selected_variant": "B"}},
                    {"agent": "simulate_agent", "status": "done", "output": camp_data["sim"]},
                    {"agent": "execute_agent",  "status": "done", "output": {"messages_queued": camp_data["seg_size"], "channel": camp_data["channel"]}},
                    {"agent": "learn_agent",    "status": "done", "output": {"insight_generated": camp_data["insight"] is not None}},
                    {"agent": "insight_agent",  "status": "done", "output": {"recommendations": 3}},
                ],
                created_at=created_at,
                executed_at=executed_at,
                completed_at=completed_at,
                created_by_email="marketer@xeno.in",
            )
            db.add(campaign)
            await db.flush()
            seeded.append((campaign, camp_data))

            # Seed messages for completed/running campaigns
            if camp_data["status"] in ("completed", "running") and executed_at:
                actual = camp_data["actual"]
                statuses_pool = (
                    ["opened"] * int(actual["open_rate"] * 50) +
                    ["clicked"] * int(actual["click_rate"] * 50) +
                    ["converted"] * int(actual["conversion_rate"] * 50) +
                    ["sent"] * max(1, 50 - int(actual["open_rate"] * 50) - int(actual["click_rate"] * 50))
                )
                for cust in used_customers[:15]:
                    db.add(Message(
                        campaign_id=campaign.id,
                        customer_id=cust.id,
                        channel=camp_data["channel"],
                        content=f"Hi {cust.name.split()[0]}, {fake.sentence(nb_words=12)}",
                        status=random.choice(statuses_pool),
                        idempotency_key=str(uuid.uuid4()),
                        sent_at=executed_at + timedelta(minutes=random.randint(1, 60)),
                        delivered_at=executed_at + timedelta(minutes=random.randint(2, 70)),
                    ))

            # Seed insight for completed campaigns
            if camp_data["status"] == "completed" and camp_data["insight"]:
                ins_data = camp_data["insight"]
                db.add(Insight(
                    campaign_id=campaign.id,
                    content={
                        **ins_data,
                        "campaign_name": camp_data["name"],
                        "channel": camp_data["channel"],
                        "segment": camp_data["segment_name"],
                        "segment_size": camp_data["seg_size"],
                        "generated_by": "learn_agent + insight_agent",
                        "confidence": round(random.uniform(0.88, 0.97), 2),
                    },
                    generated_at=completed_at or created_at,
                ))

        await db.commit()

        completed = [c for c in CAMPAIGNS if c["status"] == "completed"]
        print(f"✅ Seeded {len(CAMPAIGNS)} campaigns ({len(completed)} completed with full stats)")
        print(f"   → {len(completed)} insights with trend data seeded in Learning Console")
        print(f"   → All campaigns have actual open/click/revenue stats")
        print(f"   → Simulation vs actual comparison data included")


if __name__ == "__main__":
    asyncio.run(clear_and_reseed())
