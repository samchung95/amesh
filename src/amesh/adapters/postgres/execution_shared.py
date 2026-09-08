"""Queries and value helpers shared by execution persistence responsibilities."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.domain import (
    TenantPolicy,
)
from amesh.dsl import FlowDefinition, compile_execution_tasks
from amesh.ports.tenant_repository import TenantUnavailableError

_DATABASE_TIME = text("SELECT clock_timestamp()")

_SELECT_FLOW_REVISION = text(
    """
    SELECT id, revision, semantic_hash, canonical_definition, plugin_resolution
    FROM flow_revisions
    WHERE tenant_id = :tenant_id
      AND flow_id = :flow_id
      AND revision = :revision
    """
)

_ACTIVATE_FLOW_REVISION = text(
    """
    UPDATE flows
    SET active_revision = :revision,
        status = :status,
        lifecycle = CASE WHEN :status = 'ARCHIVED' THEN 'ARCHIVED' ELSE 'ACTIVE' END,
        archived_at = CASE WHEN :status = 'ARCHIVED' THEN clock_timestamp() ELSE NULL END,
        labels = CAST(:labels AS jsonb),
        annotations = CAST(:annotations AS jsonb),
        updated_by = :actor_id,
        version = version + 1,
        updated_at = now()
    WHERE tenant_id = :tenant_id
      AND id = :flow_id
      AND (
          CAST(:expected_version AS bigint) IS NULL
          OR version = CAST(:expected_version AS bigint)
      )
    RETURNING version
    """
)

_INSERT_EXECUTION_EVENT = text(
    """
    INSERT INTO execution_events (
        tenant_id,
        execution_id,
        sequence,
        event_id,
        event_type,
        schema_version,
        idempotency_key,
        correlation_id,
        causation_id,
        actor_id,
        reason,
        occurred_at,
        trace_context,
        payload
    )
    VALUES (
        :tenant_id,
        :execution_id,
        :sequence,
        :event_id,
        :event_type,
        2,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        :reason,
        :occurred_at,
        CAST(:trace_context AS jsonb),
        '{}'::jsonb
    )
    """
)

_INSERT_TASK_RUN = text(
    """
    WITH inserted AS (
        INSERT INTO task_runs (
            id,
            tenant_id,
            execution_id,
            task_path,
            iteration_key,
            lifecycle_phase,
            labels,
            state,
            current_attempt,
            version
        )
        VALUES (
            :task_run_id,
            :tenant_id,
            :execution_id,
            :task_id,
            :iteration_key,
            :lifecycle_phase,
            CAST(:labels AS jsonb),
            'WAITING',
            0,
            1
        )
        ON CONFLICT (tenant_id, execution_id, task_path, iteration_key) DO NOTHING
        RETURNING id, tenant_id, execution_id, task_path, iteration_key,
                  lifecycle_phase, labels, version
    )
    INSERT INTO task_run_events (
        tenant_id,
        task_run_id,
        execution_id,
        sequence,
        event_id,
        event_type,
        schema_version,
        idempotency_key,
        correlation_id,
        causation_id,
        actor_id,
        reason,
        occurred_at,
        trace_context,
        payload
    )
    SELECT
        inserted.tenant_id,
        inserted.id,
        inserted.execution_id,
        inserted.version,
        :event_id,
        'TaskRunCreated',
        1,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        NULL,
        :occurred_at,
        CAST(:trace_context AS jsonb),
        jsonb_build_object(
            'task_id', inserted.task_path,
            'iteration_key', inserted.iteration_key,
            'lifecycle_phase', inserted.lifecycle_phase,
            'labels', inserted.labels
        )
    FROM inserted
    """
)


async def _load_tenant_policy(connection: AsyncConnection) -> TenantPolicy:
    settings = await connection.scalar(text("SELECT settings FROM tenants"))
    if settings is None:
        raise TenantUnavailableError("tenant is unavailable")
    return TenantPolicy.model_validate(settings)


def _require_allowed_plugins(policy: TenantPolicy, flow: FlowDefinition) -> None:
    denied = sorted(
        {
            node.task.type
            for node in compile_execution_tasks(flow)
            if not policy.allows_plugin(node.task.type)
        }
    )
    if denied:
        raise ValueError("tenant plugin policy does not allow: " + ", ".join(denied))
