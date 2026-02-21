"""Membership domain entity."""

from dataclasses import dataclass


@dataclass
class Membership:
    """Membership domain entity - Links users to organizations with roles."""

    id: str
    org_id: str
    user_id: str | None
    role: str  # owner, admin, member
    created_at: int
    updated_at: int
    invited_email: str | None = None
    is_disabled: bool = False
    is_point_of_escalation: bool = False
    scheduling_priority: int | None = None
    responsibility: str | None = None
    personalisation_notes: str | None = None
