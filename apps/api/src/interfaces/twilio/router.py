"""Twilio phone provisioning, SIP trunking, and webhook endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.phone.bind_phone import BindPhoneUseCase
from ...application.phone.purchase_phone import PurchasePhoneUseCase
from ...application.phone.register_phone import RegisterPhoneUseCase
from ...application.phone.release_phone import ReleasePhoneUseCase
from ...config import get_settings
from ...db.database import get_db
from ...db.models import VirtualAssistantPhone
from ...infrastructure.livekit.service import LiveKitService
from ...infrastructure.livekit.sip_service import LiveKitSIPService
from ...infrastructure.twilio.service import TwilioService

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# ---------------------------------------------------------------------------
# Shared dependencies
# ---------------------------------------------------------------------------


def get_twilio() -> TwilioService:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        raise HTTPException(
            status_code=503,
            detail="Twilio credentials are not configured on this server",
        )
    return TwilioService(settings.twilio_account_sid, settings.twilio_auth_token)


def get_livekit_sip() -> LiveKitSIPService:
    return LiveKitSIPService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )


def get_livekit_service() -> LiveKitService:
    return LiveKitService(
        url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class ListNumbersRequest(BaseModel):
    country: str = "US"
    number_type: str = "local"  # "local" or "mobile"
    limit: int = 15


class PurchaseNumberRequest(BaseModel):
    phone_number: str
    org_id: str
    agent_id: int
    assigned_by: str
    bundle_sid: str | None = None
    address_sid: str | None = None


class PurchaseNumberResponse(BaseModel):
    va_phone_id: int
    phone_number: str
    twilio_sid: str


class RegisterPhoneRequest(BaseModel):
    va_phone_id: int


class BindPhoneRequest(BaseModel):
    record_calls: bool = False
    recording_public: bool = False


class ReleasePhoneRequest(BaseModel):
    release_twilio_number: bool = False


class PhoneStatusResponse(BaseModel):
    id: int
    phone_number: str
    twilio_sid: str
    org_id: str
    agent_id: int
    status: str
    type: str | None
    trunk_sid: str | None
    trunk_termination_url: str | None
    livekit_inbound_trunk_id: str | None
    livekit_outbound_trunk_id: str | None
    livekit_inbound_dispatch_rule_id: str | None
    recording_enabled: bool
    is_active: bool
    created_at: int
    updated_at: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Phase 1 — Number discovery
# ---------------------------------------------------------------------------


@router.get("/numbers/available")
async def list_available_numbers(
    country: str = "US",
    number_type: str = "local",
    limit: int = 15,
    twilio: TwilioService = Depends(get_twilio),
) -> list[dict[str, Any]]:
    """Return available Twilio phone numbers for purchase."""
    return await twilio.list_available_numbers(country, number_type, limit)


# ---------------------------------------------------------------------------
# Phase 1+2 — Purchase and assign
# ---------------------------------------------------------------------------


@router.post("/numbers/purchase", response_model=PurchaseNumberResponse)
async def purchase_number(
    data: PurchaseNumberRequest,
    db: AsyncSession = Depends(get_db),
    twilio: TwilioService = Depends(get_twilio),
) -> PurchaseNumberResponse:
    """Purchase a phone number from Twilio and create a VirtualAssistantPhone record.

    Run ``POST /api/twilio/register-phone-number`` next to set up the SIP trunk.
    """
    use_case = PurchasePhoneUseCase(db=db, twilio=twilio)
    result = await use_case.execute(
        phone_number=data.phone_number,
        org_id=data.org_id,
        agent_id=data.agent_id,
        assigned_by=data.assigned_by,
        bundle_sid=data.bundle_sid,
        address_sid=data.address_sid,
    )
    return PurchaseNumberResponse(
        va_phone_id=result.va_phone_id,
        phone_number=result.phone_number,
        twilio_sid=result.twilio_sid,
    )


# ---------------------------------------------------------------------------
# Phase 3 — SIP Trunk registration
# ---------------------------------------------------------------------------


@router.post("/register-phone-number")
async def register_phone_number(
    data: RegisterPhoneRequest,
    db: AsyncSession = Depends(get_db),
    twilio: TwilioService = Depends(get_twilio),
) -> dict[str, str]:
    """Create the Twilio Elastic SIP Trunk for an existing VirtualAssistantPhone.

    Idempotent — safe to call multiple times.
    """
    use_case = RegisterPhoneUseCase(
        db=db,
        twilio=twilio,
        livekit_sip_domain=settings.livekit_sip_domain,
    )
    try:
        await use_case.execute(va_phone_id=data.va_phone_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "message": "SIP trunk registered"}


# ---------------------------------------------------------------------------
# Phase 4 — LiveKit SIP binding
# ---------------------------------------------------------------------------


@router.post("/{va_phone_id}/bind/{agent_id}")
async def bind_phone(
    va_phone_id: int,
    agent_id: int,  # path param kept for REST semantics; use_case reads agent_id from DB
    data: BindPhoneRequest,
    db: AsyncSession = Depends(get_db),
    twilio: TwilioService = Depends(get_twilio),
    livekit_sip: LiveKitSIPService = Depends(get_livekit_sip),
) -> dict[str, str]:
    """Create LiveKit SIP trunks and dispatch rule, set status=active.

    Precondition: Phase 3 must have completed successfully for this phone.
    """
    _ = agent_id  # validated by path; the use case reads agent_id from the DB record
    use_case = BindPhoneUseCase(db=db, livekit_sip=livekit_sip, twilio=twilio)
    try:
        await use_case.execute(
            va_phone_id=va_phone_id,
            record_calls=data.record_calls,
            recording_public=data.recording_public,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "message": "Phone bound to LiveKit agent"}


# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------


@router.post("/{va_phone_id}/release")
async def release_phone(
    va_phone_id: int,
    data: ReleasePhoneRequest,
    db: AsyncSession = Depends(get_db),
    twilio: TwilioService = Depends(get_twilio),
    livekit_sip: LiveKitSIPService = Depends(get_livekit_sip),
) -> dict[str, str]:
    """Tear down SIP trunk and LiveKit resources.

    The Twilio phone number is retained (and billed) unless
    ``release_twilio_number=true`` is sent in the body.
    """
    use_case = ReleasePhoneUseCase(db=db, twilio=twilio, livekit_sip=livekit_sip)
    try:
        await use_case.execute(
            va_phone_id=va_phone_id,
            release_twilio_number=data.release_twilio_number,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "message": "SIP resources released"}


# ---------------------------------------------------------------------------
# Read — phone status
# ---------------------------------------------------------------------------


@router.get("/{va_phone_id}", response_model=PhoneStatusResponse)
async def get_phone(
    va_phone_id: int,
    db: AsyncSession = Depends(get_db),
) -> VirtualAssistantPhone:
    """Return current SIP/LiveKit status for a VirtualAssistantPhone."""
    result = await db.execute(
        select(VirtualAssistantPhone).where(VirtualAssistantPhone.id == va_phone_id)
    )
    va_phone = result.scalar_one_or_none()
    if va_phone is None:
        raise HTTPException(status_code=404, detail="VirtualAssistantPhone not found")
    return va_phone


# ---------------------------------------------------------------------------
# Twilio Webhook — inbound voice call → TwiML
# ---------------------------------------------------------------------------


@router.post("/voice/incoming")
async def incoming_voice(
    request: Request,
    db: AsyncSession = Depends(get_db),
    livekit_service: LiveKitService = Depends(get_livekit_service),
) -> Response:
    """Twilio webhook for inbound PSTN calls.

    Returns TwiML instructing Twilio to connect the call via SIP to a
    LiveKit room, where the AI agent is waiting.

    Expected form fields: To, From, CallSid
    """
    form = await request.form()
    to_number: str = str(form.get("To", ""))
    from_number: str = str(form.get("From", ""))
    call_sid: str = str(form.get("CallSid", ""))

    if not to_number:
        return PlainTextResponse(
            "<?xml version='1.0' encoding='UTF-8'?><Response><Reject/></Response>",
            media_type="text/xml",
            status_code=400,
        )

    # Look up the VA phone record
    result = await db.execute(
        select(VirtualAssistantPhone).where(
            VirtualAssistantPhone.phone_number == to_number,
            VirtualAssistantPhone.is_active == True,  # noqa: E712
        )
    )
    va_phone = result.scalar_one_or_none()

    if va_phone is None:
        logger.warning("Inbound call to %s — no active VirtualAssistantPhone found", to_number)
        return PlainTextResponse(
            "<?xml version='1.0' encoding='UTF-8'?>"
            "<Response><Say>This number is not currently in service.</Say></Response>",
            media_type="text/xml",
        )

    # Build a unique room name: call-{digits}-{CallSid}
    digits = to_number.lstrip("+")
    room_name = f"call-{digits}-{call_sid}"

    # Create the LiveKit room with agent context in metadata
    metadata: dict[str, Any] = {
        "type": "sip",
        "mode": "voice",
        "org_id": va_phone.org_id,
        "agent_id": va_phone.agent_id,
        "from_number": from_number,
        "to_number": to_number,
        "call_sid": call_sid,
    }
    try:
        await livekit_service.create_room(room_name, metadata=metadata)
    except Exception:
        logger.exception("Failed to create LiveKit room %s", room_name)

    # Resolve LiveKit SIP domain (per-org overrides supported)
    custom = va_phone.custom_credentials or {}
    livekit_sip_domain = custom.get("livekitSipDomain") or settings.livekit_sip_domain

    # Return TwiML: dial the LiveKit SIP gateway
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        "<Dial>"
        f'<Sip>sip:{room_name}@{livekit_sip_domain}</Sip>'
        "</Dial>"
        "</Response>"
    )

    logger.info(
        "Routing call %s from %s to LiveKit room %s via %s",
        call_sid,
        from_number,
        room_name,
        livekit_sip_domain,
    )

    return Response(content=twiml, media_type="text/xml")


# ---------------------------------------------------------------------------
# Twilio Webhook — inbound SMS
# ---------------------------------------------------------------------------


@router.post("/sms/incoming")
async def incoming_sms(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Twilio webhook for inbound SMS messages.

    Validates the Twilio request signature before processing.
    Returns a 204 (no content) after queuing the message for processing.
    """
    form = await request.form()
    params = {k: str(v) for k, v in form.items()}

    # Signature validation
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    if settings.twilio_auth_token and not TwilioService.validate_signature(
        settings.twilio_auth_token, signature, url, params
    ):
        logger.warning("Invalid Twilio signature on SMS webhook from %s", request.client)
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    from_number = params.get("From", "")
    to_number = params.get("To", "")
    body = params.get("Body", "")

    logger.info("Inbound SMS from %s to %s: %s", from_number, to_number, body[:100])

    # Look up the VA phone record
    result = await db.execute(
        select(VirtualAssistantPhone).where(
            VirtualAssistantPhone.phone_number == to_number,
            VirtualAssistantPhone.is_active == True,  # noqa: E712
        )
    )
    va_phone = result.scalar_one_or_none()

    if va_phone and not va_phone.is_sms_listening:
        logger.info("SMS received for %s but is_sms_listening=False — ignoring", to_number)

    # Return empty TwiML so Twilio doesn't auto-reply with an error
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="text/xml",
    )
