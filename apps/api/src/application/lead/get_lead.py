"""Get lead use case."""

from ...domain.lead.entity import Lead
from ...infrastructure.database.repositories import LeadRepository
from ...shared.exceptions import NotFoundError


class GetLeadUseCase:
    """Use case for getting a lead."""

    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def execute(self, lead_id: str) -> Lead:
        """Get lead by ID."""
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundError(f"Lead with id {lead_id} not found")
        return lead
