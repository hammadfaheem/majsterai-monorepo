"""Scenario, ScenarioOutcomeTemplate, and Transfer ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class Scenario(Base):
    """Predefined conversation flows and AI responses."""

    __tablename__ = "scenario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    response: Mapped[str | None] = mapped_column(Text)
    trigger_type: Mapped[str | None] = mapped_column(String(20))  # KEYWORD, INTENT
    trigger_value: Mapped[str | None] = mapped_column(String(255))
    questions: Mapped[list[Any] | None] = mapped_column(JSON)
    outcome: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    trade_service_id: Mapped[int | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class ScenarioOutcomeTemplate(Base):
    """Post-scenario action templates (SMS/email)."""

    __tablename__ = "scenario_outcome_template"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenario.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # SMS, EMAIL
    subject: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Transfer(Base):
    """Call transfer configuration."""

    __tablename__ = "transfer"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # COLD, WARM
    destination_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DEPARTMENT, MEMBER, PHONE
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    conditions: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    summary_format: Mapped[str | None] = mapped_column(Text)
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    scenario_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("scenario.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
