"""Availability domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Availability:
    """Time block when a schedule (or user) is available."""

    id: int
    schedule_id: int
    days: list[Any] | None  # e.g. ["mon", "tue"]
    start_time: int | None  # time of day
    end_time: int | None
    user_id: str | None
    created_at: int
    updated_at: int
