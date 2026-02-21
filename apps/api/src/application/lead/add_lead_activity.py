"""Add lead activity use case."""

from ...db.database import generate_uuid, utc_now_ms
from ...domain.lead.entity import Activity
from ...infrastructure.database.repositories import ActivityRepository, LeadRepository
from ...shared.exceptions import NotFoundError


class AddLeadActivityUseCase:
    """Use case for adding an activity to a lead."""

    def __init__(self, activity_repo: ActivityRepository, lead_repo: LeadRepository):
        self.activity_repo = activity_repo
        self.lead_repo = lead_repo

    async def execute(self, lead_id: str, activity_type: str, description: str) -> Activity:
        """Add an activity to a lead."""
        # Verify lead exists
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundError(f"Lead with id {lead_id} not found")

        activity = Activity(
            id=generate_uuid(),
            lead_id=lead_id,
            type=activity_type,
            description=description,
            metadata=None,
            created_at=utc_now_ms(),
        )

        return await self.activity_repo.create(activity)
