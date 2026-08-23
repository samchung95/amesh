from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Sequence
from contextlib import suppress

from opentelemetry import trace
from sqlalchemy.exc import DBAPIError

from amesh.adapters.postgres import (
    PostgresAdmissionPolicyRepository,
    PostgresBackfillRepository,
    PostgresCheckRepository,
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresOperationalControlRepository,
    PostgresPluginPolicyRepository,
    PostgresRealtimeRepository,
    PostgresReconciliationRepository,
    PostgresRetentionRepository,
    PostgresSchedulerRepository,
    PostgresSearchRepository,
    PostgresServiceRegistryRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
    PostgresWorkerRepository,
)
from amesh.admission_policy import AdmissionPolicyService
from amesh.config import Settings, get_settings
from amesh.database import create_database_engine
from amesh.domain import ServiceLiveness, ServiceRole, ServiceState
from amesh.observability import (
    WORKER_CAPACITY,
    configure_observability,
    instrument_async_operation,
    shutdown_observability,
)
from amesh.plugins import (
    PluginPolicyService,
    TrustedPluginRuntime,
    build_plugin_catalog,
    build_trusted_runtime,
)
from amesh.ports import SearchProjector, SearchUnavailableError, ServiceFenceError, WorkerLossPolicy
from amesh.realtime import WebhookDispatcher
from amesh.retention import RetentionService
from amesh.service_runtime import RegisteredService, service_instance_name
from amesh.storage.factory import build_object_store
from amesh.tasks import HttpTaskPolicy
from amesh.worker import (
    backfill_once,
    process_execution_checks_once,
    process_trigger_occurrences_once,
    reconcile_once,
    recover_once,
    schedule_once,
)

LOGGER = logging.getLogger("amesh.role")


