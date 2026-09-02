from __future__ import annotations

import asyncio
import secrets
import ssl
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client  # type: ignore[import-untyped]
from pydantic import SecretStr

from amesh.authentication import AuthenticationService
from amesh.config import IdentityProviderConfig
from amesh.domain import (
    AuthenticationProviderDescriptor,
    AuthenticationProviderKind,
    AuthenticationRequest,
    FederatedClaims,
    FederationProtocol,
    FederationState,
    IssuedBrowserSession,
    ProviderIdentity,
)
from amesh.ports.authentication_repository import AuthenticationProvider
from amesh.ports.federation_repository import FederationRepository

_SAFE_RETURN_PREFIXES = ("/",)
_OIDC_SIGNING_ALGORITHMS = {
    "RS256",
    "RS384",
    "RS512",
    "PS256",
    "PS384",
    "PS512",
    "ES256",
    "ES384",
    "ES512",
}


class FederationRejected(PermissionError):
    """Raised when a federated response fails deterministic validation."""


class FederationProviderUnavailable(ConnectionError):
    """Raised when an external identity provider cannot be reached."""


class IdentityFederationService:
    def __init__(
        self,
        repository: FederationRepository,
        authentication: AuthenticationService,
        providers: tuple[IdentityProviderConfig, ...],
        *,
        state_ttl_seconds: int = 300,
        http_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._repository = repository
        self._authentication = authentication
        self._providers = {provider.id: provider for provider in providers}
        self._state_ttl_seconds = state_ttl_seconds
        self._http_transport = http_transport

    def descriptors(
        self,
        *,
        identifier: str | None = None,
        tenant: str | None = None,
    ) -> tuple[AuthenticationProviderDescriptor, ...]:
        return tuple(
            _descriptor(provider)
            for provider in self._providers.values()
            if _route_matches(provider, identifier=identifier, tenant=tenant)
        )

    def provider(self, provider_id: str, *, kind: str | None = None) -> IdentityProviderConfig:
        provider = self._providers.get(provider_id)
        if provider is None or (kind is not None and provider.kind != kind):
            raise FederationRejected("identity provider is unavailable")
        return provider

    async def begin_oidc(
        self,
        provider_id: str,
        *,
        tenant: str | None,
        return_to: str,
    ) -> str:
        provider = self.provider(provider_id, kind="oidc")
        _require_tenant_route(provider, tenant)
        metadata = await self._oidc_metadata(provider)
        state_token = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)
        await self._repository.create_state(
            state_token,
            FederationState(
                provider_id=provider.id,
                protocol=FederationProtocol.OIDC,
                nonce=nonce,
                code_verifier=code_verifier,
                tenant_slug=tenant,
                return_to=_safe_return_to(return_to),
                expires_at=datetime.now(UTC) + timedelta(seconds=self._state_ttl_seconds),
            ),
        )
        try:
            async with AsyncOAuth2Client(
                client_id=provider.client_id,
                client_secret=_read_secret(provider.client_secret_file),
                redirect_uri=provider.redirect_uri,
                scope=" ".join(provider.scopes),
                code_challenge_method="S256",
            ) as client:
                url, _ = client.create_authorization_url(
                    metadata["authorization_endpoint"],
                    state=state_token,
                    nonce=nonce,
                    code_verifier=code_verifier,
                )
        except (KeyError, ValueError) as exc:
            raise FederationRejected("OIDC discovery metadata is incomplete") from exc
        return str(url)

    async def complete_oidc(
        self,
        provider_id: str,
        *,
        state_token: str,
        code: str,
    ) -> tuple[IssuedBrowserSession, str]:
        provider = self.provider(provider_id, kind="oidc")
        state = await self._repository.consume_state(
            state_token,
            provider_id=provider.id,
            now=datetime.now(UTC),
        )
        metadata = await self._oidc_metadata(provider)
        try:
            async with AsyncOAuth2Client(
                client_id=provider.client_id,
                client_secret=_read_secret(provider.client_secret_file),
                redirect_uri=provider.redirect_uri,
                scope=" ".join(provider.scopes),
                code_challenge_method="S256",
                transport=self._http_transport,
            ) as client:
                token = await client.fetch_token(
                    metadata["token_endpoint"],
                    code=code,
                    code_verifier=state.code_verifier,
                    redirect_uri=provider.redirect_uri,
                )
            claims = await self._validate_oidc_token(provider, metadata, token, state)
            identity = await self._resolve(provider, claims, tenant=state.tenant_slug)
        except httpx.HTTPError as exc:
            await self._repository.record_event(
                provider.id,
                action="oidc.callback",
                outcome="REJECTED",
                reason="provider-unavailable",
            )
            raise FederationProviderUnavailable("OIDC provider is unavailable") from exc
        except FederationProviderUnavailable:
            raise
        except Exception as exc:
            await self._repository.record_event(
                provider.id,
                action="oidc.callback",
                outcome="REJECTED",
                reason="invalid-response",
            )
            raise FederationRejected("OIDC response is invalid") from exc
        return await self._authentication.issue_federated_session(identity), state.return_to

    async def reject_oidc(
        self,
        provider_id: str,
        *,
        state_token: str,
        reason: str,
    ) -> None:
        provider = self.provider(provider_id, kind="oidc")
        await self._repository.consume_state(
            state_token,
            provider_id=provider.id,
            now=datetime.now(UTC),
        )
        await self._repository.record_event(
            provider.id,
            action="oidc.callback",
            outcome="REJECTED",
            reason=reason,
        )

    async def _oidc_metadata(self, provider: IdentityProviderConfig) -> dict[str, Any]:
        assert provider.issuer_url is not None
        discovery_url = f"{provider.issuer_url.rstrip('/')}/.well-known/openid-configuration"
        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=False,
                transport=self._http_transport,
            ) as client:
                response = await client.get(discovery_url, headers={"Accept": "application/json"})
                response.raise_for_status()
                metadata = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise FederationProviderUnavailable("OIDC discovery is unavailable") from exc
        if not isinstance(metadata, dict) or metadata.get("issuer") != provider.issuer_url:
            raise FederationRejected("OIDC issuer does not match configured provider")
        for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
            endpoint = metadata.get(key)
            if not isinstance(endpoint, str) or not _is_secure_endpoint(endpoint):
                raise FederationRejected(f"OIDC {key} must use HTTPS or loopback HTTP")
        return metadata

    async def _validate_oidc_token(
        self,
        provider: IdentityProviderConfig,
        metadata: Mapping[str, Any],
        token: Mapping[str, Any],
        state: FederationState,
    ) -> Mapping[str, Any]:
        id_token = token.get("id_token")
        if not isinstance(id_token, str):
            raise FederationRejected("OIDC token response omitted id_token")
        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=False,
                transport=self._http_transport,
            ) as client:
                response = await client.get(str(metadata["jwks_uri"]))
                response.raise_for_status()
                jwks = response.json()
            from authlib.oidc.core import CodeIDToken  # type: ignore[import-untyped]
            from joserfc import jwt
            from joserfc.jwk import KeySet

            advertised = metadata.get("id_token_signing_alg_values_supported", ["RS256"])
            algorithms = _OIDC_SIGNING_ALGORITHMS.intersection(
                str(value) for value in advertised if isinstance(value, str)
            )
            if not algorithms:
                raise FederationRejected("OIDC provider offers no accepted signing algorithm")
            decoded = jwt.decode(
                id_token,
                KeySet.import_key_set(jwks),
                algorithms=algorithms,
            )
            claims = CodeIDToken(
                decoded.claims,
                decoded.header,
                options={
                    "iss": {"value": provider.issuer_url},
                    "aud": {"value": provider.client_id},
                },
                params={
                    "nonce": state.nonce,
                    "client_id": provider.client_id,
                    "access_token": token.get("access_token"),
                },
            )
            claims.validate(leeway=provider.clock_skew_seconds)
            return dict(claims)
        except httpx.HTTPError as exc:
            raise FederationProviderUnavailable("OIDC signing keys are unavailable") from exc

    async def begin_saml(
        self,
        provider_id: str,
        request_data: dict[str, Any],
        *,
        tenant: str | None,
        return_to: str,
    ) -> str:
        provider = self.provider(provider_id, kind="saml")
        _require_tenant_route(provider, tenant)
        state_token = secrets.token_urlsafe(32)
        auth = _saml_auth(provider, request_data)
        url = auth.login(return_to=state_token)
        request_id = auth.get_last_request_id()
        if not request_id:
            raise FederationRejected("SAML request id was not generated")
        await self._repository.create_state(
            state_token,
            FederationState(
                provider_id=provider.id,
                protocol=FederationProtocol.SAML,
                request_id=request_id,
                tenant_slug=tenant,
                return_to=_safe_return_to(return_to),
                expires_at=datetime.now(UTC) + timedelta(seconds=self._state_ttl_seconds),
            ),
        )
        return str(url)

    async def complete_saml(
        self,
        provider_id: str,
        request_data: dict[str, Any],
        *,
        state_token: str,
    ) -> tuple[IssuedBrowserSession, str]:
        provider = self.provider(provider_id, kind="saml")
        state = await self._repository.consume_state(
            state_token,
            provider_id=provider.id,
            now=datetime.now(UTC),
        )
        auth = _saml_auth(provider, request_data)
        try:
            auth.process_response(request_id=state.request_id)
            if auth.get_errors() or not auth.is_authenticated():
                raise FederationRejected(auth.get_last_error_reason() or "SAML response rejected")
            assertion_id = auth.get_last_assertion_id() or auth.get_last_message_id()
            if not assertion_id:
                raise FederationRejected("SAML response omitted replay identifier")
            not_on_or_after = auth.get_last_assertion_not_on_or_after()
            replay_expiry = (
                datetime.fromtimestamp(not_on_or_after, UTC)
                if isinstance(not_on_or_after, int | float)
                else datetime.now(UTC) + timedelta(minutes=5)
            )
            await self._repository.record_assertion(
                provider.id,
                assertion_id,
                expires_at=replay_expiry,
            )
            attributes = auth.get_attributes()
            raw_claims: dict[str, Any] = {key: value for key, value in attributes.items()}
            raw_claims["NameID"] = auth.get_nameid()
            identity = await self._resolve(provider, raw_claims, tenant=state.tenant_slug)
        except FederationRejected:
            await self._repository.record_event(
                provider.id,
                action="saml.callback",
                outcome="REJECTED",
                reason="invalid-response",
            )
            raise
        except Exception as exc:
            await self._repository.record_event(
                provider.id,
                action="saml.callback",
                outcome="REJECTED",
                reason="invalid-response",
            )
            raise FederationRejected("SAML response is invalid") from exc
        return await self._authentication.issue_federated_session(identity), state.return_to

    def saml_metadata(self, provider_id: str) -> str:
        provider = self.provider(provider_id, kind="saml")
        from onelogin.saml2.settings import OneLogin_Saml2_Settings  # type: ignore[import-untyped]

        settings = OneLogin_Saml2_Settings(_saml_settings(provider), sp_validation_only=True)
        metadata = settings.get_sp_metadata()
        errors = settings.validate_metadata(metadata)
        if errors:
            raise FederationRejected(f"invalid SAML service-provider metadata: {errors[0]}")
        return str(metadata)

    async def _resolve(
        self,
        provider: IdentityProviderConfig,
        raw_claims: Mapping[str, Any],
        *,
        tenant: str | None,
    ) -> ProviderIdentity:
        claims = FederatedClaims(
            provider_id=provider.id,
            subject=_required_claim(raw_claims, provider.subject_claim),
            email=_required_claim(raw_claims, provider.email_claim),
            display=_required_claim(raw_claims, provider.display_claim),
            groups=_group_claim(raw_claims, provider.groups_claim),
        )
        domain = claims.email.rsplit("@", 1)[-1]
        if provider.domains and domain not in provider.domains:
            raise FederationRejected("identity email domain is not routed to this provider")
        _require_tenant_route(provider, tenant)
        return await self._repository.resolve_identity(
            claims,
            group_mappings=provider.group_mappings,
            default_tenant=provider.default_tenant or tenant,
            default_role=provider.default_role,
        )


