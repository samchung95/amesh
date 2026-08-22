from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import ExecutionState, FailureCategory, TaskRunState
from amesh.dsl import FlowDefinition
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports import (
    ExecutionInterventionAction,
    ExecutionLaunchSource,
    ExecutionRepository,
    PersistedExecution,
    SubflowLaunchContext,
    SubflowMode,
    SubflowPropagation,
)
from amesh.workflow.data_contracts import output_contract, validate_flow_inputs

from .service import (
    ExecutionBlockedError,
    InProcessExecutor,
    TaskExecutionContext,
    TaskExecutionError,
    TaskExecutionFailure,
    TaskExecutionPaused,
    TaskHandler,
)

SubflowAuthorizer = Callable[[FlowDefinition], Awaitable[None]]
ExecutorFactory = Callable[[], InProcessExecutor]


class SubflowTaskSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    namespace: str | None = Field(default=None, min_length=1)
    flow_id: str = Field(alias="flowId", min_length=1)
    revision: int | None = Field(default=None, ge=1)
    mode: SubflowMode = SubflowMode.SYNC
    inputs: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    propagation: SubflowPropagation = Field(default_factory=SubflowPropagation)
    output_mapping: dict[str, str] = Field(default_factory=dict, alias="outputMapping")
    output_schema: dict[str, Any] = Field(default_factory=dict, alias="outputSchema")
    artifact_mapping: dict[str, str] = Field(default_factory=dict, alias="artifactMapping")
    artifact_schema: dict[str, Any] = Field(default_factory=dict, alias="artifactSchema")
    max_depth: int = Field(default=16, ge=1, le=100, alias="maxDepth")


def subflow_task_handler(
    repository: ExecutionRepository,
    executor_factory: ExecutorFactory,
    authorize: SubflowAuthorizer,
) -> TaskHandler:
    """Build the durable `core.subflow` task handler."""

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        spec = _task_spec(task)
        parent = await repository.get_execution(
            context.execution_id,
            tenant_id=context.tenant_id,
        )
        namespace = spec.namespace or parent.namespace
        child_flow = await repository.get_flow(
            namespace,
            spec.flow_id,
            tenant_id=context.tenant_id,
            revision=spec.revision,
        )
        if child_flow.disabled:
            raise ValueError(f"subflow {child_flow.namespace}.{child_flow.id} is disabled")
        await authorize(child_flow)

        depth, identities = await _lineage(repository, parent)
        child_identity = (child_flow.namespace, child_flow.id)
        if child_identity in identities:
            chain = " -> ".join(f"{namespace}.{flow_id}" for namespace, flow_id in identities)
            raise ValueError(f"recursive subflow invocation is not allowed: {chain}")
        child_depth = depth + 1
        if child_depth > spec.max_depth:
            raise ValueError(
                f"subflow depth {child_depth} exceeds configured maximum {spec.max_depth}"
            )

        child_inputs = _validate_inputs(child_flow, spec.inputs)
        invocation_key = f"subflow:{context.task_run_id}:{context.attempt}"
        propagation = (
            SubflowPropagation(
                success=False,
                failure=False,
                cancellation=False,
                pause=False,
                restart=False,
            )
            if spec.mode is SubflowMode.DETACHED
            else spec.propagation
        )
        if context.attempt > 1 and not propagation.restart:
            previous = next(
                (
                    relationship
                    for relationship in reversed(
                        await repository.list_subflows(
                            context.execution_id,
                            tenant_id=context.tenant_id,
                        )
                    )
                    if relationship.parent_task_run_id == context.task_run_id
                ),
                None,
            )
            if previous is not None:
                previous_child = await repository.get_execution(
                    previous.child_execution_id,
                    tenant_id=context.tenant_id,
                )
                previous_flow = await repository.get_flow(
                    previous.child_namespace,
                    previous.child_flow_id,
                    tenant_id=context.tenant_id,
                    revision=previous.target_revision,
                )
                return await _existing_child_result(
                    repository,
                    parent,
                    previous_child,
                    previous_flow,
                    spec,
                    propagation,
                )
        trigger = {
            "parentExecutionId": str(context.execution_id),
            "parentTaskRunId": str(context.task_run_id),
            "parentAttempt": context.attempt,
            "correlationId": context.trigger.get("correlationId", str(context.execution_id)),
            "traceContext": context.trigger.get("traceContext", {}),
            "detached": spec.mode is SubflowMode.DETACHED,
        }
        child = await repository.create_execution(
            child_flow,
            tenant_id=context.tenant_id,
            inputs=child_inputs,
            trigger=trigger,
            launch_source=ExecutionLaunchSource.SUBFLOW,
            idempotency_key=invocation_key,
            actor_id=parent.created_by,
            labels={**context.labels, **spec.labels},
            subflow=SubflowLaunchContext(
                parent_execution_id=context.execution_id,
                parent_task_run_id=context.task_run_id,
                parent_attempt=context.attempt,
                invocation_key=invocation_key,
                mode=spec.mode,
                depth=child_depth,
                target_revision=child_flow.revision,
                propagation=propagation,
                output_mapping=spec.output_mapping,
            ),
        )
        if spec.mode is not SubflowMode.SYNC:
            return _child_reference(child, spec.mode)

        try:
            progress = await executor_factory().run_to_completion(
                child_flow,
                child.execution_id,
                tenant_id=context.tenant_id,
            )
        except (ExecutionBlockedError, TaskExecutionError) as exc:
            persisted = await repository.get_execution(
                child.execution_id,
                tenant_id=context.tenant_id,
            )
            return await _propagate_child_state(
                repository,
                parent,
                persisted,
                propagation,
                error=exc,
            )

        outputs = {
            task_run.task_id: task_run.result or {}
            for task_run in progress.task_runs
            if task_run.state is TaskRunState.SUCCESS
        }
        if not propagation.success:
            return {
                **_child_reference(child, spec.mode),
                "outputs": {},
                "artifacts": {},
                "propagated": False,
            }
        mapped = _map_child_values(
            child_flow,
            progress.state,
            outputs,
            spec.output_mapping,
            spec.output_schema,
            default_to_flow_outputs=True,
        )
        artifacts = _map_child_values(
            child_flow,
            progress.state,
            outputs,
            spec.artifact_mapping,
            spec.artifact_schema,
            default_to_flow_outputs=False,
        )
        return {
            **_child_reference(child, spec.mode),
            "childState": progress.state.value,
            "outputs": mapped,
            "artifacts": artifacts,
        }

    return run


