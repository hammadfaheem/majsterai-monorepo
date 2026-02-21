"""Lead address domain entity."""

from dataclasses import dataclass


@dataclass
class LeadAddress:
    """Address linked to a lead (for appointments, service location)."""

    id: int
    address_id: str
    lead_id: str
    created_at: int
    updated_at: int
