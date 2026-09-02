from __future__ import annotations

import builtins
import re
from collections.abc import Callable, Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from functools import wraps
from time import monotonic
from typing import Any
from uuid import UUID

from jinja2 import StrictUndefined, Template, TemplateSyntaxError, Undefined, nodes
from jinja2.nativetypes import NativeEnvironment
from jinja2.runtime import Context
from jinja2.sandbox import ImmutableSandboxedEnvironment

from amesh.dsl.models import TaskDefinition

from .contracts import (
    CompiledExpression,
    ExpressionCompileError,
    ExpressionContext,
    ExpressionLimitError,
    ExpressionLimits,
    ExpressionRenderError,
    SecretString,
    redact_secret_values,
    redacted_text,
)
from .filters import (
    abbreviate,
    boolean,
    date_add,
    date_format,
    first,
    from_json,
    from_yaml,
    is_empty,
    keys,
    last,
    number,
    split,
    to_json,
    to_yaml,
    values,
)

COMPATIBILITY_VERSION = "kestra-pebble/1.3.30-subset-1"
_VARIABLE_BLOCK = re.compile(r"{{(.*?)}}", re.DOTALL)
_ELSEIF = re.compile(r"{%\s*elseif\b")
_MISSING = object()


@dataclass
class _SecretTracker:
    values: set[str] = field(default_factory=set)

    def add(self, value: str) -> str:
        if value:
            self.values.add(value)
        return value

    @property
    def fragments(self) -> tuple[str, ...]:
        return tuple(sorted(self.values, key=len, reverse=True))

    def redact(self, value: str) -> str:
        return redacted_text(value, self.fragments)


@dataclass
class _RenderSession:
    limits: ExpressionLimits
    deadline: float
    tracker: _SecretTracker
    values: dict[str, Any] = field(default_factory=dict)
    render_depth: int = 0

    def check_time(self) -> None:
        if monotonic() > self.deadline:
            raise ExpressionLimitError("expression render time limit exceeded")


_ACTIVE_SESSION: ContextVar[_RenderSession | None] = ContextVar(
    "amesh_expression_session",
    default=None,
)


class _SandboxedNativeEnvironment(ImmutableSandboxedEnvironment, NativeEnvironment):
    intercepted_binops = frozenset({"+", "*", "**"})

    def call_binop(self, context: Context, operator: str, left: Any, right: Any) -> Any:
        session = _ACTIVE_SESSION.get()
        if session is not None:
            session.check_time()
            _guard_amplifying_operator(operator, left, right, session.limits)
        result = super().call_binop(context, operator, left, right)
        if session is not None:
            _measure_value(result, session.limits, output=True)
            session.check_time()
        return result


