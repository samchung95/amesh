from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
RESOURCE_CATALOG_VERSION = "amesh.resource-catalog/v1"


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
    return ResourceSchemaRegistry(_core_descriptors())


def _schema_hint(validator: str) -> str:
    hints = {
        "additionalProperties": "Remove the unsupported field or use a documented x- extension.",
        "required": "Add the required resource property.",
        "type": "Use the property type declared by the resource schema.",
        "enum": "Use one of the values declared by the resource schema.",
        "anyOf": "Provide one of the supported resource configuration alternatives.",
    }
    return hints.get(validator, "Update the resource configuration to match its JSON Schema.")


def _object_schema(
    properties: Mapping[str, Any],
    *,
    required: tuple[str, ...] = (),
    any_of: tuple[Mapping[str, Any], ...] = (),
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "$schema": JSON_SCHEMA_DIALECT,
        "type": "object",
        "properties": dict(properties),
        "additionalProperties": False,
    }
    if required:
        schema["required"] = list(required)
    if any_of:
        schema["anyOf"] = [dict(item) for item in any_of]
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


def _core_descriptors() -> tuple[ResourceSchemaDescriptor, ...]:
    timeout = {"type": "number", "exclusiveMinimum": 0}
    string_map = {"type": "object", "additionalProperties": {"type": "string"}}
    return (
        _descriptor(
            "core.return",
            ResourceKind.TASK,
            _object_schema({"value": {}, "timeoutSeconds": timeout}),
            title="Return value",
            description="Return a value as task output.",
            category="Core",
            property_order=("value",),
        ),
        _descriptor(
            "core.log",
            ResourceKind.TASK,
            _object_schema(
                {"message": {"type": "string"}, "timeoutSeconds": timeout},
                required=("message",),
            ),
            title="Log message",
            description="Write a rendered message to the execution log.",
            category="Core",
            property_order=("message",),
        ),
        _descriptor(
            "core.http",
            ResourceKind.TASK,
            _object_schema(
                {
                    "url": {"type": "string", "minLength": 1},
                    "method": {"type": "string", "minLength": 1},
                    "headers": string_map,
                    "body": {},
                    "timeoutSeconds": timeout,
                },
                required=("url",),
            ),
            title="HTTP request",
            description="Call an HTTP endpoint and expose its response.",
            category="Core",
            property_order=("method", "url", "headers", "body", "timeoutSeconds"),
        ),
        _descriptor(
            "core.shell",
            ResourceKind.TASK,
            _object_schema(
                {
                    "command": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"},
                    },
                    "image": {"type": "string", "minLength": 1},
                    "environment": string_map,
                    "resources": {"type": "object"},
                    "timeoutSeconds": timeout,
                },
                required=("command",),
            ),
            title="Shell command",
            description="Run a command through the selected task runner.",
            category="Core",
            property_order=("image", "command", "environment", "resources", "timeoutSeconds"),
        ),
        _descriptor(
            "core.subflow",
            ResourceKind.TASK,
            _object_schema(
                {
                    "namespace": {"type": "string", "minLength": 1},
                    "flowId": {"type": "string", "minLength": 1},
                    "revision": {"type": "integer", "minimum": 1},
                    "mode": {"type": "string", "enum": ["SYNC", "ASYNC", "DETACHED"]},
                    "inputs": {"type": "object"},
                    "labels": {"type": "object", "additionalProperties": {"type": "string"}},
                    "propagation": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "failure": {"type": "boolean"},
                            "cancellation": {"type": "boolean"},
                            "pause": {"type": "boolean"},
                            "restart": {"type": "boolean"},
                        },
                        "additionalProperties": False,
                    },
                    "outputMapping": {
                        "type": "object",
                        "additionalProperties": {"type": "string", "minLength": 1},
                    },
                    "outputSchema": {"type": "object"},
                    "artifactMapping": {
                        "type": "object",
                        "additionalProperties": {"type": "string", "minLength": 1},
                    },
                    "artifactSchema": {"type": "object"},
                    "maxDepth": {"type": "integer", "minimum": 1, "maximum": 100},
                    "timeoutSeconds": timeout,
                },
                required=("flowId",),
            ),
            title="Invoke subflow",
            description="Launch a revision-pinned child flow with durable parent-child lineage.",
            category="Core",
            property_order=(
                "namespace",
                "flowId",
                "revision",
                "mode",
                "inputs",
                "labels",
                "propagation",
                "outputMapping",
                "outputSchema",
                "artifactMapping",
                "artifactSchema",
                "maxDepth",
            ),
        ),
        *(
            _descriptor(
                resource_type,
                ResourceKind.TASK,
                _object_schema(
                    {
                        "failurePolicy": {
                            "type": "string",
                            "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                        },
                        "maxConcurrency": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10_000,
                        },
                        "timeoutSeconds": timeout,
                    }
                ),
                title=title,
                description=description,
                category="Flow control",
                property_order=("failurePolicy", "maxConcurrency", "timeoutSeconds"),
            )
            for resource_type, title, description in (
                (
                    "core.sequential",
                    "Sequential",
                    "Execute child tasks in declared order.",
                ),
                (
                    "core.parallel",
                    "Parallel",
                    "Execute independent child tasks with bounded concurrency.",
                ),
                (
                    "core.dag",
                    "DAG",
                    "Execute child tasks from explicit dependency edges.",
                ),
            )
        ),
        _descriptor(
            "core.foreach",
            ResourceKind.TASK,
            _object_schema(
                {
                    "items": {"type": ["array", "object", "string"]},
                    "range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                            "step": {"type": "integer", "not": {"const": 0}},
                        },
                        "required": ["end"],
                        "additionalProperties": False,
                    },
                    "manifestUri": {"type": "string", "minLength": 1},
                    "batchSize": {"type": "integer", "minimum": 1},
                    "failurePolicy": {
                        "type": "string",
                        "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                    },
                    "maxConcurrency": {"type": "integer", "minimum": 1, "maximum": 10_000},
                    "maxIterations": {"type": "integer", "minimum": 1, "maximum": 1_000_000},
                    "maxDurationSeconds": {"type": "number", "exclusiveMinimum": 0},
                    "maxTaskRuns": {"type": "integer", "minimum": 1, "maximum": 1_000_000},
                    "inlinePayloadBytes": {"type": "integer", "minimum": 1},
                    "continueIf": {"type": "string", "minLength": 1},
                    "breakIf": {"type": "string", "minLength": 1},
                    "timeoutSeconds": timeout,
                },
                any_of=(
                    {"required": ["items"]},
                    {"required": ["range"]},
                    {"required": ["manifestUri"]},
                ),
            ),
            title="For each",
            description="Repeat child tasks over a bounded collection or item manifest.",
            category="Flow control",
            property_order=(
                "items",
                "range",
                "manifestUri",
                "batchSize",
                "maxConcurrency",
                "failurePolicy",
                "maxIterations",
                "maxDurationSeconds",
                "maxTaskRuns",
            ),
        ),
        *(
            _descriptor(
                resource_type,
                ResourceKind.TASK,
                _object_schema(
                    {
                        "condition": {"type": "string", "minLength": 1},
                        "failurePolicy": {
                            "type": "string",
                            "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                        },
                        "maxIterations": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1_000_000,
                        },
                        "maxDurationSeconds": {"type": "number", "exclusiveMinimum": 0},
                        "maxTaskRuns": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1_000_000,
                        },
                        "inlinePayloadBytes": {"type": "integer", "minimum": 1},
                        "continueIf": {"type": "string", "minLength": 1},
                        "breakIf": {"type": "string", "minLength": 1},
                        "timeoutSeconds": timeout,
                    },
                    required=("condition", "maxIterations"),
                ),
                title=title,
                description=description,
                category="Flow control",
                property_order=(
                    "condition",
                    "failurePolicy",
                    "maxIterations",
                    "maxDurationSeconds",
                    "maxTaskRuns",
                ),
            )
            for resource_type, title, description in (
                ("core.while", "While", "Repeat child tasks while a condition remains true."),
                ("core.until", "Until", "Repeat child tasks until a condition becomes true."),
            )
        ),
        _descriptor(
            "agent.llm",
            ResourceKind.TASK,
            _object_schema(
                {
                    "prompt": {"type": "string", "minLength": 1},
                    "messages": {"type": "array", "minItems": 1, "items": {"type": "object"}},
                    "model": {"type": "string", "minLength": 1},
                    "maxCompletionTokens": {"type": "integer", "minimum": 1},
                    "timeoutSeconds": timeout,
                },
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
            ),
            title="LLM completion",
            description="Call an OpenAI-compatible language model endpoint.",
            category="Agents",
            property_order=("model", "prompt", "messages", "maxCompletionTokens"),
        ),
        _descriptor(
            "agent.mcp",
            ResourceKind.TASK,
            _object_schema(
                {
                    "endpoint": {"type": "string", "minLength": 1},
                    "tool": {"type": "string", "minLength": 1},
                    "arguments": {"type": "object"},
                    "timeoutSeconds": timeout,
                },
                required=("endpoint", "tool"),
            ),
            title="MCP tool",
            description="Invoke a tool on a Model Context Protocol server.",
            category="Agents",
            property_order=("endpoint", "tool", "arguments", "timeoutSeconds"),
        ),
        _descriptor(
            "core.cron",
            ResourceKind.TRIGGER,
            _object_schema(
                {
                    "cron": {"type": "string", "minLength": 1},
                    "timezone": {"type": "string", "minLength": 1},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                    "paused": {"type": "boolean"},
                    "condition": {"type": "string"},
                    "misfirePolicy": {
                        "type": "string",
                        "enum": ["SKIP", "CATCH_UP", "COALESCE", "BACKFILL"],
                    },
                    "misfireGraceSeconds": {"type": "integer", "minimum": 0},
                    "maxCatchUp": {"type": "integer", "minimum": 1, "maximum": 10000},
                },
                required=("cron",),
            ),
            title="Cron schedule",
            description="Create occurrences on a cron schedule in an IANA timezone.",
            category="Core",
            property_order=(
                "cron",
                "timezone",
                "start",
                "end",
                "paused",
                "condition",
                "misfirePolicy",
                "misfireGraceSeconds",
                "maxCatchUp",
            ),
        ),
        _descriptor(
            "core.interval",
            ResourceKind.TRIGGER,
            _object_schema(
                {
                    "interval": {"type": "string", "format": "duration"},
                    "timezone": {"type": "string", "minLength": 1},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                    "paused": {"type": "boolean"},
                    "condition": {"type": "string"},
                    "misfirePolicy": {
                        "type": "string",
                        "enum": ["SKIP", "CATCH_UP", "COALESCE", "BACKFILL"],
                    },
                    "misfireGraceSeconds": {"type": "integer", "minimum": 0},
                    "maxCatchUp": {"type": "integer", "minimum": 1, "maximum": 10000},
                },
                required=("interval",),
            ),
            title="Interval schedule",
            description="Create occurrences at a fixed elapsed-time interval.",
            category="Core",
            property_order=(
                "interval",
                "timezone",
                "start",
                "end",
                "paused",
                "condition",
                "misfirePolicy",
                "misfireGraceSeconds",
                "maxCatchUp",
            ),
        ),
        _descriptor(
            "core.webhook",
            ResourceKind.TRIGGER,
            _object_schema({}),
            title="Webhook",
            description="Start a flow from its authenticated webhook endpoint.",
            category="Core",
        ),
        *(
            _descriptor(
                input_type,
                ResourceKind.INPUT,
                _object_schema({"default": default_schema}),
                title=f"{input_type.title()} input",
                description=f"Declare a {input_type} flow input.",
                category="Inputs",
                property_order=("default",),
            )
            for input_type, default_schema in (
                ("string", {"type": "string"}),
                ("STRING", {"type": "string"}),
                ("integer", {"type": "integer"}),
                ("number", {"type": "number"}),
                ("boolean", {"type": "boolean"}),
                ("object", {"type": "object"}),
                ("array", {"type": "array"}),
            )
        ),
    )
