"""LiveKit service for room management and token generation."""

import json
from datetime import timedelta
from typing import Any

from livekit.api import AccessToken, LiveKitAPI, VideoGrants
from livekit.protocol.room import CreateRoomRequest, DeleteRoomRequest, UpdateRoomMetadataRequest


class LiveKitService:
    """Service for interacting with LiveKit."""

    def __init__(self, url: str, api_key: str, api_secret: str):
        """Initialize LiveKit service.

        Args:
            url: LiveKit server URL (wss://...)
            api_key: LiveKit API key
            api_secret: LiveKit API secret
        """
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret
        self._api: LiveKitAPI | None = None

    @property
    def api(self) -> LiveKitAPI:
        """Get or create LiveKit API client."""
        if self._api is None:
            self._api = LiveKitAPI(
                url=self.url.replace("wss://", "https://").replace("ws://", "http://"),
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
        return self._api

    async def create_room(
        self,
        room_name: str,
        metadata: dict[str, Any] | None = None,
        empty_timeout: int = 300,  # 5 minutes
        max_participants: int = 10,
    ) -> None:
        """Create a LiveKit room with metadata.

        The metadata is crucial - it contains the organization's agent configuration
        that the Python agent will read when it joins the room.

        Args:
            room_name: Unique room identifier
            metadata: Room metadata (org_prompt, settings, etc.)
            empty_timeout: Seconds before empty room is closed
            max_participants: Maximum participants allowed
        """
        metadata_str = json.dumps(metadata) if metadata else ""

        # Use CreateRoomRequest object (new API)
        request = CreateRoomRequest(
            name=room_name,
            metadata=metadata_str,
            empty_timeout=empty_timeout,
            max_participants=max_participants,
        )
        
        await self.api.room.create_room(request)

    async def delete_room(self, room_name: str) -> None:
        """Delete a LiveKit room."""
        request = DeleteRoomRequest(room=room_name)
        await self.api.room.delete_room(request)

    async def list_rooms(self) -> list[Any]:
        """List all active rooms."""
        from livekit.protocol.room import ListRoomsRequest
        response = await self.api.room.list_rooms(ListRoomsRequest())
        return list(response.rooms)

    def generate_token(
        self,
        room_name: str,
        participant_name: str,
        is_agent: bool = False,
        ttl_seconds: int = 3600,  # 1 hour
    ) -> str:
        """Generate an access token for a participant.

        Args:
            room_name: Room to join
            participant_name: Participant identity
            is_agent: Whether this is an agent (gets different permissions)
            ttl_seconds: Token time-to-live in seconds

        Returns:
            JWT access token string
        """
        token = AccessToken(
            api_key=self.api_key,
            api_secret=self.api_secret,
        )

        token.identity = participant_name
        token.name = participant_name
        token.ttl = timedelta(seconds=ttl_seconds)

        # Set grants based on participant type
        if is_agent:
            # Agent gets full permissions
            token.with_grants(
                VideoGrants(
                    room=room_name,
                    room_join=True,
                    room_create=True,
                    room_admin=True,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                    can_update_own_metadata=True,
                )
            )
        else:
            # Regular user gets limited permissions
            token.with_grants(
                VideoGrants(
                    room=room_name,
                    room_join=True,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )

        return token.to_jwt()

    async def update_room_metadata(
        self,
        room_name: str,
        metadata: dict[str, Any],
    ) -> None:
        """Update room metadata (for dynamic prompt updates)."""
        metadata_str = json.dumps(metadata)
        request = UpdateRoomMetadataRequest(room=room_name, metadata=metadata_str)
        await self.api.room.update_room_metadata(request)
