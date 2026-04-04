"""Scheduling ORM models: Schedule, Department, Availability, DepartmentAssignee."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now_ms


class Schedule(Base):
    """Working schedule (time zone, optional department linkage)."""

    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC")
    department_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("department.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Department(Base):
    """Department within an organization."""

    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    default_schedule_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("schedule.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_concurrent_calls: Mapped[int | None] = mapped_column(Integer)
    escalation_timeout: Mapped[int | None] = mapped_column(Integer)  # seconds
    escalation_settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Availability(Base):
    """Availability time slots for a schedule."""

    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"), nullable=False)
    days: Mapped[list[Any] | None] = mapped_column(JSON)  # e.g. ["mon", "tue"]
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class DepartmentAssignee(Base):
    """Links a department to team members with priority ordering."""

    __tablename__ = "department_assignee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)
    priority: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
