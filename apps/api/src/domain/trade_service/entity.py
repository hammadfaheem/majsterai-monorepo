"""Trade service domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class TradeService:
    """Service offered."""

    id: int
    org_id: str
    name: str
    description: str | None
    duration: int | None
    duration_unit: str | None
    followup_questions: list[Any] | None
    pricing_mode: str | None
    fixed_price: int | None
    hourly_rate: int | None
    min_price: int | None
    max_price: int | None
    call_out_fee: int | None
    plus_gst: bool
    plus_materials: bool
    is_disclose_price: bool
    custom_price_response: str | None
    is_active: bool
    trade_category_id: int | None
    created_at: int
    updated_at: int
