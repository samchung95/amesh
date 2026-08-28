from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import (
    KeyValueChange,
    KeyValueEntry,
    KeyValueWrite,
    NamespaceFile,
    NamespaceFileVersion,
    ResourceVersionConflict,
    SecretBinding,
    SecretBindingWrite,
    new_runtime_id,
    normalize_resource_key,
    normalize_resource_path,
)

from .tenant_context import tenant_transaction


class PostgresSharedResourceRepository:
    """Tenant-fenced metadata authority for namespace files, key-values and secret bindings."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def put_file(
        self,
        namespace: str,
        path: str,
        *,
        object_uri: str,
        size_bytes: int,
        checksum_sha256: str,
        content_type: str | None,
        metadata: Mapping[str, Any],
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> NamespaceFile:
        path = normalize_resource_path(path)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            namespace_uuid = await _ensure_namespace(
                connection, tenant_uuid, namespace, actor_id=actor_id
            )
            existing = (
                await connection.execute(
                    text(
                        "SELECT * FROM namespace_files WHERE tenant_id = :tenant_id "
                        "AND namespace_id = :namespace_id AND path = :path FOR UPDATE"
                    ),
                    {"tenant_id": tenant_uuid, "namespace_id": namespace_uuid, "path": path},
                )
            ).mappings().one_or_none()
            current_resource_version = int(existing["resource_version"]) if existing else 0
            if expected_version is not None and expected_version != current_resource_version:
                raise ResourceVersionConflict(
                    f"namespace file expected version {expected_version}, "
                    f"found {current_resource_version}"
                )
            file_version = int(existing["current_version"]) + 1 if existing else 1
            resource_version = current_resource_version + 1
            row = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespace_files (
                            tenant_id, namespace_id, path, current_version, resource_version,
                            deleted, metadata, created_by, updated_by
                        ) VALUES (
                            :tenant_id, :namespace_id, :path, :file_version, :resource_version,
                            false, CAST(:metadata AS jsonb), :actor_id, :actor_id
                        )
                        ON CONFLICT (tenant_id, namespace_id, path) DO UPDATE SET
                            current_version = EXCLUDED.current_version,
                            resource_version = EXCLUDED.resource_version,
                            deleted = false,
                            metadata = EXCLUDED.metadata,
                            updated_by = EXCLUDED.updated_by,
                            updated_at = clock_timestamp()
                        RETURNING *
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace_id": namespace_uuid,
                        "path": path,
                        "file_version": file_version,
                        "resource_version": resource_version,
                        "metadata": json.dumps(dict(metadata), separators=(",", ":")),
                        "actor_id": actor_id,
                    },
                )
            ).mappings().one()
            version_row = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespace_file_versions (
                            tenant_id, namespace_id, path, version, object_uri, size_bytes,
                            checksum_sha256, content_type, created_by
                        ) VALUES (
                            :tenant_id, :namespace_id, :path, :version, :object_uri, :size_bytes,
                            :checksum_sha256, :content_type, :actor_id
                        ) RETURNING *
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace_id": namespace_uuid,
                        "path": path,
                        "version": file_version,
                        "object_uri": object_uri,
                        "size_bytes": size_bytes,
                        "checksum_sha256": checksum_sha256,
                        "content_type": content_type,
                        "actor_id": actor_id,
                    },
                )
            ).mappings().one()
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="namespace_file.write",
                resource_type="namespace_file",
                resource_id=f"{namespace}/{path}",
                evidence={
                    "namespace": namespace,
                    "path": path,
                    "fileVersion": file_version,
                    "resourceVersion": resource_version,
                    "sizeBytes": size_bytes,
                    "checksumSha256": checksum_sha256,
                },
            )
            return _file_record(row, version_row, namespace=namespace, origin=namespace)

    async def list_files(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        inherited: bool = True,
    ) -> list[NamespaceFile]:
        scopes = _namespace_lineage(namespace) if inherited else (namespace,)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = await _file_rows(connection, tenant_uuid, scopes)
            resolved: dict[str, RowMapping] = {}
            for row in rows:
                resolved[str(row["path"])] = row
            files = [
                _file_record(
                    row,
                    row,
                    namespace=namespace,
                    origin=str(row["namespace_name"]),
                )
                for row in resolved.values()
                if not bool(row["deleted"])
            ]
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="namespace_file.list",
                resource_type="namespace_file",
                resource_id=namespace,
                evidence={"namespace": namespace, "count": len(files), "inherited": inherited},
            )
            return sorted(files, key=lambda item: item.path)

    async def get_file_version(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> NamespaceFileVersion:
        path = normalize_resource_path(path)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            selected: RowMapping | None = None
            for scope in reversed(_namespace_lineage(namespace)):
                row = (
                    await connection.execute(
                        text(
                            """
                            SELECT files.*, namespaces.name AS namespace_name
                            FROM namespace_files AS files
                            JOIN namespaces ON namespaces.id = files.namespace_id
                            WHERE files.tenant_id = :tenant_id
                              AND namespaces.name = :namespace AND files.path = :path
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": scope, "path": path},
                    )
                ).mappings().one_or_none()
                if row is not None:
                    if bool(row["deleted"]):
                        break
                    selected = row
                    break
            if selected is None:
                raise LookupError(f"namespace file {path!r} does not exist")
            requested_version = version or int(selected["current_version"])
            version_row = (
                await connection.execute(
                    text(
                        """
                        SELECT versions.*, namespaces.name AS namespace_name
                        FROM namespace_file_versions AS versions
                        JOIN namespaces ON namespaces.id = versions.namespace_id
                        WHERE versions.tenant_id = :tenant_id
                          AND versions.namespace_id = :namespace_id
                          AND versions.path = :path AND versions.version = :version
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace_id": selected["namespace_id"],
                        "path": path,
                        "version": requested_version,
                    },
                )
            ).mappings().one_or_none()
            if version_row is None:
                raise LookupError(f"namespace file version {requested_version} does not exist")
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="namespace_file.read",
                resource_type="namespace_file",
                resource_id=f"{namespace}/{path}",
                evidence={
                    "namespace": namespace,
                    "path": path,
                    "originNamespace": selected["namespace_name"],
                    "version": requested_version,
                },
            )
            return _file_version(version_row)

    async def list_file_versions(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> list[NamespaceFileVersion]:
        path = normalize_resource_path(path)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    text(
                        """
                        SELECT versions.*, namespaces.name AS namespace_name
                        FROM namespace_file_versions AS versions
                        JOIN namespaces ON namespaces.id = versions.namespace_id
                        WHERE versions.tenant_id = :tenant_id
                          AND namespaces.name = :namespace AND versions.path = :path
                        ORDER BY versions.version DESC
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace, "path": path},
                )
            ).mappings().all()
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="namespace_file.list",
                resource_type="namespace_file",
                resource_id=f"{namespace}/{path}/versions",
                evidence={"namespace": namespace, "path": path, "count": len(rows)},
            )
            return [_file_version(row) for row in rows]

    async def move_file(
        self,
        namespace: str,
        source_path: str,
        destination_path: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> NamespaceFile:
        source_path = normalize_resource_path(source_path)
        destination_path = normalize_resource_path(destination_path)
        if source_path == destination_path:
            raise ValueError("source and destination paths must differ")
        source_version = await self.get_file_version(
            namespace, source_path, tenant_id=tenant_id, actor_id=actor_id
        )
        moved = await self.put_file(
            namespace,
            destination_path,
            object_uri=source_version.object_uri,
            size_bytes=source_version.size_bytes,
            checksum_sha256=source_version.checksum_sha256,
            content_type=source_version.content_type,
            metadata={"movedFrom": source_path},
            tenant_id=tenant_id,
            actor_id=actor_id,
            expected_version=0,
        )
        await self.delete_file(
            namespace,
            source_path,
            tenant_id=tenant_id,
            actor_id=actor_id,
            expected_version=expected_version,
        )
        return moved

    async def delete_file(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> int:
        path = normalize_resource_path(path)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            namespace_uuid = await _ensure_namespace(
                connection, tenant_uuid, namespace, actor_id=actor_id
            )
            existing = (
                await connection.execute(
                    text(
                        "SELECT * FROM namespace_files WHERE tenant_id = :tenant_id "
                        "AND namespace_id = :namespace_id AND path = :path FOR UPDATE"
                    ),
                    {"tenant_id": tenant_uuid, "namespace_id": namespace_uuid, "path": path},
                )
            ).mappings().one_or_none()
            current = int(existing["resource_version"]) if existing else 0
            if expected_version is not None and expected_version != current:
                raise ResourceVersionConflict(
                    f"namespace file expected version {expected_version}, found {current}"
                )
            resource_version = current + 1
            current_file_version = int(existing["current_version"]) if existing else 1
            await connection.execute(
                text(
                    """
                    INSERT INTO namespace_files (
                        tenant_id, namespace_id, path, current_version, resource_version,
                        deleted, created_by, updated_by
                    ) VALUES (
                        :tenant_id, :namespace_id, :path, :file_version, :resource_version,
                        true, :actor_id, :actor_id
                    )
                    ON CONFLICT (tenant_id, namespace_id, path) DO UPDATE SET
                        resource_version = EXCLUDED.resource_version,
                        deleted = true,
                        updated_by = EXCLUDED.updated_by,
                        updated_at = clock_timestamp()
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace_id": namespace_uuid,
                    "path": path,
                    "file_version": current_file_version,
                    "resource_version": resource_version,
                    "actor_id": actor_id,
                },
            )
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="namespace_file.delete",
                resource_type="namespace_file",
                resource_id=f"{namespace}/{path}",
                evidence={
                    "namespace": namespace,
                    "path": path,
                    "resourceVersion": resource_version,
                },
            )
            return resource_version

    async def put_key_value(
        self,
        namespace: str,
        key: str,
        write: KeyValueWrite,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> KeyValueEntry:
        key = normalize_resource_key(key)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            namespace_uuid = await _ensure_namespace(
                connection, tenant_uuid, namespace, actor_id=actor_id
            )
            existing = (
                await connection.execute(
                    text(
                        "SELECT resource_version FROM namespace_key_values "
                        "WHERE tenant_id = :tenant_id AND namespace_id = :namespace_id "
                        "AND key = :key FOR UPDATE"
                    ),
                    {"tenant_id": tenant_uuid, "namespace_id": namespace_uuid, "key": key},
                )
            ).scalar_one_or_none()
            current = int(existing) if existing is not None else 0
            if write.expected_version is not None and write.expected_version != current:
                raise ResourceVersionConflict(
                    f"key-value expected version {write.expected_version}, found {current}"
                )
            version = current + 1
            row = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespace_key_values (
                            tenant_id, namespace_id, key, value_type, value, metadata, expires_at,
                            resource_version, created_by, updated_by
                        ) VALUES (
                            :tenant_id, :namespace_id, :key, :value_type, CAST(:value AS jsonb),
                            CAST(:metadata AS jsonb), :expires_at, :version, :actor_id, :actor_id
                        )
                        ON CONFLICT (tenant_id, namespace_id, key) DO UPDATE SET
                            value_type = EXCLUDED.value_type,
                            value = EXCLUDED.value,
                            metadata = EXCLUDED.metadata,
                            expires_at = EXCLUDED.expires_at,
                            resource_version = EXCLUDED.resource_version,
                            updated_by = EXCLUDED.updated_by,
                            updated_at = clock_timestamp()
                        RETURNING *
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace_id": namespace_uuid,
                        "key": key,
                        "value_type": write.value_type.value,
                        "value": json.dumps(write.value, separators=(",", ":"), ensure_ascii=False),
                        "metadata": json.dumps(write.metadata, separators=(",", ":")),
                        "expires_at": write.expires_at,
                        "version": version,
                        "actor_id": actor_id,
                    },
                )
            ).mappings().one()
            await _key_value_change(
                connection,
                tenant_uuid,
                namespace_uuid,
                key=key,
                operation="UPSERT",
                resource_version=version,
                value_type=write.value_type.value,
                metadata=write.metadata,
            )
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="key_value.write",
                resource_type="key_value",
                resource_id=f"{namespace}/{key}",
                evidence={
                    "namespace": namespace,
                    "key": key,
                    "type": write.value_type.value,
                    "resourceVersion": version,
                    "expiresAt": write.expires_at.isoformat() if write.expires_at else None,
                },
            )
            return _key_value(row, namespace)

    async def list_key_values(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> list[KeyValueEntry]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    text(
                        """
                        SELECT key_values.* FROM namespace_key_values AS key_values
                        JOIN namespaces ON namespaces.id = key_values.namespace_id
                        WHERE key_values.tenant_id = :tenant_id AND namespaces.name = :namespace
                          AND (key_values.expires_at IS NULL OR key_values.expires_at > clock_timestamp())
                        ORDER BY key_values.key
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace},
                )
            ).mappings().all()
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="key_value.list",
                resource_type="key_value",
                resource_id=namespace,
                evidence={"namespace": namespace, "count": len(rows)},
            )
            return [_key_value(row, namespace) for row in rows]

    async def get_key_value(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        audit_action: str = "key_value.read",
    ) -> KeyValueEntry:
        key = normalize_resource_key(key)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                await connection.execute(
                    text(
                        """
                        SELECT key_values.* FROM namespace_key_values AS key_values
                        JOIN namespaces ON namespaces.id = key_values.namespace_id
                        WHERE key_values.tenant_id = :tenant_id AND namespaces.name = :namespace
                          AND key_values.key = :key
                          AND (key_values.expires_at IS NULL OR key_values.expires_at > clock_timestamp())
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace, "key": key},
                )
            ).mappings().one_or_none()
            if row is None:
                raise LookupError(f"key-value {key!r} does not exist")
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action=audit_action,
                resource_type="key_value",
                resource_id=f"{namespace}/{key}",
                evidence={
                    "namespace": namespace,
                    "key": key,
                    "type": row["value_type"],
                    "resourceVersion": row["resource_version"],
                },
            )
            return _key_value(row, namespace)

    async def delete_key_value(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> bool:
        key = normalize_resource_key(key)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                await connection.execute(
                    text(
                        """
                        SELECT key_values.*, namespaces.id AS namespace_id
                        FROM namespace_key_values AS key_values
                        JOIN namespaces ON namespaces.id = key_values.namespace_id
                        WHERE key_values.tenant_id = :tenant_id AND namespaces.name = :namespace
                          AND key_values.key = :key FOR UPDATE OF key_values
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace, "key": key},
                )
            ).mappings().one_or_none()
            if row is None:
                return False
            current = int(row["resource_version"])
            if expected_version is not None and expected_version != current:
                raise ResourceVersionConflict(
                    f"key-value expected version {expected_version}, found {current}"
                )
            await connection.execute(
                text(
                    "DELETE FROM namespace_key_values WHERE tenant_id = :tenant_id "
                    "AND namespace_id = :namespace_id AND key = :key"
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace_id": row["namespace_id"],
                    "key": key,
                },
            )
            await _key_value_change(
                connection,
                tenant_uuid,
                UUID(str(row["namespace_id"])),
                key=key,
                operation="DELETE",
                resource_version=current + 1,
                value_type=None,
                metadata={},
            )
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="key_value.delete",
                resource_type="key_value",
                resource_id=f"{namespace}/{key}",
                evidence={"namespace": namespace, "key": key, "resourceVersion": current + 1},
            )
            return True

    async def list_key_value_changes(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        after: int = 0,
        limit: int = 100,
    ) -> list[KeyValueChange]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                await connection.execute(
                    text(
                        """
                        SELECT changes.*, namespaces.name AS namespace_name
                        FROM namespace_key_value_changes AS changes
                        JOIN namespaces ON namespaces.id = changes.namespace_id
                        WHERE changes.tenant_id = :tenant_id AND namespaces.name = :namespace
                          AND changes.cursor > :after
                        ORDER BY changes.cursor LIMIT :limit
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": namespace,
                        "after": after,
                        "limit": limit,
                    },
                )
            ).mappings().all()
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="key_value.list",
                resource_type="key_value",
                resource_id=f"{namespace}/changes",
                evidence={"namespace": namespace, "after": after, "count": len(rows)},
            )
            return [
                KeyValueChange(
                    cursor=row["cursor"],
                    namespace=row["namespace_name"],
                    key=row["key"],
                    operation=row["operation"],
                    resourceVersion=row["resource_version"],
                    type=row["value_type"],
                    metadata=dict(row["metadata"]),
                    occurredAt=row["occurred_at"],
                )
                for row in rows
            ]

    async def put_secret_binding(
        self,
        namespace: str,
        key: str,
        write: SecretBindingWrite,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> SecretBinding:
        key = normalize_resource_key(key)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            namespace_uuid = await _ensure_namespace(
                connection, tenant_uuid, namespace, actor_id=actor_id
            )
            existing = (
                await connection.execute(
                    text(
                        "SELECT resource_version FROM namespace_secret_bindings "
                        "WHERE tenant_id = :tenant_id AND namespace_id = :namespace_id "
                        "AND key = :key FOR UPDATE"
                    ),
                    {"tenant_id": tenant_uuid, "namespace_id": namespace_uuid, "key": key},
                )
            ).scalar_one_or_none()
            current = int(existing) if existing is not None else 0
            if write.expected_version is not None and write.expected_version != current:
                raise ResourceVersionConflict(
                    f"secret binding expected version {write.expected_version}, found {current}"
                )
            version = current + 1
            row = (
                await connection.execute(
                    text(
                        """
                        INSERT INTO namespace_secret_bindings (
                            tenant_id, namespace_id, key, provider, provider_reference, metadata,
                            resource_version, created_by, updated_by
                        ) VALUES (
                            :tenant_id, :namespace_id, :key, :provider, :reference,
                            CAST(:metadata AS jsonb), :version, :actor_id, :actor_id
                        )
                        ON CONFLICT (tenant_id, namespace_id, key) DO UPDATE SET
                            provider = EXCLUDED.provider,
                            provider_reference = EXCLUDED.provider_reference,
                            metadata = EXCLUDED.metadata,
                            resource_version = EXCLUDED.resource_version,
                            updated_by = EXCLUDED.updated_by,
                            updated_at = clock_timestamp()
                        RETURNING *
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace_id": namespace_uuid,
                        "key": key,
                        "provider": write.provider,
                        "reference": write.provider_reference,
                        "metadata": json.dumps(write.metadata, separators=(",", ":")),
                        "version": version,
                        "actor_id": actor_id,
                    },
                )
            ).mappings().one()
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="secret.write",
                resource_type="secret",
                resource_id=f"{namespace}/{key}",
                evidence={
                    "namespace": namespace,
                    "key": key,
                    "provider": write.provider,
                    "resourceVersion": version,
                },
            )
            return _secret_binding(row, namespace=namespace, origin=namespace)

    async def list_secret_bindings(
        self,
        namespace: str,
        *,
        tenant_id: str,
        actor_id: str,
        inherited: bool = True,
    ) -> list[SecretBinding]:
        scopes = _namespace_lineage(namespace) if inherited else (namespace,)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            resolved: dict[str, RowMapping] = {}
            for scope in scopes:
                rows = (
                    await connection.execute(
                        text(
                            """
                            SELECT bindings.*, namespaces.name AS namespace_name
                            FROM namespace_secret_bindings AS bindings
                            JOIN namespaces ON namespaces.id = bindings.namespace_id
                            WHERE bindings.tenant_id = :tenant_id AND namespaces.name = :namespace
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": scope},
                    )
                ).mappings().all()
                for row in rows:
                    resolved[str(row["key"])] = row
            bindings = [
                _secret_binding(row, namespace=namespace, origin=str(row["namespace_name"]))
                for row in resolved.values()
            ]
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="secret.list",
                resource_type="secret",
                resource_id=namespace,
                evidence={"namespace": namespace, "count": len(bindings), "inherited": inherited},
            )
            return sorted(bindings, key=lambda item: item.key)

    async def get_secret_binding(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> SecretBinding:
        key = normalize_resource_key(key)
        bindings = await self.list_secret_bindings(
            namespace, tenant_id=tenant_id, actor_id=actor_id, inherited=True
        )
        binding = next((item for item in bindings if item.key == key), None)
        if binding is None:
            raise LookupError(f"secret binding {key!r} does not exist")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="secret.use",
                resource_type="secret",
                resource_id=f"{namespace}/{key}",
                evidence={
                    "namespace": namespace,
                    "key": key,
                    "originNamespace": binding.origin_namespace,
                    "provider": binding.provider,
                },
            )
        return binding

    async def delete_secret_binding(
        self,
        namespace: str,
        key: str,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> bool:
        key = normalize_resource_key(key)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                await connection.execute(
                    text(
                        """
                        SELECT bindings.* FROM namespace_secret_bindings AS bindings
                        JOIN namespaces ON namespaces.id = bindings.namespace_id
                        WHERE bindings.tenant_id = :tenant_id AND namespaces.name = :namespace
                          AND bindings.key = :key FOR UPDATE OF bindings
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace, "key": key},
                )
            ).mappings().one_or_none()
            if row is None:
                return False
            current = int(row["resource_version"])
            if expected_version is not None and expected_version != current:
                raise ResourceVersionConflict(
                    f"secret binding expected version {expected_version}, found {current}"
                )
            await connection.execute(
                text(
                    "DELETE FROM namespace_secret_bindings WHERE tenant_id = :tenant_id "
                    "AND namespace_id = :namespace_id AND key = :key"
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace_id": row["namespace_id"],
                    "key": key,
                },
            )
            await _audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="secret.delete",
                resource_type="secret",
                resource_id=f"{namespace}/{key}",
                evidence={"namespace": namespace, "key": key, "resourceVersion": current},
            )
            return True


