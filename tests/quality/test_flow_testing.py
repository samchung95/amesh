from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from amesh.domain import FlowTestDefinition, FlowTestFixtureSource, FlowTestOutcome
from amesh.dsl import FlowDefinition
from amesh.flow_testing import FlowTestSimulator


def _definition(**changes: object) -> FlowTestDefinition:
    now = datetime.now(UTC)
    value: dict[str, object] = {
        "id": uuid4(),
        "tenantId": "default",
        "namespace": "tests.flow-unit",
        "flowId": "branching",
        "testId": "primary-route",
        "name": "primary route is deterministic",
        "revision": 3,
        "flowSemanticHash": "semantic-v3",
        "pluginSetHash": "plugins-v3",
        "inputs": {"route": "primary"},
        "variables": {},
        "fixtures": {
            "remote": {
                "source": "RECORDED",
                "output": {"message": "fixture-response"},
                "failuresBeforeSuccess": 1,
                "recordedAt": now,
            }
        },
        "expected": {
            "state": "SUCCESS",
            "outputs": {"message": "fixture-response", "iterationCount": 2},
            "taskStates": {
                "remote": "SUCCESS",
                "fallback": "SKIPPED",
                "loop[0].capture": "SUCCESS",
                "loop[1].capture": "SUCCESS",
                "always": "SUCCESS",
            },
            "taskOutputs": {"remote": {"message": "fixture-response"}},
        },
        "tags": ["ci", "recorded-fixture"],
        "version": 1,
        "createdBy": "user:test",
        "updatedBy": "user:test",
        "createdAt": now,
        "updatedAt": now,
    }
    value.update(changes)
    return FlowTestDefinition.model_validate(value)


def test_simulator_models_branches_retries_fixtures_generated_graph_and_finally() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "branching",
            "namespace": "tests.flow-unit",
            "revision": 3,
            "inputs": [{"id": "route", "type": "STRING", "required": True}],
            "tasks": [
                {
                    "id": "choose",
                    "type": "core.if",
                    "condition": "{{ inputs.route == 'primary' }}",
                    "then": [
                        {
                            "id": "remote",
                            "type": "plugin.recorded",
                            "retry": {"maxAttempts": 3},
                        }
                    ],
                    "else": [{"id": "fallback", "type": "core.return", "value": "fallback"}],
                },
                {
                    "id": "loop",
                    "type": "core.foreach",
                    "items": ["one", "two"],
                    "tasks": [
                        {
                            "id": "capture",
                            "type": "core.return",
                            "value": "{{ iteration.value }}",
                        }
                    ],
                },
            ],
            "finally": [{"id": "always", "type": "core.return", "value": "done"}],
            "outputs": {
                "message": "{{ outputs.remote.message }}",
                "iterationCount": "{{ outputs.loop.iterationCount }}",
            },
        }
    )

    result = FlowTestSimulator().simulate(flow, _definition())

    assert result.outcome is FlowTestOutcome.PASSED
    by_id = {task.task_id: task for task in result.tasks}
    assert by_id["remote"].attempts == 2
    assert by_id["remote"].fixture_source is FlowTestFixtureSource.RECORDED
    assert by_id["loop"].output == {
        "iterationCount": 2,
        "outputs": [
            {"capture": {"value": "one"}},
            {"capture": {"value": "two"}},
        ],
    }
    assert result.coverage.tasks_covered > 0
    assert result.coverage.handlers_total == result.coverage.handlers_covered == 1
    assert "not proof" in result.coverage.disclaimer


def test_simulator_runs_error_handlers_and_reports_expectation_failures() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "branching",
            "namespace": "tests.flow-unit",
            "revision": 3,
            "tasks": [{"id": "explode", "type": "plugin.failure"}],
            "errors": [{"id": "compensate", "type": "core.return", "value": "handled"}],
            "finally": [{"id": "always", "type": "core.return", "value": "done"}],
        }
    )
    definition = _definition(
        inputs={},
        fixtures={"explode": {"source": "INLINE", "error": "planned failure"}},
        expected={
            "state": "SUCCESS",
            "taskStates": {
                "explode": "FAILED",
                "compensate": "SUCCESS",
                "always": "SUCCESS",
            },
        },
    )

    result = FlowTestSimulator().simulate(flow, definition)

    assert result.outcome is FlowTestOutcome.FAILED
    assert result.state.value == "FAILED"
    assert next(item for item in result.assertions if item.path == "state").passed is False
    assert {task.task_id for task in result.tasks} >= {"explode", "compensate", "always"}


