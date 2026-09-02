from __future__ import annotations

import asyncio
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresWorkerRepository,
)
from amesh.dsl import FlowDefinition
from amesh.ports import (
    TaskRunState,
    TaskStateConflictError,
    WorkerClaimHeartbeat,
    WorkerCompatibility,
    WorkerCompatibilityError,
    WorkerLossPolicy,
    WorkerRegistration,
    WorkerStatus,
)


def worker_flow() -> FlowDefinition:
    identity = uuid4().hex
    return FlowDefinition.model_validate(
        {
            "id": f"worker_protocol_{identity}",
            "namespace": f"tests.worker.{identity}",
            "tasks": [
                {
                    "id": "work",
                    "type": "core.return",
                    "runner": "local",
                    "value": "ok",
                }
            ],
        }
    )


async def dispatch_one(
    executions: PostgresExecutionRepository,
    transport: PostgresDurableTransport,
) -> tuple[UUID, UUID]:
    execution = await executions.create_execution(worker_flow(), tenant_id="default", inputs={})
    task = (await executions.list_task_runs(execution.execution_id, tenant_id="default"))[0]
    await executions.start_task(task.task_run_id, tenant_id="default")
    assert await transport.publish_outbox(tenant_id="default", limit=100) >= 1
    return execution.execution_id, task.task_run_id


async def cleanup(
    engine: AsyncEngine,
    execution_ids: list[UUID],
    worker_group_prefix: str,
) -> None:
    async with engine.begin() as connection:
        for execution_id in execution_ids:
            parameters = {
                "execution_id": execution_id,
                "partition_key": f"execution:{execution_id}",
            }
            await connection.execute(
                text(
                    "DELETE FROM durable_dead_letters WHERE source_type = 'QUEUE' "
                    "AND source_id IN (SELECT id FROM durable_work_queue "
                    "WHERE partition_key = :partition_key)"
                ),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
                parameters,
            )
            await connection.execute(
                text(
                    "DELETE FROM task_attempts WHERE task_run_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
                ),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM durable_work_queue WHERE partition_key = :partition_key"),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
                parameters,
            )
            await connection.execute(
                text("DELETE FROM executions WHERE id = :execution_id"),
                parameters,
            )
        await connection.execute(
            text("DELETE FROM workers WHERE worker_group LIKE :worker_group"),
            {"worker_group": f"{worker_group_prefix}%"},
        )


