"""Trade category routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.trade_category.entity import TradeCategory as TradeCategoryEntity
from ...infrastructure.database.repositories import (
    TradeCategoryRepository,
    SQLAlchemyTradeCategoryRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> TradeCategoryRepository:
    return SQLAlchemyTradeCategoryRepository(db)


class TradeCategoryCreate(BaseModel):
    org_id: str
    name: str
    type: str | None = None


class TradeCategoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None


class TradeCategoryResponse(BaseModel):
    id: int
    org_id: str
    name: str
    type: str | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[TradeCategoryResponse])
async def list_categories(org_id: str, repo: TradeCategoryRepository = Depends(get_repo)):
    items = await repo.list_by_org_id(org_id)
    return [
        TradeCategoryResponse(id=c.id, org_id=c.org_id, name=c.name, type=c.type, created_at=c.created_at, updated_at=c.updated_at)
        for c in items
    ]


@router.get("/{category_id}", response_model=TradeCategoryResponse)
async def get_category(category_id: int, repo: TradeCategoryRepository = Depends(get_repo)):
    c = await repo.get_by_id(category_id)
    if not c:
        raise HTTPException(status_code=404, detail="Trade category not found")
    return TradeCategoryResponse(id=c.id, org_id=c.org_id, name=c.name, type=c.type, created_at=c.created_at, updated_at=c.updated_at)


@router.post("/", response_model=TradeCategoryResponse)
async def create_category(data: TradeCategoryCreate, repo: TradeCategoryRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = TradeCategoryEntity(id=0, org_id=data.org_id, name=data.name, type=data.type, created_at=now, updated_at=now)
    created = await repo.create(entity)
    return TradeCategoryResponse(id=created.id, org_id=created.org_id, name=created.name, type=created.type, created_at=created.created_at, updated_at=created.updated_at)


@router.put("/{category_id}", response_model=TradeCategoryResponse)
async def update_category(category_id: int, data: TradeCategoryUpdate, repo: TradeCategoryRepository = Depends(get_repo)):
    existing = await repo.get_by_id(category_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trade category not found")
    now = utc_now_ms()
    if data.name is not None:
        existing.name = data.name
    if data.type is not None:
        existing.type = data.type
    existing.updated_at = now
    updated = await repo.update(existing)
    return TradeCategoryResponse(id=updated.id, org_id=updated.org_id, name=updated.name, type=updated.type, created_at=updated.created_at, updated_at=updated.updated_at)


@router.delete("/{category_id}")
async def delete_category(category_id: int, repo: TradeCategoryRepository = Depends(get_repo)):
    existing = await repo.get_by_id(category_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trade category not found")
    await repo.delete(category_id)
    return {"message": "Deleted"}
