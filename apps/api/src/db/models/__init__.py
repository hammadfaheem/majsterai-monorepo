"""SQLAlchemy ORM models package.

All model classes are re-exported here so the rest of the codebase can
continue importing from ``src.db.models`` without any changes.

Import order matters: every sub-module must be imported before the mapper
is configured (i.e. before the first query or ``Base.metadata`` inspection)
so that all foreign-key string references can be resolved. Alembic's env.py
imports this package to discover all tables for autogenerate.
"""

from .base import Base, generate_uuid, utc_now_ms

# Import all domain model modules to register them with Base.metadata
from .organization import Organization
from .user import User, Membership, MembershipUnavailability, Session
from .agent import Agent, AgentActiveSession, AgentExtraPromptVersion
from .scheduling import Schedule, Department, Availability, DepartmentAssignee
from .lead import Lead, Inquiry, Activity, Note, LeadAddress, LeadCrmIdentifiers
from .appointment import Appointment, AppointmentAssignee, AppointmentCrmIdentifiers
from .trade import TradeCategory, TradeService, TradeProduct, TradePricing, TradeModality
from .invoice import (
    Invoice,
    InvoiceItem,
    InvoicePayment,
    InvoiceSettings,
    InvoiceNote,
    InvoiceActivityLog,
)
from .call_history import CallHistory, Room, Transcript
from .scenario import Scenario, ScenarioOutcomeTemplate, Transfer
from .tag import TagBase, Tag, Task
from .notification import NotificationType, NotificationLog, OrgNotificationRecipient, Reminder
from .integration import Account, Token, Credential, WebhookSubscription, SelectedCalendar
from .communication import (
    Call,
    MessageThread,
    Message,
    Chatbot,
    ChatbotThread,
    CallNow,
    Webform,
    WebformSubmission,
)
from .phone import VirtualAssistantPhone

__all__ = [
    "Base",
    "generate_uuid",
    "utc_now_ms",
    # Organization
    "Organization",
    # User / auth
    "User",
    "Membership",
    "MembershipUnavailability",
    "Session",
    # Agent
    "Agent",
    "AgentActiveSession",
    "AgentExtraPromptVersion",
    # Scheduling
    "Schedule",
    "Department",
    "Availability",
    "DepartmentAssignee",
    # Lead / CRM
    "Lead",
    "Inquiry",
    "Activity",
    "Note",
    "LeadAddress",
    "LeadCrmIdentifiers",
    # Appointment
    "Appointment",
    "AppointmentAssignee",
    "AppointmentCrmIdentifiers",
    # Trade / pricing
    "TradeCategory",
    "TradeService",
    "TradeProduct",
    "TradePricing",
    "TradeModality",
    # Invoice
    "Invoice",
    "InvoiceItem",
    "InvoicePayment",
    "InvoiceSettings",
    "InvoiceNote",
    "InvoiceActivityLog",
    # Calls / history
    "CallHistory",
    "Room",
    "Transcript",
    # Scenarios / transfers
    "Scenario",
    "ScenarioOutcomeTemplate",
    "Transfer",
    # Tags / tasks
    "TagBase",
    "Tag",
    "Task",
    # Notifications
    "NotificationType",
    "NotificationLog",
    "OrgNotificationRecipient",
    "Reminder",
    # Integrations
    "Account",
    "Token",
    "Credential",
    "WebhookSubscription",
    "SelectedCalendar",
    # Communication
    "Call",
    "MessageThread",
    "Message",
    "Chatbot",
    "ChatbotThread",
    "CallNow",
    "Webform",
    "WebformSubmission",
    # Phone
    "VirtualAssistantPhone",
]
