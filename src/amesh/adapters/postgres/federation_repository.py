from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.tenant_context import resolve_active_tenant_id
from amesh.config import IdentityGroupMapping
from amesh.domain import (
    SYSTEM_TENANT_ID,
    FederatedClaims,
    FederationProtocol,
    FederationState,
    PrincipalType,
    ProviderIdentity,
    ScimResourceRecord,
    new_runtime_id,
    token_digest,
)
from amesh.ports.errors import NotFoundError
from amesh.ports.federation_repository import (
    AmbiguousFederatedIdentity,
    FederationReplayRejected,
    FederationRepository,
    FederationStateRejected,
)
from amesh.ports.repository_support import AuditWrite

from .repository_support import PostgresRepositoryBase


class PostgresFederationRepository(PostgresRepositoryBase, FederationRepository):
    def __init__(self, engine: AsyncEngine, *, token_pepper: SecretStr) -> None:
        super().__init__(engine)
        self._token_pepper = token_pepper

    def _state_hash(self, token: str) -> bytes:
        return token_digest(token, self._token_pepper)

    async def record_event(
        self,
        provider_id: str,
        *,
        action: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object] | None = None,
    ) -> None:
        async with self._services.transactions.admin() as connection:
            await self._write_audit(
                connection,
                provider_id=provider_id,
                action=action,
                outcome=outcome,
                reason=reason,
                evidence=evidence,
            )

    async def create_state(self, token: str, state: FederationState) -> None:
        async with self._services.transactions.admin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_federation_states (
                        state_hash, provider_id, protocol, request_id, nonce, code_verifier,
                        tenant_slug, return_to, expires_at
                    ) VALUES (
                        :state_hash, :provider_id, :protocol, :request_id, :nonce, :code_verifier,
                        :tenant_slug, :return_to, :expires_at
                    )
                    """
                ),
                {
                    "state_hash": self._state_hash(token),
                    "provider_id": state.provider_id,
                    "protocol": state.protocol.value,
                    "request_id": state.request_id,
                    "nonce": state.nonce,
                    "code_verifier": state.code_verifier,
                    "tenant_slug": state.tenant_slug,
                    "return_to": state.return_to,
                    "expires_at": state.expires_at,
                },
            )

    async def attach_request_id(self, token: str, request_id: str) -> None:
        async with self._services.transactions.admin() as connection:
            result = await connection.execute(
                text(
                    """
                    UPDATE auth_federation_states
                    SET request_id = :request_id
                    WHERE state_hash = :state_hash AND consumed_at IS NULL
                    RETURNING provider_id
                    """
                ),
                {"state_hash": self._state_hash(token), "request_id": request_id},
            )
            if result.scalar_one_or_none() is None:
                raise FederationStateRejected("federation state is unavailable")

    async def consume_state(
        self,
        token: str,
        *,
        provider_id: str,
        now: datetime,
    ) -> FederationState:
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE auth_federation_states
                            SET consumed_at = :now
                            WHERE state_hash = :state_hash
                              AND provider_id = :provider_id
                              AND consumed_at IS NULL
                              AND expires_at >= :now
                            RETURNING *
                            """
                        ),
                        {
                            "state_hash": self._state_hash(token),
                            "provider_id": provider_id,
                            "now": now,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                await self._write_audit(
                    connection,
                    provider_id=provider_id,
                    action="federation.state.consume",
                    outcome="REJECTED",
                    reason="missing-expired-or-replayed-state",
                )
                raise FederationStateRejected("federation state is invalid")
        return FederationState(
            provider_id=row["provider_id"],
            protocol=FederationProtocol(row["protocol"]),
            request_id=row["request_id"],
            nonce=row["nonce"],
            code_verifier=row["code_verifier"],
            tenant_slug=row["tenant_slug"],
            return_to=row["return_to"],
            expires_at=row["expires_at"],
        )

    async def record_assertion(
        self,
        provider_id: str,
        assertion_id: str,
        *,
        expires_at: datetime,
    ) -> None:
        async with self._services.transactions.admin() as connection:
            inserted = await connection.scalar(
                text(
                    """
                    INSERT INTO auth_federation_replays (provider_id, assertion_id, expires_at)
                    VALUES (:provider_id, :assertion_id, :expires_at)
                    ON CONFLICT DO NOTHING
                    RETURNING assertion_id
                    """
                ),
                {
                    "provider_id": provider_id,
                    "assertion_id": assertion_id,
                    "expires_at": expires_at,
                },
            )
            if inserted is None:
                await self._write_audit(
                    connection,
                    provider_id=provider_id,
                    action="federation.assertion.accept",
                    outcome="REJECTED",
                    reason="replay",
                )
                raise FederationReplayRejected("identity assertion was already accepted")

    async def resolve_identity(
        self,
        claims: FederatedClaims,
        *,
        group_mappings: tuple[IdentityGroupMapping, ...],
        default_tenant: str | None,
        default_role: str | None,
    ) -> ProviderIdentity:
        async with self._services.transactions.admin() as connection:
            linked = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT identities.*, principals.display_name, principals.enabled,
                                   principals.lifecycle, principals.credential_version
                            FROM auth_federated_identities AS identities
                            JOIN auth_principals AS principals ON principals.id = identities.principal_id
                            WHERE identities.provider_id = :provider_id
                              AND identities.subject = :subject
                            FOR UPDATE
                            """
                        ),
                        {"provider_id": claims.provider_id, "subject": claims.subject},
                    )
                )
                .mappings()
                .one_or_none()
            )
            email_owner = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT provider_id, subject, principal_id
                            FROM auth_federated_identities
                            WHERE normalized_email = :email
                            FOR UPDATE
                            """
                        ),
                        {"email": claims.email},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if linked is not None and linked["normalized_email"] != claims.email:
                raise AmbiguousFederatedIdentity("federated subject changed email identity")
            if email_owner is not None and (
                email_owner["provider_id"] != claims.provider_id
                or email_owner["subject"] != claims.subject
            ):
                raise AmbiguousFederatedIdentity("email is already linked to another identity")
            if linked is None:
                principal_id = new_runtime_id()
                handle = _federated_handle(claims.provider_id, claims.subject)
                await connection.execute(
                    text(
                        """
                        INSERT INTO auth_principals (
                            id, principal_type, handle, display_name, enabled, labels, annotations,
                            created_by, updated_by
                        ) VALUES (
                            :id, 'USER', :handle, :display_name, true, '{}'::jsonb,
                            CAST(:annotations AS jsonb), :actor_id, :actor_id
                        )
                        """
                    ),
                    {
                        "id": principal_id,
                        "handle": handle,
                        "display_name": claims.display,
                        "annotations": self._services.codec.dumps(
                            {
                                "amesh.io/identity-provider": claims.provider_id,
                                "amesh.io/identity-subject-sha256": sha256(
                                    claims.subject.encode("utf-8")
                                ).hexdigest(),
                            }
                        ),
                        "actor_id": f"federation:{claims.provider_id}",
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO auth_federated_identities (
                            provider_id, subject, principal_id, normalized_email
                        ) VALUES (:provider_id, :subject, :principal_id, :email)
                        """
                    ),
                    {
                        "provider_id": claims.provider_id,
                        "subject": claims.subject,
                        "principal_id": principal_id,
                        "email": claims.email,
                    },
                )
                credential_version = 1
                await self._write_audit(
                    connection,
                    provider_id=claims.provider_id,
                    action="federation.identity.provision",
                    outcome="SUCCESS",
                    reason="new-subject",
                    resource_id=str(principal_id),
                )
            else:
                if not linked["enabled"] or linked["lifecycle"] != "ACTIVE":
                    raise PermissionError("federated identity is disabled")
                principal_id = UUID(str(linked["principal_id"]))
                credential_version = int(linked["credential_version"])
                await connection.execute(
                    text(
                        """
                        UPDATE auth_principals
                        SET display_name = :display_name, updated_by = :actor_id, updated_at = :now
                        WHERE id = :principal_id
                        """
                    ),
                    {
                        "principal_id": principal_id,
                        "display_name": claims.display,
                        "actor_id": f"federation:{claims.provider_id}",
                        "now": self._services.clock.now(),
                    },
                )
            await connection.execute(
                text(
                    """
                    UPDATE auth_federated_identities
                    SET last_authenticated_at = :now
                    WHERE provider_id = :provider_id AND subject = :subject
                    """
                ),
                {
                    "provider_id": claims.provider_id,
                    "subject": claims.subject,
                    "now": self._services.clock.now(),
                },
            )
            await self._sync_groups(
                connection,
                provider_id=claims.provider_id,
                principal_id=principal_id,
                external_groups=set(claims.groups),
                mappings=group_mappings,
            )
            if default_tenant is not None and default_role is not None:
                await self._ensure_tenant_binding(
                    connection,
                    principal_id=principal_id,
                    provider_id=claims.provider_id,
                    tenant=default_tenant,
                    role=default_role,
                )
        return ProviderIdentity(
            provider=claims.provider_id,
            principal_id=principal_id,
            display=claims.display,
            credential_version=credential_version,
        )

    async def _sync_groups(
        self,
        connection: AsyncConnection,
        *,
        provider_id: str,
        principal_id: UUID,
        external_groups: set[str],
        mappings: tuple[IdentityGroupMapping, ...],
    ) -> None:
        desired_handles = {
            item.platform_group for item in mappings if item.external in external_groups
        }
        desired_rows: list[RowMapping] = []
        if desired_handles:
            desired_rows = list(
                (
                    await connection.execute(
                        text(
                            """
                            SELECT id, handle
                            FROM auth_principals
                            WHERE principal_type = 'GROUP' AND enabled = true
                              AND lifecycle = 'ACTIVE' AND handle = ANY(CAST(:handles AS text[]))
                            """
                        ),
                        {"handles": sorted(desired_handles)},
                    )
                )
                .mappings()
                .all()
            )
            found = {str(row["handle"]) for row in desired_rows}
            if found != desired_handles:
                raise NotFoundError(
                    "federated group mapping",
                    ",".join(sorted(desired_handles - found)),
                    message="federated group mapping references an unavailable platform group",
                )
        desired_ids = {UUID(str(row["id"])) for row in desired_rows}
        current_ids = {
            UUID(str(value))
            for value in (
                await connection.scalars(
                    text(
                        """
                        SELECT group_id FROM auth_federation_group_memberships
                        WHERE provider_id = :provider_id AND principal_id = :principal_id
                        """
                    ),
                    {"provider_id": provider_id, "principal_id": principal_id},
                )
            ).all()
        }
        for group_id in current_ids - desired_ids:
            await connection.execute(
                text(
                    "DELETE FROM auth_group_memberships "
                    "WHERE group_id = :group_id AND member_id = :principal_id"
                ),
                {
                    "principal_id": principal_id,
                    "group_id": group_id,
                },
            )
            await connection.execute(
                text(
                    """
                    DELETE FROM auth_federation_group_memberships
                    WHERE provider_id = :provider_id AND principal_id = :principal_id
                      AND group_id = :group_id
                    """
                ),
                {
                    "provider_id": provider_id,
                    "principal_id": principal_id,
                    "group_id": group_id,
                },
            )
        for group_id in desired_ids - current_ids:
            inserted = await connection.scalar(
                text(
                    """
                    INSERT INTO auth_group_memberships (group_id, member_id, created_by)
                    VALUES (:group_id, :principal_id, :actor_id)
                    ON CONFLICT DO NOTHING
                    RETURNING group_id
                    """
                ),
                {
                    "group_id": group_id,
                    "principal_id": principal_id,
                    "actor_id": f"federation:{provider_id}",
                },
            )
            if inserted is not None:
                await connection.execute(
                    text(
                        """
                        INSERT INTO auth_federation_group_memberships (
                            provider_id, principal_id, group_id
                        ) VALUES (:provider_id, :principal_id, :group_id)
                        """
                    ),
                    {
                        "provider_id": provider_id,
                        "principal_id": principal_id,
                        "group_id": group_id,
                    },
                )

    async def _ensure_tenant_binding(
        self,
        connection: AsyncConnection,
        *,
        principal_id: UUID,
        provider_id: str,
        tenant: str,
        role: str,
    ) -> None:
        tenant_id = await resolve_active_tenant_id(connection, tenant)
        role_exists = await connection.scalar(
            text("SELECT EXISTS (SELECT 1 FROM auth_roles WHERE name = :role)"),
            {"role": role},
        )
        if not role_exists:
            raise NotFoundError(
                "federated tenant mapping",
                f"{tenant}:{role}",
                message="federated tenant mapping references an unavailable tenant or role",
            )
        await connection.execute(
            text(
                """
                INSERT INTO auth_role_bindings (
                    id, principal_id, role_name, scope_type, tenant_id, created_by
                ) VALUES (:id, :principal_id, :role, 'TENANT', :tenant_id, :actor_id)
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "id": new_runtime_id(),
                "principal_id": principal_id,
                "role": role,
                "tenant_id": tenant_id,
                "actor_id": f"federation:{provider_id}",
            },
        )

    async def list_scim(
        self,
        provider_id: str,
        resource_type: str,
        *,
        handle: str | None = None,
    ) -> tuple[ScimResourceRecord, ...]:
        async with self._services.transactions.admin() as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT resources.*, principals.handle, principals.display_name,
                                   principals.enabled
                            FROM auth_scim_resources AS resources
                            JOIN auth_principals AS principals ON principals.id = resources.principal_id
                            WHERE resources.provider_id = :provider_id
                              AND resources.resource_type = :resource_type
                              AND (
                                  CAST(:handle AS text) IS NULL
                                  OR (resources.resource_type = 'User' AND resources.resource_name = CAST(:handle AS text))
                                  OR (resources.resource_type = 'Group' AND principals.display_name = CAST(:handle AS text))
                              )
                            ORDER BY resources.resource_name
                            """
                        ),
                        {
                            "provider_id": provider_id,
                            "resource_type": resource_type,
                            "handle": handle,
                        },
                    )
                )
                .mappings()
                .all()
            )
            return tuple([await _to_scim_record(connection, row) for row in rows])

    async def get_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
    ) -> ScimResourceRecord:
        records = await self._get_scim_rows(provider_id, resource_type, principal_id)
        if not records:
            raise NotFoundError(
                "SCIM resource",
                principal_id,
                message="SCIM resource does not exist",
            )
        return records[0]

    async def _get_scim_rows(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
    ) -> tuple[ScimResourceRecord, ...]:
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT resources.*, principals.handle, principals.display_name,
                                   principals.enabled
                            FROM auth_scim_resources AS resources
                            JOIN auth_principals AS principals ON principals.id = resources.principal_id
                            WHERE resources.provider_id = :provider_id
                              AND resources.resource_type = :resource_type
                              AND resources.principal_id = :principal_id
                            """
                        ),
                        {
                            "provider_id": provider_id,
                            "resource_type": resource_type,
                            "principal_id": principal_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            return () if row is None else (await _to_scim_record(connection, row),)

    async def create_scim(
        self,
        provider_id: str,
        resource_type: str,
        *,
        handle: str,
        resource_name: str,
        display_name: str,
        enabled: bool,
        external_id: str | None,
        tenant: str,
        role: str,
        member_ids: tuple[UUID, ...] = (),
    ) -> ScimResourceRecord:
        principal_id = new_runtime_id()
        principal_type = PrincipalType.USER if resource_type == "User" else PrincipalType.GROUP
        now = self._services.clock.now()
        async with self._services.transactions.admin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_principals (
                        id, principal_type, handle, display_name, enabled, labels, annotations,
                        created_by, updated_by, created_at, updated_at
                    ) VALUES (
                        :id, :principal_type, :handle, :display_name, :enabled, '{}'::jsonb,
                        CAST(:annotations AS jsonb), :actor_id, :actor_id, :now, :now
                    )
                    """
                ),
                {
                    "id": principal_id,
                    "principal_type": principal_type.value,
                    "handle": handle,
                    "display_name": display_name,
                    "enabled": enabled,
                    "annotations": self._services.codec.dumps(
                        {"amesh.io/scim-provider": provider_id}
                    ),
                    "actor_id": f"scim:{provider_id}",
                    "now": now,
                },
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_scim_resources (
                        provider_id, resource_type, resource_name, external_id,
                        principal_id, created_at, updated_at
                    ) VALUES (
                        :provider_id, :resource_type, :resource_name, :external_id,
                        :principal_id, :now, :now
                    )
                    """
                ),
                {
                    "provider_id": provider_id,
                    "resource_type": resource_type,
                    "resource_name": resource_name,
                    "external_id": external_id,
                    "principal_id": principal_id,
                    "now": now,
                },
            )
            if resource_type == "Group":
                await _replace_group_members(connection, principal_id, member_ids, provider_id)
            else:
                await self._ensure_tenant_binding(
                    connection,
                    principal_id=principal_id,
                    provider_id=f"scim:{provider_id}",
                    tenant=tenant,
                    role=role,
                )
            await self._write_audit(
                connection,
                provider_id=provider_id,
                action=f"scim.{resource_type.lower()}.create",
                outcome="SUCCESS",
                reason="provisioned",
                resource_id=str(principal_id),
            )
        return await self.get_scim(provider_id, resource_type, principal_id)

    async def update_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
        *,
        display_name: str | None = None,
        enabled: bool | None = None,
        member_ids: tuple[UUID, ...] | None = None,
    ) -> ScimResourceRecord:
        now = self._services.clock.now()
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT principals.enabled
                            FROM auth_scim_resources AS resources
                            JOIN auth_principals AS principals ON principals.id = resources.principal_id
                            WHERE resources.provider_id = :provider_id
                              AND resources.resource_type = :resource_type
                              AND resources.principal_id = :principal_id
                            FOR UPDATE
                            """
                        ),
                        {
                            "provider_id": provider_id,
                            "resource_type": resource_type,
                            "principal_id": principal_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise NotFoundError(
                    "SCIM resource",
                    principal_id,
                    message="SCIM resource does not exist",
                )
            next_enabled = bool(row["enabled"]) if enabled is None else enabled
            await connection.execute(
                text(
                    """
                    UPDATE auth_principals
                    SET display_name = COALESCE(:display_name, display_name),
                        enabled = :enabled,
                        credential_version = credential_version
                            + CASE WHEN enabled AND NOT :enabled THEN 1 ELSE 0 END,
                        updated_by = :actor_id,
                        updated_at = :now
                    WHERE id = :principal_id
                    """
                ),
                {
                    "display_name": display_name,
                    "enabled": next_enabled,
                    "actor_id": f"scim:{provider_id}",
                    "now": now,
                    "principal_id": principal_id,
                },
            )
            if bool(row["enabled"]) and not next_enabled:
                await connection.execute(
                    text(
                        """
                        UPDATE auth_browser_sessions
                        SET status = 'REVOKED', revoked_at = :now, revoked_by = :actor_id
                        WHERE principal_id = :principal_id AND status = 'ACTIVE'
                        """
                    ),
                    {
                        "now": now,
                        "actor_id": f"scim:{provider_id}",
                        "principal_id": principal_id,
                    },
                )
            if resource_type == "Group" and member_ids is not None:
                await _replace_group_members(connection, principal_id, member_ids, provider_id)
            await connection.execute(
                text(
                    """
                    UPDATE auth_scim_resources
                    SET version = version + 1, updated_at = :now
                    WHERE provider_id = :provider_id AND resource_type = :resource_type
                      AND principal_id = :principal_id
                    """
                ),
                {
                    "now": now,
                    "provider_id": provider_id,
                    "resource_type": resource_type,
                    "principal_id": principal_id,
                },
            )
            await self._write_audit(
                connection,
                provider_id=provider_id,
                action=f"scim.{resource_type.lower()}.update",
                outcome="SUCCESS",
                reason="patched",
                resource_id=str(principal_id),
            )
        return await self.get_scim(provider_id, resource_type, principal_id)

    async def delete_scim(
        self,
        provider_id: str,
        resource_type: str,
        principal_id: UUID,
    ) -> None:
        now = self._services.clock.now()
        async with self._services.transactions.admin() as connection:
            deleted = await connection.scalar(
                text(
                    """
                    DELETE FROM auth_scim_resources
                    WHERE provider_id = :provider_id AND resource_type = :resource_type
                      AND principal_id = :principal_id
                    RETURNING principal_id
                    """
                ),
                {
                    "provider_id": provider_id,
                    "resource_type": resource_type,
                    "principal_id": principal_id,
                },
            )
            if deleted is None:
                raise NotFoundError(
                    "SCIM resource",
                    principal_id,
                    message="SCIM resource does not exist",
                )
            await connection.execute(
                text(
                    """
                    UPDATE auth_principals
                    SET enabled = false, lifecycle = 'TOMBSTONED', deleted_at = :now,
                        credential_version = credential_version + 1,
                        updated_by = :actor_id, updated_at = :now
                    WHERE id = :principal_id
                    """
                ),
                {
                    "principal_id": principal_id,
                    "now": now,
                    "actor_id": f"scim:{provider_id}",
                },
            )
            await connection.execute(
                text(
                    """
                    UPDATE auth_browser_sessions
                    SET status = 'REVOKED', revoked_at = :now, revoked_by = :actor_id
                    WHERE principal_id = :principal_id AND status = 'ACTIVE'
                    """
                ),
                {
                    "principal_id": principal_id,
                    "now": now,
                    "actor_id": f"scim:{provider_id}",
                },
            )
            await self._write_audit(
                connection,
                provider_id=provider_id,
                action=f"scim.{resource_type.lower()}.delete",
                outcome="SUCCESS",
                reason="deprovisioned",
                resource_id=str(principal_id),
            )

    async def _write_audit(
        self,
        connection: AsyncConnection,
        *,
        provider_id: str,
        action: str,
        outcome: str,
        reason: str,
        resource_id: str | None = None,
        evidence: dict[str, object] | None = None,
    ) -> None:
        await self._services.audit.write(
            connection,
            AuditWrite(
                tenant_id=SYSTEM_TENANT_ID,
                actor_id=f"identity-provider:{provider_id}",
                action=action,
                resource_type="identity-provider",
                resource_id=resource_id or provider_id,
                source_component="federation-repository",
                outcome=outcome,
                reason=reason,
                evidence=evidence or {},
                generate_correlation_id=False,
            ),
        )


def _federated_handle(provider_id: str, subject: str) -> str:
    digest = sha256(subject.encode("utf-8")).hexdigest()[:20]
    return f"{provider_id[:40]}-{digest}"


async def _replace_group_members(
    connection: AsyncConnection,
    group_id: UUID,
    member_ids: tuple[UUID, ...],
    provider_id: str,
) -> None:
    if member_ids:
        count = int(
            await connection.scalar(
                text(
                    """
                    SELECT count(*) FROM auth_principals
                    WHERE id = ANY(CAST(:member_ids AS uuid[]))
                      AND principal_type = 'USER' AND enabled = true AND lifecycle = 'ACTIVE'
                    """
                ),
                {"member_ids": list(member_ids)},
            )
            or 0
        )
        if count != len(set(member_ids)):
            raise ValueError("SCIM group members must identify enabled users")
    await connection.execute(
        text("DELETE FROM auth_group_memberships WHERE group_id = :group_id"),
        {"group_id": group_id},
    )
    for member_id in dict.fromkeys(member_ids):
        await connection.execute(
            text(
                """
                INSERT INTO auth_group_memberships (group_id, member_id, created_by)
                VALUES (:group_id, :member_id, :actor_id)
                """
            ),
            {
                "group_id": group_id,
                "member_id": member_id,
                "actor_id": f"scim:{provider_id}",
            },
        )


async def _to_scim_record(
    connection: AsyncConnection,
    row: RowMapping,
) -> ScimResourceRecord:
    member_ids: tuple[UUID, ...] = ()
    if row["resource_type"] == "Group":
        member_ids = tuple(
            UUID(str(value))
            for value in (
                await connection.scalars(
                    text(
                        """
                        SELECT member_id FROM auth_group_memberships
                        WHERE group_id = :group_id ORDER BY member_id
                        """
                    ),
                    {"group_id": row["principal_id"]},
                )
            ).all()
        )
    return ScimResourceRecord(
        provider_id=row["provider_id"],
        resource_type=row["resource_type"],
        principal_id=row["principal_id"],
        external_id=row["external_id"],
        resource_name=row["resource_name"],
        handle=row["handle"],
        display_name=row["display_name"],
        enabled=row["enabled"],
        version=row["version"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        member_ids=member_ids,
    )
