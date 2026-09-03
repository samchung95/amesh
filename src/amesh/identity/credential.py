from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import SecretStr

from amesh.domain import (
    ActorContext,
    CredentialKind,
    CredentialMetadata,
    CredentialStatus,
    IssuedCredential,
    PrincipalType,
    StoredCredential,
    credential_scope_covers,
    issue_token_material,
    parse_token_material,
    token_digest,
)
from amesh.ports.credential_repository import CredentialRepository


class InvalidCredential(PermissionError):
    """Raised when bearer credential validation fails closed."""


class CredentialOperationError(ValueError):
    """Raised when a requested credential lifecycle operation is invalid."""


class CredentialService:
    def __init__(
        self,
        repository: CredentialRepository,
        *,
        token_pepper: SecretStr,
        previous_token_pepper: SecretStr | None = None,
    ) -> None:
        self._repository = repository
        self._token_pepper = token_pepper
        self._previous_token_pepper = previous_token_pepper

    async def issue(
        self,
        principal_id: UUID,
        *,
        name: str,
        scopes: tuple[str, ...],
        audience: str,
        expires_at: datetime,
        rate_limit_per_minute: int,
        actor_id: str,
    ) -> IssuedCredential:
        principal = await self._repository.load_principal(principal_id)
        if principal.principal_type not in {
            PrincipalType.SERVICE_ACCOUNT,
            PrincipalType.WORKER,
            PrincipalType.PLUGIN,
        }:
            raise CredentialOperationError(
                "API tokens may only be issued to service-account or workload principals"
            )
        metadata = CredentialMetadata(
            principal_id=principal.id,
            principal_type=principal.principal_type,
            name=name,
            scopes=scopes,
            audience=audience,
            expires_at=expires_at,
            rate_limit_per_minute=rate_limit_per_minute,
            issued_credential_version=principal.credential_version,
        )
        return await self._store(metadata, actor_id=actor_id)

    async def authenticate_bearer(
        self,
        authorization: str | None,
        *,
        audience: str = "amesh-api",
    ) -> ActorContext:
        if authorization is None or not authorization.startswith("Bearer "):
            await self._repository.record_authentication_failure(
                None,
                reason="missing-bearer",
            )
            raise InvalidCredential("valid bearer token required")
        token = authorization.removeprefix("Bearer ")
        try:
            credential_id, secret = parse_token_material(token)
        except ValueError as exc:
            await self._repository.record_authentication_failure(
                None,
                reason="malformed-bearer",
            )
            raise InvalidCredential("valid bearer token required") from exc
        hashes = [token_digest(secret, self._token_pepper)]
        if self._previous_token_pepper is not None:
            hashes.append(token_digest(secret, self._previous_token_pepper))
        actor = await self._repository.authenticate(
            credential_id,
            tuple(hashes),
            audience=audience,
            now=datetime.now(UTC),
        )
        if actor is None:
            raise InvalidCredential("valid bearer token required")
        return actor

    async def list(self, principal_id: UUID) -> list[CredentialMetadata]:
        return await self._repository.list_credentials(principal_id)

    async def rotate(
        self,
        credential_id: UUID,
        *,
        overlap_seconds: int,
        actor_id: str,
    ) -> IssuedCredential:
        current = await self._repository.get_credential(credential_id)
        now = datetime.now(UTC)
        if current.kind is not CredentialKind.API_TOKEN:
            raise CredentialOperationError("only API tokens can be rotated")
        if current.status is not CredentialStatus.ACTIVE or current.expires_at <= now:
            raise CredentialOperationError("only an active, unexpired token can be rotated")
        replacement = CredentialMetadata(
            principal_id=current.principal_id,
            principal_type=current.principal_type,
            name=current.name,
            scopes=current.scopes,
            audience=current.audience,
            expires_at=current.expires_at,
            rate_limit_per_minute=current.rate_limit_per_minute,
            issued_credential_version=current.issued_credential_version,
            created_at=now,
        )
        token, secret = issue_token_material(replacement.id)
        stored = StoredCredential(
            metadata=replacement,
            token_hash=token_digest(secret, self._token_pepper),
        )
        persisted = await self._repository.rotate_credential(
            credential_id,
            stored,
            overlap_expires_at=now + timedelta(seconds=overlap_seconds),
            actor_id=actor_id,
        )
        return IssuedCredential(metadata=persisted, token=SecretStr(token))

    async def exchange(
        self,
        parent_id: UUID,
        *,
        principal_id: UUID,
        scopes: tuple[str, ...],
        audience: str,
        expires_in_seconds: int,
        rate_limit_per_minute: int,
    ) -> IssuedCredential:
        parent = await self._repository.get_credential(parent_id)
        if parent.principal_id != principal_id or parent.kind is not CredentialKind.API_TOKEN:
            raise CredentialOperationError("workload token exchange requires its API token")
        if parent.principal_type not in {PrincipalType.WORKER, PrincipalType.PLUGIN}:
            raise CredentialOperationError("only worker and plugin principals may exchange tokens")
        if audience == parent.audience:
            raise CredentialOperationError("derived token audience must differ from the parent")
        if any(not credential_scope_covers(parent.scopes, scope) for scope in scopes):
            raise CredentialOperationError("derived token scopes must be a subset of the parent")
        now = datetime.now(UTC)
        expires_at = min(parent.expires_at, now + timedelta(seconds=expires_in_seconds))
        metadata = CredentialMetadata(
            principal_id=parent.principal_id,
            principal_type=parent.principal_type,
            name=f"derived-{parent.id.hex[:12]}",
            kind=CredentialKind.DERIVED_TOKEN,
            scopes=scopes,
            audience=audience,
            expires_at=expires_at,
            rate_limit_per_minute=rate_limit_per_minute,
            issued_credential_version=parent.issued_credential_version,
            parent_token_id=parent.id,
            created_at=now,
        )
        return await self._store(metadata, actor_id=str(principal_id))

    async def revoke(self, credential_id: UUID, *, actor_id: str) -> int:
        return await self._repository.revoke_credential(credential_id, actor_id=actor_id)

    async def revoke_all(self, principal_id: UUID, *, actor_id: str) -> int:
        return await self._repository.revoke_all_credentials(principal_id, actor_id=actor_id)

    async def _store(self, metadata: CredentialMetadata, *, actor_id: str) -> IssuedCredential:
        token, secret = issue_token_material(metadata.id)
        persisted = await self._repository.create_credential(
            StoredCredential(
                metadata=metadata,
                token_hash=token_digest(secret, self._token_pepper),
            ),
            actor_id=actor_id,
        )
        return IssuedCredential(metadata=persisted, token=SecretStr(token))
