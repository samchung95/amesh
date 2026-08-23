from __future__ import annotations

import base64
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain.search import (
    SearchDocument,
    SearchDocumentType,
    SearchProjectionCondition,
    SearchProjectionStatus,
    SearchRangeField,
    SearchRequest,
    SearchResponse,
    SearchSortDirection,
    SearchSortField,
)
from amesh.ports.search_repository import SearchCursorError, SearchUnavailableError

from .tenant_context import tenant_transaction

_PROJECTION_VERSION = 1

_ENSURE_STATE = text(
    """
    INSERT INTO search_projection_state (tenant_id, projection_version)
    VALUES (:tenant_uuid, :projection_version)
    ON CONFLICT (tenant_id) DO NOTHING
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
        LEFT JOIN search_documents AS documents
          ON documents.tenant_id = flows.tenant_id
         AND documents.document_type = 'FLOW'
         AND documents.document_id = flows.id::text
        WHERE flows.tenant_id = :tenant_uuid
          AND flows.lifecycle <> 'TOMBSTONED'
          AND (
              documents.document_id IS NULL
              OR documents.source_version < flows.version
              OR documents.source_updated_at < flows.updated_at
          )
        ORDER BY flows.updated_at, flows.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'FLOW', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :projection_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, document_type, document_id) DO UPDATE SET
            namespace = EXCLUDED.namespace,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            occurred_at = EXCLUDED.occurred_at,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            projection_version = EXCLUDED.projection_version,
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
        LEFT JOIN search_documents AS documents
          ON documents.tenant_id = executions.tenant_id
         AND documents.document_type = 'EXECUTION'
         AND documents.document_id = executions.id::text
        WHERE executions.tenant_id = :tenant_uuid
          AND executions.lifecycle <> 'TOMBSTONED'
          AND (
              documents.document_id IS NULL
              OR documents.source_version < executions.version
              OR documents.source_updated_at < executions.updated_at
          )
        ORDER BY executions.updated_at, executions.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'EXECUTION', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :projection_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, document_type, document_id) DO UPDATE SET
            namespace = EXCLUDED.namespace,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            occurred_at = EXCLUDED.occurred_at,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            projection_version = EXCLUDED.projection_version,
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
        LEFT JOIN search_documents AS documents
          ON documents.tenant_id = logs.tenant_id
         AND documents.document_type = 'LOG'
         AND documents.document_id = logs.id::text
        WHERE logs.tenant_id = :tenant_uuid
          AND documents.document_id IS NULL
        ORDER BY logs.ingested_at, logs.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'LOG', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :projection_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, document_type, document_id) DO NOTHING
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
        LEFT JOIN search_documents AS documents
          ON documents.tenant_id = assets.tenant_id
         AND documents.document_type = 'ASSET'
         AND documents.document_id = assets.id::text
        WHERE assets.tenant_id = :tenant_uuid
          AND (
              documents.document_id IS NULL
              OR documents.source_version < assets.resource_version
              OR documents.source_updated_at < assets.updated_at
          )
        ORDER BY assets.updated_at, assets.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'ASSET', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :projection_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, document_type, document_id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            fields = EXCLUDED.fields,
            source_updated_at = EXCLUDED.source_updated_at,
            source_version = EXCLUDED.source_version,
            projection_version = EXCLUDED.projection_version,
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
        LEFT JOIN search_documents AS documents
          ON documents.tenant_id = audit.tenant_id
         AND documents.document_type = 'AUDIT'
         AND documents.document_id = audit.id::text
        WHERE audit.tenant_id = :tenant_uuid
          AND documents.document_id IS NULL
        ORDER BY audit.id
        LIMIT :limit
    ), projected AS (
        INSERT INTO search_documents (
            tenant_id, document_type, document_id, namespace, title, content, state,
            labels, fields, occurred_at, source_updated_at, source_version,
            projection_version, indexed_at
        )
        SELECT tenant_id, 'AUDIT', document_id, namespace, title, content, state,
               labels, fields, occurred_at, source_updated_at, source_version,
               :projection_version, clock_timestamp()
        FROM candidates
        ON CONFLICT (tenant_id, document_type, document_id) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) FROM projected
    """
)

