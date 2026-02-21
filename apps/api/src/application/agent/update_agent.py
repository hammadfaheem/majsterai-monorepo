"""Use case for updating an agent."""

from typing import Any

from ...domain.agent.entity import Agent as AgentEntity
from ...infrastructure.database.repositories import AgentRepository
from ...shared.exceptions import NotFoundError
from ...db.database import utc_now_ms


class UpdateAgentUseCase:
    """Use case for updating an agent configuration."""

    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    async def execute(
        self,
        org_id: str,
        name: str | None = None,
        prompt: str | None = None,
        extra_prompt: str | None = None,
        is_custom_prompt: bool | None = None,
        llm_model: str | None = None,
        stt_model: str | None = None,
        tts_model: dict[str, Any] | None = None,
        settings: dict[str, Any] | None = None,
        variables: dict[str, Any] | None = None,
    ) -> AgentEntity:
        """Update agent configuration for an organization."""
        agent = await self.agent_repo.get_by_org_id(org_id)
        if agent is None or agent.is_deleted():
            raise NotFoundError("Agent not found for this organization")

        # Update fields if provided
        if name is not None:
            agent.name = name
        if prompt is not None:
            agent.prompt = prompt
        if extra_prompt is not None:
            agent.extra_prompt = extra_prompt
        if is_custom_prompt is not None:
            agent.is_custom_prompt = is_custom_prompt
        if llm_model is not None:
            agent.llm_model = llm_model
        if stt_model is not None:
            agent.stt_model = stt_model
        if tts_model is not None:
            agent.tts_model = tts_model
        if settings is not None:
            agent.settings = settings
        if variables is not None:
            agent.variables = variables

        agent.updated_at = utc_now_ms()

        return await self.agent_repo.update(agent)
