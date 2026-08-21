from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.tenant_context import tenant_admin_transaction
from amesh.domain import (
    SYSTEM_TENANT_ID,
    ResourceLifecycle,
    ResourceMetadata,
    TenantDefinition,
    TenantExport,
    TenantPolicy,
    TenantStatus,
    new_runtime_id,
)
from amesh.ports.tenant_repository import TenantRepository, TenantUnavailableError

from .quota import (
    TenantQuotaType,
    release_tenant_quota,
    reserve_tenant_quota,
)

_TENANT_COLUMNS = """
    id,
    slug,
    display_name,
    status,
    settings,
    storage_prefix,
    labels,
    annotations,
    created_by,
    updated_by,
    version,
    lifecycle,
    archived_at,
    deleted_at,
    created_at,
    updated_at
"""


class PostgresTenantRepository(TenantRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create(
        self,
        tenant: TenantDefinition,
        *,
        actor_id: str,
    ) -> TenantDefinition:
        try:
            async with tenant_admin_transaction(self._engine) as connection:
                row = (
                    (
                        await connection.execute(
                            text(
                                f"""
                                INSERT INTO tenants (
                                    id,
                                    slug,
                                    display_name,
                                    status,
                                    settings,
                                    storage_prefix,
                                    labels,
                                    annotations,
                                    created_by,
                                    updated_by,
                                    version,
                                    lifecycle,
                                    created_at,
                                    updated_at
                                ) VALUES (
                                    :id,
                                    :slug,
                                    :display_name,
                                    :status,
                                    CAST(:settings AS jsonb),
                                    :storage_prefix,
                                    CAST(:labels AS jsonb),
                                    CAST(:annotations AS jsonb),
                                    :actor_id,
                                    :actor_id,
                                    :version,
                                    :lifecycle,
                                    :created_at,
                                    :updated_at
                                )
                                RETURNING {_TENANT_COLUMNS}
                                """
                            ),
                            {
                                "id": tenant.id,
                                "slug": tenant.slug,
                                "display_name": tenant.display_name,
                                "status": tenant.status.value,
                                "settings": tenant.policy.model_dump_json(),
                                "storage_prefix": tenant.storage_prefix,
                                "labels": json.dumps(tenant.metadata.labels),
                                "annotations": json.dumps(tenant.metadata.annotations),
                                "actor_id": actor_id,
                                "version": tenant.metadata.resource_version,
                                "lifecycle": tenant.metadata.lifecycle.value,
                                "created_at": tenant.metadata.created_at,
                                "updated_at": tenant.metadata.updated_at,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
                await _write_tenant_audit(
                    connection,
                    tenant_id=tenant.id,
                    actor_id=actor_id,
                    action="tenant.create",
                    resource_id=tenant.slug,
                )
        except IntegrityError as exc:
            raise ValueError(f"tenant {tenant.slug!r} already exists") from exc
        return _to_tenant(row)

    async def get(self, tenant_slug: str) -> TenantDefinition:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_TENANT_COLUMNS}
                            FROM tenants
                            WHERE slug = :tenant_slug
                              AND id <> :system_tenant_id
                            """
                        ),
                        {
                            "tenant_slug": tenant_slug,
                            "system_tenant_id": SYSTEM_TENANT_ID,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"tenant {tenant_slug!r} does not exist")
        return _to_tenant(row)

    async def require_active(self, tenant_slug: str) -> TenantDefinition:
        try:
            tenant = await self.get(tenant_slug)
        except LookupError as exc:
            raise TenantUnavailableError("tenant unavailable") from exc
        if (
            tenant.status is not TenantStatus.ACTIVE
            or tenant.metadata.lifecycle is not ResourceLifecycle.ACTIVE
        ):
            raise TenantUnavailableError("tenant unavailable")
        return tenant

    async def list(self) -> list[TenantDefinition]:
        async with tenant_admin_transaction(self._engine) as connection:
            rows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_TENANT_COLUMNS}
                            FROM tenants
                            WHERE id <> :system_tenant_id
                            ORDER BY slug
                            """
                        ),
                        {"system_tenant_id": SYSTEM_TENANT_ID},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_tenant(row) for row in rows]

    async def set_status(
        self,
        tenant_slug: str,
        status: TenantStatus,
        *,
        actor_id: str,
    ) -> TenantDefinition:
        lifecycle = (
            ResourceLifecycle.TOMBSTONED
            if status is TenantStatus.TOMBSTONED
            else ResourceLifecycle.ACTIVE
        )
        action = {
            TenantStatus.ACTIVE: "tenant.restore",
            TenantStatus.SUSPENDED: "tenant.suspend",
            TenantStatus.TOMBSTONED: "tenant.delete",
        }[status]
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            UPDATE tenants
                            SET status = :status,
                                lifecycle = :lifecycle,
                                deleted_at = CASE
                                    WHEN :status = 'TOMBSTONED' THEN now()
                                    ELSE NULL
                                END,
                                updated_by = :actor_id,
                                version = version + 1,
                                updated_at = now()
                            WHERE slug = :tenant_slug
                              AND id <> :system_tenant_id
                            RETURNING {_TENANT_COLUMNS}
                            """
                        ),
                        {
                            "tenant_slug": tenant_slug,
                            "system_tenant_id": SYSTEM_TENANT_ID,
                            "status": status.value,
                            "lifecycle": lifecycle.value,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"tenant {tenant_slug!r} does not exist")
            await _write_tenant_audit(
                connection,
                tenant_id=UUID(str(row["id"])),
                actor_id=actor_id,
                action=action,
                resource_id=tenant_slug,
            )
        return _to_tenant(row)

    async def set_policy(
        self,
        tenant_slug: str,
        policy: TenantPolicy,
        *,
        actor_id: str,
    ) -> TenantDefinition:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            UPDATE tenants
                            SET settings = CAST(:settings AS jsonb),
                                updated_by = :actor_id,
                                version = version + 1,
                                updated_at = now()
                            WHERE slug = :tenant_slug
                              AND id <> :system_tenant_id
                              AND lifecycle <> 'TOMBSTONED'
                            RETURNING {_TENANT_COLUMNS}
                            """
                        ),
                        {
                            "tenant_slug": tenant_slug,
                            "system_tenant_id": SYSTEM_TENANT_ID,
                            "settings": policy.model_dump_json(),
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"active tenant {tenant_slug!r} does not exist")
            await _write_tenant_audit(
                connection,
                tenant_id=UUID(str(row["id"])),
                actor_id=actor_id,
                action="tenant.policy.update",
                resource_id=tenant_slug,
            )
        return _to_tenant(row)

    async def export(self, tenant_slug: str, *, actor_id: str) -> TenantExport:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_TENANT_COLUMNS}
                            FROM tenants
                            WHERE slug = :tenant_slug
                              AND id <> :system_tenant_id
                            FOR UPDATE
                            """
                        ),
                        {
                            "tenant_slug": tenant_slug,
                            "system_tenant_id": SYSTEM_TENANT_ID,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError(f"tenant {tenant_slug!r} does not exist")
            tenant = _to_tenant(row)
            counts_row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT
                                (SELECT count(*) FROM namespaces WHERE tenant_id = :tenant_id)
                                    AS namespaces,
                                (SELECT count(*) FROM flows WHERE tenant_id = :tenant_id) AS flows,
                                (SELECT count(*) FROM executions WHERE tenant_id = :tenant_id)
                                    AS executions,
                                (SELECT count(*) FROM audit_events WHERE tenant_id = :tenant_id)
                                    AS audit_events
                            """
                        ),
                        {"tenant_id": tenant.id},
                    )
                )
                .mappings()
                .one()
            )
            exported = TenantExport(
                tenant=tenant,
                resource_counts={name: int(value) for name, value in counts_row.items()},
                exported_by=actor_id,
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO tenant_exports (
                        export_id, tenant_id, snapshot, resource_counts, exported_by, exported_at
                    ) VALUES (
                        :export_id,
                        :tenant_id,
                        CAST(:snapshot AS jsonb),
                        CAST(:resource_counts AS jsonb),
                        :exported_by,
                        :exported_at
                    )
                    """
                ),
                {
                    "export_id": exported.export_id,
                    "tenant_id": tenant.id,
                    "snapshot": tenant.model_dump_json(),
                    "resource_counts": json.dumps(exported.resource_counts),
                    "exported_by": actor_id,
                    "exported_at": exported.exported_at,
                },
            )
            await _write_tenant_audit(
                connection,
                tenant_id=tenant.id,
                actor_id=actor_id,
                action="tenant.export",
                resource_id=tenant_slug,
                evidence={"exportId": str(exported.export_id)},
            )
        return exported

    async def list_active_for_worker_group(self, worker_group: str) -> Sequence[str]:
        async with self._engine.begin() as connection:
            await connection.execute(text("SET LOCAL ROLE amesh_runtime"))
            values = list(
                await connection.scalars(
                    text("SELECT * FROM amesh_active_tenants_for_worker_group(:worker_group)"),
                    {"worker_group": worker_group},
                )
            )
        return [str(value) for value in values]

    async def consume_api_request(self, tenant_slug: str) -> int:
        async with tenant_admin_transaction(self._engine) as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT id, settings
                            FROM tenants
                            WHERE slug = :tenant_slug AND status = 'ACTIVE'
                              AND lifecycle = 'ACTIVE'
                            FOR UPDATE
                            """
                        ),
                        {"tenant_slug": tenant_slug},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise TenantUnavailableError("tenant unavailable")
            policy = TenantPolicy.model_validate(row["settings"])
            window_start = await connection.scalar(
                text("SELECT date_trunc('minute', clock_timestamp())")
            )
            if not isinstance(window_start, datetime):
                raise TypeError("PostgreSQL returned an invalid quota window")
            return await reserve_tenant_quota(
                connection,
                UUID(str(row["id"])),
                TenantQuotaType.API_REQUESTS,
                1,
                policy.max_api_requests_per_minute,
                window_start=window_start,
            )

    async def reserve_storage_bytes(self, tenant_slug: str, amount: int) -> int:
        async with tenant_admin_transaction(self._engine) as connection:
            row = await _lock_tenant_policy(connection, tenant_slug)
            policy = TenantPolicy.model_validate(row["settings"])
            return await reserve_tenant_quota(
                connection,
                UUID(str(row["id"])),
                TenantQuotaType.STORAGE_BYTES,
                amount,
                policy.max_storage_bytes,
            )

    async def release_storage_bytes(self, tenant_slug: str, amount: int) -> int:
        async with tenant_admin_transaction(self._engine) as connection:
            row = await _lock_tenant_policy(connection, tenant_slug)
            return await release_tenant_quota(
                connection,
                UUID(str(row["id"])),
                TenantQuotaType.STORAGE_BYTES,
                amount,
            )


