from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from time import monotonic
from uuid import UUID

from sqlalchemy.exc import DBAPIError

from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import (
    PostgresBackfillRepository,
    PostgresExecutionRepository,
    PostgresReconciliationRepository,
    PostgresSchedulerRepository,
    PostgresTenantRepository,
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
from amesh.executor import (
    InProcessExecutor,
    kubernetes_job_handler,
    local_process_handler,
)
from amesh.observability import configure_structured_logging
from amesh.ports import ReconciliationAlreadyRunningError
from amesh.reconciliation import ReconciliationService
from amesh.scheduler import CronScheduler
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler

LOGGER = logging.getLogger("amesh.worker")


async def schedule_once(
    repository: PostgresExecutionRepository,
    scheduler_repository: PostgresSchedulerRepository,
    *,
    tenant_ids: Sequence[str],
    scheduler_id: UUID,
    now: datetime | None = None,
) -> int:
    scheduler = CronScheduler(
        repository,
        scheduler_repository,
        owner_id=scheduler_id,
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
            scheduled += len(
                await scheduler.fire_due_occurrences(
                    flow,
                    at=scheduled_at,
                    tenant_id=tenant_id,
                )
            )
    return scheduled


async def recover_once(
    repository: PostgresExecutionRepository,
    settings: Settings,
    *,
    tenant_ids: Sequence[str],
) -> int:
    now = datetime.now(UTC)
    recovered = 0
    for tenant_id in tenant_ids:
        for execution in await repository.list_executions(tenant_id=tenant_id, limit=1000):
            age = (now - execution.updated_at).total_seconds()
            if (
                execution.state is not ExecutionState.RUNNING
                or age < settings.worker_recovery_grace_seconds
            ):
                continue
            flow = await repository.get_flow(
                execution.namespace,
                execution.flow_id,
                tenant_id=tenant_id,
            )
            kubernetes_runner: KubernetesJobRunner | None = None
            if settings.execution_runner_mode == "local":
                shell_handler = local_process_handler(LocalProcessRunner())
            else:
                kubernetes_runner = KubernetesJobRunner.from_in_cluster(
                    namespace=settings.kubernetes_task_namespace
                )
                shell_handler = kubernetes_job_handler(kubernetes_runner)
            executor = InProcessExecutor(
                repository,
                handlers={
                    "core.shell": shell_handler,
                    "core.http": core_http_handler(),
                    "agent.llm": agent_llm_handler(),
                    "agent.mcp": agent_mcp_handler(),
                },
                recover_running_types=frozenset({"core.shell"}),
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
    backfill_repository = PostgresBackfillRepository(engine)
    reconciliation_repository = PostgresReconciliationRepository(engine)
    tenant_repository = PostgresTenantRepository(engine)
    next_reconciliation_at = 0.0
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
                )
                await backfill_once(
                    repository,
                    backfill_repository,
                    tenant_ids=tenant_ids,
                )
                await recover_once(repository, settings, tenant_ids=tenant_ids)
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
        await engine.dispose()


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    asyncio.run(run_worker(settings))


if __name__ == "__main__":
    main()
