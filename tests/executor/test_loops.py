from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from tests.fixtures.task_schemas import registered_test_task_registry

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState, TaskRunState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext, TaskExecutionError
from amesh.executor.loops import LoopSpec, iter_foreach_items, parse_loop_spec
from amesh.ports import ObjectMetadata


class MemoryObjectStore:
    def __init__(self, objects: dict[str, bytes] | None = None) -> None:
        self.objects = objects or {}

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([chunk async for chunk in chunks])
        uri = f"memory://{tenant_id}/{key}"
        self.objects[uri] = content
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            content = self.objects[uri]
            midpoint = max(len(content) // 2, 1)
            yield content[:midpoint]
            yield content[midpoint:]

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        del tenant_id
        self.objects.pop(uri)


async def cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
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


def test_foreach_sources_stream_in_deterministic_order_and_batch_without_full_buffering() -> None:
    async def collect(spec: LoopSpec, store: MemoryObjectStore | None = None) -> list[object]:
        return [
            item
            async for item in iter_foreach_items(
                spec,
                tenant_id="default",
                object_store=store,
            )
        ]

    array = asyncio.run(collect(LoopSpec(items=["a", "b"])))
    mapping = asyncio.run(collect(LoopSpec(items={"z": 1, "a": 2})))
    ranged = asyncio.run(
        collect(LoopSpec.model_validate({"range": {"start": 1, "end": 6}, "batchSize": 2}))
    )
    store = MemoryObjectStore(
        {"memory://default/input.jsonl": b'{"key":"b","value":2}\n{"value":3}\n'}
    )
    manifested = asyncio.run(collect(LoopSpec(manifestUri="memory://default/input.jsonl"), store))

    assert [(item.index, item.key, item.value) for item in array] == [
        (0, "0", "a"),
        (1, "1", "b"),
    ]
    assert [(item.key, item.value) for item in mapping] == [("a", 2), ("z", 1)]
    assert [item.value for item in ranged] == [
        [{"key": "0", "value": 1}, {"key": "1", "value": 2}],
        [{"key": "2", "value": 3}, {"key": "3", "value": 4}],
        [{"key": "4", "value": 5}],
    ]
    assert [(item.key, item.value) for item in manifested] == [
        ("b", 2),
        ("1", {"value": 3}),
    ]


def test_loop_spec_rejects_generated_task_run_limit_before_execution() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "bounded",
            "type": "core.foreach",
            "items": [1],
            "maxIterations": 3,
            "maxTaskRuns": 2,
            "tasks": [{"id": "one", "type": "core.return"}],
        }
    )

    with pytest.raises(ValueError, match="maxTaskRuns"):
        parse_loop_spec(task)


