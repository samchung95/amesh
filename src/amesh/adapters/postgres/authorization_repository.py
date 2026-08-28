from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    SYSTEM_TENANT_ID,
    AuthorizationPolicySnapshot,
    AuthorizationScopeType,
    NamespaceAuthorizationBoundary,
    Permission,
    PrincipalDefinition,
    PrincipalType,
    ResourceMetadata,
    RoleBinding,
    RoleDefinition,
    new_runtime_id,
)
from amesh.ports.authorization_repository import (
    AuthorizationRepository,
    LastAdministratorError,
    PolicyVersionChanged,
)

_POLICY_VERSION = text("SELECT version FROM auth_policy_state WHERE singleton = true")

_POLICY_VERSION_FOR_UPDATE = text(
    "SELECT version FROM auth_policy_state WHERE singleton = true FOR UPDATE"
)

_LIST_ROLES = text(
    """
    SELECT
        roles.name,
        roles.display_name,
        roles.description,
        roles.built_in,
        permissions.resource_type,
        permissions.action,
        permissions.effect
    FROM auth_roles AS roles
    LEFT JOIN auth_role_permissions AS permissions ON permissions.role_name = roles.name
    ORDER BY roles.name, permissions.resource_type, permissions.action, permissions.effect
    """
)

_ACTOR_GROUPS = text(
    """
    SELECT memberships.group_id
    FROM auth_group_memberships AS memberships
    JOIN auth_principals AS groups
      ON groups.id = memberships.group_id
     AND groups.principal_type = 'GROUP'
     AND groups.enabled = true
     AND groups.lifecycle = 'ACTIVE'
    JOIN auth_principals AS members
      ON members.id = memberships.member_id
     AND members.enabled = true
     AND members.lifecycle = 'ACTIVE'
    WHERE memberships.member_id = :actor_id
    ORDER BY memberships.group_id
    """
)

_ACTOR_BINDINGS = text(
    """
    SELECT
        bindings.id,
        bindings.principal_id,
        principals.principal_type,
        bindings.role_name,
        bindings.scope_type,
        tenants.slug AS tenant_slug,
        bindings.namespace_name
    FROM auth_role_bindings AS bindings
    JOIN auth_principals AS principals
      ON principals.id = bindings.principal_id
     AND principals.enabled = true
     AND principals.lifecycle = 'ACTIVE'
    LEFT JOIN tenants ON tenants.id = bindings.tenant_id
    WHERE bindings.principal_id = ANY(CAST(:principal_ids AS uuid[]))
    ORDER BY bindings.id
    """
)

_LIST_BOUNDARIES = text(
    """
    SELECT tenants.slug AS tenant_slug, boundaries.namespace_name
    FROM auth_namespace_boundaries AS boundaries
    JOIN tenants ON tenants.id = boundaries.tenant_id
    ORDER BY tenants.slug, boundaries.namespace_name
    """
)

_INSERT_AUDIT = text(
    """
    INSERT INTO audit_events (
        event_id,
        tenant_id,
        actor_id,
        action,
        resource_type,
        resource_id,
        outcome,
        source,
        evidence,
        occurred_at
    ) VALUES (
        :event_id,
        :tenant_id,
        :actor_id,
        :action,
        :resource_type,
        :resource_id,
        'SUCCESS',
        CAST(:source AS jsonb),
        CAST(:evidence AS jsonb),
        :occurred_at
    )
    """
)


