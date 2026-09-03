from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine, redact_secret_values

from .contracts import (
    TaskCompletion,
    TaskConfigurationError,
    TaskExecutionContext,
    TaskHandler,
    TaskLogRecord,
)
from .loops import LOOP_TASK_TYPES

LOGGER = logging.getLogger("amesh.task.core.log")


def _contains_kv_expression(value: object) -> bool:
    if isinstance(value, str):
        return "kv(" in value
    if isinstance(value, Mapping):
        return any(_contains_kv_expression(item) for item in value.values())
    if isinstance(value, list | tuple):
        return any(_contains_kv_expression(item) for item in value)
    return False


def _core_handlers() -> dict[str, TaskHandler]:
    return {
        "core.log": _run_core_log,
        "core.return": _run_core_return,
    }


async def _run_core_log(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskCompletion:
    extra = task.configuration.handler_view()
    message = str(redact_secret_values(extra.get("message", "")))
    LOGGER.info(
        message,
        extra={
            "tenant_id": context.tenant_id,
            "execution_id": str(context.execution_id),
            "task_run_id": str(context.task_run_id),
            "task_id": task.id,
        },
    )
    return TaskCompletion(
        output={"message": message},
        logs=(
            TaskLogRecord(
                logger="amesh.task.core.log",
                message=message,
                fields={"taskId": task.id},
                redacted=message == "[REDACTED]",
            ),
        ),
    )


async def _run_core_return(
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> dict[str, Any]:
    del context
    extra = task.configuration.handler_view()
    return {"value": extra.get("value")}


def _render_task_for_execution(
    expressions: ExpressionEngine,
    task: TaskDefinition,
    context: ExpressionContext,
) -> TaskDefinition:
    extra = task.configuration.handler_view()
    deferred_keys = (
        frozenset({"condition", "continueIf", "breakIf"})
        if task.type in LOOP_TASK_TYPES
        else frozenset({"outputMapping", "outputSchema", "artifactMapping", "artifactSchema"})
    )
    deferred = {key: extra[key] for key in deferred_keys if key in extra}
    if task.type not in {"core.subflow", *LOOP_TASK_TYPES} or not deferred:
        return expressions.render_task(task, context)

    payload = task.model_dump(mode="python", by_alias=True)
    for key in deferred:
        payload.pop(key, None)
    rendered = expressions.render_task(TaskDefinition.model_validate(payload), context)
    rendered_payload = rendered.model_dump(mode="python", by_alias=True)
    rendered_payload.update(deferred)
    return TaskDefinition.model_validate(rendered_payload)


def _combine_declared_files(*mappings: Mapping[str, str]) -> dict[str, str]:
    combined: dict[str, str] = {}
    for mapping in mappings:
        for path, reference in mapping.items():
            existing = combined.get(path)
            if existing is not None and existing != reference:
                raise TaskConfigurationError(
                    f"workspace path {path!r} has conflicting input file references"
                )
            combined[path] = reference
    return combined


def _render_declared_files(
    expressions: ExpressionEngine,
    declared_files: Mapping[str, str],
    context: ExpressionContext,
) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for path, reference in declared_files.items():
        value = expressions.render_value(reference, context)
        if not isinstance(value, str) or not value:
            raise TaskConfigurationError(
                f"inputFiles reference for {path!r} must render to a non-empty internal URI"
            )
        rendered[path] = str(value)
    return rendered
