"""Appointment domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Appointment:
    """Scheduled appointment."""

    id: str
    org_id: str
    serial_id: int | None
    start: int
    end: int
    title: str | None
    description: str | None
    status: str
    lead_id: str | None
    inquiry_id: str | None
    trade_service_id: int | None
    lead_address_id: int | None
    selected_calendar_id: int | None
    attendees: list[Any] | None
    is_rescheduled: bool
    is_created_by_sophiie: bool
    notes: str | None
    customer_notes: str | None
    customer_cancellation_reason: str | None
    summary: str | None
    photos: list[Any] | None
    reference_id: str | None
    created_at: int
    updated_at: int
    deleted_at: int | None
