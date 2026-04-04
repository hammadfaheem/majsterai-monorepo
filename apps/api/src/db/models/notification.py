"""Notification and Reminder ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class NotificationType(Base):
    __tablename__ = "notification_type"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    template: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    channels: Mapped[list[Any] | None] = mapped_column(JSON)
    schedule: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(20))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    target_id: Mapped[str | None] = mapped_column(String(36))
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class OrgNotificationRecipient(Base):
    __tablename__ = "org_notification_recipient"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)
    sms: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    sources: Mapped[list[Any] | None] = mapped_column(JSON)
    all_tags: Mapped[bool] = mapped_column(Boolean, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Reminder(Base):
    __tablename__ = "reminder"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointment.id"))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    datetime: Mapped[int | None] = mapped_column(BigInteger)
    notes: Mapped[str | None] = mapped_column(Text)
    notes_type: Mapped[str | None] = mapped_column(String(20))
    priority: Mapped[str | None] = mapped_column(String(20))  # LOW, MEDIUM, HIGH
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
