"""Update call status use case."""

from ...db.database import utc_now_ms
from ...domain.call_history.entity import CallHistory
from ...infrastructure.database.repositories import CallHistoryRepository
from ...shared.exceptions import NotFoundError


class UpdateCallStatusUseCase:
    """Use case for updating call status."""

    def __init__(self, call_history_repo: CallHistoryRepository):
        self.call_history_repo = call_history_repo

    async def execute(self, room_name: str, status: str) -> CallHistory:
        """Update call status."""
        call_history = await self.call_history_repo.get_by_room_name(room_name)
        if not call_history:
            raise NotFoundError(f"Call history with room_name {room_name} not found")

        call_history.status = status
        call_history.updated_at = utc_now_ms()

        return await self.call_history_repo.update(call_history)
