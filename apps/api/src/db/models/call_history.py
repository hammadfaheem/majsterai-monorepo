"""CallHistory, Room, and Transcript ORM models."""

from typing import Any

from sqlalchemy import BigInteger, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now_ms


class CallHistory(Base):
    """Record of all AI agent calls."""

    __tablename__ = "call_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent.id"))

    direction: Mapped[str] = mapped_column(String(20), default="web")  # inbound, outbound, web
    from_phone_number: Mapped[str | None] = mapped_column(String(20))
    to_phone_number: Mapped[str | None] = mapped_column(String(20))

    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    duration: Mapped[int | None] = mapped_column(BigInteger)  # seconds

    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, active, completed

    summary: Mapped[str | None] = mapped_column(Text)
    analyzed_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    twilio_call_sid: Mapped[str | None] = mapped_column(String(255))
    function_calls: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    cost: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    total_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    variables: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    organization: Mapped["Organization"] = relationship(  # type: ignore[name-defined]
        "Organization", back_populates="call_history"
    )


class Room(Base):
    """LiveKit rooms for real-time communication."""

    __tablename__ = "room"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    last_active_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Transcript(Base):
    """Conversation transcripts stored separately for efficient retrieval."""

    __tablename__ = "transcript"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    transcript: Mapped[list[Any] | None] = mapped_column(JSON)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
