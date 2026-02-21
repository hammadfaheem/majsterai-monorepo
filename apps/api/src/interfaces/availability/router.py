"""Availability routes – CRUD for schedule availability blocks."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.availability.entity import Availability as AvailabilityEntity
from ...infrastructure.database.repositories import (
    AvailabilityRepository,
    ScheduleRepository,
    SQLAlchemyAvailabilityRepository,
    SQLAlchemyScheduleRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> AvailabilityRepository:
    return SQLAlchemyAvailabilityRepository(db)


def get_schedule_repo(db: AsyncSession = Depends(get_db)) -> ScheduleRepository:
    return SQLAlchemyScheduleRepository(db)


class AvailabilityCreate(BaseModel):
    schedule_id: int
    days: list[str] | None = None
    start_time: int | None = None
    end_time: int | None = None
    user_id: str | None = None


class AvailabilityUpdate(BaseModel):
    schedule_id: int | None = None
    days: list[str] | None = None
    start_time: int | None = None
    end_time: int | None = None
    user_id: str | None = None


class AvailabilityResponse(BaseModel):
    id: int
    schedule_id: int
    days: list[str] | None
    start_time: int | None
    end_time: int | None
    user_id: str | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(a: AvailabilityEntity) -> AvailabilityResponse:
    return AvailabilityResponse(
        id=a.id,
        schedule_id=a.schedule_id,
        days=a.days,
        start_time=a.start_time,
        end_time=a.end_time,
        user_id=a.user_id,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("/", response_model=list[AvailabilityResponse])
async def list_availabilities(
    org_id: str | None = Query(None, description="Organization ID (all availabilities for org)"),
    schedule_id: int | None = Query(None, description="Schedule ID"),
    repo: AvailabilityRepository = Depends(get_repo),
):
    if schedule_id is not None:
        items = await repo.list_by_schedule_id(schedule_id)
    elif org_id:
        items = await repo.list_by_org_id(org_id)
    else:
        raise HTTPException(status_code=400, detail="Provide org_id or schedule_id")
    return [_to_response(a) for a in items]


@router.get("/{availability_id}", response_model=AvailabilityResponse)
async def get_availability(
    availability_id: int, repo: AvailabilityRepository = Depends(get_repo)
):
    a = await repo.get_by_id(availability_id)
    if not a:
        raise HTTPException(status_code=404, detail="Availability not found")
    return _to_response(a)


@router.post("/", response_model=AvailabilityResponse)
async def create_availability(
    data: AvailabilityCreate,
    repo: AvailabilityRepository = Depends(get_repo),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repo),
):
    s = await schedule_repo.get_by_id(data.schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    now = utc_now_ms()
    entity = AvailabilityEntity(
        id=0,
        schedule_id=data.schedule_id,
        days=data.days,
        start_time=data.start_time,
        end_time=data.end_time,
        user_id=data.user_id,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{availability_id}", response_model=AvailabilityResponse)
async def update_availability(
    availability_id: int,
    data: AvailabilityUpdate,
    repo: AvailabilityRepository = Depends(get_repo),
):
    a = await repo.get_by_id(availability_id)
    if not a:
        raise HTTPException(status_code=404, detail="Availability not found")
    if data.schedule_id is not None:
        a.schedule_id = data.schedule_id
    if data.days is not None:
        a.days = data.days
    if data.start_time is not None:
        a.start_time = data.start_time
    if data.end_time is not None:
        a.end_time = data.end_time
    if data.user_id is not None:
        a.user_id = data.user_id
    a.updated_at = utc_now_ms()
    updated = await repo.update(a)
    return _to_response(updated)


@router.delete("/{availability_id}")
async def delete_availability(
    availability_id: int, repo: AvailabilityRepository = Depends(get_repo)
):
    ok = await repo.delete(availability_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Availability not found")
    return {"ok": True}
