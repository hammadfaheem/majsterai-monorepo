"""Update lead use case."""

from ...db.database import utc_now_ms
from ...domain.lead.entity import Lead
from ...infrastructure.database.repositories import LeadRepository
from ...shared.exceptions import NotFoundError


class UpdateLeadUseCase:
    """Use case for updating a lead."""

    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def execute(
        self,
        lead_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        status: str | None = None,
        source: str | None = None,
    ) -> Lead:
        """Update a lead."""
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundError(f"Lead with id {lead_id} not found")

        if name is not None:
            lead.name = name
        if email is not None:
            lead.email = email
        if phone is not None:
            lead.phone = phone
        if status is not None:
            lead.status = status
        if source is not None:
            lead.source = source

        lead.updated_at = utc_now_ms()

        return await self.lead_repo.update(lead)