def test_versioned_worker_protocol_fences_dispatch_and_recovers_lost_work(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        executions = PostgresExecutionRepository(engine)
        transport = PostgresDurableTransport(engine)
        workers = PostgresWorkerRepository(engine)
        group_prefix = f"protocol-{uuid4().hex}"
        execution_ids: list[UUID] = []
        try:
            first_worker_id = uuid4()
            first = await workers.register_worker(
                WorkerRegistration(
                    worker_id=first_worker_id,
                    worker_group=f"{group_prefix}-primary",
                    instance_name="one",
                    version="1.2.3",
                    capabilities=("core.return",),
                    runner_types=("local",),
                    capacity=1,
                    labels={"region": "test"},
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            stable = await workers.register_worker(
                WorkerRegistration(
                    worker_id=uuid4(),
                    worker_group=f"{group_prefix}-primary",
                    instance_name="one",
                    version="1.2.4",
                    capabilities=("core.return",),
                    runner_types=("local",),
                    capacity=1,
                    labels={"region": "test"},
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            assert stable.worker_id == first_worker_id
            assert stable.resource_version == first.resource_version + 1

            incompatible = await workers.register_worker(
                WorkerRegistration(
                    worker_id=uuid4(),
                    worker_group=f"{group_prefix}-incompatible",
                    instance_name="one",
                    version="2.0.0",
                    protocol_version=2,
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            assert incompatible.compatibility is WorkerCompatibility.INCOMPATIBLE
            with pytest.raises(WorkerCompatibilityError):
                await workers.claim_tasks(
                    incompatible.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )

            wrong_runner = await workers.register_worker(
                WorkerRegistration(
                    worker_id=uuid4(),
                    worker_group=f"{group_prefix}-wrong-runner",
                    instance_name="one",
                    version="1.0.0",
                    capabilities=("core.return",),
                    runner_types=("kubernetes",),
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            execution_id, task_run_id = await dispatch_one(executions, transport)
            execution_ids.append(execution_id)
            assert (
                await workers.claim_tasks(
                    wrong_runner.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
                == []
            )

            claim = (
                await workers.claim_tasks(
                    stable.worker_id,
                    tenant_id="default",
                    limit=2,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert claim.task_run_id == task_run_id
            assert claim.attempt == 1
            assert claim.fencing_token == 1

            heartbeat = await workers.heartbeat_worker(
                stable.worker_id,
                tenant_id="default",
                expected_version=stable.resource_version,
                status=WorkerStatus.READY,
                lease_duration=timedelta(seconds=30),
                claims=(
                    WorkerClaimHeartbeat(
                        queue_id=claim.queue_id,
                        task_run_id=claim.task_run_id,
                        attempt=claim.attempt,
                        fencing_token=claim.fencing_token,
                        progress={"percent": 50},
                        resource_usage={"cpu": 0.25},
                        cancellation_acknowledged=True,
                    ),
                ),
                progress={"phase": "running"},
                resource_usage={"slots": 1},
                cancellation_acknowledged=True,
                actor_id="worker-heartbeat",
            )
            assert heartbeat.claimed_work == 1
            assert heartbeat.utilization == 1
            assert heartbeat.progress == {"phase": "running"}
            assert heartbeat.cancellation_acknowledged

            drained = await workers.drain_worker(
                stable.worker_id,
                tenant_id="default",
                expected_version=heartbeat.resource_version,
                actor_id="operator",
            )
            assert drained.status is WorkerStatus.DRAINING
            second_execution_id, _ = await dispatch_one(executions, transport)
            execution_ids.append(second_execution_id)
            assert (
                await workers.claim_tasks(
                    stable.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
                == []
            )
            completed = await executions.complete_task(
                claim.task_run_id,
                claim.attempt,
                {"value": "finished while draining"},
                tenant_id="default",
                worker_id=claim.worker_id,
                fencing_token=claim.fencing_token,
            )
            assert completed.state is TaskRunState.SUCCESS
            async with engine.connect() as connection:
                assert (
                    await connection.scalar(
                        text("SELECT count(*) FROM durable_work_queue WHERE id = :queue_id"),
                        {"queue_id": claim.queue_id},
                    )
                    == 0
                )

            replacement = await workers.register_worker(
                WorkerRegistration(
                    worker_id=uuid4(),
                    worker_group=f"{group_prefix}-replacement",
                    instance_name="one",
                    version="1.0.0",
                    capabilities=("core.return",),
                    runner_types=("local",),
                    capacity=1,
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            stale_claim = (
                await workers.claim_tasks(
                    replacement.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(milliseconds=50),
                )
            )[0]
            await asyncio.sleep(0.1)
            assert (
                await workers.recover_expired_claims(
                    tenant_id="default",
                    policy=WorkerLossPolicy.REQUEUE,
                )
                == 1
            )

            successor = await workers.register_worker(
                WorkerRegistration(
                    worker_id=uuid4(),
                    worker_group=f"{group_prefix}-successor",
                    instance_name="one",
                    version="1.0.0",
                    capabilities=("core.return",),
                    runner_types=("local",),
                    capacity=1,
                ),
                tenant_id="default",
                actor_id="worker-bootstrap",
            )
            successor_claim = (
                await workers.claim_tasks(
                    successor.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(seconds=30),
                )
            )[0]
            assert successor_claim.task_run_id == stale_claim.task_run_id
            assert successor_claim.fencing_token > stale_claim.fencing_token
            with pytest.raises(TaskStateConflictError):
                await executions.complete_task(
                    stale_claim.task_run_id,
                    stale_claim.attempt,
                    {"value": "stale"},
                    tenant_id="default",
                    worker_id=stale_claim.worker_id,
                    fencing_token=stale_claim.fencing_token,
                )
            await executions.complete_task(
                successor_claim.task_run_id,
                successor_claim.attempt,
                {"value": "current"},
                tenant_id="default",
                worker_id=successor_claim.worker_id,
                fencing_token=successor_claim.fencing_token,
            )

            failed_execution_id, failed_task_run_id = await dispatch_one(executions, transport)
            execution_ids.append(failed_execution_id)
            failed_claim = (
                await workers.claim_tasks(
                    successor.worker_id,
                    tenant_id="default",
                    limit=1,
                    lease_duration=timedelta(milliseconds=50),
                )
            )[0]
            await asyncio.sleep(0.1)
            assert (
                await workers.recover_expired_claims(
                    tenant_id="default",
                    policy=WorkerLossPolicy.FAIL,
                )
                == 1
            )
            assert (await executions.list_task_runs(failed_execution_id, tenant_id="default"))[
                0
            ].state is TaskRunState.FAILED
            assert failed_claim.task_run_id == failed_task_run_id

            notified_execution = await executions.create_execution(
                worker_flow(), tenant_id="default", inputs={}
            )
            execution_ids.append(notified_execution.execution_id)
            notified_task = (
                await executions.list_task_runs(
                    notified_execution.execution_id, tenant_id="default"
                )
            )[0]
            await executions.start_task(notified_task.task_run_id, tenant_id="default")
            waiter = asyncio.create_task(
                workers.wait_for_work(tenant_id="default", timeout_seconds=2)
            )
            await asyncio.sleep(0.05)
            assert await transport.publish_outbox(tenant_id="default", limit=100) >= 1
            assert await waiter

            inventory = await workers.list_worker_inventory(tenant_id="default")
            by_id = {item.worker_id: item for item in inventory}
            assert by_id[stable.worker_id].status is WorkerStatus.DRAINING
            assert by_id[stable.worker_id].labels == {"region": "test"}
            assert by_id[successor.worker_id].claimed_work == 0
        finally:
            await cleanup(engine, execution_ids, group_prefix)
            await engine.dispose()

    asyncio.run(scenario())
