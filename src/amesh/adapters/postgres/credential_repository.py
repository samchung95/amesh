from __future__ import annotations

import hmac
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    SYSTEM_TENANT_ID,
    ActorContext,
    CredentialKind,
    CredentialMetadata,
    CredentialStatus,
    PrincipalType,
    StoredCredential,
)
from amesh.ports.credential_repository import (
    CredentialPrincipal,
    CredentialRateLimitExceeded,
    CredentialRepository,
)
from amesh.ports.errors import NotFoundError
from amesh.ports.repository_support import AuditWrite

from .repository_support import PostgresRepositoryBase

_CREDENTIAL_COLUMNS = """
    credentials.id,
    credentials.principal_id,
    principals.principal_type,
    credentials.name,
    credentials.kind,
    credentials.scopes,
    credentials.audience,
    credentials.status,
    credentials.expires_at,
    credentials.rate_limit_per_minute,
    credentials.issued_credential_version,
    credentials.parent_token_id,
    credentials.superseded_by,
    credentials.overlap_expires_at,
    credentials.last_used_at,
    credentials.created_at,
    credentials.revoked_at
"""


class PostgresCredentialRepository(PostgresRepositoryBase, CredentialRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def load_principal(self, principal_id: UUID) -> CredentialPrincipal:
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT id, principal_type, display_name, credential_version
                            FROM auth_principals
                            WHERE id = :principal_id
                              AND enabled = true
                              AND lifecycle = 'ACTIVE'
                            """
                        ),
                        {"principal_id": principal_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "enabled principal",
                principal_id,
                message="enabled principal does not exist",
            )
        return CredentialPrincipal(
            id=UUID(str(row["id"])),
            principal_type=PrincipalType(str(row["principal_type"])),
            display=str(row["display_name"]),
            credential_version=int(row["credential_version"]),
        )

    async def create_credential(
        self,
        credential: StoredCredential,
        *,
        actor_id: str,
    ) -> CredentialMetadata:
        metadata = credential.metadata
        async with self._services.transactions.admin() as connection:
            await self._validate_issuance(connection, metadata)
            await _insert_credential(connection, credential, actor_id=actor_id)
            await self._write_audit(
                connection,
                actor_id=actor_id,
                action="credential.exchange"
                if metadata.kind is CredentialKind.DERIVED_TOKEN
                else "credential.issue",
                resource_id=str(metadata.id),
                evidence={
                    "principalId": str(metadata.principal_id),
                    "kind": metadata.kind.value,
                    "audience": metadata.audience,
                    "scopes": list(metadata.scopes),
                    "expiresAt": metadata.expires_at.isoformat(),
                },
            )
        return metadata

    async def get_credential(self, credential_id: UUID) -> CredentialMetadata:
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_CREDENTIAL_COLUMNS}
                            FROM auth_credentials AS credentials
                            JOIN auth_principals AS principals
                              ON principals.id = credentials.principal_id
                            WHERE credentials.id = :credential_id
                            """
                        ),
                        {"credential_id": credential_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            message = f"credential {credential_id} does not exist"
            raise NotFoundError("credential", credential_id, message=message)
        return _to_metadata(row)

    async def list_credentials(self, principal_id: UUID) -> list[CredentialMetadata]:
        async with self._services.transactions.admin() as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_CREDENTIAL_COLUMNS}
                            FROM auth_credentials AS credentials
                            JOIN auth_principals AS principals
                              ON principals.id = credentials.principal_id
                            WHERE credentials.principal_id = :principal_id
                            ORDER BY credentials.created_at DESC, credentials.id
                            """
                        ),
                        {"principal_id": principal_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_metadata(row) for row in rows]

    async def authenticate(
        self,
        credential_id: UUID,
        candidate_hashes: tuple[bytes, ...],
        *,
        audience: str,
        now: datetime,
    ) -> ActorContext | None:
        rate_limited = False
        actor: ActorContext | None = None
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                credentials.*,
                                principals.principal_type,
                                principals.display_name,
                                principals.enabled AS principal_enabled,
                                principals.lifecycle AS principal_lifecycle,
                                principals.credential_version,
                                parent.status AS parent_status,
                                parent.expires_at AS parent_expires_at,
                                parent.overlap_expires_at AS parent_overlap_expires_at,
                                parent.issued_credential_version AS parent_credential_version
                            FROM auth_credentials AS credentials
                            JOIN auth_principals AS principals
                              ON principals.id = credentials.principal_id
                            LEFT JOIN auth_credentials AS parent
                              ON parent.id = credentials.parent_token_id
                            WHERE credentials.id = :credential_id
                            FOR UPDATE OF credentials
                            """
                        ),
                        {"credential_id": credential_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                await self._write_audit(
                    connection,
                    actor_id="unknown",
                    action="credential.authenticate",
                    resource_id=str(credential_id),
                    outcome="FAILURE",
                    evidence={"reason": "unknown-credential"},
                )
                return None
            if not _authentication_row_is_valid(row, audience=audience, now=now):
                await self._write_audit(
                    connection,
                    actor_id=str(row["principal_id"]),
                    action="credential.authenticate",
                    resource_id=str(credential_id),
                    outcome="FAILURE",
                    evidence={"reason": "credential-not-usable"},
                )
                return None
            stored_hash = bytes(row["token_hash"])
            if not any(hmac.compare_digest(stored_hash, value) for value in candidate_hashes):
                await self._write_audit(
                    connection,
                    actor_id=str(row["principal_id"]),
                    action="credential.authenticate",
                    resource_id=str(credential_id),
                    outcome="FAILURE",
                    evidence={"reason": "digest-mismatch"},
                )
                return None
            window_started_at = now.replace(second=0, microsecond=0)
            usage = await connection.scalar(
                text(
                    """
                    INSERT INTO auth_credential_usage_windows (
                        credential_id, window_started_at, request_count
                    ) VALUES (
                        :credential_id, :window_started_at, 1
                    )
                    ON CONFLICT (credential_id, window_started_at) DO UPDATE
                    SET request_count = auth_credential_usage_windows.request_count + 1
                    WHERE auth_credential_usage_windows.request_count < :rate_limit
                    RETURNING request_count
                    """
                ),
                {
                    "credential_id": credential_id,
                    "window_started_at": window_started_at,
                    "rate_limit": int(row["rate_limit_per_minute"]),
                },
            )
            if usage is None:
                await self._write_audit(
                    connection,
                    actor_id=str(row["principal_id"]),
                    action="credential.authenticate",
                    resource_id=str(credential_id),
                    outcome="FAILURE",
                    evidence={"reason": "rate-limit-exceeded"},
                )
                rate_limited = True
            else:
                await connection.execute(
                    text(
                        "UPDATE auth_credentials SET last_used_at = :now WHERE id = :credential_id"
                    ),
                    {"credential_id": credential_id, "now": now},
                )
                await self._write_audit(
                    connection,
                    actor_id=str(row["principal_id"]),
                    action="credential.use",
                    resource_id=str(credential_id),
                    evidence={"audience": audience},
                )
                actor = ActorContext(
                    principal_id=row["principal_id"],
                    principal_type=row["principal_type"],
                    display=row["display_name"],
                    credential_id=credential_id,
                    credential_scopes=tuple(row["scopes"]),
                    credential_audience=row["audience"],
                )
        if rate_limited:
            raise CredentialRateLimitExceeded("credential request quota exceeded")
        return actor

    async def record_authentication_failure(
        self,
        credential_id: UUID | None,
        *,
        reason: str,
    ) -> None:
        async with self._services.transactions.admin() as connection:
            await self._write_audit(
                connection,
                actor_id="unknown",
                action="credential.authenticate",
                resource_id=str(credential_id) if credential_id is not None else "unparseable",
                outcome="FAILURE",
                evidence={"reason": reason},
            )

    async def rotate_credential(
        self,
        current_id: UUID,
        replacement: StoredCredential,
        *,
        overlap_expires_at: datetime,
        actor_id: str,
    ) -> CredentialMetadata:
        now = self._services.clock.now()
        if overlap_expires_at > now + timedelta(hours=24):
            raise ValueError("credential rotation overlap cannot exceed 24 hours")
        async with self._services.transactions.admin() as connection:
            current = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM auth_credentials
                            WHERE id = :credential_id
                            FOR UPDATE
                            """
                        ),
                        {"credential_id": current_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if current is None:
                message = f"credential {current_id} does not exist"
                raise NotFoundError("credential", current_id, message=message)
            if current["status"] != CredentialStatus.ACTIVE.value or current["expires_at"] <= now:
                raise ValueError("only an active, unexpired token can be rotated")
            if UUID(str(current["principal_id"])) != replacement.metadata.principal_id:
                raise ValueError("replacement token principal does not match")
            await _insert_credential(connection, replacement, actor_id=actor_id)
            await connection.execute(
                text(
                    """
                    UPDATE auth_credentials
                    SET status = 'SUPERSEDED',
                        superseded_by = :replacement_id,
                        overlap_expires_at = :overlap_expires_at
                    WHERE id = :current_id
                    """
                ),
                {
                    "current_id": current_id,
                    "replacement_id": replacement.metadata.id,
                    "overlap_expires_at": overlap_expires_at,
                },
            )
            await self._write_audit(
                connection,
                actor_id=actor_id,
                action="credential.rotate",
                resource_id=str(current_id),
                evidence={
                    "replacementId": str(replacement.metadata.id),
                    "overlapExpiresAt": overlap_expires_at.isoformat(),
                },
            )
        return replacement.metadata

    async def revoke_credential(self, credential_id: UUID, *, actor_id: str) -> int:
        async with self._services.transactions.admin() as connection:
            result = await connection.execute(
                text(
                    """
                    WITH RECURSIVE targets AS (
                        SELECT id FROM auth_credentials WHERE id = :credential_id
                        UNION ALL
                        SELECT child.id
                        FROM auth_credentials AS child
                        JOIN targets AS parent ON child.parent_token_id = parent.id
                    )
                    UPDATE auth_credentials
                    SET status = 'REVOKED',
                        superseded_by = NULL,
                        overlap_expires_at = NULL,
                        revoked_by = :actor_id,
                        revoked_at = now()
                    WHERE id IN (SELECT id FROM targets)
                      AND status <> 'REVOKED'
                    RETURNING id
                    """
                ),
                {"credential_id": credential_id, "actor_id": actor_id},
            )
            revoked = len(result.mappings().all())
            if revoked == 0 and not await connection.scalar(
                text("SELECT EXISTS (SELECT 1 FROM auth_credentials WHERE id = :credential_id)"),
                {"credential_id": credential_id},
            ):
                message = f"credential {credential_id} does not exist"
                raise NotFoundError("credential", credential_id, message=message)
            await self._write_audit(
                connection,
                actor_id=actor_id,
                action="credential.revoke",
                resource_id=str(credential_id),
                evidence={"revokedCount": revoked},
            )
        return revoked

    async def revoke_all_credentials(self, principal_id: UUID, *, actor_id: str) -> int:
        async with self._services.transactions.admin() as connection:
            principal = await connection.scalar(
                text(
                    """
                    UPDATE auth_principals
                    SET credential_version = credential_version + 1
                    WHERE id = :principal_id
                    RETURNING credential_version
                    """
                ),
                {"principal_id": principal_id},
            )
            if principal is None:
                message = f"principal {principal_id} does not exist"
                raise NotFoundError("principal", principal_id, message=message)
            result = await connection.execute(
                text(
                    """
                    UPDATE auth_credentials
                    SET status = 'REVOKED',
                        superseded_by = NULL,
                        overlap_expires_at = NULL,
                        revoked_by = :actor_id,
                        revoked_at = now()
                    WHERE principal_id = :principal_id
                      AND status <> 'REVOKED'
                    RETURNING id
                    """
                ),
                {"principal_id": principal_id, "actor_id": actor_id},
            )
            revoked = len(result.mappings().all())
            await self._write_audit(
                connection,
                actor_id=actor_id,
                action="credential.revoke_all",
                resource_id=str(principal_id),
                evidence={"credentialVersion": int(principal), "revokedCount": revoked},
            )
        return revoked

    async def _write_audit(
        self,
        connection: AsyncConnection,
        *,
        actor_id: str,
        action: str,
        resource_id: str,
        evidence: dict[str, object],
        outcome: str = "SUCCESS",
    ) -> None:
        await self._services.audit.write(
            connection,
            AuditWrite(
                tenant_id=SYSTEM_TENANT_ID,
                actor_id=actor_id,
                action=action,
                resource_type="credential",
                resource_id=resource_id,
                source_component="credential-repository",
                outcome=outcome,
                evidence=evidence,
                generate_correlation_id=False,
            ),
        )

    async def _validate_issuance(
        self,
        connection: AsyncConnection,
        metadata: CredentialMetadata,
    ) -> None:
        principal = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT principal_type, credential_version
                        FROM auth_principals
                        WHERE id = :principal_id
                          AND enabled = true
                          AND lifecycle = 'ACTIVE'
                        FOR UPDATE
                        """
                    ),
                    {"principal_id": metadata.principal_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if principal is None:
            raise NotFoundError(
                "enabled principal",
                metadata.principal_id,
                message="enabled principal does not exist",
            )
        if principal["principal_type"] != metadata.principal_type.value:
            raise ValueError("credential principal type does not match")
        if int(principal["credential_version"]) != metadata.issued_credential_version:
            raise ValueError("credential version changed before issuance")
        if metadata.parent_token_id is None:
            return
        parent = (
            (
                await connection.execute(
                    text("SELECT * FROM auth_credentials WHERE id = :parent_id FOR UPDATE"),
                    {"parent_id": metadata.parent_token_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        now = self._services.clock.now()
        if (
            parent is None
            or UUID(str(parent["principal_id"])) != metadata.principal_id
            or parent["kind"] != CredentialKind.API_TOKEN.value
            or parent["status"] != CredentialStatus.ACTIVE.value
            or parent["expires_at"] <= now
            or metadata.expires_at > min(parent["expires_at"], now + timedelta(hours=1))
        ):
            raise ValueError("derived token parent is no longer eligible")


def _authentication_row_is_valid(row: RowMapping, *, audience: str, now: datetime) -> bool:
    if not row["principal_enabled"] or row["principal_lifecycle"] != "ACTIVE":
        return False
    if int(row["issued_credential_version"]) != int(row["credential_version"]):
        return False
    if row["audience"] != audience or row["expires_at"] <= now:
        return False
    status = row["status"]
    if status == CredentialStatus.REVOKED.value:
        return False
    if status == CredentialStatus.SUPERSEDED.value and row["overlap_expires_at"] <= now:
        return False
    if row["kind"] == CredentialKind.DERIVED_TOKEN.value:
        parent_status = row["parent_status"]
        if parent_status is None or row["parent_expires_at"] <= now:
            return False
        if int(row["parent_credential_version"]) != int(row["credential_version"]):
            return False
        if parent_status == CredentialStatus.REVOKED.value:
            return False
        if (
            parent_status == CredentialStatus.SUPERSEDED.value
            and row["parent_overlap_expires_at"] <= now
        ):
            return False
    return True


async def _insert_credential(
    connection: AsyncConnection,
    credential: StoredCredential,
    *,
    actor_id: str,
) -> None:
    metadata = credential.metadata
    await connection.execute(
        text(
            """
            INSERT INTO auth_credentials (
                id,
                principal_id,
                name,
                kind,
                token_hash,
                scopes,
                audience,
                status,
                expires_at,
                rate_limit_per_minute,
                issued_credential_version,
                parent_token_id,
                superseded_by,
                overlap_expires_at,
                last_used_at,
                created_by,
                created_at,
                revoked_at
            ) VALUES (
                :id,
                :principal_id,
                :name,
                :kind,
                :token_hash,
                :scopes,
                :audience,
                :status,
                :expires_at,
                :rate_limit_per_minute,
                :issued_credential_version,
                :parent_token_id,
                :superseded_by,
                :overlap_expires_at,
                :last_used_at,
                :created_by,
                :created_at,
                :revoked_at
            )
            """
        ),
        {
            "id": metadata.id,
            "principal_id": metadata.principal_id,
            "name": metadata.name,
            "kind": metadata.kind.value,
            "token_hash": credential.token_hash,
            "scopes": list(metadata.scopes),
            "audience": metadata.audience,
            "status": metadata.status.value,
            "expires_at": metadata.expires_at,
            "rate_limit_per_minute": metadata.rate_limit_per_minute,
            "issued_credential_version": metadata.issued_credential_version,
            "parent_token_id": metadata.parent_token_id,
            "superseded_by": metadata.superseded_by,
            "overlap_expires_at": metadata.overlap_expires_at,
            "last_used_at": metadata.last_used_at,
            "created_by": actor_id,
            "created_at": metadata.created_at,
            "revoked_at": metadata.revoked_at,
        },
    )


def _to_metadata(row: RowMapping) -> CredentialMetadata:
    return CredentialMetadata(
        id=row["id"],
        principal_id=row["principal_id"],
        principal_type=row["principal_type"],
        name=row["name"],
        kind=row["kind"],
        scopes=tuple(row["scopes"]),
        audience=row["audience"],
        status=row["status"],
        expires_at=row["expires_at"],
        rate_limit_per_minute=row["rate_limit_per_minute"],
        issued_credential_version=row["issued_credential_version"],
        parent_token_id=row["parent_token_id"],
        superseded_by=row["superseded_by"],
        overlap_expires_at=row["overlap_expires_at"],
        last_used_at=row["last_used_at"],
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
    )
