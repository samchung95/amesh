from __future__ import annotations

import json
from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import TenantPolicy, new_runtime_id
from amesh.ports.metadata_repository import (
    AssetMetadata,
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionLogEntry,
    ExecutionMetric,
    ExecutionOutput,
    MetadataRepository,
    MetadataVersionConflict,
    PersistedAsset,
    PersistedTrigger,
    PersistedWorker,
    WorkerMetadata,
    WorkerStatus,
)
from amesh.workflow.metadata import validate_user_labels

from .quota import TenantQuotaType, reserve_tenant_quota
from .tenant_context import tenant_transaction

_INSERT_TRIGGER = text(
    """
    INSERT INTO trigger_definitions (
        id, tenant_id, flow_revision_id, trigger_key, trigger_type,
        definition, enabled, created_by
    ) VALUES (
        :id, :tenant_id, :flow_revision_id, :trigger_key, :trigger_type,
        CAST(:definition AS jsonb), :enabled, :created_by
    )
    ON CONFLICT (tenant_id, flow_revision_id, trigger_key) DO NOTHING
    """
)

_LIST_TRIGGERS_FOR_REVISION = text(
    """
    SELECT
        trigger_definitions.id,
        trigger_definitions.flow_revision_id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        trigger_definitions.trigger_key,
        trigger_definitions.trigger_type,
        trigger_definitions.definition,
        trigger_definitions.enabled,
        trigger_definitions.created_by,
        trigger_definitions.created_at
    FROM trigger_definitions
    JOIN tenants ON tenants.id = trigger_definitions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = trigger_definitions.flow_revision_id
    JOIN flows ON flows.id = flow_revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE trigger_definitions.tenant_id = :tenant_id
      AND trigger_definitions.flow_revision_id = :flow_revision_id
    ORDER BY trigger_definitions.trigger_key
    """
)

_LIST_TRIGGERS_FOR_FLOW = text(
    """
    SELECT
        trigger_definitions.id,
        trigger_definitions.flow_revision_id,
        tenants.slug AS tenant_slug,
        namespaces.name AS namespace,
        flows.flow_key,
        trigger_definitions.trigger_key,
        trigger_definitions.trigger_type,
        trigger_definitions.definition,
        trigger_definitions.enabled,
        trigger_definitions.created_by,
        trigger_definitions.created_at
    FROM trigger_definitions
    JOIN tenants ON tenants.id = trigger_definitions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = trigger_definitions.flow_revision_id
    JOIN flows ON flows.id = flow_revisions.flow_id
    JOIN namespaces ON namespaces.id = flows.namespace_id
    WHERE trigger_definitions.tenant_id = :tenant_id
      AND namespaces.name = :namespace
      AND flows.flow_key = :flow_key
    ORDER BY flow_revisions.revision, trigger_definitions.trigger_key
    """
)

_REGISTER_WORKER = text(
    """
    INSERT INTO workers (
        id, tenant_id, worker_group, instance_name, version, status,
        capabilities, labels, last_heartbeat_at, resource_version,
        created_by, updated_by, registered_at, updated_at
    ) VALUES (
        :id, :tenant_id, :worker_group, :instance_name, :version, :status,
        CAST(:capabilities AS jsonb), CAST(:labels AS jsonb), :last_heartbeat_at, 1,
        :actor_id, :actor_id, now(), now()
    )
    ON CONFLICT (tenant_id, worker_group, instance_name) DO UPDATE SET
        version = EXCLUDED.version,
        status = EXCLUDED.status,
        capabilities = EXCLUDED.capabilities,
        labels = EXCLUDED.labels,
        last_heartbeat_at = EXCLUDED.last_heartbeat_at,
        resource_version = workers.resource_version + 1,
        updated_by = EXCLUDED.updated_by,
        updated_at = now()
    RETURNING *
    """
)

_HEARTBEAT_WORKER = text(
    """
    UPDATE workers
    SET status = :status,
        last_heartbeat_at = :last_heartbeat_at,
        resource_version = resource_version + 1,
        updated_by = :actor_id,
        updated_at = now()
    WHERE id = :worker_id
      AND tenant_id = :tenant_id
      AND resource_version = :expected_version
    RETURNING *
    """
)

_LIST_WORKERS = text(
    """
    SELECT workers.*, tenants.slug AS tenant_slug
    FROM workers
    JOIN tenants ON tenants.id = workers.tenant_id
    WHERE workers.tenant_id = :tenant_id
    ORDER BY worker_group, instance_name
    """
)

