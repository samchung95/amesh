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
from amesh.ports import (
    ExecutionRepository,
    RunnerOutputRedactor,
    TaskRunState,
    redact_runner_payload,
)


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


def test_completion_redacts_declared_outputs_and_secret_canaries() -> None:
    canary = "evidence-canary-never-persist"
    output, evidence = normalize_task_completion(
        TaskCompletion(
            output={"accessToken": canary, "nested": {"message": f"seen {canary}"}},
            sensitiveOutputKeys=("accessToken",),
            logs=(TaskLogRecord(message=f"received {canary}", fields={"password": canary}),),
            metrics=(TaskMetricRecord(name="requests", value=1, labels={"token": canary}),),
        ),
        TaskResourceLimits(),
        secret_values=(canary,),
    )

    serialized = repr((output, evidence))
    assert canary not in serialized
    assert output["accessToken"] == "[REDACTED]"
    assert evidence["logs"][0]["redacted"] is True
    assert evidence["outputSensitive"] is True


def test_completion_redacts_compound_secret_field_names() -> None:
    output, _ = normalize_task_completion(
        TaskCompletion(
            output={
                "audit.apiKey": "must-hide",
                "authorizationHeader": "must-hide-too",
                "tokenCount": 4,
            }
        ),
        TaskResourceLimits(),
    )

    assert output["audit.apiKey"] == "[REDACTED]"
    assert output["authorizationHeader"] == "[REDACTED]"
    assert output["tokenCount"] == 4


def test_runner_redactor_handles_chunk_boundaries_and_compound_fields() -> None:
    canary = "split-secret"
    redactor = RunnerOutputRedactor((canary,))
    rendered = redactor.feed("prefix-split") + redactor.feed("-secret-suffix") + redactor.flush()

    assert rendered == "prefix-[REDACTED]-suffix"
    payload = redact_runner_payload(
        {"audit.apiKey": canary, "message": f"seen {canary}"},
        (canary,),
    )
    assert payload == {"audit.apiKey": "[REDACTED]", "message": "seen [REDACTED]"}


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
    execution = SimpleNamespace(
        tenant_id="default",
        namespace="tests.contract",
        execution_id=uuid4(),
    )
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
    execution = SimpleNamespace(
        tenant_id="default",
        namespace="tests.contract",
        execution_id=uuid4(),
    )
    task_run = SimpleNamespace(task_run_id=uuid4(), current_attempt=1)

    with pytest.raises(TaskConfigurationError, match="undeclared files: extra"):
        asyncio.run(
            executor._resolve_context_resources(
                flow.tasks[0],
                cast(Any, execution),
                cast(Any, task_run),
            )
        )


def test_task_render_failure_redacts_context_secrets_before_context_exists() -> None:
    canary = "render-failure-secret"

    class ContextProvider:
        async def resolve(self, request: object) -> TaskContextResources:
            del request
            return TaskContextResources(secrets={"TOKEN": canary})

    class FailingExpressionEngine:
        compatibility_version = "fixture"

        def render_task(self, task: object, context: Any) -> object:
            del task
            raise ValueError(f"render failed with {context.secrets['TOKEN']}")

    class Repository:
        def __init__(self) -> None:
            self.failure: dict[str, Any] | None = None

        async def fail_task(
            self, task_run_id: object, attempt: int, reason: str, **kwargs: object
        ) -> None:
            del task_run_id, attempt, kwargs
            self.failure = {"reason": reason}

    task = FlowDefinition.model_validate(
        {
            "id": "render_failure",
            "namespace": "tests.contract",
            "tasks": [
                {
                    "id": "render",
                    "type": "core.return",
                    "value": "ready",
                    "contract": {"secretScopes": ["TOKEN"]},
                }
            ],
        }
    ).tasks[0]
    flow = FlowDefinition(id="render_failure", namespace="tests.contract", tasks=[task])
    execution_id = uuid4()
    task_run_id = uuid4()
    execution = SimpleNamespace(
        tenant_id="default",
        namespace="tests.contract",
        execution_id=execution_id,
        state=ExecutionState.RUNNING,
        created_at=None,
        inputs={},
        labels={},
        trigger={},
    )
    task_run = SimpleNamespace(
        task_run_id=task_run_id,
        execution_id=execution_id,
        task_id="render",
        state=TaskRunState.RUNNING,
        current_attempt=1,
        evidence={},
    )
    repository = Repository()
    executor = InProcessExecutor(
        cast(ExecutionRepository, repository),
        expressions=cast(Any, FailingExpressionEngine()),
        context_provider=ContextProvider(),
    )

    outcome = asyncio.run(
        executor._run_task(
            flow,
            cast(Any, execution),
            cast(Any, task_run),
            task,
            {},
        )
    )

    assert outcome.claimed is True
    assert repository.failure == {
        "reason": "task 'render' failed [NON_RETRYABLE]: render failed with [REDACTED]"
    }
    assert canary not in repr(repository.failure)
