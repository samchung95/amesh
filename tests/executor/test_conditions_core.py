from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

import pytest

from amesh.domain import ExecutionState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor.conditions import ConditionEvaluator
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports import PersistedExecution


class _RecordingEngine(NativeExpressionEngine):
    def __init__(
        self,
        outcomes: dict[str, bool | Exception] | None = None,
        *,
        rendered: object | Exception = None,
    ) -> None:
        super().__init__()
        self.outcomes = outcomes or {}
        self.rendered = rendered
        self.calls: list[tuple[str, object]] = []

    def evaluate_condition(self, expression: str, context: Any) -> bool:
        del context
        self.calls.append(("condition", expression))
        outcome = self.outcomes[expression]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def render_value(self, value: Any, context: Any) -> Any:
        del context
        self.calls.append(("render", value))
        if isinstance(self.rendered, Exception):
            raise self.rendered
        return self.rendered


def _execution(inputs: dict[str, object] | None = None) -> PersistedExecution:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return PersistedExecution(
        execution_id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id="default",
        state=ExecutionState.RUNNING,
        epoch=1,
        version=0,
        namespace="tests.conditions",
        flow_id="condition-flow",
        inputs=inputs or {},
        created_at=now,
        updated_at=now,
    )


def _flow(task: TaskDefinition, *, sensitive_input: bool = False) -> FlowDefinition:
    inputs = [{"id": "route", "type": "STRING", "sensitive": True}] if sensitive_input else []
    return FlowDefinition.model_validate(
        {
            "id": "condition-flow",
            "namespace": "tests.conditions",
            "inputs": inputs,
            "tasks": [task.model_dump(mode="json", by_alias=True, exclude_none=True)],
        }
    )


def _return_task(task_id: str) -> dict[str, object]:
    return {"id": task_id, "type": "core.return", "value": task_id}


def test_task_condition_selects_errors_before_run_if_and_merges_evidence() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "recover",
            "type": "core.return",
            "value": "recovered",
            "runIf": "run-if",
            "errorSelector": {
                "states": ["FAILED"],
                "categories": ["USER_CODE"],
                "taskIds": ["upstream"],
                "condition": "selector-condition",
            },
        }
    )
    flow = _flow(task, sensitive_input=True)
    execution = _execution({"route": "secret-route"})
    context = ExpressionContext(inputs=execution.inputs)
    engine = _RecordingEngine({"selector-condition": True, "run-if": True})
    decision = ConditionEvaluator(engine).evaluate_task_condition(
        flow,
        execution,
        task,
        context,
        {
            "items": [
                "ignored",
                {"taskId": "other", "state": "FAILED", "category": "USER_CODE"},
                {"taskId": "upstream", "state": "FAILED", "category": "USER_CODE"},
            ]
        },
    )

    assert decision.matched is True
    assert decision.error is None
    assert engine.calls == [
        ("condition", "selector-condition"),
        ("condition", "run-if"),
    ]
    control = cast(dict[str, Any], decision.evidence["control"])
    assert list(control) == ["errorSelector", "runIf"]
    selector = cast(dict[str, Any], control["errorSelector"])
    assert list(selector) == [
        "kind",
        "selector",
        "matchedTaskIds",
        "conditionInputs",
        "result",
    ]
    assert selector["matchedTaskIds"] == ["upstream"]
    assert selector["conditionInputs"]["inputs"]["route"] == "[REDACTED]"


def test_error_selector_miss_short_circuits_run_if() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "recover",
            "type": "core.return",
            "value": "recovered",
            "runIf": "run-if",
            "errorSelector": {"states": ["FAILED"]},
        }
    )
    flow = _flow(task)
    execution = _execution()
    engine = _RecordingEngine({"run-if": True})
    decision = ConditionEvaluator(engine).evaluate_task_condition(
        flow,
        execution,
        task,
        ExpressionContext(),
        {"items": [{"taskId": "upstream", "state": "CANCELLED"}]},
    )

    assert decision.matched is False
    assert engine.calls == []
    control = cast(dict[str, Any], decision.evidence["control"])
    assert list(control) == ["errorSelector"]


@pytest.mark.parametrize(
    ("policy", "has_error"),
    [("FALSE", False), ("FAIL", True)],
)
def test_run_if_error_policy_preserves_error_evidence(
    policy: str,
    has_error: bool,
) -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "guarded",
            "type": "core.return",
            "value": "guarded",
            "runIf": "broken",
            "conditionErrorPolicy": policy,
        }
    )
    flow = _flow(task)
    execution = _execution()
    decision = ConditionEvaluator(
        _RecordingEngine({"broken": RuntimeError("bad runIf")})
    ).evaluate_run_if(flow, execution, task, ExpressionContext())

    assert decision.matched is False
    assert (decision.error is not None) is has_error
    control = cast(dict[str, Any], decision.evidence["control"])
    assert control["runIf"] == {
        "kind": "runIf",
        "expression": "broken",
        "conditionInputs": ExpressionContext().public_values(),
        "policy": policy,
        "result": False,
        "error": {"type": "RuntimeError", "message": "bad runIf"},
    }


def test_error_selector_condition_error_is_returned_with_matching_items() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "recover",
            "type": "core.return",
            "value": "recovered",
            "errorSelector": {"states": ["FAILED"], "condition": "broken"},
        }
    )
    flow = _flow(task)
    execution = _execution()
    decision = ConditionEvaluator(
        _RecordingEngine({"broken": ValueError("bad selector condition")})
    ).evaluate_error_selector(
        flow,
        execution,
        task.error_selector,
        ExpressionContext(),
        {"items": [{"taskId": "upstream", "state": "FAILED"}]},
    )

    assert decision.matched is False
    assert isinstance(decision.error, ValueError)
    control = cast(dict[str, Any], decision.evidence["control"])
    selector = cast(dict[str, Any], control["errorSelector"])
    assert selector["matchedTaskIds"] == ["upstream"]
    assert selector["result"] is False
    assert selector["error"] == {
        "type": "ValueError",
        "message": "bad selector condition",
    }


