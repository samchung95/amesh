from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .descriptors import EditorMetadata as EditorMetadata
from .descriptors import ResourceKind as ResourceKind
from .descriptors import ResourceSchemaDescriptor as ResourceSchemaDescriptor

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
RESOURCE_CATALOG_VERSION = "amesh.resource-catalog/v1"


@dataclass(frozen=True)
class ResourceSchemaIssue:
    code: str
    message: str
    path: tuple[str | int, ...]
    hint: str


class ResourceSchemaRegistry:
    def __init__(self, descriptors: Iterable[ResourceSchemaDescriptor] = ()) -> None:
        self._descriptors: dict[tuple[ResourceKind, str], ResourceSchemaDescriptor] = {}
        self._validators: dict[tuple[ResourceKind, str], Draft202012Validator] = {}
        for descriptor in descriptors:
            self.register(descriptor)

    def register(self, descriptor: ResourceSchemaDescriptor) -> None:
        key = (descriptor.kind, descriptor.type)
        if not descriptor.type or descriptor.type.strip() != descriptor.type:
            raise ValueError("resource type must be a non-empty trimmed string")
        if key in self._descriptors:
            raise ValueError(
                f"resource schema already registered: {descriptor.kind}/{descriptor.type}"
            )
        schema = copy.deepcopy(dict(descriptor.configuration_schema))
        schema.setdefault("$schema", JSON_SCHEMA_DIALECT)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise ValueError(f"invalid schema for {descriptor.type!r}: {exc.message}") from exc
        stored = ResourceSchemaDescriptor(
            type=descriptor.type,
            kind=descriptor.kind,
            configuration_schema=schema,
            editor=descriptor.editor,
        )
        self._descriptors[key] = stored
        self._validators[key] = Draft202012Validator(schema)

    def descriptor(
        self,
        kind: ResourceKind,
        resource_type: str,
    ) -> ResourceSchemaDescriptor | None:
        return self._descriptors.get((kind, resource_type))

    def validate(
        self,
        kind: ResourceKind,
        resource_type: str,
        configuration: Mapping[str, Any],
    ) -> tuple[ResourceSchemaIssue, ...]:
        validator = self._validators.get((kind, resource_type))
        if validator is None:
            return (
                ResourceSchemaIssue(
                    code="unknown_resource_type",
                    message=f"no {kind.value} schema is registered for {resource_type!r}",
                    path=(),
                    hint="Install or register the resource plugin, or correct its type.",
                ),
            )
        errors = sorted(
            validator.iter_errors(dict(configuration)),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        return tuple(
            ResourceSchemaIssue(
                code="resource_schema_validation",
                message=error.message,
                path=tuple(error.absolute_path),
                hint=_schema_hint(error.validator),
            )
            for error in errors
        )

    def catalog(self) -> dict[str, Any]:
        resources = []
        for key in sorted(self._descriptors, key=lambda item: (item[0].value, item[1])):
            descriptor = self._descriptors[key]
            resources.append(
                {
                    "type": descriptor.type,
                    "kind": descriptor.kind.value,
                    "configurationSchema": copy.deepcopy(dict(descriptor.configuration_schema)),
                    "editor": descriptor.editor.as_dict(),
                }
            )
        return {"schemaVersion": RESOURCE_CATALOG_VERSION, "resources": resources}

    def copy(self) -> ResourceSchemaRegistry:
        return ResourceSchemaRegistry(self._descriptors.values())


def default_resource_registry() -> ResourceSchemaRegistry:
    from .specifications import all_descriptors

    return ResourceSchemaRegistry(all_descriptors())


def _schema_hint(validator: str) -> str:
    hints = {
        "additionalProperties": "Remove the unsupported field or use a documented x- extension.",
        "required": "Add the required resource property.",
        "type": "Use the property type declared by the resource schema.",
        "enum": "Use one of the values declared by the resource schema.",
        "anyOf": "Provide one of the supported resource configuration alternatives.",
    }
    return hints.get(validator, "Update the resource configuration to match its JSON Schema.")
