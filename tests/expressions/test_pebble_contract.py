from __future__ import annotations

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest

from amesh.dsl.models import TaskDefinition
from amesh.executor.service import TaskExecutionContext, _run_core_log
from amesh.expressions import (
    COMPATIBILITY_VERSION,
    ExpressionCompileError,
    ExpressionContext,
    ExpressionLimitError,
    ExpressionLimits,
    ExpressionRenderError,
    NativeExpressionEngine,
    SecretString,
)

FIXTURE = Path(__file__).with_name("fixtures") / "kestra-1.3.30-pebble-subset.json"


def test_version_pinned_kestra_pebble_subset() -> None:
    corpus = json.loads(FIXTURE.read_text(encoding="utf-8"))
    engine = NativeExpressionEngine()

    assert corpus["compatibilityVersion"] == COMPATIBILITY_VERSION
    for case in corpus["cases"]:
        assert engine.render_value(case["template"], case["context"]) == case["expected"], case[
            "id"
        ]


def test_documented_context_renders_native_scalar_collection_and_object_values() -> None:
    context = ExpressionContext(
        flow={"id": "daily", "namespace": "acme.ops", "revision": 3},
        execution={"id": "exec-1", "state": "RUNNING"},
        task={"id": "transform", "type": "core.return"},
        taskrun={"id": "run-1", "attempt": 2},
        trigger={"id": "schedule", "date": "2026-08-22T09:30:00Z"},
        inputs={"count": 2},
        outputs={"load": {"rows": 5}},
        variables={"region": "apac"},
        labels={"team": "data"},
        namespace={"id": "acme.ops"},
        secrets={"TOKEN": "vault-token"},
        key_values={"limit": 10},
    )
    template = {
        "identity": "{{ flow.namespace ~ '.' ~ flow.id }}",
        "runtime": ["{{ execution.id }}", "{{ task.id }}", "{{ taskrun.attempt }}"],
        "event": ["{{ trigger.id }}", "{{ inputs.count }}", "{{ outputs.load.rows }}"],
        "metadata": {
            "variable": "{{ vars.region }}",
            "label": "{{ labels.team }}",
            "namespace": "{{ namespace.id }}",
        },
        "services": ["{{ secret('TOKEN') }}", "{{ kv('limit') }}"],
    }

    rendered = NativeExpressionEngine().render_value(template, context)

    assert rendered["identity"] == "acme.ops.daily"
    assert rendered["runtime"] == ["exec-1", "transform", 2]
    assert rendered["event"] == ["schedule", 2, 5]
    assert rendered["metadata"] == {
        "variable": "apac",
        "label": "data",
        "namespace": "acme.ops",
    }
    assert str(rendered["services"][0]) == "vault-token"
    assert isinstance(rendered["services"][0], SecretString)
    assert rendered["services"][1] == 10


def test_compile_and_runtime_failures_are_distinct() -> None:
    engine = NativeExpressionEngine()

    with pytest.raises(ExpressionCompileError, match="line 1"):
        engine.compile("{{ inputs.value")
    with pytest.raises(ExpressionRenderError, match="missing"):
        engine.render_value("{{ inputs.missing }}", {"inputs": {}})


@pytest.mark.parametrize(
    ("error_type", "engine", "value", "context", "message"),
    [
        (
            ExpressionCompileError,
            NativeExpressionEngine(ExpressionLimits(max_template_chars=8)),
            "{{ inputs.value }}",
            {"inputs": {"value": "ok"}},
            "template exceeds",
        ),
        (
            ExpressionLimitError,
            NativeExpressionEngine(ExpressionLimits(max_context_bytes=8)),
            "{{ inputs.value }}",
            {"inputs": {"value": "context-is-too-large"}},
            "context size",
        ),
        (
            ExpressionLimitError,
            NativeExpressionEngine(ExpressionLimits(max_collection_items=2)),
            "{{ inputs.values }}",
            {"inputs": {"values": [1, 2, 3]}},
            "collection cardinality",
        ),
        (
            ExpressionLimitError,
            NativeExpressionEngine(ExpressionLimits(max_value_depth=2)),
            "{{ inputs.value }}",
            {"inputs": {"value": {"nested": {"too": "deep"}}}},
            "nesting limit",
        ),
        (
            ExpressionLimitError,
            NativeExpressionEngine(ExpressionLimits(max_output_bytes=16)),
            "{{ 'x' * 17 }}",
            {},
            "output limits",
        ),
        (
            ExpressionLimitError,
            NativeExpressionEngine(ExpressionLimits(max_render_depth=2)),
            "{{ render(vars.loop) }}",
            {"vars": {"loop": "{{ render(vars.loop) }}"}},
            "recursive render depth",
        ),
    ],
)
def test_expression_resource_limits_are_enforced(
    error_type: type[Exception],
    engine: NativeExpressionEngine,
    value: str,
    context: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        engine.render_value(value, context)


def test_expression_render_time_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    ticks = iter((0.0, 1.0))
    monkeypatch.setattr("amesh.expressions.native.monotonic", lambda: next(ticks))

    with pytest.raises(ExpressionLimitError, match="time limit"):
        NativeExpressionEngine().render_value("{{ 1 + 1 }}", {})


def test_sandbox_rejects_unsafe_attribute_access() -> None:
    with pytest.raises(ExpressionRenderError):
        NativeExpressionEngine().render_value(
            "{{ inputs.value.__class__ }}", {"inputs": {"value": 1}}
        )


def test_secret_values_are_redacted_from_previews_errors_and_core_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    engine = NativeExpressionEngine()
    context = ExpressionContext(secrets={"TOKEN": "vault-token"})

    runtime = engine.render_value("Bearer {{ secret('TOKEN') }}", context)
    assert str(runtime) == "Bearer vault-token"
    assert repr(runtime) == "'Bearer [REDACTED]'"
    assert engine.preview_value("Bearer {{ secret('TOKEN') }}", context) == "Bearer [REDACTED]"
    assert engine.preview_value("{{ secret('TOKEN') | upper }}", context) == "[REDACTED]"
    with pytest.raises(ExpressionRenderError) as error:
        engine.render_value("{{ secret('TOKEN') | number }}", context)
    assert "vault-token" not in str(error.value)
    assert "[REDACTED]" in str(error.value)

    rendered_task = engine.render_task(
        TaskDefinition(id="log", type="core.log", message="{{ secret('TOKEN') | upper }}"),
        context,
    )
    task_context = TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
    )
    with caplog.at_level("INFO", logger="amesh.task.core.log"):
        result = asyncio.run(_run_core_log(rendered_task, task_context))
    assert result.output == {"message": "[REDACTED]"}
    assert result.logs[0].redacted is True
    assert "vault-token" not in caplog.text
    assert "[REDACTED]" in caplog.text
