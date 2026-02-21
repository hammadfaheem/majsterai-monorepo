"""Use case for listing organizations."""

from ...domain.organization.entity import Organization as OrganizationEntity
from ...infrastructure.database.repositories import OrganizationRepository


class ListOrganizationsUseCase:
    """Use case for listing organizations (all for SUPERADMIN, else only member orgs)."""

    def __init__(self, org_repo: OrganizationRepository):
        self.org_repo = org_repo

    async def execute(
        self,
        user_id: str | None = None,
        user_role: str | None = None,
    ) -> list[OrganizationEntity]:
        """List organizations. If user_role is SUPERADMIN return all; else return only orgs where user is member."""
        if user_role == "SUPERADMIN":
            return await self.org_repo.list_all()
        if user_id:
            return await self.org_repo.list_by_member_user_id(user_id)
        return []
