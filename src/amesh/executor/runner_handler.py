from __future__ import annotations

from typing import Any

from amesh.domain import FailureCategory
from amesh.dsl.models import TaskDefinition
from amesh.ports import LogSourceStream, RunnerRequest, RunnerStatus, TaskRunner

from .contracts import TaskCompletion, TaskLogRecord
from .service import TaskExecutionContext, TaskExecutionFailure, TaskHandler

_RUNNER_FAILURE_CATEGORIES = {
    RunnerStatus.FAILED: FailureCategory.RETRYABLE,
    RunnerStatus.CANCELLED: FailureCategory.CANCELLED,
    RunnerStatus.TIMED_OUT: FailureCategory.TIMED_OUT,
}


def local_process_handler(runner: TaskRunner) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        if task.command is None or not task.command:
            raise ValueError(f"task {task.id!r} requires a non-empty command")
        result = await runner.run(
            RunnerRequest(
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt_id=str(context.attempt_id),
                fencing_token=context.attempt,
                command=task.command,
                environment=task.environment,
                timeout_seconds=task.timeout_seconds,
            )
        )
        if result.status is not RunnerStatus.SUCCESS:
            stderr = str(result.outputs.get("stderr", "")).strip()
            detail = f": {stderr}" if stderr else ""
            raise TaskExecutionFailure(
                f"local process ended as {result.status.value}{detail}",
                _RUNNER_FAILURE_CATEGORIES[result.status],
            )
        logs = tuple(
            TaskLogRecord(
                logger="amesh.task.core.shell",
                message=str(result.outputs[stream]),
                sourceStream=source,
            )
            for stream, source in (
                ("stdout", LogSourceStream.STDOUT),
                ("stderr", LogSourceStream.STDERR),
            )
            if result.outputs.get(stream)
        )
        return TaskCompletion(
            output={"exitCode": result.exit_code, **result.outputs},
            logs=logs,
        )

    return run


def kubernetes_job_handler(runner: TaskRunner) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        if task.command is None or not task.command:
            raise ValueError(f"task {task.id!r} requires a non-empty command")
        if task.image is None:
            raise ValueError(f"task {task.id!r} requires a container image")
        result = await runner.run(
            RunnerRequest(
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt_id=str(context.attempt_id),
                fencing_token=context.attempt,
                command=task.command,
                image=task.image,
                environment=task.environment,
                resource_limits=task.resources,
                timeout_seconds=task.timeout_seconds,
            )
        )
        if result.status is not RunnerStatus.SUCCESS:
            detail = str(result.diagnostics.get("message", "")).strip()
            suffix = f": {detail}" if detail else ""
            raise TaskExecutionFailure(
                f"Kubernetes Job ended as {result.status.value}{suffix}",
                _RUNNER_FAILURE_CATEGORIES[result.status],
            )
        return {
            "exitCode": result.exit_code,
            **result.outputs,
            "diagnostics": result.diagnostics,
        }

    return run
