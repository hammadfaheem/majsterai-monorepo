"""Use case for getting an organization."""

from ...domain.organization.entity import Organization as OrganizationEntity
from ...infrastructure.database.repositories import OrganizationRepository
from ...shared.exceptions import NotFoundError


class GetOrganizationUseCase:
    """Use case for getting an organization by ID."""

    def __init__(self, org_repo: OrganizationRepository):
        self.org_repo = org_repo

    async def execute(self, org_id: str) -> OrganizationEntity:
        """Get organization by ID."""
        organization = await self.org_repo.get_by_id(org_id)
        if organization is None or organization.is_deleted():
            raise NotFoundError("Organization not found")
        return organization
