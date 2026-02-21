"""List members use case."""

from ...domain.membership.entity import Membership
from ...infrastructure.database.repositories import MembershipRepository


class ListMembersUseCase:
    """Use case for listing organization members."""

    def __init__(self, membership_repo: MembershipRepository):
        self.membership_repo = membership_repo

    async def execute(self, org_id: str) -> list[Membership]:
        """List all members of an organization."""
        return await self.membership_repo.list_by_org_id(org_id)
