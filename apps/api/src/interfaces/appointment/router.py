"""Appointment routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms, generate_uuid
from ...domain.appointment.entity import Appointment as AppointmentEntity
from ...infrastructure.database.repositories import (
    AppointmentRepository,
    SQLAlchemyAppointmentRepository,
)

router = APIRouter()


def get_appointment_repo(db: AsyncSession = Depends(get_db)) -> AppointmentRepository:
    return SQLAlchemyAppointmentRepository(db)


class AppointmentCreate(BaseModel):
    org_id: str
    start: int
    end: int
    title: str | None = None
    description: str | None = None
    status: str = "PENDING"
    lead_id: str | None = None
    inquiry_id: str | None = None
    trade_service_id: int | None = None
    lead_address_id: int | None = None
    selected_calendar_id: int | None = None
    attendees: list | None = None
    is_rescheduled: bool = False
    is_created_by_sophiie: bool = False
    notes: str | None = None
    customer_notes: str | None = None
    summary: str | None = None
    photos: list | None = None
    reference_id: str | None = None


class AppointmentUpdate(BaseModel):
    start: int | None = None
    end: int | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None
    lead_id: str | None = None
    inquiry_id: str | None = None
    notes: str | None = None
    customer_notes: str | None = None
    summary: str | None = None
    reference_id: str | None = None
    is_rescheduled: bool | None = None


class AppointmentResponse(BaseModel):
    id: str
    org_id: str
    serial_id: int | None
    start: int
    end: int
    title: str | None
    description: str | None
    status: str
    lead_id: str | None
    inquiry_id: str | None
    trade_service_id: int | None
    lead_address_id: int | None
    selected_calendar_id: int | None
    attendees: list | None
    is_rescheduled: bool
    is_created_by_sophiie: bool
    notes: str | None
    customer_notes: str | None
    customer_cancellation_reason: str | None
    summary: str | None
    photos: list | None
    reference_id: str | None
    created_at: int
    updated_at: int
    deleted_at: int | None

    class Config:
        from_attributes = True


def _to_response(a: AppointmentEntity) -> AppointmentResponse:
    return AppointmentResponse(
        id=a.id,
        org_id=a.org_id,
        serial_id=a.serial_id,
        start=a.start,
        end=a.end,
        title=a.title,
        description=a.description,
        status=a.status,
        lead_id=a.lead_id,
        inquiry_id=a.inquiry_id,
        trade_service_id=a.trade_service_id,
        lead_address_id=a.lead_address_id,
        selected_calendar_id=a.selected_calendar_id,
        attendees=a.attendees,
        is_rescheduled=a.is_rescheduled,
        is_created_by_sophiie=a.is_created_by_sophiie,
        notes=a.notes,
        customer_notes=a.customer_notes,
        customer_cancellation_reason=a.customer_cancellation_reason,
        summary=a.summary,
        photos=a.photos,
        reference_id=a.reference_id,
        created_at=a.created_at,
        updated_at=a.updated_at,
        deleted_at=a.deleted_at,
    )


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    org_id: str = Query(..., description="Organization ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    lead_id: str | None = Query(None),
    start_from: int | None = Query(None, description="Filter from start (Unix ms)"),
    end_before: int | None = Query(None, description="Filter before end (Unix ms)"),
    statuses: str | None = Query(None, description="Comma-separated status filter"),
    repo: AppointmentRepository = Depends(get_appointment_repo),
):
    status_list = [s.strip() for s in statuses.split(",")] if statuses else None
    items = await repo.list_by_org_id(
        org_id,
        limit=limit,
        offset=offset,
        lead_id=lead_id,
        start_from=start_from,
        end_before=end_before,
        statuses=status_list,
    )
    return [_to_response(a) for a in items]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: str, repo: AppointmentRepository = Depends(get_appointment_repo)):
    a = await repo.get_by_id(appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _to_response(a)


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(data: AppointmentCreate, repo: AppointmentRepository = Depends(get_appointment_repo)):
    now = utc_now_ms()
    entity = AppointmentEntity(
        id=generate_uuid(),
        org_id=data.org_id,
        serial_id=None,
        start=data.start,
        end=data.end,
        title=data.title,
        description=data.description,
        status=data.status,
        lead_id=data.lead_id,
        inquiry_id=data.inquiry_id,
        trade_service_id=data.trade_service_id,
        lead_address_id=data.lead_address_id,
        selected_calendar_id=data.selected_calendar_id,
        attendees=data.attendees,
        is_rescheduled=data.is_rescheduled,
        is_created_by_sophiie=data.is_created_by_sophiie,
        notes=data.notes,
        customer_notes=data.customer_notes,
        customer_cancellation_reason=None,
        summary=data.summary,
        photos=data.photos,
        reference_id=data.reference_id,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    data: AppointmentUpdate,
    repo: AppointmentRepository = Depends(get_appointment_repo),
):
    existing = await repo.get_by_id(appointment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Appointment not found")
    now = utc_now_ms()
    if data.start is not None:
        existing.start = data.start
    if data.end is not None:
        existing.end = data.end
    if data.title is not None:
        existing.title = data.title
    if data.description is not None:
        existing.description = data.description
    if data.status is not None:
        existing.status = data.status
    if data.lead_id is not None:
        existing.lead_id = data.lead_id
    if data.inquiry_id is not None:
        existing.inquiry_id = data.inquiry_id
    if data.notes is not None:
        existing.notes = data.notes
    if data.customer_notes is not None:
        existing.customer_notes = data.customer_notes
    if data.summary is not None:
        existing.summary = data.summary
    if data.reference_id is not None:
        existing.reference_id = data.reference_id
    if data.is_rescheduled is not None:
        existing.is_rescheduled = data.is_rescheduled
    existing.updated_at = now
    updated = await repo.update(existing)
    return _to_response(updated)


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: str,
    hard: bool = Query(False, description="Hard delete (default: soft delete)"),
    repo: AppointmentRepository = Depends(get_appointment_repo),
):
    existing = await repo.get_by_id(appointment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if hard:
        await repo.delete(appointment_id)
    else:
        await repo.soft_delete(appointment_id, utc_now_ms())
    return {"message": "Deleted"}
