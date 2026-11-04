"""Database Engine & Async Session Management.

Supports async PostgreSQL (asyncpg) with SQLite async fallback for lightweight test environments.
Gracefully handles missing asyncpg driver by defaulting to SQLite.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

db_url = settings.DATABASE_URL

# Check if asyncpg is available when postgresql is configured
if db_url.startswith("postgresql"):
    try:
        import asyncpg  # type: ignore
    except ImportError:
        # Fallback to local SQLite for free-tier / standalone execution without asyncpg
        db_url = "sqlite+aiosqlite:///./data/adatlas_dev.db"

is_sqlite = db_url.startswith("sqlite")

engine_kwargs = {"echo": False}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
    })

engine = create_async_engine(db_url, **engine_kwargs)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding an async database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