def test_simulator_rejects_secret_like_test_data() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "branching",
            "namespace": "tests.flow-unit",
            "revision": 3,
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )

    with pytest.raises(ValueError, match="secret-like"):
        FlowTestSimulator().simulate(
            flow,
            _definition(inputs={"apiToken": "must-not-be-stored"}, fixtures={}),
        )


def test_simulator_uses_executor_handler_values_for_datetime_and_explicit_null() -> None:
    occurred_at = datetime(2026, 9, 3, 12, 30, tzinfo=UTC)
    flow = FlowDefinition.model_validate(
        {
            "id": "raw-values",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "timestamp",
                    "type": "core.return",
                    "value": occurred_at,
                },
                {
                    "id": "null-switch",
                    "type": "core.switch",
                    "value": None,
                    "cases": {
                        "not-null": [
                            {
                                "id": "not-selected",
                                "type": "core.return",
                                "value": "wrong",
                            }
                        ],
                        "default": [
                            {
                                "id": "selected",
                                "type": "core.return",
                                "value": "default",
                            }
                        ],
                    },
                },
            ],
        }
    )

    timestamp_handler_values = flow.tasks[0].configuration.handler_view()
    switch_handler_values = flow.tasks[1].configuration.handler_view()
    result = FlowTestSimulator().simulate(
        flow,
        _definition(
            flowId="raw-values",
            inputs={},
            fixtures={},
            expected={"state": "SUCCESS"},
        ),
    )
    by_id = {task.task_id: task for task in result.tasks}

    assert timestamp_handler_values["value"] is occurred_at
    assert switch_handler_values["value"] is None
    assert by_id["timestamp"].output == {"value": occurred_at}
    assert by_id["null-switch"].output == {"selectedBranch": "default"}
    assert by_id["selected"].output == {"value": "default"}


def test_simulator_uses_executor_switch_key_and_no_match_semantics() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "switch-parity",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "boolean",
                    "type": "core.switch",
                    "value": True,
                    "cases": {
                        "true": [{"id": "boolean-hit", "type": "core.return", "value": "hit"}],
                        "default": [{"id": "boolean-miss", "type": "core.return", "value": "miss"}],
                    },
                },
                {
                    "id": "structured",
                    "type": "core.switch",
                    "value": {"b": 2, "a": 1},
                    "cases": {
                        '{"a":1,"b":2}': [
                            {"id": "structured-hit", "type": "core.return", "value": "hit"}
                        ]
                    },
                },
                {
                    "id": "unmatched",
                    "type": "core.switch",
                    "value": "missing",
                    "cases": {
                        "present": [{"id": "must-skip", "type": "core.return", "value": "wrong"}]
                    },
                },
            ],
        }
    )

    result = FlowTestSimulator().simulate(
        flow,
        _definition(
            flowId="switch-parity",
            inputs={},
            fixtures={},
            expected={"state": "SUCCESS"},
        ),
    )
    by_id = {task.task_id: task for task in result.tasks}

    assert by_id["boolean"].output == {"selectedBranch": "case:true"}
    assert by_id["boolean-hit"].state.value == "SUCCESS"
    assert by_id["boolean-miss"].state.value == "SKIPPED"
    assert by_id["structured"].output == {"selectedBranch": 'case:{"a":1,"b":2}'}
    assert by_id["structured-hit"].state.value == "SUCCESS"
    assert by_id["unmatched"].output == {"selectedBranch": None}
    assert by_id["must-skip"].state.value == "SKIPPED"


def test_simulator_switch_false_policy_matches_null_after_selector_error() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "switch-selector-false",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "choose",
                    "type": "core.switch",
                    "value": "{{ 1 / 0 }}",
                    "conditionErrorPolicy": "FALSE",
                    "cases": {
                        "null": [{"id": "null-hit", "type": "core.return", "value": "hit"}],
                        "default": [{"id": "fallback", "type": "core.return", "value": "miss"}],
                    },
                }
            ],
        }
    )

    result = FlowTestSimulator().simulate(
        flow,
        _definition(
            flowId=flow.id,
            inputs={},
            fixtures={},
            expected={"state": "SUCCESS"},
        ),
    )
    by_id = {task.task_id: task for task in result.tasks}

    assert by_id["choose"].output == {"selectedBranch": "case:null"}
    assert by_id["null-hit"].state.value == "SUCCESS"
    assert by_id["fallback"].state.value == "SKIPPED"


