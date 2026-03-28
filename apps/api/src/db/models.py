"""SQLAlchemy database models based on Sophie schema."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Float, Integer, JSON, BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def utc_now_ms() -> int:
    """Get current UTC timestamp in milliseconds."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class Organization(Base):
    """Organization - the central tenant entity."""

    __tablename__ = "organization"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Localization
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC")
    country: Mapped[str | None] = mapped_column(String(2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Sophiie: billing & scheduling
    stripe_plan: Mapped[str | None] = mapped_column(String(50))  # FREE, PRO, ENTERPRISE
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    default_schedule_id: Mapped[int | None] = mapped_column(Integer)  # FK added in Phase 3
    public_scheduler_configurations: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    tag: Mapped[str | None] = mapped_column(String(50))  # DEMO, TEST, LIVE, PAUSED, CHURN_*
    seats: Mapped[int | None] = mapped_column(Integer)
    addons: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    main_trade_category_id: Mapped[int | None] = mapped_column(Integer)  # FK in Phase 4 migration

    # Settings
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Timestamps (Unix milliseconds like Sophie)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="organization")
    call_history: Mapped[list["CallHistory"]] = relationship(
        "CallHistory", back_populates="organization"
    )
    memberships: Mapped[list["Membership"]] = relationship(
        "Membership", back_populates="organization"
    )
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="organization")
    inquiries: Mapped[list["Inquiry"]] = relationship("Inquiry", back_populates="organization")
    transcripts: Mapped[list["Transcript"]] = relationship("Transcript", back_populates="organization")


class Agent(Base):
    """AI Agent configuration for an organization."""

    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    # Agent configuration
    name: Mapped[str] = mapped_column(String(100), default="Majster")
    prompt: Mapped[str] = mapped_column(Text, default="")
    extra_prompt: Mapped[str | None] = mapped_column(Text)
    is_custom_prompt: Mapped[bool] = mapped_column(Boolean, default=False)

    # Model configuration
    llm_model: Mapped[str] = mapped_column(String(100), default="openai/gpt-4o-mini")
    tts_model: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    stt_model: Mapped[str] = mapped_column(String(100), default="deepgram/nova-3")

    # Settings (JSON for flexibility like Sophie)
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    # Sophiie: prompt templating variables
    variables: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="ready")  # pending, ready, error

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")


class User(Base):
    """User - Authentication and user profile."""

    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Sophiie: profile & verification
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[str | None] = mapped_column(String(20))  # SUPERADMIN, STAFF, CUSTOMER
    email_verified: Mapped[int | None] = mapped_column(BigInteger)
    phone_verified: Mapped[int | None] = mapped_column(BigInteger)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    memberships: Mapped[list["Membership"]] = relationship("Membership", back_populates="user")


class Membership(Base):
    """Organization membership - Links users to organizations with roles."""

    __tablename__ = "membership"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))  # nullable for pending invites

    # Role: owner, admin, member
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    # Sophiie: invite & profile
    invited_email: Mapped[str | None] = mapped_column(String(255))
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_point_of_escalation: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduling_priority: Mapped[int | None] = mapped_column(Integer)
    responsibility: Mapped[str | None] = mapped_column(Text)
    personalisation_notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="memberships")
    user: Mapped["User | None"] = relationship("User", back_populates="memberships")
    unavailabilities: Mapped[list["MembershipUnavailability"]] = relationship(
        "MembershipUnavailability", back_populates="membership"
    )


class MembershipUnavailability(Base):
    """When a team member is unavailable (vacation, recurring blocks)."""

    __tablename__ = "membership_unavailability"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)

    start_date: Mapped[int | None] = mapped_column(BigInteger)  # date as ms or day timestamp
    end_date: Mapped[int | None] = mapped_column(BigInteger)
    start_time: Mapped[int | None] = mapped_column(BigInteger)  # time-of-day
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    recurrence_type: Mapped[str | None] = mapped_column(String(20))  # WEEKLY, MONTHLY
    days_of_week: Mapped[list[str] | None] = mapped_column(JSON)

    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    membership: Mapped["Membership"] = relationship("Membership", back_populates="unavailabilities")


