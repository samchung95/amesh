from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, LifecyclePhase, PlannedTask
from amesh.ports import PersistedExecution, PersistedTaskRun

from .contracts import (
    ExecutionBlockedError,
    ExecutionProgress,
    OrchestrationDecision,
    TaskExecutionError,
)
from .orchestration_core import (
    _completed_phase_evidence,
    _error_handler_is_applicable,
    _handler_error_contexts,
    _lifecycle_plan,
    _main_error_items,
    _phase_is_complete,
    _phase_plan,
    _phase_was_completed,
    _primary_error_message,
)


class LifecycleExecutionRepository(Protocol):
    async def record_execution_lifecycle(
        self,
        execution_id: UUID,
        evidence: dict[str, object],
        *,
        tenant_id: str,
        expected_epoch: int,
    ) -> PersistedExecution: ...


class FinishExecution(Protocol):
    async def __call__(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        decision: OrchestrationDecision,
        task_runs: list[PersistedTaskRun],
    ) -> PersistedExecution: ...


class RunLifecyclePhase(Protocol):
    async def __call__(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        plan: tuple[PlannedTask, ...],
        task_runs: list[PersistedTaskRun],
        *,
        handler_errors: Mapping[str, Mapping[str, Any]],
        max_tasks: int | None,
    ) -> ExecutionProgress: ...


class SkipLifecycleTasks(Protocol):
    async def __call__(
        self,
        task_runs: list[PersistedTaskRun],
        task_ids: set[str],
        phase: LifecyclePhase,
        *,
        tenant_id: str,
        reason: str,
    ) -> list[PersistedTaskRun]: ...


@dataclass
class _LifecycleCursor:
    execution: PersistedExecution
    task_runs: list[PersistedTaskRun]
    claimed_tasks: int


def _progress(cursor: _LifecycleCursor) -> ExecutionProgress:
    return ExecutionProgress(
        execution_id=cursor.execution.execution_id,
        state=cursor.execution.state,
        tasks_run=cursor.claimed_tasks,
        task_runs=tuple(cursor.task_runs),
    )


async def _without_lifecycle(
    flow: FlowDefinition,
    cursor: _LifecycleCursor,
    primary_decision: OrchestrationDecision | None,
    primary_failure: str | None,
    finish_execution: FinishExecution,
) -> ExecutionProgress:
    if primary_decision is None:
        return _progress(cursor)
    cursor.execution = await finish_execution(
        flow,
        cursor.execution,
        primary_decision,
        cursor.task_runs,
    )
    if primary_failure is not None:
        raise TaskExecutionError(primary_decision.diagnostic or primary_failure)
    return _progress(cursor)


async def _initialize_primary_evidence(
    cursor: _LifecycleCursor,
    execution_plan: tuple[PlannedTask, ...],
    primary_decision: OrchestrationDecision | None,
    primary_failure: str | None,
    repository: LifecycleExecutionRepository,
) -> tuple[dict[str, object], ExecutionState, dict[str, object]]:
    evidence = deepcopy(cursor.execution.lifecycle_evidence)
    primary = evidence.get("primary")
    if not isinstance(primary, Mapping):
        primary_state = (
            primary_decision.terminal_state
            if primary_decision is not None
            else cursor.execution.state
        )
        if primary_state not in {
            ExecutionState.SUCCESS,
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
            ExecutionState.WARNING,
        }:
            raise ExecutionBlockedError(
                f"execution {cursor.execution.execution_id} has no terminal primary outcome"
            )
        errors = _main_error_items(execution_plan, cursor.task_runs)
        diagnostic = (
            primary_decision.diagnostic
            if primary_decision is not None
            else primary_failure or _primary_error_message(errors)
        )
        primary = {
            "state": primary_state.value,
            "diagnostic": diagnostic,
            "errors": errors,
        }
        evidence = {
            "schemaVersion": 1,
            "status": LifecyclePhase.ERROR.value,
            "primary": primary,
            "phases": {},
        }
        cursor.execution = await repository.record_execution_lifecycle(
            cursor.execution.execution_id,
            evidence,
            tenant_id=cursor.execution.tenant_id,
            expected_epoch=cursor.execution.epoch,
        )

    primary_state = ExecutionState(str(primary["state"]))
    phases = evidence.get("phases")
    phase_evidence = dict(phases) if isinstance(phases, Mapping) else {}
    return evidence, primary_state, phase_evidence


async def _run_phase(
    flow: FlowDefinition,
    cursor: _LifecycleCursor,
    plan: tuple[PlannedTask, ...],
    *,
    phase: LifecyclePhase,
    next_status: str,
    evidence: dict[str, object],
    phase_evidence: dict[str, object],
    handler_errors: Mapping[str, Mapping[str, Any]],
    max_tasks: int | None,
    repository: LifecycleExecutionRepository,
    run_lifecycle_phase: RunLifecyclePhase,
) -> ExecutionProgress:
    phase_progress = await run_lifecycle_phase(
        flow,
        cursor.execution,
        plan,
        cursor.task_runs,
        handler_errors=handler_errors,
        max_tasks=max_tasks,
    )
    cursor.task_runs = list(phase_progress.task_runs)
    cursor.claimed_tasks += phase_progress.tasks_run
    if not _phase_is_complete(plan, cursor.task_runs):
        return phase_progress.model_copy(update={"tasks_run": cursor.claimed_tasks})

    phase_evidence[phase.value] = _completed_phase_evidence(plan, cursor.task_runs)
    evidence.update({"status": next_status, "phases": phase_evidence})
    cursor.execution = await repository.record_execution_lifecycle(
        cursor.execution.execution_id,
        evidence,
        tenant_id=cursor.execution.tenant_id,
        expected_epoch=cursor.execution.epoch,
    )
    return _progress(cursor)


