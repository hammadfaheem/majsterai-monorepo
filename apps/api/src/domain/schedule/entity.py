"""Schedule domain entity."""

from dataclasses import dataclass


@dataclass
class Schedule:
    """Working schedule."""

    id: int
    org_id: str | None
    name: str
    time_zone: str
    department_id: int | None
