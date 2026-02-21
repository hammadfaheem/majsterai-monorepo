"""Org notification recipient domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class OrgNotificationRecipient:
    """Who receives which notifications (per member)."""

    id: str
    member_id: str
    sms: str | None
    email: str | None
    sources: list[Any] | None
    all_tags: bool
    is_enabled: bool
    created_at: int
    updated_at: int
