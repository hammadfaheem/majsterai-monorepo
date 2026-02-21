"""Call history domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CallHistory:
    """Call history domain entity - pure business logic."""

    id: int
    room_name: str
    org_id: str
    agent_id: int | None
    direction: str
    from_phone_number: str | None
    to_phone_number: str | None
    start_time: int | None
    end_time: int | None
    duration: int | None
    status: str
    summary: str | None
    transcript: dict[str, Any] | None
    analyzed_data: dict[str, Any] | None
    extra_data: dict[str, Any] | None
    created_at: int
    updated_at: int
    twilio_call_sid: str | None = None
    function_calls: dict[str, Any] | None = None
    cost: dict[str, Any] | None = None
    total_metrics: dict[str, Any] | None = None
    variables: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate call history entity."""
        if not self.room_name:
            raise ValueError("Room name cannot be empty")
        if not self.org_id:
            raise ValueError("Call must belong to an organization")

    def is_active(self) -> bool:
        """Check if call is currently active."""
        return self.status == "active"

    def is_completed(self) -> bool:
        """Check if call is completed."""
        return self.status == "completed"

    def calculate_duration(self) -> int | None:
        """Calculate call duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) // 1000  # Convert ms to seconds
        return None
