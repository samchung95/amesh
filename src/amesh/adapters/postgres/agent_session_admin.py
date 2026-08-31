from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain.agent_session_fleet import (
    AgentSessionFleetAggregates,
    AgentSessionFleetItem,
    AgentSessionFleetPage,
    AgentSessionFleetQuery,
    AgentSessionInstanceAggregate,
    AgentSessionInstanceTenantAggregate,
    counters_from_json,
)
from amesh.domain.agent_sessions import AgentHarnessPin
from amesh.ports.agent_session_admin import AgentSessionFleetCursorError

from .tenant_context import tenant_transaction

_FLEET_CTE = """
WITH service_executions AS (
    SELECT
        e.id AS execution_id,
        e.tenant_id,
        e.namespace_name,
        e.state AS execution_state,
        e.version AS execution_version,
        e.epoch AS execution_epoch,
        e.created_at AS execution_created_at,
        e.updated_at AS execution_updated_at,
        e.terminal_at AS execution_terminal_at,
        e.trigger_context->>'ameshAgentSessionId' AS service_session_id,
        e.trigger_context->>'ameshAgentRef' AS agent_ref,
        e.trigger_context->>'ameshApplicationId' AS application_id,
        e.trigger_context->'ameshAgentSessionPolicy' AS policy_provenance,
        e.trigger_context->>'ameshActorId' AS owner_id
    FROM executions AS e
    WHERE e.tenant_id = :tenant_uuid
      AND e.trigger_context ? 'ameshAgentSessionId'
      {predicates}
), fleet AS (
    SELECT
        e.*,
        s.session_id AS attempt_session_id,
        s.task_run_id,
        s.attempt,
        s.namespace_name AS session_namespace,
        s.capability_pin_id,
        s.envelope_digest,
        s.state AS session_state,
        s.phase,
        s.version AS session_version,
        s.counters,
        s.harness_adapter,
        s.harness_version,
        s.harness_protocol,
        s.created_at AS session_created_at,
        s.updated_at AS session_updated_at,
        s.completed_at AS session_completed_at,
        CASE WHEN e.execution_state = 'SUCCESS' THEN 'SUCCEEDED'
             ELSE e.execution_state END AS lifecycle_state
    FROM service_executions AS e
    LEFT JOIN LATERAL (
        SELECT a.session_id, a.task_run_id, a.attempt, a.namespace_name,
               a.capability_pin_id, a.envelope_digest, a.state, a.phase, a.version,
               a.counters, a.harness_adapter, a.harness_version, a.harness_protocol,
               a.created_at, a.updated_at, a.completed_at
        FROM agent_sessions AS a
        WHERE a.tenant_id = e.tenant_id
          AND a.execution_id = e.execution_id
        ORDER BY a.attempt DESC, a.updated_at DESC, a.session_id DESC
        LIMIT 1
    ) AS s ON TRUE
), filtered AS (
    SELECT *
    FROM fleet
    WHERE TRUE
      {fleet_predicates}
), invocation_summary AS (
    SELECT
        i.tenant_id,
        i.execution_id,
        count(*) FILTER (WHERE i.kind = 'MODEL')::bigint AS model_count,
        count(*) FILTER (WHERE i.kind = 'TOOL')::bigint AS tool_count,
        count(*) FILTER (WHERE i.state = 'FAILED')::bigint AS failed_count,
        COALESCE(
            array_agg(DISTINCT i.provider_key ORDER BY i.provider_key)
                FILTER (WHERE i.provider_key IS NOT NULL),
            ARRAY[]::text[]
        ) AS dependency_keys
    FROM (
        SELECT inv.tenant_id, inv.execution_id, 'MODEL'::text AS kind, inv.state,
               NULL::text AS provider_key
        FROM agent_invocations AS inv
        JOIN filtered AS e
          ON e.tenant_id = inv.tenant_id AND e.execution_id = inv.execution_id
        UNION ALL
        SELECT inv.tenant_id, inv.execution_id, 'TOOL'::text AS kind, inv.state,
               inv.provider_key
        FROM tool_invocations AS inv
        JOIN filtered AS e
          ON e.tenant_id = inv.tenant_id AND e.execution_id = inv.execution_id
    ) AS i
    GROUP BY i.tenant_id, i.execution_id
)
"""


