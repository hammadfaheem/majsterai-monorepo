"""Lead management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.lead.add_lead_activity import AddLeadActivityUseCase
from ...application.lead.add_lead_note import AddLeadNoteUseCase
from ...application.lead.create_lead import CreateLeadUseCase
from ...application.lead.get_lead import GetLeadUseCase
from ...application.lead.list_leads import ListLeadsUseCase
from ...application.lead.update_lead import UpdateLeadUseCase
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    ActivityRepository,
    LeadRepository,
    NoteRepository,
    SQLAlchemyActivityRepository,
    SQLAlchemyLeadRepository,
    SQLAlchemyNoteRepository,
)
from ...shared.exceptions import NotFoundError

router = APIRouter()


def get_lead_repo(db: AsyncSession = Depends(get_db)) -> LeadRepository:
    """Dependency to get lead repository."""
    return SQLAlchemyLeadRepository(db)


def get_note_repo(db: AsyncSession = Depends(get_db)) -> NoteRepository:
    """Dependency to get note repository."""
    return SQLAlchemyNoteRepository(db)


def get_activity_repo(db: AsyncSession = Depends(get_db)) -> ActivityRepository:
    """Dependency to get activity repository."""
    return SQLAlchemyActivityRepository(db)


class LeadCreate(BaseModel):
    """Request model for creating a lead."""

    name: str
    email: str | None = None
    phone: str | None = None
    source: str | None = None


class LeadUpdate(BaseModel):
    """Request model for updating a lead."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None
    source: str | None = None


class LeadResponse(BaseModel):
    """Response model for lead."""

    id: str
    org_id: str
    email: str | None
    phone: str | None
    name: str
    status: str
    source: str | None
    last_inquiry_date: int | None
    last_contact_date: int | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    """Request model for creating a note."""

    content: str


class NoteResponse(BaseModel):
    """Response model for note."""

    id: str
    lead_id: str
    content: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    """Request model for creating an activity."""

    type: str
    description: str


class ActivityResponse(BaseModel):
    """Response model for activity."""

    id: str
    lead_id: str
    type: str
    description: str
    created_at: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[LeadResponse])
async def list_leads(
    org_id: str = Query(..., description="Organization ID"),
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """List leads for an organization."""
    use_case = ListLeadsUseCase(lead_repo)
    leads = await use_case.execute(org_id, status, limit, offset)
    return [
        LeadResponse(
            id=lead.id,
            org_id=lead.org_id,
            email=lead.email,
            phone=lead.phone,
            name=lead.name,
            status=lead.status,
            source=lead.source,
            last_inquiry_date=lead.last_inquiry_date,
            last_contact_date=lead.last_contact_date,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
        for lead in leads
    ]


@router.post("/", response_model=LeadResponse)
async def create_lead(
    org_id: str = Query(..., description="Organization ID"),
    data: LeadCreate = ...,
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """Create a new lead."""
    use_case = CreateLeadUseCase(lead_repo)
    lead = await use_case.execute(org_id, data.name, data.email, data.phone, data.source)
    return LeadResponse(
        id=lead.id,
        org_id=lead.org_id,
        email=lead.email,
        phone=lead.phone,
        name=lead.name,
        status=lead.status,
        source=lead.source,
        last_inquiry_date=lead.last_inquiry_date,
        last_contact_date=lead.last_contact_date,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """Get lead details."""
    use_case = GetLeadUseCase(lead_repo)
    try:
        lead = await use_case.execute(lead_id)
        return LeadResponse(
            id=lead.id,
            org_id=lead.org_id,
            email=lead.email,
            phone=lead.phone,
            name=lead.name,
            status=lead.status,
            source=lead.source,
            last_inquiry_date=lead.last_inquiry_date,
            last_contact_date=lead.last_contact_date,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """Update a lead."""
    use_case = UpdateLeadUseCase(lead_repo)
    try:
        lead = await use_case.execute(
            lead_id,
            data.name,
            data.email,
            data.phone,
            data.status,
            data.source,
        )
        return LeadResponse(
            id=lead.id,
            org_id=lead.org_id,
            email=lead.email,
            phone=lead.phone,
            name=lead.name,
            status=lead.status,
            source=lead.source,
            last_inquiry_date=lead.last_inquiry_date,
            last_contact_date=lead.last_contact_date,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{lead_id}/notes", response_model=list[NoteResponse])
async def list_lead_notes(
    lead_id: str,
    note_repo: NoteRepository = Depends(get_note_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """List notes for a lead."""
    use_case = GetLeadUseCase(lead_repo)
    try:
        await use_case.execute(lead_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    notes = await note_repo.get_by_lead_id(lead_id)
    return [
        NoteResponse(
            id=n.id,
            lead_id=n.lead_id,
            content=n.content,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in notes
    ]


@router.post("/{lead_id}/notes", response_model=NoteResponse)
async def add_note(
    lead_id: str,
    data: NoteCreate,
    note_repo: NoteRepository = Depends(get_note_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """Add a note to a lead."""
    use_case = AddLeadNoteUseCase(note_repo, lead_repo)
    try:
        note = await use_case.execute(lead_id, data.content)
        return NoteResponse(
            id=note.id,
            lead_id=note.lead_id,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{lead_id}/activities", response_model=list[ActivityResponse])
async def list_lead_activities(
    lead_id: str,
    activity_repo: ActivityRepository = Depends(get_activity_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """List activities for a lead."""
    use_case = GetLeadUseCase(lead_repo)
    try:
        await use_case.execute(lead_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    activities = await activity_repo.list_by_lead_id(lead_id)
    return [
        ActivityResponse(
            id=a.id,
            lead_id=a.lead_id,
            type=a.type,
            description=a.description,
            created_at=a.created_at,
        )
        for a in activities
    ]


@router.post("/{lead_id}/activities", response_model=ActivityResponse)
async def add_activity(
    lead_id: str,
    data: ActivityCreate,
    activity_repo: ActivityRepository = Depends(get_activity_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    """Add an activity to a lead."""
    use_case = AddLeadActivityUseCase(activity_repo, lead_repo)
    try:
        activity = await use_case.execute(lead_id, data.type, data.description)
        return ActivityResponse(
            id=activity.id,
            lead_id=activity.lead_id,
            type=activity.type,
            description=activity.description,
            created_at=activity.created_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
