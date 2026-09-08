"""SQL authority for the execution_lifecycle_repository execution port."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection

from amesh.admission_policy import policy_decision_metadata
from amesh.determinism import admission_policy_pins, build_determinism_envelope
from amesh.domain import (
    AdmissionBehavior,
    AdmissionDecision,
    AdmissionOutcome,
    AdmissionResourceType,
    AdmissionScope,
    ExecutionEventType,
    ExecutionState,
    FlowLifecycle,
    PluginPolicyStage,
    PolicyDecision,
    PolicyStage,
    ResolvedAdmissionPolicy,
    TaskRunLifecyclePhase,
    TenantPolicy,
    TransitionRejectionCode,
    new_runtime_id,
    resolve_admission_policies,
)
from amesh.dsl import FlowDefinition, compile_execution_tasks
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports.errors import NotFoundError
from amesh.ports.execution_repository import (
    ExecutionLaunchSource,
    ExecutionLifecycleRepository,
    ExecutionStateConflictError,
    PersistedExecution,
    PersistedSubflow,
    SubflowLaunchContext,
)
from amesh.ports.tenant_repository import TenantQuotaExceeded, TenantUnavailableError
from amesh.workflow.data_contracts import (
    redact_matching_values,
    sensitive_execution_values,
    validate_flow_inputs,
)
from amesh.workflow.metadata import (
    execution_system_labels,
    flow_system_labels,
    task_system_labels,
)

from .check_repository import (
    evaluate_execution_terminal_checks,
    record_execution_check_start,
    synchronize_active_flow_checks,
)
from .execution_control_repository import _GET_EXECUTION
from .execution_port_base import PostgresExecutionPort
from .execution_rows import execution_from_row as _to_execution
from .execution_rows import (
    subflow_from_row as _to_subflow,
)
from .execution_shared import (
    _ACTIVATE_FLOW_REVISION,
    _DATABASE_TIME,
    _INSERT_EXECUTION_EVENT,
    _INSERT_TASK_RUN,
    _SELECT_FLOW_REVISION,
    _load_tenant_policy,
    _require_allowed_plugins,
)
from .trigger_runtime_repository import (
    emit_flow_completion_occurrences,
    synchronize_flow_trigger_runtime,
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


class PostgresExecutionLifecycleRepository(PostgresExecutionPort, ExecutionLifecycleRepository):
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
        trace_context: dict[str, str] | None = None,
    ) -> PersistedExecution:
        if subflow is not None and flow.revision != subflow.target_revision:
            raise ValueError("subflow target revision does not match the loaded flow revision")
        if idempotency_key is not None:
            existing = await self._existing_execution_by_idempotency(
                tenant_id,
                idempotency_key,
            )
            if existing is not None:
                return existing
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
        submission_trace_context = self._services.codec.dumps(trace_context or {})

        async with self._services.transactions.tenant(tenant_id) as (connection, scoped_tenant_id):
            execution_id = await self._create_execution_tx(
                connection,
                scoped_tenant_id,
                tenant_id,
                flow,
                execution_id,
                inputs,
                trigger,
                launch_source,
                idempotency_key,
                actor_id,
                labels,
                subflow,
                priority,
                policy_decision,
                submission_trace_context,
            )

        return await self.get_execution(execution_id, tenant_id=tenant_id)

    async def _seed_execution_task_runs(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        execution_id: UUID,
        flow: FlowDefinition,
        initial_state: ExecutionState,
        merged_labels: dict[str, str],
        actor_id: str,
        created_at: datetime,
        submission_trace_context: str,
    ) -> None:
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
                    "labels": self._services.codec.dumps(
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
                    "trace_context": submission_trace_context,
                }
            )
        if task_rows:
            await connection.execute(
                _INSERT_TASK_RUN,
                task_rows,
            )

    async def _record_creation_checks(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        execution_id: UUID,
        flow_revision_id: UUID,
        flow: FlowDefinition,
        initial_state: ExecutionState,
        created_at: datetime,
        inputs: dict[str, object],
        launch_context: dict[str, object],
        merged_labels: dict[str, str],
    ) -> None:
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

    async def _link_subflow(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        execution_id: UUID,
        subflow: SubflowLaunchContext,
        actor_id: str,
    ) -> None:
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
                "output_mapping": self._services.codec.dumps(subflow.output_mapping),
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

    async def _insert_execution_row(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        execution_id: UUID,
        flow_id: UUID,
        flow_revision_id: UUID,
        flow: FlowDefinition,
        initial_state: ExecutionState,
        initial_version: int,
        idempotency_key: str | None,
        inputs: dict[str, object],
        launch_context: dict[str, object],
        merged_labels: dict[str, str],
        actor_id: str,
        created_at: datetime,
    ) -> UUID | None:
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
                "inputs": self._services.codec.dumps(inputs),
                "trigger_context": self._services.codec.dumps(launch_context),
                "labels": self._services.codec.dumps(merged_labels),
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
        return UUID(str(inserted_execution_id)) if inserted_execution_id is not None else None

    def _prepare_launch_context(
        self,
        flow: FlowDefinition,
        tenant_id: str,
        execution_id: UUID,
        inputs: dict[str, object],
        trigger: dict[str, object] | None,
        policy_decision: PolicyDecision | None,
        exact_revision: RowMapping,
        labels: dict[str, str] | None,
        launch_source: ExecutionLaunchSource,
        policy: TenantPolicy,
    ) -> tuple[dict[str, object], dict[str, str], tuple[ResolvedAdmissionPolicy, ...]]:
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
        return launch_context, merged_labels, resolved_policies

    async def _resolve_launch_flow(
        self,
        connection: AsyncConnection,
        scoped_tenant_id: UUID,
        tenant_id: str,
        flow: FlowDefinition,
        actor_id: str,
        subflow: SubflowLaunchContext | None,
    ) -> tuple[UUID, UUID, UUID, FlowDefinition, RowMapping]:
        tenant_uuid, namespace_id = await self._repository._ensure_namespace(
            connection,
            tenant_id,
            flow.namespace,
            actor_id,
        )
        if tenant_uuid != scoped_tenant_id:
            raise TenantUnavailableError("tenant context changed during execution creation")
        flow_id = await self._repository._ensure_flow(
            connection,
            tenant_uuid,
            namespace_id,
            flow.id,
            actor_id,
        )
        flow_resource = await self._repository._flow_resource_row(
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
        flow_revision_id, stored_flow, _created = await self._repository._ensure_flow_revision(
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
            raise ValueError(f"flow {flow.namespace}.{flow.id} is disabled and cannot be executed")
        if subflow is None and flow_resource["active_revision"] is None:
            await connection.execute(
                _ACTIVATE_FLOW_REVISION,
                {
                    "tenant_id": tenant_uuid,
                    "flow_id": flow_id,
                    "revision": stored_flow.revision,
                    "status": (FlowLifecycle.ACTIVE.value),
                    "labels": self._services.codec.dumps(
                        {**stored_flow.labels, **flow_system_labels(stored_flow)}
                    ),
                    "annotations": self._services.codec.dumps(stored_flow.annotations),
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
        return tenant_uuid, flow_id, flow_revision_id, flow, exact_revision

    async def _create_execution_tx(
        self,
        connection: AsyncConnection,
        scoped_tenant_id: UUID,
        tenant_id: str,
        flow: FlowDefinition,
        execution_id: UUID,
        inputs: dict[str, object],
        trigger: dict[str, object] | None,
        launch_source: ExecutionLaunchSource,
        idempotency_key: str | None,
        actor_id: str,
        labels: dict[str, str] | None,
        subflow: SubflowLaunchContext | None,
        priority: int | None,
        policy_decision: PolicyDecision | None,
        submission_trace_context: str,
    ) -> UUID:
        policy = await self._check_launch_quota(connection, flow)
        (
            tenant_uuid,
            flow_id,
            flow_revision_id,
            flow,
            exact_revision,
        ) = await self._resolve_launch_flow(
            connection, scoped_tenant_id, tenant_id, flow, actor_id, subflow
        )
        launch_context, merged_labels, resolved_policies = self._prepare_launch_context(
            flow,
            tenant_id,
            execution_id,
            inputs,
            trigger,
            policy_decision,
            exact_revision,
            labels,
            launch_source,
            policy,
        )
        admission = await self._repository._request_admission_tx(
            connection,
            tenant_uuid,
            AdmissionResourceType.EXECUTION,
            execution_id,
            resolved_policies,
            flow.priority if priority is None else priority,
        )
        initial_state, initial_version = self._initial_execution_state(admission)
        created_at = await connection.scalar(_DATABASE_TIME)
        if not isinstance(created_at, datetime):
            raise TypeError("PostgreSQL returned an invalid database timestamp")
        inserted_execution_id = await self._insert_execution_row(
            connection,
            tenant_uuid,
            execution_id,
            flow_id,
            flow_revision_id,
            flow,
            initial_state,
            initial_version,
            idempotency_key,
            inputs,
            launch_context,
            merged_labels,
            actor_id,
            created_at,
        )
        if inserted_execution_id is None:
            if idempotency_key is None:
                raise RuntimeError("execution insert did not return an identity")
            existing_result = await connection.execute(
                _SELECT_EXECUTION_BY_IDEMPOTENCY,
                {"tenant_id": tenant_uuid, "idempotency_key": idempotency_key},
            )
            execution_id = UUID(str(existing_result.scalar_one()))
            await self._repository._release_admission_tx(
                connection,
                tenant_uuid,
                AdmissionResourceType.EXECUTION,
                admission.resource_id,
                "duplicate idempotency key",
            )
        else:
            execution_id = UUID(str(inserted_execution_id))
            await self._initialize_new_execution(
                connection,
                tenant_uuid,
                execution_id,
                flow_revision_id,
                flow,
                initial_state,
                merged_labels,
                actor_id,
                created_at,
                submission_trace_context,
                inputs,
                launch_context,
                admission,
            )

        if subflow is not None:
            await self._link_subflow(connection, tenant_uuid, execution_id, subflow, actor_id)
        return execution_id

    def _initial_execution_state(
        self,
        admission: AdmissionDecision,
    ) -> tuple[ExecutionState, int]:
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
        return initial_state, initial_version

    async def _check_launch_quota(
        self, connection: AsyncConnection, flow: FlowDefinition
    ) -> TenantPolicy:
        policy = await _load_tenant_policy(connection)
        _require_allowed_plugins(policy, flow)
        if not policy.feature_enabled("executions"):
            raise TenantQuotaExceeded("tenant execution feature is disabled")
        queued_count = int(
            await connection.scalar(text("SELECT count(*) FROM executions WHERE state = 'QUEUED'"))
            or 0
        )
        if queued_count >= policy.max_queued_executions:
            raise TenantQuotaExceeded("tenant queued execution quota exceeded")
        return policy

    async def _initialize_new_execution(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        execution_id: UUID,
        flow_revision_id: UUID,
        flow: FlowDefinition,
        initial_state: ExecutionState,
        merged_labels: dict[str, str],
        actor_id: str,
        created_at: datetime,
        submission_trace_context: str,
        inputs: dict[str, object],
        launch_context: dict[str, object],
        admission: AdmissionDecision,
    ) -> None:
        await self._insert_initial_events(
            connection,
            tenant_uuid,
            execution_id,
            created_at,
            actor_id,
            admission.outcome,
            admission.reason,
            submission_trace_context,
        )
        await self._seed_execution_task_runs(
            connection,
            tenant_uuid,
            execution_id,
            flow,
            initial_state,
            merged_labels,
            actor_id,
            created_at,
            submission_trace_context,
        )
        await self._record_creation_checks(
            connection,
            tenant_uuid,
            execution_id,
            flow_revision_id,
            flow,
            initial_state,
            created_at,
            inputs,
            launch_context,
            merged_labels,
        )

    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> PersistedExecution:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
            result = await connection.execute(
                _GET_EXECUTION,
                {"execution_id": execution_id, "tenant_slug": tenant_id},
            )
            row = result.mappings().one_or_none()
        if row is None:
            raise NotFoundError(
                "execution",
                execution_id,
                message=f"execution {execution_id} does not exist",
            )
        return _to_execution(row)

    async def list_executions(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> list[PersistedExecution]:
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
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
        async with self._services.transactions.tenant(tenant_id) as (connection, _tenant_uuid):
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
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
            recorded = await connection.scalar(
                _RECORD_EXECUTION_LIFECYCLE,
                {
                    "execution_id": execution_id,
                    "tenant_id": tenant_uuid,
                    "expected_epoch": expected_epoch,
                    "evidence": self._services.codec.dumps(evidence),
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

    async def list_subflows(
        self,
        execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedSubflow]:
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
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
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
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

    async def _existing_execution_by_idempotency(
        self,
        tenant_id: str,
        idempotency_key: str,
    ) -> PersistedExecution | None:
        """Resolve accepted retries before admission and tenant quota checks."""

        async with self._services.transactions.tenant(tenant_id) as (
            connection,
            scoped_tenant_id,
        ):
            result = await connection.execute(
                _SELECT_EXECUTION_BY_IDEMPOTENCY,
                {"tenant_id": scoped_tenant_id, "idempotency_key": idempotency_key},
            )
            execution_id = result.scalar_one_or_none()
        if execution_id is None:
            return None
        return await self.get_execution(UUID(str(execution_id)), tenant_id=tenant_id)

    async def _insert_initial_events(
        self,
        connection: AsyncConnection,
        tenant_id: UUID,
        execution_id: UUID,
        occurred_at: datetime,
        actor_id: str,
        outcome: AdmissionOutcome,
        reason: str,
        trace_context: str,
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
                    "trace_context": trace_context,
                }
            )
        await connection.execute(_INSERT_EXECUTION_EVENT, parameters)

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
        async with self._services.transactions.tenant(tenant_id) as (connection, tenant_uuid):
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
                    "payload": self._services.codec.dumps(payload),
                    "outputs": self._services.codec.dumps(outputs or {}),
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
                await self._repository._release_admission_tx(
                    connection,
                    tenant_uuid,
                    AdmissionResourceType.EXECUTION,
                    execution_id,
                    f"execution reached {state.value}",
                )
                await self._repository._reconcile_admission_tx(connection, tenant_uuid, limit=100)
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
                    await self._repository._record_rejection(
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
                    await self._repository._record_rejection(
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
