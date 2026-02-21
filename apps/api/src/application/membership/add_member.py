"""Add member use case."""

from ...db.database import generate_uuid, utc_now_ms
from ...domain.membership.entity import Membership
from ...infrastructure.database.repositories import MembershipRepository, UserRepository
from ...shared.exceptions import NotFoundError


class AddMemberUseCase:
    """Use case for adding a member to an organization."""

    def __init__(self, membership_repo: MembershipRepository, user_repo: UserRepository):
        self.membership_repo = membership_repo
        self.user_repo = user_repo

    async def execute(
        self,
        org_id: str,
        user_id: str,
        role: str = "member",
        *,
        invited_email: str | None = None,
        scheduling_priority: int | None = None,
        responsibility: str | None = None,
        personalisation_notes: str | None = None,
        is_point_of_escalation: bool = False,
    ) -> Membership:
        """Add a member to an organization."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        existing = await self.membership_repo.get_by_org_and_user(org_id, user_id)
        if existing:
            return existing

        now = utc_now_ms()
        membership = Membership(
            id=generate_uuid(),
            org_id=org_id,
            user_id=user_id,
            role=role,
            created_at=now,
            updated_at=now,
            invited_email=invited_email,
            scheduling_priority=scheduling_priority,
            responsibility=responsibility,
            personalisation_notes=personalisation_notes,
            is_point_of_escalation=is_point_of_escalation,
        )

        return await self.membership_repo.create(membership)
