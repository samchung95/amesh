"""SQL authority for the flow_registry_repository execution port."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.domain import (
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    PluginPolicyStage,
    PolicyStage,
    compare_flow_revisions,
    new_runtime_id,
)
from amesh.dsl import FlowDefinition, compile_execution_tasks
from amesh.dsl.registry import RESOURCE_CATALOG_VERSION
from amesh.ports.errors import NotFoundError, RepositoryVersionConflict
from amesh.ports.execution_repository import (
    FlowRegistryRepository,
    PersistedFlow,
    PersistedFlowRevision,
)
from amesh.ports.repository_support import AuditWrite
from amesh.ports.tenant_repository import TenantUnavailableError
from amesh.workflow.data_contracts import (
    validate_flow_data_contract,
)
from amesh.workflow.metadata import (
    NamespaceWorkflowMetadata,
    NamespaceWorkflowMetadataUpdate,
    NamespaceWorkflowMetadataView,
    flow_system_labels,
    namespace_lineage,
    resolve_flow_metadata,
)

from .check_repository import (
    store_flow_check_definitions,
    synchronize_active_flow_checks,
)
from .execution_port_base import PostgresExecutionPort
from .execution_rows import (
    flow_from_row as _to_flow,
)
from .execution_rows import (
    flow_revision_from_row as _to_flow_revision,
)
from .execution_rows import (
    persisted_flow_revision_from_row as _to_persisted_flow_revision,
)
from .execution_shared import (
    _ACTIVATE_FLOW_REVISION,
    _SELECT_FLOW_REVISION,
    _load_tenant_policy,
    _require_allowed_plugins,
)
from .metadata_repository import store_flow_triggers
from .trigger_runtime_repository import (
    synchronize_flow_trigger_runtime,
)

_UPSERT_NAMESPACE = text(
    """
    INSERT INTO namespaces (id, tenant_id, name, created_by, updated_by)
    SELECT :namespace_id, tenants.id, :namespace, :actor_id, :actor_id
    FROM tenants
    WHERE tenants.slug = :tenant_slug
    ON CONFLICT (tenant_id, name) DO UPDATE
    SET name = EXCLUDED.name,
        updated_by = EXCLUDED.updated_by,
        updated_at = now()
    RETURNING id, tenant_id
    """
)

_UPSERT_FLOW = text(
    """
    INSERT INTO flows (
        id, tenant_id, namespace_id, flow_key, created_by, updated_by
    )
    VALUES (
        :resource_id, :tenant_id, :namespace_id, :flow_key, :actor_id, :actor_id
    )
    ON CONFLICT (tenant_id, namespace_id, flow_key)
    DO UPDATE SET flow_key = EXCLUDED.flow_key
    RETURNING id
    """
)

_INSERT_FLOW_REVISION = text(
    """
    INSERT INTO flow_revisions (
        id,
        tenant_id,
        flow_id,
        revision,
        semantic_hash,
        canonical_definition,
        plugin_resolution,
        source,
        source_commit,
        environment,
        deployment_metadata,
        created_by
    )
    VALUES (
        :revision_id,
        :tenant_id,
        :flow_id,
        :revision,
        :semantic_hash,
        CAST(:canonical_definition AS jsonb),
        CAST(:plugin_resolution AS jsonb),
        :source,
        :source_commit,
        :environment,
        CAST(:deployment_metadata AS jsonb),
        :actor_id
    )
    ON CONFLICT DO NOTHING
    RETURNING id
    """
)

_NEXT_FLOW_REVISION = text(
    """
    SELECT COALESCE(MAX(revision), 0) + 1
    FROM flow_revisions
    WHERE tenant_id = :tenant_id AND flow_id = :flow_id
    """
)

_SELECT_FLOW_RESOURCE = text(
    """
    SELECT flows.id, flows.active_revision, flows.status
    FROM flows
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE flows.tenant_id = :tenant_id
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
    """
)

_LIST_FLOW_REVISIONS = text(
    """
    SELECT
        revisions.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        revisions.revision,
        revisions.semantic_hash,
        revisions.plugin_resolution,
        revisions.source,
        revisions.source_commit,
        revisions.environment,
        revisions.deployment_metadata,
        revisions.created_by,
        revisions.created_at
    FROM flow_revisions AS revisions
    JOIN flows ON flows.id = revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN tenants ON tenants.id = revisions.tenant_id
    WHERE revisions.tenant_id = :tenant_id
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
    ORDER BY revisions.revision
    """
)

_GET_FLOW_REVISION_DOCUMENT = text(
    """
    SELECT revisions.canonical_definition
    FROM flow_revisions AS revisions
    JOIN flows ON flows.id = revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE revisions.tenant_id = :tenant_id
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
      AND revisions.revision = :revision
    """
)

_INSERT_FLOW_REVISION_EVENT = text(
    """
    INSERT INTO flow_revision_events (
        event_id, tenant_id, flow_id, revision, event_type, actor_id, reason, payload
    ) VALUES (
        :event_id, :tenant_id, :flow_id, :revision, :event_type, :actor_id, :reason,
        CAST(:payload AS jsonb)
    )
    """
)

_FLOW_REVISION_REFERENCES = text(
    """
    SELECT
        revisions.id,
        EXISTS (
            SELECT 1 FROM executions
            WHERE executions.tenant_id = revisions.tenant_id
              AND executions.flow_revision_id = revisions.id
        ) AS execution_reference,
        EXISTS (
            SELECT 1 FROM audit_events
            WHERE audit_events.tenant_id = revisions.tenant_id
              AND audit_events.resource_type = 'flow_revision'
              AND audit_events.resource_id = revisions.id::text
        ) AS audit_reference
    FROM flow_revisions AS revisions
    WHERE revisions.tenant_id = :tenant_id
      AND revisions.flow_id = :flow_id
      AND revisions.revision = :revision
    """
)

_DELETE_FLOW_REVISION = text(
    """
    DELETE FROM flow_revisions
    WHERE tenant_id = :tenant_id AND flow_id = :flow_id AND revision = :revision
    """
)

_GET_FLOW_DEFINITION = text(
    """
    SELECT
        flow_revisions.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.canonical_definition,
        flow_revisions.semantic_hash,
        flow_revisions.plugin_resolution
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = COALESCE(:revision, flows.active_revision)
    WHERE tenants.slug = :tenant_slug
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
    """
)

_LIST_FLOWS = text(
    """
    SELECT
        flows.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.semantic_hash,
        flows.labels,
        flows.annotations,
        flows.created_by,
        flows.updated_by,
        flows.version,
        flows.status,
        flows.lifecycle,
        flows.archived_at,
        flows.deleted_at,
        flows.created_at,
        flows.updated_at
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = flows.active_revision
    WHERE tenants.slug = :tenant_slug
    ORDER BY namespaces.name, flows.flow_key
    """
)

_UPSERT_NAMESPACE_WORKFLOW_METADATA = text(
    """
    INSERT INTO namespace_workflow_metadata (
        tenant_id, namespace_id, plugin_defaults, policy,
        resource_version, created_by, updated_by
    ) VALUES (
        :tenant_id, :namespace_id, CAST(:plugin_defaults AS jsonb), CAST(:policy AS jsonb),
        1, :actor_id, :actor_id
    )
    ON CONFLICT (tenant_id, namespace_id) DO UPDATE SET
        plugin_defaults = EXCLUDED.plugin_defaults,
        policy = EXCLUDED.policy,
        resource_version = namespace_workflow_metadata.resource_version + 1,
        updated_by = EXCLUDED.updated_by,
        updated_at = clock_timestamp()
    WHERE CAST(:expected_version AS bigint) IS NULL
       OR namespace_workflow_metadata.resource_version = CAST(:expected_version AS bigint)
    RETURNING *
    """
)

_LIST_NAMESPACE_WORKFLOW_METADATA = text(
    """
    SELECT metadata.*, namespaces.name AS namespace_name, tenants.slug AS tenant_slug
    FROM namespace_workflow_metadata AS metadata
    JOIN namespaces ON namespaces.id = metadata.namespace_id
    JOIN tenants ON tenants.id = metadata.tenant_id
    WHERE metadata.tenant_id = :tenant_id
      AND namespaces.name = ANY(CAST(:namespaces AS text[]))
    ORDER BY array_position(CAST(:namespaces AS text[]), namespaces.name)
    """
)

_GET_PERSISTED_FLOW = text(
    """
    SELECT
        flows.id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        flow_revisions.revision,
        flow_revisions.semantic_hash,
        flows.labels,
        flows.annotations,
        flows.created_by,
        flows.updated_by,
        flows.version,
        flows.status,
        flows.lifecycle,
        flows.archived_at,
        flows.deleted_at,
        flows.created_at,
        flows.updated_at
    FROM flows
    JOIN tenants ON tenants.id = flows.tenant_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    JOIN flow_revisions
      ON flow_revisions.flow_id = flows.id
     AND flow_revisions.revision = flows.active_revision
    WHERE flows.tenant_id = :tenant_id
      AND flows.id = :flow_id
    """
)


def _canonical_flow(flow: FlowDefinition) -> tuple[str, str]:
    canonical = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    semantic = dict(canonical)
    semantic.pop("revision", None)
    semantic_encoded = json.dumps(
        semantic,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return encoded, hashlib.sha256(semantic_encoded.encode("utf-8")).hexdigest()


def _flow_with_revision(flow: FlowDefinition, revision: int) -> FlowDefinition:
    definition = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    definition["revision"] = revision
    return FlowDefinition.model_validate(definition)


def _same_flow_semantics(definition: object, flow: FlowDefinition) -> bool:
    if not isinstance(definition, dict):
        return False
    try:
        stored = FlowDefinition.model_validate(definition).model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )
    except ValidationError:
        return False
    candidate = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    stored.pop("revision", None)
    candidate.pop("revision", None)
    return stored == candidate


def _plugin_resolution(
    flow: FlowDefinition,
    metadata_resolution: dict[str, object] | None = None,
) -> dict[str, object]:
    resources = {("task", node.task.type) for node in compile_execution_tasks(flow)} | {
        ("trigger", trigger.type) for trigger in flow.triggers
    }
    resolution: dict[str, object] = {
        "catalogVersion": RESOURCE_CATALOG_VERSION,
        "resources": [
            {"kind": kind, "type": resource_type} for kind, resource_type in sorted(resources)
        ],
    }
    if metadata_resolution:
        resolution["defaults"] = metadata_resolution
    return resolution


async def _load_namespace_workflow_metadata(
    connection: AsyncConnection,
    tenant_id: UUID,
    namespace: str,
) -> tuple[NamespaceWorkflowMetadata, ...]:
    rows = (
        (
            await connection.execute(
                _LIST_NAMESPACE_WORKFLOW_METADATA,
                {
                    "tenant_id": tenant_id,
                    "namespaces": list(namespace_lineage(namespace)),
                },
            )
        )
        .mappings()
        .all()
    )
    return tuple(
        _to_namespace_workflow_metadata(row, str(row["tenant_slug"]), str(row["namespace_name"]))
        for row in rows
    )


def _to_namespace_workflow_metadata(
    row: RowMapping,
    tenant_id: str,
    namespace: str,
) -> NamespaceWorkflowMetadata:
    return NamespaceWorkflowMetadata(
        tenantId=tenant_id,
        namespace=namespace,
        pluginDefaults=row["plugin_defaults"],
        policy=row["policy"],
        resourceVersion=row["resource_version"],
        createdBy=row["created_by"],
        updatedBy=row["updated_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


class PostgresFlowRegistryRepository(PostgresExecutionPort, FlowRegistryRepository):
    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
        revision_source: FlowRevisionSource | None = None,
    ) -> PersistedFlow:
        flow = await self._validate_flow_apply(flow, tenant_id, actor_id)
        async with self._services.transactions.tenant(tenant_id) as (connection, scoped_tenant_id):
            policy = await _load_tenant_policy(connection)
            _require_allowed_plugins(policy, flow)
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
                actor_id,
            )
            if tenant_uuid != scoped_tenant_id:
                raise TenantUnavailableError("tenant context changed during flow application")
            flow_uuid = await self._ensure_flow(
                connection,
                tenant_uuid,
                namespace_id,
                flow.id,
                actor_id,
            )
            _revision_id, stored_flow, created = await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_uuid,
                flow,
                actor_id,
                revision_source=revision_source,
                resolve_namespace_metadata=True,
            )
            expected_version: int | None = None
            if expected_etag is not None:
                current_result = await connection.execute(
                    _GET_PERSISTED_FLOW,
                    {"tenant_id": tenant_uuid, "flow_id": flow_uuid},
                )
                current_row = current_result.mappings().one_or_none()
                if current_row is None or _to_flow(current_row).etag != expected_etag:
                    raise RepositoryVersionConflict(
                        f"flow {flow.namespace}.{flow.id} does not match If-Match"
                    )
                expected_version = int(current_row["version"])
            activation = await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_uuid,
                    "revision": stored_flow.revision,
                    "status": (
                        FlowLifecycle.DISABLED.value
                        if stored_flow.disabled
                        else FlowLifecycle.ACTIVE.value
                    ),
                    "labels": self._services.codec.dumps(
                        {**stored_flow.labels, **flow_system_labels(stored_flow)}
                    ),
                    "annotations": self._services.codec.dumps(stored_flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": expected_version,
                },
            )
            if activation.scalar_one_or_none() is None:
                raise RepositoryVersionConflict(
                    f"flow {flow.namespace}.{flow.id} changed during conditional update"
                )
            await synchronize_flow_trigger_runtime(
                connection,
                tenant_uuid,
                flow_uuid,
                active_revision=stored_flow.revision,
                flow_disabled=stored_flow.disabled,
            )
            await synchronize_active_flow_checks(
                connection,
                tenant_uuid,
                flow_uuid,
                active_revision=stored_flow.revision,
                flow_disabled=stored_flow.disabled,
            )
            await self._record_flow_revision_event(
                connection,
                tenant_uuid,
                flow_uuid,
                stored_flow.revision,
                event_type="FLOW_REVISION_CREATED" if created else "FLOW_REVISION_SELECTED",
                actor_id=actor_id,
                source=revision_source,
            )
            result = await connection.execute(
                _GET_PERSISTED_FLOW,
                {"tenant_id": tenant_uuid, "flow_id": flow_uuid},
            )
            row = result.mappings().one()
        return _to_flow(row)

    async def _validate_flow_apply(
        self,
        flow: FlowDefinition,
        tenant_id: str,
        actor_id: str,
    ) -> FlowDefinition:
        if self._admission_policy_enforcer is not None:
            decision = await self._admission_policy_enforcer(
                flow,
                tenant_id,
                PolicyStage.SAVE,
                actor_id,
                None,
                None,
                None,
                None,
            )
            if decision.mutated_input is None:
                raise RuntimeError("save policy decision omitted its mutated input")
            flow = FlowDefinition.model_validate(decision.mutated_input.flow.definition)
        validate_flow_data_contract(flow)
        if self._plugin_policy_enforcer is not None:
            await self._plugin_policy_enforcer(
                flow,
                tenant_id,
                PluginPolicyStage.AUTHORING,
                actor_id,
            )
        return flow

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition:
        return (
            await self.get_flow_revision(
                namespace,
                flow_id,
                tenant_id=tenant_id,
                revision=revision,
            )
        ).flow

    async def get_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> PersistedFlowRevision:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _GET_FLOW_DEFINITION,
                {
                    "tenant_slug": tenant_id,
                    "namespace": namespace,
                    "flow_key": flow_id,
                    "revision": revision,
                },
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise NotFoundError(
                "flow",
                f"{namespace}.{flow_id}",
                message=f"flow {namespace}.{flow_id} does not exist",
            )
        return _to_persisted_flow_revision(row, self._services.codec)

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_FLOWS,
                {"tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [_to_flow(row) for row in rows]

    async def upsert_namespace_workflow_metadata(
        self,
        namespace: str,
        update: NamespaceWorkflowMetadataUpdate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> NamespaceWorkflowMetadata:
        async with self._services.transactions.tenant(tenant_id) as (connection, scoped_tenant_id):
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                namespace,
                actor_id,
            )
            if tenant_uuid != scoped_tenant_id:
                raise TenantUnavailableError("tenant context changed during metadata update")
            result = await connection.execute(
                _UPSERT_NAMESPACE_WORKFLOW_METADATA,
                {
                    "tenant_id": tenant_uuid,
                    "namespace_id": namespace_id,
                    "plugin_defaults": self._services.codec.dumps(
                        [
                            item.model_dump(mode="json", by_alias=True)
                            for item in update.plugin_defaults
                        ]
                    ),
                    "policy": update.policy.model_dump_json(by_alias=True),
                    "actor_id": actor_id,
                    "expected_version": update.expected_version,
                },
            )
            row = result.mappings().one_or_none()
            if row is None:
                raise RepositoryVersionConflict(
                    f"namespace {namespace!r} workflow metadata version is stale"
                )
            return _to_namespace_workflow_metadata(row, tenant_id, namespace)

    async def get_namespace_workflow_metadata(
        self,
        namespace: str,
        *,
        tenant_id: str,
    ) -> NamespaceWorkflowMetadataView:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            records = await _load_namespace_workflow_metadata(
                connection,
                tenant_uuid,
                namespace,
            )
        return NamespaceWorkflowMetadataView(namespace=namespace, lineage=records)

    async def list_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[FlowRevisionRecord]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _LIST_FLOW_REVISIONS,
                {"tenant_id": tenant_uuid, "namespace": namespace, "flow_key": flow_id},
            )
            rows = result.mappings().all()
        return [_to_flow_revision(row) for row in rows]

    async def diff_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        from_revision: int,
        to_revision: int,
        *,
        tenant_id: str,
    ) -> FlowRevisionDiff:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            documents: list[dict[str, object]] = []
            for revision in (from_revision, to_revision):
                document = await connection.scalar(
                    _GET_FLOW_REVISION_DOCUMENT,
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": namespace,
                        "flow_key": flow_id,
                        "revision": revision,
                    },
                )
                if not isinstance(document, dict):
                    raise NotFoundError(
                        "flow revision",
                        f"{namespace}.{flow_id}:{revision}",
                        message=f"flow {namespace}.{flow_id} revision {revision} does not exist",
                    )
                documents.append(document)
        return compare_flow_revisions(
            documents[0],
            documents[1],
            from_revision=from_revision,
            to_revision=to_revision,
        )

    async def promote_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        lifecycle: FlowLifecycle,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow:
        if self._admission_policy_enforcer is not None:
            flow = await self.get_flow(
                namespace,
                flow_id,
                tenant_id=tenant_id,
                revision=revision,
            )
            await self._admission_policy_enforcer(
                flow,
                tenant_id,
                PolicyStage.PROMOTE,
                actor_id,
                None,
                None,
                None,
                None,
            )
        return await self._select_flow_revision(
            namespace,
            flow_id,
            revision,
            lifecycle,
            tenant_id=tenant_id,
            actor_id=actor_id,
            reason=reason,
            event_type="FLOW_REVISION_PROMOTED",
        )

    async def restore_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
        reason: str | None = None,
    ) -> PersistedFlow:
        if self._admission_policy_enforcer is not None:
            flow = await self.get_flow(
                namespace,
                flow_id,
                tenant_id=tenant_id,
                revision=revision,
            )
            await self._admission_policy_enforcer(
                flow,
                tenant_id,
                PolicyStage.PROMOTE,
                actor_id,
                None,
                None,
                None,
                None,
            )
        return await self._select_flow_revision(
            namespace,
            flow_id,
            revision,
            FlowLifecycle.ACTIVE,
            tenant_id=tenant_id,
            actor_id=actor_id,
            reason=reason,
            event_type="FLOW_REVISION_RESTORED",
        )

    async def delete_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
        actor_id: str = "system:flow-manager",
    ) -> None:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            flow_row = await self._flow_resource_row(
                connection,
                tenant_uuid,
                namespace,
                flow_id,
            )
            if int(flow_row["active_revision"]) == revision:
                raise ValueError("the selected flow revision cannot be deleted")
            reference_result = await connection.execute(
                _FLOW_REVISION_REFERENCES,
                {"tenant_id": tenant_uuid, "flow_id": flow_row["id"], "revision": revision},
            )
            references = reference_result.mappings().one_or_none()
            if references is None:
                raise NotFoundError(
                    "flow revision",
                    f"{namespace}.{flow_id}:{revision}",
                    message=f"flow {namespace}.{flow_id} revision {revision} does not exist",
                )
            if references["execution_reference"]:
                raise ValueError("flow revision is referenced by an execution")
            if references["audit_reference"]:
                raise ValueError("flow revision is referenced by audit evidence")
            await connection.execute(
                _DELETE_FLOW_REVISION,
                {"tenant_id": tenant_uuid, "flow_id": flow_row["id"], "revision": revision},
            )
            await self._record_flow_revision_event(
                connection,
                tenant_uuid,
                UUID(str(flow_row["id"])),
                revision,
                event_type="FLOW_REVISION_DELETED",
                actor_id=actor_id,
            )

    async def _ensure_namespace(
        self,
        connection: AsyncConnection,
        tenant_slug: str,
        namespace: str,
        actor_id: str,
    ) -> tuple[UUID, UUID]:
        result = await connection.execute(
            _UPSERT_NAMESPACE,
            {
                "namespace_id": new_runtime_id(),
                "tenant_slug": tenant_slug,
                "namespace": namespace,
                "actor_id": actor_id,
            },
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise NotFoundError(
                "tenant",
                tenant_slug,
                message=f"tenant {tenant_slug!r} does not exist",
            )
        return UUID(str(row["tenant_id"])), UUID(str(row["id"]))

    async def _ensure_flow(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        namespace_id: UUID,
        flow_key: str,
        actor_id: str,
    ) -> UUID:
        result = await connection.execute(
            _UPSERT_FLOW,
            {
                "resource_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "namespace_id": namespace_id,
                "flow_key": flow_key,
                "actor_id": actor_id,
            },
        )
        return UUID(str(result.scalar_one()))

    async def _ensure_flow_revision(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        flow_id: UUID,
        flow: FlowDefinition,
        actor_id: str,
        *,
        revision_source: FlowRevisionSource | None = None,
        resolve_namespace_metadata: bool = False,
    ) -> tuple[UUID, FlowDefinition, bool]:
        scopes = (
            await _load_namespace_workflow_metadata(connection, tenant_id, flow.namespace)
            if resolve_namespace_metadata
            else ()
        )
        flow, metadata_resolution = resolve_flow_metadata(flow, scopes)
        validate_flow_data_contract(flow)
        requested_result = await connection.execute(
            _SELECT_FLOW_REVISION,
            {"tenant_id": tenant_id, "flow_id": flow_id, "revision": flow.revision},
        )
        requested = requested_result.mappings().one_or_none()
        if requested is not None and _same_flow_semantics(requested["canonical_definition"], flow):
            stored_flow = _flow_with_revision(flow, flow.revision)
            return UUID(str(requested["id"])), stored_flow, False

        next_revision = int(
            await connection.scalar(
                _NEXT_FLOW_REVISION,
                {"tenant_id": tenant_id, "flow_id": flow_id},
            )
            or 1
        )
        revision = max(flow.revision, next_revision)
        stored_flow = _flow_with_revision(flow, revision)
        canonical_definition, semantic_hash = _canonical_flow(stored_flow)
        source = revision_source or FlowRevisionSource()
        plugin_resolution = (
            self._plugin_resolution_provider(stored_flow)
            if self._plugin_resolution_provider is not None
            else _plugin_resolution(stored_flow)
        )
        if metadata_resolution:
            plugin_resolution = {**plugin_resolution, "defaults": metadata_resolution}
        inserted_revision_id = await connection.scalar(
            _INSERT_FLOW_REVISION,
            {
                "revision_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "flow_id": flow_id,
                "revision": revision,
                "semantic_hash": semantic_hash,
                "canonical_definition": canonical_definition,
                "plugin_resolution": self._services.codec.dumps(plugin_resolution),
                "source": source.source,
                "source_commit": source.source_commit,
                "environment": source.environment,
                "deployment_metadata": self._services.codec.dumps(source.deployment),
                "actor_id": actor_id,
            },
        )
        result = await connection.execute(
            _SELECT_FLOW_REVISION,
            {"tenant_id": tenant_id, "flow_id": flow_id, "revision": revision},
        )
        row = result.mappings().one()
        revision_id = UUID(str(row["id"]))
        if inserted_revision_id is not None:
            await store_flow_triggers(
                connection,
                tenant_id,
                revision_id,
                tuple(
                    trigger.model_dump(mode="json", by_alias=True, exclude_none=True)
                    for trigger in stored_flow.triggers
                ),
                actor_id,
            )
            await store_flow_check_definitions(
                connection,
                tenant_id,
                revision_id,
                stored_flow,
            )
        return revision_id, stored_flow, inserted_revision_id is not None

    async def _flow_resource_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        namespace: str,
        flow_id: str,
    ) -> RowMapping:
        result = await connection.execute(
            _SELECT_FLOW_RESOURCE,
            {"tenant_id": tenant_id, "namespace": namespace, "flow_key": flow_id},
        )
        row = result.mappings().one_or_none()
        if row is None:
            raise NotFoundError(
                "flow",
                f"{namespace}.{flow_id}",
                message=f"flow {namespace}.{flow_id} does not exist",
            )
        return row

    async def _select_flow_revision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        lifecycle: FlowLifecycle,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str | None,
        event_type: str,
    ) -> PersistedFlow:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            flow_row = await self._flow_resource_row(
                connection,
                tenant_uuid,
                namespace,
                flow_id,
            )
            definition = await connection.scalar(
                _GET_FLOW_REVISION_DOCUMENT,
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "flow_key": flow_id,
                    "revision": revision,
                },
            )
            if not isinstance(definition, dict):
                raise NotFoundError(
                    "flow revision",
                    f"{namespace}.{flow_id}:{revision}",
                    message=f"flow {namespace}.{flow_id} revision {revision} does not exist",
                )
            flow = FlowDefinition.model_validate(definition)
            activation = await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_row["id"],
                    "revision": revision,
                    "status": lifecycle.value,
                    "labels": self._services.codec.dumps(
                        {**flow.labels, **flow_system_labels(flow)}
                    ),
                    "annotations": self._services.codec.dumps(flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": None,
                },
            )
            if activation.scalar_one_or_none() is None:
                raise RepositoryVersionConflict(
                    f"flow {namespace}.{flow_id} changed during revision promotion"
                )
            flow_disabled = lifecycle is not FlowLifecycle.ACTIVE or flow.disabled
            await synchronize_flow_trigger_runtime(
                connection,
                tenant_uuid,
                UUID(str(flow_row["id"])),
                active_revision=revision,
                flow_disabled=flow_disabled,
            )
            await synchronize_active_flow_checks(
                connection,
                tenant_uuid,
                UUID(str(flow_row["id"])),
                active_revision=revision,
                flow_disabled=flow_disabled,
            )
            await self._record_flow_revision_event(
                connection,
                tenant_uuid,
                UUID(str(flow_row["id"])),
                revision,
                event_type=event_type,
                actor_id=actor_id,
                reason=reason,
                payload={"lifecycle": lifecycle.value},
            )
            result = await connection.execute(
                _GET_PERSISTED_FLOW,
                {"tenant_id": tenant_uuid, "flow_id": flow_row["id"]},
            )
            row = result.mappings().one()
        return _to_flow(row)

    async def _record_flow_revision_event(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        flow_id: UUID,
        revision: int,
        *,
        event_type: str,
        actor_id: str,
        reason: str | None = None,
        source: FlowRevisionSource | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        event_id = new_runtime_id()
        event_payload = {"revision": revision, **(payload or {})}
        await connection.execute(
            _INSERT_FLOW_REVISION_EVENT,
            {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "flow_id": flow_id,
                "revision": revision,
                "event_type": event_type,
                "actor_id": actor_id,
                "reason": reason,
                "payload": self._services.codec.dumps(event_payload),
            },
        )
        source_payload = (source or FlowRevisionSource()).model_dump(mode="json", exclude_none=True)
        await self._services.audit.write(
            connection,
            AuditWrite(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=event_type.lower(),
                resource_type="flow",
                resource_id=str(flow_id),
                reason=reason,
                source=source_payload,
                evidence=event_payload,
                event_id=new_runtime_id(),
                use_database_clock=True,
                generate_correlation_id=False,
            ),
        )
