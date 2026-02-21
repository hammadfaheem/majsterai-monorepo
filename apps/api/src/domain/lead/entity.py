"""Lead domain entities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Lead:
    """Lead domain entity."""

    id: str
    org_id: str
    email: str | None
    phone: str | None
    name: str
    status: str  # new, contacted, qualified, converted, lost
    source: str | None
    last_inquiry_date: int | None
    last_contact_date: int | None
    metadata: dict[str, Any] | None
    created_at: int
    updated_at: int
    deleted_at: int | None = None


@dataclass
class Inquiry:
    """Inquiry domain entity."""

    id: str
    lead_id: str
    org_id: str
    type: str  # call, email, form, chat
    message: str | None
    subject: str | None
    metadata: dict[str, Any] | None
    created_at: int


@dataclass
class Activity:
    """Activity domain entity."""

    id: str
    lead_id: str
    type: str  # call, email, meeting, note
    description: str
    metadata: dict[str, Any] | None
    created_at: int


@dataclass
class Note:
    """Note domain entity."""

    id: str
    lead_id: str
    content: str
    created_at: int
    updated_at: int
