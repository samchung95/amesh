from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import TenantPolicy, new_runtime_id
from amesh.ports.metadata_repository import (
    AssetAccessMode,
    AssetCatalogEntry,
    AssetCatalogExport,
    AssetHealth,
    AssetLineageDeclaration,
    AssetLineageEdge,
    AssetMetadata,
    AssetObservation,
    AssetObservationCreate,
    AssetRegistrationSource,
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionLogEntry,
    ExecutionMetric,
    ExecutionOutput,
    LineageEvidenceKind,
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
        size_bytes, media_type, checksum_sha256, logical_path, lineage, occurred_at
    )
    SELECT
        gen_random_uuid(), :tenant_id, :execution_id, :task_run_id, :attempt,
        item.uri, item."sizeBytes", item."mediaType", item."checksumSha256",
        item."logicalPath", COALESCE(item.lineage, '[]'::jsonb), :occurred_at
    FROM jsonb_to_recordset(CAST(:items AS jsonb)) AS item(
        uri text,
        "sizeBytes" bigint,
        "mediaType" text,
        "checksumSha256" text,
        "logicalPath" text,
        lineage jsonb
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
        id, tenant_id, namespace_name, provider, account, location, external_key,
        asset_type, display_name, description, owner, contacts, domain_group, tags,
        metadata, labels, health, last_materialization_at, source_kind,
        resource_version, created_by, updated_by
    ) VALUES (
        :id, :tenant_id, :namespace, :provider, :account, :location, :external_key,
        :asset_type, :display_name, :description, :owner, CAST(:contacts AS jsonb),
        :domain_group, CAST(:tags AS jsonb), CAST(:metadata AS jsonb),
        CAST(:labels AS jsonb), :health, :last_materialization_at, :source_kind,
        1, :actor_id, :actor_id
    )
    ON CONFLICT (tenant_id, provider, account, location, asset_type, external_key)
    DO UPDATE SET
        namespace_name = EXCLUDED.namespace_name,
        asset_type = EXCLUDED.asset_type,
        display_name = EXCLUDED.display_name,
        description = EXCLUDED.description,
        owner = EXCLUDED.owner,
        contacts = EXCLUDED.contacts,
        domain_group = EXCLUDED.domain_group,
        tags = EXCLUDED.tags,
        metadata = EXCLUDED.metadata,
        labels = EXCLUDED.labels,
        health = CASE
            WHEN EXCLUDED.health = 'UNKNOWN' THEN assets.health
            ELSE EXCLUDED.health
        END,
        last_materialization_at = COALESCE(
            EXCLUDED.last_materialization_at, assets.last_materialization_at
        ),
        source_kind = CASE
            WHEN EXCLUDED.source_kind = 'DECLARED' THEN 'DECLARED'
            ELSE assets.source_kind
        END,
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

_GET_ASSET = text(
    """
    SELECT assets.*, tenants.slug AS tenant_slug
    FROM assets
    JOIN tenants ON tenants.id = assets.tenant_id
    WHERE assets.tenant_id = :tenant_id AND assets.id = :asset_id
    """
)

_INSERT_ASSET_OBSERVATION = text(
    """
    INSERT INTO asset_observations (
        id, tenant_id, asset_id, namespace_name, access_mode, evidence_kind,
        confidence, flow_key, execution_id, task_run_id, artifact_id,
        metadata, observed_at, created_by
    ) VALUES (
        :id, :tenant_id, :asset_id, :namespace, :access_mode, :evidence_kind,
        :confidence, :flow_id, :execution_id, :task_run_id, :artifact_id,
        CAST(:metadata AS jsonb), COALESCE(:observed_at, clock_timestamp()), :actor_id
    )
    RETURNING *
    """
)

_INSERT_ASSET_LINEAGE = text(
    """
    INSERT INTO asset_lineage_edges (
        id, tenant_id, namespace_name, upstream_asset_id, downstream_asset_id,
        evidence_kind, confidence, flow_key, execution_id, task_run_id,
        artifact_id, metadata, observed_at, created_by
    ) VALUES (
        :id, :tenant_id, :namespace, :upstream_asset_id, :downstream_asset_id,
        :evidence_kind, :confidence, :flow_id, :execution_id, :task_run_id,
        :artifact_id, CAST(:metadata AS jsonb),
        COALESCE(:observed_at, clock_timestamp()), :actor_id
    )
    ON CONFLICT ON CONSTRAINT asset_lineage_identity_unique DO UPDATE SET
        confidence = GREATEST(asset_lineage_edges.confidence, EXCLUDED.confidence),
        metadata = asset_lineage_edges.metadata || EXCLUDED.metadata,
        observed_at = GREATEST(asset_lineage_edges.observed_at, EXCLUDED.observed_at),
        created_by = EXCLUDED.created_by
    RETURNING *
    """
)

