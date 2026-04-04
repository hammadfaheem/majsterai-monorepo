"""Lead, Inquiry, Activity, Note, LeadAddress, LeadCrmIdentifiers ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now_ms


class Lead(Base):
    """Lead — customer lead management."""

    __tablename__ = "lead"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))

    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, HIRED, ARCHIVED
    source: Mapped[str | None] = mapped_column(String(50))

    last_inquiry_date: Mapped[int | None] = mapped_column(BigInteger)
    last_inquiry_id: Mapped[str | None] = mapped_column(String(36))

    suburb: Mapped[str | None] = mapped_column(String(255))
    business_name: Mapped[str | None] = mapped_column(String(255))
    socials: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_phone_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    default_lead_address_id: Mapped[int | None] = mapped_column(Integer)
    auto_reply_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    has_flagged_inquiry: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_id: Mapped[str | None] = mapped_column(String(36))
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    unread_messages: Mapped[int] = mapped_column(Integer, default=0)
    unread_calls: Mapped[int] = mapped_column(Integer, default=0)
    unread_emails: Mapped[int] = mapped_column(Integer, default=0)

    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="leads")  # type: ignore[name-defined]
    inquiries: Mapped[list["Inquiry"]] = relationship("Inquiry", back_populates="lead")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="lead")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="lead")


class Inquiry(Base):
    """Inquiry — lead inquiries from various channels."""

    __tablename__ = "inquiry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    type: Mapped[str] = mapped_column(String(50), nullable=False)  # call, email, form, chat
    message: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(255))

    summary: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(50))
    is_first_inquiry: Mapped[bool] = mapped_column(Boolean, default=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointment.id"))
    lead_address_id: Mapped[int | None] = mapped_column(Integer)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    tag: Mapped[str | None] = mapped_column(String(50))
    flag_reason: Mapped[str | None] = mapped_column(String(255))
    flagged_at: Mapped[int | None] = mapped_column(BigInteger)
    flag_issues: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    outcome_actions: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    assigned_member_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))
    is_manually_reassigned: Mapped[bool] = mapped_column(Boolean, default=False)

    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="inquiries")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="inquiries")  # type: ignore[name-defined]


class Activity(Base):
    """Activity — lead activity log."""

    __tablename__ = "activity"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)

    event: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[str | None] = mapped_column(Text)
    json_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    reference_id: Mapped[str | None] = mapped_column(String(36))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))

    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")


class Note(Base):
    """Note — lead notes."""

    __tablename__ = "note"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointment.id"))

    value: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="notes")


class LeadAddress(Base):
    """Address associated with a lead."""

    __tablename__ = "lead_address"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_id: Mapped[str] = mapped_column(String(36), nullable=False)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class LeadCrmIdentifiers(Base):
    """CRM sync identifiers for a lead."""

    __tablename__ = "lead_crm_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    crm_source: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)
    crm_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    last_sync_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
