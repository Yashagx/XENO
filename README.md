<div align="center">

# ✦ XENO ORACLE
### Autonomous AI Marketing Intelligence System

**v3.0 · Built for Xeno FDE Internship Assignment 2026**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-3.87.12.186%3A3000-6366f1?style=for-the-badge&logo=amazonaws&logoColor=white)](http://3.87.12.186:3000)
[![API Docs](https://img.shields.io/badge/API%20Docs-8000%2Fdocs-10b981?style=for-the-badge&logo=fastapi&logoColor=white)](http://3.87.12.186:8000/docs)
[![AWS Bedrock](https://img.shields.io/badge/AWS%20Bedrock-Claude%203%20Haiku-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/bedrock)
[![AWS Services](https://img.shields.io/badge/AWS%20Services-9%20Integrated-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

> *"A marketer types one sentence. Ten AI agents — powered by AWS Bedrock — think, plan, simulate, and execute autonomously."*

<br/>

![10 Agents](https://img.shields.io/badge/AI%20Agents-10%20Specialized-8b5cf6?style=flat-square)
![Digital Twins](https://img.shields.io/badge/Digital%20Twins-500%20Modelled-10b981?style=flat-square)
![Bedrock](https://img.shields.io/badge/Bedrock-Claude%203%20Haiku%20%2B%20Titan%20Embed-FF9900?style=flat-square)
![DynamoDB](https://img.shields.io/badge/DynamoDB-Real--time%20Events-FF9900?style=flat-square)
![Comprehend](https://img.shields.io/badge/Comprehend-Sentiment%20NLP-FF9900?style=flat-square)
![Lambda](https://img.shields.io/badge/Lambda-Serverless%20Twin%20Rebuild-FF9900?style=flat-square)

</div>

---

## What Is Xeno Oracle?

Xeno Oracle is **not a CRM**. It is an **Autonomous Marketing Intelligence System** — a multi-agent AI operating system for growth teams, built natively on AWS.

A marketer types one sentence:

```
"Re-engage high-value customers who haven't bought in 90 days before the summer sale"
```

The system does the rest — completely autonomously:

```
Intent → Customer Memory Retrieval → Segmentation → Persona Modeling
      → Strategy → Copywriting → Pre-launch Simulation (Time Machine)
      → Execution → Real-time Delivery Tracking → Learning → Insights
```

Every step is powered by AWS services. Every decision is explainable. Every campaign gets smarter.

---

## AWS Architecture

```
                        XENO ORACLE — AWS ARCHITECTURE (us-east-1)
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐   │
│  │  AWS BEDROCK    │   │    DYNAMODB      │   │   COMPREHEND     │   │
│  │                 │   │                  │   │                  │   │
│  │ Claude 3 Haiku  │   │ campaign-events  │   │ Sentiment on     │   │
│  │ → XenoPilot LLM │   │ (real-time store │   │ every campaign   │   │
│  │                 │   │  TTL = 30 days)  │   │ message variant  │   │
│  │ Titan Embed v2  │   │                  │   │                  │   │
│  │ → Twin search   │   │ GSI: customer-   │   │ Key phrase       │   │
│  │   embeddings    │   │ events-index     │   │ extraction       │   │
│  └────────┬────────┘   └────────┬─────────┘   └────────┬─────────┘   │
│           │                     │                       │             │
│           └─────────────────────▼───────────────────────┘             │
│                                 │                                      │
│  ┌──────────────────────────────▼──────────────────────────────────┐  │
│  │              FastAPI Backend · EC2 t2.medium · Docker           │  │
│  │                      10-Agent AI Pipeline                       │  │
│  └──────┬───────────────────────────────────────────────────────┬──┘  │
│         │                                                       │      │
│  ┌──────▼────────┐  ┌──────────────┐  ┌──────────────────────┐ │      │
│  │   S3 Bucket   │  │     SES      │  │       LAMBDA         │ │      │
│  │               │  │              │  │                      │ │      │
│  │ Campaign JSON │  │ Completion   │  │ xeno-oracle-         │ │      │
│  │ exports       │  │ emails to    │  │ twin-rebuilder       │ │      │
│  │ CSV import    │  │ marketer     │  │ (async, serverless,  │ │      │
│  │ Brand assets  │  │ inbox        │  │  256MB, py3.11)      │ │      │
│  └───────────────┘  └──────────────┘  └──────────────────────┘ │      │
│                                                                  │      │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐   │      │
│  │     SNS      │  │  CLOUDWATCH   │  │    REKOGNITION     │   │      │
│  │              │  │               │  │                    │   │      │
│  │ Campaign     │  │ XenoOracle    │  │ Brand asset image  │   │      │
│  │ ready alert  │  │ namespace:    │  │ content moderation │   │      │
│  │ Completion   │  │ API latency   │  │ before S3 upload   │   │      │
│  │ notification │  │ KPI metrics   │  │                    │   │      │
│  └──────────────┘  └───────────────┘  └────────────────────┘   │      │
│                                                                  │      │
│  ┌────────────────────────────────────────────────────────────┐  │      │
│  │                   SECRETS MANAGER                          │  │      │
│  │  secret: xeno-oracle/production                           │  │      │
│  │  { GROQ_API_KEY, JWT_SECRET } — loaded at startup        │  │      │
│  └────────────────────────────────────────────────────────────┘  │      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9 AWS Services — What Each Does

| # | Service | Role | When It Fires |
|---|---|---|---|
| 1 | **Bedrock (Claude 3 Haiku)** | Powers XenoPilot conversational intelligence | Every XenoPilot query |
| 2 | **Bedrock (Titan Embeddings v2)** | Semantic vector search for customer twin retrieval | Memory Agent — twin search |
| 3 | **DynamoDB** | Real-time, high-throughput campaign event store with TTL | Every callback (delivered/opened/clicked) |
| 4 | **Comprehend** | NLP sentiment analysis on campaign message variants | After copywriter agent generates content |
| 5 | **Lambda** | Serverless async customer twin score rebuild | After each campaign completes |
| 6 | **Rekognition** | Brand asset image content moderation | Before any image is stored in S3 |
| 7 | **S3** | Campaign JSON exports, customer CSV import audit trail, brand assets | On export / CSV upload / image upload |
| 8 | **SES** | Campaign completion email to marketer | Learning agent completes |
| 9 | **SNS** | Push notification when campaign is ready + completed | Orchestrator status transitions |
| + | **CloudWatch** | API latency metrics, business KPIs, agent error tracking | Every API call + agent run |
| + | **Secrets Manager** | Secure key retrieval at startup (overrides .env) | Backend startup |

> All services implement **graceful fallback** — the app runs fully without any AWS credentials. Each service activates when configured and degrades silently when unavailable.

---

## The 10-Agent Pipeline

```
Natural Language Intent
         │
         ▼
┌─────────────────────┐
│  1. Intent Parser   │  Groq LLM → structured: goal, churn_window, LTV, channel
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. Memory Agent    │  AWS Bedrock Titan Embeddings → semantic twin search
│                     │  Retrieves relevant Customer Digital Twins
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  3. Segmentation    │  Builds precise, named, explainable audience segment
│     Agent           │  with per-customer inclusion reasoning
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  4. Persona Agent   │  Clusters into 2–5 behavioural personas
│                     │  "Weekend Browser" · "Deal Hunter" · "Lapsed VIP"
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  5. Strategy Agent  │  Channel mix · timing · campaign structure
│                     │  grounded in historical campaign performance
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  6. Copywriter      │  Persona-specific messages per channel
│     Agent           │  → AWS Comprehend sentiment analysis (async)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  7. Simulator       │  Pre-launch: open rate · click rate · revenue · ROI
│  (Time Machine)     │  P10 / P50 / P90 confidence bands
└──────────┬──────────┘
           │ ← Marketer reviews and approves
           ▼
┌─────────────────────┐
│  8. Execution Agent │  Dispatches to Channel Service per customer
│                     │  → Events stream to DynamoDB in real time
└──────────┬──────────┘
           ▼ ← Callbacks: delivered → opened → clicked → converted
┌─────────────────────┐
│  9. Learning Agent  │  Updates Digital Twins via EWMA
│                     │  → Invokes AWS Lambda for async twin rebuild
│                     │  → SES email + SNS notification to marketer
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  10. Insight Agent  │  AWS Bedrock Claude generates post-campaign
│                     │  intelligence in plain marketing language
└─────────────────────┘
```

Every step streams live to the frontend via **Redis Pub/Sub → Server-Sent Events**.

---

## Customer Digital Twin System

Every customer has a living **Digital Twin** — a structured, versioned, Bedrock-embedded memory object.

```python
CustomerTwin:
  ├── channel_affinity      # {"email": 0.74, "sms": 0.31, "whatsapp": 0.82}
  ├── category_affinity     # {"footwear": 0.91, "accessories": 0.54}
  ├── churn_probability     # 0.0–1.0, updated by Lambda after every campaign
  ├── predicted_ltv_90d    # Expected spend next 90 days (₹)
  ├── purchase_intent       # How ready to buy right now
  ├── price_sensitivity     # 0=insensitive → 1=highly sensitive
  ├── urgency_response      # Responds to "last chance" messaging?
  ├── communication_style   # casual / formal / enthusiastic / minimal
  ├── narrative_summary     # LLM-generated 2-sentence customer story
  ├── embedding             # Bedrock Titan v2 vector (1024-dim)
  └── version               # Full audit trail of every twin update
```

**Embedding flow:** narrative + affinity JSON → Bedrock Titan Embeddings v2 (1024-dim) → stored in SQLite for semantic search. Memory Agent retrieves twins using cosine similarity before every campaign.

**Rebuild flow:** After campaign completes → Learning Agent → AWS Lambda (`xeno-oracle-twin-rebuilder`, async fire-and-forget) → recomputes RFM scores → PATCH `/twins/{id}/lambda-update`.

---

## XenoPilot — Conversational CRM Intelligence

Floating ✦ button on every page. Powered by **AWS Bedrock Claude 3 Haiku** (primary) with Groq fallback.

```
You:        "Which campaign had the best ROI?"
XenoPilot:  "Campaign: Lapsed VIPs from Delhi achieved 2.5x ROI with 52.4%
             open rate across 18 messages. The 'Loyal Spenders' persona (39%
             of segment) drove most conversions. Consider a follow-up targeting
             the same segment on WhatsApp for potentially 15% higher engagement."
             
             ⚡ AWS Bedrock · Claude 3 Haiku
             [→ View Campaign]  [→ Create Follow-up]
```

Every response shows which model answered: `⚡ AWS Bedrock · Claude 3 Haiku` or `⚡ Groq · Llama 3.3 70B`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| **Animations** | Framer Motion |
| **Charts** | Recharts |
| **Icons** | Lucide React |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy (async), Pydantic v2 |
| **Primary LLM (agents)** | Groq — `llama-3.3-70b-versatile` |
| **XenoPilot LLM** | AWS Bedrock — `claude-3-haiku-20240307` |
| **Embeddings** | AWS Bedrock — `amazon.titan-embed-text-v2:0` (1024-dim) |
| **Event Store** | AWS DynamoDB (real-time) + SQLite (historical) |
| **Message NLP** | AWS Comprehend (sentiment + key phrases) |
| **Image Moderation** | AWS Rekognition |
| **Serverless Compute** | AWS Lambda (Python 3.11, 256MB, async twin rebuild) |
| **Email** | AWS SES |
| **Notifications** | AWS SNS |
| **Observability** | AWS CloudWatch (XenoOracle namespace) |
| **Object Storage** | AWS S3 |
| **Secret Management** | AWS Secrets Manager |
| **Database** | SQLite via `aiosqlite` (Docker volume) |
| **Message Broker** | Redis 7 (Pub/Sub + Streams → SSE) |
| **Auth** | JWT (HS256, 24h), `python-jose`, `passlib[bcrypt]` |
| **Deployment** | Docker Compose on AWS EC2 t2.medium |
| **AWS SDK** | `boto3 1.34` |

---

## Project Structure

```
XENO/
├── .env.production              # All secrets (never committed)
├── .gitignore
├── docker-compose.yml           # 4-container production setup
├── deploy.sh                    # One-command EC2 deployment (rsync + docker)
├── restart.sh                   # Quick container restart
├── logs.sh                      # Live log tailing from EC2
│
├── lambda/
│   ├── twin_rebuilder/
│   │   └── handler.py           # Serverless twin rebuild function
│   └── deploy_lambda.sh         # Lambda deployment script
│
├── backend/
│   ├── Dockerfile.backend
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app, lifespan, CORS, middleware
│       ├── config.py
│       ├── database.py
│       ├── redis_client.py
│       ├── models/
│       │   ├── auth.py          # User (RBAC)
│       │   ├── customer.py      # Customer + CustomerTwin + TwinAuditLog
│       │   ├── campaign.py      # Campaign + Segment + SegmentCustomer
│       │   ├── message.py       # Message + CampaignEvent
│       │   ├── order.py
│       │   └── insight.py
│       ├── agents/
│       │   ├── orchestrator.py
│       │   ├── state.py
│       │   ├── llm_client.py    # Groq API wrapper
│       │   ├── memory_agent.py
│       │   ├── segmentation_agent.py
│       │   ├── persona_agent.py
│       │   ├── strategy_agent.py
│       │   ├── copywriter_agent.py
│       │   ├── simulator_agent.py
│       │   ├── execution_agent.py
│       │   ├── learning_agent.py
│       │   ├── insight_agent.py
│       │   └── xenopilot_agent.py  # Bedrock Claude 3 Haiku primary
│       ├── api/v1/
│       │   ├── auth.py
│       │   ├── campaigns.py        # + S3 export + Rekognition asset upload
│       │   ├── customers.py        # + S3 CSV import
│       │   ├── events.py           # SSE streaming
│       │   ├── twins.py            # + Lambda rebuild trigger
│       │   ├── insights.py
│       │   ├── callbacks.py        # + DynamoDB event write
│       │   ├── xenopilot.py        # Bedrock chat endpoint
│       │   └── aws_status.py       # All 9 services status
│       ├── services/
│       │   ├── aws_service.py          # Boto3 client factory
│       │   ├── bedrock_service.py      # Claude 3 Haiku + Titan Embed
│       │   ├── embedding_service.py    # Bedrock Titan → hash fallback
│       │   ├── dynamodb_service.py     # Event store + live stats
│       │   ├── comprehend_service.py   # Sentiment + key phrases
│       │   ├── lambda_service.py       # Twin rebuild invocation
│       │   ├── rekognition_service.py  # Image content moderation
│       │   ├── s3_service.py           # Export + import + assets
│       │   ├── ses_service.py          # Completion emails
│       │   ├── sns_service.py          # Status notifications
│       │   ├── cloudwatch_service.py   # Metrics + logging
│       │   └── secrets_service.py      # Startup key loading
│       └── middleware/
│           └── logging_middleware.py   # Structured JSON + CW latency
│
├── channel-service/
│   ├── Dockerfile.channel
│   └── main.py                  # Delivery simulator + callback engine
│
└── frontend/
    ├── Dockerfile.frontend      # Multi-stage, output: standalone
    ├── next.config.ts
    ├── app/
    │   ├── layout.tsx           # Root layout + XenoPilot widget
    │   ├── globals.css          # Design system (unchanged)
    │   ├── page.tsx             # Oracle Command Center
    │   ├── login/page.tsx       # Auth with 3 demo credential pills
    │   ├── campaigns/
    │   │   ├── page.tsx
    │   │   └── [id]/page.tsx    # Detail: gauges + personas + copy + sentiment
    │   ├── twins/page.tsx       # Bedrock-powered semantic search
    │   └── insights/page.tsx    # Learning Console
    ├── components/
    │   ├── layout/Sidebar.tsx   # Nav + user block + AWS status panel
    │   ├── oracle/
    │   │   ├── IntentInput.tsx
    │   │   └── AgentTimeline.tsx
    │   ├── campaigns/
    │   │   ├── FunnelChart.tsx
    │   │   └── SimulationGauges.tsx
    │   ├── twins/TwinCard.tsx
    │   ├── xenopilot/
    │   │   └── XenoPilot.tsx    # Model badge: Bedrock vs Groq
    │   └── aws/
    │       └── AWSStatusPanel.tsx  # All 9 services with icons
    └── lib/
        ├── api.ts               # Typed client with JWT headers
        ├── auth.ts
        ├── types.ts
        └── utils.ts
```

---

## Getting Started

### Prerequisites
- Node.js 20+, Python 3.11+, Redis on port 6379
- Groq API key — [console.groq.com](https://console.groq.com) (free)
- AWS account with Bedrock model access enabled (Claude 3 Haiku + Titan Embed v2)

### Local Development

```bash
git clone https://github.com/Yashagx/XENO.git
cd XENO
cp .env.example .env       # Fill in at minimum: GROQ_API_KEY
                            # Add AWS keys for Bedrock + other services

# Backend
cd backend && python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Channel Service (new terminal)
cd channel-service
uvicorn main:app --reload --port 8001

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Production Deployment (AWS EC2)

### One-time Setup

**1. EC2 Security Group — inbound rules:**
```
Port 3000  →  0.0.0.0/0      Frontend
Port 8000  →  0.0.0.0/0      Backend API
Port 8001  →  0.0.0.0/0      Channel Service
Port 6379  →  172.31.0.0/16  Redis (VPC internal only)
```

**2. IAM User `xeno-oracle-app` — attach policies:**
```
AmazonBedrockFullAccess
AmazonDynamoDBFullAccess
ComprehendFullAccess
AWSLambdaFullAccess
AmazonRekognitionFullAccess
AmazonS3FullAccess
AmazonSESFullAccess
AmazonSNSFullAccess
CloudWatchFullAccess
SecretsManagerReadWrite
```

**3. Enable Bedrock model access** in AWS Console → Bedrock → Model access:
- Anthropic Claude 3 Haiku
- Amazon Titan Embeddings V2

**4. Provision AWS resources:**
```bash
# S3
aws s3 mb s3://xeno-oracle-data --region us-east-1

# DynamoDB
aws dynamodb create-table \
  --table-name xeno-oracle-campaign-events \
  --attribute-definitions \
    AttributeName=campaign_id,AttributeType=S \
    AttributeName=event_id,AttributeType=S \
  --key-schema \
    AttributeName=campaign_id,KeyType=HASH \
    AttributeName=event_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# SNS Topic
aws sns create-topic --name xeno-oracle-notifications --region us-east-1

# SES — verify sender email in AWS Console → SES → Verified identities

# Secrets Manager
aws secretsmanager create-secret \
  --name xeno-oracle/production \
  --secret-string '{"GROQ_API_KEY":"sk-...","JWT_SECRET":"..."}' \
  --region us-east-1

# Lambda (after filling .env.production)
bash lambda/deploy_lambda.sh
```

**5. Fill `.env.production` and deploy:**
```bash
cp .env.example .env.production   # Fill all AWS_* variables
bash deploy.sh                     # Syncs code, builds Docker, starts on EC2
```

---

## Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | admin@xeno.in | admin123 | Full access + AWS status panel |
| **Marketer** | marketer@xeno.in | marketer123 | Create + execute campaigns |
| **Viewer** | viewer@xeno.in | viewer123 | Read-only |

> On the login page, click any role pill to auto-fill and sign in in one tap.

---

## API Reference

Interactive Swagger UI at [`/docs`](http://3.87.12.186:8000/docs).

| Method | Endpoint | Description | New |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | JWT token | |
| `GET` | `/api/v1/auth/me` | Current user | |
| `POST` | `/api/v1/campaigns` | Create from intent | |
| `GET` | `/api/v1/campaigns/{id}` | Detail + agent trace + sentiment | |
| `POST` | `/api/v1/campaigns/{id}/approve` | Launch | |
| `POST` | `/api/v1/campaigns/{id}/export` | Export to S3 | |
| `GET` | `/api/v1/campaigns/{id}/live-stats` | Real-time stats from DynamoDB | ✨ |
| `POST` | `/api/v1/campaigns/{id}/upload-asset` | Image upload with Rekognition gate | ✨ |
| `GET` | `/api/v1/campaigns/{id}/stream` | SSE live events | |
| `POST` | `/api/v1/campaigns/callbacks` | Channel callbacks → DynamoDB | |
| `GET` | `/api/v1/customers` | Customer list | |
| `POST` | `/api/v1/customers/import-csv` | Bulk import + S3 audit | |
| `GET` | `/api/v1/twins` | Digital twin browser | |
| `POST` | `/api/v1/twins/{id}/rebuild` | Trigger Lambda twin rebuild | ✨ |
| `PATCH` | `/api/v1/twins/{id}/lambda-update` | Receive Lambda result | ✨ |
| `POST` | `/api/v1/xenopilot/chat` | Bedrock Claude chat | |
| `GET` | `/api/v1/insights` | Post-campaign AI insights | |
| `GET` | `/api/v1/aws/status` | All 9 services connectivity | |
| `GET` | `/health` | Backend health | |

---

## AWS Service Verification

After deployment, check all services are live:

```bash
# Get admin token
TOKEN=$(curl -s -X POST http://3.87.12.186:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@xeno.in","password":"admin123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Check all 9 AWS services
curl -s -H "Authorization: Bearer $TOKEN" \
  http://3.87.12.186:8000/api/v1/aws/status | python3 -m json.tool
```

Expected: all 9 services show `"connected": true`.

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=                        # Groq API key (agents 1-10)
JWT_SECRET=                          # Random string for JWT

# AWS Core (all services use same credentials)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# AWS Bedrock
AWS_BEDROCK_REGION=us-east-1         # Claude 3 Haiku + Titan Embed v2

# AWS DynamoDB
AWS_DYNAMODB_TABLE=xeno-oracle-campaign-events

# AWS S3
AWS_S3_BUCKET=xeno-oracle-data

# AWS SES
AWS_SES_SENDER_EMAIL=                # Must be verified in SES console
AWS_SES_ENABLED=true

# AWS SNS
AWS_SNS_TOPIC_ARN=                   # arn:aws:sns:us-east-1:...

# AWS Lambda
AWS_LAMBDA_TWIN_FUNCTION=xeno-oracle-twin-rebuilder
AWS_LAMBDA_ROLE_ARN=                 # arn:aws:iam::...:role/...
LAMBDA_SECRET=                       # Internal auth between Lambda and backend

# AWS Secrets Manager
AWS_SECRET_NAME=xeno-oracle/production

# Internal Docker network URLs
CHANNEL_SERVICE_URL=http://channel-service:8001
CRM_CALLBACK_URL=http://backend:8000

# Public URL (baked into frontend at build time)
NEXT_PUBLIC_API_URL=http://3.87.12.186:8000
```

---

## Key Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **XenoPilot LLM** | Bedrock Claude 3 Haiku (primary) + Groq (fallback) | Claude optimized for conversation; Groq for raw speed in agents |
| **Embeddings** | Bedrock Titan Embed v2 (1024-dim) | Native AWS, no external API, consistent with Bedrock usage |
| **Event store** | DynamoDB (real-time) + SQLite (historical) | DynamoDB for high-throughput writes with TTL; SQLite for complex aggregates |
| **Twin rebuild** | AWS Lambda (async `Event` invocation) | Decouples compute from API latency; demonstrates serverless thinking |
| **Image safety** | Rekognition before S3 | Production requirement — never skip content moderation in real systems |
| **Message sentiment** | Comprehend (async) | Zero-latency impact on campaign creation; enriches insight reports |
| **Agent pipeline** | Groq `llama-3.3-70b` | Sub-second inference for 10 sequential agents; Bedrock reserved for UX-facing chat |
| **Redis binding** | 127.0.0.1:6379 | Redis never exposed to internet; Docker network only |
| **Secrets** | Secrets Manager at startup | Production pattern — env vars as fallback, SM as override |

**At 10M customers:** Kafka instead of Redis Streams, Aurora PostgreSQL + read replicas, Temporal.io for agent workflows, Bedrock Knowledge Bases for RAG.

**At 100M customers:** Bedrock Agents for full orchestration, SageMaker for campaign ML models, Kinesis for event ingestion, Redshift for analytics.

---

## Built By

**Yash Agarwal** · RA2311033010055  
B.Tech CSE (Software Engineering) · SRMIST Kattankulatham · 2027  
Department of Computational Intelligence  

> Built in 6 days for Xeno FDE Internship Assignment — June 2026.  
> **9 AWS services · 10 AI agents · 500 Digital Twins · One plain-English sentence to launch.**

---

<div align="center">

**[Live Demo](http://3.87.12.186:3000) · [API Docs](http://3.87.12.186:8000/docs) · [GitHub](https://github.com/Yashagx/XENO)**

*RFC-001 · Xeno Oracle v3.0 · Yash Agarwal*

</div>