def test_foreach_resumes_acknowledged_iterations_and_spills_large_ordered_results(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "restart_loop",
                "namespace": f"tests.loops.{uuid4().hex}",
                "tasks": [
                    {
                        "id": "loop",
                        "type": "core.foreach",
                        "range": {"end": 4},
                        "maxConcurrency": 1,
                        "inlinePayloadBytes": 1,
                        "tasks": [{"id": "capture", "type": "tests.capture"}],
                    }
                ],
            }
        )
        calls: list[int] = []
        interrupted = False

        async def interrupt_once(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            nonlocal interrupted
            del task
            assert context.iteration is not None
            index = context.iteration.index
            calls.append(index)
            assert context.iteration.parent["taskId"] == "loop"
            if index == 1 and not interrupted:
                interrupted = True
                raise asyncio.CancelledError
            return {"index": index, "key": context.iteration.key}

        store = MemoryObjectStore()
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(
            repository,
            handlers={"tests.capture": interrupt_once},
            resource_registry=registered_test_task_registry("tests.capture"),
            object_store=store,
        )
        execution_id = await executor.create_execution(flow, tenant_id="default")
        try:
            with pytest.raises(asyncio.CancelledError):
                await executor.run_ready(flow, execution_id, tenant_id="default")
            after_interrupt = await repository.list_task_runs(
                execution_id,
                tenant_id="default",
            )
            assert (
                next(
                    item
                    for item in after_interrupt
                    if item.task_id == "capture" and item.iteration_key == "loop:00000000"
                ).state
                is TaskRunState.SUCCESS
            )
            await engine.dispose()

            engine = create_async_engine(migrated_test_database_url)
            repository = PostgresExecutionRepository(engine)
            resumed = await InProcessExecutor(
                repository,
                handlers={"tests.capture": interrupt_once},
                object_store=store,
            ).run_to_completion(flow, execution_id, tenant_id="default")

            assert resumed.state is ExecutionState.SUCCESS
            assert calls.count(0) == 1
            assert calls.count(1) == 2
            loop_run = next(item for item in resumed.task_runs if item.task_id == "loop")
            assert loop_run.result is not None
            uri = str(loop_run.result["manifestUri"])
            stored = json.loads(store.objects[uri])
            assert [item["index"] for item in stored["iterations"]] == [0, 1, 2, 3]
        finally:
            await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_loop_controls_conditions_failure_policies_and_bounds_are_deterministic(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        execution_ids: list[UUID] = []

        async def fail_first(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task
            assert context.iteration is not None
            if context.iteration.index == 0:
                raise ValueError("expected iteration failure")
            return {"index": context.iteration.index}

        try:
            control_flow = FlowDefinition.model_validate(
                {
                    "id": "loop_controls",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "controlled",
                            "type": "core.foreach",
                            "range": {"end": 10},
                            "continueIf": "{{ iteration.index == 1 }}",
                            "breakIf": "{{ iteration.index == 3 }}",
                            "tasks": [
                                {
                                    "id": "echo_control",
                                    "type": "core.return",
                                    "value": "{{ iteration.index }}",
                                }
                            ],
                        },
                        {
                            "id": "while_loop",
                            "type": "core.while",
                            "condition": "{{ iteration.index < 3 }}",
                            "maxIterations": 5,
                            "tasks": [
                                {
                                    "id": "echo_while",
                                    "type": "core.return",
                                    "value": "{{ iteration.index }}",
                                }
                            ],
                        },
                        {
                            "id": "until_loop",
                            "type": "core.until",
                            "condition": "{{ iteration.index >= 2 }}",
                            "maxIterations": 5,
                            "tasks": [
                                {
                                    "id": "echo_until",
                                    "type": "core.return",
                                    "value": "{{ iteration.index }}",
                                }
                            ],
                        },
                    ],
                }
            )
            control_executor = InProcessExecutor(repository)
            control_execution_id = await control_executor.create_execution(
                control_flow,
                tenant_id="default",
            )
            execution_ids.append(control_execution_id)
            controlled = await control_executor.run_to_completion(
                control_flow,
                control_execution_id,
                tenant_id="default",
            )
            results = {
                item.task_id: item.result
                for item in controlled.task_runs
                if item.iteration_key is None
            }
            assert results["controlled"]["iterationCount"] == 4
            assert [item["state"] for item in results["controlled"]["iterations"]] == [
                "SUCCESS",
                "CONTINUED",
                "SUCCESS",
                "SUCCESS",
            ]
            assert results["controlled"]["iterations"][-1]["control"] == "BREAK"
            assert results["while_loop"]["iterationCount"] == 3
            assert results["until_loop"]["iterationCount"] == 3

            continue_flow = FlowDefinition.model_validate(
                {
                    "id": "continue_failures",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "continue_loop",
                            "type": "core.foreach",
                            "items": [0, 1],
                            "failurePolicy": "CONTINUE_ON_ERROR",
                            "tasks": [{"id": "maybe_fail", "type": "tests.fail_first"}],
                        }
                    ],
                }
            )
            continue_executor = InProcessExecutor(
                repository,
                handlers={"tests.fail_first": fail_first},
                resource_registry=registered_test_task_registry("tests.fail_first"),
            )
            continue_execution_id = await continue_executor.create_execution(
                continue_flow,
                tenant_id="default",
            )
            execution_ids.append(continue_execution_id)
            continued = await continue_executor.run_to_completion(
                continue_flow,
                continue_execution_id,
                tenant_id="default",
            )
            continue_result = next(
                item for item in continued.task_runs if item.task_id == "continue_loop"
            ).result
            assert continue_result is not None
            assert [item["state"] for item in continue_result["iterations"]] == [
                "FAILED",
                "SUCCESS",
            ]

            bounded_flow = FlowDefinition.model_validate(
                {
                    "id": "bounded_while",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "bounded_loop",
                            "type": "core.while",
                            "condition": "{{ true }}",
                            "maxIterations": 2,
                            "tasks": [{"id": "bounded_child", "type": "core.return"}],
                        }
                    ],
                }
            )
            bounded_executor = InProcessExecutor(repository)
            bounded_execution_id = await bounded_executor.create_execution(
                bounded_flow,
                tenant_id="default",
            )
            execution_ids.append(bounded_execution_id)
            with pytest.raises(TaskExecutionError):
                await bounded_executor.run_ready(
                    bounded_flow,
                    bounded_execution_id,
                    tenant_id="default",
                )
            bounded_runs = await repository.list_task_runs(
                bounded_execution_id,
                tenant_id="default",
            )
            bounded_parent = next(item for item in bounded_runs if item.task_id == "bounded_loop")
            assert bounded_parent.result is not None
            assert "maxIterations=2" in bounded_parent.result["error"]
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())