class Session(Base):
    """Web session for session-based auth (optional)."""

    __tablename__ = "session"

    session_token: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    expires: Mapped[int] = mapped_column(BigInteger, nullable=False)
    impersonating_from_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    active_membership_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))


class AgentExtraPromptVersion(Base):
    """Version control for agent prompt variations."""

    __tablename__ = "agent_extra_prompt_version"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    updated_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class AgentActiveSession(Base):
    """Tracks currently active AI agent sessions (live calls)."""

    __tablename__ = "agent_active_session"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    call_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, completed, error
    from_number: Mapped[str | None] = mapped_column(String(20))
    to_number: Mapped[str | None] = mapped_column(String(20))
    type: Mapped[str | None] = mapped_column(String(20))  # inbound, outbound, web
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Scenario(Base):
    """Predefined conversation flows and responses."""

    __tablename__ = "scenario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    response: Mapped[str | None] = mapped_column(Text)
    trigger_type: Mapped[str | None] = mapped_column(String(20))  # KEYWORD, INTENT
    trigger_value: Mapped[str | None] = mapped_column(String(255))
    questions: Mapped[list[Any] | None] = mapped_column(JSON)
    outcome: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    trade_service_id: Mapped[int | None] = mapped_column(Integer)  # FK in Phase 4
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class ScenarioOutcomeTemplate(Base):
    """Templates for actions after scenarios (SMS/email)."""

    __tablename__ = "scenario_outcome_template"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenario.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # SMS, EMAIL
    subject: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Transfer(Base):
    """Call transfer configuration."""

    __tablename__ = "transfer"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # COLD, WARM
    destination_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DEPARTMENT, MEMBER, PHONE
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    conditions: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    summary_format: Mapped[str | None] = mapped_column(Text)
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    scenario_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("scenario.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Room(Base):
    """LiveKit rooms for real-time communication."""

    __tablename__ = "room"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    last_active_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


# --- Phase 3: Scheduling ---


class Schedule(Base):
    """Working schedule (time zone, optional department)."""

    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(50), default="UTC")
    department_id: Mapped[int | None] = mapped_column(Integer)  # FK added after Department exists


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
    """Availability slots for a schedule."""

    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"), nullable=False)
    days: Mapped[list[Any] | None] = mapped_column(JSON)  # e.g. ["mon", "tue"]
    start_time: Mapped[int | None] = mapped_column(BigInteger)  # time of day in ms or minutes
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class DepartmentAssignee(Base):
    """Link department to members with priority."""

    __tablename__ = "department_assignee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)
    priority: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class SelectedCalendar(Base):
    """Calendar selected for a member (OAuth credential reference)."""

    __tablename__ = "selected_calendar"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    credential_id: Mapped[str | None] = mapped_column(String(255))  # FK when credential table exists
    calendar_id: Mapped[str | None] = mapped_column(String(255))
    calendar_name: Mapped[str | None] = mapped_column(String(255))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active_for_conflict_check: Mapped[bool] = mapped_column(Boolean, default=True)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("membership.id"), nullable=False)
    channel_id: Mapped[str | None] = mapped_column(String(255))
    resource_id: Mapped[str | None] = mapped_column(String(255))
    channel_expiration: Mapped[int | None] = mapped_column(BigInteger)
    last_synced_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Appointment(Base):
    """Scheduled appointment."""

    __tablename__ = "appointment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    serial_id: Mapped[int | None] = mapped_column(Integer)  # org-scoped display number
    start: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Unix ms
    end: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="scheduled")  # scheduled, completed, cancelled, no_show
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    trade_service_id: Mapped[int | None] = mapped_column(Integer)  # FK in Phase 4
    lead_address_id: Mapped[int | None] = mapped_column(Integer)  # FK in Phase 6
    selected_calendar_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("selected_calendar.id"))
    attendees: Mapped[list[Any] | None] = mapped_column(JSON)
    is_rescheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_created_by_sophiie: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    customer_notes: Mapped[str | None] = mapped_column(Text)
    customer_cancellation_reason: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[list[Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class AppointmentAssignee(Base):
    """Appointment assigned to users."""

    __tablename__ = "appointment_assignee"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointment.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class AppointmentCrmIdentifiers(Base):
    """CRM sync identifiers for appointments."""

    __tablename__ = "appointment_crm_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointment.id"), nullable=False)
    crm_source: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)
    crm_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    last_sync_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


