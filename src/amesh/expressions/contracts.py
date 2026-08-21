from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from typing import Any, Protocol

from amesh.dsl.models import TaskDefinition


class ExpressionError(ValueError):
    """Base class for versioned expression failures."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


class ExpressionCompileError(ExpressionError):
    """Raised before runtime values are used when expression syntax is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="expression_compile_error")


class ExpressionRenderError(ExpressionError):
    """Raised when a compiled expression cannot render against runtime values."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="expression_render_error")


class ExpressionLimitError(ExpressionRenderError):
    """Raised when expression input or evaluation exceeds a configured bound."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.code = "expression_limit_exceeded"


@dataclass(frozen=True)
class ExpressionLimits:
    max_template_chars: int = 65_536
    max_ast_nodes: int = 2_048
    max_context_bytes: int = 1_048_576
    max_collection_items: int = 2_000
    max_value_depth: int = 32
    max_render_depth: int = 5
    max_output_bytes: int = 1_048_576
    max_render_seconds: float = 0.5

    def __post_init__(self) -> None:
        for definition in fields(self):
            if getattr(self, definition.name) <= 0:
                raise ValueError(f"{definition.name} must be positive")


@dataclass(frozen=True)
class ExpressionContext:
    flow: Mapping[str, Any] = field(default_factory=dict)
    execution: Mapping[str, Any] = field(default_factory=dict)
    task: Mapping[str, Any] = field(default_factory=dict)
    taskrun: Mapping[str, Any] = field(default_factory=dict)
    trigger: Mapping[str, Any] = field(default_factory=dict)
    inputs: Mapping[str, Any] = field(default_factory=dict)
    outputs: Mapping[str, Any] = field(default_factory=dict)
    variables: Mapping[str, Any] = field(default_factory=dict)
    labels: Mapping[str, Any] = field(default_factory=dict)
    namespace: Mapping[str, Any] = field(default_factory=dict)
    secrets: Mapping[str, str] = field(default_factory=dict, repr=False)
    key_values: Mapping[str, Any] = field(default_factory=dict)

    def public_values(self) -> dict[str, Any]:
        return {
            "flow": self.flow,
            "execution": self.execution,
            "task": self.task,
            "taskrun": self.taskrun,
            "trigger": self.trigger,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "vars": self.variables,
            "labels": self.labels,
            "namespace": self.namespace,
        }


@dataclass(frozen=True)
class CompiledExpression:
    source: str
    translated_source: str
    compatibility_version: str
    ast_nodes: int


class ExpressionEngine(Protocol):
    compatibility_version: str

    def compile(self, expression: str) -> CompiledExpression: ...

    def render_value(
        self,
        value: Any,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> Any: ...

    def preview_value(
        self,
        value: Any,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> Any: ...

    def render_task(
        self,
        task: TaskDefinition,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> TaskDefinition: ...

    def evaluate_condition(
        self,
        expression: str,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> bool: ...


class SecretString(str):
    """Runtime string that retains redaction metadata without masking task use."""

    secret_fragments: tuple[str, ...]

    def __new__(cls, value: str, secret_fragments: tuple[str, ...]) -> SecretString:
        instance = super().__new__(cls, value)
        instance.secret_fragments = secret_fragments
        return instance

    def __repr__(self) -> str:
        return repr(redacted_text(str(self), self.secret_fragments))


def redacted_text(value: str, secret_fragments: tuple[str, ...]) -> str:
    redacted = value
    for secret in sorted(set(secret_fragments), key=len, reverse=True):
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def redact_secret_values(value: Any) -> Any:
    if isinstance(value, SecretString):
        return redacted_text(str(value), value.secret_fragments)
    if isinstance(value, list):
        return [redact_secret_values(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secret_values(item) for item in value)
    if isinstance(value, dict):
        return {key: redact_secret_values(item) for key, item in value.items()}
    return value
