"""Agent configuration routes - Clean Architecture."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.agent.get_agent import GetAgentPromptUseCase, GetAgentUseCase
from ...application.agent.update_agent import UpdateAgentUseCase
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    AgentRepository,
    SQLAlchemyAgentRepository,
)
from ...shared.exceptions import NotFoundError

router = APIRouter()


class AgentUpdate(BaseModel):
    """Request model for updating an agent."""

    name: str | None = None
    prompt: str | None = None
    extra_prompt: str | None = None
    is_custom_prompt: bool | None = None
    llm_model: str | None = None
    stt_model: str | None = None
    tts_model: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    variables: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    """Response model for agent."""

    id: int
    org_id: str
    name: str
    prompt: str
    extra_prompt: str | None
    is_custom_prompt: bool
    llm_model: str
    stt_model: str
    tts_model: dict[str, Any] | None
    settings: dict[str, Any] | None
    variables: dict[str, Any] | None = None
    status: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def get_agent_repo(db: AsyncSession = Depends(get_db)) -> AgentRepository:
    """Dependency to get agent repository."""
    return SQLAlchemyAgentRepository(db)


@router.get("/{org_id}", response_model=AgentResponse)
async def get_agent(
    org_id: str,
    agent_repo: AgentRepository = Depends(get_agent_repo),
):
    """Get agent configuration for an organization."""
    use_case = GetAgentUseCase(agent_repo)
    try:
        agent = await use_case.execute(org_id)
        return AgentResponse(
            id=agent.id,
            org_id=agent.org_id,
            name=agent.name,
            prompt=agent.prompt,
            extra_prompt=agent.extra_prompt,
            is_custom_prompt=agent.is_custom_prompt,
            llm_model=agent.llm_model,
            stt_model=agent.stt_model,
            tts_model=agent.tts_model,
            settings=agent.settings,
            variables=agent.variables,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{org_id}", response_model=AgentResponse)
async def update_agent(
    org_id: str,
    data: AgentUpdate,
    agent_repo: AgentRepository = Depends(get_agent_repo),
):
    """Update agent configuration for an organization."""
    use_case = UpdateAgentUseCase(agent_repo)
    try:
        agent = await use_case.execute(
            org_id=org_id,
            name=data.name,
            prompt=data.prompt,
            extra_prompt=data.extra_prompt,
            is_custom_prompt=data.is_custom_prompt,
            llm_model=data.llm_model,
            stt_model=data.stt_model,
            tts_model=data.tts_model,
            settings=data.settings,
            variables=data.variables,
        )
        return AgentResponse(
            id=agent.id,
            org_id=agent.org_id,
            name=agent.name,
            prompt=agent.prompt,
            extra_prompt=agent.extra_prompt,
            is_custom_prompt=agent.is_custom_prompt,
            llm_model=agent.llm_model,
            stt_model=agent.stt_model,
            tts_model=agent.tts_model,
            settings=agent.settings,
            variables=agent.variables,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{org_id}/prompt")
async def get_agent_prompt(
    org_id: str,
    agent_repo: AgentRepository = Depends(get_agent_repo),
) -> dict[str, Any]:
    """Get just the prompt for an agent (used by LiveKit agent)."""
    use_case = GetAgentPromptUseCase(agent_repo)
    try:
        return await use_case.execute(org_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