class LdapAuthenticationProvider(AuthenticationProvider):
    def __init__(
        self,
        config: IdentityProviderConfig,
        repository: FederationRepository,
    ) -> None:
        if config.kind != "ldap":
            raise ValueError("LDAP authentication provider requires LDAP configuration")
        self.id = config.id
        self.descriptor = _descriptor(config)
        self._config = config
        self._repository = repository

    async def authenticate(
        self,
        request: AuthenticationRequest,
        *,
        now: datetime,
    ) -> ProviderIdentity | None:
        del now
        try:
            raw_claims = await asyncio.to_thread(
                _ldap_bind_and_claims,
                self._config,
                request.identifier,
                request.secret,
            )
            if raw_claims is None:
                return None
            group_values = raw_claims["groups"]
            if not isinstance(group_values, list | tuple):
                return None
            claims = FederatedClaims(
                provider_id=self.id,
                subject=str(raw_claims["subject"]),
                email=str(raw_claims["email"]),
                display=str(raw_claims["display"]),
                groups=tuple(str(value) for value in group_values),
            )
            domain = claims.email.rsplit("@", 1)[-1]
            if self._config.domains and domain not in self._config.domains:
                return None
            return await self._repository.resolve_identity(
                claims,
                group_mappings=self._config.group_mappings,
                default_tenant=self._config.default_tenant,
                default_role=self._config.default_role,
            )
        except PermissionError:
            return None
        except Exception as exc:
            raise FederationProviderUnavailable("LDAP provider is unavailable") from exc


