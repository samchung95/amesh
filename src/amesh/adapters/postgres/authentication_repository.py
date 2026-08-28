from __future__ import annotations

import hmac
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    SYSTEM_TENANT_ID,
    ActorContext,
    BrowserSession,
    PrincipalDefinition,
    PrincipalType,
    new_runtime_id,
)
from amesh.ports.authentication_repository import (
    AuthenticationRepository,
    LocalIdentityRecord,
    SessionAuthenticationRecord,
)

_BOOTSTRAP_LOCK = 280465470403


class PostgresAuthenticationRepository(AuthenticationRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def bootstrap_local_admin(
        self,
        principal: PrincipalDefinition,
        password_hash: str,
    ) -> PrincipalDefinition:
        if principal.principal_type is not PrincipalType.USER:
            raise ValueError("local bootstrap principal must be a user")
        async with self._engine.begin() as connection:
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(:lock)"), {"lock": _BOOTSTRAP_LOCK}
            )
            existing = int(
                await connection.scalar(text("SELECT count(*) FROM auth_local_credentials")) or 0
            )
            if existing:
                raise ValueError("local administrator bootstrap has already been completed")
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_principals (
                        id, principal_type, handle, display_name, enabled, labels, annotations,
                        created_by, updated_by, resource_version, lifecycle,
                        archived_at, deleted_at, created_at, updated_at
                    ) VALUES (
                        :id, 'USER', :handle, :display_name, true,
                        CAST(:labels AS jsonb), CAST(:annotations AS jsonb),
                        'bootstrap:local', 'bootstrap:local', :resource_version, :lifecycle,
                        :archived_at, :deleted_at, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "id": principal.id,
                    "handle": principal.handle,
                    "display_name": principal.display_name,
                    "labels": json.dumps(principal.metadata.labels),
                    "annotations": json.dumps(principal.metadata.annotations),
                    "resource_version": principal.metadata.resource_version,
                    "lifecycle": principal.metadata.lifecycle.value,
                    "archived_at": principal.metadata.archived_at,
                    "deleted_at": principal.metadata.deleted_at,
                    "created_at": principal.metadata.created_at,
                    "updated_at": principal.metadata.updated_at,
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_local_credentials (
                        principal_id, password_hash, created_by, updated_by
                    ) VALUES (:principal_id, :password_hash, 'bootstrap:local', 'bootstrap:local')
                    """
                ),
                {"principal_id": principal.id, "password_hash": password_hash},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_role_bindings (
                        id, principal_id, role_name, scope_type, created_by
                    ) VALUES (
                        :id, :principal_id, 'instance-admin', 'INSTANCE', 'bootstrap:local'
                    )
                    """
                ),
                {"id": new_runtime_id(), "principal_id": principal.id},
            )
            await _write_auth_audit(
                connection,
                actor_id=str(principal.id),
                action="authentication.bootstrap",
                resource_id=str(principal.id),
                outcome="SUCCESS",
                evidence={"provider": "local"},
            )
        return principal

    async def load_local_identity(self, identifier: str) -> LocalIdentityRecord | None:
        async with self._engine.connect() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                principals.id,
                                principals.display_name,
                                principals.credential_version,
                                credentials.password_hash,
                                credentials.failed_attempts,
                                credentials.locked_until
                            FROM auth_principals AS principals
                            JOIN auth_local_credentials AS credentials
                              ON credentials.principal_id = principals.id
                            WHERE principals.principal_type = 'USER'
                              AND principals.handle = :identifier
                              AND principals.enabled = true
                              AND principals.lifecycle = 'ACTIVE'
                            """
                        ),
                        {"identifier": identifier},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            return None
        return LocalIdentityRecord(
            principal_id=row["id"],
            display_name=row["display_name"],
            password_hash=row["password_hash"],
            failed_attempts=row["failed_attempts"],
            locked_until=row["locked_until"],
            credential_version=row["credential_version"],
        )

    async def allow_login_source(
        self,
        source_hash: bytes,
        *,
        now: datetime,
        limit_per_minute: int,
    ) -> bool:
        window = now.replace(second=0, microsecond=0)
        async with self._engine.begin() as connection:
            count = int(
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO auth_login_rate_windows (
                                source_hash, window_started_at, request_count
                            ) VALUES (:source_hash, :window_started_at, 1)
                            ON CONFLICT (source_hash, window_started_at) DO UPDATE
                            SET request_count = auth_login_rate_windows.request_count + 1
                            RETURNING request_count
                            """
                        ),
                        {"source_hash": source_hash, "window_started_at": window},
                    )
                ).scalar_one()
            )
            allowed = count <= limit_per_minute
            if not allowed:
                await _write_auth_audit(
                    connection,
                    actor_id="anonymous",
                    action="authentication.login",
                    resource_id="local",
                    outcome="FAILURE",
                    evidence={"provider": "local", "reason": "source-rate-limit"},
                )
        return allowed

    async def record_login_failure(
        self,
        identifier: str,
        *,
        now: datetime,
        max_failures: int,
        lock_seconds: int,
        reason: str,
    ) -> bool:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT principals.id, credentials.failed_attempts
                            FROM auth_principals AS principals
                            JOIN auth_local_credentials AS credentials
                              ON credentials.principal_id = principals.id
                            WHERE principals.principal_type = 'USER'
                              AND principals.handle = :identifier
                            FOR UPDATE OF credentials
                            """
                        ),
                        {"identifier": identifier},
                    )
                )
                .mappings()
                .one_or_none()
            )
            locked = False
            principal_id: UUID | None = None
            if row is not None:
                principal_id = row["id"]
                failures = int(row["failed_attempts"]) + 1
                locked = failures >= max_failures
                await connection.execute(
                    text(
                        """
                        UPDATE auth_local_credentials
                        SET failed_attempts = :failures,
                            locked_until = :locked_until,
                            updated_at = :now,
                            updated_by = 'authentication:login'
                        WHERE principal_id = :principal_id
                        """
                    ),
                    {
                        "failures": failures,
                        "locked_until": now + timedelta(seconds=lock_seconds) if locked else None,
                        "now": now,
                        "principal_id": principal_id,
                    },
                )
            await _write_auth_audit(
                connection,
                actor_id=str(principal_id) if principal_id is not None else "anonymous",
                action="authentication.login",
                resource_id=str(principal_id) if principal_id is not None else "local",
                outcome="FAILURE",
                evidence={"provider": "local", "reason": reason, "locked": locked},
            )
        return locked

    async def create_browser_session(
        self,
        session: BrowserSession,
        *,
        token_hash: bytes,
        csrf_hash: bytes,
        provider: str,
    ) -> ActorContext:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT id, principal_type, display_name, credential_version
                            FROM auth_principals
                            WHERE id = :principal_id
                              AND principal_type = 'USER'
                              AND enabled = true
                              AND lifecycle = 'ACTIVE'
                            FOR UPDATE
                            """
                        ),
                        {"principal_id": session.principal_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None or int(row["credential_version"]) != session.issued_credential_version:
                raise PermissionError("identity is no longer eligible for a browser session")
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_browser_sessions (
                        id, principal_id, provider, token_hash, csrf_hash,
                        issued_credential_version, created_at, last_seen_at,
                        idle_expires_at, absolute_expires_at, rotated_at
                    ) VALUES (
                        :id, :principal_id, :provider, :token_hash, :csrf_hash,
                        :credential_version, :created_at, :created_at,
                        :idle_expires_at, :absolute_expires_at, :rotated_at
                    )
                    """
                ),
                {
                    "id": session.id,
                    "principal_id": session.principal_id,
                    "provider": provider,
                    "token_hash": token_hash,
                    "csrf_hash": csrf_hash,
                    "credential_version": session.issued_credential_version,
                    "created_at": session.created_at,
                    "idle_expires_at": session.idle_expires_at,
                    "absolute_expires_at": session.absolute_expires_at,
                    "rotated_at": session.rotated_at,
                },
            )
            await connection.execute(
                text(
                    """
                    UPDATE auth_local_credentials
                    SET failed_attempts = 0,
                        locked_until = NULL,
                        last_authenticated_at = :now,
                        updated_at = :now,
                        updated_by = 'authentication:login'
                    WHERE principal_id = :principal_id
                    """
                ),
                {"now": session.created_at, "principal_id": session.principal_id},
            )
            await _write_auth_audit(
                connection,
                actor_id=str(session.principal_id),
                action="authentication.login",
                resource_id=str(session.id),
                outcome="SUCCESS",
                evidence={"provider": provider},
            )
        return ActorContext(
            principal_id=row["id"],
            principal_type=PrincipalType.USER,
            display=row["display_name"],
            credential_id=session.id,
            credential_scopes=("*:*",),
            credential_audience="amesh-api",
        )

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
    ) -> SessionAuthenticationRecord | None:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                sessions.*,
                                principals.principal_type,
                                principals.display_name,
                                principals.enabled,
                                principals.lifecycle,
                                principals.credential_version
                            FROM auth_browser_sessions AS sessions
                            JOIN auth_principals AS principals ON principals.id = sessions.principal_id
                            WHERE sessions.id = :session_id
                            FOR UPDATE OF sessions
                            """
                        ),
                        {"session_id": session_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                return None
            current_matches = hmac.compare_digest(bytes(row["token_hash"]), token_hash)
            previous_matches = (
                row["previous_token_hash"] is not None
                and row["previous_token_valid_until"] is not None
                and now < row["previous_token_valid_until"]
                and hmac.compare_digest(bytes(row["previous_token_hash"]), token_hash)
            )
            csrf_matches = csrf_hash is not None and hmac.compare_digest(
                bytes(row["csrf_hash"]), csrf_hash
            )
            eligible = (
                row["status"] == "ACTIVE"
                and row["enabled"]
                and row["lifecycle"] == "ACTIVE"
                and int(row["credential_version"]) == int(row["issued_credential_version"])
                and now < row["idle_expires_at"]
                and now < row["absolute_expires_at"]
                and (current_matches or previous_matches)
                and (not require_csrf or csrf_matches)
            )
            if not eligible:
                if row["status"] == "ACTIVE" and (
                    now >= row["idle_expires_at"]
                    or now >= row["absolute_expires_at"]
                    or int(row["credential_version"]) != int(row["issued_credential_version"])
                    or not row["enabled"]
                    or row["lifecycle"] != "ACTIVE"
                ):
                    await connection.execute(
                        text(
                            """
                            UPDATE auth_browser_sessions
                            SET status = 'REVOKED', revoked_at = :now, revoked_by = 'authentication:fence'
                            WHERE id = :session_id AND status = 'ACTIVE'
                            """
                        ),
                        {"now": now, "session_id": session_id},
                    )
                return None
            absolute_expires_at: datetime = row["absolute_expires_at"]
            idle_expires_at = min(now + timedelta(seconds=idle_seconds), absolute_expires_at)
            rotate = current_matches and now >= row["rotated_at"] + timedelta(
                seconds=rotation_seconds
            )
            if rotate:
                await connection.execute(
                    text(
                        """
                        UPDATE auth_browser_sessions
                        SET previous_token_hash = token_hash,
                            previous_token_valid_until = :previous_valid_until,
                            token_hash = :replacement_token_hash,
                            rotated_at = :now,
                            last_seen_at = :now,
                            idle_expires_at = :idle_expires_at
                        WHERE id = :session_id
                        """
                    ),
                    {
                        "previous_valid_until": now + timedelta(seconds=overlap_seconds),
                        "replacement_token_hash": replacement_token_hash,
                        "now": now,
                        "idle_expires_at": idle_expires_at,
                        "session_id": session_id,
                    },
                )
            else:
                await connection.execute(
                    text(
                        """
                        UPDATE auth_browser_sessions
                        SET last_seen_at = :now, idle_expires_at = :idle_expires_at
                        WHERE id = :session_id
                        """
                    ),
                    {"now": now, "idle_expires_at": idle_expires_at, "session_id": session_id},
                )
        actor = ActorContext(
            principal_id=row["principal_id"],
            principal_type=PrincipalType.USER,
            display=row["display_name"],
            credential_id=session_id,
            credential_scopes=("*:*",),
            credential_audience="amesh-api",
        )
        return SessionAuthenticationRecord(
            actor=actor,
            session_id=session_id,
            rotated=rotate,
            idle_expires_at=idle_expires_at,
            absolute_expires_at=absolute_expires_at,
        )

    async def revoke_session(self, session_id: UUID, *, actor_id: str) -> bool:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            principal_id = (
                await connection.execute(
                    text(
                        """
                        UPDATE auth_browser_sessions
                        SET status = 'REVOKED', revoked_at = :now, revoked_by = :actor_id
                        WHERE id = :session_id AND status = 'ACTIVE'
                        RETURNING principal_id
                        """
                    ),
                    {"now": now, "actor_id": actor_id, "session_id": session_id},
                )
            ).scalar_one_or_none()
            if principal_id is not None:
                await _write_auth_audit(
                    connection,
                    actor_id=actor_id,
                    action="authentication.logout",
                    resource_id=str(session_id),
                    outcome="SUCCESS",
                    evidence={"principalId": str(principal_id)},
                )
        return principal_id is not None

    async def revoke_all_sessions(self, principal_id: UUID, *, actor_id: str) -> int:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    UPDATE auth_browser_sessions
                    SET status = 'REVOKED', revoked_at = :now, revoked_by = :actor_id
                    WHERE principal_id = :principal_id AND status = 'ACTIVE'
                    """
                ),
                {"now": now, "actor_id": actor_id, "principal_id": principal_id},
            )
            count = int(result.rowcount)
            await _write_auth_audit(
                connection,
                actor_id=actor_id,
                action="authentication.session.revoke_all",
                resource_id=str(principal_id),
                outcome="SUCCESS",
                evidence={"revokedCount": count},
            )
        return count

    async def set_local_password(
        self,
        principal_id: UUID,
        password_hash: str,
        *,
        actor_id: str,
    ) -> int:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            principal_type = await connection.scalar(
                text(
                    """
                    SELECT principal_type FROM auth_principals
                    WHERE id = :principal_id AND enabled = true AND lifecycle = 'ACTIVE'
                    FOR UPDATE
                    """
                ),
                {"principal_id": principal_id},
            )
            if principal_type is None:
                raise LookupError("user principal does not exist")
            if principal_type != PrincipalType.USER.value:
                raise ValueError("local passwords may only be assigned to user principals")
            await connection.execute(
                text(
                    """
                    UPDATE auth_principals
                    SET credential_version = credential_version + 1,
                        resource_version = resource_version + 1,
                        updated_at = :now,
                        updated_by = :actor_id
                    WHERE id = :principal_id
                    """
                ),
                {"now": now, "actor_id": actor_id, "principal_id": principal_id},
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_local_credentials (
                        principal_id, password_hash, created_by, updated_by,
                        password_changed_at, created_at, updated_at
                    ) VALUES (
                        :principal_id, :password_hash, :actor_id, :actor_id,
                        :now, :now, :now
                    )
                    ON CONFLICT (principal_id) DO UPDATE
                    SET password_hash = EXCLUDED.password_hash,
                        failed_attempts = 0,
                        locked_until = NULL,
                        password_changed_at = EXCLUDED.password_changed_at,
                        updated_by = EXCLUDED.updated_by,
                        updated_at = EXCLUDED.updated_at
                    """
                ),
                {
                    "principal_id": principal_id,
                    "password_hash": password_hash,
                    "actor_id": actor_id,
                    "now": now,
                },
            )
            result = await connection.execute(
                text(
                    """
                    UPDATE auth_browser_sessions
                    SET status = 'REVOKED', revoked_at = :now, revoked_by = :actor_id
                    WHERE principal_id = :principal_id AND status = 'ACTIVE'
                    """
                ),
                {"now": now, "actor_id": actor_id, "principal_id": principal_id},
            )
            revoked = int(result.rowcount)
            await _write_auth_audit(
                connection,
                actor_id=actor_id,
                action="authentication.password.rotate",
                resource_id=str(principal_id),
                outcome="SUCCESS",
                evidence={"revokedSessions": revoked},
            )
        return revoked

    async def update_password_hash(self, principal_id: UUID, password_hash: str) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    UPDATE auth_local_credentials
                    SET password_hash = :password_hash,
                        updated_at = now(),
                        updated_by = 'authentication:rehash'
                    WHERE principal_id = :principal_id
                    """
                ),
                {"password_hash": password_hash, "principal_id": principal_id},
            )


async def _write_auth_audit(
    connection: AsyncConnection,
    *,
    actor_id: str,
    action: str,
    resource_id: str,
    outcome: str,
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, 'authentication', :resource_id,
                :outcome, CAST(:source AS jsonb), CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": SYSTEM_TENANT_ID,
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "outcome": outcome,
            "source": json.dumps({"component": "authentication-repository"}),
            "evidence": json.dumps(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
