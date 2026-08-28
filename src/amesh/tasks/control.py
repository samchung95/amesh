from __future__ import annotations

import asyncio
from typing import Any

from amesh.domain import FailureCategory
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskHandler,
    TaskUserCodeError,
)

_MAX_SLEEP_SECONDS = 86_400


def core_control_handlers() -> dict[str, TaskHandler]:
    return {
        "core.sleep": _run_sleep,
        "core.fail": _run_fail,
        "core.debug": _run_debug,
        "core.assert": _run_assert,
    }


async def _run_sleep(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
    extra = task.model_extra or {}
    seconds = extra.get("seconds")
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool):
        raise ValueError("sleep seconds must be a number")
    if seconds < 0 or seconds > _MAX_SLEEP_SECONDS:
        raise ValueError(f"sleep seconds must be between 0 and {_MAX_SLEEP_SECONDS}")
    if seconds:
        try:
            await asyncio.wait_for(context.cancellation.wait(), timeout=float(seconds))
        except TimeoutError:
            pass
        else:
            raise TaskExecutionFailure("sleep cancelled", FailureCategory.CANCELLED)
    return {"sleptSeconds": float(seconds)}


async def _run_fail(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
    del context
    message = (task.model_extra or {}).get("message", "task failed by request")
    if not isinstance(message, str) or not message:
        raise ValueError("fail message must be a non-empty string")
    raise TaskUserCodeError(message)


async def _run_assert(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
    del context
    extra = task.model_extra or {}
    value = extra.get("value")
    if not isinstance(value, bool):
        raise ValueError("assert value must be boolean")
    if not value:
        message = extra.get("message", "assertion failed")
        if not isinstance(message, str) or not message:
            raise ValueError("assert message must be a non-empty string")
        raise TaskUserCodeError(message)
    return {"asserted": True}


async def _run_debug(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
    extra = task.model_extra or {}
    requested = extra.get(
        "include",
        ["inputs", "outputs", "variables", "labels", "trigger", "iteration"],
    )
    allowed = {"inputs", "outputs", "variables", "labels", "trigger", "iteration", "files"}
    if not isinstance(requested, list) or not all(isinstance(item, str) for item in requested):
        raise ValueError("debug include must be an array of strings")
    unknown = sorted(set(requested) - allowed)
    if unknown:
        raise ValueError("debug include contains unsupported sections: " + ", ".join(unknown))
    values: dict[str, object] = {
        "inputs": dict(context.inputs),
        "outputs": {key: dict(value) for key, value in context.outputs.items()},
        "variables": dict(context.variables),
        "labels": dict(context.labels),
        "trigger": dict(context.trigger),
        "iteration": (context.iteration.as_mapping() if context.iteration is not None else None),
        "files": sorted(context.files),
    }
    return {
        "context": {section: values[section] for section in requested},
        "secretScopes": list(context.secret_scopes),
        "secretsRedacted": bool(context.secrets),
    }
