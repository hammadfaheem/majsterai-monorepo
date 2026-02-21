"""Membership unavailability domain entity."""

from dataclasses import dataclass


@dataclass
class MembershipUnavailability:
    """When a team member is unavailable (vacation, recurring blocks)."""

    id: str
    member_id: str
    start_date: int | None
    end_date: int | None
    start_time: int | None
    end_time: int | None
    recurrence_type: str | None  # WEEKLY, MONTHLY
    days_of_week: list[str] | None
    created_at: int
    updated_at: int
