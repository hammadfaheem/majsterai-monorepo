"""Notification log routes – GET recent sent notifications."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...infrastructure.database.repositories import (
    NotificationLogRepository,
    SQLAlchemyNotificationLogRepository,
)

router = APIRouter()


def get_repo(db: AsyncSession = Depends(get_db)) -> NotificationLogRepository:
    return SQLAlchemyNotificationLogRepository(db)


class NotificationLogResponse(BaseModel):
    id: int
    type: str
    channel: str | None
    lead_id: str | None
    target_id: str | None
    sent: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[NotificationLogResponse])
async def list_notification_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repo: NotificationLogRepository = Depends(get_repo),
):
    items = await repo.list_recent(limit=limit, offset=offset)
    return [
        NotificationLogResponse(
            id=item.id, type=item.type, channel=item.channel, lead_id=item.lead_id,
            target_id=item.target_id, sent=item.sent, created_at=item.created_at, updated_at=item.updated_at,
        )
        for item in items
    ]