def _encode_cursor(
    *, tenant_id: str, fingerprint: str, created_at: datetime, execution_id: UUID
) -> str:
    payload = {
        "v": 1,
        "tenant": tenant_id,
        "fingerprint": fingerprint,
        "createdAt": created_at.isoformat(),
        "executionId": str(execution_id),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(value: str, *, tenant_id: str, fingerprint: str) -> tuple[datetime, UUID]:
    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        if (
            payload["v"] != 1
            or payload["tenant"] != tenant_id
            or payload["fingerprint"] != fingerprint
        ):
            raise ValueError
        created_at = datetime.fromisoformat(payload["createdAt"])
        execution_id = UUID(str(payload["executionId"]))
        if created_at.tzinfo is None:
            raise ValueError
        return created_at, execution_id
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
        raise AgentSessionFleetCursorError("agent-session fleet cursor is invalid") from exc


def _predicates(query: AgentSessionFleetQuery) -> tuple[str, str, dict[str, Any]]:
    clauses: list[str] = []
    fleet_clauses: list[str] = []
    params: dict[str, Any] = {}
    if query.namespace is not None:
        clauses.append("e.namespace_name = :namespace")
        params["namespace"] = query.namespace
    if query.agent_ref is not None:
        clauses.append("e.trigger_context->>'ameshAgentRef' = :agent_ref")
        params["agent_ref"] = query.agent_ref
    if query.owner_id is not None:
        clauses.append("e.trigger_context->>'ameshActorId' = :owner_id")
        params["owner_id"] = query.owner_id
    if query.created_from is not None:
        clauses.append("e.created_at >= :created_from")
        params["created_from"] = query.created_from
    if query.created_to is not None:
        clauses.append("e.created_at < :created_to")
        params["created_to"] = query.created_to
    if query.state is not None:
        clauses.append("(CASE WHEN e.state = 'SUCCESS' THEN 'SUCCEEDED' ELSE e.state END) = :state")
        params["state"] = query.state
    if query.harness is not None:
        fleet_clauses.append("f.harness_adapter = :harness")
        params["harness"] = query.harness
    return (
        (" AND " + " AND ".join(clauses)) if clauses else "",
        (" AND " + " AND ".join(fleet_clauses)) if fleet_clauses else "",
        params,
    )


def _row_item(row: Any, tenant_id: str) -> AgentSessionFleetItem:
    session_id = UUID(str(row["service_session_id"]))
    attempt_session_id = row["attempt_session_id"]
    session_created = row["session_created_at"]
    session_updated = row["session_updated_at"]
    created_at = session_created or row["execution_created_at"]
    updated_at = session_updated or row["execution_updated_at"]
    completed_at = row["session_completed_at"] or row["execution_terminal_at"]
    harness = None
    if row["harness_adapter"] is not None:
        harness = AgentHarnessPin(
            adapter=row["harness_adapter"],
            adapterVersion=row["harness_version"],
            protocol=row["harness_protocol"],
        )
    dependency_keys = tuple((row["dependency_keys"] or ())[:20])
    return AgentSessionFleetItem(
        sessionId=session_id,
        attemptSessionId=(UUID(str(attempt_session_id)) if attempt_session_id else None),
        tenantId=tenant_id,
        namespace=row["session_namespace"] or row["namespace_name"],
        agentRef=row["agent_ref"],
        applicationId=row["application_id"],
        ownerId=row["owner_id"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        attempt=row["attempt"],
        state=row["lifecycle_state"],
        phase=row["phase"],
        version=row["session_version"],
        executionVersion=row["execution_version"],
        executionEpoch=row["execution_epoch"],
        capabilityPinId=row["capability_pin_id"],
        envelopeDigest=row["envelope_digest"],
        harness=harness,
        counters=counters_from_json(row["counters"]),
        modelInvocationCount=int(row["model_count"] or 0),
        toolInvocationCount=int(row["tool_count"] or 0),
        failedInvocationCount=int(row["failed_count"] or 0),
        dependencyKeys=dependency_keys,
        dependencyHealth="DEGRADED" if row["failed_count"] else "HEALTHY",
        createdAt=created_at,
        updatedAt=updated_at,
        completedAt=completed_at,
        policyProvenance=row["policy_provenance"],
    )


def _aggregate(row: Any) -> AgentSessionFleetAggregates:
    by_state = dict(row["by_state"] or {})
    return AgentSessionFleetAggregates(
        matchedExecutions=int(row["matched_executions"] or 0),
        active=int(row["active"] or 0),
        terminal=int(row["terminal"] or 0),
        byState={str(key): int(value) for key, value in by_state.items()},
        totalTurns=int(row["total_turns"] or 0),
        totalToolCalls=int(row["total_tool_calls"] or 0),
        totalTokens=int(row["total_tokens"] or 0),
        totalCostUsd=str(row["total_cost_usd"] or Decimal("0")),
        modelInvocations=int(row["model_invocations"] or 0),
        toolInvocations=int(row["tool_invocations"] or 0),
        failedInvocations=int(row["failed_invocations"] or 0),
        degradedDependencies=int(row["degraded_dependencies"] or 0),
    )


class PostgresAgentSessionFleetRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def list_fleet(
        self,
        tenant_id: str,
        query: AgentSessionFleetQuery,
    ) -> AgentSessionFleetPage:
        predicate_sql, fleet_predicate_sql, filter_params = _predicates(query)
        fingerprint = query.fingerprint()
        cursor_values = (
            _decode_cursor(query.cursor, tenant_id=tenant_id, fingerprint=fingerprint)
            if query.cursor
            else None
        )
        page_predicate = ""
        cursor_params: dict[str, Any] = {}
        if cursor_values is not None:
            page_predicate = " AND (f.execution_created_at, f.execution_id) < (:cursor_created_at, :cursor_execution_id)"
            cursor_params = {
                "cursor_created_at": cursor_values[0],
                "cursor_execution_id": cursor_values[1],
            }
        params = {"tenant_uuid": tenant_id, **filter_params, **cursor_params}
        cte = _FLEET_CTE.format(
            predicates=predicate_sql,
            fleet_predicates=fleet_predicate_sql,
        )
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            params["tenant_uuid"] = tenant_uuid
            page_rows = (
                (
                    await connection.execute(
                        text(
                            cte
                            + """
SELECT f.*, COALESCE(i.model_count, 0) AS model_count,
       COALESCE(i.tool_count, 0) AS tool_count,
       COALESCE(i.failed_count, 0) AS failed_count,
       COALESCE(i.dependency_keys, ARRAY[]::text[]) AS dependency_keys
FROM filtered AS f
LEFT JOIN invocation_summary AS i
  ON i.tenant_id = f.tenant_id AND i.execution_id = f.execution_id
WHERE TRUE
"""
                            + page_predicate
                            + " ORDER BY f.execution_created_at DESC, f.execution_id DESC LIMIT :limit"
                        ),
                        {**params, "limit": query.limit + 1},
                    )
                )
                .mappings()
                .all()
            )
            aggregate_row = (
                (
                    await connection.execute(
                        text(
                            cte
                            + """
SELECT count(*)::bigint AS matched_executions,
       count(*) FILTER (WHERE f.lifecycle_state IN ('RUNNING', 'QUEUED', 'PAUSED', 'CANCELLING', 'RESTARTING', 'CREATED'))::bigint AS active,
       count(*) FILTER (WHERE f.lifecycle_state IN ('SUCCEEDED', 'FAILED', 'CANCELLED', 'WARNING'))::bigint AS terminal,
       (
           SELECT COALESCE(jsonb_object_agg(states.lifecycle_state, states.state_count), '{}'::jsonb)
           FROM (
               SELECT lifecycle_state, count(*)::bigint AS state_count
               FROM filtered
               GROUP BY lifecycle_state
           ) AS states
       ) AS by_state,
       COALESCE(sum(COALESCE((f.counters->>'turns')::bigint, 0)), 0)::bigint AS total_turns,
       COALESCE(sum(COALESCE((f.counters->>'toolCalls')::bigint, 0)), 0)::bigint AS total_tool_calls,
       COALESCE(sum(COALESCE((f.counters->>'totalTokens')::bigint, 0)), 0)::bigint AS total_tokens,
       COALESCE(sum(COALESCE((f.counters->>'costUsd')::numeric, 0)), 0)::numeric AS total_cost_usd,
       COALESCE(sum(COALESCE(i.model_count, 0)), 0)::bigint AS model_invocations,
       COALESCE(sum(COALESCE(i.tool_count, 0)), 0)::bigint AS tool_invocations,
       COALESCE(sum(COALESCE(i.failed_count, 0)), 0)::bigint AS failed_invocations,
       count(*) FILTER (WHERE COALESCE(i.failed_count, 0) > 0)::bigint AS degraded_dependencies
FROM filtered AS f
LEFT JOIN invocation_summary AS i
  ON i.tenant_id = f.tenant_id AND i.execution_id = f.execution_id
"""
                        ),
                        params,
                    )
                )
                .mappings()
                .one()
            )
        rows = page_rows[: query.limit]
        next_cursor = None
        if len(page_rows) > query.limit:
            last = rows[-1]
            next_cursor = _encode_cursor(
                tenant_id=tenant_id,
                fingerprint=fingerprint,
                created_at=last["execution_created_at"],
                execution_id=last["execution_id"],
            )
        return AgentSessionFleetPage(
            items=tuple(_row_item(row, tenant_id) for row in rows),
            nextCursor=next_cursor,
            aggregates=_aggregate(aggregate_row),
            readAt=datetime.now(UTC),
        )

    async def instance_aggregate(self) -> AgentSessionInstanceAggregate:
        async with self._engine.connect() as raw_connection:
            connection = await raw_connection.execution_options(isolation_level="READ COMMITTED")
            async with connection.begin():
                await connection.execute(text("SET LOCAL ROLE amesh_tenant_admin"))
                rows = (
                    (
                        await connection.execute(
                            text(
                                """
                            WITH state_counts AS (
                                SELECT tenant_id,
                                       CASE WHEN state = 'SUCCESS' THEN 'SUCCEEDED'
                                            ELSE state END AS lifecycle_state,
                                       count(*)::bigint AS state_count
                                FROM executions
                                WHERE trigger_context ? 'ameshAgentSessionId'
                                GROUP BY tenant_id, lifecycle_state
                            )
                            SELECT tenants.id AS tenant_id,
                                   tenants.slug AS tenant_slug,
                                   count(*)::bigint AS matched_executions,
                                   count(*) FILTER (
                                       WHERE executions.state IN
                                           ('CREATED', 'QUEUED', 'RUNNING', 'PAUSED',
                                            'CANCELLING', 'RESTARTING')
                                   )::bigint AS active,
                                   count(*) FILTER (
                                       WHERE executions.state IN
                                           ('SUCCESS', 'FAILED', 'CANCELLED', 'WARNING')
                                   )::bigint AS terminal,
                                   (
                                       SELECT COALESCE(
                                           jsonb_object_agg(
                                               state_counts.lifecycle_state,
                                               state_counts.state_count
                                           ), '{}'::jsonb
                                       )
                                       FROM state_counts
                                       WHERE state_counts.tenant_id = tenants.id
                                   ) AS by_state
                            FROM executions
                            JOIN tenants ON tenants.id = executions.tenant_id
                            WHERE executions.trigger_context ? 'ameshAgentSessionId'
                            GROUP BY tenants.id, tenants.slug
                            ORDER BY tenants.slug
                            """
                            )
                        )
                    )
                    .mappings()
                    .all()
                )
        tenant_items = tuple(
            AgentSessionInstanceTenantAggregate(
                tenantId=row["tenant_id"],
                tenantSlug=row["tenant_slug"],
                matchedExecutions=int(row["matched_executions"] or 0),
                active=int(row["active"] or 0),
                terminal=int(row["terminal"] or 0),
                byState={str(key): int(value) for key, value in (row["by_state"] or {}).items()},
            )
            for row in rows
        )
        return AgentSessionInstanceAggregate(
            tenants=tenant_items,
            matchedExecutions=sum(item.matched_executions for item in tenant_items),
            active=sum(item.active for item in tenant_items),
            terminal=sum(item.terminal for item in tenant_items),
            readAt=datetime.now(UTC),
        )
