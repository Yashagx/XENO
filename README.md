<div align="center">

# ✦ XENO ORACLE
### Autonomous AI Marketing Intelligence System

**v2.0 · Built for Xeno FDE Internship Assignment 2026**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-3.87.12.186%3A3000-6366f1?style=for-the-badge&logo=vercel&logoColor=white)](http://3.87.12.186:3000)
[![Backend API](https://img.shields.io/badge/API%20Docs-8000%2Fdocs-10b981?style=for-the-badge&logo=fastapi&logoColor=white)](http://3.87.12.186:8000/docs)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![AWS](https://img.shields.io/badge/AWS-EC2%20%2B%205%20Services-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

> *"A marketer types one sentence. Ten AI agents think, plan, simulate, and execute — autonomously."*

<br/>

![Oracle Command Center](https://img.shields.io/badge/Oracle%20Command%20Center-Live-6366f1?style=flat-square)
![10 AI Agents](https://img.shields.io/badge/AI%20Agents-10%20Specialized-8b5cf6?style=flat-square)
![Digital Twins](https://img.shields.io/badge/Digital%20Twins-500%20Modelled-10b981?style=flat-square)
![AWS Services](https://img.shields.io/badge/AWS%20Services-S3%20%7C%20SES%20%7C%20SNS%20%7C%20CW%20%7C%20SM-FF9900?style=flat-square)

</div>

---

## What Is Xeno Oracle?

Xeno Oracle is **not a CRM**. It is an **Autonomous Marketing Intelligence System** — a multi-agent AI operating system for growth teams that eliminates the gap between marketing intent and campaign execution.

A marketer types one goal in plain English:

```
"Re-engage high-value customers who haven't bought in 90 days before the summer sale"
```

Xeno Oracle autonomously handles everything else:

```
Intent → Memory Retrieval → Segmentation → Persona Modeling → Strategy
      → Copywriting → Pre-launch Simulation → Execution → Learning → Insights
```

No segment builders. No copy editors. No channel pickers. Just results.

---

## The 10-Agent Pipeline

```
Natural Language Intent
         │
         ▼
┌─────────────────────┐
│  1. Intent Parser   │  Groq LLM extracts: goal, churn window, LTV tier, channel, occasion
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. Memory Agent    │  Semantic + structured query across 500 customer digital twins
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  3. Segmentation    │  Builds a precise, named, explainable audience segment
│     Agent           │  with inclusion/exclusion reasoning per customer
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  4. Persona Agent   │  Clusters segment into 2–5 behavioural personas
│                     │  (e.g. "Weekend Browser", "Deal Hunter", "Lapsed VIP")
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  5. Strategy Agent  │  Designs channel mix, timing, campaign structure
│                     │  using historical campaign performance as context
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  6. Copywriter      │  Writes persona-specific messages per channel
│     Agent           │  tailored to communication style and brand voice
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  7. Simulator Agent │  Pre-launch prediction: open rate, click rate,
│  (Time Machine)     │  revenue, ROI with P10/P50/P90 confidence bands
└──────────┬──────────┘
           │  ← Marketer reviews + approves here
           ▼
┌─────────────────────┐
│  8. Execution Agent │  Dispatches messages to Channel Service
│                     │  per customer with idempotency guarantees
└──────────┬──────────┘
           ▼  ← Async callbacks: delivered → opened → clicked → converted
┌─────────────────────┐
│  9. Learning Agent  │  Updates Digital Twins with EWMA affinity scores
│                     │  Compares actual vs predicted outcomes
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  10. Insight Agent  │  Generates plain-English post-campaign intelligence
│                     │  What worked · What to improve · Next campaign recs
└─────────────────────┘
```

Every agent step streams live to the frontend via **Redis Pub/Sub → Server-Sent Events**. The marketer watches the AI think in real time.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Next.js 16 Frontend                           │
│  Oracle Command Center · Campaigns · Twin Explorer · Insights   │
│  XenoPilot Widget · AWS Status Panel                            │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST + SSE (Server-Sent Events)
┌───────────────────────────▼──────────────────────────────────────┐
│                  FastAPI Backend (port 8000)                     │
│   10 AI Agents · JWT Auth (RBAC) · SQLite · Redis · AWS SDK     │
└────────┬──────────────────┬───────────────────────┬──────────────┘
         │                  │                       │
    ┌────▼────┐      ┌──────▼──────┐       ┌───────▼──────┐
    │ SQLite  │      │    Redis    │       │   Groq API   │
    │ (data)  │      │ (pub/sub)   │       │  (LLM core)  │
    └─────────┘      └─────────────┘       └──────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────┐
│              Channel Service (port 8001)                         │
│  Simulates Email · SMS · WhatsApp · RCS delivery lifecycle       │
│  Fires callbacks: delivered → opened → clicked → converted       │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│                    AWS Services Layer                            │
│  S3 (exports)  · SES (emails)  · SNS (notifications)           │
│  CloudWatch (metrics)  · Secrets Manager (key management)       │
└───────────────────────────────────────────────────────────────────┘
```

---

## Customer Digital Twin System

Every customer has a living **Digital Twin** — a structured, versioned memory object that evolves with every campaign interaction.

```python
CustomerTwin:
  ├── channel_affinity     # {"email": 0.74, "sms": 0.31, "whatsapp": 0.82}
  ├── category_affinity    # {"footwear": 0.91, "accessories": 0.54}
  ├── churn_probability    # 0.0 – 1.0 (updated after every campaign)
  ├── predicted_ltv_90d   # Expected spend in next 90 days (₹)
  ├── purchase_intent      # How ready to buy right now
  ├── price_sensitivity    # 0=insensitive, 1=highly price-sensitive
  ├── urgency_response     # Responds to "last chance" messaging?
  ├── communication_style  # casual / formal / enthusiastic / minimal
  ├── narrative_summary    # LLM-generated 2-sentence customer description
  └── version             # Audit trail of every twin update
```

Twins are updated after every campaign via EWMA (α=0.3) on engagement signals. Full version history stored in `twin_audit_log`.

---

## AWS Integration

All 5 AWS services are integrated with **graceful fallback** — the app runs fully without AWS credentials, and each service activates when configured.

| Service | What It Does | When It Fires |
|---|---|---|
| **S3** | Campaign JSON exports, customer CSV import audit trail | On "Export Report" click; on CSV upload |
| **SES** | Sends campaign completion summary to marketer's email | When Learning Agent finishes |
| **SNS** | Publishes to notification topic | Campaign "Ready" + Campaign "Completed" |
| **CloudWatch** | API latency metrics, campaign KPIs, agent error counts | Every API call + every agent run |
| **Secrets Manager** | Fetches `GROQ_API_KEY` + `JWT_SECRET` at startup | Backend startup (overrides .env) |

```bash
# Verify all AWS services after deployment
curl -H "Authorization: Bearer <admin_token>" \
  http://3.87.12.186:8000/api/v1/aws/status

# Expected:
{
  "s3":              { "connected": true, "bucket": "xeno-oracle-data" },
  "ses":             { "connected": true, "sender": "you@email.com" },
  "sns":             { "connected": true, "topic_arn": "arn:aws:sns:..." },
  "cloudwatch":      { "connected": true, "namespace": "XenoOracle" },
  "secrets_manager": { "connected": true, "secret_loaded": true }
}
```

---

## XenoPilot — Conversational CRM Intelligence

A floating AI chat widget (✦ button, bottom-right) on every page. Queries real SQLite data, not a mock layer.

```
You:        "Who are my top 10 customers by LTV?"
XenoPilot:  "Your top customer is Oni Yohannan (Mumbai, 27 orders, ₹5.2L total spend)
             followed by Janya Baral (Vadodara, ₹5.2L). Combined, your top 10
             customers account for ₹48.3L — 56% of total platform revenue.
             → Recommend targeting them with a VIP early-access campaign."

             [→ Create Campaign]  [→ View Twins]
```

Starter questions, conversation history, and suggested action links included.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| **Animations** | Framer Motion |
| **Charts** | Recharts |
| **Icons** | Lucide React |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy (async), Pydantic v2 |
| **AI / LLM** | Groq API — `llama-3.3-70b-versatile` |
| **Embeddings** | `text-embedding-004` (semantic twin search) |
| **Database** | SQLite via `aiosqlite` (persistent Docker volume) |
| **Message Broker** | Redis 7 (Pub/Sub + Streams for SSE) |
| **AWS SDK** | `boto3` — S3, SES, SNS, CloudWatch, Secrets Manager |
| **Auth** | JWT (HS256), `python-jose`, `passlib[bcrypt]` |
| **Deployment** | Docker Compose on AWS EC2 t2.medium |
| **Channel Service** | FastAPI microservice, async callbacks, failure injection |

---

## Project Structure

```
XENO/
├── .env.production          # Production secrets (never committed)
├── .gitignore
├── docker-compose.yml       # 4-container production setup
├── deploy.sh                # One-command EC2 deployment
├── restart.sh               # Quick container restart
├── logs.sh                  # Live log tailing from EC2
│
├── backend/
│   ├── Dockerfile.backend
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI app, lifespan, CORS, middleware
│       ├── config.py        # Pydantic settings
│       ├── database.py      # SQLAlchemy async engine
│       ├── redis_client.py  # Redis with graceful fallback
│       ├── models/
│       │   ├── auth.py      # User model (RBAC)
│       │   ├── customer.py  # Customer + CustomerTwin + TwinAuditLog
│       │   ├── campaign.py  # Campaign + Segment + SegmentCustomer
│       │   ├── message.py   # Message + CampaignEvent
│       │   ├── order.py     # Purchase history
│       │   └── insight.py   # Post-campaign AI analysis
│       ├── agents/
│       │   ├── orchestrator.py       # Pipeline state machine
│       │   ├── state.py              # CampaignState TypedDict
│       │   ├── llm_client.py         # Groq API wrapper
│       │   ├── memory_agent.py
│       │   ├── segmentation_agent.py
│       │   ├── persona_agent.py
│       │   ├── strategy_agent.py
│       │   ├── copywriter_agent.py
│       │   ├── simulator_agent.py
│       │   ├── execution_agent.py
│       │   ├── learning_agent.py
│       │   ├── insight_agent.py
│       │   └── xenopilot_agent.py    # Conversational CRM intelligence
│       ├── api/v1/
│       │   ├── auth.py        # Login, register, /me
│       │   ├── campaigns.py   # CRUD + approve + S3 export
│       │   ├── customers.py   # List + stats + CSV import
│       │   ├── events.py      # SSE streaming endpoint
│       │   ├── twins.py       # Digital twin browser + search
│       │   ├── insights.py    # Post-campaign insights
│       │   ├── callbacks.py   # Channel service delivery callbacks
│       │   ├── xenopilot.py   # Chat endpoint
│       │   └── aws_status.py  # AWS connectivity status
│       ├── services/
│       │   ├── aws_service.py        # Boto3 client factory (graceful)
│       │   ├── s3_service.py         # Export + import
│       │   ├── ses_service.py        # Completion emails
│       │   ├── sns_service.py        # Status notifications
│       │   ├── cloudwatch_service.py # Metrics + logging
│       │   └── secrets_service.py    # Startup key loading
│       └── middleware/
│           └── logging_middleware.py  # Structured JSON + CW latency
│
├── channel-service/
│   ├── Dockerfile.channel
│   ├── requirements.txt
│   └── main.py              # Delivery simulator + callback engine
│
└── frontend/
    ├── Dockerfile.frontend  # Multi-stage production build
    ├── next.config.ts       # output: 'standalone'
    ├── package.json
    ├── app/
    │   ├── layout.tsx        # Root layout + XenoPilot widget
    │   ├── globals.css       # Design system
    │   ├── page.tsx          # Oracle Command Center
    │   ├── login/page.tsx    # Auth with demo credential pills
    │   ├── campaigns/
    │   │   ├── page.tsx      # Campaign list with filters
    │   │   └── [id]/page.tsx # Full campaign detail (7 sections)
    │   ├── twins/page.tsx    # Digital Twin Explorer + search
    │   └── insights/page.tsx # Learning Console
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.tsx         # Nav + user block + AWS panel
    │   ├── oracle/
    │   │   ├── IntentInput.tsx     # NL campaign input
    │   │   └── AgentTimeline.tsx   # Live SSE agent steps
    │   ├── campaigns/
    │   │   ├── FunnelChart.tsx     # Conversion funnel
    │   │   └── SimulationGauges.tsx
    │   ├── twins/
    │   │   └── TwinCard.tsx
    │   ├── xenopilot/
    │   │   └── XenoPilot.tsx       # Floating chat widget
    │   └── aws/
    │       └── AWSStatusPanel.tsx  # Service connectivity dots
    ├── hooks/
    │   └── useEventStream.ts       # SSE hook
    └── lib/
        ├── api.ts      # Typed API client with auth headers
        ├── auth.ts     # Token helpers, logout, role checks
        ├── types.ts    # Shared TypeScript types
        └── utils.ts    # timeAgo, formatCurrency, formatPct
```

---

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- Redis running on port 6379
- Groq API key (free tier at [console.groq.com](https://console.groq.com))

### Local Development

**1. Clone the repository**
```bash
git clone https://github.com/Yashagx/XENO.git
cd XENO
```

**2. Create `.env` in the project root**
```bash
cp .env.example .env
# Fill in GROQ_API_KEY at minimum — AWS keys optional for local dev
```

**3. Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**4. Channel Service**
```bash
cd channel-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**5. Frontend**
```bash
cd frontend
npm install
npm run dev
```

**6. Open** [http://localhost:3000](http://localhost:3000)

> Redis is optional locally — the app falls back gracefully (SSE streaming disabled, everything else works).

---

## Production Deployment (AWS EC2)

### One-time AWS Setup

**1. EC2 Security Group — add inbound rules:**
```
Port 3000  →  0.0.0.0/0     (Frontend)
Port 8000  →  0.0.0.0/0     (Backend API)
Port 8001  →  0.0.0.0/0     (Channel Service)
Port 6379  →  172.31.0.0/16 (Redis — VPC internal only)
```

**2. Create AWS resources (once):**
```bash
# S3
aws s3 mb s3://xeno-oracle-data --region us-east-1

# SNS Topic
aws sns create-topic --name xeno-oracle-notifications --region us-east-1
# Subscribe your email to the topic in AWS Console

# SES — verify your sender email in AWS Console → SES → Verified identities

# Secrets Manager
aws secretsmanager create-secret \
  --name xeno-oracle/production \
  --secret-string '{"GROQ_API_KEY":"your_key","JWT_SECRET":"your_secret"}' \
  --region us-east-1
```

**3. Fill in `.env.production`:**
```bash
cp .env.example .env.production
# Fill in: GROQ_API_KEY, JWT_SECRET, all AWS_* variables
```

**4. Deploy:**
```bash
bash deploy.sh
```

The script:
1. rsync's your code to EC2 (excluding node_modules, .git, secrets)
2. Uploads `.env.production` via scp
3. Builds all 4 Docker containers on EC2
4. Waits for health checks to pass
5. Sets up systemd for auto-restart on reboot
6. Prints the live URLs

**5. Verify:**
```bash
# All containers running
ssh -i Xeno.pem ubuntu@3.87.12.186 "cd xeno-oracle && sudo docker compose ps"

# Health checks
curl http://3.87.12.186:8000/health
curl http://3.87.12.186:8001/health

# Restart without rebuild
bash restart.sh

# Tail live logs
bash logs.sh
```

---

## Demo Credentials

| Role | Email | Password | Access |
|---|---|---|---|
| **Admin** | admin@xeno.in | admin123 | Full access + AWS status panel |
| **Marketer** | marketer@xeno.in | marketer123 | Create + execute campaigns |
| **Viewer** | viewer@xeno.in | viewer123 | Read-only |

> On the login page, click any role pill to auto-fill and sign in instantly.

---

## API Reference

Interactive docs available at [`/docs`](http://3.87.12.186:8000/docs) (Swagger UI).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Get JWT token |
| `GET` | `/api/v1/auth/me` | Current user |
| `POST` | `/api/v1/campaigns` | Create campaign from intent |
| `GET` | `/api/v1/campaigns` | List all campaigns |
| `GET` | `/api/v1/campaigns/{id}` | Campaign detail + agent trace |
| `POST` | `/api/v1/campaigns/{id}/approve` | Launch campaign |
| `POST` | `/api/v1/campaigns/{id}/export` | Export report to S3 |
| `GET` | `/api/v1/campaigns/{id}/stream` | SSE live event stream |
| `POST` | `/api/v1/campaigns/callbacks` | Channel service delivery callbacks |
| `GET` | `/api/v1/customers` | Customer list |
| `GET` | `/api/v1/customers/stats` | Aggregate stats |
| `POST` | `/api/v1/customers/import-csv` | Bulk import + S3 audit |
| `GET` | `/api/v1/twins` | Digital twin browser |
| `GET` | `/api/v1/twins/{customer_id}` | Individual twin |
| `POST` | `/api/v1/xenopilot/chat` | XenoPilot conversational query |
| `GET` | `/api/v1/insights` | Post-campaign AI insights |
| `GET` | `/api/v1/aws/status` | AWS service connectivity (admin) |
| `GET` | `/health` | Backend health check |

---

## Channel Service Simulation

The channel service simulates realistic message delivery for all 4 channels, firing callbacks asynchronously:

| Channel | Delivered | Opened | Clicked | Converted |
|---|---|---|---|---|
| Email | 92% | 34% | 11% | 4% |
| SMS | 95% | 62% | 9% | 3% |
| WhatsApp | 88% | 70% | 12% | 4% |
| RCS | 85% | 55% | 10% | 3% |

**Failure injection** for testing: `POST /inject-failure` forces specific outcomes on any message.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **LLM** | Groq `llama-3.3-70b` | Sub-second inference, free tier, sufficient reasoning quality |
| **Database** | SQLite + async | Zero-config, persistent via Docker volume, adequate for demo scale |
| **Event bus** | Redis Streams | Durable ordered log without Kafka's operational overhead |
| **Agent orchestration** | Sequential pipeline | Deterministic, debuggable, explainable — vs black-box agent loops |
| **Predictions** | Weighted heuristic + LLM | No real ML training data available; rule-based is honest and explainable |
| **AWS fallback** | Graceful degradation | App never crashes without credentials; each AWS feature is additive |
| **Auth** | JWT (HS256, 24h) | Stateless, simple, no session store needed |
| **Redis binding** | 127.0.0.1 only | Redis not exposed to internet; services communicate via Docker network |

**At 10M customers:** Kafka instead of Redis Streams, PostgreSQL + read replicas, Temporal.io for workflow orchestration, Qdrant for vector search at scale.

**At 100M customers:** Event sourcing with ksqlDB, ML-trained campaign simulator (XGBoost on real data), Neo4j for customer relationship graph, Kubernetes, BigQuery for analytics.

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=                    # Groq API key
JWT_SECRET=                      # Random string for JWT signing

# AWS (all optional — app works without these)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=xeno-oracle-data
AWS_SES_REGION=us-east-1
AWS_SES_SENDER_EMAIL=            # Must be verified in SES console
AWS_SES_ENABLED=true
AWS_SNS_TOPIC_ARN=               # arn:aws:sns:us-east-1:...
AWS_SECRET_NAME=xeno-oracle/production

# Internal (set automatically in docker-compose)
DATABASE_URL=sqlite+aiosqlite:////app/data/xeno_oracle.db
REDIS_URL=redis://redis:6379
CHANNEL_SERVICE_URL=http://channel-service:8001
CRM_CALLBACK_URL=http://backend:8000

# Frontend (baked in at build time)
NEXT_PUBLIC_API_URL=http://3.87.12.186:8000
```

---

## What Makes This Different

| Typical CRM Assignment | Xeno Oracle |
|---|---|
| Customer table with filters | Living Digital Twins with version history |
| "Generate copy" AI button | Full Copywriter Agent with persona-specific variants |
| Post-hoc analytics dashboard | Pre-launch Campaign Time Machine simulator |
| Manual segment builder | NL intent → autonomous segment synthesis |
| Webhook receiver | Full callback lifecycle: delivered → opened → clicked → converted |
| Generic dashboard | Agent Reasoning Panel — see exactly why each decision was made |
| No observability | CloudWatch metrics on every API call and agent run |
| Plain .env | AWS Secrets Manager at startup |

---

## Built By

**Yash Agarwal** · RA2311033010055  
B.Tech CSE (Software Engineering) · SRMIST Kattankulatham · 2027  
Department of Computational Intelligence

> Built in 6 days for the Xeno FDE Internship Assignment — June 2026.  
> Stack: Python · TypeScript · FastAPI · Next.js · Groq · AWS · Docker

---

<div align="center">

**[Live Demo](http://3.87.12.186:3000) · [API Docs](http://3.87.12.186:8000/docs) · [GitHub](https://github.com/Yashagx/XENO)**

*RFC-001 · Xeno Oracle · Yash Agarwal*

</div>
