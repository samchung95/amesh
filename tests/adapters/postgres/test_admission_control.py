from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository, PostgresTenantRepository
from amesh.domain import (
    AdmissionBehavior,
    AdmissionOutcome,
    AdmissionResourceType,
    AdmissionScope,
    ConcurrencyLimit,
    ExecutionState,
    ResolvedAdmissionPolicy,
    TenantDefinition,
    TenantPolicy,
    new_runtime_id,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext
from amesh.ports import TenantQuotaExceeded


def _flow(namespace: str, behavior: AdmissionBehavior) -> FlowDefinition:
    return FlowDefinition(
        id="admission_flow",
        namespace=namespace,
        concurrency=[
            ConcurrencyLimit(
                id="flow-capacity",
                scope=AdmissionScope.FLOW,
                limit=1,
                behavior=behavior,
                leaseSeconds=60,
            )
        ],
        tasks=[TaskDefinition(id="hold", type="core.return")],
    )


async def _cleanup(engine: AsyncEngine, execution_ids: list[UUID], namespace: str) -> None:
    async with engine.begin() as connection:
        persisted_ids = list(
            await connection.scalars(
                text("SELECT id FROM executions WHERE namespace_name = :namespace"),
                {"namespace": namespace},
            )
        )
        execution_ids = list({*execution_ids, *persisted_ids})
        partition_keys = [f"execution:{execution_id}" for execution_id in execution_ids]
        await connection.execute(
            text(
                "DELETE FROM durable_work_queue "
                "WHERE partition_key = ANY(CAST(:partition_keys AS text[]))"
            ),
            {"partition_keys": partition_keys},
        )
        await connection.execute(
            text(
                "DELETE FROM messages_outbox "
                "WHERE partition_key = ANY(CAST(:partition_keys AS text[]))"
            ),
            {"partition_keys": partition_keys},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_reservations WHERE resource_id = ANY(CAST(:ids AS uuid[]))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM admission_requests WHERE resource_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_reservations WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[])))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM admission_requests WHERE resource_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[])))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM task_run_events WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text(
                "DELETE FROM task_attempts WHERE task_run_id IN "
                "(SELECT id FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[])))"
            ),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM task_runs WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM execution_events WHERE execution_id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )
        await connection.execute(
            text("DELETE FROM executions WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": execution_ids},
        )


@pytest.mark.parametrize(
    ("behavior", "expected"),
    [
        (AdmissionBehavior.CANCEL, ExecutionState.CANCELLED),
        (AdmissionBehavior.FAIL, ExecutionState.FAILED),
        (AdmissionBehavior.SKIP, ExecutionState.SUCCESS),
    ],
)
def test_execution_admission_limit_behaviors(
    behavior: AdmissionBehavior,
    expected: ExecutionState,
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.admission.{uuid4().hex}"
        executions: list[UUID] = []
        try:
            flow = _flow(namespace, behavior)
            first = await repository.create_execution(flow, tenant_id="default", inputs={})
            second = await repository.create_execution(flow, tenant_id="default", inputs={})
            executions.extend([first.execution_id, second.execution_id])
            assert first.state is ExecutionState.RUNNING
            assert second.state is expected
            decision = await repository.get_admission(
                AdmissionResourceType.EXECUTION,
                second.execution_id,
                tenant_id="default",
            )
            assert decision is not None
            assert decision.outcome.value == expected.value or (
                decision.outcome is AdmissionOutcome.SKIPPED and expected is ExecutionState.SUCCESS
            )
            assert decision.limiting_policy_id == "flow-capacity"
            assert "1/1" in decision.reason
        finally:
            await _cleanup(engine, executions, namespace)
            await engine.dispose()

    asyncio.run(scenario())


def test_idempotent_execution_retry_resolves_before_admission_saturation(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.admission.{uuid4().hex}"
        executions: list[UUID] = []
        try:
            flow = _flow(namespace, AdmissionBehavior.FAIL)
            first = await repository.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                idempotency_key="agent-session:retry-before-admission",
            )
            executions.append(first.execution_id)
            retried = await repository.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                idempotency_key="agent-session:retry-before-admission",
            )
            assert retried.execution_id == first.execution_id
        finally:
            await _cleanup(engine, executions, namespace)
            await engine.dispose()

    asyncio.run(scenario())


