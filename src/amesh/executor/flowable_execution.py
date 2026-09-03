from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from amesh.domain import FailureCategory
from amesh.dsl import FlowableFailurePolicy, FlowDefinition, PlannedTask
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext
from amesh.ports import PersistedExecution, PersistedTaskRun, TaskRunState

from .contracts import BranchDecision, ConditionDecision, classify_task_failure
from .flowable_core import (
    _agent_mesh_budget_error,
    _aggregate_flowable_result,
    _branch_evidence,
    _descends_from,
    _flowable_expression_context,
    _merge_completion_evidence,
    _merge_task_control,
)
from .orchestration_core import (
    _dependencies_satisfied,
    _parent_is_running,
    _task_run_is_terminal,
)


class FlowableExecutionRepository(Protocol):
    """Durable task transitions required by flowable coordination."""

    async def start_task(
        self,
        task_run_id: UUID,
        *,
        tenant_id: str,
        dispatch: bool = True,
        priority: int = 0,
        worker_group: str | None = None,
    ) -> PersistedTaskRun: ...

    async def record_task_control(
        self,
        task_run_id: UUID,
        attempt: int,
        evidence: dict[str, object],
        *,
        tenant_id: str,
    ) -> PersistedTaskRun: ...

    async def skip_task(
        self,
        task_run_id: UUID,
        result: dict[str, Any],
        *,
        tenant_id: str,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun: ...

    async def complete_task(
        self,
        task_run_id: UUID,
        attempt: int,
        result: dict[str, Any],
        *,
        tenant_id: str,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun: ...

    async def fail_task(
        self,
        task_run_id: UUID,
        attempt: int,
        reason: str,
        *,
        tenant_id: str,
        result: dict[str, object] | None = None,
        worker_id: UUID | None = None,
        fencing_token: int | None = None,
        failure_category: FailureCategory = FailureCategory.NON_RETRYABLE,
        evidence: dict[str, object] | None = None,
    ) -> PersistedTaskRun: ...


class EvaluateTaskCondition(Protocol):
    def __call__(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> ConditionDecision: ...


class SelectBranch(Protocol):
    def __call__(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> BranchDecision: ...


class FinalizeWorkingDirectory(Protocol):
    async def __call__(
        self,
        execution: PersistedExecution,
        node: PlannedTask,
        task_run: PersistedTaskRun,
        *,
        failed: bool,
    ) -> tuple[dict[str, object], dict[str, object]]: ...


@dataclass(frozen=True)
class _FlowableReduction:
    children: list[PersistedTaskRun]
    failed: list[PersistedTaskRun]
    terminal: bool
    mesh_budget_error: str | None
    workspace_output: dict[str, object]
    workspace_evidence: dict[str, object]


@dataclass(frozen=True)
class _EnsuredBranch:
    changed: bool
    selected_branch: str | None = None
    failed: bool = False


async def advance_flowables(
    flow: FlowDefinition,
    execution: PersistedExecution,
    plan: tuple[PlannedTask, ...],
    task_runs: list[PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    evaluate_task_condition: EvaluateTaskCondition,
    select_branch: SelectBranch,
    finalize_working_directory: FinalizeWorkingDirectory,
    handler_errors: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[PersistedTaskRun]:
    """Start and reduce durable flowable parents without dispatching handlers."""

    by_node_id = {node.task.id: node for node in plan}
    by_task_id = {task_run.task_id: task_run for task_run in task_runs}
    changed = True
    while changed:
        changed = False
        changed = (
            await _start_waiting_flowables(
                flow,
                execution,
                plan,
                by_node_id,
                by_task_id,
                tenant_id=tenant_id,
                repository=repository,
                evaluate_task_condition=evaluate_task_condition,
                handler_errors=handler_errors,
            )
            or changed
        )
        changed = (
            await _select_conditional_branches(
                flow,
                execution,
                plan,
                by_node_id,
                by_task_id,
                tenant_id=tenant_id,
                repository=repository,
                select_branch=select_branch,
                handler_errors=handler_errors,
            )
            or changed
        )
        changed = (
            await _reduce_running_flowables(
                execution,
                plan,
                by_task_id,
                tenant_id=tenant_id,
                repository=repository,
                finalize_working_directory=finalize_working_directory,
            )
            or changed
        )
    return list(by_task_id.values())


async def _start_waiting_flowables(
    flow: FlowDefinition,
    execution: PersistedExecution,
    plan: tuple[PlannedTask, ...],
    by_node_id: Mapping[str, PlannedTask],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    evaluate_task_condition: EvaluateTaskCondition,
    handler_errors: Mapping[str, Mapping[str, Any]] | None,
) -> bool:
    changed = False
    for node in plan:
        task_run = by_task_id[node.task.id]
        if not node.flowable or node.dynamic or task_run.state is not TaskRunState.WAITING:
            continue
        if not _parent_is_running(node, by_task_id):
            continue
        if not _dependencies_satisfied(node, by_node_id, by_task_id):
            continue
        expression_context = _flowable_expression_context(
            flow,
            execution,
            node,
            task_run,
            plan,
            by_task_id,
            handler_error=(handler_errors or {}).get(node.task.id),
        )
        run_if = evaluate_task_condition(
            flow,
            execution,
            node.task,
            expression_context,
            (handler_errors or {}).get(node.task.id),
        )
        if run_if.error is not None:
            running = await repository.start_task(
                task_run.task_run_id,
                tenant_id=tenant_id,
                dispatch=False,
            )
            reason = f"flowable runIf failed: {run_if.error}"
            by_task_id[node.task.id] = await repository.fail_task(
                running.task_run_id,
                running.current_attempt,
                reason,
                tenant_id=tenant_id,
                failure_category=FailureCategory.CONFIGURATION,
                evidence=run_if.evidence,
            )
            changed = True
            continue
        if not run_if.matched:
            changed = (
                await _skip_flowable_subtree(
                    node,
                    plan,
                    by_node_id,
                    by_task_id,
                    tenant_id=tenant_id,
                    evidence=run_if.evidence,
                    repository=repository,
                )
                or changed
            )
            continue
        running = await repository.start_task(
            task_run.task_run_id,
            tenant_id=tenant_id,
            dispatch=False,
        )
        if node.task.run_if is not None or node.task.error_selector is not None:
            running = await repository.record_task_control(
                running.task_run_id,
                running.current_attempt,
                run_if.evidence,
                tenant_id=tenant_id,
            )
        by_task_id[node.task.id] = running
        changed = True
    return changed


async def _select_conditional_branches(
    flow: FlowDefinition,
    execution: PersistedExecution,
    plan: tuple[PlannedTask, ...],
    by_node_id: Mapping[str, PlannedTask],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    select_branch: SelectBranch,
    handler_errors: Mapping[str, Mapping[str, Any]] | None,
) -> bool:
    changed = False
    for node in plan:
        task_run = by_task_id[node.task.id]
        if node.mode not in {"IF", "SWITCH"} or task_run.state is not TaskRunState.RUNNING:
            continue
        branch = await _ensure_branch_decision(
            flow,
            execution,
            node,
            task_run,
            plan,
            by_task_id,
            tenant_id=tenant_id,
            repository=repository,
            select_branch=select_branch,
            handler_error=(handler_errors or {}).get(node.task.id),
        )
        changed = branch.changed or changed
        if branch.failed:
            continue
        changed = (
            await _skip_nonselected_branches(
                node,
                plan,
                by_node_id,
                by_task_id,
                selected_branch=branch.selected_branch,
                tenant_id=tenant_id,
                repository=repository,
            )
            or changed
        )
    return changed


async def _ensure_branch_decision(
    flow: FlowDefinition,
    execution: PersistedExecution,
    node: PlannedTask,
    task_run: PersistedTaskRun,
    plan: tuple[PlannedTask, ...],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    select_branch: SelectBranch,
    handler_error: Mapping[str, Any] | None,
) -> _EnsuredBranch:
    branch_evidence = _branch_evidence(task_run.evidence)
    changed = False
    if branch_evidence is None:
        expression_context = _flowable_expression_context(
            flow,
            execution,
            node,
            task_run,
            plan,
            by_task_id,
            handler_error=handler_error,
        )
        decision = select_branch(flow, execution, node.task, expression_context)
        evidence = _merge_task_control(task_run.evidence, "branch", decision.evidence)
        if decision.error is not None:
            reason = f"conditional branch evaluation failed: {decision.error}"
            by_task_id[node.task.id] = await repository.fail_task(
                task_run.task_run_id,
                task_run.current_attempt,
                reason,
                tenant_id=tenant_id,
                failure_category=FailureCategory.CONFIGURATION,
                evidence=evidence,
            )
            return _EnsuredBranch(changed=True, failed=True)
        task_run = await repository.record_task_control(
            task_run.task_run_id,
            task_run.current_attempt,
            evidence,
            tenant_id=tenant_id,
        )
        by_task_id[node.task.id] = task_run
        branch_evidence = decision.evidence
        changed = True
    selected_branch = branch_evidence.get("selectedBranch")
    if selected_branch is not None and not isinstance(selected_branch, str):
        selected_branch = str(selected_branch)
    return _EnsuredBranch(changed=changed, selected_branch=selected_branch)


async def _skip_flowable_subtree(
    node: PlannedTask,
    plan: tuple[PlannedTask, ...],
    by_node_id: Mapping[str, PlannedTask],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    evidence: dict[str, object],
    repository: FlowableExecutionRepository,
) -> bool:
    changed = False
    for candidate in reversed(plan):
        if candidate.task.id != node.task.id and not _descends_from(
            candidate,
            node,
            by_node_id,
        ):
            continue
        task_run = by_task_id[candidate.task.id]
        if task_run.state is not TaskRunState.WAITING:
            continue
        by_task_id[candidate.task.id] = await repository.skip_task(
            task_run.task_run_id,
            {
                "skipped": True,
                "reason": f"flowable {node.task.id!r} runIf evaluated false",
                "controlTask": node.task.id,
            },
            tenant_id=tenant_id,
            evidence=(
                evidence
                if candidate.task.id == node.task.id
                else {
                    "control": {
                        "parentTask": node.task.id,
                        "reason": "parent flowable skipped",
                    }
                }
            ),
        )
        changed = True
    return changed


async def _skip_nonselected_branches(
    node: PlannedTask,
    plan: tuple[PlannedTask, ...],
    by_node_id: Mapping[str, PlannedTask],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    selected_branch: str | None,
    tenant_id: str,
    repository: FlowableExecutionRepository,
) -> bool:
    selected_path = (
        f"{node.branch_id}/{selected_branch}"
        if node.branch_id is not None and selected_branch is not None
        else selected_branch
    )
    changed = False
    for candidate in reversed(plan):
        if not _descends_from(candidate, node, by_node_id):
            continue
        if (
            selected_path is not None
            and candidate.branch_id is not None
            and (
                candidate.branch_id == selected_path
                or candidate.branch_id.startswith(f"{selected_path}/")
            )
        ):
            continue
        task_run = by_task_id[candidate.task.id]
        if task_run.state is not TaskRunState.WAITING:
            continue
        by_task_id[candidate.task.id] = await repository.skip_task(
            task_run.task_run_id,
            {
                "skipped": True,
                "reason": f"conditional branch {selected_branch!r} selected",
                "controlTask": node.task.id,
                "branch": candidate.branch_id,
                "selectedBranch": selected_branch,
            },
            tenant_id=tenant_id,
            evidence={
                "control": {
                    "parentTask": node.task.id,
                    "branch": candidate.branch_id,
                    "selectedBranch": selected_branch,
                }
            },
        )
        changed = True
    return changed


async def _reduce_running_flowables(
    execution: PersistedExecution,
    plan: tuple[PlannedTask, ...],
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    finalize_working_directory: FinalizeWorkingDirectory,
) -> bool:
    changed = False
    for node in reversed(plan):
        task_run = by_task_id[node.task.id]
        if not node.flowable or node.dynamic or task_run.state is not TaskRunState.RUNNING:
            continue
        reduction = await _prepare_reduction(
            execution,
            node,
            task_run,
            by_task_id,
            tenant_id=tenant_id,
            repository=repository,
            finalize_working_directory=finalize_working_directory,
        )
        if reduction is None:
            changed = True
            continue
        changed = (
            await _persist_reduction(
                node,
                task_run,
                reduction,
                by_task_id,
                tenant_id=tenant_id,
                repository=repository,
            )
            or changed
        )
    return changed


async def _prepare_reduction(
    execution: PersistedExecution,
    node: PlannedTask,
    task_run: PersistedTaskRun,
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
    finalize_working_directory: FinalizeWorkingDirectory,
) -> _FlowableReduction | None:
    children = [by_task_id[child_id] for child_id in node.children]
    failed = [
        child for child in children if child.state in {TaskRunState.FAILED, TaskRunState.CANCELLED}
    ]
    terminal = all(_task_run_is_terminal(child) for child in children)
    mesh_budget_error = _agent_mesh_budget_error(node, children) if terminal else None
    workspace_output: dict[str, object] = {}
    workspace_evidence: dict[str, object] = {}
    should_finalize_workspace = node.task.type == "core.workingDirectory" and (
        terminal or (failed and node.failure_policy is FlowableFailurePolicy.FAIL_FAST)
    )
    if should_finalize_workspace:
        try:
            workspace_output, workspace_evidence = await finalize_working_directory(
                execution,
                node,
                task_run,
                failed=bool(failed),
            )
        except Exception as exc:
            reason = f"working directory finalization failed: {exc}"
            by_task_id[node.task.id] = await repository.fail_task(
                task_run.task_run_id,
                task_run.current_attempt,
                reason,
                tenant_id=tenant_id,
                failure_category=classify_task_failure(exc),
                evidence=task_run.evidence,
            )
            return None
    return _FlowableReduction(
        children=children,
        failed=failed,
        terminal=terminal,
        mesh_budget_error=mesh_budget_error,
        workspace_output=workspace_output,
        workspace_evidence=workspace_evidence,
    )


async def _persist_reduction(
    node: PlannedTask,
    task_run: PersistedTaskRun,
    reduction: _FlowableReduction,
    by_task_id: dict[str, PersistedTaskRun],
    *,
    tenant_id: str,
    repository: FlowableExecutionRepository,
) -> bool:
    if reduction.failed and node.failure_policy is FlowableFailurePolicy.FAIL_FAST:
        failed_ids = [child.task_id for child in reduction.failed]
        reason = f"flowable child failure: {failed_ids}"
        by_task_id[node.task.id] = await repository.fail_task(
            task_run.task_run_id,
            task_run.current_attempt,
            reason,
            tenant_id=tenant_id,
            result={
                **_aggregate_flowable_result(node, reduction.children),
                **reduction.workspace_output,
                "error": reason,
            },
            evidence=_merge_completion_evidence(
                reduction.workspace_evidence,
                task_run.evidence,
            ),
        )
        return True
    if reduction.mesh_budget_error is not None:
        by_task_id[node.task.id] = await repository.fail_task(
            task_run.task_run_id,
            task_run.current_attempt,
            reduction.mesh_budget_error,
            tenant_id=tenant_id,
            failure_category=FailureCategory.NON_RETRYABLE,
            result={
                **_aggregate_flowable_result(node, reduction.children),
                "error": reduction.mesh_budget_error,
            },
            evidence=task_run.evidence,
        )
        return True
    if reduction.terminal and (
        not reduction.failed or node.failure_policy is FlowableFailurePolicy.CONTINUE_ON_ERROR
    ):
        by_task_id[node.task.id] = await repository.complete_task(
            task_run.task_run_id,
            task_run.current_attempt,
            {
                **_aggregate_flowable_result(node, reduction.children),
                **reduction.workspace_output,
                **(
                    {"control": task_run.evidence["control"]}
                    if task_run.evidence.get("control")
                    else {}
                ),
            },
            tenant_id=tenant_id,
            evidence=_merge_completion_evidence(
                reduction.workspace_evidence,
                task_run.evidence,
            ),
        )
        return True
    if reduction.terminal and node.failure_policy is FlowableFailurePolicy.COLLECT_ALL:
        failed_ids = [child.task_id for child in reduction.failed]
        reason = f"flowable collected child failures: {failed_ids}"
        by_task_id[node.task.id] = await repository.fail_task(
            task_run.task_run_id,
            task_run.current_attempt,
            reason,
            tenant_id=tenant_id,
            result={
                **_aggregate_flowable_result(node, reduction.children),
                **reduction.workspace_output,
                "error": reason,
            },
            evidence=_merge_completion_evidence(
                reduction.workspace_evidence,
                task_run.evidence,
            ),
        )
        return True
    return False
