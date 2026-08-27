from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.admission_policy import policy_decision_metadata
from amesh.determinism import admission_policy_pins, build_determinism_envelope
from amesh.domain import (
    AdmissionBehavior,
    AdmissionDecision,
    AdmissionDiagnostics,
    AdmissionOutcome,
    AdmissionResourceType,
    AdmissionScope,
    ExecutionEventType,
    ExecutionState,
    FailureCategory,
    FlowLifecycle,
    FlowRevisionDiff,
    FlowRevisionRecord,
    FlowRevisionSource,
    PluginPolicyStage,
    PolicyDecision,
    PolicyStage,
    ResolvedAdmissionPolicy,
    ResourceMetadata,
    ResourceVersionConflict,
    TaskRunEventType,
    TaskRunLifecyclePhase,
    TaskRunState,
    TenantPolicy,
    TransitionRejectionCode,
    compare_flow_revisions,
    new_runtime_id,
    resolve_admission_policies,
    resource_etag,
)
from amesh.dsl import FlowDefinition, TaskDefinition, compile_execution_tasks
from amesh.dsl.registry import RESOURCE_CATALOG_VERSION
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports.execution_repository import (
    ExecutionInterventionAction,
    ExecutionInterventionRecord,
    ExecutionLaunchSource,
    ExecutionRepository,
    ExecutionStateConflictError,
    PersistedExecution,
    PersistedFlow,
    PersistedIterationSummary,
    PersistedSubflow,
    PersistedTaskDeferral,
    PersistedTaskRun,
    PersistedTaskRunSummary,
    SubflowLaunchContext,
    SubflowPropagation,
    TaskStateConflictError,
)
from amesh.ports.tenant_repository import TenantQuotaExceeded, TenantUnavailableError
from amesh.workflow.data_contracts import (
    redact_matching_values,
    sensitive_execution_values,
    validate_flow_data_contract,
    validate_flow_inputs,
)
from amesh.workflow.metadata import (
    NamespaceWorkflowMetadata,
    NamespaceWorkflowMetadataUpdate,
    NamespaceWorkflowMetadataView,
    execution_system_labels,
    flow_system_labels,
    namespace_lineage,
    resolve_flow_metadata,
    task_system_labels,
)

from .check_repository import (
    evaluate_execution_terminal_checks,
    record_execution_check_start,
    store_flow_check_definitions,
    synchronize_active_flow_checks,
)
from .metadata_repository import store_flow_triggers, store_task_evidence
from .tenant_context import tenant_transaction
from .trigger_runtime_repository import (
    emit_flow_completion_occurrences,
    synchronize_flow_trigger_runtime,
)

_DATABASE_TIME = text("SELECT clock_timestamp()")

_GET_ADMISSION_REQUEST = text(
    """
    WITH ranked AS (
        SELECT request_id,
               row_number() OVER (
                   ORDER BY
                       priority
                           + floor(extract(epoch FROM (clock_timestamp() - created_at)) / 60)
                           DESC,
                       created_at,
                       request_id
               ) AS queue_position
        FROM admission_requests
        WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
    )
    SELECT requests.*,
           ranked.queue_position,
           greatest(extract(epoch FROM (clock_timestamp() - requests.created_at)), 0)
               AS queue_age_seconds
    FROM admission_requests AS requests
    LEFT JOIN ranked ON ranked.request_id = requests.request_id
    WHERE requests.tenant_id = :tenant_id
      AND requests.resource_type = :resource_type
      AND requests.resource_id = :resource_id
    ORDER BY requests.created_at DESC, requests.request_id DESC
    LIMIT 1
    """
)

_INSERT_ADMISSION_REQUEST = text(
    """
    INSERT INTO admission_requests (
        request_id, tenant_id, resource_type, resource_id, policies, priority,
        outcome, reason, limiting_policy_id, limiting_scope, limiting_bucket,
        active_count, limit_value, replaced_resource_id, admitted_at, finished_at
    ) VALUES (
        :request_id, :tenant_id, :resource_type, :resource_id, CAST(:policies AS jsonb),
        :priority, :outcome, :reason, :limiting_policy_id, :limiting_scope,
        :limiting_bucket, :active_count, :limit_value, :replaced_resource_id,
        CASE WHEN :outcome IN ('ADMITTED', 'REPLACED') THEN clock_timestamp() ELSE NULL END,
        CASE WHEN :outcome IN ('CANCELLED', 'FAILED', 'SKIPPED')
             THEN clock_timestamp() ELSE NULL END
    )
    RETURNING *
    """
)

_INSERT_ADMISSION_RESERVATION = text(
    """
    INSERT INTO admission_reservations (
        reservation_id, tenant_id, request_id, resource_type, resource_id,
        policy_id, scope, bucket, lease_expires_at
    ) VALUES (
        :reservation_id, :tenant_id, :request_id, :resource_type, :resource_id,
        :policy_id, :scope, :bucket,
        clock_timestamp() + make_interval(secs => :lease_seconds)
    )
    ON CONFLICT (tenant_id, request_id, policy_id) DO NOTHING
    """
)

_RELEASE_ADMISSION = text(
    """
    WITH released AS (
        UPDATE admission_reservations
        SET released_at = COALESCE(released_at, clock_timestamp()),
            release_reason = COALESCE(release_reason, :reason)
        WHERE tenant_id = :tenant_id
          AND resource_type = :resource_type
          AND resource_id = :resource_id
          AND released_at IS NULL
        RETURNING request_id
    )
    UPDATE admission_requests
    SET outcome = CASE WHEN outcome IN ('ADMITTED', 'REPLACED') THEN 'RELEASED' ELSE outcome END,
        reason = CASE WHEN outcome IN ('ADMITTED', 'REPLACED') THEN :reason ELSE reason END,
        finished_at = CASE
            WHEN outcome IN ('ADMITTED', 'REPLACED') THEN clock_timestamp()
            ELSE finished_at
        END
    WHERE tenant_id = :tenant_id
      AND resource_type = :resource_type
      AND resource_id = :resource_id
      AND (
          EXISTS (SELECT 1 FROM released)
          OR outcome IN ('ADMITTED', 'REPLACED')
      )
    RETURNING request_id
    """
)

_EXPIRE_ADMISSION_RESERVATIONS = text(
    """
    WITH expired AS (
        UPDATE admission_reservations
        SET released_at = clock_timestamp(), release_reason = 'lease expired'
        WHERE tenant_id = :tenant_id
          AND released_at IS NULL
          AND lease_expires_at <= clock_timestamp()
        RETURNING request_id
    )
    UPDATE admission_requests
    SET outcome = 'EXPIRED', reason = 'admission lease expired', finished_at = clock_timestamp()
    WHERE tenant_id = :tenant_id
      AND request_id IN (SELECT request_id FROM expired)
      AND NOT EXISTS (
          SELECT 1 FROM admission_reservations
          WHERE admission_reservations.request_id = admission_requests.request_id
            AND admission_reservations.released_at IS NULL
            AND admission_reservations.lease_expires_at > clock_timestamp()
      )
    RETURNING request_id
    """
)

_LIST_QUEUED_ADMISSIONS = text(
    """
    SELECT *
    FROM admission_requests
    WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
    ORDER BY
        priority + floor(extract(epoch FROM (clock_timestamp() - created_at)) / 60) DESC,
        created_at,
        request_id
    FOR UPDATE SKIP LOCKED
    LIMIT :limit
    """
)

_ADMISSION_DIAGNOSTICS = text(
    """
    SELECT
        (SELECT count(*) FROM admission_reservations
         WHERE tenant_id = :tenant_id AND released_at IS NULL
           AND lease_expires_at > clock_timestamp()) AS active_reservations,
        (SELECT count(*) FROM admission_requests
         WHERE tenant_id = :tenant_id AND outcome = 'QUEUED') AS queued_requests,
        COALESCE((SELECT greatest(extract(epoch FROM (
            clock_timestamp() - min(created_at)
        )), 0) FROM admission_requests
         WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'), 0) AS oldest_queue_age_seconds,
        COALESCE((SELECT jsonb_object_agg(limiting_policy_id, pressure)
                  FROM (SELECT limiting_policy_id, count(*) AS pressure
                        FROM admission_requests
                        WHERE tenant_id = :tenant_id AND outcome = 'QUEUED'
                          AND limiting_policy_id IS NOT NULL
                        GROUP BY limiting_policy_id) AS grouped), '{}'::jsonb)
            AS pressure_by_policy
    """
)


class _Unset:
    pass


_UNSET = _Unset()

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

_SELECT_FLOW_REVISION = text(
    """
    SELECT id, revision, semantic_hash, canonical_definition, plugin_resolution
    FROM flow_revisions
    WHERE tenant_id = :tenant_id
      AND flow_id = :flow_id
      AND revision = :revision
    """
)

