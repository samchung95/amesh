from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Sequence

from sqlalchemy.exc import DBAPIError

from amesh.adapters.postgres import (
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresReconciliationRepository,
    PostgresSchedulerRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
    PostgresWorkerRepository,
)
from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.domain import ServiceLiveness, ServiceRole, ServiceState
from amesh.observability import configure_structured_logging
from amesh.plugins import TrustedPluginRuntime, build_plugin_catalog, build_trusted_runtime
from amesh.ports import ServiceFenceError, WorkerLossPolicy
from amesh.service_runtime import RegisteredService, service_instance_name
from amesh.worker import (
    backfill_once,
    process_execution_checks_once,
    process_trigger_occurrences_once,
    reconcile_once,
    recover_once,
    schedule_once,
)

LOGGER = logging.getLogger("amesh.role")


async def _run_cycle(
    role: ServiceRole,
    settings: Settings,
    tenant_ids: Sequence[str],
    *,
    service: RegisteredService,
    executions: PostgresExecutionRepository,
    scheduler: PostgresSchedulerRepository,
    backfills: PostgresBackfillRepository,
    reconciliations: PostgresReconciliationRepository,
    workers: PostgresWorkerRepository,
    transport: PostgresDurableTransport,
    task_cache: PostgresTaskCacheRepository | None = None,
    shared_resources: PostgresSharedResourceRepository | None = None,
    trigger_runtime: PostgresTriggerRuntimeRepository | None = None,
    checks: PostgresCheckRepository | None = None,
    trusted_runtime: TrustedPluginRuntime | None = None,
) -> int:
    if role is ServiceRole.SCHEDULER:
        scheduled = await schedule_once(
            executions,
            scheduler,
            tenant_ids=tenant_ids,
            scheduler_id=service.instance.instance_id,
            trigger_runtime=trigger_runtime,
        )
        triggered = (
            await process_trigger_occurrences_once(
                executions,
                trigger_runtime,
                tenant_ids=tenant_ids,
                worker_id=service.instance.instance_id,
            )
            if trigger_runtime is not None
            else 0
        )
        check_work = (
            await process_execution_checks_once(
                executions,
                checks,
                tenant_ids=tenant_ids,
                worker_id=service.instance.instance_id,
            )
            if checks is not None
            else 0
        )
        return (
            scheduled
            + triggered
            + check_work
            + await backfill_once(
                executions,
                backfills,
                tenant_ids=tenant_ids,
            )
        )
    if role is ServiceRole.EXECUTOR:
        return await recover_once(
            executions,
            settings,
            tenant_ids=tenant_ids,
            task_cache=task_cache,
            shared_resources=shared_resources,
            trusted_runtime=trusted_runtime,
        )
    if role is ServiceRole.WORKER:
        return sum(
            [
                await workers.recover_expired_claims(
                    tenant_id=tenant_id,
                    policy=WorkerLossPolicy.REQUEUE,
                    limit=100,
                )
                for tenant_id in tenant_ids
            ]
        )
    if role is ServiceRole.INDEXER:
        return sum(
            [
                await transport.publish_outbox(tenant_id=tenant_id, limit=500)
                for tenant_id in tenant_ids
            ]
        )
    if role is ServiceRole.MAINTENANCE:
        return await reconcile_once(reconciliations, settings, tenant_ids=tenant_ids)
    raise ValueError(f"role {role.value!r} must run through amesh.server")