def test_task_dynamic_key_serializes_parallel_handlers(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.admission.{uuid4().hex}"
        execution_ids: list[UUID] = []
        active = 0
        maximum_active = 0

        async def slow_handler(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            nonlocal active, maximum_active
            del task, context
            active += 1
            maximum_active = max(maximum_active, active)
            await asyncio.sleep(0.1)
            active -= 1
            return {"ok": True}

        concurrency = [
            ConcurrencyLimit(
                id="customer-key",
                scope=AdmissionScope.KEY,
                key="{{ inputs.customer }}",
                limit=1,
                behavior=AdmissionBehavior.QUEUE,
            )
        ]
        flow = FlowDefinition(
            id="task_admission",
            namespace=namespace,
            tasks=[
                TaskDefinition(id="first", type="test.slow", concurrency=concurrency),
                TaskDefinition(id="second", type="test.slow", concurrency=concurrency),
            ],
        )
        executor = InProcessExecutor(repository, handlers={"test.slow": slow_handler})
        try:
            execution_id = await executor.create_execution(
                flow,
                tenant_id="default",
                inputs={"customer": "customer-42"},
            )
            execution_ids.append(execution_id)
            result = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert result.state is ExecutionState.SUCCESS
            assert maximum_active == 1
            task_decisions = [
                await repository.get_admission(
                    AdmissionResourceType.TASK,
                    task_run.task_run_id,
                    tenant_id="default",
                )
                for task_run in result.task_runs
            ]
            assert all(decision is not None for decision in task_decisions)
            assert {decision.outcome for decision in task_decisions if decision is not None} == {
                AdmissionOutcome.RELEASED
            }
        finally:
            await _cleanup(engine, execution_ids, namespace)
            await engine.dispose()

    asyncio.run(scenario())


def test_queue_release_replacement_fairness_and_lease_recovery(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.admission.{uuid4().hex}"
        executions: list[UUID] = []
        arbitrary_task_ids: list[UUID] = []
        try:
            queue_flow = _flow(namespace, AdmissionBehavior.QUEUE)
            first, second = await asyncio.gather(
                repository.create_execution(queue_flow, tenant_id="default", inputs={}),
                repository.create_execution(queue_flow, tenant_id="default", inputs={}),
            )
            executions.extend([first.execution_id, second.execution_id])
            running = first if first.state is ExecutionState.RUNNING else second
            queued = second if running is first else first
            assert queued.state is ExecutionState.QUEUED
            queued_decision = await repository.get_admission(
                AdmissionResourceType.EXECUTION,
                queued.execution_id,
                tenant_id="default",
            )
            assert queued_decision is not None
            assert queued_decision.queue_position == 1
            await repository.complete_execution(
                running.execution_id,
                tenant_id="default",
                expected_epoch=running.epoch,
            )
            promoted = await repository.get_execution(queued.execution_id, tenant_id="default")
            assert promoted.state is ExecutionState.RUNNING

            await repository.complete_execution(
                promoted.execution_id,
                tenant_id="default",
                expected_epoch=promoted.epoch,
            )
            replace_flow = _flow(namespace, AdmissionBehavior.REPLACE).model_copy(
                update={"revision": 2}
            )
            victim = await repository.create_execution(
                replace_flow,
                tenant_id="default",
                inputs={},
            )
            replacement = await repository.create_execution(
                replace_flow,
                tenant_id="default",
                inputs={},
            )
            executions.extend([victim.execution_id, replacement.execution_id])
            assert replacement.state is ExecutionState.RUNNING
            assert (
                await repository.get_execution(victim.execution_id, tenant_id="default")
            ).state is ExecutionState.CANCELLED

            policy = (
                ResolvedAdmissionPolicy(
                    policy_id="fair-queue",
                    scope=AdmissionScope.KEY,
                    bucket=f"TASK:KEY:default/{uuid4().hex}",
                    limit=1,
                    behavior=AdmissionBehavior.QUEUE,
                    lease_seconds=60,
                ),
            )
            holder, high, aged = new_runtime_id(), new_runtime_id(), new_runtime_id()
            arbitrary_task_ids.extend([holder, high, aged])
            assert (
                await repository.request_admission(
                    AdmissionResourceType.TASK,
                    holder,
                    policy,
                    tenant_id="default",
                )
            ).outcome is AdmissionOutcome.ADMITTED
            assert (
                await repository.request_admission(
                    AdmissionResourceType.TASK,
                    high,
                    policy,
                    tenant_id="default",
                    priority=100,
                )
            ).outcome is AdmissionOutcome.QUEUED
            assert (
                await repository.request_admission(
                    AdmissionResourceType.TASK,
                    aged,
                    policy,
                    tenant_id="default",
                    priority=0,
                )
            ).outcome is AdmissionOutcome.QUEUED
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE admission_requests SET created_at = :created_at "
                        "WHERE resource_id = :resource_id"
                    ),
                    {
                        "resource_id": aged,
                        "created_at": datetime.now(UTC) - timedelta(hours=3),
                    },
                )
            await repository.release_admission(
                AdmissionResourceType.TASK,
                holder,
                tenant_id="default",
            )
            aged_decision = await repository.get_admission(
                AdmissionResourceType.TASK,
                aged,
                tenant_id="default",
            )
            assert aged_decision is not None
            assert aged_decision.outcome is AdmissionOutcome.ADMITTED

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE admission_reservations SET lease_expires_at = clock_timestamp() "
                        "WHERE resource_id = :resource_id AND released_at IS NULL"
                    ),
                    {"resource_id": aged},
                )
            await repository.reconcile_admission(tenant_id="default")
            high_decision = await repository.get_admission(
                AdmissionResourceType.TASK,
                high,
                tenant_id="default",
            )
            assert high_decision is not None
            assert high_decision.outcome is AdmissionOutcome.ADMITTED
            diagnostics = await repository.admission_diagnostics(tenant_id="default")
            assert diagnostics.active_reservations >= 1
        finally:
            async with engine.begin() as connection:
                all_ids = [*executions, *arbitrary_task_ids]
                await connection.execute(
                    text(
                        "DELETE FROM admission_reservations "
                        "WHERE resource_id = ANY(CAST(:ids AS uuid[]))"
                    ),
                    {"ids": all_ids},
                )
                await connection.execute(
                    text(
                        "DELETE FROM admission_requests "
                        "WHERE resource_id = ANY(CAST(:ids AS uuid[]))"
                    ),
                    {"ids": all_ids},
                )
            await _cleanup(engine, executions, namespace)
            await engine.dispose()

    asyncio.run(scenario())