_NEXT_FLOW_REVISION = text(
    """
    SELECT COALESCE(MAX(revision), 0) + 1
    FROM flow_revisions
    WHERE tenant_id = :tenant_id AND flow_id = :flow_id
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

_INSERT_FLOW_AUDIT = text(
    """
    INSERT INTO audit_events (
        event_id, tenant_id, actor_id, action, resource_type, resource_id,
        outcome, reason, source, evidence, occurred_at
    ) VALUES (
        :event_id, :tenant_id, :actor_id, :action, 'flow', :resource_id,
        'SUCCESS', :reason, CAST(:source AS jsonb), CAST(:evidence AS jsonb), clock_timestamp()
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

_INSERT_EXECUTION = text(
    """
    INSERT INTO executions (
        id,
        tenant_id,
        flow_id,
        flow_revision_id,
        namespace_name,
        flow_key,
        state,
        epoch,
        version,
        idempotency_key,
        inputs,
        trigger_context,
        labels,
        created_by,
        updated_by,
        created_at,
        updated_at,
        timeout_at,
        terminal_at
    )
    VALUES (
        :execution_id,
        :tenant_id,
        :flow_id,
        :flow_revision_id,
        :namespace_name,
        :flow_key,
        :state,
        1,
        :version,
        :idempotency_key,
        CAST(:inputs AS jsonb),
        CAST(:trigger_context AS jsonb),
        CAST(:labels AS jsonb),
        :actor_id,
        :actor_id,
        :created_at,
        :created_at,
        :timeout_at,
        :terminal_at
    )
    ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
    RETURNING id
    """
)

_SELECT_EXECUTION_BY_IDEMPOTENCY = text(
    """
    SELECT id
    FROM executions
    WHERE tenant_id = :tenant_id
      AND idempotency_key = :idempotency_key
    """
)

_INSERT_SUBFLOW = text(
    """
    INSERT INTO execution_subflows (
        id,
        tenant_id,
        parent_execution_id,
        parent_task_run_id,
        parent_attempt,
        child_execution_id,
        invocation_key,
        mode,
        depth,
        target_revision,
        propagation,
        output_mapping,
        created_by
    )
    VALUES (
        :relationship_id,
        :tenant_id,
        :parent_execution_id,
        :parent_task_run_id,
        :parent_attempt,
        :child_execution_id,
        :invocation_key,
        :mode,
        :depth,
        :target_revision,
        CAST(:propagation AS jsonb),
        CAST(:output_mapping AS jsonb),
        :actor_id
    )
    ON CONFLICT (tenant_id, invocation_key) DO NOTHING
    RETURNING id
    """
)

_SELECT_SUBFLOW_CHILD_BY_INVOCATION = text(
    """
    SELECT child_execution_id
    FROM execution_subflows
    WHERE tenant_id = :tenant_id
      AND invocation_key = :invocation_key
    """
)

_SUBFLOW_COLUMNS = """
    relationships.id,
    relationships.parent_execution_id,
    relationships.parent_task_run_id,
    relationships.parent_attempt,
    relationships.child_execution_id,
    relationships.invocation_key,
    relationships.mode,
    relationships.depth,
    relationships.target_revision,
    relationships.propagation,
    relationships.output_mapping,
    parent.namespace_name AS parent_namespace,
    parent.flow_key AS parent_flow_id,
    parent_revision.revision AS parent_flow_revision,
    child.namespace_name AS child_namespace,
    child.flow_key AS child_flow_id,
    child.state AS child_state,
    relationships.created_by,
    relationships.created_at
"""

_LIST_CHILD_SUBFLOWS = text(
    f"""
    SELECT {_SUBFLOW_COLUMNS}
    FROM execution_subflows AS relationships
    JOIN executions AS parent ON parent.id = relationships.parent_execution_id
    JOIN flow_revisions AS parent_revision ON parent_revision.id = parent.flow_revision_id
    JOIN executions AS child ON child.id = relationships.child_execution_id
    WHERE relationships.tenant_id = :tenant_id
      AND relationships.parent_execution_id = :execution_id
    ORDER BY relationships.created_at, relationships.id
    """
)

_GET_PARENT_SUBFLOW = text(
    f"""
    SELECT {_SUBFLOW_COLUMNS}
    FROM execution_subflows AS relationships
    JOIN executions AS parent ON parent.id = relationships.parent_execution_id
    JOIN flow_revisions AS parent_revision ON parent_revision.id = parent.flow_revision_id
    JOIN executions AS child ON child.id = relationships.child_execution_id
    WHERE relationships.tenant_id = :tenant_id
      AND relationships.child_execution_id = :execution_id
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
        jsonb_build_object(
            'task_id', inserted.task_path,
            'iteration_key', inserted.iteration_key,
            'lifecycle_phase', inserted.lifecycle_phase,
            'labels', inserted.labels
        )
    FROM inserted
    """
)

_INSERT_TASK_RUN_EVENT = text(
    """
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
        payload
    ) VALUES (
        :tenant_id,
        :task_run_id,
        :execution_id,
        :sequence,
        :event_id,
        :event_type,
        1,
        :idempotency_key,
        :correlation_id,
        NULL,
        :actor_id,
        :reason,
        now(),
        CAST(:payload AS jsonb)
    )
    """
)

_INSERT_TRANSITION_REJECTION = text(
    """
    INSERT INTO transition_rejections (
        tenant_id,
        rejection_id,
        command_id,
        idempotency_key,
        schema_version,
        aggregate_type,
        aggregate_id,
        code,
        current_state,
        current_version,
        current_epoch,
        actor_id,
        reason,
        correlation_id,
        causation_id,
        occurred_at
    ) VALUES (
        :tenant_id,
        :rejection_id,
        :command_id,
        :idempotency_key,
        1,
        :aggregate_type,
        :aggregate_id,
        :code,
        :current_state,
        :current_version,
        :current_epoch,
        :actor_id,
        :reason,
        :correlation_id,
        NULL,
        now()
    )
    ON CONFLICT (tenant_id, aggregate_type, aggregate_id, idempotency_key) DO NOTHING
    """
)

_GET_EXECUTION = text(
    """
    SELECT
        executions.id,
        tenants.slug AS tenant_slug,
        executions.state,
        executions.epoch,
        executions.version,
        executions.namespace_name,
        executions.flow_key,
        flow_revisions.revision AS flow_revision,
        executions.inputs,
        executions.outputs,
        executions.labels,
        executions.trigger_context,
        executions.created_by,
        executions.created_at,
        executions.updated_at,
        executions.timeout_at,
        executions.cancel_deadline_at,
        executions.lifecycle_evidence
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = executions.flow_revision_id
    WHERE executions.id = :execution_id
      AND tenants.slug = :tenant_slug
    """
)

_LIST_EXECUTIONS = text(
    """
    SELECT
        executions.id,
        tenants.slug AS tenant_slug,
        executions.state,
        executions.epoch,
        executions.version,
        executions.namespace_name,
        executions.flow_key,
        flow_revisions.revision AS flow_revision,
        executions.inputs,
        executions.outputs,
        executions.labels,
        executions.trigger_context,
        executions.created_by,
        executions.created_at,
        executions.updated_at,
        executions.timeout_at,
        executions.cancel_deadline_at,
        executions.lifecycle_evidence
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = executions.flow_revision_id
    WHERE tenants.slug = :tenant_slug
    ORDER BY executions.created_at DESC, executions.id
    LIMIT :limit
    """
)

_LIST_RECOVERY_CANDIDATES = text(
    """
    SELECT
        executions.id,
        tenants.slug AS tenant_slug,
        executions.state,
        executions.epoch,
        executions.version,
        executions.namespace_name,
        executions.flow_key,
        flow_revisions.revision AS flow_revision,
        executions.inputs,
        executions.outputs,
        executions.labels,
        executions.trigger_context,
        executions.created_by,
        executions.created_at,
        executions.updated_at,
        executions.timeout_at,
        executions.cancel_deadline_at,
        executions.lifecycle_evidence
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    JOIN flow_revisions ON flow_revisions.id = executions.flow_revision_id
    WHERE tenants.slug = :tenant_slug
      AND (
          NOT EXISTS (
              SELECT 1
              FROM task_runs
              WHERE task_runs.tenant_id = executions.tenant_id
                AND task_runs.execution_id = executions.id
                AND task_runs.state = 'RUNNING'
                AND task_runs.updated_at > :updated_before
          )
      )
      AND (
          executions.state NOT IN ('CANCELLED', 'SUCCESS', 'FAILED', 'WARNING')
          OR EXISTS (
              SELECT 1
              FROM task_runs
              WHERE task_runs.tenant_id = executions.tenant_id
                AND task_runs.execution_id = executions.id
                AND task_runs.lifecycle_phase <> 'MAIN'
                AND task_runs.state IN ('WAITING', 'RUNNING', 'RETRY_DELAY')
          )
      )
    ORDER BY executions.updated_at ASC, executions.id ASC
    LIMIT :limit
    """
)

_GET_FLOW_DEFINITION = text(
    """
    SELECT flow_revisions.canonical_definition, flow_revisions.semantic_hash
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

_LIST_TASK_RUNS = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.iteration_key,
        task_runs.lifecycle_phase,
        task_runs.labels,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result
        ,task_attempts.failure_category
        ,COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND (:include_iterations OR task_runs.iteration_key IS NULL)
    ORDER BY task_runs.created_at, task_runs.task_path, task_runs.iteration_key
    LIMIT :limit OFFSET :offset
    """
)

_SUMMARIZE_TASK_RUNS = text(
    """
    SELECT
        count(*) AS total,
        count(*) FILTER (WHERE task_runs.state = 'WAITING') AS waiting,
        count(*) FILTER (WHERE task_runs.state = 'RUNNING') AS running,
        count(*) FILTER (WHERE task_runs.state = 'RETRY_DELAY') AS retry_delay,
        count(*) FILTER (WHERE task_runs.state = 'SUCCESS') AS succeeded,
        count(*) FILTER (WHERE task_runs.state = 'FAILED') AS failed,
        count(*) FILTER (WHERE task_runs.state = 'CANCELLED') AS cancelled
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND (:include_iterations OR task_runs.iteration_key IS NULL)
    """
)

_LIST_ITERATION_SUMMARIES = text(
    """
    SELECT
        split_part(iteration_key, ':', 1) AS loop_id,
        task_path AS task_id,
        count(DISTINCT iteration_key) AS iteration_count,
        count(*) FILTER (WHERE state = 'WAITING') AS waiting,
        count(*) FILTER (WHERE state IN ('RUNNING', 'RETRY_DELAY')) AS running,
        count(*) FILTER (WHERE state = 'SUCCESS') AS succeeded,
        count(*) FILTER (WHERE state = 'FAILED') AS failed,
        count(*) FILTER (WHERE state = 'CANCELLED') AS cancelled
    FROM task_runs
    JOIN tenants ON tenants.id = task_runs.tenant_id
    WHERE task_runs.execution_id = :execution_id
      AND tenants.slug = :tenant_slug
      AND iteration_key IS NOT NULL
    GROUP BY split_part(iteration_key, ':', 1), task_path
    ORDER BY loop_id, task_id
    """
)

_TASK_ATTEMPT_STARTED_AT = text(
    """
    SELECT task_attempts.started_at
    FROM task_attempts
    JOIN task_runs ON task_runs.id = task_attempts.task_run_id
    WHERE task_attempts.task_run_id = :task_run_id
      AND task_attempts.attempt = :attempt
      AND task_attempts.tenant_id = :tenant_id
    """
)

_LIST_ITERATION_TASK_RUNS = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.iteration_key,
        task_runs.lifecycle_phase,
        task_runs.labels,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result,
        task_attempts.failure_category,
        COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
    FROM task_runs
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.execution_id = :execution_id
      AND task_runs.tenant_id = :tenant_id
      AND task_runs.iteration_key = :iteration_key
    ORDER BY task_runs.created_at, task_runs.task_path
    """
)

_GET_TASK_RUN = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.lifecycle_phase,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        task_runs.retry_at,
        COALESCE(task_attempts.result, task_runs.terminal_result) AS result
        ,task_attempts.failure_category
        ,COALESCE(task_attempts.evidence, task_runs.control_evidence, '{}'::jsonb) AS evidence
    FROM task_runs
    LEFT JOIN task_attempts
      ON task_attempts.task_run_id = task_runs.id
     AND task_attempts.attempt = task_runs.current_attempt
    WHERE task_runs.id = :task_run_id
      AND task_runs.tenant_id = :tenant_id
    """
)

_START_TASK = text(
    """
    WITH updated AS (
        UPDATE task_runs
        SET state = 'RUNNING',
            current_attempt = current_attempt + 1,
            version = version + 1,
            retry_at = NULL,
            updated_at = now()
        WHERE id = :task_run_id
          AND tenant_id = :tenant_id
          AND (
              state = 'WAITING'
              OR (state = 'RETRY_DELAY' AND retry_at <= now())
          )
        RETURNING
            id,
            tenant_id,
            execution_id,
            task_path,
            state,
            current_attempt,
            version,
            retry_at
    ), inserted AS (
        INSERT INTO task_attempts (
            id,
            tenant_id,
            task_run_id,
            attempt,
            state,
            fencing_token,
            started_at
        )
        SELECT
            :attempt_id,
            updated.tenant_id,
            updated.id,
            updated.current_attempt,
            'RUNNING',
            updated.current_attempt,
            now()
        FROM updated
        RETURNING task_run_id
    )
    SELECT
        updated.id,
        updated.execution_id,
        updated.task_path,
        updated.state,
        updated.current_attempt,
        updated.version,
        updated.retry_at,
        NULL::jsonb AS result,
        NULL::text AS failure_category
    FROM updated
    JOIN inserted ON inserted.task_run_id = updated.id
    """
)

_RECORD_TASK_CONTROL = text(
    """
    WITH updated_attempt AS (
        UPDATE task_attempts AS attempts
        SET evidence = CAST(:evidence AS jsonb)
        FROM task_runs
        WHERE attempts.task_run_id = task_runs.id
          AND attempts.tenant_id = task_runs.tenant_id
          AND attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
        RETURNING attempts.task_run_id, attempts.evidence
    ), updated_run AS (
        UPDATE task_runs
        SET version = version + 1,
            control_evidence = updated_attempt.evidence,
            updated_at = clock_timestamp()
        FROM updated_attempt
        WHERE task_runs.id = updated_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            NULL::jsonb AS result,
            NULL::text AS failure_category,
            updated_attempt.evidence
    )
    SELECT * FROM updated_run
    """
)

_SKIP_TASK = text(
    """
    UPDATE task_runs
    SET state = 'SUCCESS',
        version = version + 1,
        terminal_result = CAST(:result AS jsonb),
        control_evidence = CAST(:evidence AS jsonb),
        retry_at = NULL,
        updated_at = clock_timestamp()
    WHERE id = :task_run_id
      AND tenant_id = :tenant_id
      AND state = 'WAITING'
    RETURNING
        id,
        execution_id,
        task_path,
        iteration_key,
        state,
        current_attempt,
        version,
        retry_at,
        terminal_result AS result,
        NULL::text AS failure_category,
        control_evidence AS evidence
    """
)

_FINISH_TASK = text(
    """
    WITH eligible_attempt AS (
        SELECT attempts.id, attempts.queue_id
        FROM task_attempts AS attempts
        WHERE attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND (
              (
                  CAST(:worker_id AS uuid) IS NULL
                  AND CAST(:fencing_token AS bigint) IS NULL
                  AND attempts.worker_id IS NULL
                  AND attempts.queue_id IS NULL
              )
              OR (
                  attempts.worker_id = CAST(:worker_id AS uuid)
                  AND attempts.fencing_token = CAST(:fencing_token AS bigint)
                  AND attempts.lease_expires_at > clock_timestamp()
                  AND EXISTS (
                      SELECT 1
                      FROM durable_work_queue AS queue
                      WHERE queue.id = attempts.queue_id
                        AND queue.tenant_id = attempts.tenant_id
                        AND queue.state = 'CLAIMED'
                        AND queue.claimed_by = :worker_consumer_id
                        AND queue.fencing_token = CAST(:fencing_token AS bigint)
                        AND queue.lease_expires_at > clock_timestamp()
                  )
              )
          )
        FOR UPDATE
    ), finished_attempt AS (
        UPDATE task_attempts AS attempts
        SET state = :state,
            result = CAST(:result AS jsonb),
            evidence = CAST(:evidence AS jsonb),
            failure_category = CAST(:failure_category AS text),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING
            attempts.task_run_id,
            attempts.result,
            attempts.failure_category,
            attempts.evidence,
            eligible_attempt.queue_id
    ), acknowledged_queue AS (
        DELETE FROM durable_work_queue AS queue
        USING finished_attempt
        WHERE finished_attempt.queue_id IS NOT NULL
          AND queue.id = finished_attempt.queue_id
          AND queue.tenant_id = :tenant_id
          AND queue.state = 'CLAIMED'
          AND queue.claimed_by = :worker_consumer_id
          AND queue.fencing_token = CAST(:fencing_token AS bigint)
        RETURNING queue.id
    ), finished_run AS (
        UPDATE task_runs
        SET state = :state,
            version = version + 1,
            retry_at = NULL,
            updated_at = now()
        FROM finished_attempt
        LEFT JOIN acknowledged_queue ON acknowledged_queue.id = finished_attempt.queue_id
        WHERE task_runs.id = finished_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
          AND (
              finished_attempt.queue_id IS NULL
              OR acknowledged_queue.id IS NOT NULL
          )
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            finished_attempt.result,
            finished_attempt.failure_category
            ,finished_attempt.evidence
    )
    SELECT * FROM finished_run
    """
)

_RETRY_TASK = text(
    """
    WITH eligible_attempt AS (
        SELECT attempts.id, attempts.queue_id
        FROM task_attempts AS attempts
        WHERE attempts.task_run_id = :task_run_id
          AND attempts.tenant_id = :tenant_id
          AND attempts.attempt = :attempt
          AND attempts.state = 'RUNNING'
          AND (
              (
                  CAST(:worker_id AS uuid) IS NULL
                  AND CAST(:fencing_token AS bigint) IS NULL
                  AND attempts.worker_id IS NULL
                  AND attempts.queue_id IS NULL
              )
              OR (
                  attempts.worker_id = CAST(:worker_id AS uuid)
                  AND attempts.fencing_token = CAST(:fencing_token AS bigint)
                  AND attempts.lease_expires_at > clock_timestamp()
                  AND EXISTS (
                      SELECT 1
                      FROM durable_work_queue AS queue
                      WHERE queue.id = attempts.queue_id
                        AND queue.tenant_id = attempts.tenant_id
                        AND queue.state = 'CLAIMED'
                        AND queue.claimed_by = :worker_consumer_id
                        AND queue.fencing_token = CAST(:fencing_token AS bigint)
                        AND queue.lease_expires_at > clock_timestamp()
                  )
              )
          )
        FOR UPDATE
    ), failed_attempt AS (
        UPDATE task_attempts AS attempts
        SET state = 'FAILED',
            result = CAST(:result AS jsonb),
            failure_category = CAST(:failure_category AS text),
            finished_at = clock_timestamp(),
            lease_expires_at = NULL,
            queue_id = NULL
        FROM eligible_attempt
        WHERE attempts.id = eligible_attempt.id
        RETURNING
            attempts.task_run_id,
            attempts.result,
            attempts.failure_category,
            eligible_attempt.queue_id
    ), acknowledged_queue AS (
        DELETE FROM durable_work_queue AS queue
        USING failed_attempt
        WHERE failed_attempt.queue_id IS NOT NULL
          AND queue.id = failed_attempt.queue_id
          AND queue.tenant_id = :tenant_id
          AND queue.state = 'CLAIMED'
          AND queue.claimed_by = :worker_consumer_id
          AND queue.fencing_token = CAST(:fencing_token AS bigint)
        RETURNING queue.id
    ), retrying_run AS (
        UPDATE task_runs
        SET state = 'RETRY_DELAY',
            version = version + 1,
            retry_at = :retry_at,
            updated_at = now()
        FROM failed_attempt
        LEFT JOIN acknowledged_queue ON acknowledged_queue.id = failed_attempt.queue_id
        WHERE task_runs.id = failed_attempt.task_run_id
          AND task_runs.tenant_id = :tenant_id
          AND task_runs.current_attempt = :attempt
          AND task_runs.state = 'RUNNING'
          AND (
              failed_attempt.queue_id IS NULL
              OR acknowledged_queue.id IS NOT NULL
          )
        RETURNING
            task_runs.id,
            task_runs.execution_id,
            task_runs.task_path,
            task_runs.state,
            task_runs.current_attempt,
            task_runs.version,
            task_runs.retry_at,
            failed_attempt.result,
            failed_attempt.failure_category
    )
    SELECT * FROM retrying_run
    """
)

_FINISH_EXECUTION = text(
    """
    WITH finished AS (
        UPDATE executions
        SET state = :state,
            outputs = CAST(:outputs AS jsonb),
            version = version + 1,
            updated_at = now(),
            terminal_at = now()
        WHERE id = :execution_id
          AND tenant_id = :tenant_id
          AND state = 'RUNNING'
          AND epoch = :expected_epoch
        RETURNING
            id,
            tenant_id,
            state,
            epoch,
            version,
            flow_revision_id,
            namespace_name,
            flow_key,
            inputs,
            outputs,
            labels,
            trigger_context,
            created_by,
            created_at,
            updated_at,
            timeout_at,
            cancel_deadline_at,
            lifecycle_evidence
    ), event AS (
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
            payload
        )
        SELECT
            finished.tenant_id,
            finished.id,
            finished.version,
            :event_id,
            :event_type,
            2,
            :idempotency_key,
            :correlation_id,
            NULL,
            'mvp-executor',
            :reason,
            now(),
            CAST(:payload AS jsonb)
        FROM finished
        RETURNING execution_id
    )
    SELECT
        finished.id,
        tenants.slug AS tenant_slug,
        finished.state,
        finished.epoch,
        finished.version,
        finished.flow_revision_id,
        flow_revisions.revision AS flow_revision,
        finished.namespace_name,
        finished.flow_key,
        finished.inputs,
        finished.outputs,
        finished.labels,
        finished.trigger_context,
        finished.created_by,
        finished.created_at,
        finished.updated_at,
        finished.timeout_at,
        finished.cancel_deadline_at,
        finished.lifecycle_evidence
    FROM finished
    JOIN event ON event.execution_id = finished.id
    JOIN tenants ON tenants.id = finished.tenant_id
    JOIN flow_revisions ON flow_revisions.id = finished.flow_revision_id
    """
)

_RECORD_EXECUTION_LIFECYCLE = text(
    """
    WITH updated AS (
        UPDATE executions
        SET lifecycle_evidence = CAST(:evidence AS jsonb),
            version = version + 1,
            updated_at = clock_timestamp()
        WHERE id = :execution_id
          AND tenant_id = :tenant_id
          AND epoch = :expected_epoch
        RETURNING id, tenant_id, version, state
    )
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
        payload
    )
    SELECT
        updated.tenant_id,
        updated.id,
        updated.version,
        :event_id,
        'ExecutionLifecycleRecorded',
        2,
        :idempotency_key,
        :correlation_id,
        NULL,
        'system:executor',
        'execution lifecycle evidence recorded',
        clock_timestamp(),
        CAST(:evidence AS jsonb)
    FROM updated
    RETURNING execution_id
    """
)

_LOCK_EXECUTION_CONTROL = text(
    """
    SELECT
        executions.*,
        tenants.slug AS tenant_slug,
        clock_timestamp() AS database_now
    FROM executions
    JOIN tenants ON tenants.id = executions.tenant_id
    WHERE executions.id = :execution_id
      AND executions.tenant_id = :tenant_id
    FOR UPDATE OF executions
    """
)

_LOCK_TASK_RUNS_CONTROL = text(
    """
    SELECT
        task_runs.id,
        task_runs.execution_id,
        task_runs.task_path,
        task_runs.lifecycle_phase,
        task_runs.state,
        task_runs.current_attempt,
        task_runs.version,
        attempts.id AS attempt_id,
        attempts.state AS attempt_state,
        attempts.queue_id,
        attempts.cancellation_acknowledged
    FROM task_runs
    LEFT JOIN task_attempts AS attempts
      ON attempts.task_run_id = task_runs.id
     AND attempts.attempt = task_runs.current_attempt
    WHERE task_runs.tenant_id = :tenant_id
      AND task_runs.execution_id = :execution_id
    ORDER BY task_runs.created_at, task_runs.task_path
    FOR UPDATE OF task_runs
    """
)

_UPDATE_EXECUTION_CONTROL = text(
    """
    UPDATE executions
    SET state = :state,
        epoch = :epoch,
        version = :version,
        lifecycle_evidence = CASE
            WHEN :state = 'RUNNING' AND state IN ('FAILED', 'CANCELLED', 'WARNING')
                THEN '{}'::jsonb
            ELSE lifecycle_evidence
        END,
        timeout_at = :timeout_at,
        cancel_deadline_at = :cancel_deadline_at,
        terminal_at = :terminal_at,
        updated_by = :actor_id,
        updated_at = clock_timestamp()
    WHERE id = :execution_id
      AND tenant_id = :tenant_id
    RETURNING id
    """
)

_UPDATE_TASK_CONTROL = text(
    """
    UPDATE task_runs
    SET state = :state,
        version = version + 1,
        retry_at = NULL,
        terminal_result = CASE WHEN :state = 'WAITING' THEN NULL ELSE terminal_result END,
        control_evidence = CASE
            WHEN :state = 'WAITING' THEN '{}'::jsonb
            ELSE control_evidence
        END,
        updated_at = clock_timestamp()
    WHERE id = :task_run_id
      AND tenant_id = :tenant_id
      AND state = :expected_state
    RETURNING id, execution_id, task_path, state, current_attempt, version, retry_at
    """
)

_INVALIDATE_ATTEMPT = text(
    """
    UPDATE task_attempts
    SET state = :state,
        fencing_token = fencing_token + 1,
        lease_expires_at = NULL,
        queue_id = NULL,
        finished_at = clock_timestamp(),
        failure_category = :failure_category,
        result = CAST(:result AS jsonb)
    WHERE id = :attempt_id
      AND tenant_id = :tenant_id
      AND state = 'RUNNING'
    RETURNING id
    """
)

_REQUEST_ATTEMPT_CANCELLATION = text(
    """
    UPDATE task_attempts
    SET cancellation_requested_at = clock_timestamp()
    WHERE id = :attempt_id
      AND tenant_id = :tenant_id
      AND state = 'RUNNING'
    RETURNING id
    """
)

_DELETE_TASK_QUEUE = text(
    """
    DELETE FROM durable_work_queue
    WHERE id = :queue_id
      AND tenant_id = :tenant_id
    """
)

_INSERT_EXECUTION_INTERVENTION_EVENT = text(
    """
    INSERT INTO execution_events (
        tenant_id, execution_id, sequence, event_id, event_type, schema_version,
        idempotency_key, correlation_id, causation_id, actor_id, reason, occurred_at, payload
    ) VALUES (
        :tenant_id, :execution_id, :sequence, :event_id, :event_type, 2,
        :idempotency_key, :correlation_id, NULL, :actor_id, :reason,
        clock_timestamp(), CAST(:payload AS jsonb)
    )
    """
)

_LIST_EXECUTION_INTERVENTIONS = text(
    """
    SELECT sequence, event_type, actor_id, reason, occurred_at, payload
    FROM execution_events
    WHERE tenant_id = :tenant_id
      AND execution_id = :execution_id
      AND payload ? 'intervention'
    ORDER BY sequence
    """
)


class PostgresExecutionRepository(ExecutionRepository):
    """Persists MVP executions, task runs, attempts and terminal events."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        plugin_resolution_provider: Callable[[FlowDefinition], dict[str, object]] | None = None,
        plugin_policy_enforcer: Callable[
            [FlowDefinition, str, PluginPolicyStage, str], Awaitable[None]
        ]
        | None = None,
        admission_policy_enforcer: Callable[
            [
                FlowDefinition,
                str,
                PolicyStage,
                str,
                dict[str, object] | None,
                TaskDefinition | None,
                UUID | None,
                UUID | None,
            ],
            Awaitable[PolicyDecision],
        ]
        | None = None,
    ) -> None:
        self._engine = engine
        self._plugin_resolution_provider = plugin_resolution_provider
        self._plugin_policy_enforcer = plugin_policy_enforcer
        self._admission_policy_enforcer = admission_policy_enforcer

    @asynccontextmanager
    async def execution_guard(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> AsyncIterator[bool]:
        """Hold one crash-safe owner guard while an execution is being advanced."""

        lock_key = f"execution:{tenant_id}:{execution_id}"
        async with self._engine.connect() as connection:
            acquired = bool(
                await connection.scalar(
                    text("SELECT pg_try_advisory_lock(hashtextextended(:lock_key, 0))"),
                    {"lock_key": lock_key},
                )
            )
            try:
                yield acquired
            finally:
                if acquired:
                    await connection.execute(
                        text("SELECT pg_advisory_unlock(hashtextextended(:lock_key, 0))"),
                        {"lock_key": lock_key},
                    )

    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        expected_etag: str | None = None,
        actor_id: str = "system:flow-manager",
        revision_source: FlowRevisionSource | None = None,
    ) -> PersistedFlow:
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, scoped_tenant_id):
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
                    raise ResourceVersionConflict(
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
                    "labels": json.dumps(
                        {**stored_flow.labels, **flow_system_labels(stored_flow)}
                    ),
                    "annotations": json.dumps(stored_flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": expected_version,
                },
            )
            if activation.scalar_one_or_none() is None:
                raise ResourceVersionConflict(
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

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
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
            raise LookupError(f"flow {namespace}.{flow_id} does not exist")
        definition = row["canonical_definition"]
        flow = FlowDefinition.model_validate(definition)
        flow._persisted_canonical_definition = json.dumps(
            definition,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        flow._persisted_semantic_hash = str(row["semantic_hash"])
        return flow

    async def list_flows(self, *, tenant_id: str) -> list[PersistedFlow]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, scoped_tenant_id):
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
                    "plugin_defaults": json.dumps(
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
                raise ResourceVersionConflict(
                    f"namespace {namespace!r} workflow metadata version is stale"
                )
            return _to_namespace_workflow_metadata(row, tenant_id, namespace)

    async def get_namespace_workflow_metadata(
        self,
        namespace: str,
        *,
        tenant_id: str,
    ) -> NamespaceWorkflowMetadataView:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
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
                    raise LookupError(
                        f"flow {namespace}.{flow_id} revision {revision} does not exist"
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
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
                raise LookupError(f"flow {namespace}.{flow_id} revision {revision} does not exist")
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

    async def create_execution(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        inputs: dict[str, object],
        trigger: dict[str, object] | None = None,
        launch_source: ExecutionLaunchSource = ExecutionLaunchSource.MANUAL,
        idempotency_key: str | None = None,
        actor_id: str = "system:executor",
        labels: dict[str, str] | None = None,
        subflow: SubflowLaunchContext | None = None,
        priority: int | None = None,
    ) -> PersistedExecution:
        if subflow is not None and flow.revision != subflow.target_revision:
            raise ValueError("subflow target revision does not match the loaded flow revision")
        policy_decision: PolicyDecision | None = None
        if self._admission_policy_enforcer is not None:
            policy_decision = await self._admission_policy_enforcer(
                flow,
                tenant_id,
                PolicyStage.LAUNCH,
                actor_id,
                inputs,
                None,
                None,
                None,
            )
            if policy_decision.mutated_input is None:
                raise RuntimeError("launch policy decision omitted its mutated input")
            inputs = dict(policy_decision.mutated_input.resource.inputs)
        inputs = validate_flow_inputs(flow, inputs)
        if self._plugin_policy_enforcer is not None:
            await self._plugin_policy_enforcer(
                flow,
                tenant_id,
                PluginPolicyStage.EXECUTION,
                actor_id,
            )
        execution_id = new_runtime_id()

        async with tenant_transaction(self._engine, tenant_id) as (connection, scoped_tenant_id):
            policy = await _load_tenant_policy(connection)
            _require_allowed_plugins(policy, flow)
            if not policy.feature_enabled("executions"):
                raise TenantQuotaExceeded("tenant execution feature is disabled")
            queued_count = int(
                await connection.scalar(
                    text("SELECT count(*) FROM executions WHERE state = 'QUEUED'")
                )
                or 0
            )
            if queued_count >= policy.max_queued_executions:
                raise TenantQuotaExceeded("tenant queued execution quota exceeded")
            tenant_uuid, namespace_id = await self._ensure_namespace(
                connection,
                tenant_id,
                flow.namespace,
                actor_id,
            )
            if tenant_uuid != scoped_tenant_id:
                raise TenantUnavailableError("tenant context changed during execution creation")
            flow_id = await self._ensure_flow(
                connection,
                tenant_uuid,
                namespace_id,
                flow.id,
                actor_id,
            )
            flow_resource = await self._flow_resource_row(
                connection,
                tenant_uuid,
                flow.namespace,
                flow.id,
            )
            if flow_resource["active_revision"] is not None and (
                flow_resource["status"] != FlowLifecycle.ACTIVE.value
            ):
                raise ValueError(
                    f"flow {flow.namespace}.{flow.id} lifecycle "
                    f"{flow_resource['status']} does not permit execution"
                )
            flow_revision_id, stored_flow, _created = await self._ensure_flow_revision(
                connection,
                tenant_uuid,
                flow_id,
                flow,
                actor_id,
            )
            revision_result = await connection.execute(
                _SELECT_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_id,
                    "revision": stored_flow.revision,
                },
            )
            exact_revision = revision_result.mappings().one()
            if stored_flow.disabled:
                raise ValueError(
                    f"flow {flow.namespace}.{flow.id} is disabled and cannot be executed"
                )
            if subflow is None and flow_resource["active_revision"] is None:
                await connection.execute(
                    _ACTIVATE_FLOW_REVISION,
                    {
                        "tenant_id": tenant_uuid,
                        "flow_id": flow_id,
                        "revision": stored_flow.revision,
                        "status": (FlowLifecycle.ACTIVE.value),
                        "labels": json.dumps(
                            {**stored_flow.labels, **flow_system_labels(stored_flow)}
                        ),
                        "annotations": json.dumps(stored_flow.annotations),
                        "actor_id": actor_id,
                        "expected_version": None,
                    },
                )
                await synchronize_flow_trigger_runtime(
                    connection,
                    tenant_uuid,
                    flow_id,
                    active_revision=stored_flow.revision,
                    flow_disabled=stored_flow.disabled,
                )
                await synchronize_active_flow_checks(
                    connection,
                    tenant_uuid,
                    flow_id,
                    active_revision=stored_flow.revision,
                    flow_disabled=stored_flow.disabled,
                )
            flow = stored_flow
            launch_context = dict(
                redact_matching_values(
                    dict(trigger or {}),
                    sensitive_execution_values(flow, inputs, {}),
                )
            )
            policy_metadata = (
                policy_decision_metadata(policy_decision) if policy_decision is not None else None
            )
            if policy_decision is not None:
                launch_context["_ameshPolicyDecision"] = policy_metadata
            plugin_resolution = exact_revision["plugin_resolution"]
            if not isinstance(plugin_resolution, Mapping):
                raise TypeError("persisted flow revision has an invalid plugin resolution")
            launch_context["_ameshDeterminism"] = build_determinism_envelope(
                flow,
                semantic_hash=str(exact_revision["semantic_hash"]),
                plugin_set=plugin_resolution,
                policy_pins=admission_policy_pins(policy_metadata),
            ).model_dump(mode="json", by_alias=True)
            launch_context["source"] = launch_source.value
            merged_labels = {
                **flow.labels,
                **(labels or {}),
                **execution_system_labels(
                    flow,
                    execution_id,
                    source=launch_source.value,
                ),
            }
            expression_context = ExpressionContext(
                flow={
                    "id": flow.id,
                    "namespace": flow.namespace,
                    "revision": flow.revision,
                },
                execution={"id": str(execution_id), "tenantId": tenant_id},
                trigger=launch_context,
                inputs=inputs,
                variables=flow.variables,
                labels=merged_labels,
                namespace={"id": flow.namespace},
            )
            expression_engine = NativeExpressionEngine()
            resolved_policies = (
                ResolvedAdmissionPolicy(
                    policy_id="tenant.maxConcurrentExecutions",
                    scope=AdmissionScope.TENANT,
                    bucket=f"EXECUTION:TENANT:{tenant_id}",
                    limit=policy.max_concurrent_executions,
                    behavior=AdmissionBehavior.FAIL,
                    lease_seconds=max(
                        int(flow.timeout_seconds or 3600),
                        1,
                    ),
                ),
                *resolve_admission_policies(
                    flow.concurrency,
                    resource_type=AdmissionResourceType.EXECUTION,
                    tenant_id=tenant_id,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    render_key=lambda value: expression_engine.render_value(
                        value,
                        expression_context,
                    ),
                ),
            )
            admission = await self._request_admission_tx(
                connection,
                tenant_uuid,
                AdmissionResourceType.EXECUTION,
                execution_id,
                resolved_policies,
                flow.priority if priority is None else priority,
            )
            if (
                admission.outcome is AdmissionOutcome.FAILED
                and admission.limiting_policy_id == "tenant.maxConcurrentExecutions"
            ):
                raise TenantQuotaExceeded("tenant concurrent execution quota exceeded")
            initial_state = {
                AdmissionOutcome.ADMITTED: ExecutionState.RUNNING,
                AdmissionOutcome.REPLACED: ExecutionState.RUNNING,
                AdmissionOutcome.QUEUED: ExecutionState.QUEUED,
                AdmissionOutcome.CANCELLED: ExecutionState.CANCELLED,
                AdmissionOutcome.FAILED: ExecutionState.FAILED,
                AdmissionOutcome.SKIPPED: ExecutionState.SUCCESS,
            }[admission.outcome]
            initial_version = 3 if initial_state is ExecutionState.RUNNING else 2
            if initial_state in {
                ExecutionState.CANCELLED,
                ExecutionState.FAILED,
                ExecutionState.SUCCESS,
            }:
                initial_version = 4
            created_at = await connection.scalar(_DATABASE_TIME)
            if not isinstance(created_at, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            insert_result = await connection.execute(
                _INSERT_EXECUTION,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_id,
                    "flow_revision_id": flow_revision_id,
                    "namespace_name": flow.namespace,
                    "flow_key": flow.id,
                    "state": initial_state.value,
                    "version": initial_version,
                    "idempotency_key": idempotency_key,
                    "inputs": json.dumps(inputs),
                    "trigger_context": json.dumps(launch_context),
                    "labels": json.dumps(merged_labels),
                    "actor_id": actor_id,
                    "created_at": created_at,
                    "timeout_at": (
                        created_at + timedelta(seconds=flow.timeout_seconds)
                        if flow.timeout_seconds is not None
                        else None
                    ),
                    "terminal_at": (
                        created_at
                        if initial_state
                        in {
                            ExecutionState.CANCELLED,
                            ExecutionState.FAILED,
                            ExecutionState.SUCCESS,
                        }
                        else None
                    ),
                },
            )
            inserted_execution_id = insert_result.scalar_one_or_none()
            if inserted_execution_id is None:
                if idempotency_key is None:
                    raise RuntimeError("execution insert did not return an identity")
                existing_result = await connection.execute(
                    _SELECT_EXECUTION_BY_IDEMPOTENCY,
                    {"tenant_id": tenant_uuid, "idempotency_key": idempotency_key},
                )
                execution_id = UUID(str(existing_result.scalar_one()))
                await self._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.EXECUTION,
                    admission.resource_id,
                    "duplicate idempotency key",
                )
            else:
                execution_id = UUID(str(inserted_execution_id))
                await self._insert_initial_events(
                    connection,
                    tenant_uuid,
                    execution_id,
                    created_at,
                    actor_id,
                    admission.outcome,
                    admission.reason,
                )
                task_rows: list[dict[str, object]] = []
                execution_plan = compile_execution_tasks(flow)
                for node in (
                    execution_plan
                    if initial_state
                    not in {
                        ExecutionState.CANCELLED,
                        ExecutionState.FAILED,
                        ExecutionState.SUCCESS,
                    }
                    else tuple(
                        item
                        for item in execution_plan
                        if item.lifecycle_phase.value != TaskRunLifecyclePhase.MAIN.value
                    )
                ):
                    task_event_id = new_runtime_id()
                    task_rows.append(
                        {
                            "task_run_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "execution_id": execution_id,
                            "task_id": node.task.id,
                            "iteration_key": None,
                            "lifecycle_phase": node.lifecycle_phase.value,
                            "labels": json.dumps(
                                task_system_labels(
                                    {**merged_labels, **node.task.run_labels},
                                    task_id=node.task.id,
                                    lifecycle_phase=node.lifecycle_phase.value,
                                )
                            ),
                            "event_id": task_event_id,
                            "idempotency_key": str(task_event_id),
                            "correlation_id": new_runtime_id(),
                            "actor_id": actor_id,
                            "occurred_at": created_at,
                        }
                    )
                if task_rows:
                    await connection.execute(
                        _INSERT_TASK_RUN,
                        task_rows,
                    )
                await record_execution_check_start(
                    connection,
                    tenant_uuid,
                    flow_revision_id=flow_revision_id,
                    execution_id=execution_id,
                    execution_state=initial_state.value,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    flow_revision=flow.revision,
                    created_at=created_at,
                    trigger=launch_context,
                    labels=merged_labels,
                )
                if initial_state in {
                    ExecutionState.CANCELLED,
                    ExecutionState.FAILED,
                    ExecutionState.SUCCESS,
                }:
                    await evaluate_execution_terminal_checks(
                        connection,
                        tenant_uuid,
                        flow_revision_id=flow_revision_id,
                        execution_id=execution_id,
                        execution_state=initial_state.value,
                        namespace=flow.namespace,
                        flow_id=flow.id,
                        flow_revision=flow.revision,
                        created_at=created_at,
                        terminal_at=created_at,
                        inputs=inputs,
                        trigger=launch_context,
                        labels=merged_labels,
                    )

            if subflow is not None:
                relationship_id = await connection.scalar(
                    _INSERT_SUBFLOW,
                    {
                        "relationship_id": new_runtime_id(),
                        "tenant_id": tenant_uuid,
                        "parent_execution_id": subflow.parent_execution_id,
                        "parent_task_run_id": subflow.parent_task_run_id,
                        "parent_attempt": subflow.parent_attempt,
                        "child_execution_id": execution_id,
                        "invocation_key": subflow.invocation_key,
                        "mode": subflow.mode.value,
                        "depth": subflow.depth,
                        "target_revision": subflow.target_revision,
                        "propagation": subflow.propagation.model_dump_json(),
                        "output_mapping": json.dumps(subflow.output_mapping),
                        "actor_id": actor_id,
                    },
                )
                if relationship_id is None:
                    existing_child = await connection.scalar(
                        _SELECT_SUBFLOW_CHILD_BY_INVOCATION,
                        {
                            "tenant_id": tenant_uuid,
                            "invocation_key": subflow.invocation_key,
                        },
                    )
                    if existing_child != execution_id:
                        raise ExecutionStateConflictError(
                            "subflow invocation identity resolves to another child execution"
                        )

        return await self.get_execution(execution_id, tenant_id=tenant_id)

    @property
    def has_admission_policy_enforcer(self) -> bool:
        return self._admission_policy_enforcer is not None

    async def enforce_admission_policy(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PolicyStage,
        actor_id: str,
        inputs: dict[str, object] | None = None,
        task: TaskDefinition | None = None,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        if self._admission_policy_enforcer is None:
            raise RuntimeError("admission policy enforcer is not configured")
        return await self._admission_policy_enforcer(
            flow,
            tenant_id,
            stage,
            actor_id,
            inputs,
            task,
            execution_id,
            task_run_id,
        )

    async def request_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        *,
        tenant_id: str,
        priority: int = 0,
    ) -> AdmissionDecision:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            decision = await self._request_admission_tx(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
                policies,
                priority,
            )
            if resource_type is AdmissionResourceType.TASK and decision.outcome in {
                AdmissionOutcome.CANCELLED,
                AdmissionOutcome.FAILED,
                AdmissionOutcome.SKIPPED,
            }:
                await self._terminate_denied_task(
                    connection,
                    tenant_uuid,
                    resource_id,
                    decision,
                )
            return decision

    async def get_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
    ) -> AdmissionDecision | None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._get_admission_row(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
            )
        return _to_admission_decision(row) if row is not None else None

    async def release_admission(
        self,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        *,
        tenant_id: str,
        reason: str = "resource completed",
    ) -> bool:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            released = await self._release_admission_tx(
                connection,
                tenant_uuid,
                resource_type,
                resource_id,
                reason,
            )
            await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
        return released

    async def reconcile_admission(self, *, tenant_id: str, limit: int = 100) -> int:
        if limit < 1 or limit > 10_000:
            raise ValueError("admission reconciliation limit must be between 1 and 10000")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            return await self._reconcile_admission_tx(connection, tenant_uuid, limit=limit)

    async def admission_diagnostics(self, *, tenant_id: str) -> AdmissionDiagnostics:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                _EXPIRE_ADMISSION_RESERVATIONS,
                {"tenant_id": tenant_uuid},
            )
            row = (
                (
                    await connection.execute(
                        _ADMISSION_DIAGNOSTICS,
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one()
            )
        return AdmissionDiagnostics(
            active_reservations=int(row["active_reservations"]),
            queued_requests=int(row["queued_requests"]),
            oldest_queue_age_seconds=float(row["oldest_queue_age_seconds"]),
            pressure_by_policy={
                str(key): int(value) for key, value in row["pressure_by_policy"].items()
            },
        )

    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> PersistedExecution:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _GET_EXECUTION,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise LookupError(f"execution {execution_id} does not exist")
        return _to_execution(row)

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_EXECUTIONS,
                {"tenant_slug": tenant_id, "limit": limit},
            )
            rows = result.mappings().all()
        return [_to_execution(row) for row in rows]

    async def list_recovery_candidates(
        self,
        *,
        tenant_id: str,
        updated_before: datetime,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        if limit < 1:
            raise ValueError("recovery candidate limit must be at least 1")
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_RECOVERY_CANDIDATES,
                {
                    "tenant_slug": tenant_id,
                    "updated_before": updated_before,
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
        return [_to_execution(row) for row in rows]

    async def list_subflows(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedSubflow]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        _LIST_CHILD_SUBFLOWS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_subflow(row) for row in rows]

    async def get_parent_subflow(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedSubflow | None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _GET_PARENT_SUBFLOW,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        return _to_subflow(row) if row is not None else None

    async def list_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[PersistedTaskRun]:
        if limit is not None and limit < 1:
            raise ValueError("task run limit must be positive")
        if offset < 0:
            raise ValueError("task run offset cannot be negative")
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_TASK_RUNS,
                {
                    "execution_id": execution_id,
                    "tenant_slug": tenant_id,
                    "include_iterations": include_iterations,
                    "limit": limit,
                    "offset": offset,
                },
            )
            rows = result.mappings().all()
        return [_to_task_run(row) for row in rows]

    async def summarize_task_runs(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        include_iterations: bool = True,
    ) -> PersistedTaskRunSummary:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _SUMMARIZE_TASK_RUNS,
                        {
                            "execution_id": execution_id,
                            "tenant_slug": tenant_id,
                            "include_iterations": include_iterations,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return PersistedTaskRunSummary.model_validate(row)

    async def list_iteration_summaries(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedIterationSummary]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _LIST_ITERATION_SUMMARIES,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
            rows = result.mappings().all()
        return [PersistedIterationSummary.model_validate(row) for row in rows]

    async def ensure_iteration_task_runs(
        self,
        execution_id: UUID,
        iteration_key: str,
        task_ids: tuple[str, ...],
        *,
        tenant_id: str,
    ) -> list[PersistedTaskRun]:
        if not iteration_key or len(iteration_key) > 512:
            raise ValueError("iteration key must contain between 1 and 512 characters")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            occurred_at = await connection.scalar(_DATABASE_TIME)
            if not isinstance(occurred_at, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            execution_labels = await connection.scalar(
                text(
                    "SELECT labels FROM executions "
                    "WHERE tenant_id = :tenant_id AND id = :execution_id"
                ),
                {"tenant_id": tenant_uuid, "execution_id": execution_id},
            )
            if not isinstance(execution_labels, dict):
                raise LookupError(f"execution {execution_id} does not exist")
            rows: list[dict[str, object]] = []
            for task_id in task_ids:
                event_id = new_runtime_id()
                rows.append(
                    {
                        "task_run_id": new_runtime_id(),
                        "tenant_id": tenant_uuid,
                        "execution_id": execution_id,
                        "task_id": task_id,
                        "iteration_key": iteration_key,
                        "lifecycle_phase": TaskRunLifecyclePhase.MAIN.value,
                        "labels": json.dumps(
                            task_system_labels(
                                execution_labels,
                                task_id=task_id,
                                lifecycle_phase=TaskRunLifecyclePhase.MAIN.value,
                            )
                        ),
                        "event_id": event_id,
                        "idempotency_key": str(event_id),
                        "correlation_id": new_runtime_id(),
                        "actor_id": "system:loop",
                        "occurred_at": occurred_at,
                    }
                )
            if rows:
                await connection.execute(_INSERT_TASK_RUN, rows)
            result = await connection.execute(
                _LIST_ITERATION_TASK_RUNS,
                {
                    "tenant_id": tenant_uuid,
                    "execution_id": execution_id,
                    "iteration_key": iteration_key,
                },
            )
            task_runs = result.mappings().all()
        return [_to_task_run(task_run) for task_run in task_runs]

    async def task_attempt_started_at(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
    ) -> datetime:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            started_at = await connection.scalar(
                _TASK_ATTEMPT_STARTED_AT,
                {
                    "task_run_id": task_run_id,
                    "attempt": attempt,
                    "tenant_id": tenant_uuid,
                },
            )
        if not isinstance(started_at, datetime):
            raise LookupError(f"task run {task_run_id} attempt {attempt} does not exist")
        return started_at

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _START_TASK,
                {
                    "task_run_id": task_run_id,
                    "attempt_id": new_runtime_id(),
                    "tenant_id": tenant_uuid,
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.STARTED,
                    correlation_id,
                    payload={
                        "dispatch": dispatch,
                        "priority": priority,
                        "workerGroup": worker_group,
                    },
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                conflict_message = f"task run {task_run_id} is not waiting"
                if row is not None:
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        command_id,
                        "task_run",
                        task_run_id,
                        TransitionRejectionCode.ILLEGAL_TRANSITION,
                        str(row["state"]),
                        int(row["version"]),
                        None,
                        conflict_message,
                        correlation_id,
                    )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _RECORD_TASK_CONTROL,
                        {
                            "task_run_id": task_run_id,
                            "tenant_id": tenant_uuid,
                            "attempt": attempt,
                            "evidence": json.dumps(evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.CONTROL_RECORDED,
                    correlation_id,
                    payload={"attempt": attempt, "evidence": evidence},
                    actor_id="system:flow-control",
                )
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    row is not None
                    and TaskRunState(row["state"]) is TaskRunState.RUNNING
                    and int(row["current_attempt"]) == attempt
                    and dict(row.get("evidence") or {}) == evidence
                )
                if not is_duplicate:
                    conflict_message = (
                        f"task run {task_run_id} attempt {attempt} cannot record control evidence"
                    )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        control_evidence = evidence or {}
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _SKIP_TASK,
                        {
                            "task_run_id": task_run_id,
                            "tenant_id": tenant_uuid,
                            "result": json.dumps(result),
                            "evidence": json.dumps(control_evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.SKIPPED,
                    correlation_id,
                    reason=str(result.get("reason") or "condition evaluated false"),
                    payload={**result, "attempt": 0, "evidence": control_evidence},
                    actor_id="system:flow-control",
                )
                await self._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    "task skipped before dispatch",
                )
                await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    row is not None
                    and TaskRunState(row["state"]) is TaskRunState.SUCCESS
                    and int(row["current_attempt"]) == 0
                    and dict(row.get("result") or {}) == result
                    and dict(row.get("evidence") or {}) == control_evidence
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} is not waiting"
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, object],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.SUCCESS,
            result,
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            evidence=evidence,
        )

    async def defer_task(
        self,
        task_run_id: UUID,
        attempt: int,
        resume_token: str,
        *,
        tenant_id: str,
        metadata: dict[str, object],
        expires_at: datetime | None = None,
    ) -> PersistedTaskDeferral:
        digest = _resume_token_digest(resume_token)
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            inserted = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO task_deferrals (
                                tenant_id, task_run_id, attempt, resume_token_digest,
                                metadata, expires_at
                            )
                            SELECT
                                :tenant_id, task_runs.id, :attempt, :digest,
                                CAST(:metadata AS jsonb), :expires_at
                            FROM task_runs
                            JOIN task_attempts
                              ON task_attempts.tenant_id = task_runs.tenant_id
                             AND task_attempts.task_run_id = task_runs.id
                             AND task_attempts.attempt = :attempt
                            WHERE task_runs.tenant_id = :tenant_id
                              AND task_runs.id = :task_run_id
                              AND task_runs.current_attempt = :attempt
                              AND task_runs.state = 'RUNNING'
                              AND task_attempts.state = 'RUNNING'
                            ON CONFLICT (tenant_id, task_run_id, attempt) DO NOTHING
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "task_run_id": task_run_id,
                            "attempt": attempt,
                            "digest": digest,
                            "metadata": json.dumps(metadata),
                            "expires_at": expires_at,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if inserted is None:
                existing = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
                if (
                    existing is None
                    or int(existing["attempt"]) != attempt
                    or not hmac.compare_digest(str(existing["resume_token_digest"]), digest)
                ):
                    raise TaskStateConflictError(
                        f"task run {task_run_id} attempt {attempt} cannot be deferred"
                    )
                return _to_task_deferral(existing)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE task_runs
                            SET version = version + 1, updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :task_run_id
                            RETURNING id, execution_id, task_path, state,
                                      current_attempt, version, retry_at
                            """
                        ),
                        {"tenant_id": tenant_uuid, "task_run_id": task_run_id},
                    )
                )
                .mappings()
                .one()
            )
            await self._insert_task_event(
                connection,
                tenant_uuid,
                row,
                command_id,
                TaskRunEventType.DEFERRED,
                correlation_id,
                reason="task deferred for asynchronous completion",
                payload={
                    "attempt": attempt,
                    "expiresAt": expires_at.isoformat() if expires_at is not None else None,
                    "metadata": metadata,
                },
            )
        return _to_task_deferral(inserted)

    async def get_task_deferral(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
    ) -> PersistedTaskDeferral | None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
        return _to_task_deferral(row) if row is not None else None

    async def resume_deferred_task(
        self,
        task_run_id: UUID,
        resume_token: str,
        result: dict[str, object],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        digest = _resume_token_digest(resume_token)
        expired = False
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            deferral = await self._get_deferral_row(connection, tenant_uuid, task_run_id)
            if deferral is None or not hmac.compare_digest(
                str(deferral["resume_token_digest"]), digest
            ):
                raise TaskStateConflictError("invalid or unavailable task resume token")
            state = str(deferral["state"])
            if state == "EXPIRED":
                raise TaskStateConflictError("task resume token has expired")
            expires_at = deferral["expires_at"]
            now = await connection.scalar(_DATABASE_TIME)
            if (
                state == "WAITING"
                and expires_at is not None
                and isinstance(now, datetime)
                and now >= expires_at
            ):
                await connection.execute(
                    text(
                        """
                        UPDATE task_deferrals SET state = 'EXPIRED'
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                          AND attempt = :attempt AND state = 'WAITING'
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "task_run_id": task_run_id,
                        "attempt": deferral["attempt"],
                    },
                )
                expired = True
            attempt = int(deferral["attempt"])
        if expired:
            raise TaskStateConflictError("task resume token has expired")
        completed = await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.SUCCESS,
            result,
            tenant_id=tenant_id,
            evidence=evidence,
        )
        return completed

    async def _get_deferral_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
    ) -> RowMapping | None:
        return (
            (
                await connection.execute(
                    text(
                        """
                        SELECT task_run_id, attempt, resume_token_digest, state,
                               metadata, expires_at, deferred_at, resumed_at
                        FROM task_deferrals
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                        ORDER BY attempt DESC
                        LIMIT 1
                        """
                    ),
                    {"tenant_id": tenant_id, "task_run_id": task_run_id},
                )
            )
            .mappings()
            .one_or_none()
        )

    async def retry_task(
        self,
        task_run_id: UUID,
        attempt: int,
        *,
        tenant_id: str,
        retry_at: datetime,
        reason: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.RETRYABLE,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _RETRY_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "retry_at": retry_at,
                    "result": json.dumps({"error": reason}),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                    "failure_category": failure_category.value,
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    TaskRunEventType.RETRY_SCHEDULED,
                    correlation_id,
                    reason=reason,
                    payload={"retry_at": retry_at.isoformat(), "error": reason},
                )
                await self._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    "task attempt entered retry delay",
                )
                await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    worker_id is None
                    and fencing_token is None
                    and row is not None
                    and TaskRunState(row["state"]) is TaskRunState.RETRY_DELAY
                    and int(row["current_attempt"]) == attempt
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} attempt {attempt} is not running"
                    if row is not None:
                        await self._record_rejection(
                            connection,
                            tenant_uuid,
                            command_id,
                            "task_run",
                            task_run_id,
                            TransitionRejectionCode.ILLEGAL_TRANSITION,
                            str(row["state"]),
                            int(row["version"]),
                            None,
                            conflict_message,
                            correlation_id,
                        )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.FAILED,
            result or {"error": reason},
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=failure_category,
            evidence=evidence,
        )

    async def cancel_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
    ) -> PersistedTaskRun:
        _require_complete_claim(worker_id, fencing_token)
        return await self._finish_task(
            task_run_id,
            attempt,
            TaskRunState.CANCELLED,
            {"error": reason, "failureCategory": FailureCategory.CANCELLED.value},
            tenant_id=tenant_id,
            worker_id=worker_id,
            fencing_token=fencing_token,
            failure_category=FailureCategory.CANCELLED,
        )

    async def complete_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
        outputs: dict[str, object] | None = None,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.SUCCESS,
            ExecutionEventType.SUCCEEDED,
            {},
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
            outputs=outputs,
        )

    async def fail_execution(
        self,
        execution_id: UUID,
        reason: str,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        return await self._finish_execution(
            execution_id,
            ExecutionState.FAILED,
            ExecutionEventType.FAILED,
            {"reason": reason},
            tenant_id=tenant_id,
            expected_epoch=expected_epoch,
            outputs=None,
        )

    async def record_execution_lifecycle(
        self,
        execution_id: UUID,
        evidence: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        event_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            recorded = await connection.scalar(
                _RECORD_EXECUTION_LIFECYCLE,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "expected_epoch": expected_epoch,
                    "evidence": json.dumps(evidence),
                    "event_id": event_id,
                    "idempotency_key": str(event_id),
                    "correlation_id": new_runtime_id(),
                },
            )
        if recorded is None:
            raise ExecutionStateConflictError(
                f"execution {execution_id} lifecycle evidence was fenced at epoch {expected_epoch}"
            )
        return await self.get_execution(execution_id, tenant_id=tenant_id)

    async def database_time(self) -> datetime:
        async with self._engine.connect() as connection:
            value = await connection.scalar(_DATABASE_TIME)
        if not isinstance(value, datetime):
            raise TypeError("PostgreSQL returned an invalid database timestamp")
        return value

    async def apply_execution_intervention(
        self,
        execution_id: UUID,
        action: ExecutionInterventionAction,
        *,
        tenant_id: str,
        expected_version: int,
        expected_epoch: int,
        actor_id: str,
        reason: str,
        grace_period: timedelta = timedelta(seconds=30),
        reset_task_ids: tuple[str, ...] = (),
        checkpoint_task_id: str | None = None,
        restart_timeout: timedelta | None = None,
    ) -> PersistedExecution:
        if grace_period.total_seconds() < 0:
            raise ValueError("cancellation grace period cannot be negative")
        if restart_timeout is not None and restart_timeout.total_seconds() <= 0:
            raise ValueError("restart timeout must be positive")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            execution = await self._lock_execution_for_control(
                connection,
                tenant_uuid,
                execution_id,
            )
            self._require_intervention_fence(
                execution,
                expected_version=expected_version,
                expected_epoch=expected_epoch,
            )
            tasks = await self._lock_tasks_for_control(connection, tenant_uuid, execution_id)
            state = ExecutionState(execution["state"])
            version = int(execution["version"])
            epoch = int(execution["epoch"])
            now = execution["database_now"]
            if not isinstance(now, datetime):
                raise TypeError("PostgreSQL returned an invalid database timestamp")
            correlation_id = new_runtime_id()

            if action is ExecutionInterventionAction.PAUSE:
                _require_control_state(action, state, {ExecutionState.RUNNING})
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.PAUSED,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.PAUSED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
            elif action is ExecutionInterventionAction.RESUME:
                _require_control_state(action, state, {ExecutionState.PAUSED})
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.RUNNING,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.RESUMED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
            elif action is ExecutionInterventionAction.REQUEST_CANCEL:
                _require_control_state(
                    action,
                    state,
                    {ExecutionState.RUNNING, ExecutionState.PAUSED, ExecutionState.QUEUED},
                )
                deadline = now + grace_period
                await self._request_task_cancellation(
                    connection,
                    tenant_uuid,
                    tasks,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.CANCELLING,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                    cancel_deadline_at=deadline,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.CANCEL_REQUESTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload={"graceDeadline": deadline.isoformat()},
                )
            elif action in {
                ExecutionInterventionAction.CONFIRM_CANCEL,
                ExecutionInterventionAction.FORCE_CANCEL,
            }:
                _require_control_state(action, state, {ExecutionState.CANCELLING})
                if action is ExecutionInterventionAction.CONFIRM_CANCEL:
                    unacknowledged = [
                        row
                        for row in tasks
                        if row["attempt_state"] == "RUNNING"
                        and not bool(row["cancellation_acknowledged"])
                    ]
                    if unacknowledged:
                        raise ExecutionStateConflictError(
                            "running attempts have not acknowledged cancellation"
                        )
                else:
                    deadline = execution["cancel_deadline_at"]
                    if not isinstance(deadline, datetime) or now < deadline:
                        raise ExecutionStateConflictError(
                            "force cancellation is not available before the grace deadline"
                        )
                await self._terminate_tasks(
                    connection,
                    tenant_uuid,
                    [
                        task
                        for task in tasks
                        if task["lifecycle_phase"] == TaskRunLifecyclePhase.MAIN.value
                        or task["state"] == TaskRunState.RUNNING.value
                    ],
                    task_state=TaskRunState.CANCELLED,
                    attempt_state="CANCELLED",
                    category=FailureCategory.CANCELLED,
                    event_type=TaskRunEventType.CANCELLED,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.CANCELLED,
                    version=version + 1,
                    epoch=epoch,
                    actor_id=actor_id,
                    cancel_deadline_at=None,
                    terminal_at=now,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.CANCELLED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                await evaluate_execution_terminal_checks(
                    connection,
                    tenant_uuid,
                    flow_revision_id=UUID(str(execution["flow_revision_id"])),
                    execution_id=execution_id,
                    execution_state=ExecutionState.CANCELLED.value,
                    namespace=str(execution["namespace_name"]),
                    flow_id=str(execution["flow_key"]),
                    flow_revision=int(
                        await connection.scalar(
                            text("SELECT revision FROM flow_revisions WHERE id = :id"),
                            {"id": execution["flow_revision_id"]},
                        )
                    ),
                    created_at=execution["created_at"],
                    terminal_at=now,
                    inputs=dict(execution["inputs"]),
                    trigger=dict(execution["trigger_context"]),
                    labels=dict(execution["labels"]),
                )
            elif action is ExecutionInterventionAction.RESTART:
                _require_control_state(
                    action,
                    state,
                    {ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.WARNING},
                )
                if not reset_task_ids:
                    raise ValueError("restart requires at least one reset task")
                known_task_ids = {str(row["task_path"]) for row in tasks}
                unknown = sorted(set(reset_task_ids) - known_task_ids)
                if unknown:
                    raise ValueError("restart reset tasks do not exist: " + ", ".join(unknown))
                effective_reset_task_ids = frozenset(
                    {
                        *reset_task_ids,
                        *(
                            str(row["task_path"])
                            for row in tasks
                            if row["lifecycle_phase"] != TaskRunLifecyclePhase.MAIN.value
                        ),
                    }
                )
                await self._restart_tasks(
                    connection,
                    tenant_uuid,
                    tasks,
                    reset_task_ids=effective_reset_task_ids,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                )
                timeout_at = now + restart_timeout if restart_timeout is not None else None
                await self._update_execution_control(
                    connection,
                    execution,
                    state=ExecutionState.RUNNING,
                    version=version + 2,
                    epoch=epoch + 1,
                    actor_id=actor_id,
                    timeout_at=timeout_at,
                    cancel_deadline_at=None,
                    terminal_at=None,
                )
                restart_payload: dict[str, object] = {
                    "checkpointTaskId": checkpoint_task_id,
                    "resetTaskIds": sorted(effective_reset_task_ids),
                    "nextEpoch": epoch + 1,
                }
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 1,
                    event_type=ExecutionEventType.RESTART_REQUESTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload=restart_payload,
                )
                await self._insert_execution_intervention_event(
                    connection,
                    tenant_uuid,
                    execution_id,
                    sequence=version + 2,
                    event_type=ExecutionEventType.STARTED,
                    action=action,
                    actor_id=actor_id,
                    reason=reason,
                    correlation_id=correlation_id,
                    extra_payload=restart_payload,
                )
            else:
                raise ValueError(f"unsupported execution intervention {action.value}")

            row = (
                (
                    await connection.execute(
                        _GET_EXECUTION,
                        {"execution_id": execution_id, "tenant_slug": tenant_id},
                    )
                )
                .mappings()
                .one()
            )
        return _to_execution(row)

    async def list_execution_interventions(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[ExecutionInterventionRecord]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            exists = await connection.scalar(
                text("SELECT id FROM executions WHERE id = :execution_id"),
                {"execution_id": execution_id},
            )
            if exists is None:
                raise LookupError(f"execution {execution_id} does not exist")
            rows = (
                (
                    await connection.execute(
                        _LIST_EXECUTION_INTERVENTIONS,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .all()
            )
        return [
            ExecutionInterventionRecord(
                sequence=int(row["sequence"]),
                action=ExecutionInterventionAction(row["payload"]["intervention"]),
                event_type=row["event_type"],
                actor_id=row["actor_id"],
                reason=row["reason"],
                occurred_at=row["occurred_at"],
                payload=row["payload"],
            )
            for row in rows
        ]

    async def timeout_execution(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution:
        actor_id = "system:execution-timeout"
        reason = "execution deadline exceeded"
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            execution = await self._lock_execution_for_control(
                connection,
                tenant_uuid,
                execution_id,
            )
            state = ExecutionState(execution["state"])
            epoch = int(execution["epoch"])
            now = execution["database_now"]
            timeout_at = execution["timeout_at"]
            if epoch != expected_epoch:
                raise ExecutionStateConflictError(
                    f"execution {execution_id} is fenced at epoch {epoch}; received {expected_epoch}"
                )
            if (
                state not in {ExecutionState.RUNNING, ExecutionState.PAUSED}
                or not isinstance(now, datetime)
                or not isinstance(timeout_at, datetime)
                or now < timeout_at
            ):
                raise ExecutionStateConflictError(
                    f"execution {execution_id} is not due for timeout"
                )
            version = int(execution["version"])
            tasks = await self._lock_tasks_for_control(connection, tenant_uuid, execution_id)
            correlation_id = new_runtime_id()
            await self._timeout_tasks(
                connection,
                tenant_uuid,
                tasks,
                actor_id=actor_id,
                reason=reason,
                correlation_id=correlation_id,
            )
            await self._update_execution_control(
                connection,
                execution,
                state=ExecutionState.FAILED,
                version=version + 1,
                epoch=epoch,
                actor_id=actor_id,
                cancel_deadline_at=None,
                terminal_at=now,
            )
            await connection.execute(
                _INSERT_EXECUTION_INTERVENTION_EVENT,
                {
                    "tenant_id": tenant_uuid,
                    "execution_id": execution_id,
                    "sequence": version + 1,
                    "event_id": new_runtime_id(),
                    "event_type": ExecutionEventType.FAILED.value,
                    "idempotency_key": f"timeout:{execution_id}:{epoch}",
                    "correlation_id": correlation_id,
                    "actor_id": actor_id,
                    "reason": reason,
                    "payload": json.dumps({"failureCategory": FailureCategory.TIMED_OUT.value}),
                },
            )
            row = (
                (
                    await connection.execute(
                        _GET_EXECUTION,
                        {"execution_id": execution_id, "tenant_slug": tenant_id},
                    )
                )
                .mappings()
                .one()
            )
        return _to_execution(row)

    async def _lock_execution_for_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> RowMapping:
        row = (
            (
                await connection.execute(
                    _LOCK_EXECUTION_CONTROL,
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise LookupError(f"execution {execution_id} does not exist")
        return row

    async def _lock_tasks_for_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> list[RowMapping]:
        return list(
            (
                await connection.execute(
                    _LOCK_TASK_RUNS_CONTROL,
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .all()
        )

    @staticmethod
    def _require_intervention_fence(
        execution: RowMapping,
        *,
        expected_version: int,
        expected_epoch: int,
    ) -> None:
        if int(execution["version"]) != expected_version:
            raise ExecutionStateConflictError(
                f"execution version is {execution['version']}; received {expected_version}"
            )
        if int(execution["epoch"]) != expected_epoch:
            raise ExecutionStateConflictError(
                f"execution epoch is {execution['epoch']}; received {expected_epoch}"
            )

    async def _update_execution_control(
        self,
        connection: AsyncConnection,
        execution: RowMapping,
        *,
        state: ExecutionState,
        version: int,
        epoch: int,
        actor_id: str,
        timeout_at: datetime | _Unset | None = _UNSET,
        cancel_deadline_at: datetime | _Unset | None = _UNSET,
        terminal_at: datetime | _Unset | None = _UNSET,
    ) -> None:
        changed = await connection.scalar(
            _UPDATE_EXECUTION_CONTROL,
            {
                "execution_id": execution["id"],
                "tenant_id": execution["tenant_id"],
                "state": state.value,
                "epoch": epoch,
                "version": version,
                "timeout_at": (execution["timeout_at"] if timeout_at is _UNSET else timeout_at),
                "cancel_deadline_at": (
                    execution["cancel_deadline_at"]
                    if cancel_deadline_at is _UNSET
                    else cancel_deadline_at
                ),
                "terminal_at": (execution["terminal_at"] if terminal_at is _UNSET else terminal_at),
                "actor_id": actor_id,
            },
        )
        if changed is None:
            raise ExecutionStateConflictError(
                f"execution {execution['id']} changed during intervention"
            )

    async def _request_task_cancellation(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if (
                state in {TaskRunState.WAITING, TaskRunState.RETRY_DELAY}
                and task["lifecycle_phase"] == TaskRunLifecyclePhase.MAIN.value
            ):
                changed = await self._update_task_control(
                    connection,
                    tenant_id,
                    task,
                    TaskRunState.CANCELLED,
                )
                await self._insert_task_event(
                    connection,
                    tenant_id,
                    changed,
                    new_runtime_id(),
                    TaskRunEventType.CANCELLED,
                    correlation_id,
                    reason=reason,
                    payload={
                        "intervention": ExecutionInterventionAction.REQUEST_CANCEL.value,
                        "failureCategory": FailureCategory.CANCELLED.value,
                    },
                    actor_id=actor_id,
                )
            elif state is TaskRunState.RUNNING and task["attempt_id"] is not None:
                await connection.execute(
                    _REQUEST_ATTEMPT_CANCELLATION,
                    {"tenant_id": tenant_id, "attempt_id": task["attempt_id"]},
                )

    async def _terminate_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        task_state: TaskRunState,
        attempt_state: str,
        category: FailureCategory,
        event_type: TaskRunEventType,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if state in {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}:
                continue
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state=attempt_state,
                    category=category,
                    reason=reason,
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                task_state,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=reason,
                payload={"failureCategory": category.value},
                actor_id=actor_id,
            )

    async def _restart_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        reset_task_ids: frozenset[str],
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            if str(task["task_path"]) not in reset_task_ids:
                continue
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state="CANCELLED",
                    category=FailureCategory.CANCELLED,
                    reason="superseded by execution restart",
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                TaskRunState.WAITING,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                TaskRunEventType.RESTARTED,
                correlation_id,
                reason=reason,
                payload={"intervention": ExecutionInterventionAction.RESTART.value},
                actor_id=actor_id,
            )

    async def _timeout_tasks(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        tasks: list[RowMapping],
        *,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        for task in tasks:
            state = TaskRunState(task["state"])
            if state in {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}:
                continue
            target_state = (
                TaskRunState.FAILED if state is TaskRunState.RUNNING else TaskRunState.CANCELLED
            )
            event_type = (
                TaskRunEventType.FAILED
                if target_state is TaskRunState.FAILED
                else TaskRunEventType.CANCELLED
            )
            category = (
                FailureCategory.TIMED_OUT
                if target_state is TaskRunState.FAILED
                else FailureCategory.CANCELLED
            )
            if task["attempt_state"] == "RUNNING" and task["attempt_id"] is not None:
                await self._invalidate_attempt(
                    connection,
                    tenant_id,
                    task,
                    attempt_state="TIMED_OUT",
                    category=FailureCategory.TIMED_OUT,
                    reason=reason,
                )
            changed = await self._update_task_control(
                connection,
                tenant_id,
                task,
                target_state,
            )
            await self._insert_task_event(
                connection,
                tenant_id,
                changed,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=reason,
                payload={"failureCategory": category.value},
                actor_id=actor_id,
            )

    async def _invalidate_attempt(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task: RowMapping,
        *,
        attempt_state: str,
        category: FailureCategory,
        reason: str,
    ) -> None:
        changed = await connection.scalar(
            _INVALIDATE_ATTEMPT,
            {
                "tenant_id": tenant_id,
                "attempt_id": task["attempt_id"],
                "state": attempt_state,
                "failure_category": category.value,
                "result": json.dumps({"error": reason, "failureCategory": category.value}),
            },
        )
        if changed is None:
            raise ExecutionStateConflictError(
                f"task attempt for {task['task_path']} changed during intervention"
            )
        if task["queue_id"] is not None:
            await connection.execute(
                _DELETE_TASK_QUEUE,
                {"tenant_id": tenant_id, "queue_id": task["queue_id"]},
            )

    async def _update_task_control(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task: RowMapping,
        state: TaskRunState,
    ) -> RowMapping:
        row = (
            (
                await connection.execute(
                    _UPDATE_TASK_CONTROL,
                    {
                        "tenant_id": tenant_id,
                        "task_run_id": task["id"],
                        "expected_state": task["state"],
                        "state": state.value,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ExecutionStateConflictError(
                f"task run {task['task_path']} changed during intervention"
            )
        return row

    async def _insert_execution_intervention_event(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        *,
        sequence: int,
        event_type: ExecutionEventType,
        action: ExecutionInterventionAction,
        actor_id: str,
        reason: str,
        correlation_id: UUID,
        extra_payload: dict[str, object] | None = None,
    ) -> None:
        event_id = new_runtime_id()
        payload: dict[str, object] = {"intervention": action.value}
        payload.update(extra_payload or {})
        await connection.execute(
            _INSERT_EXECUTION_INTERVENTION_EVENT,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "sequence": sequence,
                "event_id": event_id,
                "event_type": event_type.value,
                "idempotency_key": str(event_id),
                "correlation_id": correlation_id,
                "actor_id": actor_id,
                "reason": reason,
                "payload": json.dumps(payload),
            },
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
            raise LookupError(f"tenant {tenant_slug!r} does not exist")
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
        _encoded, semantic_hash = _canonical_flow(flow)
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
        canonical_definition = _encode_flow(stored_flow)
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
                "plugin_resolution": json.dumps(plugin_resolution),
                "source": source.source,
                "source_commit": source.source_commit,
                "environment": source.environment,
                "deployment_metadata": json.dumps(source.deployment),
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
            raise LookupError(f"flow {namespace}.{flow_id} does not exist")
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
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
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
                raise LookupError(f"flow {namespace}.{flow_id} revision {revision} does not exist")
            flow = FlowDefinition.model_validate(definition)
            activation = await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_row["id"],
                    "revision": revision,
                    "status": lifecycle.value,
                    "labels": json.dumps({**flow.labels, **flow_system_labels(flow)}),
                    "annotations": json.dumps(flow.annotations),
                    "actor_id": actor_id,
                    "expected_version": None,
                },
            )
            if activation.scalar_one_or_none() is None:
                raise ResourceVersionConflict(
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
                "payload": json.dumps(event_payload),
            },
        )
        source_payload = (source or FlowRevisionSource()).model_dump(mode="json", exclude_none=True)
        await connection.execute(
            _INSERT_FLOW_AUDIT,
            {
                "event_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "actor_id": actor_id,
                "action": event_type.lower(),
                "resource_id": str(flow_id),
                "reason": reason,
                "source": json.dumps(source_payload),
                "evidence": json.dumps(event_payload),
            },
        )

    async def _insert_initial_events(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        occurred_at: datetime,
        actor_id: str,
        outcome: AdmissionOutcome,
        reason: str,
    ) -> None:
        correlation_id = new_runtime_id()
        event_types = [ExecutionEventType.CREATED, ExecutionEventType.QUEUED]
        if outcome in {AdmissionOutcome.ADMITTED, AdmissionOutcome.REPLACED}:
            event_types.append(ExecutionEventType.STARTED)
        elif outcome is AdmissionOutcome.CANCELLED:
            event_types.extend([ExecutionEventType.CANCEL_REQUESTED, ExecutionEventType.CANCELLED])
        elif outcome in {AdmissionOutcome.FAILED, AdmissionOutcome.SKIPPED}:
            event_types.extend(
                [
                    ExecutionEventType.STARTED,
                    ExecutionEventType.FAILED
                    if outcome is AdmissionOutcome.FAILED
                    else ExecutionEventType.SUCCEEDED,
                ]
            )
        parameters: list[dict[str, object]] = []
        for sequence, event_type in enumerate(event_types, start=1):
            event_id = new_runtime_id()
            parameters.append(
                {
                    "tenant_id": tenant_id,
                    "execution_id": execution_id,
                    "sequence": sequence,
                    "event_id": event_id,
                    "event_type": event_type.value,
                    "idempotency_key": str(event_id),
                    "correlation_id": correlation_id,
                    "actor_id": actor_id,
                    "reason": reason if sequence > 2 else None,
                    "occurred_at": occurred_at,
                }
            )
        await connection.execute(_INSERT_EXECUTION_EVENT, parameters)

    async def _finish_task(
        self,
        task_run_id: UUID,
        attempt: int,
        state: TaskRunState,
        result_payload: dict[str, object],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun:
        command_id = new_runtime_id()
        correlation_id = new_runtime_id()
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _FINISH_TASK,
                {
                    "task_run_id": task_run_id,
                    "tenant_id": tenant_uuid,
                    "attempt": attempt,
                    "state": state.value,
                    "result": json.dumps(result_payload),
                    "evidence": json.dumps(evidence or {}),
                    "worker_id": worker_id,
                    "worker_consumer_id": str(worker_id) if worker_id is not None else None,
                    "fencing_token": fencing_token,
                    "failure_category": (
                        failure_category.value if failure_category is not None else None
                    ),
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await store_task_evidence(
                    connection,
                    tenant_uuid,
                    execution_id=row["execution_id"],
                    task_run_id=task_run_id,
                    attempt=attempt,
                    worker_id=worker_id,
                    output=result_payload,
                    evidence=evidence or {},
                )
                await connection.execute(
                    text(
                        """
                        UPDATE task_deferrals
                        SET state = CASE WHEN :state = 'SUCCESS' THEN 'COMPLETED' ELSE 'EXPIRED' END,
                            resumed_at = CASE
                                WHEN :state = 'SUCCESS' THEN clock_timestamp()
                                ELSE resumed_at
                            END
                        WHERE tenant_id = :tenant_id AND task_run_id = :task_run_id
                          AND attempt = :attempt AND state = 'WAITING'
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "task_run_id": task_run_id,
                        "attempt": attempt,
                        "state": state.value,
                    },
                )
                event_type = {
                    TaskRunState.SUCCESS: TaskRunEventType.SUCCEEDED,
                    TaskRunState.FAILED: TaskRunEventType.FAILED,
                    TaskRunState.CANCELLED: TaskRunEventType.CANCELLED,
                }[state]
                await self._insert_task_event(
                    connection,
                    tenant_uuid,
                    row,
                    command_id,
                    event_type,
                    correlation_id,
                    reason=str(result_payload.get("error"))
                    if result_payload.get("error") is not None
                    else None,
                    payload=result_payload,
                )
                await self._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.TASK,
                    task_run_id,
                    f"task reached {state.value}",
                )
                await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
            else:
                row = await self._get_task_run_row(connection, tenant_uuid, task_run_id)
                is_duplicate = (
                    worker_id is None
                    and fencing_token is None
                    and row is not None
                    and TaskRunState(row["state"]) is state
                    and int(row["current_attempt"]) == attempt
                )
                if not is_duplicate:
                    conflict_message = f"task run {task_run_id} attempt {attempt} is not running"
                    if row is not None:
                        await self._record_rejection(
                            connection,
                            tenant_uuid,
                            command_id,
                            "task_run",
                            task_run_id,
                            TransitionRejectionCode.ILLEGAL_TRANSITION,
                            str(row["state"]),
                            int(row["version"]),
                            None,
                            conflict_message,
                            correlation_id,
                        )
        if conflict_message is not None or row is None:
            raise TaskStateConflictError(
                conflict_message or f"task run {task_run_id} does not exist"
            )
        return _to_task_run(row)

    async def _finish_execution(
        self,
        execution_id: UUID,
        state: ExecutionState,
        event_type: ExecutionEventType,
        payload: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
        outputs: dict[str, object] | None,
    ) -> PersistedExecution:
        event_id = new_runtime_id()
        correlation_id = new_runtime_id()
        reason = str(payload.get("reason")) if payload.get("reason") is not None else None
        conflict_message: str | None = None
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            result = await connection.execute(
                _FINISH_EXECUTION,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "expected_epoch": expected_epoch,
                    "state": state.value,
                    "event_id": event_id,
                    "event_type": event_type.value,
                    "idempotency_key": str(event_id),
                    "correlation_id": correlation_id,
                    "reason": reason,
                    "payload": json.dumps(payload),
                    "outputs": json.dumps(outputs or {}),
                },
            )
            row = result.mappings().one_or_none()
            if row is not None:
                await evaluate_execution_terminal_checks(
                    connection,
                    tenant_uuid,
                    flow_revision_id=UUID(str(row["flow_revision_id"])),
                    execution_id=execution_id,
                    execution_state=state.value,
                    namespace=str(row["namespace_name"]),
                    flow_id=str(row["flow_key"]),
                    flow_revision=int(row["flow_revision"]),
                    created_at=row["created_at"],
                    terminal_at=row["updated_at"],
                    inputs=dict(row["inputs"]),
                    trigger=dict(row["trigger_context"]),
                    labels=dict(row["labels"]),
                )
                await emit_flow_completion_occurrences(
                    connection,
                    tenant_uuid,
                    source_execution_id=execution_id,
                    source_namespace=str(row["namespace_name"]),
                    source_flow_id=str(row["flow_key"]),
                    source_flow_revision=int(row["flow_revision"]),
                    terminal_state=state.value,
                    source_trigger=dict(row["trigger_context"]),
                )
                await self._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.EXECUTION,
                    execution_id,
                    f"execution reached {state.value}",
                )
                await self._reconcile_admission_tx(connection, tenant_uuid, limit=100)
            if row is None:
                existing_result = await connection.execute(
                    _GET_EXECUTION,
                    {"execution_id": execution_id, "tenant_slug": tenant_id},
                )
                row = existing_result.mappings().one_or_none()
                if row is None:
                    conflict_message = f"execution {execution_id} does not exist"
                elif int(row["epoch"]) != expected_epoch:
                    conflict_message = (
                        f"execution {execution_id} is fenced at epoch {row['epoch']}; "
                        f"received {expected_epoch}"
                    )
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        event_id,
                        "execution",
                        execution_id,
                        TransitionRejectionCode.EPOCH_CONFLICT,
                        str(row["state"]),
                        int(row["version"]),
                        int(row["epoch"]),
                        conflict_message,
                        correlation_id,
                    )
                elif ExecutionState(row["state"]) is not state:
                    conflict_message = (
                        f"execution {execution_id} cannot transition from "
                        f"{row['state']} to {state.value}"
                    )
                    await self._record_rejection(
                        connection,
                        tenant_uuid,
                        event_id,
                        "execution",
                        execution_id,
                        TransitionRejectionCode.ILLEGAL_TRANSITION,
                        str(row["state"]),
                        int(row["version"]),
                        int(row["epoch"]),
                        conflict_message,
                        correlation_id,
                    )
        if conflict_message is not None or row is None:
            raise ExecutionStateConflictError(
                conflict_message or f"execution {execution_id} does not exist"
            )
        return _to_execution(row)

    async def _request_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
        priority: int,
    ) -> AdmissionDecision:
        await connection.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:resource_key, 0))"),
            {"resource_key": f"{tenant_id}:{resource_type.value}:{resource_id}"},
        )
        existing = await self._get_admission_row(
            connection,
            tenant_id,
            resource_type,
            resource_id,
        )
        if existing is not None and AdmissionOutcome(existing["outcome"]) not in {
            AdmissionOutcome.RELEASED,
            AdmissionOutcome.EXPIRED,
        }:
            return _to_admission_decision(existing)
        await connection.execute(
            _EXPIRE_ADMISSION_RESERVATIONS,
            {"tenant_id": tenant_id},
        )
        for bucket in sorted({policy.bucket for policy in policies}):
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:bucket, 0))"),
                {"bucket": bucket},
            )

        limiting: ResolvedAdmissionPolicy | None = None
        active_count = 0
        for policy in policies:
            count = int(
                await connection.scalar(
                    text("SELECT amesh_admission_active_count(:resource_type, :bucket)"),
                    {"resource_type": resource_type.value, "bucket": policy.bucket},
                )
                or 0
            )
            if count >= policy.limit:
                limiting = policy
                active_count = count
                break

        replaced_resource_id: UUID | None = None
        outcome = AdmissionOutcome.ADMITTED
        reason = "all admission policies have available capacity"
        if limiting is not None and limiting.behavior is AdmissionBehavior.REPLACE:
            victim = await connection.scalar(
                text(
                    """
                    SELECT resource_id
                    FROM admission_reservations
                    WHERE tenant_id = :tenant_id
                      AND resource_type = :resource_type
                      AND bucket = :bucket
                      AND released_at IS NULL
                      AND lease_expires_at > clock_timestamp()
                    ORDER BY created_at, reservation_id
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "resource_type": resource_type.value,
                    "bucket": limiting.bucket,
                },
            )
            if victim is not None:
                replaced_resource_id = UUID(str(victim))
                await self._release_admission_tx(
                    connection,
                    tenant_id,
                    resource_type,
                    replaced_resource_id,
                    f"replaced by {resource_id}",
                    replacement=True,
                )
                await self._terminate_replaced_resource(
                    connection,
                    tenant_id,
                    resource_type,
                    replaced_resource_id,
                    resource_id,
                )
                limiting = None
                outcome = AdmissionOutcome.REPLACED
                reason = f"admitted after replacing {replaced_resource_id}"

        if limiting is not None:
            outcome = {
                AdmissionBehavior.QUEUE: AdmissionOutcome.QUEUED,
                AdmissionBehavior.CANCEL: AdmissionOutcome.CANCELLED,
                AdmissionBehavior.FAIL: AdmissionOutcome.FAILED,
                AdmissionBehavior.REPLACE: AdmissionOutcome.REPLACED,
                AdmissionBehavior.SKIP: AdmissionOutcome.SKIPPED,
            }[limiting.behavior]
            reason = (
                f"policy {limiting.policy_id} reached {active_count}/{limiting.limit}; "
                f"behavior={limiting.behavior.value}"
            )

        request_id = new_runtime_id()
        inserted = (
            (
                await connection.execute(
                    _INSERT_ADMISSION_REQUEST,
                    {
                        "request_id": request_id,
                        "tenant_id": tenant_id,
                        "resource_type": resource_type.value,
                        "resource_id": resource_id,
                        "policies": json.dumps(
                            [policy.model_dump(mode="json") for policy in policies]
                        ),
                        "priority": priority,
                        "outcome": outcome.value,
                        "reason": reason,
                        "limiting_policy_id": limiting.policy_id if limiting else None,
                        "limiting_scope": limiting.scope.value if limiting else None,
                        "limiting_bucket": limiting.bucket if limiting else None,
                        "active_count": active_count,
                        "limit_value": limiting.limit if limiting else None,
                        "replaced_resource_id": replaced_resource_id,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if inserted is None:
            raise RuntimeError("admission request identity conflict")
        if outcome in {AdmissionOutcome.ADMITTED, AdmissionOutcome.REPLACED}:
            await self._insert_admission_reservations(
                connection,
                tenant_id,
                request_id,
                resource_type,
                resource_id,
                policies,
            )
        row = await self._get_admission_row(
            connection,
            tenant_id,
            resource_type,
            resource_id,
        )
        if row is None:
            raise RuntimeError("admission decision was not persisted")
        return _to_admission_decision(row)

    async def _get_admission_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
    ) -> RowMapping | None:
        return (
            (
                await connection.execute(
                    _GET_ADMISSION_REQUEST,
                    {
                        "tenant_id": tenant_id,
                        "resource_type": resource_type.value,
                        "resource_id": resource_id,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )

    async def _insert_admission_reservations(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        request_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        policies: tuple[ResolvedAdmissionPolicy, ...],
    ) -> None:
        if not policies:
            return
        await connection.execute(
            _INSERT_ADMISSION_RESERVATION,
            [
                {
                    "reservation_id": new_runtime_id(),
                    "tenant_id": tenant_id,
                    "request_id": request_id,
                    "resource_type": resource_type.value,
                    "resource_id": resource_id,
                    "policy_id": policy.policy_id,
                    "scope": policy.scope.value,
                    "bucket": policy.bucket,
                    "lease_seconds": policy.lease_seconds,
                }
                for policy in policies
            ],
        )

    async def _release_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        reason: str,
        *,
        replacement: bool = False,
    ) -> bool:
        result = await connection.execute(
            _RELEASE_ADMISSION,
            {
                "tenant_id": tenant_id,
                "resource_type": resource_type.value,
                "resource_id": resource_id,
                "reason": reason,
            },
        )
        released = result.scalar_one_or_none() is not None
        if replacement:
            await connection.execute(
                text(
                    """
                    UPDATE admission_requests
                    SET outcome = 'REPLACED', reason = :reason,
                        finished_at = COALESCE(finished_at, clock_timestamp())
                    WHERE tenant_id = :tenant_id
                      AND resource_type = :resource_type
                      AND resource_id = :resource_id
                      AND outcome IN ('ADMITTED', 'RELEASED')
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "resource_type": resource_type.value,
                    "resource_id": resource_id,
                    "reason": reason,
                },
            )
        return released

    async def _reconcile_admission_tx(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        *,
        limit: int,
    ) -> int:
        await connection.execute(
            _EXPIRE_ADMISSION_RESERVATIONS,
            {"tenant_id": tenant_id},
        )
        queued = (
            (
                await connection.execute(
                    _LIST_QUEUED_ADMISSIONS,
                    {"tenant_id": tenant_id, "limit": limit},
                )
            )
            .mappings()
            .all()
        )
        promoted = 0
        for row in queued:
            policies = tuple(
                ResolvedAdmissionPolicy.model_validate(item) for item in row["policies"]
            )
            for bucket in sorted({policy.bucket for policy in policies}):
                await connection.execute(
                    text("SELECT pg_advisory_xact_lock(hashtextextended(:bucket, 0))"),
                    {"bucket": bucket},
                )
            capacity_reached = False
            for policy in policies:
                active = int(
                    await connection.scalar(
                        text("SELECT amesh_admission_active_count(:resource_type, :bucket)"),
                        {
                            "resource_type": row["resource_type"],
                            "bucket": policy.bucket,
                        },
                    )
                    or 0
                )
                if active >= policy.limit:
                    capacity_reached = True
                    break
            if capacity_reached:
                continue
            updated = await connection.scalar(
                text(
                    """
                    UPDATE admission_requests
                    SET outcome = 'ADMITTED', reason = 'capacity became available',
                        limiting_policy_id = NULL, limiting_scope = NULL,
                        limiting_bucket = NULL, active_count = 0, limit_value = NULL,
                        admitted_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id AND request_id = :request_id
                      AND outcome = 'QUEUED'
                    RETURNING request_id
                    """
                ),
                {"tenant_id": tenant_id, "request_id": row["request_id"]},
            )
            if updated is None:
                continue
            resource_type = AdmissionResourceType(row["resource_type"])
            resource_id = UUID(str(row["resource_id"]))
            await self._insert_admission_reservations(
                connection,
                tenant_id,
                UUID(str(row["request_id"])),
                resource_type,
                resource_id,
                policies,
            )
            if resource_type is AdmissionResourceType.EXECUTION:
                await self._start_promoted_execution(connection, tenant_id, resource_id)
            promoted += 1
        return promoted

    async def _start_promoted_execution(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
    ) -> None:
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE executions
                        SET state = 'RUNNING', version = version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :execution_id
                          AND state = 'QUEUED'
                        RETURNING version, flow_revision_id, namespace_name, flow_key,
                                  inputs, labels, trigger_context, created_at, updated_at
                        """
                    ),
                    {"tenant_id": tenant_id, "execution_id": execution_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return
        event_id = new_runtime_id()
        await connection.execute(
            _INSERT_EXECUTION_EVENT,
            {
                "tenant_id": tenant_id,
                "execution_id": execution_id,
                "sequence": int(row["version"]),
                "event_id": event_id,
                "event_type": ExecutionEventType.STARTED.value,
                "idempotency_key": str(event_id),
                "correlation_id": new_runtime_id(),
                "actor_id": "system:admission-reconciler",
                "reason": "capacity became available",
                "occurred_at": await connection.scalar(_DATABASE_TIME),
            },
        )
        flow_revision = await connection.scalar(
            text("SELECT revision FROM flow_revisions WHERE id = :id"),
            {"id": row["flow_revision_id"]},
        )
        await record_execution_check_start(
            connection,
            tenant_id,
            flow_revision_id=UUID(str(row["flow_revision_id"])),
            execution_id=execution_id,
            execution_state=ExecutionState.RUNNING.value,
            namespace=str(row["namespace_name"]),
            flow_id=str(row["flow_key"]),
            flow_revision=int(flow_revision),
            created_at=row["created_at"],
            started_at=row["updated_at"],
            trigger=dict(row["trigger_context"]),
            labels=dict(row["labels"]),
        )

    async def _terminate_replaced_resource(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        resource_type: AdmissionResourceType,
        resource_id: UUID,
        replacement_id: UUID,
    ) -> None:
        reason = f"replaced by {replacement_id}"
        if resource_type is AdmissionResourceType.EXECUTION:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE executions
                            SET state = 'CANCELLED', version = version + 2,
                                terminal_at = clock_timestamp(), updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND id = :resource_id
                              AND state IN ('RUNNING', 'QUEUED', 'PAUSED')
                            RETURNING version
                            """
                        ),
                        {"tenant_id": tenant_id, "resource_id": resource_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                occurred_at = await connection.scalar(_DATABASE_TIME)
                correlation_id = new_runtime_id()
                version = int(row["version"])
                parameters = []
                for sequence, event_type in (
                    (version - 1, ExecutionEventType.CANCEL_REQUESTED),
                    (version, ExecutionEventType.CANCELLED),
                ):
                    event_id = new_runtime_id()
                    parameters.append(
                        {
                            "tenant_id": tenant_id,
                            "execution_id": resource_id,
                            "sequence": sequence,
                            "event_id": event_id,
                            "event_type": event_type.value,
                            "idempotency_key": str(event_id),
                            "correlation_id": correlation_id,
                            "actor_id": "system:admission-controller",
                            "reason": reason,
                            "occurred_at": occurred_at,
                        }
                    )
                await connection.execute(_INSERT_EXECUTION_EVENT, parameters)
            return
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE task_runs
                        SET state = 'CANCELLED', version = version + 1,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :resource_id
                          AND state IN ('WAITING', 'RUNNING', 'RETRY_DELAY')
                        RETURNING id, execution_id, task_path, state,
                                  current_attempt, version, retry_at
                        """
                    ),
                    {"tenant_id": tenant_id, "resource_id": resource_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is not None:
            await self._insert_task_event(
                connection,
                tenant_id,
                row,
                new_runtime_id(),
                TaskRunEventType.CANCELLED,
                new_runtime_id(),
                reason=reason,
                payload={"replacementId": str(replacement_id)},
                actor_id="system:admission-controller",
            )

    async def _terminate_denied_task(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
        decision: AdmissionDecision,
    ) -> None:
        terminal_state = {
            AdmissionOutcome.CANCELLED: TaskRunState.CANCELLED,
            AdmissionOutcome.FAILED: TaskRunState.FAILED,
            AdmissionOutcome.SKIPPED: TaskRunState.SUCCESS,
        }[decision.outcome]
        event_types = (
            (TaskRunEventType.CANCELLED,)
            if terminal_state is TaskRunState.CANCELLED
            else (
                TaskRunEventType.STARTED,
                TaskRunEventType.FAILED
                if terminal_state is TaskRunState.FAILED
                else TaskRunEventType.SUCCEEDED,
            )
        )
        row = (
            (
                await connection.execute(
                    text(
                        """
                        UPDATE task_runs
                        SET state = :state, version = version + :version_delta,
                            current_attempt = CASE
                                WHEN :version_delta = 2 THEN current_attempt + 1
                                ELSE current_attempt
                            END,
                            updated_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND id = :task_run_id
                          AND state = 'WAITING'
                        RETURNING id, execution_id, task_path, state,
                                  current_attempt, version, retry_at
                        """
                    ),
                    {
                        "tenant_id": tenant_id,
                        "task_run_id": task_run_id,
                        "state": terminal_state.value,
                        "version_delta": len(event_types),
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return
        correlation_id = new_runtime_id()
        first_sequence = int(row["version"]) - len(event_types) + 1
        for offset, event_type in enumerate(event_types):
            event_row = dict(row)
            event_row["version"] = first_sequence + offset
            await self._insert_task_event(
                connection,
                tenant_id,
                event_row,
                new_runtime_id(),
                event_type,
                correlation_id,
                reason=decision.reason,
                payload={
                    "admissionRequestId": str(decision.request_id),
                    "admissionOutcome": decision.outcome.value,
                    "dispatch": event_type is not TaskRunEventType.STARTED,
                },
                actor_id="system:admission-controller",
            )

    async def _get_task_run_row(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        task_run_id: UUID,
    ) -> RowMapping | None:
        result = await connection.execute(
            _GET_TASK_RUN,
            {"task_run_id": task_run_id, "tenant_id": tenant_id},
        )
        return result.mappings().one_or_none()

    async def _insert_task_event(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        row: RowMapping | Mapping[str, object],
        event_id: UUID,
        event_type: TaskRunEventType,
        correlation_id: UUID,
        *,
        reason: str | None = None,
        payload: dict[str, object] | None = None,
        actor_id: str = "mvp-executor",
    ) -> None:
        await connection.execute(
            _INSERT_TASK_RUN_EVENT,
            {
                "tenant_id": tenant_id,
                "task_run_id": row["id"],
                "execution_id": row["execution_id"],
                "sequence": row["version"],
                "event_id": event_id,
                "event_type": event_type.value,
                "idempotency_key": str(event_id),
                "correlation_id": correlation_id,
                "actor_id": actor_id,
                "reason": reason,
                "payload": json.dumps(payload or {}),
            },
        )

    async def _record_rejection(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        command_id: UUID,
        aggregate_type: str,
        aggregate_id: UUID,
        code: TransitionRejectionCode,
        current_state: str,
        current_version: int,
        current_epoch: int | None,
        reason: str,
        correlation_id: UUID,
    ) -> None:
        await connection.execute(
            _INSERT_TRANSITION_REJECTION,
            {
                "tenant_id": tenant_id,
                "rejection_id": command_id,
                "command_id": command_id,
                "idempotency_key": str(command_id),
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "code": code.value,
                "current_state": current_state,
                "current_version": current_version,
                "current_epoch": current_epoch,
                "actor_id": "mvp-executor",
                "reason": reason,
                "correlation_id": correlation_id,
            },
        )


def _to_execution(row: RowMapping) -> PersistedExecution:
    return PersistedExecution(
        execution_id=row["id"],
        tenant_id=row["tenant_slug"],
        state=row["state"],
        epoch=row["epoch"],
        version=row["version"],
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        inputs=row["inputs"],
        outputs=row["outputs"],
        labels=row["labels"],
        trigger=row["trigger_context"],
        created_by=row["created_by"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        timeout_at=row["timeout_at"],
        cancel_deadline_at=row["cancel_deadline_at"],
        lifecycle_evidence=row.get("lifecycle_evidence") or {},
    )


def _to_subflow(row: RowMapping) -> PersistedSubflow:
    return PersistedSubflow(
        relationship_id=row["id"],
        parent_execution_id=row["parent_execution_id"],
        parent_task_run_id=row["parent_task_run_id"],
        parent_attempt=row["parent_attempt"],
        child_execution_id=row["child_execution_id"],
        invocation_key=row["invocation_key"],
        mode=row["mode"],
        depth=row["depth"],
        target_revision=row["target_revision"],
        propagation=SubflowPropagation.model_validate(row["propagation"]),
        output_mapping=row["output_mapping"],
        parent_namespace=row["parent_namespace"],
        parent_flow_id=row["parent_flow_id"],
        parent_flow_revision=row["parent_flow_revision"],
        child_namespace=row["child_namespace"],
        child_flow_id=row["child_flow_id"],
        child_state=row["child_state"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def _to_flow(row: RowMapping) -> PersistedFlow:
    created_at = row["created_at"]
    updated_at = max(created_at, row["updated_at"])
    metadata = ResourceMetadata(
        labels=row["labels"],
        annotations=row["annotations"],
        created_at=created_at,
        updated_at=updated_at,
        created_by=row["created_by"],
        updated_by=row["updated_by"],
        resource_version=row["version"],
        lifecycle=row["lifecycle"],
        archived_at=row["archived_at"],
        deleted_at=row["deleted_at"],
    )
    representation = {
        "resourceId": str(row["id"]),
        "tenantId": row["tenant_slug"],
        "namespace": row["namespace"],
        "flowId": row["flow_key"],
        "revision": row["revision"],
        "semanticHash": row["semantic_hash"],
        "metadata": metadata.model_dump(mode="json", exclude_none=True),
    }
    return PersistedFlow(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        lifecycle=row["status"],
        metadata=metadata,
        etag=resource_etag(representation),
    )


def _to_flow_revision(row: RowMapping) -> FlowRevisionRecord:
    return FlowRevisionRecord(
        resource_id=row["id"],
        tenant_id=row["tenant_slug"],
        namespace=row["namespace"],
        flow_id=row["flow_key"],
        revision=row["revision"],
        semantic_hash=row["semantic_hash"],
        plugin_resolution=row["plugin_resolution"],
        source=row["source"],
        source_commit=row["source_commit"],
        environment=row["environment"],
        deployment=row["deployment_metadata"],
        created_by=row["created_by"],
        created_at=row["created_at"],
    )


def _to_task_run(row: RowMapping) -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=row["id"],
        execution_id=row["execution_id"],
        task_id=row["task_path"],
        iteration_key=row.get("iteration_key"),
        state=row["state"],
        current_attempt=row["current_attempt"],
        version=row["version"],
        retry_at=row["retry_at"],
        result=row["result"],
        failure_category=row["failure_category"],
        evidence=row.get("evidence") or {},
        lifecycle_phase=row.get("lifecycle_phase") or TaskRunLifecyclePhase.MAIN,
        labels=dict(row.get("labels") or {}),
    )


def _to_task_deferral(row: RowMapping) -> PersistedTaskDeferral:
    return PersistedTaskDeferral(
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        state=row["state"],
        metadata=row["metadata"],
        expires_at=row["expires_at"],
        deferred_at=row["deferred_at"],
        resumed_at=row["resumed_at"],
    )


def _resume_token_digest(resume_token: str) -> str:
    if not resume_token:
        raise ValueError("resume token must not be empty")
    return hashlib.sha256(resume_token.encode("utf-8")).hexdigest()


def _to_admission_decision(row: RowMapping) -> AdmissionDecision:
    limiting_scope = row["limiting_scope"]
    return AdmissionDecision(
        request_id=row["request_id"],
        resource_type=row["resource_type"],
        resource_id=row["resource_id"],
        outcome=row["outcome"],
        reason=row["reason"],
        limiting_policy_id=row["limiting_policy_id"],
        limiting_scope=AdmissionScope(limiting_scope) if limiting_scope else None,
        limiting_bucket=row["limiting_bucket"],
        active_count=row["active_count"],
        limit=row["limit_value"],
        queue_position=row.get("queue_position"),
        queue_age_seconds=float(row.get("queue_age_seconds") or 0),
        priority=row["priority"],
        created_at=row["created_at"],
        admitted_at=row["admitted_at"],
        released_at=row["finished_at"],
        replaced_resource_id=row["replaced_resource_id"],
    )


def _require_complete_claim(worker_id: UUID | None, fencing_token: int | None) -> None:
    if (worker_id is None) != (fencing_token is None):
        raise ValueError("worker_id and fencing_token must be supplied together")
    if fencing_token is not None and fencing_token < 1:
        raise ValueError("worker fencing token must be positive")


def _require_control_state(
    action: ExecutionInterventionAction,
    state: ExecutionState,
    allowed: set[ExecutionState],
) -> None:
    if state not in allowed:
        expected = ", ".join(sorted(candidate.value for candidate in allowed))
        raise ExecutionStateConflictError(
            f"{action.value} requires execution state {expected}; found {state.value}"
        )


def _canonical_flow(flow: FlowDefinition) -> tuple[str, str]:
    if (
        flow._persisted_canonical_definition is not None
        and flow._persisted_semantic_hash is not None
    ):
        return flow._persisted_canonical_definition, flow._persisted_semantic_hash
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


def _encode_flow(flow: FlowDefinition) -> str:
    return json.dumps(
        flow.model_dump(mode="json", by_alias=True, exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _flow_with_revision(flow: FlowDefinition, revision: int) -> FlowDefinition:
    definition = flow.model_dump(mode="json", by_alias=True, exclude_none=True)
    definition["revision"] = revision
    return FlowDefinition.model_validate(definition)


def _same_flow_semantics(definition: object, flow: FlowDefinition) -> bool:
    if not isinstance(definition, dict):
        return False
    stored = dict(definition)
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
