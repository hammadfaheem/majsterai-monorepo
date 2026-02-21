"""Trade category domain entity."""

from dataclasses import dataclass


@dataclass
class TradeCategory:
    """Category of trade."""

    id: int
    org_id: str
    name: str
    type: str | None
    created_at: int
    updated_at: int