def _to_tenant(row: RowMapping) -> TenantDefinition:
    return TenantDefinition(
        id=row["id"],
        slug=row["slug"],
        display_name=row["display_name"],
        status=row["status"],
        policy=TenantPolicy.model_validate(row["settings"]),
        storage_prefix=row["storage_prefix"],
        metadata=ResourceMetadata(
            labels=row["labels"],
            annotations=row["annotations"],
            created_by=row["created_by"],
            updated_by=row["updated_by"],
            resource_version=row["version"],
            lifecycle=row["lifecycle"],
            archived_at=row["archived_at"],
            deleted_at=row["deleted_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        ),
    )


async def _lock_tenant_policy(
    connection: AsyncConnection,
    tenant_slug: str,
) -> RowMapping:
    row = (
        (
            await connection.execute(
                text(
                    """
                    SELECT id, settings
                    FROM tenants
                    WHERE slug = :tenant_slug AND status = 'ACTIVE'
                      AND lifecycle = 'ACTIVE'
                    FOR UPDATE
                    """
                ),
                {"tenant_slug": tenant_slug},
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise TenantUnavailableError("tenant unavailable")
    return row


async def _write_tenant_audit(
    connection: AsyncConnection,
    *,
    tenant_id: UUID,
    actor_id: str,
    action: str,
    resource_id: str,
    evidence: dict[str, object] | None = None,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                tenant_id,
                event_id,
                actor_id,
                action,
                resource_type,
                resource_id,
                outcome,
                source,
                evidence,
                occurred_at
            ) VALUES (
                :tenant_id,
                :event_id,
                :actor_id,
                :action,
                'tenant',
                :resource_id,
                'SUCCESS',
                CAST(:source AS jsonb),
                CAST(:evidence AS jsonb),
                :occurred_at
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "source": json.dumps({"component": "tenant-repository"}),
            "evidence": json.dumps({"superAdmin": True, **(evidence or {})}),
            "occurred_at": datetime.now(UTC),
        },
    )
