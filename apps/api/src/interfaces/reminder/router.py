"""Reminder routes – CRUD for reminders (lead/appointment follow-ups)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms, generate_uuid
from ...domain.reminder.entity import Reminder as ReminderEntity
from ...infrastructure.database.repositories import (
    ReminderRepository,
    SQLAlchemyReminderRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> ReminderRepository:
    return SQLAlchemyReminderRepository(db)


class ReminderCreate(BaseModel):
    lead_id: str | None = None
    appointment_id: str | None = None
    user_id: str | None = None
    datetime: int | None = None
    notes: str | None = None
    notes_type: str | None = None
    priority: int | None = None


class ReminderUpdate(BaseModel):
    lead_id: str | None = None
    appointment_id: str | None = None
    user_id: str | None = None
    datetime: int | None = None
    notes: str | None = None
    notes_type: str | None = None
    priority: int | None = None


class ReminderResponse(BaseModel):
    id: str
    lead_id: str | None
    appointment_id: str | None
    user_id: str | None
    datetime: int | None
    notes: str | None
    notes_type: str | None
    priority: int | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(r: ReminderEntity) -> ReminderResponse:
    return ReminderResponse(
        id=r.id,
        lead_id=r.lead_id,
        appointment_id=r.appointment_id,
        user_id=r.user_id,
        datetime=r.datetime,
        notes=r.notes,
        notes_type=r.notes_type,
        priority=r.priority,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("/", response_model=list[ReminderResponse])
async def list_reminders(
    org_id: str = Query(..., description="Organization ID"),
    lead_id: str | None = Query(None),
    user_id: str | None = Query(None),
    repo: ReminderRepository = Depends(get_repo),
):
    items = await repo.list_by_org(org_id, lead_id=lead_id, user_id=user_id)
    return [_to_response(r) for r in items]


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str, repo: ReminderRepository = Depends(get_repo)):
    r = await repo.get_by_id(reminder_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return _to_response(r)


@router.post("/", response_model=ReminderResponse)
async def create_reminder(data: ReminderCreate, repo: ReminderRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = ReminderEntity(
        id=generate_uuid(),
        lead_id=data.lead_id,
        appointment_id=data.appointment_id,
        user_id=data.user_id,
        datetime=data.datetime,
        notes=data.notes,
        notes_type=data.notes_type,
        priority=data.priority,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str, data: ReminderUpdate, repo: ReminderRepository = Depends(get_repo)
):
    r = await repo.get_by_id(reminder_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    now = utc_now_ms()
    updated_entity = ReminderEntity(
        id=r.id,
        lead_id=data.lead_id if data.lead_id is not None else r.lead_id,
        appointment_id=data.appointment_id if data.appointment_id is not None else r.appointment_id,
        user_id=data.user_id if data.user_id is not None else r.user_id,
        datetime=data.datetime if data.datetime is not None else r.datetime,
        notes=data.notes if data.notes is not None else r.notes,
        notes_type=data.notes_type if data.notes_type is not None else r.notes_type,
        priority=data.priority if data.priority is not None else r.priority,
        created_at=r.created_at,
        updated_at=now,
    )
    updated = await repo.update(updated_entity)
    return _to_response(updated)


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str, repo: ReminderRepository = Depends(get_repo)):
    ok = await repo.delete(reminder_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"ok": True}