async def run_role(settings: Settings) -> None:
    role = ServiceRole(settings.service_role)
    if role is ServiceRole.WEBSERVER:
        raise ValueError("webserver role must run through python -m amesh.server")
    engine = create_database_engine(settings)
    registry = PostgresServiceRegistryRepository(
        engine,
        stale_after_seconds=settings.service_stale_after_seconds,
    )
    service = RegisteredService(registry, settings, role)
    executions = PostgresExecutionRepository(engine)
    scheduler = PostgresSchedulerRepository(engine)
    backfills = PostgresBackfillRepository(engine)
    reconciliations = PostgresReconciliationRepository(engine)
    tenants = PostgresTenantRepository(engine)
    workers = PostgresWorkerRepository(engine)
    transport = PostgresDurableTransport(engine)
    task_cache = PostgresTaskCacheRepository(engine)
    shared_resources = PostgresSharedResourceRepository(engine)
    trigger_runtime = PostgresTriggerRuntimeRepository(engine)
    checks = PostgresCheckRepository(engine)
    trusted_runtime = build_trusted_runtime(settings, build_plugin_catalog(settings))
    work_count = 0
    try:
        await service.register()
        while True:
            try:
                current = await service.heartbeat(
                    ownership={"lastCycleWork": work_count},
                    partitions={
                        "strategy": "postgresql-durable-partitions",
                        "workerGroup": settings.worker_group,
                    },
                    dependencies={"postgresql": "READY"},
                )
                if current.state is ServiceState.DRAINING:
                    break
                tenant_ids = await tenants.list_active_for_worker_group(settings.worker_group)
                work_count = await _run_cycle(
                    role,
                    settings,
                    tenant_ids,
                    service=service,
                    executions=executions,
                    scheduler=scheduler,
                    backfills=backfills,
                    reconciliations=reconciliations,
                    workers=workers,
                    transport=transport,
                    task_cache=task_cache,
                    shared_resources=shared_resources,
                    trigger_runtime=trigger_runtime,
                    checks=checks,
                    trusted_runtime=trusted_runtime,
                )
            except (DBAPIError, OSError):
                LOGGER.exception("service role cycle interrupted; retrying")
            await asyncio.sleep(settings.service_cycle_seconds)
    finally:
        await trusted_runtime.stop()
        await service.stop()
        await engine.dispose()


async def check_readiness(settings: Settings) -> bool:
    role = ServiceRole(settings.service_role)
    engine = create_database_engine(settings)
    try:
        topology = await PostgresServiceRegistryRepository(
            engine,
            stale_after_seconds=settings.service_stale_after_seconds,
        ).topology()
        return any(
            instance.role is role
            and instance.instance_name == service_instance_name(settings)
            and instance.liveness is ServiceLiveness.LIVE
            and instance.state is ServiceState.READY
            for instance in topology.instances
        )
    finally:
        await engine.dispose()


async def request_self_drain(settings: Settings) -> bool:
    role = ServiceRole(settings.service_role)
    engine = create_database_engine(settings)
    try:
        repository = PostgresServiceRegistryRepository(
            engine,
            stale_after_seconds=settings.service_stale_after_seconds,
        )
        topology = await repository.topology()
        instance = next(
            (
                item
                for item in topology.instances
                if item.role is role
                and item.instance_name == service_instance_name(settings)
                and item.state is not ServiceState.STOPPED
            ),
            None,
        )
        if instance is None:
            return False
        for _ in range(3):
            try:
                await repository.request_drain(
                    instance.instance_id,
                    expected_version=instance.resource_version,
                    actor_id="system:kubernetes-prestop",
                    reason="graceful service termination",
                )
                return True
            except ServiceFenceError:
                try:
                    instance = await repository.get(instance.instance_id)
                except LookupError:
                    return False
                if instance.state is ServiceState.STOPPED:
                    return False
        return False
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or inspect one AMESH service role")
    parser.add_argument("--config", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--set", action="append", help=argparse.SUPPRESS)
    parser.add_argument("--check", choices=("liveness", "readiness"))
    parser.add_argument("--drain", action="store_true")
    args = parser.parse_args()
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    if args.check == "liveness":
        return
    if args.check == "readiness":
        raise SystemExit(0 if asyncio.run(check_readiness(settings)) else 1)
    if args.drain:
        raise SystemExit(0 if asyncio.run(request_self_drain(settings)) else 1)
    asyncio.run(run_role(settings))


if __name__ == "__main__":
    main()
