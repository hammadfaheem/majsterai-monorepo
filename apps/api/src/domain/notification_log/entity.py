"""Notification log domain entity."""

from dataclasses import dataclass


@dataclass
class NotificationLog:
    """Log of sent notifications."""

    id: int
    type: str
    channel: str | None
    lead_id: str | None
    target_id: str | None
    sent: bool
    created_at: int
    updated_at: int