async def _ensure_namespace(
    connection: AsyncConnection,
    tenant_id: UUID,
    namespace: str,
    *,
    actor_id: str,
) -> UUID:
    row = (
        await connection.execute(
            text(
                """
                INSERT INTO namespaces (id, tenant_id, name, created_by, updated_by)
                VALUES (:id, :tenant_id, :namespace, :actor_id, :actor_id)
                ON CONFLICT (tenant_id, name) DO UPDATE SET
                    updated_by = namespaces.updated_by
                RETURNING id
                """
            ),
            {
                "id": new_runtime_id(),
                "tenant_id": tenant_id,
                "namespace": namespace,
                "actor_id": actor_id,
            },
        )
    ).scalar_one()
    return UUID(str(row))


def _namespace_lineage(namespace: str) -> tuple[str, ...]:
    parts = namespace.split(".")
    return tuple(".".join(parts[: index + 1]) for index in range(len(parts)))


async def _file_rows(
    connection: AsyncConnection,
    tenant_id: UUID,
    scopes: tuple[str, ...],
) -> list[RowMapping]:
    rows: list[RowMapping] = []
    for scope in scopes:
        result = await connection.execute(
            text(
                """
                SELECT files.*, versions.object_uri, versions.size_bytes,
                       versions.checksum_sha256, versions.content_type,
                       versions.created_by AS version_created_by,
                       versions.created_at AS version_created_at,
                       namespaces.name AS namespace_name
                FROM namespace_files AS files
                JOIN namespaces ON namespaces.id = files.namespace_id
                LEFT JOIN namespace_file_versions AS versions
                  ON versions.tenant_id = files.tenant_id
                 AND versions.namespace_id = files.namespace_id
                 AND versions.path = files.path
                 AND versions.version = files.current_version
                WHERE files.tenant_id = :tenant_id AND namespaces.name = :namespace
                ORDER BY files.path
                """
            ),
            {"tenant_id": tenant_id, "namespace": scope},
        )
        rows.extend(result.mappings().all())
    return rows


