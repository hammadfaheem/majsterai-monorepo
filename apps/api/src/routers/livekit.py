"""LiveKit integration routes - room creation and token generation."""

import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db.database import get_db
from ..db.models import Agent, CallHistory
from ..services.livekit_service import LiveKitService

router = APIRouter()
settings = get_settings()


class CreateRoomRequest(BaseModel):
    """Request to create a LiveKit room for testing."""

    org_id: str
    mode: str = "voice"  # voice or text


class CreateRoomResponse(BaseModel):
    """Response with room details and token."""

    room_name: str
    url: str
    token: str
    metadata: dict[str, Any]


class TokenRequest(BaseModel):
    """Request for a participant token."""

    room_name: str
    participant_name: str
    org_id: str


@router.post("/create-room", response_model=CreateRoomResponse)
async def create_room(
    data: CreateRoomRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Create a LiveKit room with organization's agent configuration in metadata.
    
    This is the key endpoint that enables dynamic agent configuration:
    - Fetches agent config from database
    - Creates LiveKit room with metadata containing the prompt
    - The Python agent reads this metadata when it joins
    """
    # Fetch agent configuration
    result = await db.execute(
        select(Agent).where(
            Agent.org_id == data.org_id,
            Agent.deleted_at.is_(None),
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found for this organization")

    # Generate unique room name
    room_name = f"majster-{data.org_id[:8]}-{uuid.uuid4().hex[:8]}"

    # Build metadata (like SOFi does)
    metadata = {
        "org_id": data.org_id,
        "org_prompt": agent.prompt or "You are a helpful voice AI assistant.",
        "agent_name": agent.name,
        "extra_prompt": agent.extra_prompt,
        "llm_model": agent.llm_model,
        "stt_model": agent.stt_model,
        "tts_model": agent.tts_model,
        "settings": agent.settings or {},
        "mode": data.mode,
    }

    # Create LiveKit service
    lk_service = LiveKitService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )

    # Create room with metadata
    await lk_service.create_room(room_name, metadata)

    # Generate token for the user
    token = lk_service.generate_token(
        room_name=room_name,
        participant_name=f"user-{data.org_id[:8]}",
        is_agent=False,
    )

    # Record call history
    call_record = CallHistory(
        room_name=room_name,
        org_id=data.org_id,
        agent_id=agent.id,
        direction="web",
        status="pending",
        extra_data=metadata,
    )
    db.add(call_record)

    return {
        "room_name": room_name,
        "url": settings.livekit_url,
        "token": token,
        "metadata": metadata,
    }


@router.post("/token")
async def generate_token(data: TokenRequest) -> dict[str, str]:
    """Generate a participant token for an existing room."""
    lk_service = LiveKitService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )

    token = lk_service.generate_token(
        room_name=data.room_name,
        participant_name=data.participant_name,
        is_agent=False,
    )

    return {"token": token}
