"""Call history routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.call_history.get_call_analytics import GetCallAnalyticsUseCase
from ...application.call_history.get_call_details import GetCallDetailsUseCase
from ...application.call_history.update_call_status import UpdateCallStatusUseCase
from ...db.database import get_db
from ...infrastructure.database.repositories import (
    CallHistoryRepository,
    SQLAlchemyCallHistoryRepository,
    SQLAlchemyTranscriptRepository,
    TranscriptRepository,
)
from ...shared.exceptions import NotFoundError

router = APIRouter()


def get_call_history_repo(db: AsyncSession = Depends(get_db)) -> CallHistoryRepository:
    """Dependency to get call history repository."""
    return SQLAlchemyCallHistoryRepository(db)


def get_transcript_repo(db: AsyncSession = Depends(get_db)) -> TranscriptRepository:
    """Dependency to get transcript repository."""
    return SQLAlchemyTranscriptRepository(db)


class CallHistoryResponse(BaseModel):
    """Response model for call history."""

    id: int
    room_name: str
    org_id: str
    agent_id: int | None
    direction: str
    from_phone_number: str | None
    to_phone_number: str | None
    start_time: int | None
    end_time: int | None
    duration: int | None
    status: str
    summary: str | None
    analyzed_data: dict | None = None
    twilio_call_sid: str | None = None
    function_calls: list | None = None
    cost: dict | None = None
    total_metrics: dict | None = None
    variables: dict | None = None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class TranscriptResponse(BaseModel):
    """Response model for transcript."""

    id: str
    room_name: str
    org_id: str
    transcript: str
    segments: dict | None
    sentiment: str | None
    keywords: list[str] | None
    summary: str | None
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


class CallDetailsResponse(BaseModel):
    """Response model for call details with transcript."""

    call_history: CallHistoryResponse
    transcript: TranscriptResponse | None


@router.get("/", response_model=list[CallHistoryResponse])
async def list_calls(
    org_id: str = Query(..., description="Organization ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    call_history_repo: CallHistoryRepository = Depends(get_call_history_repo),
):
    """List call history for an organization."""
    entities = await call_history_repo.list_by_org_id(org_id, limit=limit, offset=offset)
    return [
        CallHistoryResponse(
            id=e.id,
            room_name=e.room_name,
            org_id=e.org_id,
            agent_id=e.agent_id,
            direction=e.direction,
            from_phone_number=e.from_phone_number,
            to_phone_number=e.to_phone_number,
            start_time=e.start_time,
            end_time=e.end_time,
            duration=e.duration,
            status=e.status,
            summary=e.summary,
            analyzed_data=e.analyzed_data,
            twilio_call_sid=e.twilio_call_sid,
            function_calls=e.function_calls,
            cost=e.cost,
            total_metrics=e.total_metrics,
            variables=e.variables,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in entities
    ]


@router.get("/{room_name}", response_model=CallDetailsResponse)
async def get_call_details(
    room_name: str,
    call_history_repo: CallHistoryRepository = Depends(get_call_history_repo),
    transcript_repo: TranscriptRepository = Depends(get_transcript_repo),
):
    """Get call details with transcript."""
    use_case = GetCallDetailsUseCase(call_history_repo, transcript_repo)
    try:
        call_history, transcript = await use_case.execute(room_name)
        return CallDetailsResponse(
            call_history=CallHistoryResponse(
                id=call_history.id,
                room_name=call_history.room_name,
                org_id=call_history.org_id,
                agent_id=call_history.agent_id,
                direction=call_history.direction,
                from_phone_number=call_history.from_phone_number,
                to_phone_number=call_history.to_phone_number,
                start_time=call_history.start_time,
                end_time=call_history.end_time,
                duration=call_history.duration,
                status=call_history.status,
                summary=call_history.summary,
                analyzed_data=call_history.analyzed_data,
                twilio_call_sid=call_history.twilio_call_sid,
                function_calls=call_history.function_calls,
                cost=call_history.cost,
                total_metrics=call_history.total_metrics,
                variables=call_history.variables,
                created_at=call_history.created_at,
                updated_at=call_history.updated_at,
            ),
            transcript=TranscriptResponse(
                id=transcript.id,
                room_name=transcript.room_name,
                org_id=transcript.org_id,
                transcript=transcript.transcript,
                segments=transcript.segments,
                sentiment=transcript.sentiment,
                keywords=transcript.keywords,
                summary=transcript.summary,
                created_at=transcript.created_at,
                updated_at=transcript.updated_at,
            )
            if transcript
            else None,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics/summary", response_model=dict)
async def get_analytics(
    org_id: str = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get call analytics for an organization."""
    use_case = GetCallAnalyticsUseCase(db)
    return await use_case.execute(org_id)


@router.put("/{room_name}/status")
async def update_call_status(
    room_name: str,
    status: str = Query(..., description="New status"),
    call_history_repo: CallHistoryRepository = Depends(get_call_history_repo),
):
    """Update call status."""
    use_case = UpdateCallStatusUseCase(call_history_repo)
    try:
        call_history = await use_case.execute(room_name, status)
        return CallHistoryResponse(
            id=call_history.id,
            room_name=call_history.room_name,
            org_id=call_history.org_id,
            agent_id=call_history.agent_id,
            direction=call_history.direction,
            from_phone_number=call_history.from_phone_number,
            to_phone_number=call_history.to_phone_number,
            start_time=call_history.start_time,
            end_time=call_history.end_time,
            duration=call_history.duration,
            status=call_history.status,
            summary=call_history.summary,
            analyzed_data=call_history.analyzed_data,
            twilio_call_sid=call_history.twilio_call_sid,
            function_calls=call_history.function_calls,
            cost=call_history.cost,
            total_metrics=call_history.total_metrics,
            variables=call_history.variables,
            created_at=call_history.created_at,
            updated_at=call_history.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
