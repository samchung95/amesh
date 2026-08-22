from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

from pwdlib import PasswordHash
from pydantic import SecretStr

from amesh.domain import (
    AuthenticatedBrowserSession,
    AuthenticationProviderDescriptor,
    AuthenticationProviderKind,
    AuthenticationRequest,
    BrowserSession,
    IssuedBrowserSession,
    PrincipalDefinition,
    PrincipalType,
    ProviderIdentity,
    issue_csrf_material,
    issue_session_material,
    parse_session_material,
    token_digest,
)
from amesh.observability import AUTHENTICATION_ATTEMPTS, AUTHENTICATION_LOCKOUTS
from amesh.ports.authentication_repository import (
    AuthenticationProvider,
    AuthenticationRepository,
)


class InvalidAuthentication(PermissionError):
    """Raised for every public local-login failure to avoid identity disclosure."""


class AuthenticationRateLimited(PermissionError):
    """Raised when the bounded source login rate is exhausted."""


class InvalidCsrf(InvalidAuthentication):
    """Raised when a browser session is valid but an unsafe request lacks CSRF proof."""


class LocalAuthenticationDisabled(PermissionError):
    """Raised when deployment policy requires federated-only authentication."""


class PasswordPolicyError(ValueError):
    """Raised when a local password does not meet the published policy."""


class LocalAuthenticationProvider(AuthenticationProvider):
    id = "local"
    descriptor = AuthenticationProviderDescriptor(
        id=id,
        kind=AuthenticationProviderKind.LOCAL,
        display_name="Local account",
    )

    def __init__(
        self,
        repository: AuthenticationRepository,
        *,
        password_hash: PasswordHash,
        max_failures: int,
        lock_seconds: int,
    ) -> None:
        self._repository = repository
        self._password_hash = password_hash
        self._max_failures = max_failures
        self._lock_seconds = lock_seconds
        self._dummy_hash = password_hash.hash("amesh-nonexistent-identity-dummy-secret")

    async def authenticate(
        self,
        request: AuthenticationRequest,
        *,
        now: datetime,
    ) -> ProviderIdentity | None:
        identifier = request.identifier.strip().lower()
        identity = await self._repository.load_local_identity(identifier)
        supplied = request.secret.get_secret_value()
        if identity is None:
            self._password_hash.verify(supplied, self._dummy_hash)
            await self._repository.record_login_failure(
                identifier,
                now=now,
                max_failures=self._max_failures,
                lock_seconds=self._lock_seconds,
                reason="invalid-identity",
            )
            return None
        if identity.locked_until is not None and now < identity.locked_until:
            locked = await self._repository.record_login_failure(
                identifier,
                now=now,
                max_failures=self._max_failures,
                lock_seconds=self._lock_seconds,
                reason="account-locked",
            )
            if locked:
                AUTHENTICATION_LOCKOUTS.inc()
            return None
        verified, updated_hash = self._password_hash.verify_and_update(
            supplied,
            identity.password_hash,
        )
        if not verified:
            locked = await self._repository.record_login_failure(
                identifier,
                now=now,
                max_failures=self._max_failures,
                lock_seconds=self._lock_seconds,
                reason="invalid-secret",
            )
            if locked:
                AUTHENTICATION_LOCKOUTS.inc()
            return None
        if updated_hash is not None:
            await self._repository.update_password_hash(identity.principal_id, updated_hash)
        return ProviderIdentity(
            provider=self.id,
            principal_id=identity.principal_id,
            display=identity.display_name,
            credential_version=identity.credential_version,
        )