class NativeExpressionEngine:
    """Bounded native evaluator with a declared Kestra Pebble compatibility subset."""

    compatibility_version = COMPATIBILITY_VERSION

    def __init__(self, limits: ExpressionLimits | None = None) -> None:
        self.limits = limits or ExpressionLimits()
        self._environment = _SandboxedNativeEnvironment(
            autoescape=False,
            undefined=StrictUndefined,
        )
        self._environment.globals.clear()
        self._environment.filters.clear()
        declared_filters: dict[str, Callable[..., Any]] = {
            "abbreviate": abbreviate,
            "boolean": boolean,
            "date": date_format,
            "dateAdd": date_add,
            "default": _default,
            "first": first,
            "fromJson": from_json,
            "fromYaml": from_yaml,
            "join": _join,
            "json": to_json,
            "keys": keys,
            "last": last,
            "length": len,
            "lower": _lower,
            "number": number,
            "replace": _replace,
            "reverse": _reverse,
            "sort": _sort,
            "split": split,
            "toJson": to_json,
            "toYaml": to_yaml,
            "trim": _trim,
            "upper": _upper,
            "values": values,
            "yaml": to_yaml,
        }
        self._environment.filters.update(
            {
                name: _track_secret_filter(filter_function)
                for name, filter_function in declared_filters.items()
            }
        )
        self._environment.tests.clear()
        self._environment.tests.update(
            {
                "boolean": lambda value: isinstance(value, bool),
                "defined": lambda value: not isinstance(value, Undefined),
                "empty": is_empty,
                "iterable": lambda value: isinstance(value, Mapping | Sequence),
                "mapping": lambda value: isinstance(value, Mapping),
                "null": lambda value: value is None,
                "number": lambda value: (
                    isinstance(value, int | float) and not isinstance(value, bool)
                ),
                "string": lambda value: isinstance(value, str),
            }
        )
        self._template_cache: dict[str, Template] = {}

    def compile(self, expression: str) -> CompiledExpression:
        if len(expression) > self.limits.max_template_chars:
            raise ExpressionCompileError(
                f"template exceeds {self.limits.max_template_chars} characters"
            )
        translated = _translate_pebble_subset(expression)
        try:
            parsed = self._environment.parse(translated)
            ast_nodes = 1 + sum(1 for _ in parsed.find_all(nodes.Node))
            if ast_nodes > self.limits.max_ast_nodes:
                raise ExpressionCompileError(
                    f"template exceeds {self.limits.max_ast_nodes} AST nodes"
                )
            self._compiled_template(translated)
        except ExpressionCompileError:
            raise
        except TemplateSyntaxError as exc:
            raise ExpressionCompileError(f"line {exc.lineno}: {exc.message}") from exc
        return CompiledExpression(
            source=expression,
            translated_source=translated,
            compatibility_version=self.compatibility_version,
            ast_nodes=ast_nodes,
        )

    def render_value(
        self,
        value: Any,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> Any:
        return self._evaluate(value, context, preview=False)

    def preview_value(
        self,
        value: Any,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> Any:
        return self._evaluate(value, context, preview=True)

    def render_task(
        self,
        task: TaskDefinition,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> TaskDefinition:
        payload = task.model_dump(mode="python", by_alias=True)
        for key in task.configuration.handler_view():
            payload[key] = self.render_value(payload[key], context)
        if task.command is not None:
            payload["command"] = [
                _string_value(self.render_value(argument, context)) for argument in task.command
            ]
        if task.image is not None:
            payload["image"] = _string_value(self.render_value(task.image, context))
        payload["environment"] = {
            key: _string_value(self.render_value(value, context))
            for key, value in task.environment.items()
        }
        payload["inputFiles"] = {
            key: _string_value(self.render_value(value, context))
            for key, value in task.input_files.items()
        }
        payload["outputFiles"] = [
            _string_value(self.render_value(value, context)) for value in task.output_files
        ]
        if task.output_manifest is not None:
            payload["outputManifest"] = _string_value(
                self.render_value(task.output_manifest, context)
            )
        payload["resources"] = self.render_value(task.resources, context)
        return TaskDefinition.model_validate(payload)

    def evaluate_condition(
        self,
        expression: str,
        context: Mapping[str, Any] | ExpressionContext,
    ) -> bool:
        rendered = self.render_value(expression, context)
        if not isinstance(rendered, bool):
            raise ExpressionRenderError("runIf must render to a boolean")
        return rendered

    def _evaluate(
        self,
        value: Any,
        context: Mapping[str, Any] | ExpressionContext,
        *,
        preview: bool,
    ) -> Any:
        public, secrets, key_values = _context_values(context)
        _measure_value(public, self.limits)
        _measure_value(secrets, self.limits)
        _measure_value(key_values, self.limits)
        tracker = _SecretTracker()
        session = _RenderSession(
            limits=self.limits,
            deadline=monotonic() + self.limits.max_render_seconds,
            tracker=tracker,
        )
        session.values = self._runtime_values(public, secrets, key_values, session)
        token = _ACTIVE_SESSION.set(session)
        try:
            rendered = self._render_value(value, session, 0)
            session.check_time()
            _measure_value(rendered, self.limits, output=True)
        except ExpressionCompileError:
            raise
        except ExpressionRenderError as exc:
            sanitized = tracker.redact(str(exc))
            if sanitized == str(exc):
                raise
            raise type(exc)(sanitized) from exc
        except Exception as exc:
            raise ExpressionRenderError(tracker.redact(str(exc))) from exc
        finally:
            _ACTIVE_SESSION.reset(token)
        marked = _mark_secret_values(rendered, tracker.fragments)
        return redact_secret_values(marked) if preview else marked

    def _runtime_values(
        self,
        public: Mapping[str, Any],
        secrets: Mapping[str, str],
        key_values: Mapping[str, Any],
        session: _RenderSession,
    ) -> dict[str, Any]:
        values = dict(public)

        def secret(name: str, default: Any = _MISSING) -> str:
            session.check_time()
            if name not in secrets:
                if default is _MISSING:
                    raise KeyError(f"secret {name!r} is not available")
                return str(default)
            resolved = session.tracker.add(str(secrets[name]))
            return SecretString(resolved, session.tracker.fragments)

        def kv(name: str, default: Any = _MISSING) -> Any:
            session.check_time()
            if name not in key_values:
                if default is _MISSING:
                    raise KeyError(f"key-value {name!r} is not available")
                return default
            return key_values[name]

        def render(nested: Any) -> Any:
            session.check_time()
            if not isinstance(nested, str):
                return nested
            if session.render_depth >= session.limits.max_render_depth:
                raise ExpressionLimitError("recursive render depth limit exceeded")
            session.render_depth += 1
            try:
                return self._render_string(nested, session)
            finally:
                session.render_depth -= 1

        values.update(
            {
                "coalesce": _coalesce,
                "kv": kv,
                "max": builtins.max,
                "min": builtins.min,
                "null": None,
                "render": render,
                "secret": secret,
            }
        )
        return values

    def _render_value(self, value: Any, session: _RenderSession, depth: int) -> Any:
        session.check_time()
        if depth > session.limits.max_value_depth:
            raise ExpressionLimitError("rendered value nesting limit exceeded")
        if isinstance(value, str):
            return self._render_string(value, session)
        if isinstance(value, list):
            return [self._render_value(item, session, depth + 1) for item in value]
        if isinstance(value, tuple):
            return tuple(self._render_value(item, session, depth + 1) for item in value)
        if isinstance(value, dict):
            return {
                key: self._render_value(item, session, depth + 1) for key, item in value.items()
            }
        return value

    def _render_string(self, value: str, session: _RenderSession) -> Any:
        if "{{" not in value and "{%" not in value:
            return value
        compiled = self.compile(value)
        try:
            rendered = self._compiled_template(compiled.translated_source).render(**session.values)
            if isinstance(rendered, Undefined):
                str(rendered)
            return rendered
        except ExpressionRenderError:
            raise
        except Exception as exc:
            raise ExpressionRenderError(session.tracker.redact(str(exc))) from exc

    def _compiled_template(self, translated_source: str) -> Template:
        cached = self._template_cache.get(translated_source)
        if cached is not None:
            return cached
        compiled = self._environment.from_string(translated_source)
        if len(self._template_cache) >= 512:
            self._template_cache.pop(next(iter(self._template_cache)))
        self._template_cache[translated_source] = compiled
        return compiled


def _context_values(
    context: Mapping[str, Any] | ExpressionContext,
) -> tuple[dict[str, Any], Mapping[str, str], Mapping[str, Any]]:
    if isinstance(context, ExpressionContext):
        return context.public_values(), context.secrets, context.key_values
    public = dict(context)
    secrets = public.pop("secrets", {})
    key_values = public.pop("keyValues", public.pop("key_values", {}))
    if not isinstance(secrets, Mapping) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in secrets.items()
    ):
        raise ExpressionRenderError("secrets context must map strings to strings")
    if not isinstance(key_values, Mapping):
        raise ExpressionRenderError("key-values context must be a mapping")
    return public, secrets, key_values


def _translate_pebble_subset(source: str) -> str:
    translated = _ELSEIF.sub("{% elif", source)
    return _VARIABLE_BLOCK.sub(
        lambda match: "{{" + _translate_coalesce(match.group(1)) + "}}",
        translated,
    )


def _translate_coalesce(expression: str) -> str:
    position = _top_level_coalesce(expression)
    if position is None:
        return expression
    left = expression[:position].strip()
    right = expression[position + 2 :].strip()
    if not left or not right:
        return expression
    return f" coalesce({left}, {_translate_coalesce(right)}) "


def _top_level_coalesce(expression: str) -> int | None:
    quote: str | None = None
    escaped = False
    depth = 0
    index = 0
    while index < len(expression) - 1:
        character = expression[index]
        if escaped:
            escaped = False
        elif character == "\\" and quote is not None:
            escaped = True
        elif character in {"'", '"'}:
            quote = None if quote == character else character if quote is None else quote
        elif quote is None:
            if character in "([{":
                depth += 1
            elif character in ")]}":
                depth = max(depth - 1, 0)
            elif character == "?" and expression[index + 1] == "?" and depth == 0:
                return index
        index += 1
    return None


def _guard_amplifying_operator(
    operator: str,
    left: Any,
    right: Any,
    limits: ExpressionLimits,
) -> None:
    if operator == "**" and (
        not isinstance(right, int | float)
        or abs(right) > 10
        or (isinstance(left, int | float) and abs(left) > 1_000_000)
    ):
        raise ExpressionLimitError("exponentiation exceeds expression limits")
    if operator == "*":
        sequence, multiplier = (left, right) if isinstance(right, int) else (right, left)
        if isinstance(multiplier, int) and isinstance(sequence, str | list | tuple):
            if multiplier < 0:
                return
            projected = len(sequence) * multiplier
            limit = (
                limits.max_output_bytes
                if isinstance(sequence, str)
                else limits.max_collection_items
            )
            if projected > limit:
                raise ExpressionLimitError("multiplication exceeds expression output limits")


def _measure_value(
    value: Any,
    limits: ExpressionLimits,
    *,
    output: bool = False,
    _depth: int = 0,
    _seen: set[int] | None = None,
) -> int:
    if _depth > limits.max_value_depth:
        raise ExpressionLimitError("expression value nesting limit exceeded")
    seen = _seen if _seen is not None else set()
    if isinstance(value, str | bytes | bytearray):
        size = len(value.encode("utf-8")) if isinstance(value, str) else len(value)
    elif value is None or isinstance(value, bool | int | float | datetime | date | UUID | Enum):
        size = len(str(value).encode("utf-8"))
    elif isinstance(value, Mapping):
        if len(value) > limits.max_collection_items:
            raise ExpressionLimitError("expression mapping cardinality limit exceeded")
        identity = id(value)
        if identity in seen:
            raise ExpressionLimitError("cyclic expression context is not supported")
        seen.add(identity)
        size = sum(
            _measure_value(key, limits, output=output, _depth=_depth + 1, _seen=seen)
            + _measure_value(item, limits, output=output, _depth=_depth + 1, _seen=seen)
            for key, item in value.items()
        )
        seen.remove(identity)
    elif isinstance(value, Sequence):
        if len(value) > limits.max_collection_items:
            raise ExpressionLimitError("expression collection cardinality limit exceeded")
        identity = id(value)
        if identity in seen:
            raise ExpressionLimitError("cyclic expression context is not supported")
        seen.add(identity)
        size = sum(
            _measure_value(item, limits, output=output, _depth=_depth + 1, _seen=seen)
            for item in value
        )
        seen.remove(identity)
    else:
        raise ExpressionLimitError(f"unsupported expression value type {type(value).__name__!r}")
    maximum = limits.max_output_bytes if output else limits.max_context_bytes
    if size > maximum:
        kind = "output" if output else "context"
        raise ExpressionLimitError(f"expression {kind} size limit exceeded")
    return size


def _mark_secret_values(value: Any, fragments: tuple[str, ...]) -> Any:
    if not fragments:
        return value
    if isinstance(value, str) and any(fragment in value for fragment in fragments if fragment):
        return SecretString(value, fragments)
    if isinstance(value, list):
        return [_mark_secret_values(item, fragments) for item in value]
    if isinstance(value, tuple):
        return tuple(_mark_secret_values(item, fragments) for item in value)
    if isinstance(value, dict):
        return {key: _mark_secret_values(item, fragments) for key, item in value.items()}
    return value


def _track_secret_filter(
    filter_function: Callable[..., Any],
) -> Callable[..., Any]:
    @wraps(filter_function)
    def tracked(value: Any, *args: Any, **kwargs: Any) -> Any:
        result = filter_function(value, *args, **kwargs)
        session = _ACTIVE_SESSION.get()
        if session is None or not _contains_secret_value(value):
            return result
        return _mark_derived_secret(result, session.tracker)

    return tracked


def _contains_secret_value(value: Any) -> bool:
    if isinstance(value, SecretString):
        return True
    if isinstance(value, Mapping):
        return any(_contains_secret_value(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return any(_contains_secret_value(item) for item in value)
    return False


def _mark_derived_secret(value: Any, tracker: _SecretTracker) -> Any:
    if isinstance(value, str):
        tracker.add(value)
        return SecretString(value, tracker.fragments)
    if isinstance(value, list):
        return [_mark_derived_secret(item, tracker) for item in value]
    if isinstance(value, tuple):
        return tuple(_mark_derived_secret(item, tracker) for item in value)
    if isinstance(value, dict):
        return {key: _mark_derived_secret(item, tracker) for key, item in value.items()}
    raise ExpressionRenderError("secret-derived filter results must remain strings")


def _string_value(value: Any) -> str:
    return value if isinstance(value, str) else str(value)


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is not None and not isinstance(value, Undefined):
            return value
    return None


def _default(value: Any, fallback: Any = "", use_false: bool = False) -> Any:
    if isinstance(value, Undefined) or value is None or (use_false and not value):
        return fallback
    return value


def _join(value: Sequence[Any], separator: str = "") -> str:
    return separator.join(str(item) for item in value)


def _lower(value: Any) -> str:
    return str(value).lower()


def _replace(value: Any, old: str, new: str) -> str:
    return str(value).replace(old, new)


def _reverse(value: Sequence[Any]) -> list[Any]:
    return list(reversed(value))


def _sort(value: Sequence[Any]) -> list[Any]:
    return sorted(value)


def _trim(value: Any) -> str:
    return str(value).strip()


def _upper(value: Any) -> str:
    return str(value).upper()
