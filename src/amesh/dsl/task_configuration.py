from __future__ import annotations

from collections.abc import Iterator, Mapping
from types import MappingProxyType
from typing import Any


def _copy_configuration_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _copy_configuration_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_copy_configuration_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_copy_configuration_value(item) for item in value)
    if isinstance(value, set):
        return {_copy_configuration_value(item) for item in value}
    if isinstance(value, frozenset):
        return frozenset(_copy_configuration_value(item) for item in value)
    return value


def _copy_configuration(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: _copy_configuration_value(value) for key, value in values.items()}


_TASK_STRUCTURAL_FIELDS = frozenset(
    {
        "id",
        "type",
        "description",
        "dependsOn",
        "runIf",
        "conditionErrorPolicy",
        "retry",
        "tasks",
        "condition",
        "then",
        "elseIf",
        "else",
        "cases",
        "predicateCases",
        "errors",
        "errorSelector",
        "contract",
        "taskCache",
    }
)
_LOOP_CONDITION_TYPES = frozenset({"core.while", "core.until"})


class TaskConfiguration(Mapping[str, Any]):
    """Immutable, kind-bound task configuration used for schema validation."""

    __slots__ = ("_handler_values", "_kind", "_values")
    _kind: str
    _values: Mapping[str, Any]
    _handler_values: Mapping[str, Any]

    def __init__(
        self,
        kind: str,
        values: Mapping[str, Any] | None = None,
        *,
        handler_values: Mapping[str, Any] | None = None,
    ) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(
            self,
            "_values",
            MappingProxyType(_copy_configuration(values or {})),
        )
        object.__setattr__(
            self,
            "_handler_values",
            MappingProxyType(
                _copy_configuration((values or {}) if handler_values is None else handler_values)
            ),
        )

    @classmethod
    def from_task_payload(
        cls,
        kind: str,
        payload: Mapping[str, Any],
        *,
        handler_values: Mapping[str, Any] | None,
    ) -> TaskConfiguration:
        structural = _TASK_STRUCTURAL_FIELDS
        if kind in _LOOP_CONDITION_TYPES:
            structural = structural - {"condition"}
        values = {
            key: value
            for key, value in payload.items()
            if key not in structural and not key.startswith("x-")
        }
        return cls(kind, values, handler_values=handler_values)

    def __setattr__(self, name: str, value: object) -> None:
        del name, value
        raise AttributeError("TaskConfiguration is immutable")

    @property
    def kind(self) -> str:
        return self._kind

    def mutable_copy(self) -> dict[str, Any]:
        """Return a detached top-level copy for renderers that must update values."""

        return _copy_configuration(self._values)

    def handler_view(self) -> TaskConfiguration:
        """Return the immutable payload accepted by existing built-in handlers."""

        return TaskConfiguration(self.kind, self._handler_values)

    def __getitem__(self, key: str) -> Any:
        return _copy_configuration_value(self._values[key])

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskConfiguration):
            return NotImplemented
        return self.kind == other.kind and self._values == other._values

    def __repr__(self) -> str:
        return f"TaskConfiguration(kind={self.kind!r}, values={dict(self)!r})"
