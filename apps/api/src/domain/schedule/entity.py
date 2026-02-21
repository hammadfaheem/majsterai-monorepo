"""Schedule domain entity."""

from dataclasses import dataclass


@dataclass
class Schedule:
    """Working schedule."""

    id: int
    name: str
    time_zone: str
    department_id: int | None
