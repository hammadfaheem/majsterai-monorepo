"""TagBase domain entity."""

from dataclasses import dataclass


@dataclass
class TagBase:
    """Org-level tag definition."""

    id: str
    org_id: str
    value: str
    color: str | None
    type: str  # LEAD, INQUIRY
    description: str | None
    external_id: str | None
    external_type: str | None
    is_enabled: bool
    created_at: int
    updated_at: int
