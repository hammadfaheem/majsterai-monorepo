"""Agent configuration routes."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db.models import Agent

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
    status: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/{org_id}", response_model=AgentResponse)
async def get_agent(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    """Get agent configuration for an organization."""
    result = await db.execute(
        select(Agent).where(
            Agent.org_id == org_id,
            Agent.deleted_at.is_(None),
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found for this organization")
    return agent


@router.put("/{org_id}", response_model=AgentResponse)
async def update_agent(
    org_id: str,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    """Update agent configuration for an organization."""
    result = await db.execute(
        select(Agent).where(
            Agent.org_id == org_id,
            Agent.deleted_at.is_(None),
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found for this organization")

    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    return agent


@router.get("/{org_id}/prompt")
async def get_agent_prompt(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get just the prompt for an agent (used by LiveKit agent)."""
    result = await db.execute(
        select(Agent).where(
            Agent.org_id == org_id,
            Agent.deleted_at.is_(None),
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

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
