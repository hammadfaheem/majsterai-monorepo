"""Invoice domain entity."""

from dataclasses import dataclass


@dataclass
class Invoice:
    """Invoice."""

    id: str
    org_id: str
    lead_id: str | None
    index: int | None
    status: str
    date: int | None
    due_date: int | None
    tax_type: str | None
    reference: str | None
    notes: str | None
    accept_credit_card: bool
    reminder_sent: bool
    approved_at: int | None
    sent_at: int | None
    external_id: str | None
    last_synced_at: int | None
    is_sync_failed: bool
    created_at: int
    updated_at: int
