from __future__ import annotations

from typing import Any

from amesh.domain import FailureCategory
from amesh.dsl.models import TaskDefinition
from amesh.ports import LogSourceStream, RunnerRequest, RunnerStatus, TaskRunner
from amesh.workflow.working_directory import WorkingDirectoryManager

from .contracts import TaskArtifactRecord, TaskCompletion, TaskLogRecord
from .service import TaskExecutionContext, TaskExecutionFailure, TaskHandler

_RUNNER_FAILURE_CATEGORIES = {
    RunnerStatus.FAILED: FailureCategory.RETRYABLE,
    RunnerStatus.CANCELLED: FailureCategory.CANCELLED,
    RunnerStatus.TIMED_OUT: FailureCategory.TIMED_OUT,
}


def local_process_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager | None = None,
) -> TaskHandler:
    workspaces = workspace_manager or WorkingDirectoryManager(None)

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        if task.command is None or not task.command:
            raise ValueError(f"task {task.id!r} requires a non-empty command")
        quota_bytes = context.workspace_quota_bytes or task.workspace_quota_bytes
        workspace = await workspaces.prepare(
            tenant_id=context.tenant_id,
            execution_id=str(context.execution_id),
            task_run_id=str(context.task_run_id),
            attempt_id=str(context.attempt_id),
            scope_id=context.workspace_scope_id,
            input_files=context.files,
            file_references=context.file_references,
            quota_bytes=quota_bytes,
        )
        try:
            result = await runner.run(
                RunnerRequest(
                    tenant_id=context.tenant_id,
                    execution_id=str(context.execution_id),
                    task_run_id=str(context.task_run_id),
                    attempt_id=str(context.attempt_id),
                    fencing_token=context.attempt,
                    command=task.command,
                    environment=task.environment,
                    input_files={
                        name: str(workspace.path.joinpath(*name.split("/")))
                        for name in context.files
                    },
                    working_directory=str(workspace.path),
                    timeout_seconds=task.timeout_seconds,
                )
            )
            if result.status is not RunnerStatus.SUCCESS:
                stderr = str(result.outputs.get("stderr", "")).strip()
                detail = f": {stderr}" if stderr else ""
                artifacts: tuple[TaskArtifactRecord, ...] = ()
                if task.retain_diagnostics_on_failure:
                    diagnostic = await workspaces.retain_failure_diagnostics(
                        workspace,
                        tenant_id=context.tenant_id,
                        execution_id=str(context.execution_id),
                        task_run_id=str(context.task_run_id),
                        attempt=context.attempt,
                        details={
                            "runnerStatus": result.status.value,
                            "exitCode": result.exit_code,
                            "stdout": str(result.outputs.get("stdout", "")),
                            "stderr": str(result.outputs.get("stderr", "")),
                        },
                        quota_bytes=quota_bytes,
                    )
                    artifacts = (diagnostic,)
                raise TaskExecutionFailure(
                    f"local process ended as {result.status.value}{detail}",
                    _RUNNER_FAILURE_CATEGORIES[result.status],
                    result={
                        "exitCode": result.exit_code,
                        **result.outputs,
                    },
                    evidence=_artifact_evidence(artifacts),
                )
            collected = await workspaces.collect(
                workspace,
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt=context.attempt,
                patterns=task.output_files,
                manifest_path=task.output_manifest,
                quota_bytes=quota_bytes,
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
                output={
                    "exitCode": result.exit_code,
                    **result.outputs,
                    "outputFiles": dict(collected.output_files),
                },
                logs=logs,
                artifacts=collected.artifacts,
            )
        finally:
            if not workspace.shared:
                workspaces.cleanup(workspace.path)

    return run


def kubernetes_job_handler(runner: TaskRunner) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        if task.command is None or not task.command:
            raise ValueError(f"task {task.id!r} requires a non-empty command")
        if task.image is None:
            raise ValueError(f"task {task.id!r} requires a container image")
        if task.input_files or task.output_files or task.output_manifest is not None:
            raise ValueError("Kubernetes workspace transfer is owned by the Kubernetes runner epic")
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


def _artifact_evidence(artifacts: tuple[TaskArtifactRecord, ...]) -> dict[str, object]:
    return {
        "artifacts": [
            artifact.model_dump(mode="json", by_alias=True, exclude_none=True)
            for artifact in artifacts
        ],
        "sizes": {"artifactBytes": sum(artifact.size_bytes for artifact in artifacts)},
    }
