"""Lead address routes – CRUD for addresses linked to leads."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.lead_address.entity import LeadAddress as LeadAddressEntity
from ...infrastructure.database.repositories import (
    LeadAddressRepository,
    LeadRepository,
    SQLAlchemyLeadAddressRepository,
    SQLAlchemyLeadRepository,
)
router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> LeadAddressRepository:
    return SQLAlchemyLeadAddressRepository(db)


def get_lead_repo(db: AsyncSession = Depends(get_db)) -> LeadRepository:
    return SQLAlchemyLeadRepository(db)


class LeadAddressCreate(BaseModel):
    address_id: str
    lead_id: str


class LeadAddressResponse(BaseModel):
    id: int
    address_id: str
    lead_id: str
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(a: LeadAddressEntity) -> LeadAddressResponse:
    return LeadAddressResponse(
        id=a.id,
        address_id=a.address_id,
        lead_id=a.lead_id,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("/", response_model=list[LeadAddressResponse])
async def list_lead_addresses(
    lead_id: str = Query(..., description="Lead ID"),
    repo: LeadAddressRepository = Depends(get_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    lead = await lead_repo.get_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    items = await repo.list_by_lead_id(lead_id)
    return [_to_response(a) for a in items]


@router.get("/{lead_address_id}", response_model=LeadAddressResponse)
async def get_lead_address(
    lead_address_id: int, repo: LeadAddressRepository = Depends(get_repo)
):
    a = await repo.get_by_id(lead_address_id)
    if not a:
        raise HTTPException(status_code=404, detail="Lead address not found")
    return _to_response(a)


@router.post("/", response_model=LeadAddressResponse)
async def create_lead_address(
    data: LeadAddressCreate,
    repo: LeadAddressRepository = Depends(get_repo),
    lead_repo: LeadRepository = Depends(get_lead_repo),
):
    lead = await lead_repo.get_by_id(data.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    now = utc_now_ms()
    entity = LeadAddressEntity(
        id=0,
        address_id=data.address_id,
        lead_id=data.lead_id,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.delete("/{lead_address_id}")
async def delete_lead_address(
    lead_address_id: int, repo: LeadAddressRepository = Depends(get_repo)
):
    ok = await repo.delete(lead_address_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lead address not found")
    return {"ok": True}