class SubflowCoordinator:
    """Resume durable asynchronous children independently of their parent request."""

    def __init__(
        self,
        repository: ExecutionRepository,
        executor_factory: ExecutorFactory,
    ) -> None:
        self._repository = repository
        self._executor_factory = executor_factory

    async def run_pending(
        self,
        parent_execution_id: UUID,
        *,
        tenant_id: str,
    ) -> list[PersistedExecution]:
        completed: list[PersistedExecution] = []
        for relationship in await self._repository.list_subflows(
            parent_execution_id,
            tenant_id=tenant_id,
        ):
            child = await self._repository.get_execution(
                relationship.child_execution_id,
                tenant_id=tenant_id,
            )
            if child.state is not ExecutionState.RUNNING:
                completed.append(child)
                completed.extend(
                    await self.run_pending(
                        child.execution_id,
                        tenant_id=tenant_id,
                    )
                )
                continue
            flow = await self._repository.get_flow(
                child.namespace,
                child.flow_id,
                tenant_id=tenant_id,
                revision=relationship.target_revision,
            )
            with suppress(ExecutionBlockedError, TaskExecutionError):
                await self._executor_factory().run_to_completion(
                    flow,
                    child.execution_id,
                    tenant_id=tenant_id,
                )
            persisted_child = await self._repository.get_execution(
                child.execution_id,
                tenant_id=tenant_id,
            )
            completed.append(persisted_child)
            completed.extend(
                await self.run_pending(
                    child.execution_id,
                    tenant_id=tenant_id,
                )
            )
        return completed


def _task_spec(task: TaskDefinition) -> SubflowTaskSpec:
    extra = task.model_extra or {}
    return SubflowTaskSpec.model_validate(
        {
            key: value
            for key, value in extra.items()
            if key
            in {
                "namespace",
                "flowId",
                "revision",
                "mode",
                "inputs",
                "labels",
                "propagation",
                "outputMapping",
                "outputSchema",
                "artifactMapping",
                "artifactSchema",
                "maxDepth",
            }
        }
    )


async def _lineage(
    repository: ExecutionRepository,
    execution: PersistedExecution,
) -> tuple[int, tuple[tuple[str, str], ...]]:
    identities: list[tuple[str, str]] = [(execution.namespace, execution.flow_id)]
    current_id = execution.execution_id
    depth = 0
    while (
        parent := await repository.get_parent_subflow(
            current_id,
            tenant_id=execution.tenant_id,
        )
    ) is not None:
        depth = max(depth, parent.depth)
        identity = (parent.parent_namespace, parent.parent_flow_id)
        if identity in identities:
            raise ValueError("persisted subflow lineage contains a cycle")
        identities.append(identity)
        current_id = parent.parent_execution_id
        if len(identities) > 100:
            raise ValueError("persisted subflow lineage exceeds the supported depth")
    return depth, tuple(identities)