@pytest.mark.parametrize("has_default", [True, False])
def test_simulator_switch_fallback_policy_selects_logical_default_after_selector_error(
    has_default: bool,
) -> None:
    task = FlowDefinition.model_validate(
        {
            "id": "switch-selector-fallback",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "choose",
                    "type": "core.switch",
                    "value": "{{ 1 / 0 }}",
                    "conditionErrorPolicy": "FALLBACK",
                    "cases": {
                        "default": [{"id": "fallback", "type": "core.return", "value": "hit"}]
                    },
                }
            ],
        }
    ).tasks[0]
    if not has_default:
        task = task.model_copy(update={"cases": {"other": []}})
    flow = FlowDefinition.model_construct(
        id="switch-selector-fallback",
        namespace="tests.flow-unit",
        tasks=[task],
    )

    result = FlowTestSimulator().simulate(
        flow,
        _definition(
            flowId=flow.id,
            inputs={},
            fixtures={},
            expected={"state": "SUCCESS"},
        ),
    )
    by_id = {item.task_id: item for item in result.tasks}

    assert by_id["choose"].output == {"selectedBranch": "default"}
    if has_default:
        assert by_id["fallback"].state.value == "SUCCESS"


def test_simulator_switch_fail_policy_raises_selector_error() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "switch-selector-fail",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "choose",
                    "type": "core.switch",
                    "value": "{{ 1 / 0 }}",
                    "conditionErrorPolicy": "FAIL",
                    "cases": {
                        "default": [{"id": "fallback", "type": "core.return", "value": "miss"}]
                    },
                }
            ],
        }
    )

    with pytest.raises(ValueError, match="division by zero"):
        FlowTestSimulator().simulate(
            flow,
            _definition(
                flowId=flow.id,
                inputs={},
                fixtures={},
                expected={"state": "SUCCESS"},
            ),
        )


def test_simulator_uses_executor_foreach_order_batching_and_iteration_values() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "foreach-parity",
            "namespace": "tests.flow-unit",
            "tasks": [
                {
                    "id": "mapping",
                    "type": "core.foreach",
                    "items": {"z": 1, "a": 2},
                    "tasks": [
                        {
                            "id": "capture",
                            "type": "core.return",
                            "value": {
                                "index": "{{ iteration.index }}",
                                "key": "{{ iteration.key }}",
                                "value": "{{ iteration.value }}",
                                "parent": "{{ iteration.parent }}",
                            },
                        }
                    ],
                },
                {
                    "id": "ranged",
                    "type": "core.foreach",
                    "range": {"start": 1, "end": 6},
                    "batchSize": 2,
                    "tasks": [
                        {
                            "id": "capture",
                            "type": "core.return",
                            "value": "{{ iteration.value }}",
                        }
                    ],
                },
            ],
        }
    )

    result = FlowTestSimulator().simulate(
        flow,
        _definition(
            flowId="foreach-parity",
            inputs={},
            fixtures={},
            expected={"state": "SUCCESS"},
        ),
    )
    by_id = {task.task_id: task for task in result.tasks}

    first_mapping_value = by_id["mapping[0].capture"].output["value"]
    second_mapping_value = by_id["mapping[1].capture"].output["value"]
    assert {key: first_mapping_value[key] for key in ("index", "key", "value")} == {
        "index": 0,
        "key": "a",
        "value": 2,
    }
    assert {key: second_mapping_value[key] for key in ("index", "key", "value")} == {
        "index": 1,
        "key": "z",
        "value": 1,
    }
    assert first_mapping_value["parent"] == second_mapping_value["parent"]
    assert first_mapping_value["parent"]["taskId"] == "mapping"
    assert first_mapping_value["parent"]["attempt"] == 1
    assert UUID(first_mapping_value["parent"]["taskRunId"]).version == 5
    assert by_id["ranged"].output == {
        "iterationCount": 3,
        "outputs": [
            {
                "capture": {
                    "value": [
                        {"key": "0", "value": 1},
                        {"key": "1", "value": 2},
                    ]
                }
            },
            {
                "capture": {
                    "value": [
                        {"key": "2", "value": 3},
                        {"key": "3", "value": 4},
                    ]
                }
            },
            {"capture": {"value": [{"key": "4", "value": 5}]}},
        ],
    }
