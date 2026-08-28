from __future__ import annotations

import pytest

from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionRenderError, NativeExpressionEngine


def test_native_engine_renders_only_the_documented_context() -> None:
    engine = NativeExpressionEngine()
    context = {
        "inputs": {"name": "Ada"},
        "outputs": {"first": {"count": 2}},
        "vars": {"suffix": "items"},
    }
    task = TaskDefinition.model_validate(
        {
            "id": "render",
            "type": "core.return",
            "command": ["echo", "{{ inputs.name }}"],
            "environment": {"COUNT": "{{ outputs.first.count }}"},
            "value": {
                "message": "{{ inputs.name }} has {{ outputs.first.count }} {{ vars.suffix }}",
                "count": "{{ outputs.first.count }}",
            },
        }
    )

    rendered = engine.render_task(task, context)

    assert rendered.command == ["echo", "Ada"]
    assert rendered.environment == {"COUNT": "2"}
    assert rendered.model_extra == {"value": {"message": "Ada has 2 items", "count": 2}}
    assert engine.evaluate_condition("{{ outputs.first.count == 2 }}", context)


def test_native_engine_rejects_missing_values_and_non_boolean_conditions() -> None:
    engine = NativeExpressionEngine()

    with pytest.raises(ExpressionRenderError):
        engine.render_value("{{ inputs.missing }}", {"inputs": {}})
    with pytest.raises(ExpressionRenderError, match="runIf must render to a boolean"):
        engine.evaluate_condition("{{ inputs.name }}", {"inputs": {"name": "Ada"}})