class PostgresAuthorizationRepository(AuthorizationRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def policy_version(self) -> int:
        async with self._engine.connect() as connection:
            return int((await connection.execute(_POLICY_VERSION)).scalar_one())

    async def load_policy_snapshot(
        self,
        actor_id: UUID,
        *,
        expected_version: int,
    ) -> AuthorizationPolicySnapshot:
        async with self._engine.connect() as connection:
            initial_version = int((await connection.execute(_POLICY_VERSION)).scalar_one())
            if initial_version != expected_version:
                raise PolicyVersionChanged(
                    f"expected policy version {expected_version}, found {initial_version}"
                )
            role_rows = (await connection.execute(_LIST_ROLES)).mappings().all()
            group_rows = (
                (await connection.execute(_ACTOR_GROUPS, {"actor_id": actor_id})).mappings().all()
            )
            principal_ids = [actor_id, *(UUID(str(row["group_id"])) for row in group_rows)]
            binding_rows = (
                (
                    await connection.execute(
                        _ACTOR_BINDINGS,
                        {"principal_ids": principal_ids},
                    )
                )
                .mappings()
                .all()
            )
            boundary_rows = (await connection.execute(_LIST_BOUNDARIES)).mappings().all()
            final_version = int((await connection.execute(_POLICY_VERSION)).scalar_one())
        if final_version != expected_version:
            raise PolicyVersionChanged(
                f"policy changed from version {expected_version} to {final_version}"
            )
        return AuthorizationPolicySnapshot(
            version=final_version,
            roles=_roles_from_rows(role_rows),
            bindings=tuple(_to_binding(row) for row in binding_rows),
            group_ids=tuple(UUID(str(row["group_id"])) for row in group_rows),
            boundaries=tuple(
                NamespaceAuthorizationBoundary(
                    tenant_id=row["tenant_slug"],
                    namespace=row["namespace_name"],
                )
                for row in boundary_rows
            ),
        )

    async def create_principal(
        self,
        principal: PrincipalDefinition,
        *,
        actor_id: str,
    ) -> PrincipalDefinition:
        async with self._engine.begin() as connection:
            result = await connection.execute(
                text(
                    """
                    INSERT INTO auth_principals (
                        id,
                        principal_type,
                        handle,
                        display_name,
                        enabled,
                        labels,
                        annotations,
                        created_by,
                        updated_by,
                        resource_version,
                        lifecycle,
                        archived_at,
                        deleted_at,
                        created_at,
                        updated_at
                    ) VALUES (
                        :id,
                        :principal_type,
                        :handle,
                        :display_name,
                        :enabled,
                        CAST(:labels AS jsonb),
                        CAST(:annotations AS jsonb),
                        :created_by,
                        :updated_by,
                        :resource_version,
                        :lifecycle,
                        :archived_at,
                        :deleted_at,
                        :created_at,
                        :updated_at
                    )
                    RETURNING *
                    """
                ),
                {
                    "id": principal.id,
                    "principal_type": principal.principal_type.value,
                    "handle": principal.handle,
                    "display_name": principal.display_name,
                    "enabled": principal.enabled,
                    "labels": json.dumps(principal.metadata.labels),
                    "annotations": json.dumps(principal.metadata.annotations),
                    "created_by": actor_id,
                    "updated_by": actor_id,
                    "resource_version": principal.metadata.resource_version,
                    "lifecycle": principal.metadata.lifecycle.value,
                    "archived_at": principal.metadata.archived_at,
                    "deleted_at": principal.metadata.deleted_at,
                    "created_at": principal.metadata.created_at,
                    "updated_at": principal.metadata.updated_at,
                },
            )
            row = result.mappings().one()
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="principal.create",
                resource_type="principal",
                resource_id=str(principal.id),
            )
        return _to_principal(row)

    async def list_principals(self) -> list[PrincipalDefinition]:
        async with self._engine.connect() as connection:
            rows = (
                (
                    await connection.execute(
                        text("SELECT * FROM auth_principals ORDER BY principal_type, handle")
                    )
                )
                .mappings()
                .all()
            )
        return [_to_principal(row) for row in rows]

    async def add_group_member(
        self,
        group_id: UUID,
        member_id: UUID,
        *,
        actor_id: str,
    ) -> None:
        async with self._engine.begin() as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT id, principal_type, enabled
                        FROM auth_principals
                        WHERE id IN (:group_id, :member_id)
                        """
                        ),
                        {"group_id": group_id, "member_id": member_id},
                    )
                )
                .mappings()
                .all()
            )
            by_id = {UUID(str(row["id"])): row for row in rows}
            group = by_id.get(group_id)
            member = by_id.get(member_id)
            if group is None or group["principal_type"] != PrincipalType.GROUP.value:
                raise ValueError("group_id must identify an existing group")
            if member is None or not member["enabled"]:
                raise ValueError("member_id must identify an enabled principal")
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_group_memberships (group_id, member_id, created_by)
                    VALUES (:group_id, :member_id, :created_by)
                    ON CONFLICT (group_id, member_id) DO NOTHING
                    """
                ),
                {"group_id": group_id, "member_id": member_id, "created_by": actor_id},
            )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="group.member.add",
                resource_type="group",
                resource_id=str(group_id),
                evidence={"memberId": str(member_id)},
            )

    async def remove_group_member(
        self,
        group_id: UUID,
        member_id: UUID,
        *,
        actor_id: str,
    ) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(_POLICY_VERSION_FOR_UPDATE)
            group_is_instance_admin = bool(
                await connection.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM auth_role_bindings
                            WHERE principal_id = :group_id
                              AND role_name = 'instance-admin'
                              AND scope_type = 'INSTANCE'
                        )
                        """
                    ),
                    {"group_id": group_id},
                )
            )
            result = await connection.execute(
                text(
                    """
                    DELETE FROM auth_group_memberships
                    WHERE group_id = :group_id AND member_id = :member_id
                    RETURNING group_id
                    """
                ),
                {"group_id": group_id, "member_id": member_id},
            )
            if result.scalar_one_or_none() is None:
                raise LookupError("group membership does not exist")
            if group_is_instance_admin and await _effective_instance_admin_count(connection) == 0:
                raise LastAdministratorError(
                    "cannot remove the final enabled instance administrator"
                )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="group.member.remove",
                resource_type="group",
                resource_id=str(group_id),
                evidence={"memberId": str(member_id)},
            )

    async def upsert_role(
        self,
        role: RoleDefinition,
        *,
        actor_id: str,
    ) -> RoleDefinition:
        if role.built_in:
            raise ValueError("built-in roles are migration-owned and immutable")
        async with self._engine.begin() as connection:
            existing_built_in = await connection.scalar(
                text("SELECT built_in FROM auth_roles WHERE name = :name FOR UPDATE"),
                {"name": role.name},
            )
            if existing_built_in:
                raise ValueError(f"built-in role {role.name!r} is immutable")
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_roles (
                        name, display_name, description, built_in, created_by, updated_by
                    ) VALUES (
                        :name, :display_name, :description, false, :actor_id, :actor_id
                    )
                    ON CONFLICT (name) DO UPDATE
                    SET display_name = EXCLUDED.display_name,
                        description = EXCLUDED.description,
                        updated_by = EXCLUDED.updated_by,
                        updated_at = now()
                    """
                ),
                {
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "actor_id": actor_id,
                },
            )
            await connection.execute(
                text("DELETE FROM auth_role_permissions WHERE role_name = :role_name"),
                {"role_name": role.name},
            )
            if role.permissions:
                await connection.execute(
                    text(
                        """
                        INSERT INTO auth_role_permissions (
                            role_name, resource_type, action, effect
                        ) VALUES (
                            :role_name, :resource_type, :action, :effect
                        )
                        """
                    ),
                    [
                        {
                            "role_name": role.name,
                            "resource_type": permission.resource_type,
                            "action": str(permission.action),
                            "effect": permission.effect.value,
                        }
                        for permission in role.permissions
                    ],
                )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="role.upsert",
                resource_type="role",
                resource_id=role.name,
            )
        return role

    async def list_roles(self) -> list[RoleDefinition]:
        async with self._engine.connect() as connection:
            rows = (await connection.execute(_LIST_ROLES)).mappings().all()
        return list(_roles_from_rows(rows))

    async def create_binding(
        self,
        binding: RoleBinding,
        *,
        actor_id: str,
    ) -> RoleBinding:
        async with self._engine.begin() as connection:
            tenant_id = await _tenant_uuid(connection, binding.tenant_id)
            principal_type = await connection.scalar(
                text(
                    """
                    SELECT principal_type
                    FROM auth_principals
                    WHERE id = :principal_id
                      AND enabled = true
                      AND lifecycle = 'ACTIVE'
                    """
                ),
                {"principal_id": binding.principal_id},
            )
            if principal_type is None:
                raise ValueError("role binding principal must exist and be enabled")
            if principal_type != binding.principal_type.value:
                raise ValueError("role binding principal type does not match the principal")
            if not await connection.scalar(
                text("SELECT EXISTS (SELECT 1 FROM auth_roles WHERE name = :role_name)"),
                {"role_name": binding.role_name},
            ):
                raise ValueError(f"role {binding.role_name!r} does not exist")
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_role_bindings (
                        id,
                        principal_id,
                        role_name,
                        scope_type,
                        tenant_id,
                        namespace_name,
                        created_by
                    ) VALUES (
                        :id,
                        :principal_id,
                        :role_name,
                        :scope_type,
                        :tenant_id,
                        :namespace_name,
                        :created_by
                    )
                    """
                ),
                {
                    "id": binding.id,
                    "principal_id": binding.principal_id,
                    "role_name": binding.role_name,
                    "scope_type": binding.scope_type.value,
                    "tenant_id": tenant_id,
                    "namespace_name": binding.namespace,
                    "created_by": actor_id,
                },
            )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="role.binding.create",
                resource_type="role_binding",
                resource_id=str(binding.id),
                tenant_id=tenant_id,
            )
        return binding

    async def list_bindings(self) -> list[RoleBinding]:
        async with self._engine.connect() as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT
                            bindings.id,
                            bindings.principal_id,
                            principals.principal_type,
                            bindings.role_name,
                            bindings.scope_type,
                            tenants.slug AS tenant_slug,
                            bindings.namespace_name
                        FROM auth_role_bindings AS bindings
                        JOIN auth_principals AS principals ON principals.id = bindings.principal_id
                        LEFT JOIN tenants ON tenants.id = bindings.tenant_id
                        ORDER BY bindings.id
                        """
                        )
                    )
                )
                .mappings()
                .all()
            )
        return [_to_binding(row) for row in rows]

    async def delete_binding(self, binding_id: UUID, *, actor_id: str) -> None:
        async with self._engine.begin() as connection:
            await connection.execute(_POLICY_VERSION_FOR_UPDATE)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT
                            bindings.id,
                            bindings.role_name,
                            bindings.scope_type,
                            bindings.tenant_id,
                            principals.enabled
                        FROM auth_role_bindings AS bindings
                        JOIN auth_principals AS principals ON principals.id = bindings.principal_id
                        WHERE bindings.id = :binding_id
                        FOR UPDATE
                        """
                        ),
                        {"binding_id": binding_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"role binding {binding_id} does not exist")
            await connection.execute(
                text("DELETE FROM auth_role_bindings WHERE id = :binding_id"),
                {"binding_id": binding_id},
            )
            if (
                row["role_name"] == "instance-admin"
                and row["scope_type"] == AuthorizationScopeType.INSTANCE.value
                and row["enabled"]
                and await _effective_instance_admin_count(connection) == 0
            ):
                raise LastAdministratorError(
                    "cannot remove the final enabled instance administrator"
                )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="role.binding.delete",
                resource_type="role_binding",
                resource_id=str(binding_id),
                tenant_id=row["tenant_id"],
            )

    async def set_namespace_boundary(
        self,
        boundary: NamespaceAuthorizationBoundary,
        *,
        actor_id: str,
    ) -> NamespaceAuthorizationBoundary:
        async with self._engine.begin() as connection:
            tenant_id = await _tenant_uuid(connection, boundary.tenant_id)
            assert tenant_id is not None
            await connection.execute(
                text(
                    """
                    INSERT INTO auth_namespace_boundaries (
                        tenant_id, namespace_name, created_by
                    ) VALUES (
                        :tenant_id, :namespace_name, :created_by
                    )
                    ON CONFLICT (tenant_id, namespace_name) DO UPDATE
                    SET created_by = EXCLUDED.created_by,
                        created_at = now()
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "namespace_name": boundary.namespace,
                    "created_by": actor_id,
                },
            )
            await _write_audit(
                connection,
                actor_id=actor_id,
                action="authorization.boundary.set",
                resource_type="namespace",
                resource_id=boundary.namespace,
                tenant_id=tenant_id,
            )
        return boundary


