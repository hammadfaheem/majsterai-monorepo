"""Add lead note use case."""

from ...db.database import generate_uuid, utc_now_ms
from ...domain.lead.entity import Note
from ...infrastructure.database.repositories import LeadRepository, NoteRepository
from ...shared.exceptions import NotFoundError


class AddLeadNoteUseCase:
    """Use case for adding a note to a lead."""

    def __init__(self, note_repo: NoteRepository, lead_repo: LeadRepository):
        self.note_repo = note_repo
        self.lead_repo = lead_repo

    async def execute(self, lead_id: str, content: str) -> Note:
        """Add a note to a lead."""
        # Verify lead exists
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            raise NotFoundError(f"Lead with id {lead_id} not found")

        note = Note(
            id=generate_uuid(),
            lead_id=lead_id,
            content=content,
            created_at=utc_now_ms(),
            updated_at=utc_now_ms(),
        )

        return await self.note_repo.create(note)
