from __future__ import annotations

import ast
import asyncio
import hashlib
import inspect
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import amesh.executor as executor_api
import amesh.executor.contracts as executor_contracts
import amesh.executor.control as executor_control
import amesh.executor.runner_handler as executor_runner_handler
import amesh.executor.service as executor_service
import amesh.executor.subflows as executor_subflows
from amesh.domain import ExecutionState, TaskRunState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.dsl.models import RetryPolicy
from amesh.executor import InProcessExecutor, TaskCompletion, TaskExecutionContext
from amesh.ports import ExecutionRepository, PersistedExecution, PersistedTaskRun

ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_ROOT = ROOT / "src" / "amesh" / "executor"

EXPECTED_EXECUTOR_EXPORTS = (
    "ExecutionBlockedError",
    "ExecutionProgress",
    "InProcessExecutor",
    "OrchestrationDecision",
    "SubflowCoordinator",
    "SubflowTaskSpec",
    "TaskArtifactRecord",
    "TaskAssetRecord",
    "TaskCancellationChannel",
    "TaskCompletion",
    "TaskConfigurationError",
    "TaskContextProvider",
    "TaskContextRequest",
    "TaskContextResources",
    "TaskDeferral",
    "TaskExecutionContext",
    "TaskExecutionError",
    "TaskExecutionFailure",
    "TaskExecutionPaused",
    "TaskExitMetadata",
    "TaskFileReference",
    "TaskHandler",
    "TaskLogRecord",
    "TaskMetricRecord",
    "TaskPlatformError",
    "TaskResourceLimitError",
    "TaskUserCodeError",
    "docker_container_handler",
    "execution_lifecycle_pending",
    "kubernetes_job_handler",
    "local_process_handler",
    "normalize_task_completion",
    "preview_execution_intervention",
    "reduce_orchestration",
    "required_runner_ids",
    "selecting_runner_handler",
    "subflow_task_handler",
)

EXPECTED_SIGNATURES = {
    "InProcessExecutor": (
        "(repository: 'ExecutionRepository', handlers: 'Mapping[str, TaskHandler] | None' = None, "
        "expressions: 'ExpressionEngine | None' = None, recover_running_types: "
        "'frozenset[str] | None' = None, context_provider: 'TaskContextProvider | None' = None, "
        "resource_registry: 'ResourceSchemaRegistry | None' = None, object_store: "
        "'ObjectStore | None' = None, task_cache: 'TaskCacheRepository | None' = None, "
        "workspace_manager: 'WorkingDirectoryManager | None' = None, dispatch_policy_enforcer: "
        "'DispatchPolicyEnforcer | None' = None, admission_poll_initial_seconds: 'float' = 0.05, "
        "admission_poll_max_seconds: 'float' = 1.0) -> 'None'"
    ),
    "InProcessExecutor.create_execution": (
        "(self, flow: 'FlowDefinition', *, tenant_id: 'str', inputs: 'dict[str, Any] | None' = "
        "None, launch_source: 'ExecutionLaunchSource' = <ExecutionLaunchSource.MANUAL: "
        "'manual'>) -> 'UUID'"
    ),
    "InProcessExecutor.run_ready": (
        "(self, flow: 'FlowDefinition', execution_id: 'UUID', *, tenant_id: 'str', "
        "max_tasks: 'int | None' = None) -> 'ExecutionProgress'"
    ),
    "InProcessExecutor.run_to_completion": (
        "(self, flow: 'FlowDefinition', execution_id: 'UUID', *, tenant_id: 'str') -> "
        "'ExecutionProgress'"
    ),
    "reduce_orchestration": (
        "(flow: 'FlowDefinition', task_runs: 'list[PersistedTaskRun]', *, now: 'datetime') -> "
        "'OrchestrationDecision'"
    ),
    "normalize_task_completion": (
        "(result: 'dict[str, Any] | TaskCompletion', limits: 'TaskResourceLimits', *, "
        "secret_values: 'Iterable[str]' = ()) -> 'tuple[dict[str, Any], dict[str, Any]]'"
    ),
}