# --- Phase 4: Business services and pricing (trade_*) ---


class TradeCategory(Base):
    """Category of trade (e.g. plumbing, electrical)."""

    __tablename__ = "trade_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))  # service, product
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeService(Base):
    """Service offered (e.g. drain cleaning)."""

    __tablename__ = "trade_service"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)  # minutes
    duration_unit: Mapped[str | None] = mapped_column(String(20))  # minutes, hours
    followup_questions: Mapped[list[Any] | None] = mapped_column(JSON)
    pricing_mode: Mapped[str | None] = mapped_column(String(20))  # fixed, hourly, quote
    fixed_price: Mapped[int | None] = mapped_column(Integer)  # cents
    hourly_rate: Mapped[int | None] = mapped_column(Integer)
    min_price: Mapped[int | None] = mapped_column(Integer)
    max_price: Mapped[int | None] = mapped_column(Integer)
    call_out_fee: Mapped[int | None] = mapped_column(Integer)
    plus_gst: Mapped[bool] = mapped_column(Boolean, default=False)
    plus_materials: Mapped[bool] = mapped_column(Boolean, default=False)
    is_disclose_price: Mapped[bool] = mapped_column(Boolean, default=True)
    custom_price_response: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trade_category.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeProduct(Base):
    """Product offered."""

    __tablename__ = "trade_product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)  # cents
    max_price: Mapped[int | None] = mapped_column(Integer)
    pricing_type: Mapped[str | None] = mapped_column(String(20))
    faqs: Mapped[list[Any] | None] = mapped_column(JSON)
    is_disclose_price: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trade_category.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradePricing(Base):
    """Pricing config per trade category."""

    __tablename__ = "trade_pricing"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trade_category_id: Mapped[int] = mapped_column(ForeignKey("trade_category.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    call_out_fee: Mapped[int | None] = mapped_column(Integer)
    hour_rate: Mapped[int | None] = mapped_column(Integer)
    tax_rate: Mapped[float | None] = mapped_column(Float)
    after_hours: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class TradeModality(Base):
    """Service area / modality (e.g. mobile, location)."""

    __tablename__ = "trade_modality"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50))
    address_id: Mapped[int | None] = mapped_column(Integer)
    origin_suburb: Mapped[str | None] = mapped_column(String(255))
    travel_distance_km: Mapped[int | None] = mapped_column(Integer)
    service_area: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    postcode_list: Mapped[list[Any] | None] = mapped_column(JSON)
    exception_postcode_list: Mapped[list[Any] | None] = mapped_column(JSON)
    landmark: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


# --- Phase 5: Invoicing ---


class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    index: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, sent, paid, overdue, cancelled
    date: Mapped[int | None] = mapped_column(BigInteger)
    due_date: Mapped[int | None] = mapped_column(BigInteger)
    tax_type: Mapped[str | None] = mapped_column(String(20))
    reference: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    accept_credit_card: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
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


class CallHistory(Base):
    """Record of all AI agent calls."""

    __tablename__ = "call_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agent.id"))

    # Call details
    direction: Mapped[str] = mapped_column(String(20), default="web")  # inbound, outbound, web
    from_phone_number: Mapped[str | None] = mapped_column(String(20))
    to_phone_number: Mapped[str | None] = mapped_column(String(20))

    # Timing
    start_time: Mapped[int | None] = mapped_column(BigInteger)
    end_time: Mapped[int | None] = mapped_column(BigInteger)
    duration: Mapped[int | None] = mapped_column(BigInteger)  # seconds

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, active, completed

    # AI-generated data
    summary: Mapped[str | None] = mapped_column(Text)
    transcript: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    analyzed_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    # Sophiie extensions
    twilio_call_sid: Mapped[str | None] = mapped_column(String(255))
    function_calls: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    cost: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    total_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    variables: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Extra data
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="call_history"
    )