def _roles_from_rows(rows: Sequence[RowMapping]) -> tuple[RoleDefinition, ...]:
    roles: list[RoleDefinition] = []
    current_name: str | None = None
    current: dict[str, object] | None = None
    permissions: list[Permission] = []
    for row in rows:
        name = str(row["name"])
        if name != current_name:
            if current is not None:
                roles.append(
                    RoleDefinition.model_validate({**current, "permissions": tuple(permissions)})
                )
            current_name = name
            current = {
                "name": name,
                "display_name": row["display_name"],
                "description": row["description"],
                "built_in": row["built_in"],
            }
            permissions = []
        if row["resource_type"] is not None:
            permissions.append(
                Permission(
                    resource_type=row["resource_type"],
                    action=row["action"],
                    effect=row["effect"],
                )
            )
    if current is not None:
        roles.append(RoleDefinition.model_validate({**current, "permissions": tuple(permissions)}))
    return tuple(roles)


def _to_principal(row: RowMapping) -> PrincipalDefinition:
    return PrincipalDefinition(
        id=row["id"],
        principal_type=row["principal_type"],
        handle=row["handle"],
        display_name=row["display_name"],
        enabled=row["enabled"],
        metadata=ResourceMetadata(
            labels=row["labels"],
            annotations=row["annotations"],
            created_by=row["created_by"],
            updated_by=row["updated_by"],
            resource_version=row["resource_version"],
            lifecycle=row["lifecycle"],
            archived_at=row["archived_at"],
            deleted_at=row["deleted_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        ),
    )


def _to_binding(row: RowMapping) -> RoleBinding:
    return RoleBinding(
        id=row["id"],
        principal_id=row["principal_id"],
        principal_type=row["principal_type"],
        role_name=row["role_name"],
        scope_type=row["scope_type"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace_name"],
    )


async def _tenant_uuid(connection: AsyncConnection, tenant_slug: str | None) -> UUID | None:
    if tenant_slug is None:
        return None
    value = await connection.scalar(
        text("SELECT id FROM tenants WHERE slug = :tenant_slug"),
        {"tenant_slug": tenant_slug},
    )
    if value is None:
        raise LookupError(f"tenant {tenant_slug!r} does not exist")
    return UUID(str(value))


async def _write_audit(
    connection: AsyncConnection,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    tenant_id: UUID | None = None,
    evidence: dict[str, object] | None = None,
) -> None:
    await connection.execute(
        _INSERT_AUDIT,
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id or SYSTEM_TENANT_ID,
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "source": json.dumps({"component": "authorization-repository"}),
            "evidence": json.dumps(evidence or {}),
            "occurred_at": datetime.now(UTC),
        },
    )


async def _effective_instance_admin_count(connection: AsyncConnection) -> int:
    value = await connection.scalar(
        text(
            """
            WITH effective_admins AS (
                SELECT principals.id AS principal_id
                FROM auth_role_bindings AS bindings
                JOIN auth_principals AS principals ON principals.id = bindings.principal_id
                WHERE bindings.role_name = 'instance-admin'
                  AND bindings.scope_type = 'INSTANCE'
                  AND principals.principal_type <> 'GROUP'
                  AND principals.enabled = true
                  AND principals.lifecycle = 'ACTIVE'
                UNION
                SELECT members.id AS principal_id
                FROM auth_role_bindings AS bindings
                JOIN auth_principals AS groups
                  ON groups.id = bindings.principal_id
                 AND groups.principal_type = 'GROUP'
                 AND groups.enabled = true
                 AND groups.lifecycle = 'ACTIVE'
                JOIN auth_group_memberships AS memberships
                  ON memberships.group_id = groups.id
                JOIN auth_principals AS members
                  ON members.id = memberships.member_id
                 AND members.enabled = true
                 AND members.lifecycle = 'ACTIVE'
                WHERE bindings.role_name = 'instance-admin'
                  AND bindings.scope_type = 'INSTANCE'
            )
            SELECT count(*) FROM effective_admins
            """
        )
    )
    return int(value or 0)
