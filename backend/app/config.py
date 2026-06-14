from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://xeno:xenopassword@localhost:5432/xeno_oracle"
    DATABASE_URL_SYNC: str = "postgresql://xeno:xenopassword@localhost:5432/xeno_oracle"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # AI - Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_DIMENSION: int = 768

    # Auth
    JWT_SECRET: str = "xeno-oracle-dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080

    # Services
    CHANNEL_SERVICE_URL: str = "http://localhost:8001"
    CRM_CALLBACK_URL: str = "http://localhost:8000/api/v1/campaigns/callbacks"

    # App
    BACKEND_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
