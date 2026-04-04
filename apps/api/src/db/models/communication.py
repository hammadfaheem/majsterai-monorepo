"""Communication ORM models: Call, MessageThread, Message, Chatbot, Webform, etc."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, generate_uuid, utc_now_ms


class Call(Base):
    __tablename__ = "call"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    external_id: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    transcripts: Mapped[list[Any] | None] = mapped_column(JSON)
    duration: Mapped[int | None] = mapped_column(Integer)
    direction: Mapped[str | None] = mapped_column(String(20))
    key_points: Mapped[list[Any] | None] = mapped_column(JSON)
    recording_url_status: Mapped[str | None] = mapped_column(String(20))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class MessageThread(Base):
    __tablename__ = "message_thread"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source: Mapped[str | None] = mapped_column(String(50))
    external_id: Mapped[str | None] = mapped_column(String(255))
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Message(Base):
    __tablename__ = "message"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source: Mapped[str | None] = mapped_column(String(50))
    direction: Mapped[str | None] = mapped_column(String(20))
    sender_type: Mapped[str | None] = mapped_column(String(20))
    receiver_type: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(255))
    external_id: Mapped[str | None] = mapped_column(String(255))
    sentiment: Mapped[str | None] = mapped_column(String(20))
    summary: Mapped[str | None] = mapped_column(Text)
    key_points: Mapped[list[Any] | None] = mapped_column(JSON)
    attachments: Mapped[list[Any] | None] = mapped_column(JSON)
    message_thread_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("message_thread.id"))
    replied_by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    content_storage: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Chatbot(Base):
    __tablename__ = "chatbot"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class ChatbotThread(Base):
    __tablename__ = "chatbot_thread"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    external_id: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    transcripts: Mapped[list[Any] | None] = mapped_column(JSON)
    started_at: Mapped[int | None] = mapped_column(BigInteger)
    ended_at: Mapped[int | None] = mapped_column(BigInteger)
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class CallNow(Base):
    __tablename__ = "call_now"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    country_restriction_type: Mapped[str | None] = mapped_column(String(20))
    countries: Mapped[list[Any] | None] = mapped_column(JSON)
    dial_code_restriction_type: Mapped[str | None] = mapped_column(String(20))
    dial_codes: Mapped[list[Any] | None] = mapped_column(JSON)
    blocked_phone_numbers: Mapped[list[Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Webform(Base):
    __tablename__ = "webform"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    inputs: Mapped[list[Any] | None] = mapped_column(JSON)
    title: Mapped[str | None] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class WebformSubmission(Base):
    __tablename__ = "webform_submission"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    webform_id: Mapped[str] = mapped_column(String(36), ForeignKey("webform.id"), nullable=False)
    submission_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    submitted_at: Mapped[int | None] = mapped_column(BigInteger)
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    session_id: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
