"""Application Configuration via Pydantic Settings v2.

Supports Free-Tier local development, mock auth modes, and local storage fallback.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AdAtlas"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    FRONTEND_URL: str = "http://localhost:3000"

    # Authentication & RBAC (Free-tier friendly: 'mock' allows zero-config dev)
    AUTH_MODE: Literal["mock", "google"] = "mock"
    JWT_SECRET_PRIMARY: str = "default_local_dev_secret_key_change_in_production_32bytes"
    JWT_SECRET_SECONDARY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Database (PostgreSQL 16 default, supports SQLite async for zero-infra test runs)
    DATABASE_URL: str = "postgresql+asyncpg://adatlas:adatlas_dev_password@localhost:5432/adatlas_dev"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis & Task Queues
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Storage Tier (Free-Tier: 'local' uses local filesystem; 's3' uses MinIO / AWS)
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_LOCAL_DIR: str = "./data/storage"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_BUCKET_NAME: str = "adatlas-raw-payloads"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "ap-south-1"

    # Data Collectors
    ADAPTER_A_ENABLED: bool = True
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_ACCESS_TOKEN: str = ""

    ADAPTER_B_ENABLED: bool = True
    ADAPTER_B_PROVIDER: str = "apify_free_tier"
    ADAPTER_B_API_KEY: str = ""

    # Adapter C (Playwright UI Scraper): strictly OFF per ADR-0001 & ADR-0002
    ADAPTER_C_ENABLED: bool = False

    # External APIs (Optional - free tier fallbacks if empty)
    GOOGLE_PLACES_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Billable Budget Ceilings (USD)
    BUDGET_CAP_PROVIDER: float = 150.00
    BUDGET_CAP_PLACES: float = 100.00
    BUDGET_CAP_LLM: float = 50.00

    # Safety & Scraper Boundaries
    COLLECTION_ENABLED: bool = True
    MAX_PAGES_PER_DOMAIN: int = 8
    REQUEST_TIMEOUT_SECONDS: int = 10
    MAX_DECOMPRESSED_BODY_BYTES: int = 2 * 1024 * 1024  # 2 MB
    MAX_REDIRECT_HOPS: int = 5


settings = Settings()