EXPECTED_SCHEMA_HASHES = {
    "execution-command.schema.json": (
        "2765bf046d1d66d16e85937520b78137a5f6299b128f2ba265a774ca030f5b9c"
    ),
    "execution-event.schema.json": (
        "11acb3b8ce4497f965a0386df6a8e4d8ecdc00d7a8544e3ce00caffd1ee16cb8"
    ),
    "execution-snapshot.schema.json": (
        "fa1091858c8819310ccccecf7f15b23a626a900be6f2c49dfe87281639bd3346"
    ),
    "execution-transition.schema.json": (
        "fde2453402ffb9ac30fad2c352876db78fd2d4d64a2a7f9b1c5ed5085593b5db"
    ),
    "task-run-command.schema.json": (
        "a939e95d5938dba4d433eb2aa2e5ced69ef59c63b8453d5087f0dbd6875f20d0"
    ),
    "task-run-event.schema.json": (
        "4fa8cc53e4c88c35550acc663a1e1a37ae2308a40ed6ccfc80863a94c520d19d"
    ),
    "task-run-snapshot.schema.json": (
        "2c78da059cc623a471dbc1816b9eaeb03f40fffe6865a94e81bd5a0fc834c8f5"
    ),
    "task-run-transition.schema.json": (
        "0f6d73e0c1e7b4de7522be227a50400d341c78c79d15e46e484fb87cb73901dd"
    ),
}

EXECUTION_ID = UUID("018f47f4-a289-7c7e-9f0b-61dcf6e7d900")
TASK_RUN_ID = UUID("018f47f4-a289-7c7e-9f0b-61dcf6e7d901")


def _fixed_execution() -> PersistedExecution:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    return PersistedExecution(
        execution_id=EXECUTION_ID,
        tenant_id="default",
        state=ExecutionState.RUNNING,
        epoch=1,
        version=1,
        namespace="tests.cache",
        flow_id="cached",
        flow_revision=1,
        inputs={"value": "alpha"},
        labels={},
        trigger={},
        created_at=timestamp,
        updated_at=timestamp,
    )


def _cached_flow() -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "cached",
            "namespace": "tests.cache",
            "revision": 1,
            "inputs": [{"id": "value", "type": "STRING", "default": "default"}],
            "tasks": [
                {
                    "id": "result",
                    "type": "test.cached",
                    "value": "{{ inputs.value }}",
                    "taskCache": {
                        "enabled": True,
                        "ttl": "PT1H",
                        "namespace": "acceptance",
                        "scope": "TASK",
                        "invalidationPolicy": "TTL_AND_REVISION",
                        "keyContext": ["inputs", "variables"],
                        "codeVersion": "plugin:1",
                    },
                }
            ],
        }
    )


def test_public_executor_surface_signatures_and_reexports_are_compatible() -> None:
    assert tuple(executor_api.__all__) == EXPECTED_EXECUTOR_EXPORTS
    assert len(executor_api.__all__) == 37

    assert executor_api.InProcessExecutor is executor_service.InProcessExecutor
    assert executor_api.TaskExecutionContext is executor_service.TaskExecutionContext
    assert executor_api.reduce_orchestration is executor_service.reduce_orchestration
    assert executor_api.TaskCompletion is executor_contracts.TaskCompletion
    assert (
        executor_api.preview_execution_intervention
        is executor_control.preview_execution_intervention
    )
    assert executor_api.local_process_handler is executor_runner_handler.local_process_handler
    assert executor_api.subflow_task_handler is executor_subflows.subflow_task_handler

    actual_signatures = {
        "InProcessExecutor": str(inspect.signature(executor_api.InProcessExecutor)),
        "InProcessExecutor.create_execution": str(
            inspect.signature(executor_api.InProcessExecutor.create_execution)
        ),
        "InProcessExecutor.run_ready": str(
            inspect.signature(executor_api.InProcessExecutor.run_ready)
        ),
        "InProcessExecutor.run_to_completion": str(
            inspect.signature(executor_api.InProcessExecutor.run_to_completion)
        ),
        "reduce_orchestration": str(inspect.signature(executor_api.reduce_orchestration)),
        "normalize_task_completion": str(inspect.signature(executor_api.normalize_task_completion)),
    }
    assert actual_signatures == EXPECTED_SIGNATURES


