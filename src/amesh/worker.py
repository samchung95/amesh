from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from time import monotonic
from uuid import UUID

from sqlalchemy.exc import DBAPIError

from amesh.adapters.agent_session_registry import create_agent_session_harness
from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.kubernetes import ProfiledKubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresAgentMemoryRepository,
    PostgresAgentPrimitiveRepository,
    PostgresAgentResourceRepository,
    PostgresAgentSessionRepository,
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresExecutionRepository,
    PostgresHumanTaskRepository,
    PostgresOperationalControlRepository,
    PostgresPluginPolicyRepository,
    PostgresReconciliationRepository,
    PostgresSchedulerRepository,
    PostgresSharedResourceRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.admission_policy import AdmissionPolicyService
from amesh.backfills import BackfillService
from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.domain import (
    ExecutionState,
    FlowLifecycle,
    OperationalBoundary,
    PolicyDecision,
    PolicyStage,
    ReconciliationMode,
    ReconciliationRequest,
    RunningWorkPolicy,
    new_runtime_id,
)
from amesh.domain.runner import RunnerId, RunnerPolicySet
from amesh.dsl import FlowDefinition, TaskDefinition, compile_execution_tasks
from amesh.executor import (
    InProcessExecutor,
    TaskHandler,
    docker_container_handler,
    execution_lifecycle_pending,
    kubernetes_job_handler,
    local_process_handler,
    required_runner_ids,
    selecting_runner_handler,
)
from amesh.human_tasks import HumanTaskService, approval_task_handler
from amesh.model_continuations import configured_model_continuation_protector
from amesh.observability import (
    configure_observability,
    instrument_async_operation,
    shutdown_observability,
)
from amesh.plugin_sdk import PluginResolver
from amesh.plugins import (
    IsolatedPluginRuntime,
    PluginPolicyService,
    TrustedPluginRuntime,
    build_isolated_runtime,
    build_plugin_catalog,
    build_trusted_runtime,
)
from amesh.ports import (
    AgentMemoryRepository,
    AgentPrimitiveRepository,
    AgentResourceRepository,
    AgentSessionRepository,
    CheckRepository,
    ExecutionInterventionAction,
    ExecutionLaunchSource,
    PersistedExecution,
    PersistedTaskRun,
    ReconciliationAlreadyRunningError,
    TaskCacheRepository,
    TriggerRuntimeRepository,
)
from amesh.reconciliation import ReconciliationService
from amesh.scheduler import CronScheduler
from amesh.storage.factory import build_object_store
from amesh.tasks import (
    SCRIPT_TASK_TYPES,
    HttpTaskPolicy,
    agent_llm_handler,
    agent_mcp_handler,
    agent_mesh_handlers,
    agent_session_handler,
    core_utility_handlers,
    script_task_handlers,
)
from amesh.workflow.shared_resources import SharedResourceContextProvider
from amesh.workflow.working_directory import WorkingDirectoryManager

LOGGER = logging.getLogger("amesh.worker")


class ScheduleCycleError(RuntimeError):
    def __init__(self, *, scheduled: int, failures: Sequence[str]) -> None:
        self.scheduled = scheduled
        self.failures = tuple(failures)
        preview = "; ".join(self.failures[:3])
        suffix = f"; and {len(self.failures) - 3} more" if len(self.failures) > 3 else ""
        super().__init__(
            f"schedule cycle launched {scheduled} execution(s) but "
            f"{len(self.failures)} flow evaluation(s) failed: {preview}{suffix}"
        )