def _file_record(
    current: RowMapping,
    version: RowMapping,
    *,
    namespace: str,
    origin: str,
) -> NamespaceFile:
    return NamespaceFile(
        namespace=namespace,
        path=current["path"],
        version=current["current_version"],
        resourceVersion=current["resource_version"],
        sizeBytes=version["size_bytes"],
        checksumSha256=version["checksum_sha256"],
        contentType=version["content_type"],
        metadata=dict(current["metadata"]),
        originNamespace=origin,
        inherited=origin != namespace,
        createdAt=current["created_at"],
        updatedAt=current["updated_at"],
    )


def _file_version(row: RowMapping) -> NamespaceFileVersion:
    return NamespaceFileVersion(
        namespace=row["namespace_name"],
        path=row["path"],
        version=row["version"],
        sizeBytes=row["size_bytes"],
        checksumSha256=row["checksum_sha256"],
        contentType=row["content_type"],
        objectUri=row["object_uri"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )


def _key_value(row: RowMapping, namespace: str) -> KeyValueEntry:
    return KeyValueEntry(
        namespace=namespace,
        key=row["key"],
        type=row["value_type"],
        value=row["value"],
        expiresAt=row["expires_at"],
        metadata=dict(row["metadata"]),
        resourceVersion=row["resource_version"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


def _secret_binding(row: RowMapping, *, namespace: str, origin: str) -> SecretBinding:
    return SecretBinding(
        namespace=namespace,
        key=row["key"],
        provider=row["provider"],
        providerReference=row["provider_reference"],
        metadata=dict(row["metadata"]),
        resourceVersion=row["resource_version"],
        inherited=origin != namespace,
        originNamespace=origin,
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


async def _key_value_change(
    connection: AsyncConnection,
    tenant_id: UUID,
    namespace_id: UUID,
    *,
    key: str,
    operation: str,
    resource_version: int,
    value_type: str | None,
    metadata: Mapping[str, Any],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO namespace_key_value_changes (
                tenant_id, namespace_id, key, operation, resource_version, value_type, metadata
            ) VALUES (
                :tenant_id, :namespace_id, :key, :operation, :resource_version, :value_type,
                CAST(:metadata AS jsonb)
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "namespace_id": namespace_id,
            "key": key,
            "operation": operation,
            "resource_version": resource_version,
            "value_type": value_type,
            "metadata": json.dumps(dict(metadata), separators=(",", ":")),
        },
    )


async def _audit(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    evidence: Mapping[str, Any],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                tenant_id, event_id, actor_id, action, resource_type, resource_id,
                outcome, source, evidence, occurred_at
            ) VALUES (
                :tenant_id, :event_id, :actor_id, :action, :resource_type, :resource_id,
                'SUCCESS', '{"component":"namespace-resources"}'::jsonb,
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "evidence": json.dumps(dict(evidence), separators=(",", ":"), default=str),
            "occurred_at": datetime.now(UTC),
        },
    )
