from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.domain import ActorContext, CredentialMetadata, PrincipalType, StoredCredential


class CredentialRateLimitExceeded(RuntimeError):
    """Raised when a credential has exhausted its own request quota."""


@dataclass(frozen=True)
class CredentialPrincipal:
    id: UUID
    principal_type: PrincipalType
    display: str
    credential_version: int


class CredentialRepository(Protocol):
    async def load_principal(self, principal_id: UUID) -> CredentialPrincipal: ...

    async def create_credential(
        self,
        credential: StoredCredential,
        *,
        actor_id: str,
    ) -> CredentialMetadata: ...

    async def get_credential(self, credential_id: UUID) -> CredentialMetadata: ...

    async def list_credentials(self, principal_id: UUID) -> list[CredentialMetadata]: ...

    async def authenticate(
        self,
        credential_id: UUID,
        candidate_hashes: tuple[bytes, ...],
        *,
        audience: str,
        now: datetime,
    ) -> ActorContext | None: ...

    async def record_authentication_failure(
        self,
        credential_id: UUID | None,
        *,
        reason: str,
    ) -> None: ...

    async def rotate_credential(
        self,
        current_id: UUID,
        replacement: StoredCredential,
        *,
        overlap_expires_at: datetime,
        actor_id: str,
    ) -> CredentialMetadata: ...

    async def revoke_credential(self, credential_id: UUID, *, actor_id: str) -> int: ...

    async def revoke_all_credentials(self, principal_id: UUID, *, actor_id: str) -> int: ...
