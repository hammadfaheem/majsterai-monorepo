"""Appointment ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class Appointment(Base):
    """Scheduled appointment."""

    __tablename__ = "appointment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    serial_id: Mapped[int | None] = mapped_column(Integer)
    start: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Unix ms
    end: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30), default="PENDING"
    )  # PENDING, CONFIRMED, IN_PROGRESS, COMPLETE, CANCELLED
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    trade_service_id: Mapped[int | None] = mapped_column(Integer)
    lead_address_id: Mapped[int | None] = mapped_column(Integer)
    selected_calendar_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("selected_calendar.id"))
    attendees: Mapped[list[Any] | None] = mapped_column(JSON)
    is_rescheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_created_by_sophiie: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    customer_notes: Mapped[str | None] = mapped_column(Text)
    customer_cancellation_reason: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[list[Any] | None] = mapped_column(JSON)
    # Stores Google/Outlook event ID for deduplication during external calendar sync
    reference_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    # Never hard delete — Google sync needs cancelled events to find the row
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)


class AppointmentAssignee(Base):
    """Appointment assigned to users."""

    __tablename__ = "appointment_assignee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointment.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class AppointmentCrmIdentifiers(Base):
    """CRM sync identifiers for appointments."""

    __tablename__ = "appointment_crm_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointment.id"), nullable=False)
    crm_source: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)
    crm_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    last_sync_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
