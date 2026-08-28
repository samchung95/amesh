from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.domain.authentication import (
    AuthenticationProviderDescriptor,
    AuthenticationRequest,
    BrowserSession,
    ProviderIdentity,
)
from amesh.domain.authorization import ActorContext, PrincipalDefinition


@dataclass(frozen=True)
class LocalIdentityRecord:
    principal_id: UUID
    display_name: str
    password_hash: str
    failed_attempts: int
    locked_until: datetime | None
    credential_version: int


@dataclass(frozen=True)
class SessionAuthenticationRecord:
    actor: ActorContext
    session_id: UUID
    rotated: bool
    idle_expires_at: datetime
    absolute_expires_at: datetime


class AuthenticationProvider(Protocol):
    id: str
    descriptor: AuthenticationProviderDescriptor

    async def authenticate(
        self,
        request: AuthenticationRequest,
        *,
        now: datetime,
    ) -> ProviderIdentity | None: ...


class AuthenticationRepository(Protocol):
    async def bootstrap_local_admin(
        self,
        principal: PrincipalDefinition,
        password_hash: str,
    ) -> PrincipalDefinition: ...

    async def load_local_identity(self, identifier: str) -> LocalIdentityRecord | None: ...

    async def allow_login_source(
        self,
        source_hash: bytes,
        *,
        now: datetime,
        limit_per_minute: int,
    ) -> bool: ...

    async def record_login_failure(
        self,
        identifier: str,
        *,
        now: datetime,
        max_failures: int,
        lock_seconds: int,
        reason: str,
    ) -> bool: ...

    async def create_browser_session(
        self,
        session: BrowserSession,
        *,
        token_hash: bytes,
        csrf_hash: bytes,
        provider: str,
    ) -> ActorContext: ...

    async def authenticate_browser_session(
        self,
        session_id: UUID,
        *,
        token_hash: bytes,
        csrf_hash: bytes | None,
        require_csrf: bool,
        now: datetime,
        idle_seconds: int,
        rotation_seconds: int,
        replacement_token_hash: bytes,
        overlap_seconds: int,
    ) -> SessionAuthenticationRecord | None: ...

    async def revoke_session(self, session_id: UUID, *, actor_id: str) -> bool: ...

    async def revoke_all_sessions(self, principal_id: UUID, *, actor_id: str) -> int: ...

    async def set_local_password(
        self,
        principal_id: UUID,
        password_hash: str,
        *,
        actor_id: str,
    ) -> int: ...

    async def update_password_hash(self, principal_id: UUID, password_hash: str) -> None: ...
