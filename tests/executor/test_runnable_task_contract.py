from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest

from amesh.domain import ExecutionState, FailureCategory
from amesh.dsl import FlowDefinition, TaskResourceLimits
from amesh.executor import (
    InProcessExecutor,
    TaskArtifactRecord,
    TaskCancellationChannel,
    TaskCompletion,
    TaskConfigurationError,
    TaskContextResources,
    TaskExitMetadata,
    TaskLogRecord,
    TaskMetricRecord,
    TaskPlatformError,
    TaskResourceLimitError,
    TaskUserCodeError,
    normalize_task_completion,
)
from amesh.executor.service import classify_task_failure
from amesh.ports import ExecutionRepository


def test_structured_completion_is_normalized_and_bounded() -> None:
    output, evidence = normalize_task_completion(
        TaskCompletion(
            output={"answer": 42},
            logs=(TaskLogRecord(message="done"),),
            metrics=(TaskMetricRecord(name="tokens", value=7, unit="count"),),
            artifacts=(TaskArtifactRecord(uri="s3://bucket/report.json", sizeBytes=128),),
            exit=TaskExitMetadata(code=0, durationMs=12.5),
        ),
        TaskResourceLimits(),
    )

    assert output == {"answer": 42}
    assert evidence["logs"][0]["message"] == "done"
    assert evidence["metrics"][0]["name"] == "tokens"
    assert evidence["artifacts"][0]["sizeBytes"] == 128
    assert evidence["exit"] == {
        "status": "SUCCESS",
        "code": 0,
        "reason": None,
        "durationMs": 12.5,
    }
    assert evidence["sizes"]["artifactBytes"] == 128


@pytest.mark.parametrize(
    ("completion", "limits", "kind"),
    [
        (
            TaskCompletion(output={"value": "too large"}),
            TaskResourceLimits(maxOutputBytes=4),
            "output",
        ),
        (
            TaskCompletion(logs=(TaskLogRecord(message="too large"),)),
            TaskResourceLimits(maxLogBytes=4),
            "log",
        ),
        (
            TaskCompletion(artifacts=(TaskArtifactRecord(uri="s3://bucket/item", sizeBytes=5),)),
            TaskResourceLimits(maxArtifactBytes=4),
            "artifact",
        ),
    ],
)
def test_completion_limits_reject_oversized_evidence(
    completion: TaskCompletion,
    limits: TaskResourceLimits,
    kind: str,
) -> None:
    with pytest.raises(TaskResourceLimitError, match=kind):
        normalize_task_completion(completion, limits)


def test_task_failure_contract_distinguishes_required_categories() -> None:
    assert (
        classify_task_failure(TaskConfigurationError("bad config")) is FailureCategory.CONFIGURATION
    )
    assert classify_task_failure(TaskUserCodeError("bad code")) is FailureCategory.USER_CODE
    assert classify_task_failure(TaskPlatformError("control plane")) is FailureCategory.PLATFORM
    assert classify_task_failure(OSError("worker unavailable")) is FailureCategory.INFRASTRUCTURE


def test_registered_task_schema_is_checked_before_execution_creation() -> None:
    class Repository:
        async def create_execution(self, *args: object, **kwargs: object) -> None:
            raise AssertionError("invalid task configuration reached persistence")

    flow = FlowDefinition.model_validate(
        {
            "id": "invalid_before_start",
            "namespace": "tests.contract",
            "tasks": [{"id": "log", "type": "core.log"}],
        }
    )
    executor = InProcessExecutor(cast(ExecutionRepository, Repository()))

    with pytest.raises(TaskConfigurationError, match="'message' is a required property"):
        asyncio.run(executor.create_execution(flow, tenant_id="default"))


def test_cancellation_channel_reads_durable_execution_state() -> None:
    class Repository:
        state = ExecutionState.RUNNING

        async def get_execution(self, *args: object, **kwargs: object) -> Any:
            return SimpleNamespace(state=self.state)

    repository = Repository()
    channel = TaskCancellationChannel(
        cast(ExecutionRepository, repository),
        tenant_id="default",
        execution_id=uuid4(),
    )

    assert asyncio.run(channel.requested()) is False
    repository.state = ExecutionState.CANCELLING
    assert asyncio.run(channel.requested()) is True


def test_declared_secret_scope_requires_a_context_provider() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "secret_context",
            "namespace": "tests.contract",
            "tasks": [
                {
                    "id": "custom",
                    "type": "test.custom",
                    "contract": {"secretScopes": ["payments:read"]},
                }
            ],
        }
    )
    executor = InProcessExecutor(cast(ExecutionRepository, object()))
    execution = SimpleNamespace(tenant_id="default", execution_id=uuid4())
    task_run = SimpleNamespace(task_run_id=uuid4(), current_attempt=1)

    with pytest.raises(TaskConfigurationError, match="no context provider"):
        asyncio.run(
            executor._resolve_context_resources(
                flow.tasks[0],
                cast(Any, execution),
                cast(Any, task_run),
            )
        )


def test_context_provider_cannot_add_undeclared_files() -> None:
    class ContextProvider:
        async def resolve(self, request: object) -> TaskContextResources:
            del request
            return TaskContextResources(files={"extra": "/sandbox/extra"})

    flow = FlowDefinition.model_validate(
        {
            "id": "file_context",
            "namespace": "tests.contract",
            "tasks": [
                {
                    "id": "custom",
                    "type": "test.custom",
                    "contract": {"files": {"payload": "/requested/payload"}},
                }
            ],
        }
    )
    executor = InProcessExecutor(
        cast(ExecutionRepository, object()),
        context_provider=ContextProvider(),
    )
    execution = SimpleNamespace(tenant_id="default", execution_id=uuid4())
    task_run = SimpleNamespace(task_run_id=uuid4(), current_attempt=1)

    with pytest.raises(TaskConfigurationError, match="undeclared files: extra"):
        asyncio.run(
            executor._resolve_context_resources(
                flow.tasks[0],
                cast(Any, execution),
                cast(Any, task_run),
            )
        )
