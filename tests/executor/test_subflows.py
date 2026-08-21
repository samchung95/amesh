from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition
from amesh.executor import (
    InProcessExecutor,
    SubflowCoordinator,
    TaskExecutionContext,
    TaskExecutionError,
    TaskExecutionFailure,
    TaskExecutionPaused,
    preview_execution_intervention,
    subflow_task_handler,
)
from amesh.ports import (
    ExecutionInterventionAction,
    ExecutionLaunchSource,
    SubflowLaunchContext,
    SubflowMode,
    SubflowPropagation,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def cleanup_execution_tree(engine: AsyncEngine, root_id: UUID) -> None:
    async with engine.connect() as connection:
        child_ids = list(
            (
                await connection.execute(
                    text(
                        "WITH RECURSIVE descendants(id) AS ("
                        "SELECT child_execution_id FROM execution_subflows "
                        "WHERE parent_execution_id = :root_id UNION ALL "
                        "SELECT links.child_execution_id FROM execution_subflows links "
                        "JOIN descendants ON links.parent_execution_id = descendants.id) "
                        "SELECT id FROM descendants"
                    ),
                    {"root_id": root_id},
                )
            ).scalars()
        )
    execution_ids = [*reversed(child_ids), root_id]
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "DELETE FROM execution_subflows WHERE parent_execution_id = ANY(:ids) "
                "OR child_execution_id = ANY(:ids)"
            ),
            {"ids": execution_ids},
        )
        for execution_id in execution_ids:
            await connection.execute(
                text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
                {"partition_key": f"execution:{execution_id}"},
            )
            await connection.execute(
                text(
                    "DELETE FROM transition_rejections WHERE "
                    "(aggregate_type = 'execution' AND aggregate_id = :execution_id) OR "
                    "(aggregate_type = 'task_run' AND aggregate_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id))"
                ),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text(
                    "DELETE FROM task_attempts WHERE task_run_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
                ),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM executions WHERE id = :execution_id"),
                {"execution_id": execution_id},
            )


def executor_factory(
    repository: PostgresExecutionRepository,
    authorized: list[tuple[str, str, int]],
    *,
    deny_system: bool = False,
) -> Callable[[], InProcessExecutor]:
    handlers = {}

    async def authorize(flow: FlowDefinition) -> None:
        authorized.append((flow.namespace, flow.id, flow.revision))
        if deny_system and flow.system:
            raise ValueError("system subflow requires tenant administration")

    def factory() -> InProcessExecutor:
        return InProcessExecutor(
            repository,
            handlers=handlers,
            recover_running_types=frozenset({"core.subflow"}),
        )

    handlers["core.subflow"] = subflow_task_handler(repository, factory, authorize)
    return factory


