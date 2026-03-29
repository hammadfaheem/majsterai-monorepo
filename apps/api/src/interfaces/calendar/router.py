"""Calendar routes — selected calendars management and Google/Outlook OAuth scaffold."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ...infrastructure.database.repositories import (
    SQLAlchemySelectedCalendarRepository,
    SelectedCalendarRepository,
)

router = APIRouter()


def get_calendar_repo(db: AsyncSession = Depends(get_db)) -> SelectedCalendarRepository:
    return SQLAlchemySelectedCalendarRepository(db)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class SelectedCalendarUpsert(BaseModel):
    member_id: str
    org_id: str | None = None
    credential_id: str | None = None
    calendar_id: str | None = None
    calendar_name: str | None = None
    integration: str | None = None  # "google" | "outlook"
    is_default: bool = False
    is_active_for_conflict_check: bool = True


class SelectedCalendarResponse(BaseModel):
    id: int
    org_id: str | None
    credential_id: str | None
    calendar_id: str | None
    calendar_name: str | None
    integration: str | None
    is_default: bool
    is_active_for_conflict_check: bool
    member_id: str
    last_synced_at: int | None
    next_async_token: str | None
    created_at: int
    updated_at: int


# ---------------------------------------------------------------------------
# Selected Calendars CRUD
# ---------------------------------------------------------------------------

@router.get("/selected-calendars", response_model=list[SelectedCalendarResponse])
async def list_selected_calendars(
    member_id: str | None = Query(None),
    org_id: str | None = Query(None),
    repo: SelectedCalendarRepository = Depends(get_calendar_repo),
):
    """List calendars linked for a member or org."""
    if member_id:
        return await repo.list_by_member_id(member_id)
    if org_id:
        return await repo.list_by_org_id(org_id)
    raise HTTPException(status_code=400, detail="member_id or org_id required")


@router.post("/selected-calendars", response_model=SelectedCalendarResponse)
async def upsert_selected_calendar(
    data: SelectedCalendarUpsert,
    repo: SelectedCalendarRepository = Depends(get_calendar_repo),
):
    """Add or update a linked calendar for a member."""
    return await repo.upsert(data.model_dump())


@router.put("/selected-calendars/{calendar_id}/set-default")
async def set_default_calendar(
    calendar_id: int,
    member_id: str = Query(...),
    repo: SelectedCalendarRepository = Depends(get_calendar_repo),
):
    """Set one calendar as the default for writing new events."""
    ok = await repo.set_default(calendar_id, member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return {"message": "Default calendar updated"}


@router.delete("/selected-calendars/{calendar_id}")
async def remove_selected_calendar(
    calendar_id: int,
    repo: SelectedCalendarRepository = Depends(get_calendar_repo),
):
    """Remove a linked calendar."""
    ok = await repo.delete(calendar_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return {"message": "Calendar removed"}


# ---------------------------------------------------------------------------
# Google OAuth scaffold
# ---------------------------------------------------------------------------
# These endpoints require GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in .env.
# The actual OAuth flow redirects the user to Google and exchanges the code
# for access + refresh tokens, which are stored in the `credential` table.
# ---------------------------------------------------------------------------

@router.get("/google/auth-url")
async def google_auth_url(
    org_id: str = Query(...),
    redirect_uri: str = Query(...),
):
    """
    Return the Google OAuth2 authorization URL.

    Configure GOOGLE_CLIENT_ID in .env. The frontend should redirect the user
    to the returned URL. After consent, Google redirects back to redirect_uri
    with a `code` query param — pass it to /calendar/google/callback.
    """
    try:
        from ...config import get_settings
        settings = get_settings()
        client_id = settings.google_client_id
        if not client_id:
            raise HTTPException(
                status_code=503,
                detail="Google OAuth not configured — set GOOGLE_CLIENT_ID in .env",
            )
        scopes = "https://www.googleapis.com/auth/calendar"
        url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
            f"&access_type=offline"
            f"&prompt=consent"
            f"&state={org_id}"
        )
        return {"url": url}
    except ImportError:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")


@router.post("/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    org_id: str = Query(...),
    redirect_uri: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange Google OAuth code for tokens and store them in the credential table.

    Requires GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET in .env.
    After this call, the user can call /calendar/google/calendars to list
    their calendars and then POST /calendar/selected-calendars to link one.
    """
    try:
        from ...config import get_settings
        import httpx
        settings = get_settings()
        if not settings.google_client_id or not settings.google_client_secret:
            raise HTTPException(
                status_code=503,
                detail="Google OAuth not configured",
            )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google token exchange failed")
        tokens = resp.json()
        # Store in credential table
        from ...db.database import utc_now_ms, generate_uuid
        from ...db.models import Credential
        expires_at = utc_now_ms() + int(tokens.get("expires_in", 3600)) * 1000
        credential = Credential(
            id=generate_uuid(),
            org_id=org_id,
            type="google_calendar",
            access_token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            expires_at=expires_at,
        )
        db.add(credential)
        await db.flush()
        return {"credential_id": credential.id, "message": "Google calendar connected"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/google/calendars")
async def list_google_calendars(
    credential_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the list of Google calendars for a connected credential.

    Requires google-api-python-client: `uv add google-api-python-client`.
    Returns calendars the user can write new events to.
    """
    from sqlalchemy import select
    from ...db.models import Credential
    result = await db.execute(select(Credential).where(Credential.id == credential_id))
    credential = result.scalar_one_or_none()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    try:
        from ...config import get_settings
        import httpx
        settings = get_settings()
        access_token = await _get_valid_access_token(credential, db, settings)
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/calendar/v3/users/me/calendarList",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Google API error")
        items = resp.json().get("items", [])
        return [
            {
                "id": c["id"],
                "name": c.get("summary", ""),
                "primary": c.get("primary", False),
                "access_role": c.get("accessRole", ""),
            }
            for c in items
        ]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Google incremental sync (pull changes back into DB)
# ---------------------------------------------------------------------------

@router.post("/google/sync")
async def sync_google_calendar(
    selected_calendar_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    repo: SelectedCalendarRepository = Depends(get_calendar_repo),
):
    """
    Pull delta changes from Google back into the appointment table.

    Uses the stored next_async_token for incremental sync:
    - Only changed events since the last sync are returned
    - Cancelled Google events → soft-delete the matching appointment
    - Updated events → update appointment fields using extendedProperties.private
    """
    cal = await repo.get_by_id(selected_calendar_id)
    if not cal:
        raise HTTPException(status_code=404, detail="Selected calendar not found")

    if not cal.get("credential_id"):
        raise HTTPException(status_code=400, detail="No credential linked to this calendar")

    from sqlalchemy import select as sa_select
    from ...db.models import Credential, Appointment
    from ...db.database import utc_now_ms
    from ...config import get_settings
    import httpx

    result = await db.execute(
        sa_select(Credential).where(Credential.id == cal["credential_id"])
    )
    credential = result.scalar_one_or_none()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    settings = get_settings()
    access_token = await _get_valid_access_token(credential, db, settings)
    calendar_id = cal.get("calendar_id", "primary")
    sync_token = cal.get("next_async_token")

    params: dict = {"fields": "items,nextSyncToken,nextPageToken"}
    if sync_token:
        params["syncToken"] = sync_token
    else:
        # First sync — fetch last 30 days
        from datetime import datetime, timezone, timedelta
        time_min = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        params["timeMin"] = time_min

    changed_events = []
    next_sync_token = None
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            if resp.status_code == 410:
                # Sync token expired — clear it and let client retry
                await repo.update_sync_token(selected_calendar_id, "")
                return {"message": "Sync token expired, please retry", "full_sync_required": True}
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Google API error")
            data = resp.json()
            changed_events.extend(data.get("items", []))
            next_sync_token = data.get("nextSyncToken")
            page_token = data.get("nextPageToken")
            if not page_token:
                break
            params = {"pageToken": page_token}

    # Store new sync token
    if next_sync_token:
        await repo.update_sync_token(selected_calendar_id, next_sync_token)

    processed = 0
    for event in changed_events:
        ext_id = event.get("id")
        status = event.get("status")
        if status == "cancelled":
            # Soft-delete matching appointment
            appt_result = await db.execute(
                sa_select(Appointment).where(Appointment.reference_id == ext_id)
            )
            appt = appt_result.scalar_one_or_none()
            if appt and not appt.deleted_at:
                appt.deleted_at = utc_now_ms()
                processed += 1
        else:
            # Update appointment using extendedProperties.private metadata
            private = (event.get("extendedProperties") or {}).get("private", {})
            appt_id = private.get("appointmentId")
            if appt_id:
                appt_result = await db.execute(
                    sa_select(Appointment).where(Appointment.id == appt_id)
                )
                appt = appt_result.scalar_one_or_none()
                if appt:
                    if event.get("summary"):
                        appt.title = event["summary"]
                    processed += 1

    await db.flush()
    return {"message": "Sync complete", "events_processed": processed}


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _get_valid_access_token(credential, db: AsyncSession, settings) -> str:
    """Return a valid access token, refreshing via refresh_token if expired."""
    from ...db.database import utc_now_ms
    import httpx

    now = utc_now_ms()
    # Refresh if token expires within the next 5 minutes
    if credential.expires_at and credential.expires_at > now + 300_000:
        return credential.access_token

    if not credential.refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Google credential expired and no refresh token available",
        )
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": credential.refresh_token,
                "grant_type": "refresh_token",
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to refresh Google token")

    tokens = resp.json()
    credential.access_token = tokens["access_token"]
    credential.expires_at = now + int(tokens.get("expires_in", 3600)) * 1000
    await db.flush()
    return credential.access_token
