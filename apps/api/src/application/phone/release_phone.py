"""Teardown — Remove SIP/LiveKit resources without releasing the Twilio number itself."""

from __future__ import annotations

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import VirtualAssistantPhone, utc_now_ms
from ...infrastructure.livekit.sip_service import LiveKitSIPService
from ...infrastructure.twilio.service import TwilioService

logger = logging.getLogger(__name__)


class ReleasePhoneUseCase:
    """Tears down the SIP trunk and LiveKit resources for a VirtualAssistantPhone.

    The Twilio phone number itself is NOT released — the org continues to pay
    for it unless ``release_twilio_number=True`` is passed.

    Teardown order:
      1. Delete Twilio SIP trunk (disconnects PSTN routing)
      2. Delete SIP credentials from credential list
      3. Delete credential list
      4. Delete LiveKit outbound trunk
      5. Delete LiveKit inbound trunk
      6. Delete LiveKit dispatch rule
      7. Clear SIP/LiveKit fields in DB
      8. (Optional) Release the Twilio phone number
    """

    def __init__(
        self,
        db: AsyncSession,
        twilio: TwilioService,
        livekit_sip: LiveKitSIPService,
    ) -> None:
        self._db = db
        self._twilio = twilio
        self._livekit_sip = livekit_sip

    async def execute(
        self,
        va_phone_id: int,
        release_twilio_number: bool = False,
    ) -> None:
        """Tear down all SIP/LiveKit resources for the given phone record."""
        result = await self._db.execute(
            select(VirtualAssistantPhone).where(VirtualAssistantPhone.id == va_phone_id)
        )
        va_phone = result.scalar_one_or_none()
        if va_phone is None:
            raise ValueError(f"VirtualAssistantPhone id={va_phone_id} not found")

        # 1. Delete Twilio SIP trunk
        if va_phone.trunk_sid:
            try:
                await self._twilio.remove_trunk(va_phone.trunk_sid)
                logger.info("Deleted Twilio trunk %s", va_phone.trunk_sid)
            except Exception:
                logger.exception("Failed to delete Twilio trunk %s", va_phone.trunk_sid)

        # 2+3. Delete SIP credentials + credential list
        if va_phone.credential_list_sid:
            if va_phone.sip_username:
                try:
                    await self._twilio.remove_credentials_from_list(
                        va_phone.credential_list_sid, va_phone.sip_username
                    )
                except Exception:
                    logger.exception(
                        "Failed to delete SIP credential %s", va_phone.sip_username
                    )
            try:
                await self._twilio.remove_credential_list(va_phone.credential_list_sid)
                logger.info("Deleted credential list %s", va_phone.credential_list_sid)
            except Exception:
                logger.exception(
                    "Failed to delete credential list %s", va_phone.credential_list_sid
                )

        # Resolve custom LiveKit credentials if needed
        custom = va_phone.custom_credentials or {}
        livekit_sip = self._livekit_sip
        if custom.get("livekitWsUrl"):
            livekit_sip = LiveKitSIPService(
                url=custom["livekitWsUrl"],
                api_key=custom.get("livekitApiKey", ""),
                api_secret=custom.get("livekitApiSecret", ""),
            )

        # 4. Delete LiveKit outbound trunk
        if va_phone.livekit_outbound_trunk_id:
            try:
                await livekit_sip.delete_trunk(va_phone.livekit_outbound_trunk_id)
                logger.info("Deleted LiveKit outbound trunk %s", va_phone.livekit_outbound_trunk_id)
            except Exception:
                logger.exception(
                    "Failed to delete LiveKit outbound trunk %s",
                    va_phone.livekit_outbound_trunk_id,
                )

        # 5. Delete LiveKit inbound trunk (skip if same as outbound — shouldn't happen)
        if va_phone.livekit_inbound_trunk_id and (
            va_phone.livekit_inbound_trunk_id != va_phone.livekit_outbound_trunk_id
        ):
            try:
                await livekit_sip.delete_trunk(va_phone.livekit_inbound_trunk_id)
                logger.info("Deleted LiveKit inbound trunk %s", va_phone.livekit_inbound_trunk_id)
            except Exception:
                logger.exception(
                    "Failed to delete LiveKit inbound trunk %s",
                    va_phone.livekit_inbound_trunk_id,
                )

        # 6. Delete LiveKit dispatch rule
        if va_phone.livekit_inbound_dispatch_rule_id:
            try:
                await livekit_sip.delete_dispatch_rule(va_phone.livekit_inbound_dispatch_rule_id)
                logger.info(
                    "Deleted LiveKit dispatch rule %s", va_phone.livekit_inbound_dispatch_rule_id
                )
            except Exception:
                logger.exception(
                    "Failed to delete dispatch rule %s",
                    va_phone.livekit_inbound_dispatch_rule_id,
                )

        # 7. Clear SIP/LiveKit fields in DB
        await self._db.execute(
            update(VirtualAssistantPhone)
            .where(VirtualAssistantPhone.id == va_phone_id)
            .values(
                type=None,
                status="pending",
                trunk_sid=None,
                sip_domain=None,
                sip_username=None,
                sip_password=None,
                credential_list_sid=None,
                trunk_termination_url=None,
                livekit_trunk_id=None,
                livekit_inbound_trunk_id=None,
                livekit_outbound_trunk_id=None,
                livekit_inbound_dispatch_rule_id=None,
                updated_at=utc_now_ms(),
            )
        )
        await self._db.commit()

        # 8. Optionally release the Twilio phone number
        if release_twilio_number and va_phone.twilio_sid:
            try:
                await self._twilio.release_number(va_phone.twilio_sid)
                logger.info(
                    "Released Twilio number %s (SID=%s)",
                    va_phone.phone_number,
                    va_phone.twilio_sid,
                )
            except Exception:
                logger.exception(
                    "Failed to release Twilio number %s", va_phone.twilio_sid
                )

        logger.info("Teardown complete for VirtualAssistantPhone id=%s", va_phone_id)
