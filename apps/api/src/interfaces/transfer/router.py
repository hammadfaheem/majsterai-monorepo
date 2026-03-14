"""Transfer routes - CRUD for call transfer configs."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...db.database import generate_uuid
from ...domain.transfer.entity import Transfer as TransferEntity
from ...domain.user.entity import User as UserEntity
from ...infrastructure.database.repositories import (
    MembershipRepository,
    TransferRepository,
    SQLAlchemyTransferRepository,
)
from ...interfaces.auth.router import get_current_user_dep, get_membership_repo
from ...shared.org_access import require_org_membership, verify_org_access

router = APIRouter()


def get_transfer_repo(db: AsyncSession = Depends(get_db)) -> TransferRepository:
    return SQLAlchemyTransferRepository(db)


class TransferCreate(BaseModel):
    org_id: str
    label: str
    method: str  # COLD, WARM
    destination_type: str  # DEPARTMENT, MEMBER, PHONE
    destination: str
    conditions: dict | None = None
    summary_format: str | None = None
    settings: dict | None = None
    scenario_id: str | None = None


class TransferUpdate(BaseModel):
    label: str | None = None
    method: str | None = None
    destination_type: str | None = None
    destination: str | None = None
    conditions: dict | None = None
    summary_format: str | None = None
    settings: dict | None = None
    scenario_id: str | None = None


class TransferResponse(BaseModel):
    id: str
    org_id: str
    label: str
    method: str
    destination_type: str
    destination: str
    conditions: dict | None
    summary_format: str | None
    settings: dict | None
    scenario_id: str | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[TransferResponse])
async def list_transfers(
    org_id: str,
    repo: TransferRepository = Depends(get_transfer_repo),
):
    items = await repo.list_by_org_id(org_id)
    return [
        TransferResponse(
            id=t.id,
            org_id=t.org_id,
            label=t.label,
            method=t.method,
            destination_type=t.destination_type,
            destination=t.destination,
            conditions=t.conditions,
            summary_format=t.summary_format,
            settings=t.settings,
            scenario_id=t.scenario_id,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in items
    ]


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: str,
    repo: TransferRepository = Depends(get_transfer_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    t = await repo.get_by_id(transfer_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transfer not found")
    await verify_org_access(t.org_id, current_user, membership_repo)
    return TransferResponse(
        id=t.id,
        org_id=t.org_id,
        label=t.label,
        method=t.method,
        destination_type=t.destination_type,
        destination=t.destination,
        conditions=t.conditions,
        summary_format=t.summary_format,
        settings=t.settings,
        scenario_id=t.scenario_id,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.post("/", response_model=TransferResponse)
async def create_transfer(
    data: TransferCreate,
    repo: TransferRepository = Depends(get_transfer_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    await verify_org_access(data.org_id, current_user, membership_repo)
    now = utc_now_ms()
    entity = TransferEntity(
        id=generate_uuid(),
        org_id=data.org_id,
        label=data.label,
        method=data.method,
        destination_type=data.destination_type,
        destination=data.destination,
        conditions=data.conditions,
        summary_format=data.summary_format,
        settings=data.settings,
        scenario_id=data.scenario_id,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return TransferResponse(
        id=created.id,
        org_id=created.org_id,
        label=created.label,
        method=created.method,
        destination_type=created.destination_type,
        destination=created.destination,
        conditions=created.conditions,
        summary_format=created.summary_format,
        settings=created.settings,
        scenario_id=created.scenario_id,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.put("/{transfer_id}", response_model=TransferResponse)
async def update_transfer(
    transfer_id: str,
    data: TransferUpdate,
    repo: TransferRepository = Depends(get_transfer_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    existing = await repo.get_by_id(transfer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Transfer not found")
    await verify_org_access(existing.org_id, current_user, membership_repo)
    now = utc_now_ms()
    if data.label is not None:
        existing.label = data.label
    if data.method is not None:
        existing.method = data.method
    if data.destination_type is not None:
        existing.destination_type = data.destination_type
    if data.destination is not None:
        existing.destination = data.destination
    if data.conditions is not None:
        existing.conditions = data.conditions
    if data.summary_format is not None:
        existing.summary_format = data.summary_format
    if data.settings is not None:
        existing.settings = data.settings
    if data.scenario_id is not None:
        existing.scenario_id = data.scenario_id
    existing.updated_at = now
    updated = await repo.update(existing)
    return TransferResponse(
        id=updated.id,
        org_id=updated.org_id,
        label=updated.label,
        method=updated.method,
        destination_type=updated.destination_type,
        destination=updated.destination,
        conditions=updated.conditions,
        summary_format=updated.summary_format,
        settings=updated.settings,
        scenario_id=updated.scenario_id,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{transfer_id}")
async def delete_transfer(
    transfer_id: str,
    repo: TransferRepository = Depends(get_transfer_repo),
    current_user: UserEntity = Depends(get_current_user_dep),
    membership_repo: MembershipRepository = Depends(get_membership_repo),
):
    existing = await repo.get_by_id(transfer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Transfer not found")
    await verify_org_access(existing.org_id, current_user, membership_repo)
    await repo.delete(transfer_id)
    return {"message": "Deleted"}