def test_sync_subflow_pins_revision_maps_outputs_and_preserves_lineage() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.subflow.{uuid4().hex}"
        child_v1 = FlowDefinition.model_validate(
            {
                "id": "child",
                "namespace": namespace,
                "revision": 1,
                "labels": {"child": "v1"},
                "inputs": [{"id": "name", "type": "string", "required": True}],
                "tasks": [
                    {
                        "id": "reply",
                        "type": "core.return",
                        "value": {
                            "message": "hello {{ inputs.name }}",
                            "artifacts": ["amesh://reports/hello.txt"],
                        },
                    }
                ],
                "outputs": {"message": "{{ outputs.reply.value.message }}"},
            }
        )
        child_v2 = FlowDefinition.model_validate(
            {
                **child_v1.model_dump(mode="python", by_alias=True),
                "revision": 2,
                "tasks": [
                    {
                        "id": "reply",
                        "type": "core.return",
                        "value": "v2 {{ inputs.name }}",
                    }
                ],
            }
        )
        parent = FlowDefinition.model_validate(
            {
                "id": "parent",
                "namespace": namespace,
                "labels": {"team": "platform"},
                "inputs": [{"id": "person", "type": "string", "required": True}],
                "tasks": [
                    {
                        "id": "call_child",
                        "type": "core.subflow",
                        "namespace": namespace,
                        "flowId": "child",
                        "revision": 1,
                        "mode": "SYNC",
                        "inputs": {"name": "{{ inputs.person }}"},
                        "labels": {"purpose": "test"},
                        "outputMapping": {"greeting": "{{ outputs.reply.value.message }}"},
                        "outputSchema": {
                            "type": "object",
                            "properties": {"greeting": {"type": "string"}},
                            "required": ["greeting"],
                            "additionalProperties": False,
                        },
                        "artifactMapping": {"documents": "{{ outputs.reply.value.artifacts }}"},
                        "artifactSchema": {
                            "type": "object",
                            "properties": {
                                "documents": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            },
                            "required": ["documents"],
                            "additionalProperties": False,
                        },
                    }
                ],
            }
        )
        await repository.apply_flow(child_v1, tenant_id="default")
        await repository.apply_flow(child_v2, tenant_id="default")
        authorized: list[tuple[str, str, int]] = []
        factory = executor_factory(repository, authorized)
        execution = await repository.create_execution(
            parent,
            tenant_id="default",
            inputs={"person": "Ada"},
            trigger={"correlationId": "trace-123", "traceContext": {"traceparent": "00-abc"}},
        )
        try:
            try:
                completed = await factory().run_to_completion(
                    parent,
                    execution.execution_id,
                    tenant_id="default",
                )
            except TaskExecutionError as exc:
                task_runs = await repository.list_task_runs(
                    execution.execution_id,
                    tenant_id="default",
                )
                raise AssertionError(task_runs[0].result) from exc
            assert completed.state is ExecutionState.SUCCESS
            result = completed.task_runs[0].result
            assert result is not None
            assert result["childRevision"] == 1
            assert result["outputs"] == {"greeting": "hello Ada"}
            assert result["artifacts"] == {"documents": ["amesh://reports/hello.txt"]}
            assert authorized == [(namespace, "child", 1)]

            relationships = await repository.list_subflows(
                execution.execution_id,
                tenant_id="default",
            )
            assert len(relationships) == 1
            relationship = relationships[0]
            assert relationship.mode is SubflowMode.SYNC
            assert relationship.target_revision == 1
            child = await repository.get_execution(
                relationship.child_execution_id,
                tenant_id="default",
            )
            assert child.flow_revision == 1
            assert child.labels == {
                "child": "v1",
                "team": "platform",
                "purpose": "test",
            }
            assert child.trigger["correlationId"] == "trace-123"
            assert child.trigger["traceContext"] == {"traceparent": "00-abc"}
            assert child.trigger["parentExecutionId"] == str(execution.execution_id)
            parent_link = await repository.get_parent_subflow(
                child.execution_id,
                tenant_id="default",
            )
            assert parent_link == relationship
            assert (
                await repository.get_flow(namespace, "child", tenant_id="default")
            ).revision == 2
        finally:
            await cleanup_execution_tree(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_async_and_detached_children_run_independently_from_successful_parent() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.subflow.async.{uuid4().hex}"
        success_child = FlowDefinition.model_validate(
            {
                "id": "success_child",
                "namespace": namespace,
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        failed_child = FlowDefinition.model_validate(
            {
                "id": "failed_child",
                "namespace": namespace,
                "tasks": [{"id": "fail", "type": "missing.handler"}],
            }
        )
        parent = FlowDefinition.model_validate(
            {
                "id": "parent",
                "namespace": namespace,
                "tasks": [
                    {
                        "id": "async_child",
                        "type": "core.subflow",
                        "flowId": "success_child",
                        "mode": "ASYNC",
                    },
                    {
                        "id": "detached_child",
                        "type": "core.subflow",
                        "flowId": "failed_child",
                        "mode": "DETACHED",
                    },
                    {
                        "id": "unmapped_success",
                        "type": "core.subflow",
                        "flowId": "success_child",
                        "propagation": {"success": False},
                    },
                ],
            }
        )
        await repository.apply_flow(success_child, tenant_id="default")
        await repository.apply_flow(failed_child, tenant_id="default")
        authorized: list[tuple[str, str, int]] = []
        factory = executor_factory(repository, authorized)
        execution = await repository.create_execution(parent, tenant_id="default", inputs={})
        try:
            parent_result = await factory().run_to_completion(
                parent,
                execution.execution_id,
                tenant_id="default",
            )
            assert parent_result.state is ExecutionState.SUCCESS
            unmapped = next(
                task_run
                for task_run in parent_result.task_runs
                if task_run.task_id == "unmapped_success"
            )
            assert unmapped.result is not None
            assert UUID(str(unmapped.result["childExecutionId"]))
            assert unmapped.result["outputs"] == {}
            assert unmapped.result["artifacts"] == {}
            assert unmapped.result["propagated"] is False
            relationships = await repository.list_subflows(
                execution.execution_id,
                tenant_id="default",
            )
            assert {item.mode for item in relationships} == {
                SubflowMode.SYNC,
                SubflowMode.ASYNC,
                SubflowMode.DETACHED,
            }
            detached = next(item for item in relationships if item.mode is SubflowMode.DETACHED)
            assert not detached.propagation.failure
            assert not detached.propagation.cancellation
            assert not detached.propagation.success

            children = await SubflowCoordinator(repository, factory).run_pending(
                execution.execution_id,
                tenant_id="default",
            )
            assert {child.flow_id: child.state for child in children} == {
                "success_child": ExecutionState.SUCCESS,
                "failed_child": ExecutionState.FAILED,
            }
            persisted_parent = await repository.get_execution(
                execution.execution_id,
                tenant_id="default",
            )
            assert persisted_parent.state is ExecutionState.SUCCESS
        finally:
            await cleanup_execution_tree(engine, execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_subflow_rejects_cycles_invalid_inputs_and_unauthorized_system_flows() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.subflow.denied.{uuid4().hex}"
        scenarios = (
            FlowDefinition.model_validate(
                {
                    "id": "self_cycle",
                    "namespace": namespace,
                    "tasks": [{"id": "recurse", "type": "core.subflow", "flowId": "self_cycle"}],
                }
            ),
            FlowDefinition.model_validate(
                {
                    "id": "typed_child",
                    "namespace": namespace,
                    "inputs": [{"id": "count", "type": "integer", "required": True}],
                    "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
                }
            ),
            FlowDefinition.model_validate(
                {
                    "id": "system_child",
                    "namespace": namespace,
                    "system": True,
                    "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
                }
            ),
        )
        for flow in scenarios:
            await repository.apply_flow(flow, tenant_id="default")
        parents = (
            scenarios[0],
            FlowDefinition.model_validate(
                {
                    "id": "bad_input_parent",
                    "namespace": namespace,
                    "tasks": [
                        {
                            "id": "call",
                            "type": "core.subflow",
                            "flowId": "typed_child",
                            "inputs": {"count": "not-an-integer"},
                        }
                    ],
                }
            ),
            FlowDefinition.model_validate(
                {
                    "id": "system_parent",
                    "namespace": namespace,
                    "tasks": [{"id": "call", "type": "core.subflow", "flowId": "system_child"}],
                }
            ),
        )
        invalid_output_parent = FlowDefinition.model_validate(
            {
                "id": "invalid_output_parent",
                "namespace": namespace,
                "tasks": [
                    {
                        "id": "call",
                        "type": "core.subflow",
                        "flowId": "typed_child",
                        "inputs": {"count": 1},
                        "outputMapping": {"value": "{{ outputs.done.value }}"},
                        "outputSchema": {
                            "type": "object",
                            "properties": {"value": {"type": "integer"}},
                            "required": ["value"],
                        },
                    }
                ],
            }
        )
        execution_ids: list[UUID] = []
        try:
            for index, parent in enumerate(parents):
                authorized: list[tuple[str, str, int]] = []
                factory = executor_factory(repository, authorized, deny_system=index == 2)
                execution = await repository.create_execution(
                    parent,
                    tenant_id="default",
                    inputs={},
                )
                execution_ids.append(execution.execution_id)
                with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                    await factory().run_to_completion(
                        parent,
                        execution.execution_id,
                        tenant_id="default",
                    )
                assert not await repository.list_subflows(
                    execution.execution_id,
                    tenant_id="default",
                )
            assert authorized == [(namespace, "system_child", 1)]
            factory = executor_factory(repository, [])
            execution = await repository.create_execution(
                invalid_output_parent,
                tenant_id="default",
                inputs={},
            )
            execution_ids.append(execution.execution_id)
            with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                await factory().run_to_completion(
                    invalid_output_parent,
                    execution.execution_id,
                    tenant_id="default",
                )
            task_runs = await repository.list_task_runs(
                execution.execution_id,
                tenant_id="default",
            )
            assert "does not match schema" in str(task_runs[0].result)
        finally:
            for execution_id in execution_ids:
                await cleanup_execution_tree(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_sync_subflow_honors_cancellation_and_restart_propagation_policy() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        namespace = f"tests.subflow.policy.{uuid4().hex}"
        child = FlowDefinition.model_validate(
            {
                "id": "child",
                "namespace": namespace,
                "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            }
        )
        parent = FlowDefinition.model_validate(
            {
                "id": "parent",
                "namespace": namespace,
                "tasks": [{"id": "call", "type": "core.subflow", "flowId": "child"}],
            }
        )
        await repository.apply_flow(child, tenant_id="default")
        parent_execution = await repository.create_execution(
            parent,
            tenant_id="default",
            inputs={},
        )
        parent_task = (
            await repository.list_task_runs(
                parent_execution.execution_id,
                tenant_id="default",
            )
        )[0]
        running_parent_task = await repository.start_task(
            parent_task.task_run_id,
            tenant_id="default",
        )
        invocation_key = (
            f"subflow:{running_parent_task.task_run_id}:{running_parent_task.current_attempt}"
        )
        cancelled_child = await repository.create_execution(
            child,
            tenant_id="default",
            inputs={},
            launch_source=ExecutionLaunchSource.SUBFLOW,
            idempotency_key=invocation_key,
            subflow=SubflowLaunchContext(
                parent_execution_id=parent_execution.execution_id,
                parent_task_run_id=running_parent_task.task_run_id,
                parent_attempt=running_parent_task.current_attempt,
                invocation_key=invocation_key,
                mode=SubflowMode.SYNC,
                depth=1,
                target_revision=1,
                propagation=SubflowPropagation(),
            ),
        )
        cancelling_child = await repository.apply_execution_intervention(
            cancelled_child.execution_id,
            ExecutionInterventionAction.REQUEST_CANCEL,
            tenant_id="default",
            expected_version=cancelled_child.version,
            expected_epoch=cancelled_child.epoch,
            actor_id="tests:subflow",
            reason="policy test",
            grace_period=timedelta(0),
        )
        await repository.apply_execution_intervention(
            cancelled_child.execution_id,
            ExecutionInterventionAction.CONFIRM_CANCEL,
            tenant_id="default",
            expected_version=cancelling_child.version,
            expected_epoch=cancelling_child.epoch,
            actor_id="tests:subflow",
            reason="policy test",
        )
        context = TaskExecutionContext(
            tenant_id="default",
            execution_id=parent_execution.execution_id,
            task_run_id=running_parent_task.task_run_id,
            attempt=running_parent_task.current_attempt,
            attempt_id=uuid4(),
            inputs={},
            outputs={},
            variables={},
        )
        factory = executor_factory(repository, [])

        async def authorize(_: FlowDefinition) -> None:
            return None

        handler = subflow_task_handler(repository, factory, authorize)
        non_propagating_task = parent.tasks[0].__class__.model_validate(
            {
                **parent.tasks[0].model_dump(mode="python", by_alias=True),
                "propagation": {"cancellation": False},
            }
        )
        pause_parent_execution = await repository.create_execution(
            parent,
            tenant_id="default",
            inputs={},
        )
        pause_parent_task = (
            await repository.list_task_runs(
                pause_parent_execution.execution_id,
                tenant_id="default",
            )
        )[0]
        running_pause_task = await repository.start_task(
            pause_parent_task.task_run_id,
            tenant_id="default",
        )
        pause_invocation_key = (
            f"subflow:{running_pause_task.task_run_id}:{running_pause_task.current_attempt}"
        )
        paused_child = await repository.create_execution(
            child,
            tenant_id="default",
            inputs={},
            launch_source=ExecutionLaunchSource.SUBFLOW,
            idempotency_key=pause_invocation_key,
            subflow=SubflowLaunchContext(
                parent_execution_id=pause_parent_execution.execution_id,
                parent_task_run_id=running_pause_task.task_run_id,
                parent_attempt=running_pause_task.current_attempt,
                invocation_key=pause_invocation_key,
                mode=SubflowMode.SYNC,
                depth=1,
                target_revision=1,
                propagation=SubflowPropagation(),
            ),
        )
        await repository.apply_execution_intervention(
            paused_child.execution_id,
            ExecutionInterventionAction.PAUSE,
            tenant_id="default",
            expected_version=paused_child.version,
            expected_epoch=paused_child.epoch,
            actor_id="tests:subflow",
            reason="policy test",
        )
        pause_context = TaskExecutionContext(
            tenant_id="default",
            execution_id=pause_parent_execution.execution_id,
            task_run_id=running_pause_task.task_run_id,
            attempt=running_pause_task.current_attempt,
            attempt_id=uuid4(),
            inputs={},
            outputs={},
            variables={},
        )
        non_propagating_pause_task = parent.tasks[0].__class__.model_validate(
            {
                **parent.tasks[0].model_dump(mode="python", by_alias=True),
                "propagation": {"pause": False},
            }
        )
        restart_parent = FlowDefinition.model_validate(
            {
                "id": "restart_parent",
                "namespace": namespace,
                "tasks": [
                    {
                        "id": "call",
                        "type": "core.subflow",
                        "flowId": "child",
                        "propagation": {"restart": False},
                    },
                    {
                        "id": "fail",
                        "type": "missing.handler",
                        "dependsOn": ["call"],
                    },
                ],
            }
        )
        restart_execution = await repository.create_execution(
            restart_parent,
            tenant_id="default",
            inputs={},
        )
        try:
            result = await handler(non_propagating_task, context)
            assert result["childState"] == "CANCELLED"
            assert result["propagated"] is False
            with pytest.raises(TaskExecutionFailure, match="was cancelled"):
                await handler(parent.tasks[0], context)

            pause_result = await handler(non_propagating_pause_task, pause_context)
            assert pause_result["childState"] == "PAUSED"
            assert pause_result["propagated"] is False
            with pytest.raises(TaskExecutionPaused, match="paused"):
                await handler(parent.tasks[0], pause_context)
            assert (
                await repository.get_execution(
                    pause_parent_execution.execution_id,
                    tenant_id="default",
                )
            ).state is ExecutionState.PAUSED

            with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                await factory().run_to_completion(
                    restart_parent,
                    restart_execution.execution_id,
                    tenant_id="default",
                )
            failed = await repository.get_execution(
                restart_execution.execution_id,
                tenant_id="default",
            )
            failed_tasks = await repository.list_task_runs(
                restart_execution.execution_id,
                tenant_id="default",
            )
            preview = preview_execution_intervention(
                restart_parent,
                failed,
                failed_tasks,
                ExecutionInterventionAction.RESTART,
                checkpoint_task_id="call",
                now=await repository.database_time(),
            )
            await repository.apply_execution_intervention(
                restart_execution.execution_id,
                ExecutionInterventionAction.RESTART,
                tenant_id="default",
                expected_version=failed.version,
                expected_epoch=failed.epoch,
                actor_id="tests:subflow",
                reason="restart without child replay",
                reset_task_ids=preview.impacted_task_ids,
                checkpoint_task_id="call",
            )
            with pytest.raises(TaskExecutionError, match="unsatisfiable execution graph"):
                await factory().run_to_completion(
                    restart_parent,
                    restart_execution.execution_id,
                    tenant_id="default",
                )
            assert (
                len(
                    await repository.list_subflows(
                        restart_execution.execution_id,
                        tenant_id="default",
                    )
                )
                == 1
            )
        finally:
            await cleanup_execution_tree(engine, parent_execution.execution_id)
            await cleanup_execution_tree(engine, pause_parent_execution.execution_id)
            await cleanup_execution_tree(engine, restart_execution.execution_id)
            await engine.dispose()

    asyncio.run(scenario())