@instrument_async_operation("scheduler", "schedule")
async def schedule_once(
    repository: PostgresExecutionRepository,
    scheduler_repository: PostgresSchedulerRepository,
    *,
    tenant_ids: Sequence[str],
    scheduler_id: UUID,
    now: datetime | None = None,
    trigger_runtime: TriggerRuntimeRepository | None = None,
    operational_controls: PostgresOperationalControlRepository | None = None,
) -> int:
    scheduler = CronScheduler(
        repository,
        scheduler_repository,
        owner_id=scheduler_id,
        trigger_runtime=trigger_runtime,
        operational_controls=operational_controls,
    )
    scheduled_at = now or await scheduler_repository.database_time()
    scheduled = 0
    failures: list[str] = []
    for tenant_id in tenant_ids:
        for persisted_flow in await repository.list_flows(tenant_id=tenant_id):
            if persisted_flow.lifecycle is not FlowLifecycle.ACTIVE:
                continue
            flow = await repository.get_flow(
                persisted_flow.namespace,
                persisted_flow.flow_id,
                tenant_id=tenant_id,
            )
            try:
                scheduled += len(
                    await scheduler.fire_due_occurrences(
                        flow,
                        at=scheduled_at,
                        tenant_id=tenant_id,
                    )
                )
            except (DBAPIError, OSError):
                raise
            except Exception as exc:
                failures.append(
                    f"{tenant_id}/{persisted_flow.namespace}/{persisted_flow.flow_id}: "
                    f"{type(exc).__name__}: {exc}"
                )
    if failures:
        raise ScheduleCycleError(scheduled=scheduled, failures=failures)
    return scheduled


@instrument_async_operation("scheduler", "triggers")
async def process_trigger_occurrences_once(
    repository: PostgresExecutionRepository,
    trigger_runtime: TriggerRuntimeRepository,
    *,
    tenant_ids: Sequence[str],
    worker_id: UUID,
    limit: int = 100,
    operational_controls: PostgresOperationalControlRepository | None = None,
) -> int:
    """Launch accepted non-temporal occurrences with fenced retry/dead-letter handling."""

    processed = 0
    for tenant_id in tenant_ids:
        if operational_controls is not None:
            tenant_decision = await operational_controls.evaluate(
                OperationalBoundary.TRIGGERS,
                tenant_id=tenant_id,
                component_id=f"scheduler:{worker_id}",
                component_role="SCHEDULER",
            )
            if tenant_decision.blocked:
                continue
        claimed = await trigger_runtime.claim_due_occurrences(
            tenant_id=tenant_id,
            owner_id=worker_id,
            lease_duration=timedelta(seconds=30),
            limit=limit,
        )
        for occurrence in claimed:
            retry_delay = timedelta(seconds=30)
            try:
                flow = await repository.get_flow(
                    occurrence.namespace,
                    occurrence.flow_id,
                    tenant_id=tenant_id,
                    revision=occurrence.flow_revision,
                )
                trigger = next(item for item in flow.triggers if item.id == occurrence.trigger_id)
                retry_delay = trigger.retry_delay
                if operational_controls is not None:
                    decisions = [
                        await operational_controls.evaluate(
                            boundary,
                            tenant_id=tenant_id,
                            namespace=flow.namespace,
                            flow_id=flow.id,
                            component_id=f"scheduler:{worker_id}",
                            component_role="SCHEDULER",
                        )
                        for boundary in (
                            OperationalBoundary.TRIGGERS,
                            OperationalBoundary.NEW_EXECUTIONS,
                        )
                    ]
                    if any(decision.blocked for decision in decisions):
                        await trigger_runtime.defer_occurrence(
                            occurrence.occurrence_id,
                            tenant_id=tenant_id,
                            owner_id=worker_id,
                            fencing_token=occurrence.fencing_token,
                            reason="occurrence deferred by operational control",
                            retry_delay=retry_delay,
                        )
                        continue
                execution = await repository.create_execution(
                    flow,
                    tenant_id=tenant_id,
                    inputs=trigger.inputs or occurrence.payload,
                    trigger={
                        **occurrence.payload,
                        **occurrence.metadata,
                        "id": trigger.id,
                        "type": trigger.type,
                        "occurrenceId": str(occurrence.occurrence_id),
                        "occurrenceKey": occurrence.occurrence_key,
                        "payload": occurrence.payload,
                        **(
                            {
                                "date": occurrence.metadata.get("observedAt"),
                                "timezone": trigger.timezone,
                            }
                            if occurrence.trigger_type in {"core.cron", "core.interval"}
                            else {}
                        ),
                    },
                    launch_source=(
                        ExecutionLaunchSource.SCHEDULED
                        if occurrence.trigger_type in {"core.cron", "core.interval"}
                        else ExecutionLaunchSource.EVENT
                    ),
                    idempotency_key=(
                        occurrence.occurrence_key
                        if occurrence.trigger_type in {"core.cron", "core.interval"}
                        else (
                            f"trigger:{occurrence.trigger_definition_id}:"
                            f"{occurrence.occurrence_key}"
                        )
                    ),
                    actor_id="system:trigger-worker",
                )
                await trigger_runtime.complete_occurrence(
                    occurrence.occurrence_id,
                    tenant_id=tenant_id,
                    owner_id=worker_id,
                    fencing_token=occurrence.fencing_token,
                    execution_id=execution.execution_id,
                    evidence={
                        "decision": "launched",
                        "reason": "occurrence created an execution",
                    },
                )
                processed += 1
            except Exception as exc:
                await trigger_runtime.fail_occurrence(
                    occurrence.occurrence_id,
                    tenant_id=tenant_id,
                    owner_id=worker_id,
                    fencing_token=occurrence.fencing_token,
                    error=str(exc),
                    retry_delay=retry_delay,
                )
    return processed


