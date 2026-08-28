from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

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
