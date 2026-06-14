# XENO ORACLE v2.0

XENO ORACLE is an AI-native CRM (Customer Relationship Management) system that utilizes 10 distinct AI agents to plan, simulate, and execute marketing campaigns. It features real-time agent execution streaming, live campaign simulation, AWS integration for production deployments, and a built-in AI assistant (XenoPilot) for conversational CRM intelligence.

## Features
- **10-Agent AI Pipeline**: Intent parsing, customer memory, segmentation, persona modeling, campaign strategy, copywriting, simulation, execution, learning, and insights.
- **XenoPilot**: An integrated AI data analyst widget for querying live CRM data in natural language.
- **Role-Based Access Control (RBAC)**: Distinct permissions for `admin`, `marketer`, and `viewer` roles.
- **Full AWS Integration**:
  - **S3**: Campaign exports and customer data CSV imports
  - **SES**: Real email delivery for campaign completion reports
  - **SNS**: Push notifications for campaign readiness and completion
  - **CloudWatch**: Structured API latency metrics and business KPIs
  - **Secrets Manager**: Secure API key retrieval at startup
- **Dockerized Production Environment**: Streamlined deployment to AWS EC2 using a single `docker-compose` setup.

## Architecture
- **Frontend**: Next.js 16 (React 19), Tailwind CSS, Lucide Icons, Recharts
- **Backend**: FastAPI, SQLAlchemy (Async/SQLite), Pydantic
- **Channel Service**: FastAPI microservice simulating email, SMS, and WhatsApp delivery
- **AI Models**: Groq (`llama-3.3-70b-versatile`) for reasoning, `text-embedding-004` for semantic search
- **Message Broker**: Redis (Pub/Sub & Streams) for live UI updates

## Local Development
1. Install dependencies for the frontend, backend, and channel-service.
2. Setup a local `.env` file in the root based on `.env.production` (but omit AWS keys if you don't need them locally).
3. Ensure Redis is running locally on port 6379.
4. Run the components:
   - Frontend: `npm run dev`
   - Backend: `uvicorn app.main:app --reload`
   - Channel Service: `uvicorn main:app --port 8001 --reload`

## Production Deployment (AWS EC2)
1. Add your AWS IAM credentials to `.env.production`.
2. Run `bash deploy.sh` from your local terminal.
3. The script will securely `rsync` your code to the EC2 instance, provision Docker containers, and set up a systemd service to survive instance reboots.

## Demo Logins
Once deployed, you can access the system via the following demo accounts:
- **Admin**: admin@xeno.in / admin123
- **Marketer**: marketer@xeno.in / marketer123
- **Viewer**: viewer@xeno.in / viewer123

## License
MIT
