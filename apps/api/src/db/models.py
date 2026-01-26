"""SQLAlchemy database models based on Sophie schema."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now_ms() -> int:
    """Get current UTC timestamp in milliseconds."""
    return int(datetime.utcnow().timestamp() * 1000)


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Organization(Base):
    """Organization - the central tenant entity."""

    __tablename__ = "organization"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Localization
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC")
    country: Mapped[str | None] = mapped_column(String(2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Settings
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Timestamps (Unix milliseconds like Sophie)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="organization")
    call_history: Mapped[list["CallHistory"]] = relationship(
        "CallHistory", back_populates="organization"
    )


class Agent(Base):
    """AI Agent configuration for an organization."""

    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    # Agent configuration
    name: Mapped[str] = mapped_column(String(100), default="Majster")
    prompt: Mapped[str] = mapped_column(Text, default="")
    extra_prompt: Mapped[str | None] = mapped_column(Text)
    is_custom_prompt: Mapped[bool] = mapped_column(Boolean, default=False)

    # Model configuration
    llm_model: Mapped[str] = mapped_column(String(100), default="openai/gpt-4o-mini")
    tts_model: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    stt_model: Mapped[str] = mapped_column(String(100), default="deepgram/nova-3")

    # Settings (JSON for flexibility like Sophie)
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="ready")  # pending, ready, error

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")


class CallHistory(Base):
    """Record of all AI agent calls."""

    __tablename__ = "call_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent.id"))

    # Call details
    direction: Mapped[str] = mapped_column(String(20), default="web")  # inbound, outbound, web
    from_phone_number: Mapped[str | None] = mapped_column(String(20))
    to_phone_number: Mapped[str | None] = mapped_column(String(20))

    # Timing
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    duration: Mapped[int | None] = mapped_column(BigInteger)  # seconds

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, active, completed

    # AI-generated data
    summary: Mapped[str | None] = mapped_column(Text)
    transcript: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    analyzed_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Extra data
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="call_history"
    )
