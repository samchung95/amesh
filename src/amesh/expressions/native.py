from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from jinja2 import StrictUndefined, Undefined
from jinja2.nativetypes import NativeEnvironment
from jinja2.sandbox import SandboxedEnvironment

from amesh.dsl.models import TaskDefinition


class ExpressionRenderError(ValueError):
    """Raised when an AMESH-native expression cannot be rendered."""


class _SandboxedNativeEnvironment(SandboxedEnvironment, NativeEnvironment):
    pass


class NativeExpressionEngine:
    """Renders the intentionally small MVP expression context with native values."""

    def __init__(self) -> None:
        self._environment = _SandboxedNativeEnvironment(
            autoescape=False,
            undefined=StrictUndefined,
        )
        self._environment.globals.clear()

    def render_value(self, value: Any, context: Mapping[str, Any]) -> Any:
        if isinstance(value, str):
            return self._render_string(value, context)
        if isinstance(value, list):
            return [self.render_value(item, context) for item in value]
        if isinstance(value, tuple):
            return tuple(self.render_value(item, context) for item in value)
        if isinstance(value, dict):
            return {key: self.render_value(item, context) for key, item in value.items()}
        return value

    def render_task(
        self,
        task: TaskDefinition,
        context: Mapping[str, Any],
    ) -> TaskDefinition:
        payload = task.model_dump(mode="python", by_alias=True)
        for key in task.model_extra or {}:
            payload[key] = self.render_value(payload[key], context)
        if task.command is not None:
            payload["command"] = [
                str(self.render_value(argument, context)) for argument in task.command
            ]
        if task.image is not None:
            payload["image"] = str(self.render_value(task.image, context))
        payload["environment"] = {
            key: str(self.render_value(value, context)) for key, value in task.environment.items()
        }
        payload["resources"] = self.render_value(task.resources, context)
        return TaskDefinition.model_validate(payload)

    def evaluate_condition(
        self,
        expression: str,
        context: Mapping[str, Any],
    ) -> bool:
        rendered = self._render_string(expression, context)
        if not isinstance(rendered, bool):
            raise ExpressionRenderError("runIf must render to a boolean")
        return rendered

    def _render_string(self, value: str, context: Mapping[str, Any]) -> Any:
        if "{{" not in value and "{%" not in value:
            return value
        try:
            rendered = self._environment.from_string(value).render(**dict(context))
            if isinstance(rendered, Undefined):
                str(rendered)
            return rendered
        except Exception as exc:
            raise ExpressionRenderError(str(exc)) from exc
