from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.database import async_engine, Base, IS_SQLITE
from app.api.v1 import router as v1_router
from app.config import settings
from app.middleware.logging_middleware import structured_logging_middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _seed_users(db):
    """Seed default users if users table is empty."""
    import bcrypt
    from sqlalchemy import select, func
    from app.models.auth import User
    count_result = await db.execute(select(func.count(User.id)))
    count = count_result.scalar()
    if count == 0:
        seed_users = [
            {"email": "admin@xeno.in",    "password": "admin123",    "name": "Admin",        "role": "admin"},
            {"email": "marketer@xeno.in", "password": "marketer123", "name": "Priya Sharma", "role": "marketer"},
            {"email": "viewer@xeno.in",   "password": "viewer123",   "name": "Viewer",       "role": "viewer"},
        ]
        for u in seed_users:
            user = User(
                email=u["email"],
                name=u["name"],
                password_hash=bcrypt.hashpw(u["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                role=u["role"]
            )
            db.add(user)
        await db.commit()
        logger.info("Seeded 3 default users (admin, marketer, viewer)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load secrets from AWS (overrides env vars if found)
    try:
        from app.services.secrets_service import load_secrets_from_aws
        aws_secrets = await load_secrets_from_aws()
        if aws_secrets.get('GROQ_API_KEY'):
            os.environ['GROQ_API_KEY'] = aws_secrets['GROQ_API_KEY']
        if aws_secrets.get('JWT_SECRET'):
            os.environ['JWT_SECRET'] = aws_secrets['JWT_SECRET']
    except Exception as e:
        logger.warning(f"AWS Secrets loading skipped: {e}")

    # Startup: create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Enable WAL mode for concurrent async access (SQLite only)
        if IS_SQLITE:
            from sqlalchemy import text
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout=10000"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))

    # Seed default users
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await _seed_users(db)

    logger.info("XENO ORACLE backend started")
    yield
    # Shutdown
    await async_engine.dispose()
    logger.info("XENO ORACLE backend stopped")


app = FastAPI(
    title="XENO ORACLE API",
    description="Autonomous AI Marketing Intelligence System",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow EC2 public IP and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://3.87.12.186:3000",
        "http://3.87.12.186",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured logging middleware
app.middleware("http")(structured_logging_middleware)

# Routers
app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "xeno-oracle",
        "version": "2.0.0",
    }
