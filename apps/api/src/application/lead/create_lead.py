"""Create lead use case."""

from ...db.database import generate_uuid, utc_now_ms
from ...domain.lead.entity import Lead
from ...infrastructure.database.repositories import LeadRepository


class CreateLeadUseCase:
    """Use case for creating a new lead."""

    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def execute(
        self,
        org_id: str,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        source: str | None = None,
    ) -> Lead:
        """Create a new lead."""
        lead = Lead(
            id=generate_uuid(),
            org_id=org_id,
            email=email,
            phone=phone,
            name=name,
            status="new",
            source=source,
            last_inquiry_date=None,
            last_contact_date=None,
            metadata=None,
            created_at=utc_now_ms(),
            updated_at=utc_now_ms(),
            deleted_at=None,
        )

        return await self.lead_repo.create(lead)
