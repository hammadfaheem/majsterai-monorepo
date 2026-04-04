"""User, Membership, MembershipUnavailability, and Session ORM models."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid, utc_now_ms


class User(Base):
    """User — authentication and profile."""

    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[str | None] = mapped_column(String(20))  # SUPERADMIN, STAFF, CUSTOMER
    email_verified: Mapped[int | None] = mapped_column(BigInteger)
    phone_verified: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="user")


class Membership(Base):
    """Membership — links users to organizations with a role."""

    __tablename__ = "membership"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))

    role: Mapped[str] = mapped_column(String(20), default="USER", nullable=False)  # OWNER, ADMIN, USER

    invited_email: Mapped[str | None] = mapped_column(String(255))
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_point_of_escalation: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduling_priority: Mapped[int | None] = mapped_column(Integer)
    responsibility: Mapped[str | None] = mapped_column(Text)
    personalisation_notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="memberships")  # type: ignore[name-defined]
    user: Mapped["User | None"] = relationship("User", back_populates="memberships")
    unavailabilities: Mapped[list["MembershipUnavailability"]] = relationship(
        "MembershipUnavailability", back_populates="membership"
    )


class MembershipUnavailability(Base):
    """Time blocks when a team member is unavailable."""

    __tablename__ = "membership_unavailability"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)

    start_date: Mapped[int | None] = mapped_column(BigInteger)
    end_date: Mapped[int | None] = mapped_column(BigInteger)
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    recurrence_type: Mapped[str | None] = mapped_column(String(20))  # WEEKLY, MONTHLY
    days_of_week: Mapped[list[str] | None] = mapped_column(JSON)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    membership: Mapped["Membership"] = relationship("Membership", back_populates="unavailabilities")


class Session(Base):
    """Web session for session-based auth."""

    __tablename__ = "session"

    session_token: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    expires: Mapped[int] = mapped_column(BigInteger, nullable=False)
    impersonating_from_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    active_membership_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))
