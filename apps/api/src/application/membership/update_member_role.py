"""Update member role use case."""

from ...db.database import utc_now_ms
from ...domain.membership.entity import Membership
from ...infrastructure.database.repositories import MembershipRepository
from ...shared.exceptions import NotFoundError


class UpdateMemberRoleUseCase:
    """Use case for updating a member's role."""

    def __init__(self, membership_repo: MembershipRepository):
        self.membership_repo = membership_repo

    async def execute(
        self,
        org_id: str,
        user_id: str,
        role: str | None = None,
        *,
        is_disabled: bool | None = None,
        is_point_of_escalation: bool | None = None,
        scheduling_priority: int | None = None,
        responsibility: str | None = None,
        personalisation_notes: str | None = None,
    ) -> Membership:
        """Update a member's role and profile."""
        membership = await self.membership_repo.get_by_org_and_user(org_id, user_id)
        if not membership:
            raise NotFoundError(f"Membership not found for user {user_id} in org {org_id}")

        if role is not None:
            membership.role = role
        if is_disabled is not None:
            membership.is_disabled = is_disabled
        if is_point_of_escalation is not None:
            membership.is_point_of_escalation = is_point_of_escalation
        if scheduling_priority is not None:
            membership.scheduling_priority = scheduling_priority
        if responsibility is not None:
            membership.responsibility = responsibility
        if personalisation_notes is not None:
            membership.personalisation_notes = personalisation_notes

        membership.updated_at = utc_now_ms()

        return await self.membership_repo.update(membership)
