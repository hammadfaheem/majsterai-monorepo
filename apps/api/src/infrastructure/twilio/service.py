"""Twilio REST API service using httpx (no Twilio SDK required)."""

import base64
import hashlib
import hmac
import logging
import re
import secrets
from typing import Any
import httpx

logger = logging.getLogger(__name__)

_TWILIO_BASE = "https://api.twilio.com/2010-04-01/Accounts"
_TWILIO_TRUNKING_BASE = "https://trunking.twilio.com/v1"
_TWILIO_SIP_BASE = "https://api.twilio.com/2010-04-01/Accounts"


class TwilioService:
    """Thin async wrapper around the Twilio REST API using httpx."""

    def __init__(self, account_sid: str, auth_token: str) -> None:
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._auth = base64.b64encode(
            f"{account_sid}:{auth_token}".encode()
        ).decode()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Basic {self._auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    async def _post(self, url: str, data: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self._headers(), data=data)
            resp.raise_for_status()
            return resp.json()

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    async def _delete(self, url: str) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(url, headers=self._headers())
            if resp.status_code not in (200, 204):
                resp.raise_for_status()

    # ------------------------------------------------------------------
    # Phase 1 — Number discovery & purchase
    # ------------------------------------------------------------------

    async def list_available_numbers(
        self,
        country: str = "US",
        number_type: str = "local",
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        """Return available phone numbers for purchase."""
        url = (
            f"{_TWILIO_BASE}/{self._account_sid}"
            f"/AvailablePhoneNumbers/{country}/{number_type.capitalize()}.json"
        )
        data = await self._get(
            url,
            params={
                "VoiceEnabled": "true",
                "SmsEnabled": "true",
                "MmsEnabled": "true",
                "Limit": str(limit),
            },
        )
        numbers = data.get("available_phone_numbers", [])
        # Normalise capabilities (Twilio SDK bug: SMS/MMS keyed as MMS in raw response)
        for n in numbers:
            caps = n.get("capabilities", {})
            caps.setdefault("sms", caps.get("SMS", caps.get("MMS", False)))
            caps.setdefault("mms", caps.get("MMS", False))
        return numbers

    async def get_pricing(self, country: str = "US") -> dict[str, Any]:
        """Fetch phone number pricing for a country."""
        url = f"https://pricing.twilio.com/v1/PhoneNumbers/Countries/{country}"
        return await self._get(url)

    async def purchase_number(
        self,
        phone_number: str,
        bundle_sid: str | None = None,
        address_sid: str | None = None,
    ) -> dict[str, str]:
        """Purchase a phone number. Returns {sid, phone_number}."""
        url = f"{_TWILIO_BASE}/{self._account_sid}/IncomingPhoneNumbers.json"
        params: dict[str, str] = {"PhoneNumber": phone_number}
        if bundle_sid:
            params["BundleSid"] = bundle_sid
        if address_sid:
            params["AddressSid"] = address_sid

        data = await self._post(url, params)
        return {"sid": data["sid"], "phone_number": data["phone_number"]}

    # ------------------------------------------------------------------
    # Phase 3 — SIP Trunk registration
    # ------------------------------------------------------------------

    async def create_sip_trunk(self, phone_number: str) -> str:
        """Create a Twilio Elastic SIP Trunk. Returns trunk SID."""
        url = f"{_TWILIO_TRUNKING_BASE}/Trunks"
        data = await self._post(
            url,
            {
                "FriendlyName": f"external-{phone_number}-{secrets.token_hex(4)}",
            },
        )
        return data["sid"]

    async def create_credential_list(self, phone_number: str) -> str:
        """Create a SIP credential list. Returns its SID.

        Idempotent: returns existing list SID if one already exists for this number.
        """
        friendly_name = f"external-{phone_number}-creds"
        existing = await self._get(
            f"{_TWILIO_BASE}/{self._account_sid}/SIP/CredentialLists.json",
            params={"FriendlyName": friendly_name},
        )
        items = existing.get("credential_lists", [])
        if items:
            return items[0]["sid"]

        data = await self._post(
            f"{_TWILIO_BASE}/{self._account_sid}/SIP/CredentialLists.json",
            {"FriendlyName": friendly_name},
        )
        return data["sid"]

    async def attach_credential_list(
        self, trunk_sid: str, credential_list_sid: str
    ) -> None:
        """Attach a SIP credential list to a trunk."""
        await self._post(
            f"{_TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}/CredentialLists",
            {"CredentialListSid": credential_list_sid},
        )

    @staticmethod
    def generate_sip_password() -> str:
        """Generate a SIP password satisfying Twilio complexity requirements.

        Format: {8 hex bytes}Aa1{4 hex bytes} — provides digits + uppercase + lowercase.
        """
        return f"{secrets.token_hex(8)}Aa1{secrets.token_hex(4)}"

    async def create_or_rotate_credentials(
        self,
        credential_list_sid: str,
        username: str,
        password: str,
    ) -> None:
        """Create SIP credentials, or rotate the password if they already exist."""
        existing = await self._get(
            f"{_TWILIO_BASE}/{self._account_sid}"
            f"/SIP/CredentialLists/{credential_list_sid}/Credentials.json"
        )
        creds = existing.get("credentials", [])
        found = next((c for c in creds if c["username"] == username), None)

        if found:
            await self._post(
                f"{_TWILIO_BASE}/{self._account_sid}"
                f"/SIP/CredentialLists/{credential_list_sid}/Credentials/{found['sid']}.json",
                {"Password": password},
            )
        else:
            await self._post(
                f"{_TWILIO_BASE}/{self._account_sid}"
                f"/SIP/CredentialLists/{credential_list_sid}/Credentials.json",
                {"Username": username, "Password": password},
            )

    async def update_trunk_domain(self, trunk_sid: str, sanitized_phone: str) -> None:
        """Set the trunk's termination domain to {digits}.pstn.twilio.com.

        If the domain is already taken (HTTP 400), logs a warning and continues.
        """
        try:
            await self._post(
                f"{_TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}",
                {
                    "DomainName": f"{sanitized_phone}.pstn.twilio.com",
                    "Secure": "false",
                    "TransferMode": "enable-all",
                    "TransferCallerId": "from-transferee",
                },
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 400:
                logger.warning(
                    "Trunk domain %s.pstn.twilio.com already exists — skipping domain update",
                    sanitized_phone,
                )
            else:
                raise

    async def add_origination_url(
        self, trunk_sid: str, livekit_sip_domain: str, phone_number: str
    ) -> None:
        """Point trunk origination to the LiveKit SIP gateway."""
        await self._post(
            f"{_TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}/OriginationUrls",
            {
                "Weight": "1",
                "Priority": "1",
                "SipUrl": f"sip:{livekit_sip_domain}",
                "Enabled": "true",
                "FriendlyName": f"external-{phone_number}-origination",
            },
        )

    async def associate_number_with_trunk(
        self, phone_number: str, trunk_sid: str
    ) -> None:
        """Link the Twilio IncomingPhoneNumber to the SIP trunk."""
        existing = await self._get(
            f"{_TWILIO_BASE}/{self._account_sid}/IncomingPhoneNumbers.json",
            params={"PhoneNumber": phone_number},
        )
        numbers = existing.get("incoming_phone_numbers", [])
        if not numbers:
            raise ValueError(f"Phone number {phone_number} not found in Twilio account")

        await self._post(
            f"{_TWILIO_BASE}/{self._account_sid}"
            f"/IncomingPhoneNumbers/{numbers[0]['sid']}.json",
            {"TrunkSid": trunk_sid},
        )

    async def update_sms_webhook(self, twilio_sid: str, sms_url: str) -> None:
        """Set the inbound SMS webhook URL on the phone number."""
        await self._post(
            f"{_TWILIO_BASE}/{self._account_sid}/IncomingPhoneNumbers/{twilio_sid}.json",
            {"SmsUrl": sms_url, "SmsMethod": "POST"},
        )

    # ------------------------------------------------------------------
    # Phase 3 — Recording
    # ------------------------------------------------------------------

    async def update_trunk_recording(
        self, trunk_sid: str, record_calls: bool
    ) -> None:
        """Configure call recording mode on the SIP trunk."""
        payload: dict[str, str] = {
            "Mode": "record-from-ringing" if record_calls else "do-not-record",
        }
        if record_calls:
            payload["Trim"] = "do-not-trim"
        await self._post(
            f"{_TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}/Recording",
            payload,
        )

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------

    async def remove_trunk(self, trunk_sid: str) -> None:
        """Delete the Elastic SIP Trunk."""
        await self._delete(f"{_TWILIO_TRUNKING_BASE}/Trunks/{trunk_sid}")

    async def remove_credentials_from_list(
        self, credential_list_sid: str, username: str
    ) -> None:
        """Delete a specific credential from a credential list."""
        existing = await self._get(
            f"{_TWILIO_BASE}/{self._account_sid}"
            f"/SIP/CredentialLists/{credential_list_sid}/Credentials.json"
        )
        creds = existing.get("credentials", [])
        found = next((c for c in creds if c["username"] == username), None)
        if found:
            await self._delete(
                f"{_TWILIO_BASE}/{self._account_sid}"
                f"/SIP/CredentialLists/{credential_list_sid}/Credentials/{found['sid']}.json"
            )

    async def remove_credential_list(self, credential_list_sid: str) -> None:
        """Delete the entire SIP credential list."""
        await self._delete(
            f"{_TWILIO_BASE}/{self._account_sid}"
            f"/SIP/CredentialLists/{credential_list_sid}.json"
        )

    async def release_number(self, twilio_sid: str) -> None:
        """Release (delete) the Twilio phone number from the account."""
        await self._delete(
            f"{_TWILIO_BASE}/{self._account_sid}/IncomingPhoneNumbers/{twilio_sid}.json"
        )

    # ------------------------------------------------------------------
    # Webhook signature validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_signature(
        auth_token: str,
        signature: str,
        url: str,
        params: dict[str, str],
    ) -> bool:
        """Validate an incoming Twilio webhook request signature (HMAC-SHA1).

        Algorithm:
        1. Sort POST params alphabetically and append key+value pairs to the URL.
        2. Compute HMAC-SHA1 of the result using auth_token as the key.
        3. Compare (constant-time) with the X-Twilio-Signature header.
        """
        # Build the signed string: URL + sorted param key-value pairs
        sorted_params = sorted(params.items())
        s = url + "".join(k + v for k, v in sorted_params)

        mac = hmac.new(auth_token.encode("utf-8"), s.encode("utf-8"), hashlib.sha1)
        expected = base64.b64encode(mac.digest()).decode()
        return hmac.compare_digest(expected, signature)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def sanitize_phone(phone_number: str) -> str:
        """Strip all non-digit characters from a phone number string."""
        return re.sub(r"[^0-9]", "", phone_number)
