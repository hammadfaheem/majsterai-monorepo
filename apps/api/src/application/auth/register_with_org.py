"""Register user with organization, membership, and default agent in one transaction."""

import bcrypt

from ...db.database import generate_uuid, utc_now_ms
from ...domain.user.entity import User as UserEntity
from ...domain.membership.entity import Membership as MembershipEntity
from ...infrastructure.database.repositories import (
    AgentRepository,
    MembershipRepository,
    OrganizationRepository,
    UserRepository,
)
from ..organization.create_organization import CreateOrganizationUseCase


class RegisterWithOrgUseCase:
    """Register a new user with a default organization, membership, and agent."""

    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        agent_repo: AgentRepository,
        membership_repo: MembershipRepository,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.agent_repo = agent_repo
        self.membership_repo = membership_repo

    async def execute(
        self,
        email: str,
        name: str,
        password: str,
        *,
        org_name: str | None = None,
        time_zone: str = "UTC",
        country: str | None = None,
        currency: str = "USD",
    ) -> UserEntity:
        """Create user, org, membership, and agent in one logical transaction."""
        # Check for existing user
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        now = utc_now_ms()

        # 1. Create user
        user = UserEntity(
            id=generate_uuid(),
            email=email,
            name=name,
            password_hash=password_hash,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        user = await self.user_repo.create(user)

        # 2. Create organization and default agent
        display_org_name = org_name or f"{name}'s Organization"
        create_org_use_case = CreateOrganizationUseCase(
            self.org_repo, self.agent_repo
        )
        organization, _ = await create_org_use_case.execute(
            name=display_org_name,
            time_zone=time_zone,
            country=country,
            currency=currency,
        )

        # 3. Create membership (user as owner)
        membership = MembershipEntity(
            id=generate_uuid(),
            org_id=organization.id,
            user_id=user.id,
            role="owner",
            created_at=now,
            updated_at=now,
        )
        await self.membership_repo.create(membership)

        return user
