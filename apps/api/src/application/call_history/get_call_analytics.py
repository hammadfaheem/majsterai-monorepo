"""Get call analytics use case."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import CallHistory


class GetCallAnalyticsUseCase:
    """Use case for getting call analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, org_id: str) -> dict[str, Any]:
        """Get call analytics for an organization."""
        # Total calls
        total_calls_result = await self.session.execute(
            select(func.count(CallHistory.id)).where(CallHistory.org_id == org_id)
        )
        total_calls = total_calls_result.scalar() or 0

        # Completed calls
        completed_calls_result = await self.session.execute(
            select(func.count(CallHistory.id)).where(
                CallHistory.org_id == org_id, CallHistory.status == "completed"
            )
        )
        completed_calls = completed_calls_result.scalar() or 0

        # Average duration
        avg_duration_result = await self.session.execute(
            select(func.avg(CallHistory.duration)).where(
                CallHistory.org_id == org_id,
                CallHistory.status == "completed",
                CallHistory.duration.isnot(None),
            )
        )
        avg_duration = avg_duration_result.scalar() or 0

        # Total duration
        total_duration_result = await self.session.execute(
            select(func.sum(CallHistory.duration)).where(
                CallHistory.org_id == org_id,
                CallHistory.status == "completed",
                CallHistory.duration.isnot(None),
            )
        )
        total_duration = total_duration_result.scalar() or 0

        return {
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "average_duration_seconds": float(avg_duration) if avg_duration else 0,
            "total_duration_seconds": int(total_duration) if total_duration else 0,
        }
