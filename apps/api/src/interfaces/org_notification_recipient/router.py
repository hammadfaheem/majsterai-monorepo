"""Org notification recipient routes – GET/PUT for who receives what."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.org_notification_recipient.entity import OrgNotificationRecipient as OrgNotificationRecipientEntity
from ...infrastructure.database.repositories import (
    OrgNotificationRecipientRepository,
    SQLAlchemyOrgNotificationRecipientRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> OrgNotificationRecipientRepository:
    return SQLAlchemyOrgNotificationRecipientRepository(db)


class OrgNotificationRecipientUpdate(BaseModel):
    sms: str | None = None
    email: str | None = None
    sources: list | None = None
    all_tags: bool | None = None
    is_enabled: bool | None = None


class OrgNotificationRecipientResponse(BaseModel):
    id: str
    member_id: str
    sms: str | None
    email: str | None
    sources: list | None
    all_tags: bool
    is_enabled: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[OrgNotificationRecipientResponse])
async def list_org_notification_recipients(
    org_id: str, repo: OrgNotificationRecipientRepository = Depends(get_repo)
):
    items = await repo.list_by_org_id(org_id)
    return [
        OrgNotificationRecipientResponse(
            id=r.id, member_id=r.member_id, sms=r.sms, email=r.email,
            sources=r.sources, all_tags=r.all_tags, is_enabled=r.is_enabled,
            created_at=r.created_at, updated_at=r.updated_at,
        )
        for r in items
    ]


@router.get("/{recipient_id}", response_model=OrgNotificationRecipientResponse)
async def get_org_notification_recipient(
    recipient_id: str, repo: OrgNotificationRecipientRepository = Depends(get_repo)
):
    r = await repo.get_by_id(recipient_id)
    if not r:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return OrgNotificationRecipientResponse(
        id=r.id, member_id=r.member_id, sms=r.sms, email=r.email,
        sources=r.sources, all_tags=r.all_tags, is_enabled=r.is_enabled,
        created_at=r.created_at, updated_at=r.updated_at,
    )


@router.put("/{recipient_id}", response_model=OrgNotificationRecipientResponse)
async def update_org_notification_recipient(
    recipient_id: str,
    data: OrgNotificationRecipientUpdate,
    repo: OrgNotificationRecipientRepository = Depends(get_repo),
):
    existing = await repo.get_by_id(recipient_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recipient not found")
    now = utc_now_ms()
    if data.sms is not None:
        existing.sms = data.sms
    if data.email is not None:
        existing.email = data.email
    if data.sources is not None:
        existing.sources = data.sources
    if data.all_tags is not None:
        existing.all_tags = data.all_tags
    if data.is_enabled is not None:
        existing.is_enabled = data.is_enabled
    existing.updated_at = now
    updated = await repo.update(existing)
    return OrgNotificationRecipientResponse(
        id=updated.id, member_id=updated.member_id, sms=updated.sms, email=updated.email,
        sources=updated.sources, all_tags=updated.all_tags, is_enabled=updated.is_enabled,
        created_at=updated.created_at, updated_at=updated.updated_at,
    )
