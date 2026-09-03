from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid5

from amesh.domain import (
    AdmissionDecision,
    AdmissionOutcome,
    AdmissionResourceType,
    ExecutionState,
    FailureCategory,
    PolicyDecision,
)
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor.attempt_execution import (
    AttemptExecutionCallbacks,
    execute_task_attempt,
)
from amesh.executor.contracts import (
    ConditionDecision,
    TaskContextResources,
    TaskExecutionContext,
    TaskHandler,
)
from amesh.expressions import NativeExpressionEngine
from amesh.ports import (
    ExecutionRepository,
    PersistedExecution,
    PersistedTaskRun,
    TaskCacheDecision,
    TaskCacheKey,
    TaskCacheLookup,
    TaskCacheRepository,
    TaskRunState,
)

EXECUTION_ID = UUID("018f47f4-a289-7c7e-9f0b-61dcf6e7d900")
TASK_RUN_ID = UUID("018f47f4-a289-7c7e-9f0b-61dcf6e7d901")
NOW = datetime(2026, 1, 1, tzinfo=UTC)


class _Repository:
    def __init__(self, task_run: PersistedTaskRun, events: list[str]) -> None:
        self.task_run = task_run
        self.events = events
        self.completed: tuple[dict[str, Any], dict[str, Any]] | None = None
        self.failed: dict[str, Any] | None = None
        self.retried: dict[str, Any] | None = None

    async def request_admission(self, *_args: Any, **_kwargs: Any) -> AdmissionDecision:
        self.events.append("admission")
        return AdmissionDecision(
            request_id=UUID("00000000-0000-0000-0000-000000000010"),
            resource_type=AdmissionResourceType.TASK,
            resource_id=TASK_RUN_ID,
            outcome=AdmissionOutcome.ADMITTED,
            reason="capacity available",
            created_at=NOW,
            admitted_at=NOW,
        )

    async def start_task(self, *_args: Any, **_kwargs: Any) -> PersistedTaskRun:
        self.events.append("start")
        self.task_run = self.task_run.model_copy(
            update={"state": TaskRunState.RUNNING, "current_attempt": 1}
        )
        return self.task_run

    async def complete_task(
        self,
        _task_run_id: UUID,
        _attempt: int,
        output: dict[str, Any],
        **kwargs: Any,
    ) -> PersistedTaskRun:
        self.events.append("complete")
        self.completed = (output, kwargs["evidence"])
        return self.task_run.model_copy(update={"state": TaskRunState.SUCCESS, "result": output})

    async def record_task_control(
        self,
        *_args: Any,
        **_kwargs: Any,
    ) -> PersistedTaskRun:
        self.events.append("record-control")
        return self.task_run

    async def database_time(self) -> datetime:
        self.events.append("database-time")
        return NOW

    async def retry_task(self, *_args: Any, **kwargs: Any) -> PersistedTaskRun:
        self.events.append("retry")
        self.retried = kwargs
        return self.task_run

    async def fail_task(self, *_args: Any, **kwargs: Any) -> PersistedTaskRun:
        self.events.append("fail")
        self.failed = kwargs
        return self.task_run


class _RetryEngine(NativeExpressionEngine):
    def __init__(self, events: list[str]) -> None:
        super().__init__()
        self.events = events

    def evaluate_condition(self, expression: str, context: Any) -> bool:
        del context
        self.events.append(f"retry-condition:{expression}")
        return True


class _HitCache:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.key: TaskCacheKey | None = None

    async def lookup_or_reserve(
        self,
        key: TaskCacheKey,
        **_kwargs: Any,
    ) -> TaskCacheLookup:
        self.events.append("cache-lookup")
        self.key = key
        return TaskCacheLookup(
            decision=TaskCacheDecision.HIT,
            reason="matching entry",
            key_hash=key.key_hash,
            output={"cached": True},
            evidence={"stored": True},
        )


def _execution(inputs: dict[str, Any] | None = None) -> PersistedExecution:
    return PersistedExecution(
        execution_id=EXECUTION_ID,
        tenant_id="default",
        state=ExecutionState.RUNNING,
        epoch=1,
        version=1,
        namespace="tests.attempt",
        flow_id="attempt-flow",
        inputs=inputs or {},
        created_at=NOW,
        updated_at=NOW,
    )