@instrument_async_operation("scheduler", "checks")
async def process_execution_checks_once(
    repository: PostgresExecutionRepository,
    checks: CheckRepository,
    *,
    tenant_ids: Sequence[str],
    worker_id: UUID,
    limit: int = 100,
    operational_controls: PostgresOperationalControlRepository | None = None,
) -> int:
    """Evaluate due checks and execute their bounded durable actions."""

    processed = 0
    for tenant_id in tenant_ids:
        processed += await checks.process_due_checks(tenant_id=tenant_id, limit=limit)
        actions = await checks.claim_actions(
            tenant_id=tenant_id,
            owner_id=worker_id,
            lease_duration=timedelta(seconds=30),
            limit=limit,
        )
        for action in actions:
            try:
                if action.action_type == "NOTIFY":
                    await checks.publish_notification(action, tenant_id=tenant_id)
                    evidence = {
                        "decision": "notified",
                        "channel": action.channel,
                    }
                elif action.action_type == "RUN_FLOW":
                    if action.target_namespace is None or action.target_flow_id is None:
                        raise ValueError("RUN_FLOW check action has no target")
                    flow = await repository.get_flow(
                        action.target_namespace,
                        action.target_flow_id,
                        tenant_id=tenant_id,
                    )
                    if operational_controls is not None:
                        decision = await operational_controls.evaluate(
                            OperationalBoundary.NEW_EXECUTIONS,
                            tenant_id=tenant_id,
                            namespace=flow.namespace,
                            flow_id=flow.id,
                            component_id=f"scheduler:{worker_id}",
                            component_role="SCHEDULER",
                        )
                        if decision.blocked:
                            raise RuntimeError("check flow launch blocked by operational control")
                    execution = await repository.create_execution(
                        flow,
                        tenant_id=tenant_id,
                        inputs=action.payload,
                        trigger={
                            "id": "check-action",
                            "type": "core.check",
                            "evaluationId": str(action.evaluation_id),
                            "sourceExecutionId": (
                                str(action.execution_id) if action.execution_id else None
                            ),
                            "checkPolicyDepth": action.policy_depth + 1,
                        },
                        launch_source=ExecutionLaunchSource.EVENT,
                        idempotency_key=f"check-action:{action.action_id}",
                        actor_id="system:check-worker",
                    )
                    evidence = {
                        "decision": "flow-launched",
                        "executionId": str(execution.execution_id),
                    }
                else:
                    raise ValueError(f"unsupported check action {action.action_type!r}")
                await checks.complete_action(
                    action.action_id,
                    tenant_id=tenant_id,
                    owner_id=worker_id,
                    fencing_token=action.fencing_token,
                    evidence=evidence,
                )
                processed += 1
            except Exception as exc:
                await checks.fail_action(
                    action.action_id,
                    tenant_id=tenant_id,
                    owner_id=worker_id,
                    fencing_token=action.fencing_token,
                    error=str(exc),
                    retry_delay=timedelta(seconds=30),
                )
    return processed


