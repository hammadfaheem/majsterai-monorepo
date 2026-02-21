"""Get call details use case."""

from ...domain.call_history.entity import CallHistory
from ...domain.transcript.entity import Transcript
from ...infrastructure.database.repositories import CallHistoryRepository, TranscriptRepository
from ...shared.exceptions import NotFoundError


class GetCallDetailsUseCase:
    """Use case for getting call details with transcript."""

    def __init__(
        self,
        call_history_repo: CallHistoryRepository,
        transcript_repo: TranscriptRepository,
    ):
        self.call_history_repo = call_history_repo
        self.transcript_repo = transcript_repo

    async def execute(self, room_name: str) -> tuple[CallHistory, Transcript | None]:
        """Get call details with transcript."""
        call_history = await self.call_history_repo.get_by_room_name(room_name)
        if not call_history:
            raise NotFoundError(f"Call history with room_name {room_name} not found")

        transcript = await self.transcript_repo.get_by_room_name(room_name)

        return call_history, transcript
