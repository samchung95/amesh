"""Immutable resource descriptors shared by registry and feature specifications."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from jsonschema import Draft202012Validator


class ResourceKind(StrEnum):
    TASK = "task"
    TRIGGER = "trigger"
    INPUT = "input"


class TaskRuntimeOwnership(StrEnum):
    """The single runtime boundary responsible for executing a built-in task kind."""

    HANDLER = "handler"
    EXECUTOR = "executor"
    FLOWABLE = "flowable"


@dataclass(frozen=True)
class HandlerConfigurationContract:
    """Independent configuration contract shared by a task handler and its catalog entry."""

    schema: Mapping[str, Any]
    validator: Callable[[Mapping[str, Any]], None] | None = field(
        default=None,
        compare=False,
        repr=False,
    )

    def model_json_schema(self) -> dict[str, Any]:
        return copy.deepcopy(dict(self.schema))

    def validate(self, configuration: Mapping[str, Any]) -> None:
        configuration = configuration_for_schema(self.schema, configuration)
        if self.validator is not None:
            self.validator(configuration)
            return
        errors = sorted(
            Draft202012Validator(self.model_json_schema()).iter_errors(dict(configuration)),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if errors:
            raise ValueError("; ".join(error.message for error in errors))

    def snapshot(self) -> HandlerConfigurationContract:
        return HandlerConfigurationContract(self.model_json_schema(), self.validator)


def configuration_for_schema(
    schema: Mapping[str, Any],
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Treat null properties absent from the resource schema as unset."""

    properties = schema.get("properties")
    declared = properties if isinstance(properties, Mapping) else {}
    return {
        key: value for key, value in configuration.items() if value is not None or key in declared
    }


@dataclass(frozen=True)
class EditorMetadata:
    title: str
    description: str
    category: str
    property_order: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "propertyOrder": list(self.property_order),
        }


@dataclass(frozen=True)
class ResourceSchemaDescriptor:
    type: str
    kind: ResourceKind
    configuration_schema: Mapping[str, Any]
    editor: EditorMetadata


@dataclass(frozen=True)
class TaskSpecification:
    """Frozen descriptor for an executable task kind and its handler identity."""

    type: str
    kind: ResourceKind
    configuration_contract: HandlerConfigurationContract
    editor: EditorMetadata
    handler_name: str = ""
    runtime_ownership: TaskRuntimeOwnership = TaskRuntimeOwnership.HANDLER

    def __post_init__(self) -> None:
        if self.kind is not ResourceKind.TASK:
            raise ValueError("task specifications must use the task resource kind")
        if self.runtime_ownership is not TaskRuntimeOwnership.FLOWABLE and not self.handler_name:
            raise ValueError("executable task specifications require a handler name")
        if self.runtime_ownership is TaskRuntimeOwnership.FLOWABLE and self.handler_name:
            raise ValueError("flowable task specifications cannot declare a handler name")

    @property
    def configuration_schema(self) -> Mapping[str, Any]:
        return self.configuration_contract.model_json_schema()

    @property
    def descriptor(self) -> ResourceSchemaDescriptor:
        return ResourceSchemaDescriptor(
            type=self.type,
            kind=self.kind,
            configuration_schema=self.configuration_schema,
            editor=self.editor,
        )
