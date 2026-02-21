"""Reminder domain entity."""

from dataclasses import dataclass


@dataclass
class Reminder:
    """Scheduled reminder for lead or appointment follow-up."""

    id: str
    lead_id: str | None
    appointment_id: str | None
    user_id: str | None
    datetime: int | None
    notes: str | None
    notes_type: str | None  # CALL, TEXT, EMAIL
    priority: int | None  # LOW=1, MEDIUM=2, HIGH=3
    created_at: int
    updated_at: int