def _validate_inputs(flow: FlowDefinition, supplied: Mapping[str, Any]) -> dict[str, Any]:
    return validate_flow_inputs(flow, supplied)


async def _propagate_child_state(
    repository: ExecutionRepository,
    parent: PersistedExecution,
    child: PersistedExecution,
    propagation: SubflowPropagation,
    *,
    error: Exception,
) -> dict[str, Any]:
    if child.state is ExecutionState.PAUSED and propagation.pause:
        await repository.apply_execution_intervention(
            parent.execution_id,
            ExecutionInterventionAction.PAUSE,
            tenant_id=parent.tenant_id,
            expected_version=parent.version,
            expected_epoch=parent.epoch,
            actor_id="system:subflow",
            reason=f"synchronous child {child.execution_id} paused",
        )
        raise TaskExecutionPaused(f"synchronous child {child.execution_id} paused")
    if child.state is ExecutionState.CANCELLED and propagation.cancellation:
        raise TaskExecutionFailure(
            f"synchronous child {child.execution_id} was cancelled",
            FailureCategory.CANCELLED,
        )
    if child.state in {ExecutionState.FAILED, ExecutionState.WARNING} and propagation.failure:
        raise TaskExecutionFailure(
            f"synchronous child {child.execution_id} ended as {child.state.value}: {error}",
            FailureCategory.NON_RETRYABLE,
        )
    return {
        **_child_reference(child, SubflowMode.SYNC),
        "childState": child.state.value,
        "outputs": {},
        "propagated": False,
    }


def _map_child_values(
    flow: FlowDefinition,
    state: ExecutionState,
    outputs: Mapping[str, dict[str, Any]],
    mapping: Mapping[str, str],
    schema: Mapping[str, Any],
    *,
    default_to_flow_outputs: bool,
) -> dict[str, Any]:
    selected: Mapping[str, Any] = mapping
    if default_to_flow_outputs:
        selected = mapping or {
            output_id: output_contract(value).value
            for output_id, value in flow.outputs.items()
        } or outputs
    rendered = NativeExpressionEngine().render_value(
        dict(selected),
        ExpressionContext(
            flow={"id": flow.id, "namespace": flow.namespace, "revision": flow.revision},
            execution={"state": state.value},
            outputs=outputs,
        ),
    )
    if not isinstance(rendered, dict):
        raise TypeError("subflow mapping must render to an object")
    json.dumps(rendered)
    if schema:
        try:
            Draft202012Validator.check_schema(dict(schema))
            Draft202012Validator(dict(schema)).validate(rendered)
        except SchemaError as exc:
            raise ValueError(f"invalid subflow result schema: {exc.message}") from exc
        except ValidationError as exc:
            path = ".".join(str(part) for part in exc.absolute_path) or "$"
            raise ValueError(
                f"subflow result at {path} does not match schema: {exc.message}"
            ) from exc
    return rendered


def _child_reference(child: PersistedExecution, mode: SubflowMode) -> dict[str, Any]:
    return {
        "childExecutionId": str(child.execution_id),
        "childNamespace": child.namespace,
        "childFlowId": child.flow_id,
        "childRevision": child.flow_revision,
        "childState": child.state.value,
        "mode": mode.value,
    }


async def _existing_child_result(
    repository: ExecutionRepository,
    parent: PersistedExecution,
    child: PersistedExecution,
    flow: FlowDefinition,
    spec: SubflowTaskSpec,
    propagation: SubflowPropagation,
) -> dict[str, Any]:
    if spec.mode is not SubflowMode.SYNC:
        return _child_reference(child, spec.mode)
    if child.state is not ExecutionState.SUCCESS:
        return await _propagate_child_state(
            repository,
            parent,
            child,
            propagation,
            error=RuntimeError("child restart propagation is disabled"),
        )
    if not propagation.success:
        return {
            **_child_reference(child, spec.mode),
            "outputs": {},
            "artifacts": {},
            "propagated": False,
            "reused": True,
        }
    task_runs = await repository.list_task_runs(
        child.execution_id,
        tenant_id=child.tenant_id,
    )
    outputs = {
        task_run.task_id: task_run.result or {}
        for task_run in task_runs
        if task_run.state is TaskRunState.SUCCESS
    }
    return {
        **_child_reference(child, spec.mode),
        "outputs": _map_child_values(
            flow,
            child.state,
            outputs,
            spec.output_mapping,
            spec.output_schema,
            default_to_flow_outputs=True,
        ),
        "artifacts": _map_child_values(
            flow,
            child.state,
            outputs,
            spec.artifact_mapping,
            spec.artifact_schema,
            default_to_flow_outputs=False,
        ),
        "reused": True,
    }
