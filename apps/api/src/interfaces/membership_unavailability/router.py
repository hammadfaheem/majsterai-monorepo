"""Membership unavailability routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.membership_unavailability.entity import MembershipUnavailability as MembershipUnavailabilityEntity
from ...infrastructure.database.repositories import (
    MembershipUnavailabilityRepository,
    SQLAlchemyMembershipUnavailabilityRepository,
)

router = APIRouter()


def get_unavailability_repo(db: AsyncSession = Depends(get_db)) -> MembershipUnavailabilityRepository:
    """Dependency to get membership unavailability repository."""
    return SQLAlchemyMembershipUnavailabilityRepository(db)


class MembershipUnavailabilityCreate(BaseModel):
    """Request model for creating unavailability."""

    member_id: str
    start_date: int | None = None
    end_date: int | None = None
    start_time: int | None = None
    end_time: int | None = None
    recurrence_type: str | None = None
    days_of_week: list[str] | None = None


class MembershipUnavailabilityUpdate(BaseModel):
    """Request model for updating unavailability (partial)."""

    start_date: int | None = None
    end_date: int | None = None
    start_time: int | None = None
    end_time: int | None = None
    recurrence_type: str | None = None
    days_of_week: list[str] | None = None


class MembershipUnavailabilityResponse(BaseModel):
    """Response model for membership unavailability."""

    id: str
    member_id: str
    start_date: int | None
    end_date: int | None
    start_time: int | None
    end_time: int | None
    recurrence_type: str | None
    days_of_week: list[str] | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[MembershipUnavailabilityResponse])
async def list_unavailabilities_by_org(
    org_id: str,
    repo: MembershipUnavailabilityRepository = Depends(get_unavailability_repo),
):
    """List all unavailabilities for members of an organization."""
    items = await repo.list_by_org_id(org_id)
    return [
        MembershipUnavailabilityResponse(
            id=u.id,
            member_id=u.member_id,
            start_date=u.start_date,
            end_date=u.end_date,
            start_time=u.start_time,
            end_time=u.end_time,
            recurrence_type=u.recurrence_type,
            days_of_week=u.days_of_week,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in items
    ]


@router.get("/member/{member_id}", response_model=list[MembershipUnavailabilityResponse])
async def list_unavailabilities_by_member(
    member_id: str,
    repo: MembershipUnavailabilityRepository = Depends(get_unavailability_repo),
):
    """List unavailabilities for a specific membership."""
    items = await repo.list_by_member_id(member_id)
    return [
        MembershipUnavailabilityResponse(
            id=u.id,
            member_id=u.member_id,
            start_date=u.start_date,
            end_date=u.end_date,
            start_time=u.start_time,
            end_time=u.end_time,
            recurrence_type=u.recurrence_type,
            days_of_week=u.days_of_week,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in items
    ]


@router.post("/", response_model=MembershipUnavailabilityResponse)
async def create_unavailability(
    data: MembershipUnavailabilityCreate,
    repo: MembershipUnavailabilityRepository = Depends(get_unavailability_repo),
):
    """Create a membership unavailability."""
    from ...db.database import generate_uuid

    now = utc_now_ms()
    entity = MembershipUnavailabilityEntity(
        id=generate_uuid(),
        member_id=data.member_id,
        start_date=data.start_date,
        end_date=data.end_date,
        start_time=data.start_time,
        end_time=data.end_time,
        recurrence_type=data.recurrence_type,
        days_of_week=data.days_of_week,
        created_at=now,
        updated_at=now,
    )
    created = await repo.create(entity)
    return MembershipUnavailabilityResponse(
        id=created.id,
        member_id=created.member_id,
        start_date=created.start_date,
        end_date=created.end_date,
        start_time=created.start_time,
        end_time=created.end_time,
        recurrence_type=created.recurrence_type,
        days_of_week=created.days_of_week,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.put("/{unavailability_id}", response_model=MembershipUnavailabilityResponse)
async def update_unavailability(
    unavailability_id: str,
    data: MembershipUnavailabilityUpdate,
    repo: MembershipUnavailabilityRepository = Depends(get_unavailability_repo),
):
    """Update a membership unavailability."""
    existing = await repo.get_by_id(unavailability_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Unavailability not found")

    now = utc_now_ms()
    if data.start_date is not None:
        existing.start_date = data.start_date
    if data.end_date is not None:
        existing.end_date = data.end_date
    if data.start_time is not None:
        existing.start_time = data.start_time
    if data.end_time is not None:
        existing.end_time = data.end_time
    if data.recurrence_type is not None:
        existing.recurrence_type = data.recurrence_type
    if data.days_of_week is not None:
        existing.days_of_week = data.days_of_week
    existing.updated_at = now

    updated = await repo.update(existing)
    return MembershipUnavailabilityResponse(
        id=updated.id,
        member_id=updated.member_id,
        start_date=updated.start_date,
        end_date=updated.end_date,
        start_time=updated.start_time,
        end_time=updated.end_time,
        recurrence_type=updated.recurrence_type,
        days_of_week=updated.days_of_week,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/{unavailability_id}")
async def delete_unavailability(
    unavailability_id: str,
    repo: MembershipUnavailabilityRepository = Depends(get_unavailability_repo),
):
    """Delete a membership unavailability."""
    existing = await repo.get_by_id(unavailability_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Unavailability not found")
    await repo.delete(unavailability_id)
    return {"message": "Deleted"}
