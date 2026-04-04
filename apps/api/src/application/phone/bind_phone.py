"""Phase 4 — Bind a VirtualAssistantPhone to a LiveKit agent via SIP trunks."""

from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import VirtualAssistantPhone, utc_now_ms
from ...infrastructure.livekit.sip_service import LiveKitSIPService
from ...infrastructure.twilio.service import TwilioService

logger = logging.getLogger(__name__)


class BindPhoneUseCase:
    """Creates LiveKit inbound/outbound SIP trunks and a dispatch rule.

    Idempotent — existing trunks that already cover the phone number are
    reused rather than duplicated.

    Preconditions:
      - VirtualAssistantPhone must have trunk_termination_url, sip_username, and
        sip_password set (i.e. Phase 3 must have completed).
    """

    def __init__(
        self,
        db: AsyncSession,
        livekit_sip: LiveKitSIPService,
        twilio: TwilioService,
    ) -> None:
        self._db = db
        self._livekit_sip = livekit_sip
        self._twilio = twilio

    async def execute(
        self,
        va_phone_id: int,
        record_calls: bool = False,
        recording_public: bool = False,
    ) -> None:
        """Run Phase 4 for the given VirtualAssistantPhone row."""
        result = await self._db.execute(
            select(VirtualAssistantPhone).where(VirtualAssistantPhone.id == va_phone_id)
        )
        va_phone = result.scalar_one_or_none()
        if va_phone is None:
            raise ValueError(f"VirtualAssistantPhone id={va_phone_id} not found")

        if not va_phone.trunk_termination_url or not va_phone.sip_username:
            raise ValueError(
                f"Phone {va_phone.phone_number} has not completed Phase 3 — "
                "run RegisterPhoneUseCase first"
            )

        # Idempotency: skip if LiveKit trunks already exist
        if va_phone.livekit_inbound_trunk_id and va_phone.livekit_outbound_trunk_id:
            logger.info(
                "Phone %s already bound to LiveKit — skipping Phase 4",
                va_phone.phone_number,
            )
            return

        phone_number = va_phone.phone_number
        agent_name = str(va_phone.agent_id)

        # Resolve per-org LiveKit credentials if set
        custom = va_phone.custom_credentials or {}
        livekit_sip = self._livekit_sip
        if custom.get("livekitWsUrl"):
            livekit_sip = LiveKitSIPService(
                url=custom["livekitWsUrl"],
                api_key=custom.get("livekitApiKey", ""),
                api_secret=custom.get("livekitApiSecret", ""),
            )

        # Fetch existing trunks for idempotency checks
        inbound_trunks = await livekit_sip.list_inbound_trunks()
        outbound_trunks = await livekit_sip.list_outbound_trunks()
        dispatch_rules = await livekit_sip.list_dispatch_rules()

        existing_inbound = next(
            (t for t in inbound_trunks if phone_number in list(t.numbers)), None
        )
        existing_outbound = next(
            (t for t in outbound_trunks if phone_number in list(t.numbers)), None
        )

        # Create outbound trunk (LiveKit → Twilio)
        if existing_outbound:
            outbound_id = existing_outbound.sip_trunk_id
            logger.info("Reusing existing outbound trunk %s", outbound_id)
        else:
            outbound_id = await livekit_sip.create_outbound_trunk(
                name=agent_name,
                termination_url=va_phone.trunk_termination_url,
                numbers=[phone_number],
                auth_username=va_phone.sip_username,
                auth_password=va_phone.sip_password or "",
            )
            logger.info("Created outbound trunk %s for %s", outbound_id, phone_number)

        # Create inbound trunk (Twilio → LiveKit)
        if existing_inbound:
            inbound_id = existing_inbound.sip_trunk_id
            logger.info("Reusing existing inbound trunk %s", inbound_id)
        else:
            inbound_id = await livekit_sip.create_inbound_trunk(
                name=agent_name,
                numbers=[phone_number],
                krisp_enabled=True,
            )
            logger.info("Created inbound trunk %s for %s", inbound_id, phone_number)

        # Create dispatch rule
        existing_rule = next(
            (r for r in dispatch_rules if inbound_id in list(r.trunk_ids)), None
        )
        if existing_rule:
            rule_id = existing_rule.sip_dispatch_rule_id
            logger.info("Reusing existing dispatch rule %s", rule_id)
        else:
            rule_id = await livekit_sip.create_dispatch_rule(
                phone_number=phone_number,
                inbound_trunk_id=inbound_id,
            )
            logger.info("Created dispatch rule %s for %s", rule_id, phone_number)

        # Optional: configure call recording on the trunk
        if va_phone.trunk_sid:
            await self._twilio.update_trunk_recording(va_phone.trunk_sid, record_calls)

        # Persist LiveKit IDs to DB
        await self._db.execute(
            update(VirtualAssistantPhone)
            .where(VirtualAssistantPhone.id == va_phone_id)
            .values(
                livekit_trunk_id=outbound_id,
                livekit_inbound_trunk_id=inbound_id,
                livekit_outbound_trunk_id=outbound_id,
                livekit_inbound_dispatch_rule_id=rule_id,
                status="active",
                recording_enabled=record_calls,
                recording_public=recording_public,
                updated_at=utc_now_ms(),
            )
        )
        await self._db.commit()

        logger.info(
            "Phase 4 complete for %s — inbound=%s outbound=%s rule=%s",
            phone_number,
            inbound_id,
            outbound_id,
            rule_id,
        )
