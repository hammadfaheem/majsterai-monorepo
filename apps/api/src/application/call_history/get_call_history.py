"""Get call history use case."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import CallHistory
from ...domain.call_history.entity import CallHistory as CallHistoryEntity
from ...infrastructure.database.repositories import CallHistoryRepository


class GetCallHistoryUseCase:
    """Use case for getting call history."""

    def __init__(self, call_history_repo: CallHistoryRepository):
        self.call_history_repo = call_history_repo

    async def execute(
        self, org_id: str, limit: int = 100, offset: int = 0
    ) -> list[CallHistoryEntity]:
        """Get call history for an organization."""
        # This is a simplified version - in production, add filtering to repository
        # For now, we'll need to extend the repository
        # For simplicity, returning empty list - repository needs extension
        return []