_INFER_ASSET_LINEAGE = text(
    """
    INSERT INTO asset_lineage_edges (
        id, tenant_id, namespace_name, upstream_asset_id, downstream_asset_id,
        evidence_kind, confidence, flow_key, execution_id, task_run_id,
        artifact_id, metadata, observed_at, created_by
    )
    SELECT gen_random_uuid(), writes.tenant_id, writes.namespace_name,
           reads.asset_id, writes.asset_id, 'INFERRED',
           LEAST(reads.confidence, writes.confidence) * 0.8,
           writes.flow_key, writes.execution_id, writes.task_run_id,
           writes.artifact_id, '{}'::jsonb,
           GREATEST(reads.observed_at, writes.observed_at), :actor_id
    FROM asset_observations AS reads
    JOIN asset_observations AS writes
      ON writes.tenant_id = reads.tenant_id
     AND writes.execution_id = reads.execution_id
     AND writes.access_mode = 'WRITE'
    WHERE reads.tenant_id = :tenant_id
      AND reads.execution_id = :execution_id
      AND reads.access_mode = 'READ'
      AND reads.asset_id <> writes.asset_id
    ON CONFLICT ON CONSTRAINT asset_lineage_identity_unique DO UPDATE SET
        confidence = GREATEST(asset_lineage_edges.confidence, EXCLUDED.confidence),
        observed_at = GREATEST(asset_lineage_edges.observed_at, EXCLUDED.observed_at),
        created_by = EXCLUDED.created_by
    """
)

_LIST_ASSET_OBSERVATIONS = text(
    """
    SELECT observations.*, tenants.slug AS tenant_slug
    FROM asset_observations AS observations
    JOIN tenants ON tenants.id = observations.tenant_id
    WHERE observations.tenant_id = :tenant_id
      AND observations.asset_id = :asset_id
    ORDER BY observations.observed_at DESC, observations.id
    LIMIT 200
    """
)

_LIST_ASSET_LINEAGE = text(
    """
    SELECT edges.*, tenants.slug AS tenant_slug
    FROM asset_lineage_edges AS edges
    JOIN tenants ON tenants.id = edges.tenant_id
    WHERE edges.tenant_id = :tenant_id
      AND (edges.upstream_asset_id = :asset_id OR edges.downstream_asset_id = :asset_id)
    ORDER BY edges.observed_at DESC, edges.id
    """
)

_LIST_CATALOG_OBSERVATIONS = text(
    """
    SELECT observations.*, assets.provider, assets.account, assets.location,
           assets.asset_type, assets.external_key, assets.display_name,
           tenants.slug AS tenant_slug
    FROM asset_observations AS observations
    JOIN assets ON assets.tenant_id = observations.tenant_id
               AND assets.id = observations.asset_id
    JOIN tenants ON tenants.id = observations.tenant_id
    WHERE observations.tenant_id = :tenant_id
      AND (CAST(:namespace AS text) IS NULL OR observations.namespace_name = :namespace)
    ORDER BY observations.observed_at, observations.id
    """
)

