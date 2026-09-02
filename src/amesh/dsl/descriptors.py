"""Immutable resource descriptors shared by registry and feature specifications."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ResourceKind(StrEnum):
    TASK = "task"
    TRIGGER = "trigger"
    INPUT = "input"


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
    configuration_schema: Mapping[str, Any]
    editor: EditorMetadata
    handler_name: str = ""

    @property
    def descriptor(self) -> ResourceSchemaDescriptor:
        return ResourceSchemaDescriptor(
            type=self.type,
            kind=self.kind,
            configuration_schema=self.configuration_schema,
            editor=self.editor,
        )