@instrument_async_operation("executor", "recover")
async def recover_once(
    repository: PostgresExecutionRepository,
    settings: Settings,
    *,
    tenant_ids: Sequence[str],
    task_cache: TaskCacheRepository | None = None,
    shared_resources: PostgresSharedResourceRepository | None = None,
    human_tasks: PostgresHumanTaskRepository | None = None,
    trusted_runtime: TrustedPluginRuntime | None = None,
    isolated_runtime: IsolatedPluginRuntime | None = None,
    operational_controls: PostgresOperationalControlRepository | None = None,
    agent_primitives: AgentPrimitiveRepository | None = None,
    agent_resources: AgentResourceRepository | None = None,
    agent_sessions: AgentSessionRepository | None = None,
    agent_memory: AgentMemoryRepository | None = None,
) -> int:
    now = datetime.now(UTC)
    recovered = 0
    for tenant_id in tenant_ids:
        for execution in await repository.list_executions(tenant_id=tenant_id, limit=1000):
            age = (now - execution.updated_at).total_seconds()
            if age < settings.worker_recovery_grace_seconds:
                continue
            flow = await repository.get_flow(
                execution.namespace,
                execution.flow_id,
                tenant_id=tenant_id,
                revision=execution.flow_revision,
            )
            if execution.state is not ExecutionState.RUNNING:
                task_runs = await repository.list_task_runs(
                    execution.execution_id,
                    tenant_id=tenant_id,
                )
                if not execution_lifecycle_pending(flow, execution, task_runs):
                    continue
            kubernetes_runner: ProfiledKubernetesJobRunner | None = None
            object_store = build_object_store(settings)
            workspace_manager = WorkingDirectoryManager(object_store)
            runner_policy = RunnerPolicySet(settings.runner_policies)
            fallback_runner = RunnerId(settings.execution_runner_mode)
            available_runners = {RunnerId.KUBERNETES}
            if settings.is_local_process_runner_enabled:
                available_runners.add(RunnerId.LOCAL)
            if settings.docker_runner_enabled:
                available_runners.add(RunnerId.DOCKER)
            planned_tasks = compile_execution_tasks(flow)
            selected_runners = required_runner_ids(
                (node.task for node in planned_tasks),
                runner_policy,
                namespace=flow.namespace,
                fallback=fallback_runner,
                available=frozenset(available_runners),
            )
            if operational_controls is not None:
                decision = await operational_controls.evaluate(
                    OperationalBoundary.WORKER_DISPATCH,
                    tenant_id=tenant_id,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    plugin_ids=tuple(node.task.type for node in planned_tasks),
                    runner_ids=tuple(runner.value for runner in selected_runners),
                    component_id="executor:recovery",
                    component_role="EXECUTOR",
                )
                if decision.blocked:
                    if decision.running_work_policy is RunningWorkPolicy.CONTINUE:
                        pass
                    elif decision.running_work_policy is RunningWorkPolicy.CANCEL:
                        await repository.apply_execution_intervention(
                            execution.execution_id,
                            ExecutionInterventionAction.FORCE_CANCEL,
                            tenant_id=tenant_id,
                            expected_version=execution.version,
                            expected_epoch=execution.epoch,
                            actor_id="system:operational-control",
                            reason=(
                                "cancelled by operational control "
                                + ",".join(str(control.control_id) for control in decision.controls)
                            ),
                        )
                        continue
                    else:
                        continue
            runner_handlers: dict[RunnerId, TaskHandler] = {}
            docker_runner: DockerContainerRunner | None = None
            if RunnerId.LOCAL in selected_runners:
                runner_handlers[RunnerId.LOCAL] = local_process_handler(
                    LocalProcessRunner(),
                    workspace_manager,
                    namespace=flow.namespace,
                )
            if RunnerId.DOCKER in selected_runners:
                docker_runner = DockerContainerRunner(
                    endpoint=settings.docker_runner_endpoint,
                    image_policy=settings.docker_image_policy,
                    signature_command=settings.docker_signature_verification_command,
                    vulnerability_command=settings.docker_vulnerability_verification_command,
                )
                runner_handlers[RunnerId.DOCKER] = docker_container_handler(
                    docker_runner,
                    workspace_manager,
                    namespace=flow.namespace,
                )
            if RunnerId.KUBERNETES in selected_runners:
                kubernetes_runner = ProfiledKubernetesJobRunner(
                    settings.effective_kubernetes_runner_profiles
                )
                runner_handlers[RunnerId.KUBERNETES] = kubernetes_job_handler(
                    kubernetes_runner,
                    workspace_manager,
                    namespace=flow.namespace,
                )
            shell_handler = selecting_runner_handler(
                runner_handlers,
                runner_policy,
                namespace=flow.namespace,
                fallback=fallback_runner,
            )
            http_policy = HttpTaskPolicy(
                allowed_hosts=settings.network_egress_allowed_hosts,
                allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
                maximum_response_bytes=settings.core_http_max_response_bytes,
                maximum_pages=settings.core_http_max_pages,
                maximum_redirects=settings.core_http_max_redirects,
                http_proxy_url=(
                    settings.network_http_proxy_url.get_secret_value()
                    if settings.network_http_proxy_url is not None
                    else None
                ),
                https_proxy_url=(
                    settings.network_https_proxy_url.get_secret_value()
                    if settings.network_https_proxy_url is not None
                    else None
                ),
                no_proxy=settings.network_no_proxy,
                ca_file=settings.network_outbound_ca_file,
                client_certificate_file=settings.network_outbound_client_certificate_file,
                client_key_file=settings.network_outbound_client_key_file,
            )
            model_handler = agent_llm_handler(
                http_policy=http_policy,
                repository=agent_primitives,
                continuation_protector=configured_model_continuation_protector(
                    primary_key_id=settings.model_continuation_key_id,
                    primary_key=settings.model_continuation_encryption_key,
                    previous_key_id=settings.model_continuation_previous_key_id,
                    previous_key=settings.model_continuation_previous_encryption_key,
                ),
            )
            mcp_handler = agent_mcp_handler(
                repository=agent_primitives,
                http_policy=http_policy,
            )
            handlers = {
                "core.shell": shell_handler,
                **{
                    task_type: model_handler
                    for task_type in (
                        "agent.llm",
                        "agent.chat",
                        "agent.embedding",
                        "agent.structured",
                        "agent.toolCall",
                    )
                },
                "agent.mcp": mcp_handler,
                **core_utility_handlers(workspace_manager, http_policy=http_policy),
                **script_task_handlers(shell_handler, settings.script_task_policy),
            }
            if agent_resources is not None and agent_sessions is not None:
                handlers.update(agent_mesh_handlers(agent_resources))
                handlers["agent.session"] = agent_session_handler(
                    resources=agent_resources,
                    sessions=agent_sessions,
                    model_handler=model_handler,
                    mcp_handler=mcp_handler,
                    harness=create_agent_session_harness(
                        settings.agent_session_harness,
                        settings.agent_session_pi_worker_command,
                        max_frame_bytes=settings.agent_session_max_frame_bytes,
                    ),
                    memory=agent_memory,
                )
            if human_tasks is not None:
                handlers["core.approval"] = approval_task_handler(
                    human_tasks,
                    repository,
                    token_pepper=settings.amesh_token_pepper.get_secret_value(),
                )
            if settings.trusted_plugin_approvals or settings.isolated_plugin_services:
                revisions = await repository.list_flow_revisions(
                    execution.namespace,
                    execution.flow_id,
                    tenant_id=tenant_id,
                )
                revision = next(
                    (item for item in revisions if item.revision == execution.flow_revision),
                    None,
                )
                if revision is None:
                    raise RuntimeError(
                        f"flow revision {execution.flow_revision} plugin resolution is unavailable"
                    )
                plugin_handlers: dict[str, TaskHandler] = {}
                if settings.trusted_plugin_approvals:
                    if trusted_runtime is None:
                        raise RuntimeError("trusted plugin approvals require a configured runtime")
                    await trusted_runtime.ensure_started()
                    plugin_handlers.update(
                        trusted_runtime.task_handlers(revision.plugin_resolution)
                    )
                if settings.isolated_plugin_services:
                    if isolated_runtime is None:
                        raise RuntimeError("isolated plugin services require a configured runtime")
                    await isolated_runtime.ensure_configured()
                    for task_type, handler in isolated_runtime.task_handlers(
                        revision.plugin_resolution
                    ).items():
                        if task_type in plugin_handlers:
                            raise RuntimeError(
                                f"plugin task identity {task_type!r} has multiple runtime owners"
                            )
                        plugin_handlers[task_type] = handler
                for task_type, handler in plugin_handlers.items():
                    if task_type in handlers:
                        raise RuntimeError(
                            f"plugin task identity {task_type!r} conflicts with a core task"
                        )
                    handlers[task_type] = handler

            async def enforce_dispatch_policy(
                dispatch_flow: FlowDefinition,
                dispatch_execution: PersistedExecution,
                task_run: PersistedTaskRun,
                task: TaskDefinition,
            ) -> PolicyDecision:
                return await repository.enforce_admission_policy(
                    dispatch_flow,
                    tenant_id=dispatch_execution.tenant_id,
                    stage=PolicyStage.DISPATCH,
                    actor_id=dispatch_execution.created_by,
                    inputs=dict(dispatch_execution.inputs),
                    task=task,
                    execution_id=dispatch_execution.execution_id,
                    task_run_id=task_run.task_run_id,
                )

            executor = InProcessExecutor(
                repository,
                handlers=handlers,
                recover_running_types=frozenset(
                    {"core.shell", "agent.session", *SCRIPT_TASK_TYPES}
                ),
                context_provider=(
                    SharedResourceContextProvider(
                        shared_resources,
                        object_store=object_store,
                    )
                    if shared_resources is not None
                    else None
                ),
                object_store=object_store,
                task_cache=task_cache,
                workspace_manager=workspace_manager,
                dispatch_policy_enforcer=(
                    enforce_dispatch_policy if repository.has_admission_policy_enforcer else None
                ),
            )
            try:
                await executor.run_to_completion(
                    flow,
                    execution.execution_id,
                    tenant_id=tenant_id,
                )
                recovered += 1
                LOGGER.info(
                    "recovered execution",
                    extra={
                        "tenant_id": tenant_id,
                        "execution_id": str(execution.execution_id),
                    },
                )
            except Exception:
                LOGGER.exception(
                    "execution recovery failed",
                    extra={
                        "tenant_id": tenant_id,
                        "execution_id": str(execution.execution_id),
                    },
                )
            finally:
                if docker_runner is not None:
                    await asyncio.to_thread(docker_runner.close)
                if kubernetes_runner is not None:
                    await kubernetes_runner.close()
    return recovered