_LIST_CATALOG_LINEAGE = text(
    """
    SELECT edges.*, upstream.provider AS upstream_provider,
           upstream.account AS upstream_account, upstream.location AS upstream_location,
           upstream.external_key AS upstream_external_key,
           downstream.provider AS downstream_provider,
           downstream.account AS downstream_account, downstream.location AS downstream_location,
           downstream.external_key AS downstream_external_key,
           tenants.slug AS tenant_slug
    FROM asset_lineage_edges AS edges
    JOIN assets AS upstream ON upstream.tenant_id = edges.tenant_id
                           AND upstream.id = edges.upstream_asset_id
    JOIN assets AS downstream ON downstream.tenant_id = edges.tenant_id
                             AND downstream.id = edges.downstream_asset_id
    JOIN tenants ON tenants.id = edges.tenant_id
    WHERE edges.tenant_id = :tenant_id
      AND (CAST(:namespace AS text) IS NULL OR edges.namespace_name = :namespace)
    ORDER BY edges.observed_at, edges.id
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


def _asset_parameters(
    asset: AssetMetadata,
    tenant_id: UUID,
    actor_id: str,
    expected_version: int | None,
) -> dict[str, object]:
    return {
        "id": asset.asset_id,
        "tenant_id": tenant_id,
        "namespace": asset.namespace,
        "provider": asset.provider,
        "account": asset.account,
        "location": asset.location,
        "external_key": asset.external_key,
        "asset_type": asset.asset_type,
        "display_name": asset.display_name,
        "description": asset.description,
        "owner": asset.owner,
        "contacts": json.dumps(asset.contacts),
        "domain_group": asset.domain_group,
        "tags": json.dumps(asset.tags),
        "metadata": json.dumps(asset.metadata),
        "labels": json.dumps(
            {
                **asset.labels,
                "amesh.asset.provider": asset.provider,
                "amesh.asset.type": asset.asset_type,
            }
        ),
        "health": asset.health.value,
        "last_materialization_at": asset.last_materialization_at,
        "source_kind": asset.source.value,
        "actor_id": actor_id,
        "expected_version": expected_version,
    }


async def _upsert_asset_with_connection(
    connection: AsyncConnection,
    tenant_id: UUID,
    asset: AssetMetadata,
    *,
    actor_id: str,
    expected_version: int | None = None,
) -> RowMapping:
    row = (
        (
            await connection.execute(
                _UPSERT_ASSET,
                _asset_parameters(asset, tenant_id, actor_id, expected_version),
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise MetadataVersionConflict(
            f"asset {asset.provider}/{asset.external_key} version is stale"
        )
    return row


async def _infer_asset_lineage(
    connection: AsyncConnection,
    tenant_id: UUID,
    execution_id: UUID | None,
    actor_id: str,
) -> None:
    if execution_id is None:
        return
    await connection.execute(
        _INFER_ASSET_LINEAGE,
        {"tenant_id": tenant_id, "execution_id": execution_id, "actor_id": actor_id},
    )


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
    assets = cast(list[dict[str, object]], evidence.get("assets", []))
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
    if assets:
        execution_context = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT namespace_name, flow_key
                        FROM executions
                        WHERE tenant_id = :tenant_id AND id = :execution_id
                        """
                    ),
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .one()
        )
        plugin_actor = f"plugin:{worker_id}" if worker_id is not None else "plugin:runtime"
        for item in assets:
            access_mode = AssetAccessMode(str(item["accessMode"]))
            asset = AssetMetadata.model_validate(
                {
                    **item,
                    "assetId": new_runtime_id(),
                    "namespace": execution_context["namespace_name"],
                    "health": (
                        AssetHealth.HEALTHY
                        if access_mode is AssetAccessMode.WRITE
                        else AssetHealth.UNKNOWN
                    ),
                    "lastMaterializationAt": (
                        occurred_at if access_mode is AssetAccessMode.WRITE else None
                    ),
                    "source": AssetRegistrationSource.PLUGIN_EVENT,
                }
            )
            asset_row = await _upsert_asset_with_connection(
                connection,
                tenant_id,
                asset,
                actor_id=plugin_actor,
            )
            artifact_id = None
            artifact_uri = item.get("artifactUri")
            if isinstance(artifact_uri, str):
                artifact_id = await connection.scalar(
                    text(
                        """
                        SELECT id FROM execution_artifacts
                        WHERE tenant_id = :tenant_id AND execution_id = :execution_id
                          AND task_run_id = :task_run_id AND uri = :uri
                        ORDER BY occurred_at DESC LIMIT 1
                        """
                    ),
                    {
                        "tenant_id": tenant_id,
                        "execution_id": execution_id,
                        "task_run_id": task_run_id,
                        "uri": artifact_uri,
                    },
                )
            await connection.execute(
                _INSERT_ASSET_OBSERVATION,
                {
                    "id": new_runtime_id(),
                    "tenant_id": tenant_id,
                    "asset_id": asset_row["id"],
                    "namespace": execution_context["namespace_name"],
                    "access_mode": access_mode.value,
                    "evidence_kind": LineageEvidenceKind.OBSERVED.value,
                    "confidence": 1.0,
                    "flow_id": execution_context["flow_key"],
                    "execution_id": execution_id,
                    "task_run_id": task_run_id,
                    "artifact_id": artifact_id,
                    "metadata": json.dumps({}),
                    "observed_at": occurred_at,
                    "actor_id": plugin_actor,
                },
            )
        await _infer_asset_lineage(connection, tenant_id, execution_id, plugin_actor)


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
            row = await _upsert_asset_with_connection(
                connection,
                tenant_uuid,
                asset,
                actor_id=actor_id,
                expected_version=expected_version,
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

    async def get_asset(self, asset_id: UUID, *, tenant_id: str) -> PersistedAsset:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_ASSET,
                        {"tenant_id": tenant_uuid, "asset_id": asset_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError("asset unavailable")
        return _to_asset(row, tenant_id)

    async def record_asset_observation(
        self,
        observation: AssetObservationCreate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> AssetObservation:
        asset = observation.asset
        if observation.access_mode is AssetAccessMode.WRITE:
            asset = asset.model_copy(
                update={
                    "health": AssetHealth.HEALTHY,
                    "last_materialization_at": observation.observed_at or datetime.now(UTC),
                }
            )
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            asset_row = await _upsert_asset_with_connection(
                connection,
                tenant_uuid,
                asset,
                actor_id=actor_id,
            )
            row = (
                (
                    await connection.execute(
                        _INSERT_ASSET_OBSERVATION,
                        {
                            "id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "asset_id": asset_row["id"],
                            "namespace": asset.namespace,
                            "access_mode": observation.access_mode.value,
                            "evidence_kind": observation.evidence_kind.value,
                            "confidence": observation.confidence,
                            "flow_id": observation.flow_id,
                            "execution_id": observation.execution_id,
                            "task_run_id": observation.task_run_id,
                            "artifact_id": observation.artifact_id,
                            "metadata": json.dumps(observation.metadata),
                            "observed_at": observation.observed_at,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _infer_asset_lineage(
                connection,
                tenant_uuid,
                observation.execution_id,
                actor_id,
            )
        return _to_asset_observation(row, tenant_id)

    async def declare_asset_lineage(
        self,
        declaration: AssetLineageDeclaration,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
    ) -> AssetLineageEdge:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _INSERT_ASSET_LINEAGE,
                        {
                            "id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "upstream_asset_id": declaration.upstream_asset_id,
                            "downstream_asset_id": declaration.downstream_asset_id,
                            "evidence_kind": declaration.evidence_kind.value,
                            "confidence": declaration.confidence,
                            "flow_id": declaration.flow_id,
                            "execution_id": declaration.execution_id,
                            "task_run_id": declaration.task_run_id,
                            "artifact_id": declaration.artifact_id,
                            "metadata": json.dumps(declaration.metadata),
                            "observed_at": declaration.observed_at,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _to_asset_lineage(row, tenant_id)

    async def get_asset_catalog_entry(
        self, asset_id: UUID, *, tenant_id: str
    ) -> AssetCatalogEntry:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            asset_row = (
                (
                    await connection.execute(
                        _GET_ASSET,
                        {"tenant_id": tenant_uuid, "asset_id": asset_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if asset_row is None:
                raise LookupError("asset unavailable")
            observation_rows = (
                (
                    await connection.execute(
                        _LIST_ASSET_OBSERVATIONS,
                        {"tenant_id": tenant_uuid, "asset_id": asset_id},
                    )
                )
                .mappings()
                .all()
            )
            edge_rows = (
                (
                    await connection.execute(
                        _LIST_ASSET_LINEAGE,
                        {"tenant_id": tenant_uuid, "asset_id": asset_id},
                    )
                )
                .mappings()
                .all()
            )
            all_assets = (
                (await connection.execute(_LIST_ASSETS, {"tenant_id": tenant_uuid}))
                .mappings()
                .all()
            )
        by_id = {row["id"]: _to_asset(row, tenant_id) for row in all_assets}
        upstream_ids = {
            row["upstream_asset_id"]
            for row in edge_rows
            if row["downstream_asset_id"] == asset_id
        }
        downstream_ids = {
            row["downstream_asset_id"]
            for row in edge_rows
            if row["upstream_asset_id"] == asset_id
        }
        return AssetCatalogEntry(
            asset=_to_asset(asset_row, tenant_id),
            upstream=tuple(by_id[item] for item in sorted(upstream_ids, key=str)),
            downstream=tuple(by_id[item] for item in sorted(downstream_ids, key=str)),
            observations=tuple(
                _to_asset_observation(row, tenant_id) for row in observation_rows
            ),
            edges=tuple(_to_asset_lineage(row, tenant_id) for row in edge_rows),
        )

    async def export_asset_catalog(
        self, *, tenant_id: str, namespace: str | None = None
    ) -> AssetCatalogExport:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            observation_rows = (
                (
                    await connection.execute(
                        _LIST_CATALOG_OBSERVATIONS,
                        {"tenant_id": tenant_uuid, "namespace": namespace},
                    )
                )
                .mappings()
                .all()
            )
            edge_rows = (
                (
                    await connection.execute(
                        _LIST_CATALOG_LINEAGE,
                        {"tenant_id": tenant_uuid, "namespace": namespace},
                    )
                )
                .mappings()
                .all()
            )
            generated_at = await connection.scalar(text("SELECT clock_timestamp()"))
        events = tuple(_openlineage_observation(row, tenant_id) for row in observation_rows) + tuple(
            _openlineage_edge(row, tenant_id) for row in edge_rows
        )
        return AssetCatalogExport(
            generatedAt=generated_at or datetime.now(UTC),
            producer="https://github.com/amesh-workflows/amesh",
            events=events,
        )


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
        logical_path=row["logical_path"],
        lineage=tuple(row["lineage"]),
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
        assetId=row["id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        provider=row["provider"],
        account=row["account"],
        location=row["location"],
        externalKey=row["external_key"],
        assetType=row["asset_type"],
        displayName=row["display_name"],
        description=row["description"],
        owner=row["owner"],
        contacts=tuple(row["contacts"]),
        domainGroup=row["domain_group"],
        tags=tuple(row["tags"]),
        customMetadata=row["metadata"],
        labels=row["labels"],
        health=row["health"],
        lastMaterializationAt=row["last_materialization_at"],
        source=row["source_kind"],
        resourceVersion=row["resource_version"],
        createdBy=row["created_by"],
        updatedBy=row["updated_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


def _to_asset_observation(row: RowMapping, tenant_id: str) -> AssetObservation:
    return AssetObservation(
        observationId=row["id"],
        assetId=row["asset_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        accessMode=row["access_mode"],
        evidenceKind=row["evidence_kind"],
        confidence=float(row["confidence"]),
        flowId=row["flow_key"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        artifactId=row["artifact_id"],
        metadata=row["metadata"],
        observedAt=row["observed_at"],
        createdBy=row["created_by"],
    )


def _to_asset_lineage(row: RowMapping, tenant_id: str) -> AssetLineageEdge:
    return AssetLineageEdge(
        edgeId=row["id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        upstreamAssetId=row["upstream_asset_id"],
        downstreamAssetId=row["downstream_asset_id"],
        evidenceKind=row["evidence_kind"],
        confidence=float(row["confidence"]),
        flowId=row["flow_key"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        artifactId=row["artifact_id"],
        metadata=row["metadata"],
        observedAt=row["observed_at"],
        createdBy=row["created_by"],
    )


def _openlineage_dataset(
    provider: str,
    account: str,
    location: str,
    external_key: str,
) -> dict[str, object]:
    return {
        "namespace": f"{provider}://{account}/{location}",
        "name": external_key,
    }


def _openlineage_observation(row: RowMapping, tenant_id: str) -> dict[str, object]:
    dataset = _openlineage_dataset(
        str(row["provider"]),
        str(row["account"]),
        str(row["location"]),
        str(row["external_key"]),
    )
    inputs = [dataset] if row["access_mode"] == AssetAccessMode.READ.value else []
    outputs = [dataset] if row["access_mode"] == AssetAccessMode.WRITE.value else []
    return {
        "eventType": "OTHER",
        "eventTime": row["observed_at"].isoformat(),
        "run": {"runId": str(row["execution_id"] or row["id"])},
        "job": {
            "namespace": f"amesh://{tenant_id}/{row['namespace_name']}",
            "name": str(row["flow_key"] or "asset-observation"),
        },
        "inputs": inputs,
        "outputs": outputs,
        "producer": "https://github.com/amesh-workflows/amesh",
        "schemaURL": (
            "https://openlineage.io/spec/1-0-5/OpenLineage.json#/definitions/RunEvent"
        ),
    }


def _openlineage_edge(row: RowMapping, tenant_id: str) -> dict[str, object]:
    return {
        "eventType": "OTHER",
        "eventTime": row["observed_at"].isoformat(),
        "run": {"runId": str(row["execution_id"] or row["id"])},
        "job": {
            "namespace": f"amesh://{tenant_id}/{row['namespace_name']}",
            "name": str(row["flow_key"] or "declared-lineage"),
        },
        "inputs": [
            _openlineage_dataset(
                str(row["upstream_provider"]),
                str(row["upstream_account"]),
                str(row["upstream_location"]),
                str(row["upstream_external_key"]),
            )
        ],
        "outputs": [
            _openlineage_dataset(
                str(row["downstream_provider"]),
                str(row["downstream_account"]),
                str(row["downstream_location"]),
                str(row["downstream_external_key"]),
            )
        ],
        "producer": "https://github.com/amesh-workflows/amesh",
        "schemaURL": (
            "https://openlineage.io/spec/1-0-5/OpenLineage.json#/definitions/RunEvent"
        ),
    }
