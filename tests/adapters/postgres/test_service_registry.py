from __future__ import annotations

import asyncio
import os
from contextlib import suppress
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh import __version__
from amesh.adapters.postgres import PostgresServiceRegistryRepository
from amesh.config import Settings
from amesh.domain import (
    FailoverStatus,
    ServiceCompatibility,
    ServiceLiveness,
    ServiceRegistration,
    ServiceRole,
    ServiceState,
)
from amesh.ports import ServiceFenceError, ServiceVersionSkewError
from amesh.role import run_role

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _registration(
    role: ServiceRole,
    name: str,
    zone: str,
    *,
    version: str = __version__,
) -> ServiceRegistration:
    return ServiceRegistration(
        id=uuid4(),
        role=role,
        instanceName=name,
        version=version,
        failureZone=zone,
    )


def test_registry_fences_replaced_instances_and_reports_failover_topology(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresServiceRegistryRepository(engine, stale_after_seconds=20)
            first = await repository.register(
                _registration(ServiceRole.SCHEDULER, "scheduler-0", "zone-a")
            )
            first = await repository.heartbeat(
                first.instance_id,
                first.generation,
                ownership={"scheduleLeases": 3},
                partitions={"strategy": "postgresql-durable-partitions"},
                dependencies={"postgresql": "READY"},
            )
            assert first.state is ServiceState.READY

            replacement = await repository.register(
                _registration(ServiceRole.SCHEDULER, "scheduler-0", "zone-a")
            )
            assert replacement.instance_id != first.instance_id
            assert replacement.generation == first.generation + 1
            with pytest.raises(ServiceFenceError):
                await repository.heartbeat(first.instance_id, first.generation)
            replacement = await repository.heartbeat(
                replacement.instance_id,
                replacement.generation,
            )

            peer = await repository.register(
                _registration(ServiceRole.SCHEDULER, "scheduler-1", "zone-b")
            )
            peer = await repository.heartbeat(peer.instance_id, peer.generation)
            skewed = await repository.register(
                _registration(
                    ServiceRole.EXECUTOR,
                    "executor-old",
                    "zone-b",
                    version="0.1.0",
                )
            )
            skewed = await repository.heartbeat(skewed.instance_id, skewed.generation)

            topology = await repository.topology()
            scheduler = next(item for item in topology.roles if item.role is ServiceRole.SCHEDULER)
            assert scheduler.failover_status is FailoverStatus.REDUNDANT
            assert scheduler.ready_instances == 2
            assert scheduler.failure_zones == ("zone-a", "zone-b")
            assert topology.version_skew
            assert skewed.compatibility is ServiceCompatibility.ROLLING_COMPATIBLE

            with pytest.raises(ServiceVersionSkewError, match="unsafe with"):
                await repository.register(
                    _registration(
                        ServiceRole.WORKER,
                        "worker-unsafe",
                        "zone-c",
                        version="9.0.0",
                    )
                )

            with pytest.raises(ServiceFenceError):
                await repository.request_drain(
                    replacement.instance_id,
                    expected_version=replacement.resource_version - 1,
                    actor_id="test:operator",
                    reason="stale drain",
                )
            draining = await repository.request_drain(
                replacement.instance_id,
                expected_version=replacement.resource_version,
                actor_id="test:operator",
                reason="rolling upgrade",
            )
            assert draining.state is ServiceState.DRAINING
            still_draining = await repository.heartbeat(
                draining.instance_id,
                draining.generation,
            )
            assert still_draining.state is ServiceState.DRAINING

            stopped = await repository.stop(peer.instance_id, peer.generation)
            assert stopped.state is ServiceState.STOPPED
            assert stopped.liveness is ServiceLiveness.STOPPED
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text(
                            "SELECT count(*) FROM audit_events "
                            "WHERE action = 'service.drain' AND actor_id = 'test:operator'"
                        )
                    )
                    == 1
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_failed_cycle_is_live_but_degraded_until_a_successful_cycle(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresServiceRegistryRepository(engine, stale_after_seconds=20)
            instance = await repository.register(
                _registration(ServiceRole.SCHEDULER, "scheduler-health", "zone-a")
            )

            failed = await repository.heartbeat(
                instance.instance_id,
                instance.generation,
                ready=False,
                failure="schedule cycle failed",
            )
            assert failed.liveness is ServiceLiveness.LIVE
            assert failed.state is ServiceState.DEGRADED
            assert failed.last_success_at is None
            assert failed.last_failure_at is not None
            assert failed.consecutive_failures == 1
            assert failed.last_failure == "schedule cycle failed"
            degraded_topology = await repository.topology()
            scheduler = next(
                item for item in degraded_topology.roles if item.role is ServiceRole.SCHEDULER
            )
            assert scheduler.ready_instances == 0
            assert scheduler.degraded_instances == 1

            recovered = await repository.heartbeat(
                failed.instance_id,
                failed.generation,
                ready=True,
            )
            assert recovered.state is ServiceState.READY
            assert recovered.last_success_at is not None
            assert recovered.last_failure_at == failed.last_failure_at
            assert recovered.consecutive_failures == 0
            assert recovered.last_failure is None
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_role_process_observes_drain_before_taking_another_cycle(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        observer = create_async_engine(migrated_test_database_url)
        task: asyncio.Task[None] | None = None
        try:
            settings = Settings(
                _env_file=None,
                database_url=migrated_test_database_url,
                service_role="indexer",
                service_instance_name="indexer-drain-test",
                service_failure_zone="zone-a",
                service_heartbeat_seconds=1,
                service_stale_after_seconds=5,
                service_cycle_seconds=0.1,
            )
            task = asyncio.create_task(run_role(settings))
            repository = PostgresServiceRegistryRepository(observer, stale_after_seconds=5)
            instance = None
            for _ in range(40):
                topology = await repository.topology()
                instance = next(
                    (
                        item
                        for item in topology.instances
                        if item.instance_name == "indexer-drain-test"
                        and item.state is ServiceState.READY
                    ),
                    None,
                )
                if instance is not None:
                    break
                await asyncio.sleep(0.05)
            assert instance is not None
            for _ in range(10):
                try:
                    await repository.request_drain(
                        instance.instance_id,
                        expected_version=instance.resource_version,
                        actor_id="test:operator",
                        reason="test graceful drain",
                    )
                    break
                except ServiceFenceError:
                    instance = await repository.get(instance.instance_id)
            else:
                pytest.fail("role heartbeat did not expose a drainable version")
            await asyncio.wait_for(task, timeout=5)
            stopped = await repository.get(instance.instance_id)
            assert stopped.state is ServiceState.STOPPED
        finally:
            if task is not None and not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            await observer.dispose()

    asyncio.run(scenario())