def test_executor_constructs_the_stable_attempt_identity() -> None:
    execution = _fixed_execution().model_copy(
        update={"namespace": "tests.executor", "flow_id": "attempt_identity"}
    )
    task_run = PersistedTaskRun(
        task_run_id=TASK_RUN_ID,
        execution_id=EXECUTION_ID,
        task_id="capture",
        state=TaskRunState.WAITING,
        current_attempt=0,
        version=1,
    )
    captured_contexts: list[TaskExecutionContext] = []

    class Repository:
        def __init__(self) -> None:
            self.execution = execution
            self.task_run = task_run

        async def get_execution(self, *_: object, **__: object) -> PersistedExecution:
            return self.execution

        async def list_task_runs(self, *_: object, **__: object) -> list[PersistedTaskRun]:
            return [self.task_run]

        async def database_time(self) -> datetime:
            return datetime(2026, 1, 1, tzinfo=UTC)

        async def start_task(self, *_: object, **__: object) -> PersistedTaskRun:
            self.task_run = self.task_run.model_copy(
                update={"state": TaskRunState.RUNNING, "current_attempt": 1}
            )
            return self.task_run

        async def complete_task(
            self,
            _task_run_id: UUID,
            _attempt: int,
            result: dict[str, Any],
            **__: object,
        ) -> PersistedTaskRun:
            self.task_run = self.task_run.model_copy(
                update={"state": TaskRunState.SUCCESS, "result": result}
            )
            return self.task_run

        async def complete_execution(self, *_: object, **__: object) -> PersistedExecution:
            self.execution = self.execution.model_copy(update={"state": ExecutionState.SUCCESS})
            return self.execution

    async def capture_handler(
        _task: TaskDefinition,
        context: TaskExecutionContext,
    ) -> TaskCompletion:
        captured_contexts.append(context)
        return TaskCompletion(output={"captured": True})

    flow = FlowDefinition(
        id="attempt_identity",
        namespace="tests.executor",
        tasks=[TaskDefinition(id="capture", type="test.capture")],
    )
    repository = Repository()
    result = asyncio.run(
        InProcessExecutor(
            cast(ExecutionRepository, repository),
            handlers={"test.capture": capture_handler},
        ).run_ready(flow, EXECUTION_ID, tenant_id="default")
    )

    assert result.state is ExecutionState.SUCCESS
    assert len(captured_contexts) == 1
    assert captured_contexts[0].attempt == 1
    assert captured_contexts[0].attempt_id == UUID("903e9150-01f8-5685-bbd9-ed3a3caf74d3")


def test_retry_and_cache_derivations_are_byte_stable() -> None:
    retry_policy = RetryPolicy(
        maxAttempts=3,
        delaySeconds=2,
        backoffMultiplier=2,
        maxIntervalSeconds=10,
        jitterRatio=0.25,
    )
    assert [
        executor_service.retry_delay_seconds(retry_policy, TASK_RUN_ID, attempt)
        for attempt in (1, 2, 3)
    ] == [2.3513580734891932, 3.093337642636499, 7.6527220534308675]

    execution = _fixed_execution()
    context = TaskExecutionContext(
        tenant_id="default",
        execution_id=EXECUTION_ID,
        task_run_id=TASK_RUN_ID,
        attempt=1,
        attempt_id=UUID("903e9150-01f8-5685-bbd9-ed3a3caf74d3"),
        inputs=execution.inputs,
        outputs={},
        variables={},
        secret_scopes=("service",),
        secrets={"service": "secret-a"},
    )
    flow = _cached_flow()
    cache_key = executor_service.derive_task_cache_key(
        flow,
        execution,
        flow.tasks[0],
        context,
    )

    assert cache_key.model_dump(mode="json") == {
        "key_hash": "dd2ca34a32b309c616ca46162d6e9c04f7b6211d8addf833e154a5b46614c610",
        "key_prefix": "acceptance/tests.cache/cached/result",
        "cache_namespace": "acceptance",
        "scope": "TASK",
        "namespace": "tests.cache",
        "flow_id": "cached",
        "flow_revision": 1,
        "task_id": "result",
        "task_type": "test.cached",
        "security_context_hash": (
            "f7668fac719dc515907c922690216f200357fad8e1b983950d5b34907f7d1591"
        ),
        "invalidation_policy": "TTL_AND_REVISION",
        "ttl": "PT1H",
        "population_lease": "PT1H",
    }


def test_persisted_execution_and_task_schema_bytes_are_stable() -> None:
    actual = {
        name: hashlib.sha256((ROOT / "schemas" / name).read_bytes()).hexdigest()
        for name in EXPECTED_SCHEMA_HASHES
    }
    assert actual == EXPECTED_SCHEMA_HASHES


def test_every_executor_implementation_file_is_at_most_900_lines() -> None:
    oversized = {
        path.relative_to(ROOT).as_posix(): len(path.read_text(encoding="utf-8").splitlines())
        for path in sorted(EXECUTOR_ROOT.rglob("*.py"))
        if len(path.read_text(encoding="utf-8").splitlines()) > 900
    }
    assert oversized == {}, f"executor implementation files exceed 900 lines: {oversized}"


def test_every_executor_callable_is_at_most_120_lines() -> None:
    oversized: list[str] = []
    for path in sorted(EXECUTOR_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            assert node.end_lineno is not None
            line_count = node.end_lineno - node.lineno + 1
            if line_count > 120:
                location = path.relative_to(ROOT).as_posix()
                oversized.append(f"{location}:{node.lineno} {node.name} ({line_count} lines)")
    assert oversized == [], "executor callables exceed 120 lines:\n" + "\n".join(oversized)