@pytest.mark.parametrize(
    ("policy", "selected", "has_error", "calls"),
    [
        ("FALSE", "else-if:secondary", False, ["broken", "secondary"]),
        ("FALLBACK", "else", False, ["broken"]),
        ("FAIL", None, True, ["broken"]),
    ],
)
def test_if_branch_error_policy_preserves_order_and_evidence(
    policy: str,
    selected: str | None,
    has_error: bool,
    calls: list[str],
) -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "choose",
            "type": "core.if",
            "condition": "broken",
            "conditionErrorPolicy": policy,
            "then": [_return_task("primary")],
            "elseIf": [
                {
                    "id": "secondary",
                    "condition": "secondary",
                    "tasks": [_return_task("secondary-task")],
                }
            ],
            "else": [_return_task("fallback")],
        }
    )
    flow = _flow(task, sensitive_input=True)
    execution = _execution({"route": "secret-route"})
    engine = _RecordingEngine({"broken": RuntimeError("bad condition"), "secondary": True})
    decision = ConditionEvaluator(engine).select_branch(
        flow,
        execution,
        task,
        ExpressionContext(inputs=execution.inputs),
    )

    assert decision.selected_branch == selected
    assert (decision.error is not None) is has_error
    assert [value for kind, value in engine.calls if kind == "condition"] == calls
    assert list(decision.evidence) == [
        "kind",
        "conditionInputs",
        "evaluations",
        "policy",
        "selectedBranch",
    ]
    condition_inputs = cast(dict[str, Any], decision.evidence["conditionInputs"])
    evaluations = cast(list[dict[str, Any]], decision.evidence["evaluations"])
    assert condition_inputs["inputs"]["route"] == "[REDACTED]"
    assert evaluations[0] == {
        "branch": "then",
        "expression": "broken",
        "result": False,
        "error": {"type": "RuntimeError", "message": "bad condition"},
    }


def test_switch_false_policy_continues_after_selector_error_to_exact_null_case() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "choose",
            "type": "core.switch",
            "value": "selector",
            "conditionErrorPolicy": "FALSE",
            "cases": {
                "paid": [_return_task("paid")],
                "null": [_return_task("null")],
                "default": [_return_task("fallback")],
            },
        }
    )
    flow = _flow(task)
    execution = _execution()
    engine = _RecordingEngine(rendered=ValueError("bad selector"))
    decision = ConditionEvaluator(engine).select_branch(
        flow,
        execution,
        task,
        ExpressionContext(),
    )

    assert decision.selected_branch == "case:null"
    assert decision.error is None
    assert engine.calls == [("render", "selector")]
    assert decision.evidence["selector"] is None
    assert decision.evidence["evaluations"] == [
        {
            "kind": "selector",
            "result": False,
            "error": {"type": "ValueError", "message": "bad selector"},
        },
        {"kind": "exact", "branch": "case:paid", "result": False},
        {"kind": "exact", "branch": "case:null", "result": True},
    ]


@pytest.mark.parametrize(
    ("policy", "selected", "has_error"),
    [("FALLBACK", "default", False), ("FAIL", None, True)],
)
def test_switch_selector_error_preserves_special_evidence_order(
    policy: str,
    selected: str | None,
    has_error: bool,
) -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "choose",
            "type": "core.switch",
            "value": "selector",
            "conditionErrorPolicy": policy,
            "cases": {"default": [_return_task("fallback")]},
        }
    )
    flow = _flow(task)
    execution = _execution()
    decision = ConditionEvaluator(
        _RecordingEngine(rendered=ValueError("bad selector"))
    ).select_branch(flow, execution, task, ExpressionContext())

    assert decision.selected_branch == selected
    assert (decision.error is not None) is has_error
    assert list(decision.evidence) == [
        "kind",
        "conditionInputs",
        "policy",
        "selector",
        "evaluations",
        "selectedBranch",
    ]
    assert decision.evidence["selector"] == "[ERROR]"


def test_switch_predicates_follow_exact_cases_and_false_policy_continues() -> None:
    task = TaskDefinition.model_validate(
        {
            "id": "choose",
            "type": "core.switch",
            "value": "selector",
            "conditionErrorPolicy": "FALSE",
            "cases": {"paid": [_return_task("paid")]},
            "predicateCases": [
                {
                    "id": "broken",
                    "condition": "broken",
                    "tasks": [_return_task("broken-task")],
                },
                {
                    "id": "eligible",
                    "condition": "eligible",
                    "tasks": [_return_task("eligible-task")],
                },
            ],
        }
    )
    flow = _flow(task)
    execution = _execution()
    engine = _RecordingEngine(
        {"broken": RuntimeError("bad predicate"), "eligible": True},
        rendered="free",
    )
    decision = ConditionEvaluator(engine).select_branch(
        flow,
        execution,
        task,
        ExpressionContext(),
    )

    assert decision.selected_branch == "predicate:eligible"
    assert engine.calls == [
        ("render", "selector"),
        ("condition", "broken"),
        ("condition", "eligible"),
    ]
    evaluations = cast(list[dict[str, Any]], decision.evidence["evaluations"])
    assert [item["branch"] for item in evaluations] == [
        "case:paid",
        "predicate:broken",
        "predicate:eligible",
    ]
