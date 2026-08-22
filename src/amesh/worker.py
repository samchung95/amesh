from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from time import monotonic
from uuid import UUID

from sqlalchemy.exc import DBAPIError

from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.kubernetes import ProfiledKubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresExecutionRepository,
    PostgresReconciliationRepository,
    PostgresSchedulerRepository,
    PostgresSharedResourceRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
)
from amesh.backfills import BackfillService
from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.domain import (
    ExecutionState,
    ReconciliationMode,
    ReconciliationRequest,
    new_runtime_id,
)
from amesh.domain.runner import RunnerId, RunnerPolicySet
from amesh.dsl import compile_execution_tasks
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
from amesh.observability import configure_structured_logging
from amesh.plugins import (
    IsolatedPluginRuntime,
    TrustedPluginRuntime,
    build_isolated_runtime,
    build_plugin_catalog,
    build_trusted_runtime,
)
from amesh.ports import (
    CheckRepository,
    ExecutionLaunchSource,
    ReconciliationAlreadyRunningError,
    TaskCacheRepository,
    TriggerRuntimeRepository,
)
from amesh.reconciliation import ReconciliationService
from amesh.scheduler import CronScheduler
from amesh.storage.factory import build_object_store
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler
from amesh.workflow.shared_resources import SharedResourceContextProvider
from amesh.workflow.working_directory import WorkingDirectoryManager

LOGGER = logging.getLogger("amesh.worker")


async def schedule_once(
    repository: PostgresExecutionRepository,
    scheduler_repository: PostgresSchedulerRepository,
    *,
    tenant_ids: Sequence[str],
    scheduler_id: UUID,
    now: datetime | None = None,
    trigger_runtime: TriggerRuntimeRepository | None = None,
) -> int:
    scheduler = CronScheduler(
        repository,
        scheduler_repository,
        owner_id=scheduler_id,
        trigger_runtime=trigger_runtime,
    )
    scheduled_at = now or await scheduler_repository.database_time()
    scheduled = 0
    for tenant_id in tenant_ids:
        for persisted_flow in await repository.list_flows(tenant_id=tenant_id):
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
            except Exception:
                LOGGER.exception(
                    "scheduled flow evaluation failed; continuing",
                    extra={
                        "tenant_id": tenant_id,
                        "namespace": persisted_flow.namespace,
                        "flow_id": persisted_flow.flow_id,
                    },
                )
    return scheduled


async def process_trigger_occurrences_once(
    repository: PostgresExecutionRepository,
    trigger_runtime: TriggerRuntimeRepository,
    *,
    tenant_ids: Sequence[str],
    worker_id: UUID,
    limit: int = 100,
) -> int:
    """Launch accepted non-temporal occurrences with fenced retry/dead-letter handling."""

    processed = 0
    for tenant_id in tenant_ids:
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
                    },
                    launch_source=ExecutionLaunchSource.EVENT,
                    idempotency_key=(
                        f"trigger:{occurrence.trigger_definition_id}:{occurrence.occurrence_key}"
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


async def process_execution_checks_once(
    repository: PostgresExecutionRepository,
    checks: CheckRepository,
    *,
    tenant_ids: Sequence[str],
    worker_id: UUID,
    limit: int = 100,
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


async def recover_once(
    repository: PostgresExecutionRepository,
    settings: Settings,
    *,
    tenant_ids: Sequence[str],
    task_cache: TaskCacheRepository | None = None,
    shared_resources: PostgresSharedResourceRepository | None = None,
    trusted_runtime: TrustedPluginRuntime | None = None,
    isolated_runtime: IsolatedPluginRuntime | None = None,
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
            selected_runners = required_runner_ids(
                (node.task for node in compile_execution_tasks(flow)),
                runner_policy,
                namespace=flow.namespace,
                fallback=fallback_runner,
                available=frozenset(available_runners),
            )
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
            handlers = {
                "core.shell": shell_handler,
                "core.http": core_http_handler(),
                "agent.llm": agent_llm_handler(),
                "agent.mcp": agent_mcp_handler(),
            }
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
            executor = InProcessExecutor(
                repository,
                handlers=handlers,
                recover_running_types=frozenset({"core.shell"}),
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


async def backfill_once(
    repository: PostgresExecutionRepository,
    backfill_repository: PostgresBackfillRepository,
    *,
    tenant_ids: Sequence[str],
) -> int:
    service = BackfillService(repository, backfill_repository)
    processed = 0
    for tenant_id in tenant_ids:
        processed += await service.process_active(tenant_id=tenant_id)
    return processed


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
    repository = PostgresExecutionRepository(engine)
    scheduler_repository = PostgresSchedulerRepository(engine)
    trigger_runtime = PostgresTriggerRuntimeRepository(engine)
    checks = PostgresCheckRepository(engine)
    backfill_repository = PostgresBackfillRepository(engine)
    reconciliation_repository = PostgresReconciliationRepository(engine)
    shared_resources = PostgresSharedResourceRepository(engine)
    tenant_repository = PostgresTenantRepository(engine)
    next_reconciliation_at = 0.0
    plugin_catalog = build_plugin_catalog(settings)
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
                )
                await process_trigger_occurrences_once(
                    repository,
                    trigger_runtime,
                    tenant_ids=tenant_ids,
                    worker_id=worker_uuid,
                )
                await process_execution_checks_once(
                    repository,
                    checks,
                    tenant_ids=tenant_ids,
                    worker_id=worker_uuid,
                )
                await backfill_once(
                    repository,
                    backfill_repository,
                    tenant_ids=tenant_ids,
                )
                await recover_once(
                    repository,
                    settings,
                    tenant_ids=tenant_ids,
                    shared_resources=shared_resources,
                    trusted_runtime=trusted_runtime,
                    isolated_runtime=isolated_runtime,
                )
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
    configure_structured_logging(settings.log_level)
    asyncio.run(run_worker(settings))


if __name__ == "__main__":
    main()
