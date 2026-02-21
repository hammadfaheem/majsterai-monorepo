"""Task domain entity."""

from dataclasses import dataclass


@dataclass
class Task:
    """Task linked to lead/inquiry."""

    id: str
    org_id: str
    title: str
    is_completed: bool
    type: str | None
    inquiry_id: str | None
    lead_id: str | None
    assigned_member_id: str | None
    is_created_by_sophiie: bool
    created_at: int
    updated_at: int
