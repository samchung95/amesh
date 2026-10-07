from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import httpx
import pytest
from joserfc import jwt
from joserfc.jwk import RSAKey

from amesh.config import IdentityGroupMapping, IdentityProviderConfig
from amesh.domain import (
    FederatedClaims,
    FederationState,
    ProviderIdentity,
)
from amesh.federation import (
    FederationProviderUnavailable,
    IdentityFederationService,
)
from amesh.ports.federation_repository import FederationStateRejected


class MemoryFederationRepository:
    def __init__(self) -> None:
        self.states: dict[str, FederationState] = {}
        self.claims: list[FederatedClaims] = []
        self.events: list[tuple[str, str]] = []

    async def create_state(self, token: str, state: FederationState) -> None:
        self.states[token] = state

    async def consume_state(
        self,
        token: str,
        *,
        provider_id: str,
        now: datetime,
    ) -> FederationState:
        state = self.states.pop(token, None)
        if state is None or state.provider_id != provider_id or state.expires_at < now:
            raise FederationStateRejected("invalid state")
        return state

    async def resolve_identity(
        self,
        claims: FederatedClaims,
        *,
        group_mappings: tuple[IdentityGroupMapping, ...],
        default_tenant: str | None,
        default_role: str | None,
    ) -> ProviderIdentity:
        del group_mappings, default_tenant, default_role
        self.claims.append(claims)
        return ProviderIdentity(
            provider=claims.provider_id,
            principal_id=uuid4(),
            display=claims.display,
            credential_version=1,
        )

    async def record_event(
        self,
        provider_id: str,
        *,
        action: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object] | None = None,
    ) -> None:
        del action, evidence
        self.events.append((provider_id, f"{outcome}:{reason}"))


class SessionIssuer:
    def __init__(self) -> None:
        self.identities: list[ProviderIdentity] = []

    async def issue_federated_session(
        self,
        identity: ProviderIdentity,
        *,
        now: datetime | None = None,
    ) -> object:
        del now
        self.identities.append(identity)
        return object()


def _oidc_provider(secret_file: Path) -> IdentityProviderConfig:
    return IdentityProviderConfig.model_validate(
        {
            "id": "corporate-oidc",
            "kind": "oidc",
            "displayName": "Corporate OIDC",
            "domains": ["example.com"],
            "tenants": ["default"],
            "issuerUrl": "https://idp.example.test",
            "clientId": "amesh-client",
            "clientSecretFile": str(secret_file),
            "redirectUri": "https://amesh.example.test/api/v1/auth/federated/corporate-oidc/callback",
            "groupMappings": [{"external": "Engineering", "platformGroup": "engineers"}],
            "defaultTenant": "default",
            "defaultRole": "viewer",
        }
    )


def test_oidc_pkce_rotation_clock_skew_replay_routing_and_outage(tmp_path: Path) -> None:
    async def scenario() -> None:
        secret_file = tmp_path / "oidc-secret"
        secret_file.write_text("client-secret-one\n", encoding="utf-8")
        provider = _oidc_provider(secret_file)
        repository = MemoryFederationRepository()
        issuer = SessionIssuer()
        signing_key = RSAKey.generate_key(auto_kid=True)
        active_state: FederationState | None = None

        async def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("openid-configuration"):
                return httpx.Response(
                    200,
                    json={
                        "issuer": provider.issuer_url,
                        "authorization_endpoint": "https://idp.example.test/authorize",
                        "token_endpoint": "https://idp.example.test/token",
                        "jwks_uri": "https://idp.example.test/jwks",
                        "id_token_signing_alg_values_supported": ["RS256", "none"],
                    },
                )
            if request.url.path == "/jwks":
                return httpx.Response(200, json={"keys": [signing_key.as_dict()]})
            if request.url.path == "/token":
                expected_basic = base64.b64encode(b"amesh-client:client-secret-two").decode("ascii")
                assert request.headers["Authorization"] == f"Basic {expected_basic}"
                form = parse_qs((await request.aread()).decode("utf-8"))
                assert active_state is not None
                now = datetime.now(UTC)
                encoded = jwt.encode(
                    {"alg": "RS256", "kid": signing_key.kid},
                    {
                        "iss": provider.issuer_url,
                        "sub": "employee-123",
                        "aud": provider.client_id,
                        "iat": int(now.timestamp()),
                        "exp": int((now - timedelta(seconds=30)).timestamp()),
                        "nonce": active_state.nonce,
                        "email": "ada@example.com",
                        "name": "Ada Lovelace",
                        "groups": ["Engineering"],
                    },
                    signing_key,
                )
                assert form["code_verifier"][0] == active_state.code_verifier
                return httpx.Response(
                    200,
                    json={"access_token": "access", "token_type": "Bearer", "id_token": encoded},
                )
            return httpx.Response(404)

        service = IdentityFederationService(
            repository,
            issuer,  # type: ignore[arg-type]
            (provider,),
            http_transport=httpx.MockTransport(handler),
        )
        descriptors = service.descriptors(identifier="ada@example.com", tenant="default")
        assert [(item.id, item.login_mode) for item in descriptors] == [
            ("corporate-oidc", "redirect")
        ]
        assert service.descriptors(identifier="ada@other.test", tenant="default") == ()
        authorization_url = await service.begin_oidc(
            provider.id,
            tenant="default",
            return_to="/flows",
        )
        parameters = parse_qs(urlparse(authorization_url).query)
        assert parameters["code_challenge_method"] == ["S256"]
        state_token = parameters["state"][0]
        active_state = repository.states[state_token]
        secret_file.write_text("client-secret-two\n", encoding="utf-8")
        issued, return_to = await service.complete_oidc(
            provider.id,
            state_token=state_token,
            code="accepted-code",
        )
        assert issued is not None
        assert return_to == "/flows"
        assert repository.claims[0].groups == ("Engineering",)
        assert issuer.identities[0].display == "Ada Lovelace"
        with pytest.raises(FederationStateRejected):
            await service.complete_oidc(
                provider.id,
                state_token=state_token,
                code="replayed-code",
            )

        signing_key = RSAKey.generate_key(auto_kid=True)
        rotated_url = await service.begin_oidc(provider.id, tenant="default", return_to="/")
        rotated_state = parse_qs(urlparse(rotated_url).query)["state"][0]
        active_state = repository.states[rotated_state]
        await service.complete_oidc(
            provider.id,
            state_token=rotated_state,
            code="rotated-key-code",
        )
        assert len(issuer.identities) == 2

        async def outage(_request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("offline")

        offline = IdentityFederationService(
            repository,
            issuer,  # type: ignore[arg-type]
            (provider,),
            http_transport=httpx.MockTransport(outage),
        )
        with pytest.raises(FederationProviderUnavailable):
            await offline.begin_oidc(provider.id, tenant="default", return_to="/")

    asyncio.run(scenario())
