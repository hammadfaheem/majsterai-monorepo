"""Organization domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Organization:
    """Organization domain entity - pure business logic."""

    id: str
    name: str
    slug: str
    time_zone: str
    country: str | None
    currency: str
    settings: dict[str, Any] | None
    created_at: int
    updated_at: int
    deleted_at: int | None = None
    # Sophiie extensions
    stripe_plan: str | None = None
    stripe_customer_id: str | None = None
    default_schedule_id: int | None = None
    public_scheduler_configurations: dict[str, Any] | None = None
    tag: str | None = None
    seats: int | None = None
    addons: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate organization entity."""
        if not self.name or len(self.name.strip()) < 1:
            raise ValueError("Organization name cannot be empty")
        if not self.slug or len(self.slug.strip()) < 1:
            raise ValueError("Organization slug cannot be empty")
        if self.settings is None:
            self.settings = {}

    def is_deleted(self) -> bool:
        """Check if organization is soft deleted."""
        return self.deleted_at is not None
