"""Transcript domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Transcript:
    """Transcript domain entity."""

    id: str
    room_name: str
    org_id: str
    transcript: str
    segments: dict[str, Any] | None
    sentiment: str | None  # positive, neutral, negative
    keywords: list[str] | None
    summary: str | None
    created_at: int
    updated_at: int
