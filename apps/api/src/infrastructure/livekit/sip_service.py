"""LiveKit SIP service — inbound/outbound trunks and dispatch rules."""

import logging

import aiohttp
from livekit import api as lkapi

logger = logging.getLogger(__name__)


class LiveKitSIPService:
    """Async wrapper for LiveKit SIP operations."""

    def __init__(self, url: str, api_key: str, api_secret: str) -> None:
        # LiveKit HTTP URL (convert wss:// to https://)
        self._url = url.replace("wss://", "https://").replace("ws://", "http://")
        self._api_key = api_key
        self._api_secret = api_secret

    # ------------------------------------------------------------------
    # Listing helpers
    # ------------------------------------------------------------------

    async def list_inbound_trunks(self) -> list[lkapi.SIPInboundTrunkInfo]:
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            resp = await svc.list_sip_inbound_trunk(lkapi.ListSIPInboundTrunkRequest())
        return list(resp.items)

    async def list_outbound_trunks(self) -> list[lkapi.SIPOutboundTrunkInfo]:
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            resp = await svc.list_sip_outbound_trunk(lkapi.ListSIPOutboundTrunkRequest())
        return list(resp.items)

    async def list_dispatch_rules(self) -> list[lkapi.SIPDispatchRuleInfo]:
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            resp = await svc.list_sip_dispatch_rule(lkapi.ListSIPDispatchRuleRequest())
        return list(resp.items)

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    async def create_outbound_trunk(
        self,
        name: str,
        termination_url: str,
        numbers: list[str],
        auth_username: str,
        auth_password: str,
    ) -> str:
        """Create a LiveKit outbound SIP trunk (LiveKit → Twilio). Returns trunk SID."""
        trunk = lkapi.SIPOutboundTrunkInfo(
            name=name,
            address=termination_url,
            numbers=numbers,
            auth_username=auth_username,
            auth_password=auth_password,
            transport=lkapi.SIP_TRANSPORT_AUTO,
        )
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            result = await svc.create_sip_outbound_trunk(
                lkapi.CreateSIPOutboundTrunkRequest(trunk=trunk)
            )
        return result.sip_trunk_id

    async def create_inbound_trunk(
        self,
        name: str,
        numbers: list[str],
        krisp_enabled: bool = True,
    ) -> str:
        """Create a LiveKit inbound SIP trunk (Twilio → LiveKit). Returns trunk SID."""
        trunk = lkapi.SIPInboundTrunkInfo(
            name=name,
            numbers=numbers,
            krisp_enabled=krisp_enabled,
        )
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            result = await svc.create_sip_inbound_trunk(
                lkapi.CreateSIPInboundTrunkRequest(trunk=trunk)
            )
        return result.sip_trunk_id

    async def create_dispatch_rule(
        self,
        phone_number: str,
        inbound_trunk_id: str,
    ) -> str:
        """Create a dispatch rule routing inbound calls to per-call rooms.

        Each inbound call gets its own room named:
          call-{digits}-{LiveKit-assigned-suffix}
        """
        digits = phone_number.lstrip("+")
        rule = lkapi.SIPDispatchRule(
            dispatch_rule_individual=lkapi.SIPDispatchRuleIndividual(
                room_prefix=f"call-{digits}",
            )
        )
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            result = await svc.create_sip_dispatch_rule(
                lkapi.CreateSIPDispatchRuleRequest(
                    rule=rule,
                    trunk_ids=[inbound_trunk_id],
                    name="Twilio-inbound-dispatch",
                )
            )
        return result.sip_dispatch_rule_id

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    async def delete_trunk(self, trunk_id: str) -> None:
        """Delete an inbound or outbound SIP trunk."""
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            await svc.delete_sip_trunk(lkapi.DeleteSIPTrunkRequest(sip_trunk_id=trunk_id))

    async def delete_dispatch_rule(self, rule_id: str) -> None:
        """Delete a SIP dispatch rule."""
        async with aiohttp.ClientSession() as session:
            svc = lkapi.sip_service.SipService(
                session, self._url, self._api_key, self._api_secret
            )
            await svc.delete_sip_dispatch_rule(
                lkapi.DeleteSIPDispatchRuleRequest(sip_dispatch_rule_id=rule_id)
            )
