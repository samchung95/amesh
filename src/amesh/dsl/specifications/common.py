from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from amesh.dsl.descriptors import (
    EditorMetadata,
    ResourceKind,
    ResourceSchemaDescriptor,
)
from amesh.dsl.descriptors import TaskRuntimeOwnership as TaskRuntimeOwnership
from amesh.dsl.descriptors import TaskSpecification as TaskSpecification
from amesh.dsl.handler_contracts import bind_builtin_handler_contract


def _object_schema(
    properties: Mapping[str, Any],
    *,
    required: tuple[str, ...] = (),
    any_of: tuple[Mapping[str, Any], ...] = (),
    all_of: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": dict(properties),
        "additionalProperties": False,
    }
    if required:
        schema["required"] = list(required)
    if any_of:
        schema["anyOf"] = [dict(item) for item in any_of]
    if all_of:
        schema["allOf"] = [dict(item) for item in all_of]
    return schema


def _descriptor(
    resource_type: str,
    kind: ResourceKind,
    schema: Mapping[str, Any],
    *,
    title: str,
    description: str,
    category: str,
    property_order: tuple[str, ...] = (),
) -> ResourceSchemaDescriptor:
    return ResourceSchemaDescriptor(
        type=resource_type,
        kind=kind,
        configuration_schema=schema,
        editor=EditorMetadata(
            title=title,
            description=description,
            category=category,
            property_order=property_order,
        ),
    )


def _task(
    resource_type: str,
    kind: ResourceKind,
    schema: Mapping[str, Any] | None = None,
    *,
    title: str,
    description: str,
    category: str,
    property_order: tuple[str, ...] = (),
    runtime_ownership: TaskRuntimeOwnership = TaskRuntimeOwnership.HANDLER,
) -> TaskSpecification:
    configuration_contract = bind_builtin_handler_contract(resource_type, schema)
    return TaskSpecification(
        type=resource_type,
        kind=kind,
        configuration_contract=configuration_contract,
        editor=EditorMetadata(
            title=title,
            description=description,
            category=category,
            property_order=property_order,
        ),
        handler_name=(
            resource_type if runtime_ownership is not TaskRuntimeOwnership.FLOWABLE else ""
        ),
        runtime_ownership=runtime_ownership,
    )


timeout = {"type": "number", "exclusiveMinimum": 0}
mesh_session_budget: dict[str, Any] = {
    "type": "object",
    "properties": {
        "maxTotalTokens": {"type": "integer", "minimum": 1},
        "maxCostUsd": {"type": ["number", "string"]},
        "maxDurationSeconds": {"type": "integer", "minimum": 1, "maximum": 86_400},
        "maxToolCalls": {"type": "integer", "minimum": 0, "maximum": 10_000},
    },
    "required": [
        "maxTotalTokens",
        "maxCostUsd",
        "maxDurationSeconds",
        "maxToolCalls",
    ],
    "additionalProperties": False,
}
input_files = {"type": "object", "additionalProperties": {"type": "string"}}
output_files = {
    "type": "array",
    "uniqueItems": True,
    "items": {"type": "string", "minLength": 1, "maxLength": 4096},
}
workspace_properties = {
    "inputFiles": input_files,
    "outputFiles": output_files,
    "outputManifest": {"type": "string", "minLength": 1, "maxLength": 4096},
    "workspaceQuotaBytes": {"type": "integer", "minimum": 1},
    "retainDiagnosticsOnFailure": {"type": "boolean"},
}
