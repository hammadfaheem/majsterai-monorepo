"""Trade service routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.trade_service.entity import TradeService as TradeServiceEntity
from ...infrastructure.database.repositories import (
    TradeServiceRepository,
    SQLAlchemyTradeServiceRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> TradeServiceRepository:
    return SQLAlchemyTradeServiceRepository(db)


class TradeServiceCreate(BaseModel):
    org_id: str
    name: str
    description: str | None = None
    duration: int | None = None
    duration_unit: str | None = None
    followup_questions: list | None = None
    pricing_mode: str | None = None
    fixed_price: int | None = None
    hourly_rate: int | None = None
    min_price: int | None = None
    max_price: int | None = None
    call_out_fee: int | None = None
    plus_gst: bool = False
    plus_materials: bool = False
    is_disclose_price: bool = True
    custom_price_response: str | None = None
    is_active: bool = True
    trade_category_id: int | None = None


class TradeServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration: int | None = None
    duration_unit: str | None = None
    followup_questions: list | None = None
    pricing_mode: str | None = None
    fixed_price: int | None = None
    hourly_rate: int | None = None
    min_price: int | None = None
    max_price: int | None = None
    call_out_fee: int | None = None
    plus_gst: bool | None = None
    plus_materials: bool | None = None
    is_disclose_price: bool | None = None
    custom_price_response: str | None = None
    is_active: bool | None = None
    trade_category_id: int | None = None


class TradeServiceResponse(BaseModel):
    id: int
    org_id: str
    name: str
    description: str | None
    duration: int | None
    duration_unit: str | None
    followup_questions: list | None
    pricing_mode: str | None
    fixed_price: int | None
    hourly_rate: int | None
    min_price: int | None
    max_price: int | None
    call_out_fee: int | None
    plus_gst: bool
    plus_materials: bool
    is_disclose_price: bool
    custom_price_response: str | None
    is_active: bool
    trade_category_id: int | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


def _to_response(s: TradeServiceEntity) -> TradeServiceResponse:
    return TradeServiceResponse(
        id=s.id,
        org_id=s.org_id,
        name=s.name,
        description=s.description,
        duration=s.duration,
        duration_unit=s.duration_unit,
        followup_questions=s.followup_questions,
        pricing_mode=s.pricing_mode,
        fixed_price=s.fixed_price,
        hourly_rate=s.hourly_rate,
        min_price=s.min_price,
        max_price=s.max_price,
        call_out_fee=s.call_out_fee,
        plus_gst=s.plus_gst,
        plus_materials=s.plus_materials,
        is_disclose_price=s.is_disclose_price,
        custom_price_response=s.custom_price_response,
        is_active=s.is_active,
        trade_category_id=s.trade_category_id,
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


@router.get("/org/{org_id}", response_model=list[TradeServiceResponse])
async def list_services(org_id: str, repo: TradeServiceRepository = Depends(get_repo)):
    items = await repo.list_by_org_id(org_id)
    return [_to_response(s) for s in items]


@router.get("/{service_id}", response_model=TradeServiceResponse)
async def get_service(service_id: int, repo: TradeServiceRepository = Depends(get_repo)):
    s = await repo.get_by_id(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Trade service not found")
    return _to_response(s)


@router.post("/", response_model=TradeServiceResponse)
async def create_service(data: TradeServiceCreate, repo: TradeServiceRepository = Depends(get_repo)):
    now = utc_now_ms()
    entity = TradeServiceEntity(
        id=0,
        org_id=data.org_id,
        name=data.name,
        description=data.description,
        duration=data.duration,
        duration_unit=data.duration_unit,
        followup_questions=data.followup_questions,
        pricing_mode=data.pricing_mode,
        fixed_price=data.fixed_price,
        hourly_rate=data.hourly_rate,
        min_price=data.min_price,
        max_price=data.max_price,
        call_out_fee=data.call_out_fee,
        plus_gst=data.plus_gst,
        plus_materials=data.plus_materials,
        is_disclose_price=data.is_disclose_price,
        custom_price_response=data.custom_price_response,
        is_active=data.is_active,
        trade_category_id=data.trade_category_id,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return _to_response(created)


@router.put("/{service_id}", response_model=TradeServiceResponse)
async def update_service(service_id: int, data: TradeServiceUpdate, repo: TradeServiceRepository = Depends(get_repo)):
    existing = await repo.get_by_id(service_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trade service not found")
    now = utc_now_ms()
    if data.name is not None:
        existing.name = data.name
    if data.description is not None:
        existing.description = data.description
    if data.duration is not None:
        existing.duration = data.duration
    if data.duration_unit is not None:
        existing.duration_unit = data.duration_unit
    if data.followup_questions is not None:
        existing.followup_questions = data.followup_questions
    if data.pricing_mode is not None:
        existing.pricing_mode = data.pricing_mode
    if data.fixed_price is not None:
        existing.fixed_price = data.fixed_price
    if data.hourly_rate is not None:
        existing.hourly_rate = data.hourly_rate
    if data.min_price is not None:
        existing.min_price = data.min_price
    if data.max_price is not None:
        existing.max_price = data.max_price
    if data.call_out_fee is not None:
        existing.call_out_fee = data.call_out_fee
    if data.plus_gst is not None:
        existing.plus_gst = data.plus_gst
    if data.plus_materials is not None:
        existing.plus_materials = data.plus_materials
    if data.is_disclose_price is not None:
        existing.is_disclose_price = data.is_disclose_price
    if data.custom_price_response is not None:
        existing.custom_price_response = data.custom_price_response
    if data.is_active is not None:
        existing.is_active = data.is_active
    if data.trade_category_id is not None:
        existing.trade_category_id = data.trade_category_id
    existing.updated_at = now
    updated = await repo.update(existing)
    return _to_response(updated)


@router.delete("/{service_id}")
async def delete_service(service_id: int, repo: TradeServiceRepository = Depends(get_repo)):
    existing = await repo.get_by_id(service_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Trade service not found")
    await repo.delete(service_id)
    return {"message": "Deleted"}
