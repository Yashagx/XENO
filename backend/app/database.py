from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, text
from app.config import settings

# Detect SQLite
IS_SQLITE = "sqlite" in settings.DATABASE_URL

if IS_SQLITE:
    # For SQLite: use StaticPool so all async requests share ONE connection.
    # This avoids "database is locked" because SQLite only supports one writer
    # and aiosqlite serialises all operations on that single connection internally.
    from sqlalchemy.pool import StaticPool
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    sync_engine = create_engine(
        settings.DATABASE_URL_SYNC,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    sync_engine = create_engine(
        settings.DATABASE_URL_SYNC,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