def test_tenant_storage_and_api_quotas_are_atomic(migrated_test_database_url: str) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresTenantRepository(engine)
        suffix = uuid4().hex[:10]
        tenant = TenantDefinition(
            slug=f"quota-{suffix}",
            display_name="Quota test",
            policy=TenantPolicy(
                max_storage_bytes=5,
                max_api_requests_per_minute=2,
            ),
        )
        try:
            await repository.create(tenant, actor_id="test:admission")
            assert await repository.reserve_storage_bytes(tenant.slug, 3) == 3
            with pytest.raises(TenantQuotaExceeded, match="storage_bytes"):
                await repository.reserve_storage_bytes(tenant.slug, 3)
            assert await repository.release_storage_bytes(tenant.slug, 2) == 1
            assert await repository.consume_api_request(tenant.slug) == 1
            assert await repository.consume_api_request(tenant.slug) == 2
            with pytest.raises(TenantQuotaExceeded, match="api_requests"):
                await repository.consume_api_request(tenant.slug)
        finally:
            async with engine.begin() as connection:
                await connection.execute(
                    text("DELETE FROM tenant_quota_usage WHERE tenant_id = :tenant_id"),
                    {"tenant_id": tenant.id},
                )
                await connection.execute(
                    text("DELETE FROM audit_events WHERE tenant_id = :tenant_id"),
                    {"tenant_id": tenant.id},
                )
                await connection.execute(
                    text("DELETE FROM tenants WHERE id = :tenant_id"),
                    {"tenant_id": tenant.id},
                )
            await engine.dispose()

    asyncio.run(scenario())
