from __future__ import annotations

import base64
import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain.search import (
    SearchDocument,
    SearchDocumentType,
    SearchProjectionCondition,
    SearchProjectionStatus,
    SearchProjectionVerification,
    SearchProjectionVerificationItem,
    SearchRangeField,
    SearchRequest,
    SearchResponse,
    SearchSortDirection,
    SearchSortField,
)
from amesh.observability import SEARCH_PROJECTION_LAG
from amesh.ports.search_repository import SearchCursorError, SearchUnavailableError

from .tenant_context import tenant_transaction

_SCHEMA_VERSION = 2
_ARCHIVE_DAYS = 7

_ENSURE_STATE = text(
    """
    INSERT INTO search_projection_state (tenant_id, projection_version, schema_version)
    VALUES (:tenant_uuid, 1, :schema_version)
    ON CONFLICT (tenant_id) DO UPDATE
    SET schema_version = GREATEST(search_projection_state.schema_version, EXCLUDED.schema_version)
    """
)

_FLOW_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT flows.tenant_id,
               flows.id::text AS document_id,
               namespaces.name AS namespace,
               namespaces.name || '.' || flows.flow_key AS title,
               concat_ws(' ', flows.flow_key, namespaces.name, flows.status,
                          revisions.canonical_definition ->> 'description') AS content,
               flows.status AS state,
               flows.labels,
               jsonb_build_object(
                   'flowId', flows.flow_key,
                   'revision', COALESCE(flows.active_revision, 0),
                   'lifecycle', flows.lifecycle
               ) AS fields,
               flows.created_at AS occurred_at,
               flows.updated_at AS source_updated_at,
               flows.version AS source_version
        FROM flows
        JOIN namespaces ON namespaces.id = flows.namespace_id
        LEFT JOIN flow_revisions AS revisions
          ON revisions.tenant_id = flows.tenant_id
         AND revisions.flow_id = flows.id
         AND revisions.revision = flows.active_revision
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = flows.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'FLOW'
         AND documents.document_id = flows.id::text
        WHERE flows.tenant_id = :tenant_uuid
          AND flows.lifecycle <> 'TOMBSTONED'
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR flows.created_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR flows.created_at <= CAST(:rebuild_to AS timestamptz))
          AND (
              documents.document_id IS NULL
              OR documents.source_version < flows.version
              OR documents.source_updated_at < flows.updated_at
          )
        ORDER BY flows.updated_at, flows.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'FLOW', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO UPDATE SET
            namespace = EXCLUDED.namespace,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            occurred_at = EXCLUDED.occurred_at,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            indexed_at = clock_timestamp()
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_EXECUTION_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT executions.tenant_id,
               executions.id::text AS document_id,
               executions.namespace_name AS namespace,
               executions.flow_key || ' · ' || executions.id::text AS title,
               concat_ws(' ', executions.id::text, executions.flow_key,
                          executions.namespace_name, executions.state) AS content,
               executions.state,
               executions.labels,
               jsonb_build_object(
                   'flowId', executions.flow_key,
                   'executionId', executions.id::text,
                   'lifecycle', executions.lifecycle
               ) AS fields,
               executions.created_at AS occurred_at,
               executions.updated_at AS source_updated_at,
               executions.version AS source_version
        FROM executions
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = executions.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'EXECUTION'
         AND documents.document_id = executions.id::text
        WHERE executions.tenant_id = :tenant_uuid
          AND executions.lifecycle <> 'TOMBSTONED'
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR executions.created_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR executions.created_at <= CAST(:rebuild_to AS timestamptz))
          AND (
              documents.document_id IS NULL
              OR documents.source_version < executions.version
              OR documents.source_updated_at < executions.updated_at
          )
        ORDER BY executions.updated_at, executions.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'EXECUTION', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO UPDATE SET
            namespace = EXCLUDED.namespace,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            occurred_at = EXCLUDED.occurred_at,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            indexed_at = clock_timestamp()
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_TASK_RUN_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT task_runs.tenant_id,
               task_runs.id::text AS document_id,
               executions.namespace_name AS namespace,
               task_runs.task_path || ' · ' || executions.flow_key AS title,
               concat_ws(' ', task_runs.task_path, task_runs.iteration_key,
                          task_runs.state, executions.id::text) AS content,
               task_runs.state,
               task_runs.labels,
               jsonb_strip_nulls(jsonb_build_object(
                   'flowId', executions.flow_key,
                   'executionId', task_runs.execution_id::text,
                   'taskRunId', task_runs.id::text,
                   'taskPath', task_runs.task_path,
                   'iterationKey', task_runs.iteration_key,
                   'currentAttempt', task_runs.current_attempt
               )) AS fields,
               task_runs.created_at AS occurred_at,
               task_runs.updated_at AS source_updated_at,
               task_runs.version AS source_version
        FROM task_runs
        JOIN executions
          ON executions.tenant_id = task_runs.tenant_id
         AND executions.id = task_runs.execution_id
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = task_runs.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'TASK_RUN'
         AND documents.document_id = task_runs.id::text
        WHERE task_runs.tenant_id = :tenant_uuid
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR task_runs.created_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR task_runs.created_at <= CAST(:rebuild_to AS timestamptz))
          AND (
              documents.document_id IS NULL
              OR documents.source_version < task_runs.version
              OR documents.source_updated_at < task_runs.updated_at
          )
        ORDER BY task_runs.updated_at, task_runs.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'TASK_RUN', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO UPDATE SET
            namespace = EXCLUDED.namespace,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            occurred_at = EXCLUDED.occurred_at,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            indexed_at = clock_timestamp()
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_LOG_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT logs.tenant_id,
               logs.id::text AS document_id,
               executions.namespace_name AS namespace,
               logs.level || ' · ' || logs.logger AS title,
               CASE WHEN logs.redacted THEN '' ELSE logs.message END AS content,
               logs.level AS state,
               '{}'::jsonb AS labels,
               jsonb_strip_nulls(jsonb_build_object(
                   'flowId', executions.flow_key,
                   'executionId', logs.execution_id::text,
                   'taskRunId', logs.task_run_id::text,
                   'level', logs.level,
                   'logger', logs.logger
               )) AS fields,
               logs.occurred_at,
               logs.ingested_at AS source_updated_at,
               0::bigint AS source_version
        FROM execution_logs AS logs
        JOIN executions
          ON executions.tenant_id = logs.tenant_id
         AND executions.id = logs.execution_id
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = logs.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'LOG'
         AND documents.document_id = logs.id::text
        WHERE logs.tenant_id = :tenant_uuid
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR logs.occurred_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR logs.occurred_at <= CAST(:rebuild_to AS timestamptz))
          AND documents.document_id IS NULL
        ORDER BY logs.ingested_at, logs.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'LOG', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_METRIC_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT metrics.tenant_id,
               metrics.id::text AS document_id,
               executions.namespace_name AS namespace,
               metrics.metric_name || ' · ' || metrics.metric_kind AS title,
               concat_ws(' ', metrics.metric_name, metrics.metric_kind,
                          metrics.metric_value::text, metrics.unit) AS content,
               metrics.metric_kind AS state,
               metrics.labels,
               jsonb_strip_nulls(jsonb_build_object(
                   'flowId', executions.flow_key,
                   'executionId', metrics.execution_id::text,
                   'taskRunId', metrics.task_run_id::text,
                   'metricName', metrics.metric_name,
                   'metricKind', metrics.metric_kind,
                   'unit', metrics.unit
               )) AS fields,
               metrics.occurred_at,
               metrics.occurred_at AS source_updated_at,
               0::bigint AS source_version
        FROM execution_metrics AS metrics
        JOIN executions
          ON executions.tenant_id = metrics.tenant_id
         AND executions.id = metrics.execution_id
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = metrics.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'METRIC'
         AND documents.document_id = metrics.id::text
        WHERE metrics.tenant_id = :tenant_uuid
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR metrics.occurred_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR metrics.occurred_at <= CAST(:rebuild_to AS timestamptz))
          AND documents.document_id IS NULL
        ORDER BY metrics.occurred_at, metrics.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'METRIC', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_ASSET_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT assets.tenant_id,
               assets.id::text AS document_id,
               assets.namespace_name AS namespace,
               assets.display_name AS title,
               concat_ws(' ', assets.display_name, assets.external_key,
                          assets.provider, assets.account, assets.location,
                          assets.asset_type, assets.description, assets.owner,
                          assets.domain_group) AS content,
               assets.asset_type AS state,
               assets.labels,
               jsonb_build_object(
                   'provider', assets.provider,
                   'account', assets.account,
                   'location', assets.location,
                   'assetType', assets.asset_type,
                   'externalKey', assets.external_key,
                   'health', assets.health
               ) AS fields,
               assets.created_at AS occurred_at,
               assets.updated_at AS source_updated_at,
               assets.resource_version AS source_version
        FROM assets
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = assets.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'ASSET'
         AND documents.document_id = assets.id::text
        WHERE assets.tenant_id = :tenant_uuid
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR assets.created_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR assets.created_at <= CAST(:rebuild_to AS timestamptz))
          AND (
              documents.document_id IS NULL
              OR documents.source_version < assets.resource_version
              OR documents.source_updated_at < assets.updated_at
          )
        ORDER BY assets.updated_at, assets.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'ASSET', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            indexed_at = clock_timestamp()
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_AUDIT_PROJECTION = text(
    """
    WITH candidates AS (
        SELECT audit.tenant_id,
               audit.id::text AS document_id,
               NULL::text AS namespace,
               audit.action || ' · ' || audit.resource_type AS title,
               concat_ws(' ', audit.action, audit.resource_type, audit.resource_id,
                          audit.outcome, audit.reason, audit.actor_id) AS content,
               audit.outcome AS state,
               '{}'::jsonb AS labels,
               jsonb_strip_nulls(jsonb_build_object(
                   'resourceType', audit.resource_type,
                   'resourceId', audit.resource_id,
                   'action', audit.action,
                   'outcome', audit.outcome,
                   'actorId', audit.actor_id
               )) AS fields,
               audit.occurred_at,
               audit.occurred_at AS source_updated_at,
               audit.id AS source_version
        FROM audit_events AS audit
        LEFT JOIN search_documents_v2 AS documents
          ON documents.tenant_id = audit.tenant_id
         AND documents.projection_version = :target_version
         AND documents.document_type = 'AUDIT'
         AND documents.document_id = audit.id::text
        WHERE audit.tenant_id = :tenant_uuid
          AND (CAST(:rebuild_from AS timestamptz) IS NULL
               OR audit.occurred_at >= CAST(:rebuild_from AS timestamptz))
          AND (CAST(:rebuild_to AS timestamptz) IS NULL
               OR audit.occurred_at <= CAST(:rebuild_to AS timestamptz))
          AND documents.document_id IS NULL
        ORDER BY audit.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents_v2 (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'AUDIT', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :target_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, projection_version, document_type, document_id) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_DELETE_ROLLUPS = text(
    """
    DELETE FROM search_projection_daily_rollups
    WHERE tenant_id = :tenant_uuid AND projection_version = :target_version
    """
)

_INSERT_ROLLUPS = text(
    """
    INSERT INTO search_projection_daily_rollups (
        tenant_id, projection_version, document_type, bucket_date,
        document_count, checksum, updated_at
    )
    SELECT tenant_id, projection_version, document_type, occurred_at::date,
           count(*)::bigint,
           md5(string_agg(document_id || ':' || source_version::text,
                          ',' ORDER BY document_id)),
           clock_timestamp()
    FROM search_documents_v2
    WHERE tenant_id = :tenant_uuid AND projection_version = :target_version
    GROUP BY tenant_id, projection_version, document_type, occurred_at::date
    """
)

_SOURCE_DIAGNOSTICS = text(
    """
    SELECT
        (SELECT count(*) FROM flows
          WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED')
      + (SELECT count(*) FROM executions
          WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED')
      + (SELECT count(*) FROM task_runs WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM execution_logs WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM execution_metrics WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM assets WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM audit_events WHERE tenant_id = :tenant_uuid)
        AS source_documents,
        GREATEST(
          (SELECT max(updated_at) FROM flows WHERE tenant_id = :tenant_uuid),
          (SELECT max(updated_at) FROM executions WHERE tenant_id = :tenant_uuid),
          (SELECT max(updated_at) FROM task_runs WHERE tenant_id = :tenant_uuid),
          (SELECT max(ingested_at) FROM execution_logs WHERE tenant_id = :tenant_uuid),
          (SELECT max(occurred_at) FROM execution_metrics WHERE tenant_id = :tenant_uuid),
          (SELECT max(updated_at) FROM assets WHERE tenant_id = :tenant_uuid),
          (SELECT max(occurred_at) FROM audit_events WHERE tenant_id = :tenant_uuid)
        ) AS latest_source_at
    """
)

_STATUS = text(
    """
    SELECT state.*,
           (SELECT count(*) FROM search_documents_v2
             WHERE tenant_id = state.tenant_id
               AND projection_version = CASE
                   WHEN state.condition = 'REBUILDING' THEN state.rebuild_version
                   ELSE state.projection_version
               END) AS actual_documents
    FROM search_projection_state AS state
    WHERE state.tenant_id = :tenant_uuid
    """
)

_SORT_SQL = {
    SearchSortField.RELEVANCE: "relevance",
    SearchSortField.TITLE: "lower(title)",
    SearchSortField.OCCURRED_AT: "occurred_at",
    SearchSortField.UPDATED_AT: "source_updated_at",
    SearchSortField.TYPE: "document_type",
    SearchSortField.STATE: "COALESCE(state, '')",
}

_RANGE_SQL = {
    SearchRangeField.OCCURRED_AT: "occurred_at",
    SearchRangeField.UPDATED_AT: "source_updated_at",
    SearchRangeField.SOURCE_VERSION: "source_version",
}

_DOCUMENT_PROJECTORS = {
    SearchDocumentType.FLOW: _FLOW_PROJECTION,
    SearchDocumentType.EXECUTION: _EXECUTION_PROJECTION,
    SearchDocumentType.TASK_RUN: _TASK_RUN_PROJECTION,
    SearchDocumentType.LOG: _LOG_PROJECTION,
    SearchDocumentType.METRIC: _METRIC_PROJECTION,
    SearchDocumentType.ASSET: _ASSET_PROJECTION,
    SearchDocumentType.AUDIT: _AUDIT_PROJECTION,
}

_SOURCE_IDENTITIES = {
    SearchDocumentType.FLOW: """
        SELECT id::text AS document_id, version::bigint AS source_version,
               updated_at AS source_updated_at
        FROM flows
        WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED'
    """,
    SearchDocumentType.EXECUTION: """
        SELECT id::text AS document_id, version::bigint AS source_version,
               updated_at AS source_updated_at
        FROM executions
        WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED'
    """,
    SearchDocumentType.TASK_RUN: """
        SELECT id::text AS document_id, version::bigint AS source_version,
               updated_at AS source_updated_at
        FROM task_runs WHERE tenant_id = :tenant_uuid
    """,
    SearchDocumentType.LOG: """
        SELECT id::text AS document_id, 0::bigint AS source_version,
               ingested_at AS source_updated_at
        FROM execution_logs WHERE tenant_id = :tenant_uuid
    """,
    SearchDocumentType.METRIC: """
        SELECT id::text AS document_id, 0::bigint AS source_version,
               occurred_at AS source_updated_at
        FROM execution_metrics WHERE tenant_id = :tenant_uuid
    """,
    SearchDocumentType.ASSET: """
        SELECT id::text AS document_id, resource_version::bigint AS source_version,
               updated_at AS source_updated_at
        FROM assets WHERE tenant_id = :tenant_uuid
    """,
    SearchDocumentType.AUDIT: """
        SELECT id::text AS document_id, id::bigint AS source_version,
               occurred_at AS source_updated_at
        FROM audit_events WHERE tenant_id = :tenant_uuid
    """,
}


async def _archive_and_delete_stale(
    connection: AsyncConnection,
    parameters: dict[str, Any],
) -> int:
    deleted = 0
    for document_type in SearchDocumentType:
        typed_parameters = {**parameters, "document_type": document_type.value}
        await connection.execute(
            text(
                f"""
                WITH source_ids AS ({_SOURCE_IDENTITIES[document_type]})
                INSERT INTO search_projection_archives (
                    tenant_id, projection_version, document_type, document_id,
                    namespace, title, content, state, labels, fields, occurred_at,
                    source_updated_at, source_version, source_policy, archived_at, purge_at
                )
                SELECT documents.tenant_id, documents.projection_version,
                       documents.document_type, documents.document_id, documents.namespace,
                       documents.title, documents.content, documents.state, documents.labels,
                       documents.fields, documents.occurred_at, documents.source_updated_at,
                       documents.source_version, 'authoritative-source-retention',
                       clock_timestamp(),
                       clock_timestamp() + make_interval(days => :archive_days)
                FROM search_documents_v2 AS documents
                WHERE documents.tenant_id = :tenant_uuid
                  AND documents.projection_version = :target_version
                  AND documents.document_type = :document_type
                  AND NOT EXISTS (
                      SELECT 1 FROM source_ids
                      WHERE source_ids.document_id = documents.document_id
                  )
                ON CONFLICT (tenant_id, projection_version, document_type, document_id)
                DO UPDATE SET archived_at = EXCLUDED.archived_at,
                              purge_at = EXCLUDED.purge_at,
                              source_policy = EXCLUDED.source_policy
                """
            ),
            typed_parameters,
        )
        result = await connection.execute(
            text(
                f"""
                WITH source_ids AS ({_SOURCE_IDENTITIES[document_type]})
                DELETE FROM search_documents_v2 AS documents
                WHERE documents.tenant_id = :tenant_uuid
                  AND documents.projection_version = :target_version
                  AND documents.document_type = :document_type
                  AND NOT EXISTS (
                      SELECT 1 FROM source_ids
                      WHERE source_ids.document_id = documents.document_id
                  )
                """
            ),
            typed_parameters,
        )
        deleted += result.rowcount or 0
    return deleted


def _encode_cursor(offset: int, fingerprint: str) -> str:
    raw = json.dumps({"offset": offset, "fingerprint": fingerprint}, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _decode_cursor(value: str | None, fingerprint: str) -> int:
    if value is None:
        return 0
    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        offset = int(payload["offset"])
        if offset < 0 or payload["fingerprint"] != fingerprint:
            raise ValueError
        return offset
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SearchCursorError("search cursor is invalid for this request") from exc


async def _verify_generation(
    connection: AsyncConnection,
    *,
    tenant_uuid: Any,
    projection_version: int,
    persist: bool,
) -> SearchProjectionVerification:
    items: list[SearchProjectionVerificationItem] = []
    verified_at = datetime.now(UTC)
    for document_type in SearchDocumentType:
        source = (
            (
                await connection.execute(
                    text(
                        f"""
                    WITH identities AS ({_SOURCE_IDENTITIES[document_type]})
                    SELECT count(*)::bigint AS row_count,
                           md5(COALESCE(string_agg(
                               document_id || ':' || source_version::text,
                               ',' ORDER BY document_id
                           ), '')) AS checksum,
                           max(source_updated_at) AS last_updated_at,
                           max(document_id) AS last_document_id
                    FROM identities
                    """
                    ),
                    {"tenant_uuid": tenant_uuid},
                )
            )
            .mappings()
            .one()
        )
        projected = (
            (
                await connection.execute(
                    text(
                        """
                    SELECT count(*)::bigint AS row_count,
                           md5(COALESCE(string_agg(
                               document_id || ':' || source_version::text,
                               ',' ORDER BY document_id
                           ), '')) AS checksum,
                           max(source_updated_at) AS last_updated_at,
                           max(document_id) AS last_document_id
                    FROM search_documents_v2
                    WHERE tenant_id = :tenant_uuid
                      AND projection_version = :projection_version
                      AND document_type = :document_type
                    """
                    ),
                    {
                        "tenant_uuid": tenant_uuid,
                        "projection_version": projection_version,
                        "document_type": document_type.value,
                    },
                )
            )
            .mappings()
            .one()
        )
        source_count = int(source["row_count"])
        projected_count = int(projected["row_count"])
        source_checksum = str(source["checksum"])
        projected_checksum = str(projected["checksum"])
        verified = source_count == projected_count and source_checksum == projected_checksum
        last_position = {
            "sourceUpdatedAt": (
                source["last_updated_at"].isoformat()
                if source["last_updated_at"] is not None
                else None
            ),
            "documentId": source["last_document_id"],
        }
        item = SearchProjectionVerificationItem(
            documentType=document_type,
            sourceCount=source_count,
            projectedCount=projected_count,
            sourceChecksum=source_checksum,
            projectedChecksum=projected_checksum,
            lastPosition=last_position,
            verified=verified,
        )
        items.append(item)
        if persist:
            await connection.execute(
                text(
                    """
                    INSERT INTO search_projection_checkpoints (
                        tenant_id, projection_version, document_type, source_count,
                        projected_count, source_checksum, projected_checksum,
                        last_position, verified, verified_at, updated_at
                    ) VALUES (
                        :tenant_uuid, :projection_version, :document_type, :source_count,
                        :projected_count, :source_checksum, :projected_checksum,
                        CAST(:last_position AS jsonb), :verified, :verified_at, clock_timestamp()
                    )
                    ON CONFLICT (tenant_id, projection_version, document_type) DO UPDATE SET
                        source_count = EXCLUDED.source_count,
                        projected_count = EXCLUDED.projected_count,
                        source_checksum = EXCLUDED.source_checksum,
                        projected_checksum = EXCLUDED.projected_checksum,
                        last_position = EXCLUDED.last_position,
                        verified = EXCLUDED.verified,
                        verified_at = EXCLUDED.verified_at,
                        updated_at = clock_timestamp()
                    """
                ),
                {
                    "tenant_uuid": tenant_uuid,
                    "projection_version": projection_version,
                    "document_type": document_type.value,
                    "source_count": source_count,
                    "projected_count": projected_count,
                    "source_checksum": source_checksum,
                    "projected_checksum": projected_checksum,
                    "last_position": json.dumps(last_position),
                    "verified": verified,
                    "verified_at": verified_at,
                },
            )
    checksum = hashlib.sha256(
        "|".join(f"{item.document_type.value}:{item.projected_checksum}" for item in items).encode()
    ).hexdigest()
    return SearchProjectionVerification(
        projectionVersion=projection_version,
        schemaVersion=_SCHEMA_VERSION,
        verified=all(item.verified for item in items),
        checksum=checksum,
        items=tuple(items),
        verifiedAt=verified_at,
    )


def _status_from_row(row: RowMapping) -> SearchProjectionStatus:
    source_documents = int(row["source_documents"])
    actual_documents = int(row["actual_documents"])
    latest_source_at = row["latest_source_at"]
    last_projected_at = row["last_projected_at"]
    lag_seconds = None
    if latest_source_at is not None and last_projected_at is not None:
        lag_seconds = max(0.0, (latest_source_at - last_projected_at).total_seconds())
    progress = 1.0 if source_documents == 0 else min(1.0, actual_documents / source_documents)
    return SearchProjectionStatus(
        projectionVersion=int(row["projection_version"]),
        schemaVersion=int(row["schema_version"]),
        buildingVersion=(
            int(row["rebuild_version"]) if row["rebuild_version"] is not None else None
        ),
        condition=SearchProjectionCondition(str(row["condition"])),
        enabled=bool(row["enabled"]),
        documentsIndexed=actual_documents,
        sourceDocuments=source_documents,
        progress=progress,
        lastProjectedAt=last_projected_at,
        latestSourceAt=latest_source_at,
        lagSeconds=lag_seconds,
        rebuildStartedAt=row["rebuild_started_at"],
        rebuildCompletedAt=row["rebuild_completed_at"],
        failures=int(row["failure_count"]),
        lastError=row["last_error"],
        checkpointsVerified=bool(row["checkpoints_verified"]),
        activeChecksum=row["active_checksum"],
    )


class PostgresSearchRepository:
    """Optional tenant-isolated PostgreSQL FTS/trigram projection and projector."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def project_once(self, *, tenant_id: str, limit: int = 500) -> int:
        bounded_limit = max(1, min(limit, 5_000))
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                base_parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                }
                await connection.execute(_ENSURE_STATE, base_parameters)
                state = (
                    (
                        await connection.execute(
                            text(
                                """
                            SELECT projection_version, rebuild_version, condition,
                                   rebuild_types, rebuild_from, rebuild_to, active_checksum
                            FROM search_projection_state
                            WHERE tenant_id = :tenant_uuid
                            FOR UPDATE
                            """
                            ),
                            base_parameters,
                        )
                    )
                    .mappings()
                    .one()
                )
                condition = SearchProjectionCondition(str(state["condition"]))
                if condition is SearchProjectionCondition.DISABLED:
                    return 0
                rebuilding = condition is SearchProjectionCondition.REBUILDING
                active_version = int(state["projection_version"])
                target_version = (
                    int(state["rebuild_version"])
                    if rebuilding and state["rebuild_version"] is not None
                    else active_version
                )
                parameters = {
                    **base_parameters,
                    "limit": bounded_limit,
                    "target_version": target_version,
                    "rebuild_from": None,
                    "rebuild_to": None,
                    "archive_days": _ARCHIVE_DAYS,
                }
                projected = 0
                for document_type in SearchDocumentType:
                    projected += int(
                        await connection.scalar(_DOCUMENT_PROJECTORS[document_type], parameters)
                        or 0
                    )
                deleted = 0
                if projected == 0:
                    deleted = await _archive_and_delete_stale(connection, parameters)
                    await connection.execute(
                        text(
                            "DELETE FROM search_projection_archives "
                            "WHERE tenant_id = :tenant_uuid AND purge_at <= clock_timestamp()"
                        ),
                        parameters,
                    )
                    await connection.execute(_DELETE_ROLLUPS, parameters)
                    await connection.execute(_INSERT_ROLLUPS, parameters)
                diagnostics = (
                    (await connection.execute(_SOURCE_DIAGNOSTICS, parameters)).mappings().one()
                )
                actual_documents = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_documents_v2 "
                            "WHERE tenant_id = :tenant_uuid "
                            "AND projection_version = :target_version"
                        ),
                        parameters,
                    )
                    or 0
                )
                verification = (
                    await _verify_generation(
                        connection,
                        tenant_uuid=tenant_uuid,
                        projection_version=target_version,
                        persist=True,
                    )
                    if projected == 0
                    else None
                )
                checkpoints_verified = verification is not None and verification.verified
                completed = rebuilding and checkpoints_verified
                next_condition = (
                    SearchProjectionCondition.READY
                    if not rebuilding or completed
                    else SearchProjectionCondition.REBUILDING
                )
                if not rebuilding and verification is not None and not verification.verified:
                    next_condition = SearchProjectionCondition.DEGRADED
                active_checksum = (
                    verification.checksum
                    if verification is not None and verification.verified and not rebuilding
                    else state["active_checksum"]
                )
                if completed and verification is not None:
                    active_checksum = verification.checksum
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET projection_version = CASE WHEN :completed
                                THEN :target_version ELSE projection_version END,
                            rebuild_version = CASE WHEN :completed THEN NULL ELSE rebuild_version END,
                            rebuild_types = CASE WHEN :completed THEN NULL ELSE rebuild_types END,
                            rebuild_from = CASE WHEN :completed THEN NULL ELSE rebuild_from END,
                            rebuild_to = CASE WHEN :completed THEN NULL ELSE rebuild_to END,
                            condition = :condition,
                            documents_indexed = :documents_indexed,
                            source_documents = :source_documents,
                            last_projected_at = clock_timestamp(),
                            latest_source_at = :latest_source_at,
                            rebuild_completed_at = CASE WHEN :completed
                                THEN clock_timestamp() ELSE rebuild_completed_at END,
                            last_error = NULL,
                            error_at = NULL,
                            checkpoints_verified = :checkpoints_verified,
                            active_checksum = :active_checksum,
                            resource_version = resource_version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    {
                        **parameters,
                        "completed": completed,
                        "condition": next_condition.value,
                        "documents_indexed": actual_documents,
                        "source_documents": int(diagnostics["source_documents"]),
                        "latest_source_at": diagnostics["latest_source_at"],
                        "checkpoints_verified": checkpoints_verified,
                        "active_checksum": active_checksum,
                    },
                )
                if completed:
                    await connection.execute(
                        text(
                            """
                            DELETE FROM search_documents_v2
                            WHERE tenant_id = :tenant_uuid
                              AND projection_version <> :target_version
                            """
                        ),
                        parameters,
                    )
                    await connection.execute(
                        text(
                            """
                            DELETE FROM search_projection_daily_rollups
                            WHERE tenant_id = :tenant_uuid
                              AND projection_version <> :target_version
                            """
                        ),
                        parameters,
                    )
                    await connection.execute(
                        text(
                            """
                            INSERT INTO search_projection_events (
                                event_id, tenant_id, event_type, actor_id, reason,
                                projection_version, payload
                            ) VALUES (
                                gen_random_uuid(), :tenant_uuid,
                                'SearchProjectionRebuildCompleted', 'system:indexer',
                                'authoritative projection rebuild converged',
                                :target_version,
                                jsonb_build_object(
                                    'documents', CAST(:documents_indexed AS bigint),
                                    'checksum', CAST(:checksum AS text)
                                )
                            )
                            """
                        ),
                        {
                            **parameters,
                            "documents_indexed": actual_documents,
                            "checksum": active_checksum,
                        },
                    )
                return projected + int(deleted)
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection cycle unavailable") from exc

    async def record_failure(self, *, tenant_id: str, error: str) -> None:
        bounded_error = error[:2_000]
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                    "error": bounded_error,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                parameters["projection_version"] = int(
                    await connection.scalar(
                        text(
                            "SELECT projection_version FROM search_projection_state "
                            "WHERE tenant_id = :tenant_uuid"
                        ),
                        parameters,
                    )
                    or 1
                )
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET condition = 'DEGRADED',
                            failure_count = failure_count + 1,
                            last_error = :error,
                            error_at = clock_timestamp(),
                            resource_version = resource_version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    parameters,
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_projection_events (
                            event_id, tenant_id, event_type, actor_id, reason,
                            projection_version, payload
                        ) VALUES (
                            gen_random_uuid(), :tenant_uuid, 'SearchProjectionFailed',
                            'system:indexer', 'optional search projection cycle failed',
                            :projection_version,
                            jsonb_build_object('error', CAST(:error AS text))
                        )
                        """
                    ),
                    parameters,
                )
        except SQLAlchemyError:
            return

    async def status(self, *, tenant_id: str) -> SearchProjectionStatus:
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                diagnostics = (
                    (await connection.execute(_SOURCE_DIAGNOSTICS, parameters)).mappings().one()
                )
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET source_documents = :source_documents,
                            latest_source_at = :latest_source_at
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    {
                        **parameters,
                        "source_documents": int(diagnostics["source_documents"]),
                        "latest_source_at": diagnostics["latest_source_at"],
                    },
                )
                status = _status_from_row(
                    (await connection.execute(_STATUS, parameters)).mappings().one()
                )
                SEARCH_PROJECTION_LAG.set(status.lag_seconds or 0)
                return status
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection status unavailable") from exc

    async def request_rebuild(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
        document_types: tuple[SearchDocumentType, ...] = (),
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> SearchProjectionStatus:
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                selected_types = tuple(sorted(set(document_types), key=lambda item: item.value))
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                    "actor_id": actor_id,
                    "reason": reason,
                    "types": [item.value for item in selected_types],
                    "all_types": not selected_types,
                    "rebuild_types": (
                        [item.value for item in selected_types] if selected_types else None
                    ),
                    "rebuild_from": from_time,
                    "rebuild_to": to_time,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                state = (
                    (
                        await connection.execute(
                            text(
                                """
                            SELECT projection_version, rebuild_version
                            FROM search_projection_state
                            WHERE tenant_id = :tenant_uuid
                            FOR UPDATE
                            """
                            ),
                            parameters,
                        )
                    )
                    .mappings()
                    .one()
                )
                active_version = int(state["projection_version"])
                target_version = (
                    max(
                        active_version,
                        int(state["rebuild_version"] or active_version),
                    )
                    + 1
                )
                parameters.update(
                    {
                        "active_version": active_version,
                        "target_version": target_version,
                    }
                )
                await connection.execute(
                    text(
                        "DELETE FROM search_documents_v2 "
                        "WHERE tenant_id = :tenant_uuid AND projection_version = :target_version"
                    ),
                    parameters,
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_documents_v2 (
                            tenant_id, projection_version, document_type, document_id,
                            namespace, title, content, state, labels, fields, occurred_at,
                            source_updated_at, source_version, indexed_at
                        )
                        SELECT tenant_id, :target_version, document_type, document_id,
                               namespace, title, content, state, labels, fields, occurred_at,
                               source_updated_at, source_version, indexed_at
                        FROM search_documents_v2
                        WHERE tenant_id = :tenant_uuid
                          AND projection_version = :active_version
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    parameters,
                )
                await connection.execute(
                    text(
                        """
                        DELETE FROM search_documents_v2
                        WHERE tenant_id = :tenant_uuid
                          AND projection_version = :target_version
                          AND (:all_types OR document_type = ANY(CAST(:types AS text[])))
                          AND (CAST(:rebuild_from AS timestamptz) IS NULL
                               OR occurred_at >= CAST(:rebuild_from AS timestamptz))
                          AND (CAST(:rebuild_to AS timestamptz) IS NULL
                               OR occurred_at <= CAST(:rebuild_to AS timestamptz))
                        """
                    ),
                    parameters,
                )
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET rebuild_version = :target_version,
                            rebuild_types = CAST(:rebuild_types AS text[]),
                            rebuild_from = :rebuild_from,
                            rebuild_to = :rebuild_to,
                            enabled = true,
                            condition = 'REBUILDING',
                                documents_indexed = 0,
                                checkpoints_verified = false,
                                rebuild_started_at = clock_timestamp(),
                                rebuild_completed_at = NULL,
                                last_error = NULL,
                                error_at = NULL,
                                resource_version = resource_version + 1,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_uuid
                            """
                    ),
                    parameters,
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_projection_events (
                            event_id, tenant_id, event_type, actor_id, reason,
                            projection_version, payload
                        ) VALUES (
                            gen_random_uuid(), :tenant_uuid,
                            'SearchProjectionRebuildRequested', :actor_id, :reason,
                            :target_version,
                            jsonb_strip_nulls(jsonb_build_object(
                                'types', CAST(:rebuild_types AS text[]),
                                'from', CAST(:rebuild_from AS timestamptz),
                                'to', CAST(:rebuild_to AS timestamptz)
                            ))
                        )
                        """
                    ),
                    parameters,
                )
                diagnostics = (
                    (await connection.execute(_SOURCE_DIAGNOSTICS, parameters)).mappings().one()
                )
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET source_documents = :source_documents,
                            latest_source_at = :latest_source_at
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    {
                        **parameters,
                        "source_documents": int(diagnostics["source_documents"]),
                        "latest_source_at": diagnostics["latest_source_at"],
                    },
                )
                return _status_from_row(
                    (await connection.execute(_STATUS, parameters)).mappings().one()
                )
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search rebuild could not be requested") from exc

    async def set_enabled(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        enabled: bool,
        reason: str,
    ) -> SearchProjectionStatus:
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                    "actor_id": actor_id,
                    "reason": reason,
                    "enabled": enabled,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                version = int(
                    await connection.scalar(
                        text(
                            """
                            UPDATE search_projection_state
                            SET enabled = :enabled,
                                condition = CASE
                                    WHEN NOT :enabled THEN 'DISABLED'
                                    WHEN rebuild_version IS NOT NULL THEN 'REBUILDING'
                                    ELSE 'READY'
                                END,
                                resource_version = resource_version + 1,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_uuid
                            RETURNING projection_version
                            """
                        ),
                        parameters,
                    )
                    or 1
                )
                parameters["projection_version"] = version
                await connection.execute(
                    text(
                        """
                        INSERT INTO search_projection_events (
                            event_id, tenant_id, event_type, actor_id, reason,
                            projection_version, payload
                        ) VALUES (
                            gen_random_uuid(), :tenant_uuid,
                            'SearchProjectionControlChanged', :actor_id, :reason,
                            :projection_version,
                            jsonb_build_object('enabled', CAST(:enabled AS boolean))
                        )
                        """
                    ),
                    parameters,
                )
                diagnostics = (
                    (await connection.execute(_SOURCE_DIAGNOSTICS, parameters)).mappings().one()
                )
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET source_documents = :source_documents,
                            latest_source_at = :latest_source_at
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    {
                        **parameters,
                        "source_documents": int(diagnostics["source_documents"]),
                        "latest_source_at": diagnostics["latest_source_at"],
                    },
                )
                return _status_from_row(
                    (await connection.execute(_STATUS, parameters)).mappings().one()
                )
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection control unavailable") from exc

    async def verify(self, *, tenant_id: str) -> SearchProjectionVerification:
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {"tenant_uuid": tenant_uuid, "schema_version": _SCHEMA_VERSION}
                await connection.execute(_ENSURE_STATE, parameters)
                projection_version = int(
                    await connection.scalar(
                        text(
                            "SELECT projection_version FROM search_projection_state "
                            "WHERE tenant_id = :tenant_uuid"
                        ),
                        parameters,
                    )
                    or 1
                )
                return await _verify_generation(
                    connection,
                    tenant_uuid=tenant_uuid,
                    projection_version=projection_version,
                    persist=True,
                )
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection verification unavailable") from exc

    async def search(
        self,
        request: SearchRequest,
        *,
        tenant_id: str,
        authorized_types: tuple[SearchDocumentType, ...],
        denied_types: tuple[SearchDocumentType, ...] = (),
    ) -> SearchResponse:
        ordered_types = tuple(sorted(set(authorized_types), key=lambda item: item.value))
        fingerprint = request.fingerprint(authorized_types=ordered_types)
        offset = _decode_cursor(request.cursor, fingerprint)
        if not ordered_types:
            status = await self.status(tenant_id=tenant_id)
            return SearchResponse(
                items=(),
                nextCursor=None,
                deniedTypes=denied_types,
                projectionVersion=status.projection_version,
                projectionCondition=status.condition,
            )

        response_denied = denied_types
        authoritative_fallback = False
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                status_parameters = {
                    "tenant_uuid": tenant_uuid,
                    "schema_version": _SCHEMA_VERSION,
                }
                await connection.execute(_ENSURE_STATE, status_parameters)
                state = (await connection.execute(_STATUS, status_parameters)).mappings().one()
                authoritative_fallback = (
                    not bool(state["enabled"])
                    or str(state["condition"]) == SearchProjectionCondition.DISABLED.value
                )
                selected_types = ordered_types
                source_sql = "search_documents_v2"
                rank = (
                    "CASE WHEN :query = '' THEN 0.0 ELSE "
                    "ts_rank_cd(search_vector, websearch_to_tsquery('simple', :query)) "
                    "+ similarity(title, :query) END"
                )
                if authoritative_fallback:
                    fallback_types = tuple(
                        item
                        for item in ordered_types
                        if item in {SearchDocumentType.FLOW, SearchDocumentType.EXECUTION}
                    )
                    unsupported = set(ordered_types) - set(fallback_types)
                    response_denied = tuple(
                        sorted(set(denied_types) | unsupported, key=lambda item: item.value)
                    )
                    selected_types = fallback_types
                    source_sql = """
                        (
                            SELECT 'FLOW'::text AS document_type, flows.id::text AS document_id,
                                   namespaces.name AS namespace,
                                   namespaces.name || '.' || flows.flow_key AS title,
                                   concat_ws(' ', flows.flow_key, namespaces.name, flows.status,
                                             revisions.canonical_definition ->> 'description') AS content,
                                   flows.status AS state, flows.labels,
                                   jsonb_build_object(
                                       'flowId', flows.flow_key,
                                       'revision', COALESCE(flows.active_revision, 0),
                                       'lifecycle', flows.lifecycle
                                   ) AS fields,
                                   flows.created_at AS occurred_at,
                                   flows.updated_at AS source_updated_at,
                                   flows.version AS source_version
                            FROM flows
                            JOIN namespaces ON namespaces.id = flows.namespace_id
                            LEFT JOIN flow_revisions AS revisions
                              ON revisions.tenant_id = flows.tenant_id
                             AND revisions.flow_id = flows.id
                             AND revisions.revision = flows.active_revision
                            WHERE flows.tenant_id = :tenant_uuid
                              AND flows.lifecycle <> 'TOMBSTONED'
                            UNION ALL
                            SELECT 'EXECUTION'::text, executions.id::text,
                                   executions.namespace_name,
                                   executions.flow_key || ' · ' || executions.id::text,
                                   concat_ws(' ', executions.id::text, executions.flow_key,
                                             executions.namespace_name, executions.state),
                                   executions.state, executions.labels,
                                   jsonb_build_object(
                                       'flowId', executions.flow_key,
                                       'executionId', executions.id::text,
                                       'lifecycle', executions.lifecycle
                                   ),
                                   executions.created_at, executions.updated_at, executions.version
                            FROM executions
                            WHERE executions.tenant_id = :tenant_uuid
                              AND executions.lifecycle <> 'TOMBSTONED'
                        ) AS authoritative_documents
                    """
                    rank = (
                        "CASE WHEN :query = '' THEN 0.0 "
                        "WHEN lower(title || ' ' || content) LIKE "
                        "'%' || lower(:query) || '%' THEN 1.0 ELSE 0.0 END"
                    )
                if not selected_types:
                    return SearchResponse(
                        items=(),
                        nextCursor=None,
                        deniedTypes=response_denied,
                        projectionVersion=int(state["projection_version"]),
                        projectionCondition=SearchProjectionCondition(str(state["condition"])),
                        authoritativeFallback=authoritative_fallback,
                    )
                where = [
                    "tenant_id = :tenant_uuid" if not authoritative_fallback else "TRUE",
                    "document_type = ANY(CAST(:types AS text[]))",
                ]
                parameters: dict[str, Any] = {
                    "tenant_uuid": tenant_uuid,
                    "projection_version": int(state["projection_version"]),
                    "types": [item.value for item in selected_types],
                    "query": request.query.strip(),
                    "limit": request.limit + 1,
                    "offset": offset,
                    "labels": json.dumps(request.labels),
                    "fields": json.dumps(request.fields),
                }
                if not authoritative_fallback:
                    where.append("projection_version = :projection_version")
                if request.query.strip():
                    where.append(
                        "lower(title || ' ' || content) LIKE '%' || lower(:query) || '%'"
                        if authoritative_fallback
                        else "(search_vector @@ websearch_to_tsquery('simple', :query) "
                        "OR title % :query)"
                    )
                if request.namespace is not None:
                    where.append("namespace = :namespace")
                    parameters["namespace"] = request.namespace
                if request.states:
                    where.append("state = ANY(CAST(:states AS text[]))")
                    parameters["states"] = list(request.states)
                if request.labels:
                    where.append("labels @> CAST(:labels AS jsonb)")
                if request.fields:
                    where.append("fields @> CAST(:fields AS jsonb)")
                if request.from_time is not None:
                    where.append("occurred_at >= :from_time")
                    parameters["from_time"] = request.from_time
                if request.to_time is not None:
                    where.append("occurred_at <= :to_time")
                    parameters["to_time"] = request.to_time
                for index, item in enumerate(request.ranges):
                    column = _RANGE_SQL[item.field]
                    if item.gte is not None:
                        key = f"range_{index}_gte"
                        where.append(f"{column} >= :{key}")
                        parameters[key] = item.gte
                    if item.lte is not None:
                        key = f"range_{index}_lte"
                        where.append(f"{column} <= :{key}")
                        parameters[key] = item.lte
                sort_column = _SORT_SQL[request.sort]
                direction = "ASC" if request.direction is SearchSortDirection.ASC else "DESC"
                if request.sort is SearchSortField.RELEVANCE:
                    sort_column = "relevance"
                statement = text(
                    f"""
                    SELECT document_type, document_id, namespace, title,
                           left(content, 500) AS summary, state, labels, fields,
                           occurred_at, source_updated_at, source_version,
                           {rank} AS relevance
                    FROM {source_sql}
                    WHERE {" AND ".join(where)}
                    ORDER BY {sort_column} {direction}, document_type ASC, document_id ASC
                    LIMIT :limit OFFSET :offset
                    """
                )
                await connection.execute(
                    text("SELECT set_config('statement_timeout', '1500', true)")
                )
                rows = (await connection.execute(statement, parameters)).mappings().all()
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection unavailable") from exc

        has_more = len(rows) > request.limit
        selected: list[RowMapping] = list(rows[: request.limit])
        items = tuple(
            SearchDocument(
                documentType=SearchDocumentType(str(row["document_type"])),
                documentId=str(row["document_id"]),
                namespace=row["namespace"],
                title=str(row["title"]),
                summary=str(row["summary"]),
                state=row["state"],
                labels=dict(row["labels"]),
                fields=dict(row["fields"]),
                occurredAt=row["occurred_at"],
                updatedAt=row["source_updated_at"],
                sourceVersion=int(row["source_version"]),
                relevance=max(0.0, float(row["relevance"])),
            )
            for row in selected
        )
        return SearchResponse(
            items=items,
            nextCursor=(_encode_cursor(offset + request.limit, fingerprint) if has_more else None),
            deniedTypes=response_denied,
            projectionVersion=int(state["projection_version"]),
            projectionCondition=SearchProjectionCondition(str(state["condition"])),
            authoritativeFallback=authoritative_fallback,
        )
