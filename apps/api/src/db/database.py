"""Database connection and session management."""

import ssl
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings

settings = get_settings()


def prepare_database_url(url: str) -> tuple[str, bool]:
    """Prepare database URL for asyncpg.

    Strips params unsupported by asyncpg (sslmode, channel_binding) from the
    URL query string and returns the cleaned URL plus a flag indicating whether
    SSL should be enabled.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    # Detect SSL requirement before stripping
    sslmode_values = params.pop("sslmode", [])
    needs_ssl = any(v in ("require", "verify-ca", "verify-full") for v in sslmode_values)

    # Remove channel_binding (not supported by asyncpg)
    params.pop("channel_binding", None)

    new_query = urlencode(params, doseq=True)
    cleaned = urlunparse(parsed._replace(query=new_query))
    return cleaned, needs_ssl


# Clean the URL and convert postgresql:// to postgresql+asyncpg://
raw_url = settings.database_url
cleaned_url, use_ssl = prepare_database_url(raw_url)
database_url = cleaned_url.replace("postgresql://", "postgresql+asyncpg://")

# asyncpg requires ssl to be passed as a context object, not via URL params
connect_args: dict = {"ssl": ssl.create_default_context()} if use_ssl else {}

engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    # For Neon serverless: use smaller pool with faster recycling
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
    connect_args=connect_args,
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
