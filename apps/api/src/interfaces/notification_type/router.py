"""Notification type routes – GET/PUT for org-level notification templates."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db, utc_now_ms
from ...domain.notification_type.entity import NotificationType as NotificationTypeEntity
from ...infrastructure.database.repositories import (
    NotificationTypeRepository,
    SQLAlchemyNotificationTypeRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> NotificationTypeRepository:
    return SQLAlchemyNotificationTypeRepository(db)


class NotificationTypeUpdate(BaseModel):
    value: str | None = None
    template: dict | None = None
    channels: list | None = None
    schedule: dict | None = None
    enabled: bool | None = None


class NotificationTypeResponse(BaseModel):
    id: str
    org_id: str
    value: str
    template: dict | None
    channels: list | None
    schedule: dict | None
    enabled: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/org/{org_id}", response_model=list[NotificationTypeResponse])
async def list_notification_types(org_id: str, repo: NotificationTypeRepository = Depends(get_repo)):
    items = await repo.list_by_org_id(org_id)
    return [
        NotificationTypeResponse(
            id=t.id, org_id=t.org_id, value=t.value, template=t.template,
            channels=t.channels, schedule=t.schedule, enabled=t.enabled,
            created_at=t.created_at, updated_at=t.updated_at,
        )
        for t in items
    ]


@router.get("/{notification_type_id}", response_model=NotificationTypeResponse)
async def get_notification_type(
    notification_type_id: str, repo: NotificationTypeRepository = Depends(get_repo)
):
    t = await repo.get_by_id(notification_type_id)
    if not t:
        raise HTTPException(status_code=404, detail="Notification type not found")
    return NotificationTypeResponse(
        id=t.id, org_id=t.org_id, value=t.value, template=t.template,
        channels=t.channels, schedule=t.schedule, enabled=t.enabled,
        created_at=t.created_at, updated_at=t.updated_at,
    )


@router.put("/{notification_type_id}", response_model=NotificationTypeResponse)
async def update_notification_type(
    notification_type_id: str,
    data: NotificationTypeUpdate,
    repo: NotificationTypeRepository = Depends(get_repo),
):
    existing = await repo.get_by_id(notification_type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Notification type not found")
    now = utc_now_ms()
    if data.value is not None:
        existing.value = data.value
    if data.template is not None:
        existing.template = data.template
    if data.channels is not None:
        existing.channels = data.channels
    if data.schedule is not None:
        existing.schedule = data.schedule
    if data.enabled is not None:
        existing.enabled = data.enabled
    existing.updated_at = now
    updated = await repo.update(existing)
    return NotificationTypeResponse(
        id=updated.id, org_id=updated.org_id, value=updated.value, template=updated.template,
        channels=updated.channels, schedule=updated.schedule, enabled=updated.enabled,
        created_at=updated.created_at, updated_at=updated.updated_at,
    )
