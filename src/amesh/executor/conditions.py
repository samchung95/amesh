from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from amesh.dsl import FlowDefinition
from amesh.dsl.models import ConditionErrorPolicy, ErrorSelector, TaskDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine
from amesh.ports import PersistedExecution

from .contracts import BranchDecision, ConditionDecision
from .flowable_core import (
    _merge_control_evidence,
    _merge_task_control,
    _redact_condition_value,
    _redacted_condition_inputs,
    _sensitive_input_values,
    switch_case_key,
)

__all__ = ["ConditionEvaluator"]


class ConditionEvaluator:
    """Evaluate task conditions and flowable branch selection."""

    def __init__(self, expressions: ExpressionEngine) -> None:
        self._expressions = expressions

    def evaluate_run_if(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> ConditionDecision:
        if task.run_if is None:
            return ConditionDecision(matched=True, evidence={})
        record: dict[str, object] = {
            "kind": "runIf",
            "expression": task.run_if,
            "conditionInputs": _redacted_condition_inputs(flow, execution, context),
            "policy": task.condition_error_policy.value,
        }
        try:
            matched = self._expressions.evaluate_condition(task.run_if, context)
        except Exception as exc:
            record.update(
                {
                    "result": False,
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                }
            )
            evidence = _merge_task_control({}, "runIf", record)
            if task.condition_error_policy is ConditionErrorPolicy.FALSE:
                return ConditionDecision(matched=False, evidence=evidence)
            return ConditionDecision(matched=False, evidence=evidence, error=exc)
        record["result"] = matched
        return ConditionDecision(
            matched=matched,
            evidence=_merge_task_control({}, "runIf", record),
        )

    def evaluate_error_selector(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        selector: ErrorSelector | None,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> ConditionDecision:
        if selector is None:
            return ConditionDecision(matched=True, evidence={})
        raw_items = (handler_error or {}).get("items", ())
        items = [dict(item) for item in raw_items if isinstance(item, Mapping)]
        matched_items = [
            item
            for item in items
            if (not selector.states or item.get("state") in selector.states)
            and (not selector.categories or item.get("category") in selector.categories)
            and (not selector.task_ids or item.get("taskId") in selector.task_ids)
        ]
        record: dict[str, object] = {
            "kind": "errorSelector",
            "selector": selector.model_dump(mode="json", by_alias=True, exclude_none=True),
            "matchedTaskIds": [str(item.get("taskId")) for item in matched_items],
            "conditionInputs": _redacted_condition_inputs(flow, execution, context),
        }
        matched = bool(matched_items)
        if matched and selector.condition is not None:
            try:
                matched = self._expressions.evaluate_condition(selector.condition, context)
            except Exception as exc:
                record.update(
                    {
                        "result": False,
                        "error": {"type": type(exc).__name__, "message": str(exc)},
                    }
                )
                return ConditionDecision(
                    matched=False,
                    evidence=_merge_task_control({}, "errorSelector", record),
                    error=exc,
                )
        record["result"] = matched
        return ConditionDecision(
            matched=matched,
            evidence=_merge_task_control({}, "errorSelector", record),
        )

    def evaluate_task_condition(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
        handler_error: Mapping[str, Any] | None,
    ) -> ConditionDecision:
        selector = self.evaluate_error_selector(
            flow,
            execution,
            task.error_selector,
            context,
            handler_error,
        )
        if not selector.matched or selector.error is not None:
            return selector
        run_if = self.evaluate_run_if(flow, execution, task, context)
        return ConditionDecision(
            matched=run_if.matched,
            evidence=_merge_control_evidence(selector.evidence, run_if.evidence),
            error=run_if.error,
        )

    def select_branch(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
    ) -> BranchDecision:
        inputs = _redacted_condition_inputs(flow, execution, context)
        if task.type == "core.if":
            return self._select_if_branch(task, context, inputs)
        return self._select_switch_branch(flow, execution, task, context, inputs)

    def _select_if_branch(
        self,
        task: TaskDefinition,
        context: ExpressionContext,
        inputs: Mapping[str, object],
    ) -> BranchDecision:
        evaluations: list[dict[str, object]] = []
        policy = task.condition_error_policy
        branches = [("then", task.condition or "")]
        branches.extend((f"else-if:{branch.id}", branch.condition) for branch in task.else_if)
        for branch_id, expression in branches:
            try:
                result = self._expressions.evaluate_condition(expression, context)
            except Exception as exc:
                evaluations.append(_condition_error(branch_id, expression, exc))
                selected = "else" if policy is ConditionErrorPolicy.FALLBACK else None
                evidence = _branch_evidence("IF", inputs, evaluations, policy, selected)
                if policy is ConditionErrorPolicy.FAIL:
                    return BranchDecision(None, evidence, error=exc)
                if policy is ConditionErrorPolicy.FALLBACK:
                    return BranchDecision("else", evidence)
                continue
            evaluations.append({"branch": branch_id, "expression": expression, "result": result})
            if result:
                return BranchDecision(
                    branch_id,
                    _branch_evidence("IF", inputs, evaluations, policy, branch_id),
                )
        selected = "else" if task.else_tasks else None
        return BranchDecision(
            selected,
            _branch_evidence("IF", inputs, evaluations, policy, selected),
        )

    def _select_switch_branch(
        self,
        flow: FlowDefinition,
        execution: PersistedExecution,
        task: TaskDefinition,
        context: ExpressionContext,
        inputs: Mapping[str, object],
    ) -> BranchDecision:
        evaluations: list[dict[str, object]] = []
        policy = task.condition_error_policy
        try:
            rendered_selector = self._expressions.render_value(
                task.configuration.handler_view()["value"],
                context,
            )
        except Exception as exc:
            error_decision = _selector_error_decision(inputs, evaluations, policy, exc)
            if policy is not ConditionErrorPolicy.FALSE:
                return error_decision
            rendered_selector = None
        selector_key = switch_case_key(rendered_selector)
        redacted_selector = _redact_condition_value(
            rendered_selector,
            _sensitive_input_values(flow, execution),
        )
        exact = _select_exact_case(task, selector_key, evaluations)
        if exact is not None:
            return BranchDecision(
                exact,
                _switch_evidence(inputs, redacted_selector, evaluations, policy, exact),
            )
        predicate = self._select_predicate_case(
            task,
            context,
            inputs,
            redacted_selector,
            evaluations,
        )
        if predicate is not None:
            return predicate
        selected = "default" if "default" in task.cases else None
        return BranchDecision(
            selected,
            _switch_evidence(inputs, redacted_selector, evaluations, policy, selected),
        )

    def _select_predicate_case(
        self,
        task: TaskDefinition,
        context: ExpressionContext,
        inputs: Mapping[str, object],
        selector: object,
        evaluations: list[dict[str, object]],
    ) -> BranchDecision | None:
        policy = task.condition_error_policy
        for branch in task.predicate_cases:
            branch_id = f"predicate:{branch.id}"
            try:
                result = self._expressions.evaluate_condition(branch.condition, context)
            except Exception as exc:
                evaluations.append(_predicate_error(branch_id, branch.condition, exc))
                selected = "default" if policy is ConditionErrorPolicy.FALLBACK else None
                evidence = _switch_evidence(inputs, selector, evaluations, policy, selected)
                if policy is ConditionErrorPolicy.FAIL:
                    return BranchDecision(None, evidence, error=exc)
                if policy is ConditionErrorPolicy.FALLBACK:
                    return BranchDecision("default", evidence)
                continue
            evaluations.append(
                {
                    "kind": "predicate",
                    "branch": branch_id,
                    "expression": branch.condition,
                    "result": result,
                }
            )
            if result:
                return BranchDecision(
                    branch_id,
                    _switch_evidence(inputs, selector, evaluations, policy, branch_id),
                )
        return None


def _condition_error(branch: str, expression: str, exc: Exception) -> dict[str, object]:
    return {
        "branch": branch,
        "expression": expression,
        "result": False,
        "error": {"type": type(exc).__name__, "message": str(exc)},
    }


def _predicate_error(branch: str, expression: str, exc: Exception) -> dict[str, object]:
    return {
        "kind": "predicate",
        "branch": branch,
        "expression": expression,
        "result": False,
        "error": {"type": type(exc).__name__, "message": str(exc)},
    }


def _branch_evidence(
    kind: str,
    inputs: Mapping[str, object],
    evaluations: list[dict[str, object]],
    policy: ConditionErrorPolicy,
    selected: str | None,
) -> dict[str, object]:
    return {
        "kind": kind,
        "conditionInputs": inputs,
        "evaluations": evaluations,
        "policy": policy.value,
        "selectedBranch": selected,
    }


def _switch_evidence(
    inputs: Mapping[str, object],
    selector: object,
    evaluations: list[dict[str, object]],
    policy: ConditionErrorPolicy,
    selected: str | None,
) -> dict[str, object]:
    return {
        "kind": "SWITCH",
        "conditionInputs": inputs,
        "selector": selector,
        "evaluations": evaluations,
        "policy": policy.value,
        "selectedBranch": selected,
    }


def _selector_error_decision(
    inputs: Mapping[str, object],
    evaluations: list[dict[str, object]],
    policy: ConditionErrorPolicy,
    exc: Exception,
) -> BranchDecision:
    selected = "default" if policy is ConditionErrorPolicy.FALLBACK else None
    evaluations.append(
        {
            "kind": "selector",
            "result": False,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
    )
    evidence: dict[str, object] = {
        "kind": "SWITCH",
        "conditionInputs": inputs,
        "policy": policy.value,
        "selector": "[ERROR]",
        "evaluations": evaluations,
        "selectedBranch": selected,
    }
    if policy is ConditionErrorPolicy.FAIL:
        return BranchDecision(None, evidence, error=exc)
    return BranchDecision(selected, evidence)


def _select_exact_case(
    task: TaskDefinition,
    selector_key: str,
    evaluations: list[dict[str, object]],
) -> str | None:
    for case in task.cases:
        if case == "default":
            continue
        matched = selector_key == switch_case_key(case)
        branch = f"case:{case}"
        evaluations.append({"kind": "exact", "branch": branch, "result": matched})
        if matched:
            return branch
    return None