async def _skip_inapplicable_error_handlers(
    cursor: _LifecycleCursor,
    error_plan: tuple[PlannedTask, ...],
    primary_state: ExecutionState,
    handler_errors: Mapping[str, Mapping[str, Any]],
    skip_lifecycle_tasks: SkipLifecycleTasks,
) -> None:
    skip_ids = {
        node.task.id
        for node in error_plan
        if primary_state not in {ExecutionState.FAILED, ExecutionState.CANCELLED}
        or not _error_handler_is_applicable(
            node,
            primary_state,
            handler_errors.get(node.task.id),
        )
    }
    if skip_ids:
        cursor.task_runs = await skip_lifecycle_tasks(
            cursor.task_runs,
            skip_ids,
            LifecyclePhase.ERROR,
            tenant_id=cursor.execution.tenant_id,
            reason=f"error handler not selected for {primary_state.value}",
        )


async def advance_execution_lifecycle(
    flow: FlowDefinition,
    execution: PersistedExecution,
    execution_plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    *,
    primary_decision: OrchestrationDecision | None,
    max_tasks: int | None,
    repository: LifecycleExecutionRepository,
    finish_execution: FinishExecution,
    run_lifecycle_phase: RunLifecyclePhase,
    skip_lifecycle_tasks: SkipLifecycleTasks,
    claimed_tasks: int = 0,
    primary_failure: str | None = None,
) -> ExecutionProgress:
    """Advance exactly one durable lifecycle checkpoint."""

    cursor = _LifecycleCursor(execution, task_runs, claimed_tasks)
    lifecycle_plan = _lifecycle_plan(execution_plan)
    if not lifecycle_plan:
        return await _without_lifecycle(
            flow,
            cursor,
            primary_decision,
            primary_failure,
            finish_execution,
        )

    evidence, primary_state, phase_evidence = await _initialize_primary_evidence(
        cursor,
        execution_plan,
        primary_decision,
        primary_failure,
        repository,
    )
    handler_errors = _handler_error_contexts(execution_plan, cursor.task_runs, primary_state)

    error_plan = _phase_plan(lifecycle_plan, LifecyclePhase.ERROR)
    if not _phase_was_completed(phase_evidence, LifecyclePhase.ERROR):
        await _skip_inapplicable_error_handlers(
            cursor,
            error_plan,
            primary_state,
            handler_errors,
            skip_lifecycle_tasks,
        )
        return await _run_phase(
            flow,
            cursor,
            error_plan,
            phase=LifecyclePhase.ERROR,
            next_status=LifecyclePhase.FINALLY.value,
            evidence=evidence,
            phase_evidence=phase_evidence,
            handler_errors=handler_errors,
            max_tasks=max_tasks,
            repository=repository,
            run_lifecycle_phase=run_lifecycle_phase,
        )

    finally_plan = _phase_plan(lifecycle_plan, LifecyclePhase.FINALLY)
    if not _phase_was_completed(phase_evidence, LifecyclePhase.FINALLY):
        return await _run_phase(
            flow,
            cursor,
            finally_plan,
            phase=LifecyclePhase.FINALLY,
            next_status=LifecyclePhase.AFTER_EXECUTION.value,
            evidence=evidence,
            phase_evidence=phase_evidence,
            handler_errors={},
            max_tasks=max_tasks,
            repository=repository,
            run_lifecycle_phase=run_lifecycle_phase,
        )

    if cursor.execution.state is ExecutionState.RUNNING:
        cursor.execution = await finish_execution(
            flow,
            cursor.execution,
            OrchestrationDecision(
                terminal_state=primary_state,
                diagnostic=(
                    str(evidence["primary"].get("diagnostic"))
                    if isinstance(evidence["primary"], Mapping)
                    and evidence["primary"].get("diagnostic")
                    else None
                ),
            ),
            cursor.task_runs,
        )
        return _progress(cursor)

    after_plan = _phase_plan(lifecycle_plan, LifecyclePhase.AFTER_EXECUTION)
    if not _phase_was_completed(phase_evidence, LifecyclePhase.AFTER_EXECUTION):
        terminal_errors = _handler_error_contexts(
            execution_plan,
            cursor.task_runs,
            primary_state,
        )
        return await _run_phase(
            flow,
            cursor,
            after_plan,
            phase=LifecyclePhase.AFTER_EXECUTION,
            next_status="COMPLETE",
            evidence=evidence,
            phase_evidence=phase_evidence,
            handler_errors=terminal_errors,
            max_tasks=max_tasks,
            repository=repository,
            run_lifecycle_phase=run_lifecycle_phase,
        )
    return _progress(cursor)
