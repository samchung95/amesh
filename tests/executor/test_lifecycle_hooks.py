from __future__ import annotations

import asyncio
import os
from datetime import timedelta
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.task_schemas import registered_test_task_registry

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState, TaskRunLifecyclePhase, TaskRunState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import (
    ExecutionBlockedError,
    InProcessExecutor,
    TaskExecutionContext,
    TaskPlatformError,
    TaskUserCodeError,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.ports import ExecutionInterventionAction

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_error_finally_and_after_execution_hooks_are_durable_and_ordered() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

        async def user_failure(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task, context
            raise TaskUserCodeError("primary user failure")

        async def cleanup_failure(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task, context
            raise TaskPlatformError("cleanup platform failure")

        handlers = {
            "tests.user_failure": user_failure,
            "tests.cleanup_failure": cleanup_failure,
        }
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        try:
            repository = PostgresExecutionRepository(engine)

            success_flow = FlowDefinition.model_validate(
                {
                    "id": "success_lifecycle",
                    "namespace": "tests.lifecycle",
                    "tasks": [{"id": "main", "type": "core.return", "value": "done"}],
                    "errors": [{"id": "unused_error", "type": "core.return"}],
                    "finally": [
                        {
                            "id": "success_finally",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                    "afterExecution": [
                        {
                            "id": "success_after",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                }
            )
            success_executor = InProcessExecutor(repository)
            success_id = await success_executor.create_execution(
                success_flow,
                tenant_id="default",
            )
            assert {
                item.task_id
                for item in await repository.list_task_runs(success_id, tenant_id="default")
            } == {"main", "unused_error", "success_finally", "success_after"}
            for _ in range(8):
                interrupted = await success_executor.run_ready(
                    success_flow,
                    success_id,
                    tenant_id="default",
                )
                interrupted_runs = {item.task_id: item for item in interrupted.task_runs}
                if (
                    interrupted.state is ExecutionState.SUCCESS
                    and interrupted_runs["success_after"].state is TaskRunState.WAITING
                ):
                    break
            else:
                raise AssertionError("success execution did not reach the afterExecution boundary")

            await engine.dispose()
            engine = create_async_engine(database.database_url)
            repository = PostgresExecutionRepository(engine)
            completed = await InProcessExecutor(repository).run_to_completion(
                success_flow,
                success_id,
                tenant_id="default",
            )
            success_runs = {item.task_id: item for item in completed.task_runs}
            success_execution = await repository.get_execution(success_id, tenant_id="default")
            assert completed.state is ExecutionState.SUCCESS
            assert success_runs["unused_error"].current_attempt == 0
            assert success_runs["success_finally"].result == {"value": "RUNNING"}
            assert success_runs["success_after"].result == {"value": "SUCCESS"}
            assert success_execution.lifecycle_evidence["status"] == "COMPLETE"

            async with engine.connect() as connection:
                terminal_before_after = await connection.scalar(
                    text(
                        "SELECT e.terminal_at <= a.started_at "
                        "FROM task_attempts a JOIN task_runs tr ON tr.id = a.task_run_id "
                        "JOIN executions e ON e.id = tr.execution_id "
                        "WHERE e.id = :execution_id AND tr.task_path = 'success_after'"
                    ),
                    {"execution_id": success_id},
                )
            assert terminal_before_after is True

            failure_flow = FlowDefinition.model_validate(
                {
                    "id": "failure_lifecycle",
                    "namespace": "tests.lifecycle",
                    "tasks": [
                        {
                            "id": "group",
                            "type": "core.sequential",
                            "tasks": [{"id": "boom", "type": "tests.user_failure"}],
                            "errors": [
                                {
                                    "id": "local_match",
                                    "type": "core.return",
                                    "errorSelector": {
                                        "states": ["FAILED"],
                                        "categories": ["USER_CODE"],
                                        "taskIds": ["boom"],
                                        "condition": "{{ error.taskId == 'boom' }}",
                                    },
                                    "value": {
                                        "notification": "incident-created",
                                        "compensationCommand": "undo-primary",
                                        "diagnosticArtifacts": ["primary.log"],
                                        "taskId": "{{ error.taskId }}",
                                    },
                                },
                                {
                                    "id": "local_miss",
                                    "type": "core.return",
                                    "errorSelector": {"categories": ["PLATFORM"]},
                                },
                            ],
                        }
                    ],
                    "errors": [
                        {"id": "cleanup_failure", "type": "tests.cleanup_failure"},
                        {
                            "id": "global_handler",
                            "type": "core.return",
                            "runIf": "{{ error.state == 'FAILED' }}",
                            "value": "global-handled",
                        },
                    ],
                    "finally": [
                        {
                            "id": "failure_finally",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                    "afterExecution": [
                        {
                            "id": "failure_after",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                }
            )
            failure_executor = InProcessExecutor(
                repository,
                handlers=handlers,
                resource_registry=registered_test_task_registry(*handlers),
            )
            failure_id = await failure_executor.create_execution(
                failure_flow,
                tenant_id="default",
            )
            with pytest.raises(ExecutionBlockedError, match="stopped in state FAILED"):
                await failure_executor.run_to_completion(
                    failure_flow,
                    failure_id,
                    tenant_id="default",
                )
            failure_execution = await repository.get_execution(failure_id, tenant_id="default")
            failure_runs = {
                item.task_id: item
                for item in await repository.list_task_runs(failure_id, tenant_id="default")
            }
            assert failure_execution.state is ExecutionState.FAILED
            assert failure_execution.lifecycle_evidence["status"] == "COMPLETE"
            assert (
                failure_execution.lifecycle_evidence["primary"]["errors"][-1]["category"]
                == "USER_CODE"
            )
            cleanup_failures = failure_execution.lifecycle_evidence["phases"]["ERROR"]["failures"]
            assert len(cleanup_failures) == 1
            assert cleanup_failures[0]["taskId"] == "cleanup_failure"
            assert cleanup_failures[0]["handlerOwnerId"] == "flow"
            assert cleanup_failures[0]["state"] == "FAILED"
            assert cleanup_failures[0]["category"] == "PLATFORM"
            assert "cleanup platform failure" in cleanup_failures[0]["error"]
            assert failure_runs["local_match"].result == {
                "value": {
                    "notification": "incident-created",
                    "compensationCommand": "undo-primary",
                    "diagnosticArtifacts": ["primary.log"],
                    "taskId": "boom",
                }
            }
            assert failure_runs["local_miss"].current_attempt == 0
            assert failure_runs["global_handler"].state is TaskRunState.SUCCESS
            assert failure_runs["failure_finally"].result == {"value": "RUNNING"}
            assert failure_runs["failure_after"].result == {"value": "FAILED"}
            assert failure_runs["failure_after"].lifecycle_phase is (
                TaskRunLifecyclePhase.AFTER_EXECUTION
            )

            cancellation_flow = FlowDefinition.model_validate(
                {
                    "id": "cancel_lifecycle",
                    "namespace": "tests.lifecycle",
                    "tasks": [{"id": "cancelled_main", "type": "core.return"}],
                    "errors": [
                        {
                            "id": "cancel_handler",
                            "type": "core.return",
                            "errorSelector": {
                                "states": ["CANCELLED"],
                                "categories": ["CANCELLED"],
                            },
                            "value": "cancel-handled",
                        }
                    ],
                    "finally": [
                        {
                            "id": "cancel_finally",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                    "afterExecution": [
                        {
                            "id": "cancel_after",
                            "type": "core.return",
                            "value": "{{ execution.state }}",
                        }
                    ],
                }
            )
            cancellation_executor = InProcessExecutor(repository)
            cancellation_id = await cancellation_executor.create_execution(
                cancellation_flow,
                tenant_id="default",
            )
            cancellation_execution = await repository.get_execution(
                cancellation_id,
                tenant_id="default",
            )
            cancelling = await repository.apply_execution_intervention(
                cancellation_id,
                ExecutionInterventionAction.REQUEST_CANCEL,
                tenant_id="default",
                expected_version=cancellation_execution.version,
                expected_epoch=cancellation_execution.epoch,
                actor_id="test:operator",
                reason="acceptance cancellation",
                grace_period=timedelta(seconds=1),
            )
            await repository.apply_execution_intervention(
                cancellation_id,
                ExecutionInterventionAction.CONFIRM_CANCEL,
                tenant_id="default",
                expected_version=cancelling.version,
                expected_epoch=cancelling.epoch,
                actor_id="test:operator",
                reason="no running attempts",
            )
            with pytest.raises(ExecutionBlockedError, match="stopped in state CANCELLED"):
                await cancellation_executor.run_to_completion(
                    cancellation_flow,
                    cancellation_id,
                    tenant_id="default",
                )
            cancellation_runs = {
                item.task_id: item
                for item in await repository.list_task_runs(cancellation_id, tenant_id="default")
            }
            assert cancellation_runs["cancelled_main"].state is TaskRunState.CANCELLED
            assert cancellation_runs["cancel_handler"].result == {"value": "cancel-handled"}
            assert cancellation_runs["cancel_finally"].result == {"value": "CANCELLED"}
            assert cancellation_runs["cancel_after"].result == {"value": "CANCELLED"}
            cancellation_execution = await repository.get_execution(
                cancellation_id,
                tenant_id="default",
            )
            assert cancellation_execution.lifecycle_evidence["status"] == "COMPLETE"
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