def test_foreach_parallelism_collect_all_and_duration_limit(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        execution_ids: list[UUID] = []
        active = 0
        max_active = 0

        async def staggered(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            nonlocal active, max_active
            del task
            assert context.iteration is not None
            active += 1
            max_active = max(max_active, active)
            try:
                await asyncio.sleep((4 - context.iteration.index) * 0.01)
                return {"index": context.iteration.index}
            finally:
                active -= 1

        async def fail_first(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task
            assert context.iteration is not None
            if context.iteration.index == 0:
                raise ValueError("expected iteration failure")
            return {"index": context.iteration.index}

        async def slow(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task, context
            await asyncio.sleep(0.05)
            return {}

        try:
            parallel_flow = FlowDefinition.model_validate(
                {
                    "id": "parallel_loop",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "parallel",
                            "type": "core.foreach",
                            "range": {"end": 4},
                            "maxConcurrency": 3,
                            "tasks": [{"id": "staggered", "type": "tests.staggered"}],
                        }
                    ],
                }
            )
            parallel_executor = InProcessExecutor(
                repository,
                handlers={"tests.staggered": staggered},
                resource_registry=registered_test_task_registry("tests.staggered"),
            )
            parallel_id = await parallel_executor.create_execution(
                parallel_flow,
                tenant_id="default",
            )
            execution_ids.append(parallel_id)
            parallel = await parallel_executor.run_to_completion(
                parallel_flow,
                parallel_id,
                tenant_id="default",
            )
            parallel_result = next(
                item for item in parallel.task_runs if item.task_id == "parallel"
            ).result
            assert parallel_result is not None
            assert max_active == 3
            assert [item["index"] for item in parallel_result["iterations"]] == [0, 1, 2, 3]
            static_runs = await repository.list_task_runs(
                parallel_id,
                tenant_id="default",
                include_iterations=False,
            )
            summaries = await repository.list_iteration_summaries(
                parallel_id,
                tenant_id="default",
            )
            assert [item.task_id for item in static_runs] == ["parallel"]
            assert len(summaries) == 1
            assert summaries[0].iteration_count == 4
            assert summaries[0].succeeded == 4

            collect_flow = FlowDefinition.model_validate(
                {
                    "id": "collect_all_loop",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "collect",
                            "type": "core.foreach",
                            "items": [0, 1, 2],
                            "failurePolicy": "COLLECT_ALL",
                            "tasks": [{"id": "maybe_fail", "type": "tests.fail_first"}],
                        }
                    ],
                }
            )
            collect_executor = InProcessExecutor(
                repository,
                handlers={"tests.fail_first": fail_first},
                resource_registry=registered_test_task_registry("tests.fail_first"),
            )
            collect_id = await collect_executor.create_execution(
                collect_flow,
                tenant_id="default",
            )
            execution_ids.append(collect_id)
            with pytest.raises(TaskExecutionError):
                await collect_executor.run_ready(
                    collect_flow,
                    collect_id,
                    tenant_id="default",
                )
            collect_runs = await repository.list_task_runs(collect_id, tenant_id="default")
            collect_result = next(item for item in collect_runs if item.task_id == "collect").result
            assert collect_result is not None
            assert [item["state"] for item in collect_result["iterations"]] == [
                "FAILED",
                "SUCCESS",
                "SUCCESS",
            ]

            duration_flow = FlowDefinition.model_validate(
                {
                    "id": "duration_loop",
                    "namespace": f"tests.loops.{uuid4().hex}",
                    "tasks": [
                        {
                            "id": "duration",
                            "type": "core.foreach",
                            "items": [0, 1],
                            "maxDurationSeconds": 0.01,
                            "tasks": [{"id": "slow", "type": "tests.slow"}],
                        }
                    ],
                }
            )
            duration_executor = InProcessExecutor(
                repository,
                handlers={"tests.slow": slow},
                resource_registry=registered_test_task_registry("tests.slow"),
            )
            duration_id = await duration_executor.create_execution(
                duration_flow,
                tenant_id="default",
            )
            execution_ids.append(duration_id)
            with pytest.raises(TaskExecutionError):
                await duration_executor.run_ready(
                    duration_flow,
                    duration_id,
                    tenant_id="default",
                )
            duration_runs = await repository.list_task_runs(duration_id, tenant_id="default")
            duration_result = next(
                item for item in duration_runs if item.task_id == "duration"
            ).result
            assert duration_result is not None
            assert "maxDurationSeconds=0.01" in duration_result["error"]
        finally:
            for execution_id in execution_ids:
                await cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