def _ldap_bind_and_claims(
    provider: IdentityProviderConfig,
    identifier: str,
    secret: SecretStr,
) -> dict[str, object] | None:
    import ldap3  # type: ignore[import-untyped]
    from ldap3.core.exceptions import LDAPInvalidCredentialsResult  # type: ignore[import-untyped]
    from ldap3.utils.conv import escape_filter_chars  # type: ignore[import-untyped]
    from ldap3.utils.dn import escape_rdn  # type: ignore[import-untyped]

    assert provider.ldap_host is not None
    assert provider.ldap_ca_file is not None
    assert provider.ldap_user_dn_template is not None
    tls = ldap3.Tls(
        validate=ssl.CERT_REQUIRED,
        ca_certs_file=provider.ldap_ca_file,
        version=ssl.PROTOCOL_TLS_CLIENT,
    )
    server = ldap3.Server(
        provider.ldap_host,
        port=provider.ldap_port,
        use_ssl=not provider.ldap_start_tls,
        tls=tls,
        connect_timeout=10,
    )
    user_dn = provider.ldap_user_dn_template.format(identifier=escape_rdn(identifier.strip()))
    connection = ldap3.Connection(
        server,
        user=user_dn,
        password=secret.get_secret_value(),
        raise_exceptions=True,
        receive_timeout=10,
    )
    try:
        connection.open()
        if provider.ldap_start_tls:
            connection.start_tls()
        try:
            bound = connection.bind()
        except LDAPInvalidCredentialsResult:
            return None
        if not bound:
            return None
        connection.search(
            user_dn,
            "(objectClass=*)",
            search_scope=ldap3.BASE,
            attributes=["mail", "displayName"],
        )
        if not connection.entries:
            return None
        entry = connection.entries[0]
        email = str(entry["mail"].value or "")
        display = str(entry["displayName"].value or identifier)
        groups: list[str] = []
        if provider.ldap_group_search_base:
            group_filter = provider.ldap_group_filter.format(
                user_dn=escape_filter_chars(user_dn),
                identifier=escape_filter_chars(identifier),
            )
            connection.search(
                provider.ldap_group_search_base,
                group_filter,
                attributes=[provider.ldap_group_name_attribute],
            )
            groups = [
                str(item[provider.ldap_group_name_attribute].value)
                for item in connection.entries
                if item[provider.ldap_group_name_attribute].value is not None
            ]
        return {"subject": user_dn, "email": email, "display": display, "groups": groups}
    finally:
        connection.unbind()


