from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import httpx
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from joserfc import jwt
from joserfc.jwk import RSAKey
from pydantic import SecretStr

from amesh.config import IdentityGroupMapping, IdentityProviderConfig
from amesh.domain import (
    AuthenticationRequest,
    FederatedClaims,
    FederationState,
    ProviderIdentity,
)
from amesh.federation import (
    FederationProviderUnavailable,
    IdentityFederationService,
    LdapAuthenticationProvider,
)
from amesh.ports.federation_repository import FederationStateRejected


class MemoryFederationRepository:
    def __init__(self) -> None:
        self.states: dict[str, FederationState] = {}
        self.claims: list[FederatedClaims] = []
        self.events: list[tuple[str, str]] = []
        self.assertions: set[tuple[str, str]] = set()

    async def create_state(self, token: str, state: FederationState) -> None:
        self.states[token] = state

    async def attach_request_id(self, token: str, request_id: str) -> None:
        self.states[token] = self.states[token].model_copy(update={"request_id": request_id})

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

    async def record_assertion(
        self,
        provider_id: str,
        assertion_id: str,
        *,
        expires_at: datetime,
    ) -> None:
        del expires_at
        identity = (provider_id, assertion_id)
        if identity in self.assertions:
            raise PermissionError("replay")
        self.assertions.add(identity)


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


def _write_certificate_pair(tmp_path: Path, name: str) -> tuple[Path, Path]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC) - timedelta(minutes=1))
        .not_valid_after(datetime.now(UTC) + timedelta(days=30))
        .sign(key, hashes.SHA256())
    )
    key_file = tmp_path / f"{name}.key"
    cert_file = tmp_path / f"{name}.crt"
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    cert_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return key_file, cert_file


def test_saml_metadata_publishes_key_rotation_and_signed_request(tmp_path: Path) -> None:
    async def scenario() -> None:
        key_file, cert_file = _write_certificate_pair(tmp_path, "current")
        _, next_cert_file = _write_certificate_pair(tmp_path, "next")
        provider = IdentityProviderConfig.model_validate(
            {
                "id": "corporate-saml",
                "kind": "saml",
                "displayName": "Corporate SAML",
                "subjectClaim": "NameID",
                "emailClaim": "email",
                "displayClaim": "displayName",
                "idpEntityId": "https://idp.example.test/metadata",
                "ssoUrl": "https://idp.example.test/sso",
                "idpSigningCertFiles": [str(cert_file), str(next_cert_file)],
                "spEntityId": "https://amesh.example.test/saml/metadata",
                "acsUrl": "https://amesh.example.test/api/v1/auth/federated/corporate-saml/callback",
                "spCertFile": str(cert_file),
                "spPrivateKeyFile": str(key_file),
                "nextSpCertFile": str(next_cert_file),
            }
        )
        repository = MemoryFederationRepository()
        service = IdentityFederationService(
            repository,
            SessionIssuer(),  # type: ignore[arg-type]
            (provider,),
        )
        metadata = service.saml_metadata(provider.id)
        assert metadata.count("X509Certificate") >= 4
        location = await service.begin_saml(
            provider.id,
            {
                "https": "on",
                "http_host": "amesh.example.test",
                "server_port": "443",
                "script_name": "/login",
                "get_data": {},
                "post_data": {},
            },
            tenant=None,
            return_to="/flows",
        )
        query = parse_qs(urlparse(location).query)
        assert {"SAMLRequest", "RelayState", "SigAlg", "Signature"} <= query.keys()
        stored = repository.states[query["RelayState"][0]]
        assert stored.request_id
        assert stored.return_to == "/flows"

    asyncio.run(scenario())


def test_ldap_provider_maps_tls_authenticated_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    async def scenario() -> None:
        provider = IdentityProviderConfig.model_validate(
            {
                "id": "directory",
                "kind": "ldap",
                "displayName": "Corporate directory",
                "domains": ["example.com"],
                "ldapHost": "ldap.example.com",
                "ldapCaFile": "/mounted/ca.pem",
                "ldapUserDnTemplate": "uid={identifier},ou=people,dc=example,dc=com",
                "groupMappings": [{"external": "Operators", "platformGroup": "operators"}],
            }
        )
        repository = MemoryFederationRepository()

        def accepted(
            _provider: IdentityProviderConfig,
            identifier: str,
            secret: SecretStr,
        ) -> dict[str, object]:
            assert identifier == "ada"
            assert secret.get_secret_value() == "password"
            return {
                "subject": "uid=ada,ou=people,dc=example,dc=com",
                "email": "ada@example.com",
                "display": "Ada Lovelace",
                "groups": ["Operators"],
            }

        monkeypatch.setattr("amesh.federation._ldap_bind_and_claims", accepted)
        ldap = LdapAuthenticationProvider(provider, repository)
        identity = await ldap.authenticate(
            AuthenticationRequest(
                provider="directory",
                identifier="ada",
                secret=SecretStr("password"),
            ),
            now=datetime.now(UTC),
        )
        assert identity is not None
        assert ldap.descriptor.login_mode == "password"
        assert repository.claims[0].email == "ada@example.com"

    asyncio.run(scenario())
