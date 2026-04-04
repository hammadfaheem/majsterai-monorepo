"""Database connection and session management."""

import ssl
from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from ..config import get_settings
from .models import generate_uuid, utc_now_ms  # re-exported for backwards compatibility

__all__ = ["generate_uuid", "utc_now_ms", "engine", "async_session_maker"]


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


def _build_engine() -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Build the async SQLAlchemy engine from current settings.

    Called once at import time so other modules can import ``engine`` and
    ``async_session_maker`` as module-level names, but settings are read
    through the cached ``get_settings()`` so they're always up to date.
    """
    settings = get_settings()
    raw_url = settings.database_url
    cleaned_url, use_ssl = prepare_database_url(raw_url)
    database_url = cleaned_url.replace("postgresql://", "postgresql+asyncpg://")

    # asyncpg requires ssl to be passed as a context object, not via URL params
    connect_args: dict = {"ssl": ssl.create_default_context()} if use_ssl else {}

    _engine = create_async_engine(
        database_url,
        # Only emit SQL to stdout when DEBUG=true — never in production
        echo=settings.debug,
        pool_pre_ping=True,
        # Suitable for Neon serverless: smaller pool, faster recycling
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
        connect_args=connect_args,
    )

    _session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return _engine, _session_maker


engine, async_session_maker = _build_engine()


async def ping_db() -> bool:
    """Verify the database connection is reachable. Returns True on success."""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — intentional broad catch for connectivity probe
        return False


async def init_db() -> None:
    """Verify database connectivity on startup.

    Schema management is handled exclusively by Alembic (``alembic upgrade head``).
    This function no longer calls ``create_all`` — running that against an existing
    database silently skips schema changes, which is incorrect for production.
    """
    if not await ping_db():
        raise RuntimeError(
            "Cannot connect to the database. "
            "Check DATABASE_URL and ensure the server is reachable."
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