def _task_run() -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=TASK_RUN_ID,
        execution_id=EXECUTION_ID,
        task_id="work",
        state=TaskRunState.WAITING,
        current_attempt=0,
        version=1,
    )


def _flow(task: TaskDefinition) -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "attempt-flow",
            "namespace": "tests.attempt",
            "inputs": [{"id": "name", "type": "STRING"}],
            "tasks": [task.model_dump(mode="json", by_alias=True, exclude_none=True)],
        }
    )


def _policy_decision() -> PolicyDecision:
    return cast(
        PolicyDecision,
        SimpleNamespace(
            decision_id=UUID("00000000-0000-0000-0000-000000000020"),
            engine_version="test/v1",
            stage=SimpleNamespace(value="TASK_DISPATCH"),
            outcome=SimpleNamespace(value="ALLOW"),
            allowed=True,
            pinned_policies=(),
            matched_rules=(),
            warnings=(),
            mutations=(),
            required_approvals=(),
            input_hash="a" * 64,
            evaluation_duration_ms=0.0,
        ),
    )


def _callbacks(
    repository: _Repository,
    events: list[str],
    handler: TaskHandler,
    *,
    expressions: NativeExpressionEngine | None = None,
    task_cache: TaskCacheRepository | None = None,
    with_dispatch: bool = False,
) -> AttemptExecutionCallbacks:
    def evaluate_condition(*_args: Any, **_kwargs: Any) -> ConditionDecision:
        events.append("condition")
        return ConditionDecision(True, {"control": {"runIf": {"result": True}}})

    async def resolve_context(
        _task: TaskDefinition,
        _execution: PersistedExecution,
        _task_run: PersistedTaskRun,
        **kwargs: Any,
    ) -> TaskContextResources:
        if kwargs.get("resolve_values", True):
            events.append("context-values")
            return TaskContextResources(secrets={"token": "top-secret"})
        events.append("context-files")
        return TaskContextResources(files=dict(kwargs["declared_files"]))

    async def run_loop(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise AssertionError("loop callback was unexpectedly used")

    async def enforce_dispatch(*_args: Any, **_kwargs: Any) -> PolicyDecision:
        events.append("dispatch")
        return _policy_decision()

    return AttemptExecutionCallbacks(
        repository=cast(ExecutionRepository, repository),
        handlers={"test.task": handler},
        expressions=expressions or NativeExpressionEngine(),
        evaluate_task_condition=evaluate_condition,
        resolve_context_resources=resolve_context,
        run_loop=run_loop,
        task_cache=task_cache,
        dispatch_policy_enforcer=enforce_dispatch if with_dispatch else None,
    )


def test_attempt_preserves_admission_dispatch_context_and_completion_order() -> None:
    async def scenario() -> None:
        events: list[str] = []
        task = TaskDefinition.model_validate(
            {
                "id": "work",
                "type": "test.task",
                "value": "{{ inputs.name }}",
                "inputFiles": {"child.txt": "child://{{ inputs.name }}"},
                "workspaceQuotaBytes": 100,
                "concurrency": [{"id": "one", "scope": "TENANT", "limit": 1}],
            }
        )
        workspace = TaskDefinition.model_validate(
            {
                "id": "workspace",
                "type": "core.workingDirectory",
                "inputFiles": {"parent.txt": "parent://{{ inputs.name }}"},
                "workspaceQuotaBytes": 200,
                "tasks": [task.model_dump(mode="json", by_alias=True, exclude_none=True)],
            }
        )
        repository = _Repository(_task_run(), events)
        contexts: list[TaskExecutionContext] = []

        async def handler(
            rendered_task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, Any]:
            events.append("invoke")
            contexts.append(context)
            return {"value": rendered_task.configuration.handler_view()["value"]}

        outcome = await execute_task_attempt(
            _callbacks(repository, events, handler, with_dispatch=True),
            _flow(task),
            _execution({"name": "Ada"}),
            repository.task_run,
            task,
            {},
            workspace_parent=workspace,
        )

        assert outcome.claimed is True and outcome.failure is None
        assert events == [
            "admission",
            "condition",
            "dispatch",
            "start",
            "context-values",
            "context-files",
            "invoke",
            "complete",
        ]
        assert repository.completed is not None
        assert repository.completed[0] == {"value": "Ada"}
        assert repository.completed[1]["control"]["policy"]["allowed"] is True
        context = contexts[0]
        assert context.attempt_id == uuid5(TASK_RUN_ID, "attempt:1")
        assert context.workspace_scope_id == "workspace"
        assert context.workspace_quota_bytes == 100
        assert context.files == {
            "parent.txt": "parent://Ada",
            "child.txt": "child://Ada",
        }

    asyncio.run(scenario())


def test_attempt_cache_hit_completes_without_invoking_handler() -> None:
    async def scenario() -> None:
        events: list[str] = []
        task = TaskDefinition.model_validate(
            {
                "id": "work",
                "type": "test.task",
                "taskCache": {"enabled": True, "ttl": "PT1H"},
            }
        )
        repository = _Repository(_task_run(), events)
        cache = _HitCache(events)

        async def handler(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
            raise AssertionError("cache hit invoked task handler")

        outcome = await execute_task_attempt(
            _callbacks(
                repository,
                events,
                cast(TaskHandler, handler),
                task_cache=cast(TaskCacheRepository, cache),
            ),
            _flow(task),
            _execution({"name": "Ada"}),
            repository.task_run,
            task,
            {},
        )

        assert outcome.claimed is True and outcome.failure is None
        assert events == [
            "condition",
            "start",
            "context-values",
            "context-files",
            "cache-lookup",
            "complete",
        ]
        assert repository.completed is not None
        assert repository.completed[0] == {"cached": True}
        assert repository.completed[1]["cache"]["decision"] == "HIT"

    asyncio.run(scenario())


def test_attempt_failure_redacts_then_records_retry_condition_before_database_time() -> None:
    async def scenario() -> None:
        events: list[str] = []
        task = TaskDefinition.model_validate(
            {
                "id": "work",
                "type": "test.task",
                "contract": {"secretScopes": ["token"]},
                "retry": {
                    "maxAttempts": 2,
                    "delaySeconds": 3,
                    "condition": "retry-it",
                },
            }
        )
        repository = _Repository(_task_run(), events)

        async def handler(
            _task: TaskDefinition,
            _context: TaskExecutionContext,
        ) -> dict[str, Any]:
            events.append("invoke")
            raise OSError("network failed with top-secret")

        outcome = await execute_task_attempt(
            _callbacks(
                repository,
                events,
                handler,
                expressions=_RetryEngine(events),
            ),
            _flow(task),
            _execution({"name": "Ada"}),
            repository.task_run,
            task,
            {},
        )

        assert outcome.claimed is True and outcome.failure is None
        assert events == [
            "condition",
            "start",
            "context-values",
            "context-files",
            "invoke",
            "retry-condition:retry-it",
            "record-control",
            "database-time",
            "retry",
        ]
        assert repository.retried is not None
        assert repository.retried["reason"] == (
            "task 'work' failed [INFRASTRUCTURE]: network failed with [REDACTED]"
        )
        assert repository.retried["failure_category"] is FailureCategory.INFRASTRUCTURE
        assert repository.retried["retry_at"] == NOW.replace(second=3)

    asyncio.run(scenario())


def test_attempt_timeout_is_classified_and_finally_failed() -> None:
    async def scenario() -> None:
        events: list[str] = []
        task = TaskDefinition.model_validate(
            {
                "id": "work",
                "type": "test.task",
                "timeoutSeconds": 0.001,
            }
        )
        repository = _Repository(_task_run(), events)

        async def handler(
            _task: TaskDefinition,
            _context: TaskExecutionContext,
        ) -> dict[str, Any]:
            events.append("invoke")
            await asyncio.sleep(1)
            return {}

        outcome = await execute_task_attempt(
            _callbacks(repository, events, handler),
            _flow(task),
            _execution({"name": "Ada"}),
            repository.task_run,
            task,
            {},
        )

        assert outcome.claimed is True
        assert outcome.failure == "task 'work' failed [TIMED_OUT]: "
        assert events == [
            "condition",
            "start",
            "context-values",
            "context-files",
            "invoke",
            "fail",
        ]
        assert repository.failed is not None
        assert repository.failed["failure_category"] is FailureCategory.TIMED_OUT

    asyncio.run(scenario())
