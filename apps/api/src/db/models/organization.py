"""Organization ORM model."""

from typing import Any

from sqlalchemy import BigInteger, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now_ms


class Organization(Base):
    """Organization — the central tenant entity."""

    __tablename__ = "organization"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Localization
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC")
    country: Mapped[str | None] = mapped_column(String(2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Billing & scheduling
    stripe_plan: Mapped[str | None] = mapped_column(String(50))  # FREE, PRO, ENTERPRISE
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    default_schedule_id: Mapped[int | None] = mapped_column(Integer)
    public_scheduler_configurations: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    tag: Mapped[str | None] = mapped_column(String(50))  # DEMO, TEST, LIVE, PAUSED, CHURN_*
    seats: Mapped[int | None] = mapped_column(Integer)
    addons: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    main_trade_category_id: Mapped[int | None] = mapped_column(Integer)

    # Settings
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Timestamps (Unix milliseconds)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="organization")  # type: ignore[name-defined]
    call_history: Mapped[list["CallHistory"]] = relationship("CallHistory", back_populates="organization")  # type: ignore[name-defined]
    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="organization")  # type: ignore[name-defined]
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="organization")  # type: ignore[name-defined]
    inquiries: Mapped[list["Inquiry"]] = relationship("Inquiry", back_populates="organization")  # type: ignore[name-defined]
    va_phone: Mapped["VirtualAssistantPhone | None"] = relationship(  # type: ignore[name-defined]
        "VirtualAssistantPhone", back_populates="organization", uselist=False
    )