_DELETE_STALE = text(
    """
    DELETE FROM search_documents AS documents
    WHERE documents.tenant_id = :tenant_uuid
      AND (
        (documents.document_type = 'FLOW' AND NOT EXISTS (
            SELECT 1 FROM flows
            WHERE flows.tenant_id = documents.tenant_id
              AND flows.id::text = documents.document_id
              AND flows.lifecycle <> 'TOMBSTONED'
        ))
        OR (documents.document_type = 'EXECUTION' AND NOT EXISTS (
            SELECT 1 FROM executions
            WHERE executions.tenant_id = documents.tenant_id
              AND executions.id::text = documents.document_id
              AND executions.lifecycle <> 'TOMBSTONED'
        ))
        OR (documents.document_type = 'LOG' AND NOT EXISTS (
            SELECT 1 FROM execution_logs
            WHERE execution_logs.tenant_id = documents.tenant_id
              AND execution_logs.id::text = documents.document_id
        ))
        OR (documents.document_type = 'ASSET' AND NOT EXISTS (
            SELECT 1 FROM assets
            WHERE assets.tenant_id = documents.tenant_id
              AND assets.id::text = documents.document_id
        ))
      )
    """
)

_SOURCE_DIAGNOSTICS = text(
    """
    SELECT
        (SELECT count(*) FROM flows
          WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED')
      + (SELECT count(*) FROM executions
          WHERE tenant_id = :tenant_uuid AND lifecycle <> 'TOMBSTONED')
      + (SELECT count(*) FROM execution_logs WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM assets WHERE tenant_id = :tenant_uuid)
      + (SELECT count(*) FROM audit_events WHERE tenant_id = :tenant_uuid)
        AS source_documents,
        GREATEST(
          (SELECT max(updated_at) FROM flows WHERE tenant_id = :tenant_uuid),
          (SELECT max(updated_at) FROM executions WHERE tenant_id = :tenant_uuid),
          (SELECT max(ingested_at) FROM execution_logs WHERE tenant_id = :tenant_uuid),
          (SELECT max(updated_at) FROM assets WHERE tenant_id = :tenant_uuid),
          (SELECT max(occurred_at) FROM audit_events WHERE tenant_id = :tenant_uuid)
        ) AS latest_source_at
    """
)

