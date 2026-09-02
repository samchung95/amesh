from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from pydantic import SecretStr

from amesh.domain import FailureCategory
from amesh.dsl.models import TaskDefinition
from amesh.observability import instrument_async_operation
from amesh.ports import (
    LogLevel,
    LogSourceStream,
    RunnerDiagnostics,
    RunnerId,
    RunnerPolicySet,
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    ScopedRunnerCredential,
    TaskRunner,
    redact_runner_payload,
)

if TYPE_CHECKING:
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
    *,
    namespace: str = "default",
    requires_image: bool = False,
    runner_label: str = "local process",
) -> TaskHandler:
    from amesh.workflow.working_directory import WorkingDirectoryManager

    workspaces = workspace_manager or WorkingDirectoryManager(None)

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        if task.command is None or not task.command:
            raise ValueError(f"task {task.id!r} requires a non-empty command")
        if requires_image and task.image is None:
            raise ValueError(f"task {task.id!r} requires a container image")
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
            result = await _dispatch_runner(
                runner,
                RunnerRequest(
                    tenant_id=context.tenant_id,
                    namespace=namespace,
                    worker_group=task.worker_group,
                    execution_id=str(context.execution_id),
                    task_run_id=str(context.task_run_id),
                    attempt_id=str(context.attempt_id),
                    fencing_token=context.attempt,
                    command=task.command,
                    image=task.image if requires_image else None,
                    environment=task.environment,
                    credentials=_runner_credentials(task, context),
                    input_files={
                        name: str(workspace.path.joinpath(*name.split("/")))
                        for name in context.files
                    },
                    working_directory=str(workspace.path),
                    standardInput=task.standard_input,
                    resource_limits=task.resources,
                    network_policy=task.network_policy,
                    security_policy=task.security_policy,
                    extension=task.task_runner,
                    timeout_seconds=task.timeout_seconds,
                    outputLimitBytes=task.contract.resource_limits.max_output_bytes,
                ),
                context,
            )
            secret_values = tuple(context.secrets.values())
            safe_outputs = redact_runner_payload(result.outputs, secret_values)
            if not isinstance(safe_outputs, dict):
                raise TypeError("runner outputs must be a mapping")
            if result.status is not RunnerStatus.SUCCESS:
                stderr = str(safe_outputs.get("stderr", "")).strip()
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
                            "signal": result.signal,
                            "stdout": str(safe_outputs.get("stdout", "")),
                            "stderr": str(safe_outputs.get("stderr", "")),
                        },
                        quota_bytes=quota_bytes,
                    )
                    artifacts = (diagnostic,)
                raise TaskExecutionFailure(
                    f"{runner_label} ended as {result.status.value}{detail}",
                    _RUNNER_FAILURE_CATEGORIES[result.status],
                    result={
                        "exitCode": result.exit_code,
                        "signal": result.signal,
                        "metrics": result.metrics.model_dump(
                            mode="json", by_alias=True, exclude_none=True
                        ),
                        **(
                            {"diagnostics": _public_runner_diagnostics(result.diagnostics)}
                            if requires_image
                            else {}
                        ),
                        **safe_outputs,
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
                    level=LogLevel(entry.level),
                    logger="amesh.task.core.shell",
                    message=entry.message,
                    fields={"sequence": entry.sequence},
                    sourceStream=source,
                    occurredAt=entry.occurred_at,
                )
                for entry in result.logs
                if (
                    source := {
                        "STDOUT": LogSourceStream.STDOUT,
                        "STDERR": LogSourceStream.STDERR,
                    }.get(entry.stream.value)
                )
            )
            return TaskCompletion(
                output={
                    "exitCode": result.exit_code,
                    "signal": result.signal,
                    "metrics": result.metrics.model_dump(
                        mode="json", by_alias=True, exclude_none=True
                    ),
                    **safe_outputs,
                    **(
                        {"diagnostics": _public_runner_diagnostics(result.diagnostics)}
                        if requires_image
                        else {}
                    ),
                    "outputFiles": dict(collected.output_files),
                },
                logs=logs,
                artifacts=collected.artifacts,
            )
        finally:
            if not workspace.shared:
                workspaces.cleanup(workspace.path)

    return run


