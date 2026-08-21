from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import (
    InProcessExecutor,
    TaskArtifactRecord,
    TaskCompletion,
    TaskContextRequest,
    TaskContextResources,
    TaskDeferral,
    TaskExecutionContext,
    TaskExitMetadata,
    TaskLogRecord,
    TaskMetricRecord,
    normalize_task_completion,
)
from amesh.ports import TaskRunState, TaskStateConflictError

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


async def _cleanup_execution(engine: AsyncEngine, execution_id: UUID) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("DELETE FROM messages_outbox WHERE partition_key = :key"),
            {"key": f"execution:{execution_id}"},
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


def _flow(name: str) -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": name,
            "namespace": f"tests.deferral.{uuid4().hex}",
            "tasks": [
                {
                    "id": "callback",
                    "type": "test.defer",
                    "contract": {
                        "secretScopes": ["callbacks:write"],
                        "files": {"payload": "/requested/payload.json"},
                    },
                }
            ],
        }
    )


def test_durable_deferral_context_resume_evidence_and_restart() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

        token = "resume-token-with-at-least-sixteen-characters"
        requests: list[TaskContextRequest] = []
        handler_calls = 0

        class ContextProvider:
            async def resolve(self, request: TaskContextRequest) -> TaskContextResources:
                requests.append(request)
                return TaskContextResources(
                    secrets={"callbackKey": "secret-value"},
                    files={"payload": "C:/sandbox/payload.json"},
                )

        async def defer_handler(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> TaskDeferral:
            nonlocal handler_calls
            del task
            handler_calls += 1
            assert context.secret_scopes == ("callbacks:write",)
            assert context.secrets == {"callbackKey": "secret-value"}
            assert context.files == {"payload": "C:/sandbox/payload.json"}
            assert await context.cancellation.requested() is False
            return TaskDeferral(
                resumeToken=token,
                metadata={"provider": "test"},
                expiresAt=datetime.now(UTC) + timedelta(minutes=5),
            )

        flow = _flow("durable_callback")
        first_engine = create_async_engine(TEST_DATABASE_URL)
        first_repository = PostgresExecutionRepository(first_engine)
        first_executor = InProcessExecutor(
            first_repository,
            handlers={"test.defer": defer_handler},
            context_provider=ContextProvider(),
        )
        execution_id = await first_executor.create_execution(flow, tenant_id="default")
        try:
            deferred_progress = await first_executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )
            assert deferred_progress.state is ExecutionState.RUNNING
            assert deferred_progress.task_runs[0].state is TaskRunState.RUNNING
            assert handler_calls == 1
            assert requests[0].secret_scopes == ("callbacks:write",)
            await first_engine.dispose()

            resumed_engine = create_async_engine(TEST_DATABASE_URL)
            resumed_repository = PostgresExecutionRepository(resumed_engine)
            try:
                restarted = await InProcessExecutor(resumed_repository).run_to_completion(
                    flow,
                    execution_id,
                    tenant_id="default",
                )
                assert restarted.state is ExecutionState.RUNNING
                assert handler_calls == 1
                task_run = restarted.task_runs[0]
                deferral = await resumed_repository.get_task_deferral(
                    task_run.task_run_id,
                    tenant_id="default",
                )
                assert deferral is not None
                assert deferral.state == "WAITING"
                assert deferral.metadata == {"provider": "test"}

                with pytest.raises(TaskStateConflictError, match="invalid or unavailable"):
                    await resumed_repository.resume_deferred_task(
                        task_run.task_run_id,
                        "wrong-token-with-at-least-sixteen-characters",
                        {"answer": 42},
                        tenant_id="default",
                    )

                output, evidence = normalize_task_completion(
                    TaskCompletion(
                        output={"answer": 42},
                        logs=(TaskLogRecord(message="callback accepted"),),
                        metrics=(TaskMetricRecord(name="callbacks", value=1),),
                        artifacts=(
                            TaskArtifactRecord(uri="s3://bucket/result.json", sizeBytes=64),
                        ),
                        exit=TaskExitMetadata(code=0),
                    ),
                    flow.tasks[0].contract.resource_limits,
                )
                completed = await resumed_repository.resume_deferred_task(
                    task_run.task_run_id,
                    token,
                    output,
                    tenant_id="default",
                    evidence=evidence,
                )
                duplicate = await resumed_repository.resume_deferred_task(
                    task_run.task_run_id,
                    token,
                    {"ignored": "duplicate"},
                    tenant_id="default",
                    evidence={"ignored": True},
                )
                assert completed.state is TaskRunState.SUCCESS
                assert completed.result == {"answer": 42}
                assert duplicate == completed
                assert completed.evidence["logs"][0]["message"] == "callback accepted"

                with pytest.raises(TaskStateConflictError, match="attempt 0 is not running"):
                    await resumed_repository.complete_task(
                        task_run.task_run_id,
                        0,
                        {"stale": True},
                        tenant_id="default",
                    )

                finished = await InProcessExecutor(resumed_repository).run_to_completion(
                    flow,
                    execution_id,
                    tenant_id="default",
                )
                assert finished.state is ExecutionState.SUCCESS

                async with resumed_engine.connect() as connection:
                    attempt = (
                        (
                            await connection.execute(
                                text(
                                    "SELECT id, attempt, evidence FROM task_attempts "
                                    "WHERE task_run_id = :task_run_id"
                                ),
                                {"task_run_id": task_run.task_run_id},
                            )
                        )
                        .mappings()
                        .one()
                    )
                    stored_token = await connection.scalar(
                        text(
                            "SELECT resume_token_digest FROM task_deferrals "
                            "WHERE task_run_id = :task_run_id"
                        ),
                        {"task_run_id": task_run.task_run_id},
                    )
                    event_types = (
                        (
                            await connection.execute(
                                text(
                                    "SELECT event_type FROM task_run_events "
                                    "WHERE task_run_id = :task_run_id ORDER BY sequence"
                                ),
                                {"task_run_id": task_run.task_run_id},
                            )
                        )
                        .scalars()
                        .all()
                    )
                assert attempt["id"] is not None
                assert attempt["attempt"] == 1
                assert attempt["evidence"]["artifacts"][0]["sizeBytes"] == 64
                assert stored_token != token
                assert len(stored_token) == 64
                assert event_types == [
                    "TaskRunCreated",
                    "TaskRunStarted",
                    "TaskRunDeferred",
                    "TaskRunSucceeded",
                ]
            finally:
                await _cleanup_execution(resumed_engine, execution_id)
                await resumed_engine.dispose()
        finally:
            await first_engine.dispose()

    asyncio.run(scenario())


