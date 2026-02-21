"""List leads use case."""

from ...domain.lead.entity import Lead
from ...infrastructure.database.repositories import LeadRepository


class ListLeadsUseCase:
    """Use case for listing leads."""

    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def execute(
        self, org_id: str, status: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Lead]:
        """List leads for an organization."""
        return await self.lead_repo.list_by_org_id(org_id, status, limit, offset)
