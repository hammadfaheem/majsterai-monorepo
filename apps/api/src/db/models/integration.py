"""Integration ORM models: Account, Token, Credential, WebhookSubscription, SelectedCalendar."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class Account(Base):
    """OAuth provider account linked to a user."""

    __tablename__ = "account"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[str | None] = mapped_column(Text)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Token(Base):
    """Short-lived verification / magic-link tokens."""

    __tablename__ = "token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(255))
    data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    expires: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)


class Credential(Base):
    """OAuth credentials for external integrations (calendar, CRM, etc.)."""

    __tablename__ = "credential"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organization.id"))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # calendar, crm, etc.
    access_token: Mapped[str | None] = mapped_column(Text)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class WebhookSubscription(Base):
    """Outbound webhook subscriptions for an organization."""

    __tablename__ = "webhook_subscription"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[list[Any] | None] = mapped_column(JSON)
    secret: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class SelectedCalendar(Base):
    """Calendar selected for a member (linked to an OAuth credential)."""

    __tablename__ = "selected_calendar"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organization.id"))
    credential_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("credential.id"))
    calendar_id: Mapped[str | None] = mapped_column(String(255))
    calendar_name: Mapped[str | None] = mapped_column(String(255))
    integration: Mapped[str | None] = mapped_column(String(20))  # google, outlook
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active_for_conflict_check: Mapped[bool] = mapped_column(Boolean, default=True)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)
    channel_id: Mapped[str | None] = mapped_column(String(255))
    resource_id: Mapped[str | None] = mapped_column(String(255))
    channel_expiration: Mapped[int | None] = mapped_column(BigInteger)
    last_synced_at: Mapped[int | None] = mapped_column(BigInteger)
    # Google's nextSyncToken for incremental sync
    next_async_token: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
