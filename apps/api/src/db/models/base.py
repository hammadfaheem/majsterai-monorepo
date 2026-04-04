"""Shared SQLAlchemy declarative base and common column helpers."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now_ms() -> int:
    """Return current UTC timestamp in milliseconds."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""

    pass
