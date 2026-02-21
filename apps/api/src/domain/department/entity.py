"""Department domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Department:
    """Department within an organization."""

    id: int
    org_id: str
    name: str
    description: str | None
    default_schedule_id: int | None
    is_active: bool
    max_concurrent_calls: int | None
    escalation_timeout: int | None
    escalation_settings: dict[str, Any] | None
    created_at: int
    updated_at: int
