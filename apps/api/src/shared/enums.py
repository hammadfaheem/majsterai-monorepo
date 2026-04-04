"""Domain-wide string enumerations.

Using ``StrEnum`` (Python 3.11+) means enum members compare equal to their
string values, so existing string comparisons in routers and repositories
continue to work without modification while the type system enforces valid
values everywhere.
"""

from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


# ---------------------------------------------------------------------------
# User / Auth
# ---------------------------------------------------------------------------


class UserRole(StrEnum):
    SUPERADMIN = "SUPERADMIN"
    STAFF = "STAFF"
    CUSTOMER = "CUSTOMER"


class MembershipRole(StrEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    USER = "USER"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class AgentStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Call / Session
# ---------------------------------------------------------------------------


class CallDirection(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    WEB = "web"


class CallStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class ActiveSessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"


# ---------------------------------------------------------------------------
# Lead / CRM
# ---------------------------------------------------------------------------


class LeadStatus(StrEnum):
    PENDING = "PENDING"
    HIRED = "HIRED"
    ARCHIVED = "ARCHIVED"


class InquiryType(StrEnum):
    CALL = "call"
    EMAIL = "email"
    FORM = "form"
    CHAT = "chat"


# ---------------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------------


class AppointmentStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


class InvoiceStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Transfer
# ---------------------------------------------------------------------------


class TransferMethod(StrEnum):
    COLD = "COLD"
    WARM = "WARM"


class TransferDestinationType(StrEnum):
    DEPARTMENT = "DEPARTMENT"
    MEMBER = "MEMBER"
    PHONE = "PHONE"


# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------


class ScenarioTriggerType(StrEnum):
    KEYWORD = "KEYWORD"
    INTENT = "INTENT"


# ---------------------------------------------------------------------------
# Notification / Messaging
# ---------------------------------------------------------------------------


class NotificationChannel(StrEnum):
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"


class MessageDirection(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class SenderType(StrEnum):
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------


class RecurrenceType(StrEnum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


# ---------------------------------------------------------------------------
# Trade / Pricing
# ---------------------------------------------------------------------------


class PricingMode(StrEnum):
    FIXED = "fixed"
    HOURLY = "hourly"
    QUOTE = "quote"


# ---------------------------------------------------------------------------
# Stripe plan
# ---------------------------------------------------------------------------


class StripePlan(StrEnum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


# ---------------------------------------------------------------------------
# Virtual assistant phone
# ---------------------------------------------------------------------------


class VirtualPhoneStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