@instrument_async_operation("scheduler", "backfill")
async def backfill_once(
    repository: PostgresExecutionRepository,
    backfill_repository: PostgresBackfillRepository,
    *,
    tenant_ids: Sequence[str],
    operational_controls: PostgresOperationalControlRepository | None = None,
) -> int:
    service = BackfillService(repository, backfill_repository, operational_controls)
    processed = 0
    for tenant_id in tenant_ids:
        processed += await service.process_active(tenant_id=tenant_id)
    return processed


@instrument_async_operation("maintenance", "reconcile")
async def reconcile_once(
    repository: PostgresReconciliationRepository,
    settings: Settings,
    *,
    tenant_ids: Sequence[str],
) -> int:
    service = ReconciliationService(repository)
    bucket = datetime.now(UTC).replace(second=0, microsecond=0).isoformat()
    repaired = 0
    for tenant_id in tenant_ids:
        try:
            run = await service.run(
                ReconciliationRequest(
                    mode=ReconciliationMode.APPLY,
                    staleAfterSeconds=settings.worker_reconciliation_stuck_after_seconds,
                    maxFindings=min(settings.worker_reconciliation_max_repairs * 10, 1_000),
                    maxRepairs=settings.worker_reconciliation_max_repairs,
                    idempotencyKey=f"automatic:{bucket}",
                    reason="periodic durable-state reconciliation",
                ),
                tenant_id=tenant_id,
                actor_id="system:reconciler",
            )
        except ReconciliationAlreadyRunningError:
            continue
        repaired += run.repairs_applied
    return repaired