_STATUS = text(
    """
    SELECT state.*,
           (SELECT count(*) FROM search_documents
             WHERE tenant_id = state.tenant_id) AS actual_documents
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
        condition=SearchProjectionCondition(str(row["condition"])),
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
    )


class PostgresSearchRepository:
    """Optional tenant-isolated PostgreSQL FTS/trigram projection and projector."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def project_once(self, *, tenant_id: str, limit: int = 500) -> int:
        bounded_limit = max(1, min(limit, 5_000))
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "limit": bounded_limit,
                    "projection_version": _PROJECTION_VERSION,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                previous_condition = await connection.scalar(
                    text(
                        "SELECT condition FROM search_projection_state "
                        "WHERE tenant_id = :tenant_uuid"
                    ),
                    parameters,
                )
                projected = 0
                for statement in (
                    _FLOW_PROJECTION,
                    _EXECUTION_PROJECTION,
                    _LOG_PROJECTION,
                    _ASSET_PROJECTION,
                    _AUDIT_PROJECTION,
                ):
                    projected += int(await connection.scalar(statement, parameters) or 0)
                deleted = (await connection.execute(_DELETE_STALE, parameters)).rowcount or 0
                diagnostics = (
                    await connection.execute(_SOURCE_DIAGNOSTICS, parameters)
                ).mappings().one()
                actual_documents = int(
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM search_documents "
                            "WHERE tenant_id = :tenant_uuid"
                        ),
                        parameters,
                    )
                    or 0
                )
                rebuilding = previous_condition == SearchProjectionCondition.REBUILDING.value
                completed = rebuilding and projected == 0
                await connection.execute(
                    text(
                        """
                        UPDATE search_projection_state
                        SET condition = CASE
                                WHEN :rebuilding AND NOT :completed THEN 'REBUILDING'
                                ELSE 'READY'
                            END,
                            documents_indexed = :documents_indexed,
                            source_documents = :source_documents,
                            last_projected_at = clock_timestamp(),
                            latest_source_at = :latest_source_at,
                            rebuild_completed_at = CASE WHEN :completed
                                THEN clock_timestamp() ELSE rebuild_completed_at END,
                            last_error = NULL,
                            error_at = NULL,
                            resource_version = resource_version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_uuid
                        """
                    ),
                    {
                        **parameters,
                        "rebuilding": rebuilding,
                        "completed": completed,
                        "documents_indexed": actual_documents,
                        "source_documents": int(diagnostics["source_documents"]),
                        "latest_source_at": diagnostics["latest_source_at"],
                    },
                )
                if completed:
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
                                :projection_version,
                                jsonb_build_object(
                                    'documents', CAST(:documents_indexed AS bigint)
                                )
                            )
                            """
                        ),
                        {**parameters, "documents_indexed": actual_documents},
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
                    "projection_version": _PROJECTION_VERSION,
                    "error": bounded_error,
                }
                await connection.execute(_ENSURE_STATE, parameters)
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
                    "projection_version": _PROJECTION_VERSION,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                diagnostics = (
                    await connection.execute(_SOURCE_DIAGNOSTICS, parameters)
                ).mappings().one()
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
                return _status_from_row((await connection.execute(_STATUS, parameters)).mappings().one())
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search projection status unavailable") from exc

    async def request_rebuild(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> SearchProjectionStatus:
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters = {
                    "tenant_uuid": tenant_uuid,
                    "projection_version": _PROJECTION_VERSION,
                    "actor_id": actor_id,
                    "reason": reason,
                }
                await connection.execute(_ENSURE_STATE, parameters)
                await connection.execute(
                    text("DELETE FROM search_documents WHERE tenant_id = :tenant_uuid"), parameters
                )
                version = int(
                    await connection.scalar(
                        text(
                            """
                            UPDATE search_projection_state
                            SET projection_version = projection_version + 1,
                                condition = 'REBUILDING',
                                documents_indexed = 0,
                                rebuild_started_at = clock_timestamp(),
                                rebuild_completed_at = NULL,
                                last_error = NULL,
                                error_at = NULL,
                                resource_version = resource_version + 1,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_uuid
                            RETURNING projection_version
                            """
                        ),
                        parameters,
                    )
                    or _PROJECTION_VERSION
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
                            'SearchProjectionRebuildRequested', :actor_id, :reason,
                            :projection_version, '{}'::jsonb
                        )
                        """
                    ),
                    parameters,
                )
                diagnostics = (
                    await connection.execute(_SOURCE_DIAGNOSTICS, parameters)
                ).mappings().one()
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
                return _status_from_row((await connection.execute(_STATUS, parameters)).mappings().one())
        except SQLAlchemyError as exc:
            raise SearchUnavailableError("search rebuild could not be requested") from exc

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

        where = [
            "tenant_id = :tenant_uuid",
            "document_type = ANY(CAST(:types AS text[]))",
        ]
        parameters: dict[str, Any] = {
            "types": [item.value for item in ordered_types],
            "query": request.query.strip(),
            "limit": request.limit + 1,
            "offset": offset,
            "labels": json.dumps(request.labels),
            "fields": json.dumps(request.fields),
        }
        if request.query.strip():
            where.append(
                "(search_vector @@ websearch_to_tsquery('simple', :query) OR title % :query)"
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

        rank = (
            "CASE WHEN :query = '' THEN 0.0 ELSE "
            "ts_rank_cd(search_vector, websearch_to_tsquery('simple', :query)) "
            "+ similarity(title, :query) END"
        )
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
            FROM search_documents
            WHERE {' AND '.join(where)}
            ORDER BY {sort_column} {direction}, document_type ASC, document_id ASC
            LIMIT :limit OFFSET :offset
            """
        )
        try:
            async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
                parameters["tenant_uuid"] = tenant_uuid
                await connection.execute(text("SELECT set_config('statement_timeout', '1500', true)"))
                rows = (await connection.execute(statement, parameters)).mappings().all()
                status_parameters = {
                    "tenant_uuid": tenant_uuid,
                    "projection_version": _PROJECTION_VERSION,
                }
                await connection.execute(_ENSURE_STATE, status_parameters)
                state = (await connection.execute(_STATUS, status_parameters)).mappings().one()
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
            nextCursor=(
                _encode_cursor(offset + request.limit, fingerprint) if has_more else None
            ),
            deniedTypes=denied_types,
            projectionVersion=int(state["projection_version"]),
            projectionCondition=SearchProjectionCondition(str(state["condition"])),
        )
