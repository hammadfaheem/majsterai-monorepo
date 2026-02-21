"""Use case for getting an agent."""

from typing import Any

from ...domain.agent.entity import Agent as AgentEntity
from ...infrastructure.database.repositories import AgentRepository
from ...shared.exceptions import NotFoundError


class GetAgentUseCase:
    """Use case for getting an agent by organization ID."""

    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    async def execute(self, org_id: str) -> AgentEntity:
        """Get agent by organization ID."""
        agent = await self.agent_repo.get_by_org_id(org_id)
        if agent is None or agent.is_deleted():
            raise NotFoundError("Agent not found for this organization")
        return agent


class GetAgentPromptUseCase:
    """Use case for getting agent prompt configuration."""

    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    async def execute(self, org_id: str) -> dict[str, Any]:
        """Get agent prompt configuration for LiveKit agent."""
        agent = await self.agent_repo.get_by_org_id(org_id)
        if agent is None or agent.is_deleted():
            raise NotFoundError("Agent not found")

        return {
            "org_id": org_id,
            "agent_name": agent.name,
            "prompt": agent.prompt,
            "extra_prompt": agent.extra_prompt,
            "llm_model": agent.llm_model,
            "stt_model": agent.stt_model,
            "tts_model": agent.tts_model,
            "settings": agent.settings,
        }