_INSERT_LOG = text(
    """
    INSERT INTO execution_logs (
        id, tenant_id, execution_id, task_run_id, attempt, worker_id,
        trace_id, source_stream, level, logger, message, fields, redacted, occurred_at
    ) VALUES (
        :id, :tenant_id, :execution_id, :task_run_id, :attempt, :worker_id,
        :trace_id, :source_stream, :level, :logger, :message,
        CAST(:fields AS jsonb), :redacted, :occurred_at
    )
    RETURNING *
    """
)

_LIST_LOGS = text(
    """
    SELECT *
    FROM execution_logs
    WHERE tenant_id = :tenant_id AND execution_id = :execution_id
    ORDER BY occurred_at, id
    """
)

_INSERT_TASK_LOGS_BATCH = text(
    """
    INSERT INTO execution_logs (
        id, tenant_id, execution_id, task_run_id, attempt, worker_id,
        trace_id, source_stream, level, logger, message, fields, redacted, occurred_at
    )
    SELECT
        gen_random_uuid(), :tenant_id, :execution_id, :task_run_id, :attempt, :worker_id,
        item."traceId", COALESCE(item."sourceStream", 'TASK'),
        COALESCE(item.level, 'INFO'), COALESCE(item.logger, 'task'),
        COALESCE(item.message, ''), COALESCE(item.fields, '{}'::jsonb),
        COALESCE(item.redacted, false), COALESCE(item."occurredAt", :occurred_at)
    FROM jsonb_to_recordset(CAST(:items AS jsonb)) AS item(
        level text,
        logger text,
        message text,
        fields jsonb,
        redacted boolean,
        "sourceStream" text,
        "traceId" text,
        "occurredAt" timestamptz
    )
    """
)

_INSERT_METRIC = text(
    """
    INSERT INTO execution_metrics (
        id, tenant_id, execution_id, task_run_id, attempt, metric_name, metric_kind,
        metric_value, unit, labels, occurred_at
    ) VALUES (
        :id, :tenant_id, :execution_id, :task_run_id, :attempt, :metric_name, :metric_kind,
        :metric_value, :unit, CAST(:labels AS jsonb), :occurred_at
    )
    RETURNING *
    """
)

_LIST_METRICS = text(
    """
    SELECT *
    FROM execution_metrics
    WHERE tenant_id = :tenant_id AND execution_id = :execution_id
    ORDER BY occurred_at, id
    """
)

_INSERT_TASK_METRICS_BATCH = text(
    """
    INSERT INTO execution_metrics (
        id, tenant_id, execution_id, task_run_id, attempt, metric_name, metric_kind,
        metric_value, unit, labels, occurred_at
    )
    SELECT
        gen_random_uuid(), :tenant_id, :execution_id, :task_run_id, :attempt,
        item.name, COALESCE(item.kind, 'GAUGE'), item.value, item.unit,
        COALESCE(item.labels, '{}'::jsonb), :occurred_at
    FROM jsonb_to_recordset(CAST(:items AS jsonb)) AS item(
        name text,
        kind text,
        value numeric,
        unit text,
        labels jsonb
    )
    """
)

_INSERT_TASK_ARTIFACTS_BATCH = text(
    """
    INSERT INTO execution_artifacts (
        id, tenant_id, execution_id, task_run_id, attempt, uri,
        size_bytes, media_type, checksum_sha256, occurred_at
    )
    SELECT
        gen_random_uuid(), :tenant_id, :execution_id, :task_run_id, :attempt,
        item.uri, item."sizeBytes", item."mediaType", item."checksumSha256", :occurred_at
    FROM jsonb_to_recordset(CAST(:items AS jsonb)) AS item(
        uri text,
        "sizeBytes" bigint,
        "mediaType" text,
        "checksumSha256" text
    )
    """
)

_LIST_OUTPUTS = text(
    """
    SELECT *
    FROM execution_outputs
    WHERE tenant_id = :tenant_id AND execution_id = :execution_id
    ORDER BY occurred_at, id
    """
)

_LIST_ARTIFACTS = text(
    """
    SELECT *
    FROM execution_artifacts
    WHERE tenant_id = :tenant_id AND execution_id = :execution_id
    ORDER BY occurred_at, id
    """
)

_LIST_EVIDENCE_EVENTS = text(
    """
    SELECT *
    FROM execution_evidence_events
    WHERE tenant_id = :tenant_id
      AND execution_id = :execution_id
      AND cursor > :after_cursor
    ORDER BY cursor
    LIMIT :limit
    """
)