def docker_container_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager | None = None,
    *,
    namespace: str = "default",
) -> TaskHandler:
    return local_process_handler(
        runner,
        workspace_manager,
        namespace=namespace,
        requires_image=True,
        runner_label="Docker container",
    )


def kubernetes_job_handler(
    runner: TaskRunner,
    workspace_manager: WorkingDirectoryManager | None = None,
    *,
    namespace: str = "default",
) -> TaskHandler:
    return local_process_handler(
        runner,
        workspace_manager,
        namespace=namespace,
        requires_image=True,
        runner_label="Kubernetes Job",
    )


def selecting_runner_handler(
    handlers: Mapping[RunnerId, TaskHandler],
    policy: RunnerPolicySet,
    *,
    namespace: str,
    fallback: RunnerId,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> Any:
        selected = policy.select(
            namespace=namespace,
            worker_group=task.worker_group,
            requested=task.task_runner.type if task.task_runner is not None else None,
            fallback=fallback,
            available=frozenset(handlers),
        )
        return await handlers[selected](task, context)

    return run


def required_runner_ids(
    tasks: Iterable[TaskDefinition],
    policy: RunnerPolicySet,
    *,
    namespace: str,
    fallback: RunnerId,
    available: frozenset[RunnerId] = frozenset(RunnerId),
) -> frozenset[RunnerId]:
    return frozenset(
        policy.select(
            namespace=namespace,
            worker_group=task.worker_group,
            requested=task.task_runner.type if task.task_runner is not None else None,
            fallback=fallback,
            available=available,
        )
        for task in tasks
        if task.type == "core.shell" or task.type.startswith("script.")
    )


def _runner_credentials(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> tuple[ScopedRunnerCredential, ...]:
    missing = set(task.runner_credentials.values()).difference(context.secrets)
    if missing:
        raise ValueError(f"runner credential scopes are unavailable: {', '.join(sorted(missing))}")
    return tuple(
        ScopedRunnerCredential(
            scope=scope,
            environmentVariable=environment_variable,
            value=SecretStr(context.secrets[scope]),
        )
        for environment_variable, scope in sorted(task.runner_credentials.items())
    )


@instrument_async_operation("runner", "dispatch")
async def _dispatch_runner(
    runner: TaskRunner,
    request: RunnerRequest,
    context: TaskExecutionContext,
) -> RunnerResult:
    running = asyncio.create_task(runner.run(request))
    cancellation = asyncio.create_task(context.cancellation.wait())
    try:
        done, _ = await asyncio.wait(
            {running, cancellation},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if running in done:
            return await running
        await runner.cancel(request.attempt_id, request.fencing_token)
        return await running
    finally:
        cancellation.cancel()
        with suppress(asyncio.CancelledError):
            await cancellation
        if not running.done():
            running.cancel()
            with suppress(asyncio.CancelledError):
                await running


def _artifact_evidence(artifacts: tuple[TaskArtifactRecord, ...]) -> dict[str, object]:
    return {
        "artifacts": [
            artifact.model_dump(mode="json", by_alias=True, exclude_none=True)
            for artifact in artifacts
        ],
        "sizes": {"artifactBytes": sum(artifact.size_bytes for artifact in artifacts)},
    }


def _public_runner_diagnostics(diagnostics: RunnerDiagnostics) -> dict[str, Any]:
    value = diagnostics.model_dump(mode="json", by_alias=True, exclude_none=True)
    details = value.pop("details", {})
    if isinstance(details, dict):
        value.update(details)
    if diagnostics.runner is RunnerId.KUBERNETES and diagnostics.external_id is not None:
        value.setdefault("jobName", diagnostics.external_id)
    return value
