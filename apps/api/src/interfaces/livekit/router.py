"""LiveKit integration routes - Clean Architecture."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.livekit.create_room import CreateRoomUseCase
from ...config import get_settings
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    AgentRepository,
    CallHistoryRepository,
    OrganizationRepository,
    SQLAlchemyAgentRepository,
    SQLAlchemyCallHistoryRepository,
    SQLAlchemyOrganizationRepository,
)
from ...infrastructure.livekit.service import LiveKitService
from ...shared.exceptions import NotFoundError

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


def get_agent_repo(db: AsyncSession = Depends(get_db)) -> AgentRepository:
    """Dependency to get agent repository."""
    return SQLAlchemyAgentRepository(db)


def get_call_history_repo(db: AsyncSession = Depends(get_db)) -> CallHistoryRepository:
    """Dependency to get call history repository."""
    return SQLAlchemyCallHistoryRepository(db)


def get_org_repo(db: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    """Dependency to get organization repository."""
    return SQLAlchemyOrganizationRepository(db)


def get_livekit_service() -> LiveKitService:
    """Dependency to get LiveKit service."""
    return LiveKitService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )


@router.post("/create-room", response_model=CreateRoomResponse)
async def create_room(
    data: CreateRoomRequest,
    agent_repo: AgentRepository = Depends(get_agent_repo),
    call_history_repo: CallHistoryRepository = Depends(get_call_history_repo),
    org_repo: OrganizationRepository = Depends(get_org_repo),
    livekit_service: LiveKitService = Depends(get_livekit_service),
) -> dict[str, Any]:
    """
    Create a LiveKit room with organization's agent configuration in metadata.

    This is the key endpoint that enables dynamic agent configuration:
    - Fetches agent config from database
    - Creates LiveKit room with metadata containing the prompt
    - The Python agent reads this metadata when it joins
    """
    use_case = CreateRoomUseCase(
        agent_repo=agent_repo,
        call_history_repo=call_history_repo,
        livekit_service=livekit_service,
        livekit_url=settings.livekit_url,
        org_repo=org_repo,
    )

    try:
        result = await use_case.execute(org_id=data.org_id, mode=data.mode)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/token")
async def generate_token(data: TokenRequest) -> dict[str, str]:
    """Generate a participant token for an existing room."""
    livekit_service = LiveKitService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )

    token = livekit_service.generate_token(
        room_name=data.room_name,
        participant_name=data.participant_name,
        is_agent=False,
    )

    return {"token": token}