def _descriptor(provider: IdentityProviderConfig) -> AuthenticationProviderDescriptor:
    return AuthenticationProviderDescriptor(
        id=provider.id,
        kind=AuthenticationProviderKind(provider.kind),
        display_name=provider.display_name,
        interactive=True,
        login_mode="password" if provider.kind == "ldap" else "redirect",
        domains=provider.domains,
        tenants=provider.tenants,
    )


def _route_matches(
    provider: IdentityProviderConfig,
    *,
    identifier: str | None,
    tenant: str | None,
) -> bool:
    if tenant and provider.tenants and tenant not in provider.tenants:
        return False
    if identifier and "@" in identifier and provider.domains:
        return identifier.rsplit("@", 1)[-1].lower() in provider.domains
    return True


def _require_tenant_route(provider: IdentityProviderConfig, tenant: str | None) -> None:
    if provider.tenants and (tenant is None or tenant not in provider.tenants):
        raise FederationRejected("identity provider is not routed to this tenant")


def _required_claim(claims: Mapping[str, Any], path: str) -> str:
    value: Any = claims
    for segment in path.split("."):
        if not isinstance(value, Mapping) or segment not in value:
            raise FederationRejected(f"identity provider omitted required claim {path!r}")
        value = value[segment]
    if isinstance(value, list | tuple):
        value = value[0] if value else None
    if not isinstance(value, str) or not value.strip():
        raise FederationRejected(f"identity provider claim {path!r} is invalid")
    return value.strip()


