"""Phase 3 — Create Twilio Elastic SIP Trunk and link it to a VirtualAssistantPhone."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import VirtualAssistantPhone, utc_now_ms
from ...infrastructure.twilio.service import TwilioService

logger = logging.getLogger(__name__)

_SLEEP_SECS = 2  # Twilio API is eventually consistent; wait before sub-resource ops


class RegisterPhoneUseCase:
    """Steps 2.1–2.7 from the developer guide.

    Creates:
      - Twilio Elastic SIP Trunk
      - SIP Credential List + credentials
      - Trunk domain (E164-digits.pstn.twilio.com)
      - Origination URL pointing at the LiveKit SIP gateway
      - Associates the IncomingPhoneNumber with the trunk

    All operations are idempotent — if *trunk_sid* is already set on the
    VirtualAssistantPhone record this use case is a no-op.
    """

    def __init__(
        self,
        db: AsyncSession,
        twilio: TwilioService,
        livekit_sip_domain: str,
    ) -> None:
        self._db = db
        self._twilio = twilio
        self._livekit_sip_domain = livekit_sip_domain

    async def execute(self, va_phone_id: int) -> None:
        """Run Phase 3 for the given VirtualAssistantPhone row."""
        result = await self._db.execute(
            select(VirtualAssistantPhone).where(VirtualAssistantPhone.id == va_phone_id)
        )
        va_phone = result.scalar_one_or_none()
        if va_phone is None:
            raise ValueError(f"VirtualAssistantPhone id={va_phone_id} not found")

        # Idempotency: skip if already registered
        if va_phone.trunk_sid:
            logger.info(
                "Phone %s already has trunk_sid=%s — skipping Phase 3",
                va_phone.phone_number,
                va_phone.trunk_sid,
            )
            return

        phone_number = va_phone.phone_number
        sanitized = TwilioService.sanitize_phone(phone_number)  # digits only

        # Step 2.1 — Create Elastic SIP Trunk
        logger.info("Creating SIP trunk for %s", phone_number)
        trunk_sid = await self._twilio.create_sip_trunk(phone_number)
        await asyncio.sleep(_SLEEP_SECS)

        # Step 2.2 — Create / retrieve credential list
        logger.info("Creating credential list for %s", phone_number)
        credential_list_sid = await self._twilio.create_credential_list(phone_number)
        await asyncio.sleep(_SLEEP_SECS)

        # Step 2.3 — Attach credential list to trunk
        await self._twilio.attach_credential_list(trunk_sid, credential_list_sid)

        # Step 2.4 — Create / rotate SIP credentials
        username = f"external-{sanitized}"
        password = TwilioService.generate_sip_password()
        await self._twilio.create_or_rotate_credentials(
            credential_list_sid, username, password
        )

        # Step 2.5 — Set trunk domain
        await self._twilio.update_trunk_domain(trunk_sid, sanitized)

        # Step 2.6 — Add origination URL (Twilio → LiveKit)
        await self._twilio.add_origination_url(
            trunk_sid, self._livekit_sip_domain, phone_number
        )

        # Step 2.6.5 — Associate IncomingPhoneNumber with trunk
        await self._twilio.associate_number_with_trunk(phone_number, trunk_sid)

        # Step 2.7 — Persist to DB
        await self._db.execute(
            update(VirtualAssistantPhone)
            .where(VirtualAssistantPhone.id == va_phone_id)
            .values(
                type="external",
                status="pending",
                trunk_sid=trunk_sid,
                sip_username=username,
                sip_password=password,
                credential_list_sid=credential_list_sid,
                trunk_termination_url=f"{sanitized}.pstn.twilio.com",
                updated_at=utc_now_ms(),
            )
        )
        await self._db.commit()

        logger.info(
            "Phase 3 complete for %s — trunk_sid=%s, termination=%s.pstn.twilio.com",
            phone_number,
            trunk_sid,
            sanitized,
        )
