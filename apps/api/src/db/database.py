"""Database connection and session management."""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+asyncpg://
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now_ms() -> int:
    """Get current UTC timestamp in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


async def init_db() -> None:
    """Initialize database - create tables."""
    from .models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
