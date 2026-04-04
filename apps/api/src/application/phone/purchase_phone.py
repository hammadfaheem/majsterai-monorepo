"""Phase 1 + 2 — Purchase a Twilio phone number and assign it to an org."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import VirtualAssistantPhone, utc_now_ms
from ...infrastructure.twilio.service import TwilioService

logger = logging.getLogger(__name__)


@dataclass
class PurchasePhoneResult:
    va_phone_id: int
    phone_number: str
    twilio_sid: str


class PurchasePhoneUseCase:
    """Search available numbers, purchase one, and insert a VirtualAssistantPhone row.

    The caller is responsible for running Phase 3 (RegisterPhoneUseCase) and
    Phase 4 (BindPhoneUseCase) after this returns successfully.
    """

    def __init__(
        self,
        db: AsyncSession,
        twilio: TwilioService,
    ) -> None:
        self._db = db
        self._twilio = twilio

    async def list_available(
        self,
        country: str = "US",
        number_type: str = "local",
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        """Return available numbers from Twilio without purchasing."""
        return await self._twilio.list_available_numbers(country, number_type, limit)

    async def execute(
        self,
        phone_number: str,
        org_id: str,
        agent_id: int,
        assigned_by: str,
        bundle_sid: str | None = None,
        address_sid: str | None = None,
    ) -> PurchasePhoneResult:
        """Purchase *phone_number* and create the database record.

        Args:
            phone_number: E.164 number to purchase, e.g. "+12015551234".
            org_id: Organization that will own this number (unique — one per org).
            agent_id: Agent this number will be bound to.
            assigned_by: User ID performing the purchase.
            bundle_sid: Twilio Regulatory Bundle SID (required for AU numbers).
            address_sid: Twilio Address SID (required for AU numbers).
        """
        # Purchase from Twilio
        purchased = await self._twilio.purchase_number(
            phone_number, bundle_sid=bundle_sid, address_sid=address_sid
        )
        logger.info("Purchased Twilio number %s (SID=%s)", purchased["phone_number"], purchased["sid"])

        # Insert the database record
        va_phone = VirtualAssistantPhone(
            phone_number=purchased["phone_number"],
            twilio_sid=purchased["sid"],
            org_id=org_id,
            agent_id=agent_id,
            assigned_by=assigned_by,
            is_active=True,
            status="pending",
            created_at=utc_now_ms(),
            updated_at=utc_now_ms(),
        )
        self._db.add(va_phone)
        await self._db.flush()  # populate va_phone.id
        await self._db.commit()

        return PurchasePhoneResult(
            va_phone_id=va_phone.id,
            phone_number=va_phone.phone_number,
            twilio_sid=va_phone.twilio_sid,
        )