class AuthenticationService:
    def __init__(
        self,
        repository: AuthenticationRepository,
        *,
        token_pepper: SecretStr,
        policy: str,
        session_idle_seconds: int,
        session_absolute_seconds: int,
        session_rotation_seconds: int,
        session_overlap_seconds: int,
        login_rate_limit_per_minute: int,
        login_max_failures: int,
        login_lock_seconds: int,
        password_hash: PasswordHash | None = None,
        providers: tuple[AuthenticationProvider, ...] = (),
    ) -> None:
        self._repository = repository
        self._token_pepper = token_pepper
        self._policy = policy
        self._session_idle_seconds = session_idle_seconds
        self._session_absolute_seconds = session_absolute_seconds
        self._session_rotation_seconds = session_rotation_seconds
        self._session_overlap_seconds = session_overlap_seconds
        self._login_rate_limit_per_minute = login_rate_limit_per_minute
        self._password_hash = password_hash or PasswordHash.recommended()
        local = LocalAuthenticationProvider(
            repository,
            password_hash=self._password_hash,
            max_failures=login_max_failures,
            lock_seconds=login_lock_seconds,
        )
        self._providers: dict[str, AuthenticationProvider] = {local.id: local}
        for provider in providers:
            if provider.id in self._providers:
                raise ValueError(f"authentication provider {provider.id!r} is registered twice")
            if provider.descriptor.id != provider.id:
                raise ValueError("authentication provider descriptor id must match provider id")
            self._providers[provider.id] = provider

    def providers(self) -> tuple[AuthenticationProviderDescriptor, ...]:
        return tuple(
            provider.descriptor
            for provider in self._providers.values()
            if self._policy != "federated-only"
            or provider.descriptor.kind is not AuthenticationProviderKind.LOCAL
        )

    async def bootstrap_local_admin(
        self,
        *,
        handle: str,
        display_name: str,
        password: SecretStr,
    ) -> PrincipalDefinition:
        self._require_local_enabled()
        encoded = self._hash_password(password)
        return await self._repository.bootstrap_local_admin(
            PrincipalDefinition(
                principal_type=PrincipalType.USER,
                handle=handle.strip().lower(),
                display_name=display_name.strip(),
            ),
            encoded,
        )

    async def login(
        self,
        request: AuthenticationRequest,
        *,
        source: str,
    ) -> IssuedBrowserSession:
        now = datetime.now(UTC)
        if request.provider == "local":
            self._require_local_enabled()
        provider = self._providers.get(request.provider)
        if provider is None:
            AUTHENTICATION_ATTEMPTS.labels(provider="unknown", outcome="invalid").inc()
            raise InvalidAuthentication("authentication failed")
        source_material = sha256(source.encode("utf-8")).hexdigest()
        allowed = await self._repository.allow_login_source(
            token_digest(source_material, self._token_pepper),
            now=now,
            limit_per_minute=self._login_rate_limit_per_minute,
        )
        if not allowed:
            AUTHENTICATION_ATTEMPTS.labels(provider=provider.id, outcome="rate-limited").inc()
            raise AuthenticationRateLimited("authentication rate limit exceeded")
        identity = await provider.authenticate(request, now=now)
        if identity is None:
            AUTHENTICATION_ATTEMPTS.labels(provider=provider.id, outcome="invalid").inc()
            raise InvalidAuthentication("authentication failed")
        session = BrowserSession(
            principal_id=identity.principal_id,
            issued_credential_version=identity.credential_version,
            created_at=now,
            idle_expires_at=now + timedelta(seconds=self._session_idle_seconds),
            absolute_expires_at=now + timedelta(seconds=self._session_absolute_seconds),
            rotated_at=now,
        )
        session_token, session_secret = issue_session_material(session.id)
        csrf_token = issue_csrf_material()
        actor = await self._repository.create_browser_session(
            session,
            token_hash=token_digest(session_secret, self._token_pepper),
            csrf_hash=token_digest(csrf_token, self._token_pepper),
            provider=identity.provider,
        )
        AUTHENTICATION_ATTEMPTS.labels(provider=provider.id, outcome="success").inc()
        return IssuedBrowserSession(
            actor=actor,
            session_id=session.id,
            session_token=SecretStr(session_token),
            csrf_token=SecretStr(csrf_token),
            idle_expires_at=session.idle_expires_at,
            absolute_expires_at=session.absolute_expires_at,
        )

    async def authenticate_session(
        self,
        token: str,
        *,
        csrf_cookie: str | None,
        csrf_header: str | None,
        require_csrf: bool,
    ) -> AuthenticatedBrowserSession:
        try:
            session_id, secret = parse_session_material(token)
        except ValueError as exc:
            raise InvalidAuthentication("authentication failed") from exc
        csrf_hash: bytes | None = None
        if require_csrf:
            if (
                csrf_cookie is None
                or csrf_header is None
                or not secrets.compare_digest(csrf_cookie, csrf_header)
                or len(csrf_cookie) > 256
            ):
                raise InvalidCsrf("CSRF validation failed")
            csrf_hash = token_digest(csrf_cookie, self._token_pepper)
        replacement_token, replacement_secret = issue_session_material(session_id)
        authenticated = await self._repository.authenticate_browser_session(
            session_id,
            token_hash=token_digest(secret, self._token_pepper),
            csrf_hash=csrf_hash,
            require_csrf=require_csrf,
            now=datetime.now(UTC),
            idle_seconds=self._session_idle_seconds,
            rotation_seconds=self._session_rotation_seconds,
            replacement_token_hash=token_digest(replacement_secret, self._token_pepper),
            overlap_seconds=self._session_overlap_seconds,
        )
        if authenticated is None:
            raise InvalidAuthentication("authentication failed")
        return AuthenticatedBrowserSession(
            actor=authenticated.actor,
            session_id=authenticated.session_id,
            rotated_token=SecretStr(replacement_token) if authenticated.rotated else None,
            idle_expires_at=authenticated.idle_expires_at,
            absolute_expires_at=authenticated.absolute_expires_at,
        )

    async def logout(self, session_id: UUID, *, actor_id: str) -> bool:
        return await self._repository.revoke_session(session_id, actor_id=actor_id)

    async def revoke_all(self, principal_id: UUID, *, actor_id: str) -> int:
        return await self._repository.revoke_all_sessions(principal_id, actor_id=actor_id)

    async def set_local_password(
        self,
        principal_id: UUID,
        password: SecretStr,
        *,
        actor_id: str,
    ) -> int:
        self._require_local_enabled()
        return await self._repository.set_local_password(
            principal_id,
            self._hash_password(password),
            actor_id=actor_id,
        )

    async def change_local_password(
        self,
        principal_id: UUID,
        *,
        identifier: str,
        current_password: SecretStr,
        new_password: SecretStr,
    ) -> int:
        self._require_local_enabled()
        provider = self._providers["local"]
        identity = await provider.authenticate(
            AuthenticationRequest(
                provider="local",
                identifier=identifier,
                secret=current_password,
            ),
            now=datetime.now(UTC),
        )
        if identity is None or identity.principal_id != principal_id:
            raise InvalidAuthentication("authentication failed")
        return await self.set_local_password(
            principal_id,
            new_password,
            actor_id=str(principal_id),
        )

    def _hash_password(self, password: SecretStr) -> str:
        value = password.get_secret_value()
        if len(value) < 12:
            raise PasswordPolicyError("local passwords must contain at least 12 characters")
        if len(value) > 1024:
            raise PasswordPolicyError("local passwords cannot exceed 1024 characters")
        return self._password_hash.hash(value)

    def _require_local_enabled(self) -> None:
        if self._policy == "federated-only":
            AUTHENTICATION_ATTEMPTS.labels(provider="local", outcome="policy-denied").inc()
            raise LocalAuthenticationDisabled("local authentication is disabled by policy")