@instrument_async_operation("service", "cycle")
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
    operational_controls: PostgresOperationalControlRepository,
    task_cache: PostgresTaskCacheRepository | None = None,
    shared_resources: PostgresSharedResourceRepository | None = None,
    trigger_runtime: PostgresTriggerRuntimeRepository | None = None,
    checks: PostgresCheckRepository | None = None,
    trusted_runtime: TrustedPluginRuntime | None = None,
    webhook_dispatcher: WebhookDispatcher | None = None,
    search_projector: SearchProjector | None = None,
    retention_service: RetentionService | None = None,
) -> int:
    trace.get_current_span().set_attribute("amesh.role", role.value)
    if role is ServiceRole.SCHEDULER:
        scheduled = await schedule_once(
            executions,
            scheduler,
            tenant_ids=tenant_ids,
            scheduler_id=service.instance.instance_id,
            trigger_runtime=trigger_runtime,
            operational_controls=operational_controls,
        )
        triggered = (
            await process_trigger_occurrences_once(
                executions,
                trigger_runtime,
                tenant_ids=tenant_ids,
                worker_id=service.instance.instance_id,
                operational_controls=operational_controls,
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
                operational_controls=operational_controls,
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
                operational_controls=operational_controls,
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
            operational_controls=operational_controls,
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
        outbox_work = sum(
            [
                await transport.publish_outbox(tenant_id=tenant_id, limit=500)
                for tenant_id in tenant_ids
            ]
        )
        webhook_work = (
            await webhook_dispatcher.run_once(
                tenant_ids,
                worker_id=str(service.instance.instance_id),
                limit=settings.webhook_delivery_batch_size,
            )
            if webhook_dispatcher is not None
            else 0
        )
        search_work = 0
        if search_projector is not None:
            for tenant_id in tenant_ids:
                try:
                    search_work += await search_projector.project_once(
                        tenant_id=tenant_id,
                        limit=5_000,
                    )
                except SearchUnavailableError as exc:
                    LOGGER.exception("optional search projection cycle failed")
                    await search_projector.record_failure(tenant_id=tenant_id, error=str(exc))
        return outbox_work + webhook_work + search_work
    if role is ServiceRole.MAINTENANCE:
        reconciled = await reconcile_once(reconciliations, settings, tenant_ids=tenant_ids)
        if retention_service is None:
            return reconciled
        lifecycle = await retention_service.run_scheduled_once(tuple(tenant_ids))
        return reconciled + lifecycle.records_processed
    raise ValueError(f"role {role.value!r} must run through amesh.server")


async def run_role(settings: Settings, *, stop_event: asyncio.Event | None = None) -> None:
    role = ServiceRole(settings.service_role)
    if role is ServiceRole.WEBSERVER:
        raise ValueError("webserver role must run through python -m amesh.server")
    engine = create_database_engine(settings)
    registry = PostgresServiceRegistryRepository(
        engine,
        stale_after_seconds=settings.service_stale_after_seconds,
    )
    service = RegisteredService(registry, settings, role)
    plugin_catalog = build_plugin_catalog(settings)
    plugin_policy = PluginPolicyService(
        PostgresPluginPolicyRepository(engine),
        plugin_catalog,
        default_allow=settings.plugin_trust_mode == "development",
    )
    admission_policy = AdmissionPolicyService(PostgresAdmissionPolicyRepository(engine))
    executions = PostgresExecutionRepository(
        engine,
        plugin_policy_enforcer=plugin_policy.enforce_flow,
        admission_policy_enforcer=admission_policy.enforce_repository,
    )
    scheduler = PostgresSchedulerRepository(engine)
    backfills = PostgresBackfillRepository(engine)
    reconciliations = PostgresReconciliationRepository(engine)
    tenants = PostgresTenantRepository(engine)
    workers = PostgresWorkerRepository(engine)
    transport = PostgresDurableTransport(engine)
    operational_controls = PostgresOperationalControlRepository(engine)
    task_cache = PostgresTaskCacheRepository(engine)
    shared_resources = PostgresSharedResourceRepository(engine)
    trigger_runtime = PostgresTriggerRuntimeRepository(engine)
    checks = PostgresCheckRepository(engine)
    trusted_runtime = build_trusted_runtime(settings, plugin_catalog)
    realtime = PostgresRealtimeRepository(engine)
    search_projector = PostgresSearchRepository(engine)
    retention_service = RetentionService(
        PostgresRetentionRepository(engine),
        build_object_store(settings),
    )
    webhook_dispatcher = WebhookDispatcher(
        realtime,
        signing_key=settings.webhook_signing_key.get_secret_value(),
        policy=HttpTaskPolicy(
            allowed_hosts=settings.network_egress_allowed_hosts,
            allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
            maximum_response_bytes=settings.core_http_max_response_bytes,
            maximum_pages=settings.core_http_max_pages,
            maximum_redirects=0,
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
        ),
        timeout_seconds=settings.webhook_delivery_timeout_seconds,
    )
    work_count = 0
    stop = stop_event or asyncio.Event()
    try:
        await service.register()
        if role is ServiceRole.WORKER:
            WORKER_CAPACITY.set(1)
        while not stop.is_set():
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
                await operational_controls.acknowledge_active(
                    tenant_ids=tenant_ids,
                    component_id=str(service.instance.instance_id),
                    component_role=role.value,
                )
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
                    operational_controls=operational_controls,
                    task_cache=task_cache,
                    shared_resources=shared_resources,
                    trigger_runtime=trigger_runtime,
                    checks=checks,
                    trusted_runtime=trusted_runtime,
                    webhook_dispatcher=webhook_dispatcher,
                    search_projector=search_projector,
                    retention_service=retention_service,
                )
            except (DBAPIError, OSError, LookupError):
                LOGGER.exception("service role cycle interrupted; retrying")
            with suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=settings.service_cycle_seconds)
    finally:
        if role is ServiceRole.WORKER:
            WORKER_CAPACITY.set(0)
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
    configure_observability(settings)
    try:
        if args.check == "liveness":
            return
        if args.check == "readiness":
            raise SystemExit(0 if asyncio.run(check_readiness(settings)) else 1)
        if args.drain:
            raise SystemExit(0 if asyncio.run(request_self_drain(settings)) else 1)
        asyncio.run(run_role(settings))
    finally:
        shutdown_observability()


if __name__ == "__main__":
    main()