def test_expired_deferral_cannot_resume() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        token = "expired-token-with-at-least-sixteen-characters"

        async def defer_handler(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> TaskDeferral:
            del task, context
            return TaskDeferral(
                resumeToken=token,
                expiresAt=datetime.now(UTC) - timedelta(seconds=1),
            )

        flow = FlowDefinition.model_validate(
            {
                "id": "expired_callback",
                "namespace": f"tests.deferral.{uuid4().hex}",
                "tasks": [{"id": "callback", "type": "test.defer"}],
            }
        )
        engine = create_async_engine(TEST_DATABASE_URL)
        repository = PostgresExecutionRepository(engine)
        executor = InProcessExecutor(repository, handlers={"test.defer": defer_handler})
        execution_id = await executor.create_execution(flow, tenant_id="default")
        try:
            progress = await executor.run_ready(flow, execution_id, tenant_id="default")
            task_run = progress.task_runs[0]
            with pytest.raises(TaskStateConflictError, match="expired"):
                await repository.resume_deferred_task(
                    task_run.task_run_id,
                    token,
                    {},
                    tenant_id="default",
                )
            deferral = await repository.get_task_deferral(
                task_run.task_run_id,
                tenant_id="default",
            )
            assert deferral is not None
            assert deferral.state == "EXPIRED"
            failed = await executor.run_ready(flow, execution_id, tenant_id="default")
            assert failed.state is ExecutionState.FAILED
            assert failed.task_runs[0].state is TaskRunState.FAILED
        finally:
            await _cleanup_execution(engine, execution_id)
            await engine.dispose()

    asyncio.run(scenario())
