"""Use case for creating a LiveKit room with agent configuration."""

import uuid
from typing import Any

from ...domain.call_history.entity import CallHistory as CallHistoryEntity
from ...infrastructure.database.repositories import (
    AgentRepository,
    CallHistoryRepository,
    OrganizationRepository,
)
from ...infrastructure.livekit.service import LiveKitService
from ...shared.exceptions import NotFoundError
from ...db.database import utc_now_ms


class CreateRoomUseCase:
    """Use case for creating a LiveKit room with agent metadata."""

    def __init__(
        self,
        agent_repo: AgentRepository,
        call_history_repo: CallHistoryRepository,
        livekit_service: LiveKitService,
        livekit_url: str,
        org_repo: OrganizationRepository | None = None,
    ):
        self.agent_repo = agent_repo
        self.call_history_repo = call_history_repo
        self.livekit_service = livekit_service
        self.livekit_url = livekit_url
        self.org_repo = org_repo

    async def execute(
        self,
        org_id: str,
        mode: str = "voice",
    ) -> dict[str, Any]:
        """
        Create a LiveKit room with organization's agent configuration in metadata.

        This is the key use case that enables dynamic agent configuration:
        - Fetches agent config from database
        - Creates LiveKit room with metadata containing the prompt
        - The Python agent reads this metadata when it joins
        """
        # Fetch agent configuration
        agent = await self.agent_repo.get_by_org_id(org_id)
        if agent is None or agent.is_deleted():
            raise NotFoundError("Agent not found for this organization")

        # Fetch org name for greeting/closing interpolation (metadata mode)
        org_name = ""
        if self.org_repo:
            org = await self.org_repo.get_by_id(org_id)
            if org:
                org_name = org.name or ""

        # Generate unique room name
        room_name = f"majster-{org_id[:8]}-{uuid.uuid4().hex[:8]}"

        # Build metadata (like SOFi does)
        metadata = {
            "org_id": org_id,
            "org_name": org_name,
            "org_prompt": agent.prompt or "You are a helpful voice AI assistant.",
            "agent_name": agent.name,
            "extra_prompt": agent.extra_prompt,
            "llm_model": agent.llm_model,
            "stt_model": agent.stt_model,
            "tts_model": agent.tts_model,
            "settings": agent.settings or {},
            "mode": mode,
        }

        # Create room with metadata
        await self.livekit_service.create_room(room_name, metadata)

        # Generate token for the user
        token = self.livekit_service.generate_token(
            room_name=room_name,
            participant_name=f"user-{org_id[:8]}",
            is_agent=False,
        )

        # Record call history
        now = utc_now_ms()
        call_history = CallHistoryEntity(
            id=0,  # Auto-increment, will be set by database
            room_name=room_name,
            org_id=org_id,
            agent_id=agent.id,
            direction="web",
            from_phone_number=None,
            to_phone_number=None,
            start_time=None,
            end_time=None,
            duration=None,
            status="pending",
            summary=None,
            transcript=None,
            analyzed_data=None,
            extra_data=metadata,
            created_at=now,
            updated_at=now,
        )

        await self.call_history_repo.create(call_history)

        return {
            "room_name": room_name,
            "url": self.livekit_url,
            "token": token,
            "metadata": metadata,
        }
