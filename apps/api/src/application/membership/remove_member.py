"""Remove member use case."""

from ...infrastructure.database.repositories import MembershipRepository
from ...shared.exceptions import NotFoundError


class RemoveMemberUseCase:
    """Use case for removing a member from an organization."""

    def __init__(self, membership_repo: MembershipRepository):
        self.membership_repo = membership_repo

    async def execute(self, org_id: str, user_id: str) -> None:
        """Remove a member from an organization."""
        membership = await self.membership_repo.get_by_org_and_user(org_id, user_id)
        if not membership:
            raise NotFoundError(f"Membership not found for user {user_id} in org {org_id}")

        await self.membership_repo.delete(membership.id)
