"""
SQLite dev mode - overrides PostgreSQL config for local development
without Docker. Gracefully removes pgvector Vector columns.
"""
import os
# Override DB URLs before any imports
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./xeno_oracle.db")
os.environ.setdefault("DATABASE_URL_SYNC", "sqlite:///./xeno_oracle.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