_UPSERT_ASSET = text(
    """
    INSERT INTO assets (
        id, tenant_id, provider, external_key, asset_type, display_name,
        metadata, labels, resource_version, created_by, updated_by
    ) VALUES (
        :id, :tenant_id, :provider, :external_key, :asset_type, :display_name,
        CAST(:metadata AS jsonb), CAST(:labels AS jsonb), 1, :actor_id, :actor_id
    )
    ON CONFLICT (tenant_id, provider, external_key) DO UPDATE SET
        asset_type = EXCLUDED.asset_type,
        display_name = EXCLUDED.display_name,
        metadata = EXCLUDED.metadata,
        labels = EXCLUDED.labels,
        resource_version = assets.resource_version + 1,
        updated_by = EXCLUDED.updated_by,
        updated_at = now()
    WHERE CAST(:expected_version AS bigint) IS NULL
       OR assets.resource_version = CAST(:expected_version AS bigint)
    RETURNING *
    """
)

_LIST_ASSETS = text(
    """
    SELECT assets.*, tenants.slug AS tenant_slug
    FROM assets
    JOIN tenants ON tenants.id = assets.tenant_id
    WHERE assets.tenant_id = :tenant_id
    ORDER BY provider, external_key
    """
)


async def store_flow_triggers(
    connection: AsyncConnection,
    tenant_id: UUID,
    flow_revision_id: UUID,
    definitions: tuple[dict[str, object], ...],
    actor_id: str,
) -> None:
    """Materialize immutable trigger definitions inside the flow write transaction."""

    parameters = [
        {
            "id": new_runtime_id(),
            "tenant_id": tenant_id,
            "flow_revision_id": flow_revision_id,
            "trigger_key": str(definition["id"]),
            "trigger_type": str(definition["type"]),
            "definition": json.dumps(definition),
            "enabled": not bool(definition.get("disabled", False)),
            "created_by": actor_id,
        }
        for definition in definitions
    ]
    if parameters:
        await connection.execute(_INSERT_TRIGGER, parameters)


async def store_task_evidence(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    execution_id: UUID,
    task_run_id: UUID,
    attempt: int,
    worker_id: UUID | None,
    output: dict[str, object],
    evidence: dict[str, object],
) -> None:
    """Project one normalized completion into queryable evidence in the same transaction."""

    occurred_at = await connection.scalar(text("SELECT clock_timestamp()"))
    logs = cast(list[dict[str, object]], evidence.get("logs", []))
    metrics = cast(list[dict[str, object]], evidence.get("metrics", []))
    artifacts = cast(list[dict[str, object]], evidence.get("artifacts", []))
    sizes = cast(dict[str, object], evidence.get("sizes", {}))

    if logs:
        await connection.execute(
            _INSERT_TASK_LOGS_BATCH,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "task_run_id": task_run_id,
                "attempt": attempt,
                "worker_id": worker_id,
                "occurred_at": occurred_at,
                "items": json.dumps(logs),
            },
        )
    if metrics:
        await connection.execute(
            _INSERT_TASK_METRICS_BATCH,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "task_run_id": task_run_id,
                "attempt": attempt,
                "occurred_at": occurred_at,
                "items": json.dumps(metrics),
            },
        )
    await connection.execute(
        text(
            """
            INSERT INTO execution_outputs (
                id, tenant_id, execution_id, task_run_id, attempt,
                value, size_bytes, sensitive, occurred_at
            ) VALUES (
                :id, :tenant_id, :execution_id, :task_run_id, :attempt,
                CAST(:value AS jsonb), :size_bytes, :sensitive, :occurred_at
            )
            """
        ),
        {
            "id": new_runtime_id(),
            "tenant_id": tenant_id,
            "execution_id": execution_id,
            "task_run_id": task_run_id,
            "attempt": attempt,
            "value": json.dumps(output),
            "size_bytes": int(
                cast(
                    int,
                    sizes.get(
                        "outputBytes",
                        len(json.dumps(output, separators=(",", ":")).encode("utf-8")),
                    ),
                )
            ),
            "sensitive": bool(evidence.get("outputSensitive", False)),
            "occurred_at": occurred_at,
        },
    )
    if artifacts:
        await connection.execute(
            _INSERT_TASK_ARTIFACTS_BATCH,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "task_run_id": task_run_id,
                "attempt": attempt,
                "occurred_at": occurred_at,
                "items": json.dumps(artifacts),
            },
        )


