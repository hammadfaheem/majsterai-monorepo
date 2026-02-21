"""Schedule routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...domain.schedule.entity import Schedule as ScheduleEntity
from ...infrastructure.database.repositories import (
    ScheduleRepository,
    SQLAlchemyScheduleRepository,
)

router = APIRouter()


def get_schedule_repo(db: AsyncSession = Depends(get_db)) -> ScheduleRepository:
    return SQLAlchemyScheduleRepository(db)


class ScheduleCreate(BaseModel):
    name: str
    time_zone: str = "UTC"
    department_id: int | None = None


class ScheduleUpdate(BaseModel):
    name: str | None = None
    time_zone: str | None = None
    department_id: int | None = None


class ScheduleResponse(BaseModel):
    id: int
    name: str
    time_zone: str
    department_id: int | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ScheduleResponse])
async def list_schedules(repo: ScheduleRepository = Depends(get_schedule_repo)):
    items = await repo.list_all()
    return [ScheduleResponse(id=s.id, name=s.name, time_zone=s.time_zone, department_id=s.department_id) for s in items]


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, repo: ScheduleRepository = Depends(get_schedule_repo)):
    s = await repo.get_by_id(schedule_id)
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleResponse(id=s.id, name=s.name, time_zone=s.time_zone, department_id=s.department_id)


@router.post("/", response_model=ScheduleResponse)
async def create_schedule(data: ScheduleCreate, repo: ScheduleRepository = Depends(get_schedule_repo)):
    entity = ScheduleEntity(id=0, name=data.name, time_zone=data.time_zone, department_id=data.department_id)
    created = await repo.create(entity)
    return ScheduleResponse(id=created.id, name=created.name, time_zone=created.time_zone, department_id=created.department_id)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: int, data: ScheduleUpdate, repo: ScheduleRepository = Depends(get_schedule_repo)):
    existing = await repo.get_by_id(schedule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if data.name is not None:
        existing.name = data.name
    if data.time_zone is not None:
        existing.time_zone = data.time_zone
    if data.department_id is not None:
        existing.department_id = data.department_id
    updated = await repo.update(existing)
    return ScheduleResponse(id=updated.id, name=updated.name, time_zone=updated.time_zone, department_id=updated.department_id)


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int, repo: ScheduleRepository = Depends(get_schedule_repo)):
    existing = await repo.get_by_id(schedule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await repo.delete(schedule_id)
    return {"message": "Deleted"}
