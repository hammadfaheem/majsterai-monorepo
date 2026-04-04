"""VirtualAssistantPhone ORM model."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now_ms


class VirtualAssistantPhone(Base):
    """Phone number provisioned from Twilio, assigned to an org/agent for voice AI."""

    __tablename__ = "virtual_assistant_phone"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # Core Twilio identity
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    twilio_sid: Mapped[str] = mapped_column(String(34), unique=True, nullable=False)

    # One phone per org (enforced by unique constraint on org_id)
    org_id: Mapped[str] = mapped_column(
        String(191), ForeignKey("organization.id"), unique=True, nullable=False
    )
    agent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent.id"), nullable=False)
    assigned_by: Mapped[str] = mapped_column(String(191), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, active
    type: Mapped[str | None] = mapped_column(String(255))  # e.g. "external"

    # SMS settings
    is_sms_listening: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    global_sms_auto_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_lead_sms_auto_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Twilio Elastic SIP Trunk fields
    trunk_sid: Mapped[str | None] = mapped_column(String(255))
    sip_domain: Mapped[str | None] = mapped_column(String(255))
    sip_username: Mapped[str | None] = mapped_column(String(255))
    sip_password: Mapped[str | None] = mapped_column(String(255))
    credential_list_sid: Mapped[str | None] = mapped_column(String(255))
    trunk_termination_url: Mapped[str | None] = mapped_column(String(255))

    # LiveKit SIP fields
    livekit_trunk_id: Mapped[str | None] = mapped_column(String(255))
    livekit_inbound_trunk_id: Mapped[str | None] = mapped_column(String(255))
    livekit_outbound_trunk_id: Mapped[str | None] = mapped_column(String(255))
    livekit_inbound_dispatch_rule_id: Mapped[str | None] = mapped_column(String(255))

    # Recording
    recording_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    recording_public: Mapped[bool] = mapped_column(Boolean, default=False)

    # Per-org LiveKit credential overrides for multi-tenant setups
    # Shape: {"livekitWsUrl": "wss://...", "livekitApiKey": "...", "livekitApiSecret": "...", "livekitSipDomain": "..."}
    custom_credentials: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    schedule_deleted_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    organization: Mapped["Organization"] = relationship(  # type: ignore[name-defined]
        "Organization", back_populates="va_phone"
    )
    agent: Mapped["Agent"] = relationship("Agent", back_populates="va_phones")  # type: ignore[name-defined]
