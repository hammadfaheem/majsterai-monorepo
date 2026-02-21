"""Tag base routes – CRUD for org-level tag definitions."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms, generate_uuid
from ...domain.tag_base.entity import TagBase as TagBaseEntity
from ...infrastructure.database.repositories import (
    TagBaseRepository,
    SQLAlchemyTagBaseRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> TagBaseRepository:
    return SQLAlchemyTagBaseRepository(db)


class TagBaseCreate(BaseModel):
    org_id: str
    value: str
    color: str | None = None
    type: str = "LEAD"
    description: str | None = None
    is_enabled: bool = True


class TagBaseUpdate(BaseModel):
    value: str | None = None
    color: str | None = None
    type: str | None = None
    description: str | None = None
    is_enabled: bool | None = None


class TagBaseResponse(BaseModel):
    id: str
    org_id: str
    value: str
    color: str | None
    type: str
    description: str | None
    is_enabled: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[TagBaseResponse])
async def list_tag_bases(org_id: str, repo: TagBaseRepository = Depends(get_repo)):
    items = await repo.list_by_org_id(org_id)
    return [
        TagBaseResponse(
            id=t.id, org_id=t.org_id, value=t.value, color=t.color,
            type=t.type, description=t.description, is_enabled=t.is_enabled,
            created_at=t.created_at, updated_at=t.updated_at,
        )
        for t in items
    ]


@router.get("/{tag_base_id}", response_model=TagBaseResponse)
async def get_tag_base(tag_base_id: str, repo: TagBaseRepository = Depends(get_repo)):
    t = await repo.get_by_id(tag_base_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagBaseResponse(
        id=t.id, org_id=t.org_id, value=t.value, color=t.color,
        type=t.type, description=t.description, is_enabled=t.is_enabled,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.post("/", response_model=TagBaseResponse)
async def create_tag_base(data: TagBaseCreate, repo: TagBaseRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = TagBaseEntity(
        id=generate_uuid(), org_id=data.org_id, value=data.value, color=data.color,
        type=data.type, description=data.description, external_id=None, external_type=None,
        is_enabled=data.is_enabled, created_at=now, updated_at=now,
    )
    created = await repo.create(entity)
    return TagBaseResponse(
        id=created.id, org_id=created.org_id, value=created.value, color=created.color,
        type=created.type, description=created.description, is_enabled=created.is_enabled,
        created_at=created.created_at, updated_at=created.updated_at,
    )


@router.put("/{tag_base_id}", response_model=TagBaseResponse)
async def update_tag_base(tag_base_id: str, data: TagBaseUpdate, repo: TagBaseRepository = Depends(get_repo)):
    existing = await repo.get_by_id(tag_base_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Tag not found")
    now = utc_now_ms()
    if data.value is not None:
        existing.value = data.value
    if data.color is not None:
        existing.color = data.color
    if data.type is not None:
        existing.type = data.type
    if data.description is not None:
        existing.description = data.description
    if data.is_enabled is not None:
        existing.is_enabled = data.is_enabled
    existing.updated_at = now
    updated = await repo.update(existing)
    return TagBaseResponse(
        id=updated.id, org_id=updated.org_id, value=updated.value, color=updated.color,
        type=updated.type, description=updated.description, is_enabled=updated.is_enabled,
        created_at=updated.created_at, updated_at=updated.updated_at,
    )


@router.delete("/{tag_base_id}")
async def delete_tag_base(tag_base_id: str, repo: TagBaseRepository = Depends(get_repo)):
    existing = await repo.get_by_id(tag_base_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Tag not found")
    await repo.delete(tag_base_id)
    return {"message": "Deleted"}
