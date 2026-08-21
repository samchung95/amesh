from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.kubernetes import KubernetesJobRunner
from amesh.adapters.postgres import PostgresExecutionRepository, PostgresTenantRepository
from amesh.config import Settings, get_settings
from amesh.domain import ExecutionState, new_runtime_id
from amesh.executor import InProcessExecutor, kubernetes_job_handler
from amesh.observability import configure_structured_logging
from amesh.scheduler import CronScheduler
from amesh.tasks import agent_llm_handler, agent_mcp_handler, core_http_handler

LOGGER = logging.getLogger("amesh.worker")


async def schedule_once(
    repository: PostgresExecutionRepository,
    *,
    tenant_ids: Sequence[str],
    now: datetime | None = None,
) -> int:
    scheduler = CronScheduler(repository)
    scheduled_at = now or datetime.now(UTC)
    scheduled = 0
    for tenant_id in tenant_ids:
        for persisted_flow in await repository.list_flows(tenant_id=tenant_id):
            flow = await repository.get_flow(
                persisted_flow.namespace,
                persisted_flow.flow_id,
                tenant_id=tenant_id,
            )
            if flow.disabled:
                continue
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
            runner = KubernetesJobRunner.from_in_cluster(
                namespace=settings.kubernetes_task_namespace
            )
            executor = InProcessExecutor(
                repository,
                handlers={
                    "core.shell": kubernetes_job_handler(runner),
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
                await runner.close()
    return recovered


async def run_worker(settings: Settings) -> None:
    worker_id = str(new_runtime_id())
    engine = create_async_engine(settings.database_url)
    repository = PostgresExecutionRepository(engine)
    tenant_repository = PostgresTenantRepository(engine)
    LOGGER.info("worker started", extra={"worker_id": worker_id})
    try:
        while True:
            tenant_ids = await tenant_repository.list_active_for_worker_group(settings.worker_group)
            await schedule_once(repository, tenant_ids=tenant_ids)
            await recover_once(repository, settings, tenant_ids=tenant_ids)
            await asyncio.sleep(settings.worker_poll_seconds)
    finally:
        await engine.dispose()


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    asyncio.run(run_worker(settings))


if __name__ == "__main__":
    main()
