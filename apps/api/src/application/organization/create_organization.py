"""Use case for creating a new organization."""

import re

from ...domain.agent.entity import Agent as AgentEntity
from ...domain.organization.entity import Organization as OrganizationEntity
from ...infrastructure.database.repositories import AgentRepository, OrganizationRepository
from ...db.database import utc_now_ms


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class CreateOrganizationUseCase:
    """Use case for creating a new organization with default agent."""

    def __init__(
        self,
        org_repo: OrganizationRepository,
        agent_repo: AgentRepository,
    ):
        self.org_repo = org_repo
        self.agent_repo = agent_repo

    async def execute(
        self,
        name: str,
        time_zone: str = "UTC",
        country: str | None = None,
        currency: str = "USD",
    ) -> tuple[OrganizationEntity, AgentEntity]:
        """Create a new organization with a default agent."""
        # Generate unique slug
        base_slug = generate_slug(name)
        slug = base_slug

        # Check if slug exists and make unique if needed
        counter = 1
        while True:
            existing = await self.org_repo.get_by_slug(slug)
            if existing is None:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        now = utc_now_ms()
        from ...db.database import generate_uuid

        # Create organization entity
        organization = OrganizationEntity(
            id=generate_uuid(),  # Generate UUID
            name=name.strip(),
            slug=slug,
            time_zone=time_zone,
            country=country,
            currency=currency,
            settings={},
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        # Save organization
        organization = await self.org_repo.create(organization)

        # Create default agent for the organization
        agent = AgentEntity(
            id=0,  # Auto-increment, will be set by database
            org_id=organization.id,
            name="Majster",
            prompt="",  # Empty prompt - will be generated dynamically
            extra_prompt=None,
            is_custom_prompt=False,
            llm_model="openai/gpt-4o-mini",
            stt_model="deepgram/nova-3",
            tts_model={},
            settings={},
            status="ready",
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        agent = await self.agent_repo.create(agent)

        return organization, agent
