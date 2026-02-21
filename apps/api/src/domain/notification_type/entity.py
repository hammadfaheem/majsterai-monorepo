"""Notification type domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class NotificationType:
    """Org-level notification template."""

    id: str
    org_id: str
    value: str
    template: dict[str, Any] | None
    channels: list[Any] | None
    schedule: dict[str, Any] | None
    enabled: bool
    created_at: int
    updated_at: int
