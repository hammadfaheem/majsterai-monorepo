"""Invoice ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    index: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(30), default="draft"
    )  # draft, sent, paid, overdue, cancelled
    date: Mapped[int | None] = mapped_column(BigInteger)
    due_date: Mapped[int | None] = mapped_column(BigInteger)
    tax_type: Mapped[str | None] = mapped_column(String(20))
    reference: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    accept_credit_card: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_overdue_reminder: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_due_reminder: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_paid_reminder: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[int | None] = mapped_column(BigInteger)
    sent_at: Mapped[int | None] = mapped_column(BigInteger)
    external_id: Mapped[str | None] = mapped_column(String(255))
    last_synced_at: Mapped[int | None] = mapped_column(BigInteger)
    is_sync_failed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoice.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # cents
    external_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class InvoicePayment(Base):
    __tablename__ = "invoice_payment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoice.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # cents
    date: Mapped[int | None] = mapped_column(BigInteger)
    method: Mapped[str | None] = mapped_column(String(50))
    reference: Mapped[str | None] = mapped_column(String(255))
    account: Mapped[str | None] = mapped_column(String(255))
    external_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class InvoiceSettings(Base):
    __tablename__ = "invoice_settings"

    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), primary_key=True)
    tax_rate: Mapped[float | None] = mapped_column(Float)
    index_prefix: Mapped[str | None] = mapped_column(String(20))
    payment_terms: Mapped[str | None] = mapped_column(String(100))
    show_logo: Mapped[bool] = mapped_column(Boolean, default=True)
    accent_color: Mapped[str | None] = mapped_column(String(20))
    footer: Mapped[str | None] = mapped_column(Text)
    enable_voice: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_to_xero: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_from_xero: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_timing: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class InvoiceNote(Base):
    __tablename__ = "invoice_note"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoice.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class InvoiceActivityLog(Base):
    __tablename__ = "invoice_activity_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoice.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
