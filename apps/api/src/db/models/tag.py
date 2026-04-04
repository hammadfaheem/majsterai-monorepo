"""TagBase, Tag, and Task ORM models."""

from sqlalchemy import BigInteger, Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class TagBase(Base):
    """Tag definition (template) for an organization."""

    __tablename__ = "tag_base"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # LEAD, INQUIRY
    description: Mapped[str | None] = mapped_column(Text)
    external_id: Mapped[str | None] = mapped_column(String(255))
    external_type: Mapped[str | None] = mapped_column(String(50))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Tag(Base):
    """Tag applied to a lead, inquiry, or notification recipient."""

    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_base_id: Mapped[str] = mapped_column(String(36), ForeignKey("tag_base.id"), nullable=False)
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    org_notification_recipient_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("org_notification_recipient.id")
    )
    member_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)


class Task(Base):
    """Task associated with a lead or inquiry."""

    __tablename__ = "task"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[str | None] = mapped_column(String(50))
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    assigned_member_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))
    is_created_by_sophiie: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