class Lead(Base):
    """Lead - Customer lead management."""

    __tablename__ = "lead"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    # Contact information
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Lead details
    status: Mapped[str] = mapped_column(
        String(20), default="new"
    )  # new, contacted, qualified, converted, lost
    source: Mapped[str | None] = mapped_column(String(50))  # web, phone, referral, etc.

    # Tracking
    last_inquiry_date: Mapped[int | None] = mapped_column(BigInteger)
    last_contact_date: Mapped[int | None] = mapped_column(BigInteger)

    # Sophiie Phase 6
    suburb: Mapped[str | None] = mapped_column(String(255))
    business_name: Mapped[str | None] = mapped_column(String(255))
    socials: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_phone_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    default_lead_address_id: Mapped[int | None] = mapped_column(Integer)
    last_inquiry_id: Mapped[str | None] = mapped_column(String(36))
    auto_reply_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    has_flagged_inquiry: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_id: Mapped[str | None] = mapped_column(String(36))
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)

    # Additional data
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="leads")
    inquiries: Mapped[list["Inquiry"]] = relationship("Inquiry", back_populates="lead")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="lead")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="lead")


class Inquiry(Base):
    """Inquiry - Lead inquiries from various sources."""

    __tablename__ = "inquiry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    # Inquiry details
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # call, email, form, chat
    message: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(255))

    # Sophiie Phase 6
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

    # Additional data
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="inquiries")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="inquiries")


class Activity(Base):
    """Activity - Lead activity log."""

    __tablename__ = "activity"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)

    # Activity details
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # call, email, meeting, note
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(36))
    json_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Additional data
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, name="metadata")

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")


class Note(Base):
    """Note - Lead notes."""

    __tablename__ = "note"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointment.id"))

    # Note content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="notes")


# Phase 6: tag_base, tag, task, lead_address, lead_crm_identifiers
class TagBase(Base):
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
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_base_id: Mapped[str] = mapped_column(String(36), ForeignKey("tag_base.id"), nullable=False)
    inquiry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("inquiry.id"))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("lead.id"))
    org_notification_recipient_id: Mapped[str | None] = mapped_column(String(36))
    member_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("membership.id"))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)


class Task(Base):
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


class LeadAddress(Base):
    __tablename__ = "lead_address"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_id: Mapped[str] = mapped_column(String(36), nullable=False)  # reference to address entity if any
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class LeadCrmIdentifiers(Base):
    __tablename__ = "lead_crm_identifiers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("lead.id"), nullable=False)
    crm_source: Mapped[str] = mapped_column(String(50), nullable=False)
    identifier_type: Mapped[str] = mapped_column(String(50), nullable=False)
    crm_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    last_sync_at: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


# --- Phase 7: Communication and messaging ---
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


# --- Phase 8: Notifications and reminders ---
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
    priority: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


# --- Phase 9: Auth and integrations ---
class Account(Base):
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
    __tablename__ = "token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(255))
    data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    expires: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)


class VerificationToken(Base):
    __tablename__ = "verification_token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)


class Credential(Base):
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
    __tablename__ = "webhook_subscription"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[list[Any] | None] = mapped_column(JSON)
    secret: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)


class Transcript(Base):
    """Transcript - Full call transcripts with segments."""

    __tablename__ = "transcript"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organization.id"), nullable=False)

    # Transcript content
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    segments: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # Timestamped segments

    # Analysis
    sentiment: Mapped[str | None] = mapped_column(String(20))  # positive, neutral, negative
    keywords: Mapped[list[str] | None] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=utc_now_ms, onupdate=utc_now_ms)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="transcripts")