def _group_claim(claims: Mapping[str, Any], path: str) -> tuple[str, ...]:
    value: Any = claims
    for segment in path.split("."):
        if not isinstance(value, Mapping) or segment not in value:
            return ()
        value = value[segment]
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list | tuple):
        return tuple(str(item) for item in value if isinstance(item, str) and item)
    raise FederationRejected(f"identity provider group claim {path!r} is invalid")


def _read_secret(path: str | None) -> str:
    if path is None:
        raise FederationRejected("identity provider secret file is not configured")
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise FederationProviderUnavailable("identity provider secret file is unavailable") from exc
    if not value:
        raise FederationRejected("identity provider secret file is empty")
    return value


def _read_pem(path: str | None) -> str:
    return _read_secret(path).replace("\r\n", "\n")


def _saml_settings(provider: IdentityProviderConfig) -> dict[str, Any]:
    assert provider.sp_entity_id is not None
    assert provider.acs_url is not None
    assert provider.idp_entity_id is not None
    assert provider.sso_url is not None
    signing_certs = [_read_pem(path) for path in provider.idp_signing_cert_files]
    sp: dict[str, Any] = {
        "entityId": provider.sp_entity_id,
        "assertionConsumerService": {
            "url": provider.acs_url,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        },
        "singleLogoutService": {
            "url": provider.slo_url or provider.acs_url,
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        },
        "x509cert": _read_pem(provider.sp_cert_file),
        "privateKey": _read_pem(provider.sp_private_key_file),
    }
    if provider.next_sp_cert_file:
        sp["x509certNew"] = _read_pem(provider.next_sp_cert_file)
    return {
        "strict": True,
        "debug": False,
        "sp": sp,
        "idp": {
            "entityId": provider.idp_entity_id,
            "singleSignOnService": {
                "url": provider.sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": provider.slo_url or provider.sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509certMulti": {"signing": signing_certs},
        },
        "security": {
            "authnRequestsSigned": True,
            "logoutRequestSigned": True,
            "logoutResponseSigned": True,
            "wantMessagesSigned": False,
            "wantAssertionsSigned": True,
            "wantNameId": True,
            "rejectDeprecatedAlgorithm": True,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        },
    }


def _saml_auth(provider: IdentityProviderConfig, request_data: dict[str, Any]) -> Any:
    from onelogin.saml2.auth import OneLogin_Saml2_Auth  # type: ignore[import-untyped]

    return OneLogin_Saml2_Auth(request_data, _saml_settings(provider))


def _safe_return_to(value: str) -> str:
    if value.startswith("//") or not value.startswith(_SAFE_RETURN_PREFIXES):
        return "/"
    return value


def _is_secure_endpoint(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" or (
        parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    )