async def run_worker(settings: Settings) -> None:
    worker_uuid = new_runtime_id()
    worker_id = str(worker_uuid)
    engine = create_database_engine(settings)
    plugin_catalog = build_plugin_catalog(settings)
    plugin_policy = PluginPolicyService(
        PostgresPluginPolicyRepository(engine),
        plugin_catalog,
        default_allow=settings.plugin_trust_mode == "development",
    )
    admission_policy = AdmissionPolicyService(PostgresAdmissionPolicyRepository(engine))
    repository = PostgresExecutionRepository(
        engine,
        plugin_resolution_provider=lambda flow: (
            PluginResolver(plugin_catalog.snapshot).resolve_flow(flow).revision_payload()
        ),
        plugin_policy_enforcer=plugin_policy.enforce_flow,
        admission_policy_enforcer=admission_policy.enforce_repository,
    )
    scheduler_repository = PostgresSchedulerRepository(engine)
    trigger_runtime = PostgresTriggerRuntimeRepository(engine)
    checks = PostgresCheckRepository(engine)
    backfill_repository = PostgresBackfillRepository(engine)
    reconciliation_repository = PostgresReconciliationRepository(engine)
    shared_resources = PostgresSharedResourceRepository(engine)
    human_tasks = PostgresHumanTaskRepository(engine)
    operational_controls = PostgresOperationalControlRepository(engine)
    agent_primitives = PostgresAgentPrimitiveRepository(engine)
    agent_resources = PostgresAgentResourceRepository(engine)
    agent_sessions = PostgresAgentSessionRepository(engine)
    agent_memory = PostgresAgentMemoryRepository(engine)
    human_task_service = HumanTaskService(
        human_tasks,
        repository,
        token_pepper=settings.amesh_token_pepper.get_secret_value(),
    )
    tenant_repository = PostgresTenantRepository(engine)
    next_reconciliation_at = 0.0
    trusted_runtime = build_trusted_runtime(settings, plugin_catalog)
    isolated_runtime = build_isolated_runtime(settings, plugin_catalog)
    LOGGER.info("worker started", extra={"worker_id": worker_id})
    try:
        while True:
            try:
                tenant_ids = await tenant_repository.list_active_for_worker_group(
                    settings.worker_group
                )
                await schedule_once(
                    repository,
                    scheduler_repository,
                    tenant_ids=tenant_ids,
                    scheduler_id=worker_uuid,
                    trigger_runtime=trigger_runtime,
                    operational_controls=operational_controls,
                )
                await process_trigger_occurrences_once(
                    repository,
                    trigger_runtime,
                    tenant_ids=tenant_ids,
                    worker_id=worker_uuid,
                    operational_controls=operational_controls,
                )
                await process_execution_checks_once(
                    repository,
                    checks,
                    tenant_ids=tenant_ids,
                    worker_id=worker_uuid,
                    operational_controls=operational_controls,
                )
                await backfill_once(
                    repository,
                    backfill_repository,
                    tenant_ids=tenant_ids,
                    operational_controls=operational_controls,
                )
                await recover_once(
                    repository,
                    settings,
                    tenant_ids=tenant_ids,
                    shared_resources=shared_resources,
                    human_tasks=human_tasks,
                    trusted_runtime=trusted_runtime,
                    isolated_runtime=isolated_runtime,
                    operational_controls=operational_controls,
                    agent_primitives=agent_primitives,
                    agent_resources=agent_resources,
                    agent_sessions=agent_sessions,
                    agent_memory=agent_memory,
                )
                await operational_controls.acknowledge_active(
                    tenant_ids=tenant_ids,
                    component_id=worker_id,
                    component_role="WORKER",
                )
                for tenant_id in tenant_ids:
                    await human_task_service.reconcile(tenant_id=tenant_id)
                current_time = monotonic()
                if current_time >= next_reconciliation_at:
                    await reconcile_once(
                        reconciliation_repository,
                        settings,
                        tenant_ids=tenant_ids,
                    )
                    next_reconciliation_at = (
                        current_time + settings.worker_reconciliation_interval_seconds
                    )
            except (DBAPIError, OSError):
                LOGGER.exception(
                    "worker database cycle interrupted; retrying",
                    extra={"worker_id": worker_id},
                )
            await asyncio.sleep(settings.worker_poll_seconds)
    finally:
        await trusted_runtime.stop()
        await engine.dispose()


def main() -> None:
    settings = get_settings()
    configure_observability(settings.model_copy(update={"service_role": "worker"}))
    try:
        asyncio.run(run_worker(settings))
    finally:
        shutdown_observability()


if __name__ == "__main__":
    main()
