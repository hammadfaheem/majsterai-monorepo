"""Transfer domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Transfer:
    """Call transfer configuration."""

    id: str
    org_id: str
    label: str
    method: str
    destination_type: str
    destination: str
    conditions: dict[str, Any] | None
    summary_format: str | None
    settings: dict[str, Any] | None
    scenario_id: str | None
    created_at: int
    updated_at: int
