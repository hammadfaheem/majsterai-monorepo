"""Scenario domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Scenario:
    """Predefined conversation flow."""

    id: str
    org_id: str
    name: str
    prompt: str | None
    response: str | None
    trigger_type: str | None
    trigger_value: str | None
    questions: list[Any] | None
    outcome: dict[str, Any] | None
    trade_service_id: int | None
    is_active: bool
    created_at: int
    updated_at: int
