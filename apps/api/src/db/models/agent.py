"""Agent ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now_ms


class Agent(Base):
    """AI agent configuration for an organization."""

    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), default="Majster")
    prompt: Mapped[str] = mapped_column(Text, default="")
    extra_prompt: Mapped[str | None] = mapped_column(Text)
    is_custom_prompt: Mapped[bool] = mapped_column(Boolean, default=False)

    llm_model: Mapped[str] = mapped_column(String(100), default="openai/gpt-4o-mini")
    tts_model: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    stt_model: Mapped[str] = mapped_column(String(100), default="deepgram/nova-3")

    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    variables: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(20), default="ready")  # pending, ready, error

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")  # type: ignore[name-defined]
    va_phones: Mapped[list["VirtualAssistantPhone"]] = relationship(  # type: ignore[name-defined]
        "VirtualAssistantPhone", back_populates="agent"
    )


class AgentExtraPromptVersion(Base):
    """Version control for agent prompt variations."""

    __tablename__ = "agent_extra_prompt_version"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    updated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class AgentActiveSession(Base):
    """Tracks currently active AI agent sessions (live calls)."""

    __tablename__ = "agent_active_session"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organization.id"))
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent.id"))
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    call_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, completed, error
    from_number: Mapped[str | None] = mapped_column(String(20))
    to_number: Mapped[str | None] = mapped_column(String(20))
    type: Mapped[str | None] = mapped_column(String(20))  # inbound, outbound, web
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