class PostgresMetadataRepository(MetadataRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def replace_flow_triggers(
        self,
        flow_revision_id: UUID,
        definitions: tuple[dict[str, object], ...],
        *,
        tenant_id: str,
        actor_id: str,
    ) -> list[PersistedTrigger]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await store_flow_triggers(
                connection,
                tenant_uuid,
                flow_revision_id,
                definitions,
                actor_id,
            )
            rows = (
                (
                    await connection.execute(
                        _LIST_TRIGGERS_FOR_REVISION,
                        {"tenant_id": tenant_uuid, "flow_revision_id": flow_revision_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_trigger(row) for row in rows]

    async def list_flow_triggers(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[PersistedTrigger]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_TRIGGERS_FOR_FLOW,
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_key": flow_id,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [_to_trigger(row) for row in rows]

    async def register_worker(
        self,
        worker: WorkerMetadata,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> PersistedWorker:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _REGISTER_WORKER,
                        {
                            "id": worker.worker_id,
                            "tenant_id": tenant_uuid,
                            "worker_group": worker.worker_group,
                            "instance_name": worker.instance_name,
                            "version": worker.version,
                            "status": worker.status.value,
                            "capabilities": json.dumps(worker.capabilities),
                            "labels": json.dumps(worker.labels),
                            "last_heartbeat_at": worker.last_heartbeat_at,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            return _to_worker(row, tenant_id)

    async def heartbeat_worker(
        self,
        worker_id: UUID,
        *,
        tenant_id: str,
        status: WorkerStatus,
        last_heartbeat_at: datetime,
        expected_version: int,
        actor_id: str,
    ) -> PersistedWorker:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _HEARTBEAT_WORKER,
                        {
                            "worker_id": worker_id,
                            "tenant_id": tenant_uuid,
                            "status": status.value,
                            "last_heartbeat_at": last_heartbeat_at,
                            "expected_version": expected_version,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise MetadataVersionConflict(
                    f"worker {worker_id} does not exist or version {expected_version} is stale"
                )
            return _to_worker(row, tenant_id)

    async def list_workers(self, *, tenant_id: str) -> list[PersistedWorker]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (await connection.execute(_LIST_WORKERS, {"tenant_id": tenant_uuid}))
                .mappings()
                .all()
            )
        return [_to_worker(row, tenant_id) for row in rows]

    async def append_log(
        self,
        entry: ExecutionLogEntry,
        *,
        tenant_id: str,
    ) -> ExecutionLogEntry:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            settings = await connection.scalar(
                text("SELECT settings FROM tenants WHERE id = :tenant_id FOR UPDATE"),
                {"tenant_id": tenant_uuid},
            )
            if settings is None:
                raise LookupError("tenant is unavailable")
            policy = TenantPolicy.model_validate(settings)
            encoded_fields = json.dumps(entry.fields)
            await reserve_tenant_quota(
                connection,
                tenant_uuid,
                TenantQuotaType.LOG_BYTES,
                len(entry.message.encode("utf-8")) + len(encoded_fields.encode("utf-8")),
                policy.max_log_bytes,
            )
            row = (
                (
                    await connection.execute(
                        _INSERT_LOG,
                        {
                            "id": entry.log_id,
                            "tenant_id": tenant_uuid,
                            "execution_id": entry.execution_id,
                            "task_run_id": entry.task_run_id,
                            "attempt": entry.attempt,
                            "worker_id": entry.worker_id,
                            "trace_id": entry.trace_id,
                            "source_stream": entry.source_stream.value,
                            "level": entry.level.value,
                            "logger": entry.logger,
                            "message": entry.message,
                            "fields": encoded_fields,
                            "redacted": entry.redacted,
                            "occurred_at": entry.occurred_at,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _to_log(row)

    async def list_logs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionLogEntry]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_LOGS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_log(row) for row in rows]

    async def append_metric(
        self,
        metric: ExecutionMetric,
        *,
        tenant_id: str,
    ) -> ExecutionMetric:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _INSERT_METRIC,
                        {
                            "id": metric.metric_id,
                            "tenant_id": tenant_uuid,
                            "execution_id": metric.execution_id,
                            "task_run_id": metric.task_run_id,
                            "attempt": metric.attempt,
                            "metric_name": metric.metric_name,
                            "metric_kind": metric.metric_kind.value,
                            "metric_value": metric.metric_value,
                            "unit": metric.unit,
                            "labels": json.dumps(metric.labels),
                            "occurred_at": metric.occurred_at,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _to_metric(row)

    async def list_metrics(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionMetric]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_METRICS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_metric(row) for row in rows]

    async def list_outputs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionOutput]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_OUTPUTS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_output(row) for row in rows]

    async def list_artifacts(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionArtifact]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_ARTIFACTS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_artifact(row) for row in rows]

    async def list_evidence_events(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        after_cursor: int = 0,
        limit: int = 500,
    ) -> list[ExecutionEvidenceEvent]:
        if not 1 <= limit <= 1000:
            raise ValueError("evidence event limit must be between 1 and 1000")
        if after_cursor < 0:
            raise ValueError("evidence event cursor cannot be negative")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_EVIDENCE_EVENTS,
                        {
                            "tenant_id": tenant_uuid,
                            "execution_id": execution_id,
                            "after_cursor": after_cursor,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [_to_evidence_event(row) for row in rows]

    async def upsert_asset(
        self,
        asset: AssetMetadata,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int | None = None,
    ) -> PersistedAsset:
        validate_user_labels(asset.labels)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _UPSERT_ASSET,
                        {
                            "id": asset.asset_id,
                            "tenant_id": tenant_uuid,
                            "provider": asset.provider,
                            "external_key": asset.external_key,
                            "asset_type": asset.asset_type,
                            "display_name": asset.display_name,
                            "metadata": json.dumps(asset.metadata),
                            "labels": json.dumps(
                                {
                                    **asset.labels,
                                    "amesh.asset.provider": asset.provider,
                                    "amesh.asset.type": asset.asset_type,
                                }
                            ),
                            "actor_id": actor_id,
                            "expected_version": expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise MetadataVersionConflict(
                    f"asset {asset.provider}/{asset.external_key} version is stale"
                )
            return _to_asset(row, tenant_id)

    async def list_assets(self, *, tenant_id: str) -> list[PersistedAsset]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (await connection.execute(_LIST_ASSETS, {"tenant_id": tenant_uuid}))
                .mappings()
                .all()
            )
        return [_to_asset(row, tenant_id) for row in rows]


def _to_trigger(row: RowMapping) -> PersistedTrigger:
    return PersistedTrigger(
        trigger_id=row["id"],
        flow_revision_id=row["flow_revision_id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        trigger_key=row["trigger_key"],
        trigger_type=row["trigger_type"],
        definition=row["definition"],
        enabled=row["enabled"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def _to_worker(row: RowMapping, tenant_id: str) -> PersistedWorker:
    return PersistedWorker(
        worker_id=row["id"],
        tenant_id=tenant_id,
        worker_group=row["worker_group"],
        instance_name=row["instance_name"],
        version=row["version"],
        status=row["status"],
        capabilities=row["capabilities"],
        labels=row["labels"],
        last_heartbeat_at=row["last_heartbeat_at"],
        resource_version=row["resource_version"],
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        created_at=row["registered_at"],
        updated_at=row["updated_at"],
    )


def _to_log(row: RowMapping) -> ExecutionLogEntry:
    return ExecutionLogEntry(
        log_id=row["id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        worker_id=row["worker_id"],
        trace_id=row["trace_id"],
        source_stream=row["source_stream"],
        level=row["level"],
        logger=row["logger"],
        message=row["message"],
        fields=row["fields"],
        redacted=row["redacted"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _to_metric(row: RowMapping) -> ExecutionMetric:
    return ExecutionMetric(
        metric_id=row["id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        metric_name=row["metric_name"],
        metric_kind=row["metric_kind"],
        metric_value=row["metric_value"],
        unit=row["unit"],
        labels=row["labels"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _to_output(row: RowMapping) -> ExecutionOutput:
    return ExecutionOutput(
        output_id=row["id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        value=row["value"],
        size_bytes=row["size_bytes"],
        sensitive=row["sensitive"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _to_artifact(row: RowMapping) -> ExecutionArtifact:
    return ExecutionArtifact(
        artifact_id=row["id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        uri=row["uri"],
        size_bytes=row["size_bytes"],
        media_type=row["media_type"],
        checksum_sha256=row["checksum_sha256"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _to_evidence_event(row: RowMapping) -> ExecutionEvidenceEvent:
    return ExecutionEvidenceEvent(
        cursor=row["cursor"],
        event_id=row["event_id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        kind=row["kind"],
        event_type=row["event_type"],
        payload=row["payload"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _to_asset(row: RowMapping, tenant_id: str) -> PersistedAsset:
    return PersistedAsset(
        asset_id=row["id"],
        tenant_id=tenant_id,
        provider=row["provider"],
        external_key=row["external_key"],
        asset_type=row["asset_type"],
        display_name=row["display_name"],
        metadata=row["metadata"],
        labels=row["labels"],
        resource_version=row["resource_version"],
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
