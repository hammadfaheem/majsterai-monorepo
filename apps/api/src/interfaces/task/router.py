"""Task routes – CRUD for tasks (lead/inquiry)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms, generate_uuid
from ...domain.task.entity import Task as TaskEntity
from ...infrastructure.database.repositories import (
    TaskRepository,
    SQLAlchemyTaskRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return SQLAlchemyTaskRepository(db)


class TaskCreate(BaseModel):
    org_id: str
    title: str
    is_completed: bool = False
    type: str | None = None
    inquiry_id: str | None = None
    lead_id: str | None = None
    assigned_member_id: str | None = None
    is_created_by_sophiie: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None
    type: str | None = None
    lead_id: str | None = None
    assigned_member_id: str | None = None


class TaskResponse(BaseModel):
    id: str
    org_id: str
    title: str
    is_completed: bool
    type: str | None
    inquiry_id: str | None
    lead_id: str | None
    assigned_member_id: str | None
    is_created_by_sophiie: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(t: TaskEntity) -> TaskResponse:
    return TaskResponse(
        id=t.id,
        org_id=t.org_id,
        title=t.title,
        is_completed=t.is_completed,
        type=t.type,
        inquiry_id=t.inquiry_id,
        lead_id=t.lead_id,
        assigned_member_id=t.assigned_member_id,
        is_created_by_sophiie=t.is_created_by_sophiie,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    org_id: str = Query(..., description="Organization ID"),
    lead_id: str | None = Query(None),
    repo: TaskRepository = Depends(get_repo),
):
    items = await repo.list_by_org_id(org_id, lead_id=lead_id)
    return [_to_response(t) for t in items]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, repo: TaskRepository = Depends(get_repo)):
    t = await repo.get_by_id(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(t)


@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreate, repo: TaskRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = TaskEntity(
        id=generate_uuid(),
        org_id=data.org_id,
        title=data.title,
        is_completed=data.is_completed,
        type=data.type,
        inquiry_id=data.inquiry_id,
        lead_id=data.lead_id,
        assigned_member_id=data.assigned_member_id,
        is_created_by_sophiie=data.is_created_by_sophiie,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, data: TaskUpdate, repo: TaskRepository = Depends(get_repo)):
    existing = await repo.get_by_id(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    now = utc_now_ms()
    if data.title is not None:
        existing.title = data.title
    if data.is_completed is not None:
        existing.is_completed = data.is_completed
    if data.type is not None:
        existing.type = data.type
    if data.lead_id is not None:
        existing.lead_id = data.lead_id
    if data.assigned_member_id is not None:
        existing.assigned_member_id = data.assigned_member_id
    existing.updated_at = now
    updated = await repo.update(existing)
    return _to_response(updated)


@router.delete("/{task_id}")
async def delete_task(task_id: str, repo: TaskRepository = Depends(get_repo)):
    existing = await repo.get_by_id(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    await repo.delete(task_id)
    return {"message": "Deleted"}
