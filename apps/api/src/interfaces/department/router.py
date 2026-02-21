"""Department routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.department.entity import Department as DepartmentEntity
from ...infrastructure.database.repositories import (
    DepartmentRepository,
    SQLAlchemyDepartmentRepository,
)

router = APIRouter()


def get_department_repo(db: AsyncSession = Depends(get_db)) -> DepartmentRepository:
    return SQLAlchemyDepartmentRepository(db)


class DepartmentCreate(BaseModel):
    org_id: str
    name: str
    description: str | None = None
    default_schedule_id: int | None = None
    is_active: bool = True
    max_concurrent_calls: int | None = None
    escalation_timeout: int | None = None
    escalation_settings: dict | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    default_schedule_id: int | None = None
    is_active: bool | None = None
    max_concurrent_calls: int | None = None
    escalation_timeout: int | None = None
    escalation_settings: dict | None = None


class DepartmentResponse(BaseModel):
    id: int
    org_id: str
    name: str
    description: str | None
    default_schedule_id: int | None
    is_active: bool
    max_concurrent_calls: int | None
    escalation_timeout: int | None
    escalation_settings: dict | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(d: DepartmentEntity) -> DepartmentResponse:
    return DepartmentResponse(
        id=d.id,
        org_id=d.org_id,
        name=d.name,
        description=d.description,
        default_schedule_id=d.default_schedule_id,
        is_active=d.is_active,
        max_concurrent_calls=d.max_concurrent_calls,
        escalation_timeout=d.escalation_timeout,
        escalation_settings=d.escalation_settings,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


@router.get("/org/{org_id}", response_model=list[DepartmentResponse])
async def list_departments(org_id: str, repo: DepartmentRepository = Depends(get_department_repo)):
    items = await repo.list_by_org_id(org_id)
    return [_to_response(d) for d in items]


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: int, repo: DepartmentRepository = Depends(get_department_repo)):
    d = await repo.get_by_id(department_id)
    if not d:
        raise HTTPException(status_code=404, detail="Department not found")
    return _to_response(d)


@router.post("/", response_model=DepartmentResponse)
async def create_department(data: DepartmentCreate, repo: DepartmentRepository = Depends(get_department_repo)):
    now = utc_now_ms()
    entity = DepartmentEntity(
        id=0,
        org_id=data.org_id,
        name=data.name,
        description=data.description,
        default_schedule_id=data.default_schedule_id,
        is_active=data.is_active,
        max_concurrent_calls=data.max_concurrent_calls,
        escalation_timeout=data.escalation_timeout,
        escalation_settings=data.escalation_settings,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    repo: DepartmentRepository = Depends(get_department_repo),
):
    existing = await repo.get_by_id(department_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Department not found")
    now = utc_now_ms()
    if data.name is not None:
        existing.name = data.name
    if data.description is not None:
        existing.description = data.description
    if data.default_schedule_id is not None:
        existing.default_schedule_id = data.default_schedule_id
    if data.is_active is not None:
        existing.is_active = data.is_active
    if data.max_concurrent_calls is not None:
        existing.max_concurrent_calls = data.max_concurrent_calls
    if data.escalation_timeout is not None:
        existing.escalation_timeout = data.escalation_timeout
    if data.escalation_settings is not None:
        existing.escalation_settings = data.escalation_settings
    existing.updated_at = now
    updated = await repo.update(existing)
    return _to_response(updated)


@router.delete("/{department_id}")
async def delete_department(department_id: int, repo: DepartmentRepository = Depends(get_department_repo)):
    existing = await repo.get_by_id(department_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Department not found")
    await repo.delete(department_id)
    return {"message": "Deleted"}
