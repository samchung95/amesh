from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from amesh.domain.scripts import script_catalog_schema

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
    model_provider = {
        "type": "object",
        "properties": {
            "adapter": {"type": "string", "const": "openai-compatible"},
            "endpoint": {"type": "string", "format": "uri", "minLength": 1},
            "embeddingEndpoint": {"type": "string", "format": "uri", "minLength": 1},
            "credentialRef": {"type": "string", "minLength": 1},
        },
        "required": ["endpoint", "credentialRef"],
        "additionalProperties": False,
    }
    model_budget = {
        "type": "object",
        "properties": {
            "maxTotalTokens": {"type": "integer", "minimum": 1},
            "maxCompletionTokens": {"type": "integer", "minimum": 1},
            "maxCostUsd": {"type": ["number", "string"]},
        },
        "required": ["maxTotalTokens", "maxCostUsd"],
        "additionalProperties": False,
    }
    model_data_handling = {
        "type": "object",
        "properties": {
            "egress": {
                "type": "string",
                "enum": ["DENY_SECRETS", "REDACT_SECRETS", "ALLOW"],
            },
            "promptRetention": {
                "type": "string",
                "enum": ["REDACTED", "HASH_ONLY"],
            },
        },
        "required": ["egress", "promptRetention"],
        "additionalProperties": False,
    }
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
    agent_endpoint = {
        "type": "object",
        "properties": {
            "task": {"type": "string", "minLength": 1},
            "agent": {"type": "string", "minLength": 1},
            "agentRevision": {"type": "integer", "minimum": 1},
        },
        "required": ["task", "agent", "agentRevision"],
        "additionalProperties": False,
    }
    route_policy = {
        "type": "object",
        "properties": {
            "outcome": {"type": "string", "enum": ["ALLOW", "DENY"]},
            "decisionId": {"type": "string", "minLength": 1},
            "policyDigest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        },
        "required": ["outcome", "decisionId", "policyDigest"],
        "additionalProperties": False,
    }
    model_parameters = {
        "type": "object",
        "properties": {
            "temperature": {"type": "number", "minimum": 0, "maximum": 2},
            "topP": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
            "seed": {"type": "integer"},
        },
        "additionalProperties": False,
    }
    model_messages = {
        "type": "array",
        "minItems": 1,
        "items": {
            "type": "object",
            "properties": {
                "role": {"enum": ["system", "user", "assistant", "tool"]},
                "content": {"type": "string", "minLength": 1},
            },
            "required": ["role", "content"],
            "additionalProperties": False,
        },
    }
    bounded_model_properties = {
        "provider": model_provider,
        "model": {"type": "string", "minLength": 1},
        "budget": model_budget,
        "dataHandling": model_data_handling,
        "parameters": model_parameters,
        "timeoutSeconds": timeout,
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
    runner_properties = {
        "taskRunner": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "type": {"const": "local"},
                        "inheritHostEnvironment": {"type": "boolean"},
                        "allowedHostEnvironment": {
                            "type": "array",
                            "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "shell": {"type": "boolean"},
                    },
                    "required": ["type"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "type": {"const": "docker"},
                        "pullPolicy": {
                            "type": "string",
                            "enum": ["NEVER", "IF_NOT_PRESENT", "ALWAYS"],
                        },
                        "platform": {"type": "string", "minLength": 1},
                        "runtime": {"type": "string", "minLength": 1},
                        "registryUsernameVariable": {"type": "string", "minLength": 1},
                        "registryPasswordVariable": {"type": "string", "minLength": 1},
                    },
                    "required": ["type"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "type": {"const": "kubernetes"},
                        "serviceAccountName": {"type": "string", "minLength": 1},
                        "labels": string_map,
                        "nodeSelector": string_map,
                        "runtimeClassName": {"type": "string", "minLength": 1},
                    },
                    "required": ["type"],
                    "additionalProperties": False,
                },
            ]
        },
        "runnerCredentials": string_map,
        "networkPolicy": {
            "type": "object",
            "properties": {
                "access": {"type": "string", "enum": ["inherit", "none", "restricted"]},
                "allowedEgress": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
            },
            "additionalProperties": False,
        },
        "securityPolicy": {
            "type": "object",
            "properties": {
                "privileged": {"type": "boolean"},
                "readOnlyRootFilesystem": {"type": "boolean"},
                "runAsUser": {"type": "integer", "minimum": 0},
                "capabilityAdd": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
                "capabilityDrop": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
                "noNewPrivileges": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    }
    http_auth = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["bearer", "basic", "apiKey"]},
            "token": {"type": "string", "minLength": 1},
            "username": {"type": "string", "minLength": 1},
            "password": {"type": "string", "minLength": 1},
            "name": {"type": "string", "minLength": 1},
            "value": {"type": "string", "minLength": 1},
            "in": {"type": "string", "enum": ["header", "query"]},
        },
        "required": ["type"],
        "additionalProperties": False,
    }
    http_properties = {
        "url": {"type": "string", "minLength": 1},
        "method": {"type": "string", "minLength": 1},
        "headers": string_map,
        "query": string_map,
        "auth": http_auth,
        "body": {},
        "maxResponseBytes": {"type": "integer", "minimum": 1},
        "pagination": {
            "type": "object",
            "properties": {
                "nextUrlPath": {"type": "string", "minLength": 1},
                "itemsPath": {"type": "string", "minLength": 1},
                "maxPages": {"type": "integer", "minimum": 1},
            },
            "required": ["nextUrlPath"],
            "additionalProperties": False,
        },
        "timeoutSeconds": timeout,
    }
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
            _object_schema(http_properties, required=("url",)),
            title="HTTP request",
            description="Call a protected HTTP endpoint with auth, pagination and response limits.",
            category="Core",
            property_order=(
                "method",
                "url",
                "query",
                "headers",
                "auth",
                "body",
                "pagination",
                "maxResponseBytes",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "core.download",
            ResourceKind.TASK,
            _object_schema(
                {
                    **http_properties,
                    "destination": {"type": "string", "minLength": 1, "maxLength": 4096},
                    **workspace_properties,
                },
                required=("url", "destination"),
            ),
            title="HTTP download",
            description="Download a bounded response into the isolated task workspace.",
            category="Core",
            property_order=(
                "url",
                "destination",
                "headers",
                "auth",
                "maxResponseBytes",
                "outputFiles",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "core.document.extract",
            ResourceKind.TASK,
            _object_schema(
                {
                    "artifact": {
                        "type": "object",
                        "required": [
                            "schemaVersion",
                            "reference",
                            "contentAddress",
                            "tenantId",
                            "namespace",
                            "path",
                            "version",
                            "sizeBytes",
                            "checksumSha256",
                            "provenance",
                            "retention",
                        ],
                    },
                    "source": {"type": "string", "minLength": 1, "maxLength": 4096},
                    "limits": {
                        "type": "object",
                        "properties": {
                            "maxBytes": {"type": "integer", "minimum": 1, "maximum": 1073741824},
                            "maxPages": {"type": "integer", "minimum": 1, "maximum": 100000},
                            "maxTokens": {"type": "integer", "minimum": 1, "maximum": 10000000},
                            "chunkTokens": {"type": "integer", "minimum": 1, "maximum": 16384},
                            "chunkOverlapTokens": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 4096,
                            },
                            "wallTimeSeconds": {
                                "type": "number",
                                "exclusiveMinimum": 0,
                                "maximum": 3600,
                            },
                        },
                        "additionalProperties": False,
                    },
                    "inputFiles": input_files,
                    "outputFiles": output_files,
                    "workspaceQuotaBytes": {"type": "integer", "minimum": 1},
                },
                required=("artifact", "source", "limits", "inputFiles"),
            ),
            title="Extract PDF document",
            description=(
                "Extract bounded, page-aware text and chunks from a tenant-scoped PDF artifact."
            ),
            category="Documents",
            property_order=(
                "source",
                "artifact",
                "limits",
                "inputFiles",
                "outputFiles",
            ),
        ),
        _descriptor(
            "core.files.compress",
            ResourceKind.TASK,
            _object_schema(
                {
                    "sources": {
                        "type": "array",
                        "minItems": 1,
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1, "maxLength": 4096},
                    },
                    "destination": {"type": "string", "minLength": 1, "maxLength": 4096},
                    **workspace_properties,
                    "timeoutSeconds": timeout,
                },
                required=("sources", "destination"),
            ),
            title="Compress files",
            description="Create a ZIP archive from workspace files.",
            category="Files",
            property_order=("sources", "destination", "inputFiles", "outputFiles"),
        ),
        _descriptor(
            "core.files.extract",
            ResourceKind.TASK,
            _object_schema(
                {
                    "source": {"type": "string", "minLength": 1, "maxLength": 4096},
                    "destination": {"type": "string", "minLength": 1, "maxLength": 4096},
                    "maxEntries": {"type": "integer", "minimum": 1, "maximum": 10_000},
                    "maxUncompressedBytes": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 104_857_600,
                    },
                    **workspace_properties,
                    "timeoutSeconds": timeout,
                },
                required=("source", "destination"),
            ),
            title="Extract archive",
            description="Extract a bounded ZIP archive without path traversal or symlinks.",
            category="Files",
            property_order=(
                "source",
                "destination",
                "maxEntries",
                "maxUncompressedBytes",
                "inputFiles",
                "outputFiles",
            ),
        ),
        *(
            _descriptor(
                f"core.files.{operation}",
                ResourceKind.TASK,
                _object_schema(
                    {
                        "source": {"type": "string", "minLength": 1, "maxLength": 4096},
                        **(
                            {
                                "destination": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 4096,
                                }
                            }
                            if operation in {"copy", "move"}
                            else {}
                        ),
                        **(
                            {"algorithm": {"type": "string", "enum": ["sha256", "sha512"]}}
                            if operation == "checksum"
                            else {}
                        ),
                        **workspace_properties,
                        "timeoutSeconds": timeout,
                    },
                    required=(
                        ("source", "destination") if operation in {"copy", "move"} else ("source",)
                    ),
                ),
                title=title,
                description=description,
                category="Files",
                property_order=("source", "destination", "algorithm", "inputFiles", "outputFiles"),
            )
            for operation, title, description in (
                ("checksum", "Checksum file", "Compute a SHA-256 or SHA-512 workspace checksum."),
                ("copy", "Copy file", "Copy a file within the isolated workspace."),
                ("move", "Move file", "Move a file within the isolated workspace."),
                ("delete", "Delete file", "Delete a file within the isolated workspace."),
            )
        ),
        *(
            _descriptor(
                f"core.data.{format_name}",
                ResourceKind.TASK,
                _object_schema(
                    {
                        "operation": {
                            "type": "string",
                            "enum": (
                                ["trim", "upper", "lower", "replace", "split", "join"]
                                if format_name == "text"
                                else ["parse", "serialize"]
                            ),
                        },
                        "input": {},
                        "value": {},
                        "delimiter": {"type": "string", "minLength": 1, "maxLength": 1},
                        "search": {"type": "string"},
                        "replacement": {"type": "string"},
                        "separator": {"type": "string"},
                        "maxPayloadBytes": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10_485_760,
                        },
                        "timeoutSeconds": timeout,
                    },
                    any_of=({"required": ["input"]}, {"required": ["value"]}),
                ),
                title=f"{format_name.upper()} transform",
                description=f"Parse or deterministically transform {format_name.upper()} data.",
                category="Data",
                property_order=(
                    "operation",
                    "input",
                    "value",
                    "delimiter",
                    "search",
                    "replacement",
                    "separator",
                    "maxPayloadBytes",
                ),
            )
            for format_name in ("json", "yaml", "csv", "xml", "text")
        ),
        _descriptor(
            "core.sleep",
            ResourceKind.TASK,
            _object_schema(
                {"seconds": {"type": "number", "minimum": 0, "maximum": 86_400}},
                required=("seconds",),
            ),
            title="Sleep",
            description="Wait for a bounded duration while honoring cancellation.",
            category="Core",
            property_order=("seconds",),
        ),
        _descriptor(
            "core.approval",
            ResourceKind.TASK,
            _object_schema(
                {
                    "title": {"type": "string", "minLength": 1, "maxLength": 256},
                    "description": {"type": "string", "maxLength": 4096},
                    "form": {"type": "object"},
                    "assigneeIds": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "format": "uuid"},
                    },
                    "groupIds": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "format": "uuid"},
                    },
                    "deadlineAt": {"type": "string", "format": "date-time"},
                    "deadlineSeconds": {
                        "type": "number",
                        "exclusiveMinimum": 0,
                        "maximum": 31_536_000,
                    },
                    "escalationAssigneeIds": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "format": "uuid"},
                    },
                    "escalationGroupIds": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "format": "uuid"},
                    },
                },
                any_of=({"required": ["assigneeIds"]}, {"required": ["groupIds"]}),
            ),
            title="Human approval",
            description="Pause durably until an assigned participant records a decision.",
            category="Core",
            property_order=(
                "title",
                "description",
                "form",
                "assigneeIds",
                "groupIds",
                "deadlineAt",
                "deadlineSeconds",
                "escalationAssigneeIds",
                "escalationGroupIds",
            ),
        ),
        _descriptor(
            "core.fail",
            ResourceKind.TASK,
            _object_schema({"message": {"type": "string", "minLength": 1}}),
            title="Fail",
            description="Fail the task with a workflow-authored message.",
            category="Core",
            property_order=("message",),
        ),
        _descriptor(
            "core.debug",
            ResourceKind.TASK,
            _object_schema(
                {
                    "include": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {
                            "type": "string",
                            "enum": [
                                "inputs",
                                "outputs",
                                "variables",
                                "labels",
                                "trigger",
                                "iteration",
                                "files",
                            ],
                        },
                    }
                }
            ),
            title="Debug context",
            description="Return selected non-secret execution context sections.",
            category="Core",
            property_order=("include",),
        ),
        _descriptor(
            "core.assert",
            ResourceKind.TASK,
            _object_schema(
                {"value": {}, "message": {"type": "string", "minLength": 1}},
                required=("value",),
            ),
            title="Assert",
            description="Fail unless a rendered boolean value is true.",
            category="Core",
            property_order=("value", "message"),
        ),
        _descriptor(
            "core.notify.webhook",
            ResourceKind.TASK,
            _object_schema(http_properties, required=("url",)),
            title="Webhook notification",
            description="Deliver a protected generic webhook notification.",
            category="Notifications",
            property_order=("method", "url", "headers", "auth", "body", "maxResponseBytes"),
        ),
        _descriptor(
            "core.notify.email",
            ResourceKind.TASK,
            _object_schema(
                {
                    "smtpHost": {"type": "string", "minLength": 1},
                    "smtpPort": {"type": "integer", "minimum": 1, "maximum": 65_535},
                    "startTls": {"type": "boolean"},
                    "auth": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "minLength": 1},
                            "password": {"type": "string", "minLength": 1},
                        },
                        "required": ["username", "password"],
                        "additionalProperties": False,
                    },
                    "sender": {"type": "string", "minLength": 3},
                    "recipients": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 3},
                    },
                    "subject": {"type": "string", "minLength": 1},
                    "text": {"type": "string", "minLength": 1, "maxLength": 1_048_576},
                    "timeoutSeconds": timeout,
                },
                required=("smtpHost", "sender", "recipients", "subject", "text"),
            ),
            title="Email notification",
            description="Deliver a bounded text email through an SMTP relay.",
            category="Notifications",
            property_order=(
                "smtpHost",
                "smtpPort",
                "startTls",
                "auth",
                "sender",
                "recipients",
                "subject",
                "text",
            ),
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
                    "stdin": {"type": "string"},
                    "environment": string_map,
                    "resources": {"type": "object"},
                    "timeoutSeconds": timeout,
                    **workspace_properties,
                    **runner_properties,
                },
                required=("command",),
            ),
            title="Shell command",
            description="Run a command through the selected task runner.",
            category="Core",
            property_order=(
                "image",
                "command",
                "stdin",
                "environment",
                "inputFiles",
                "outputFiles",
                "outputManifest",
                "workspaceQuotaBytes",
                "retainDiagnosticsOnFailure",
                "taskRunner",
                "runnerCredentials",
                "networkPolicy",
                "securityPolicy",
                "resources",
                "timeoutSeconds",
            ),
        ),
        *(
            _descriptor(
                f"script.{language}",
                ResourceKind.TASK,
                _object_schema(
                    {
                        **script_catalog_schema(),
                        "image": {"type": "string", "minLength": 1},
                        "environment": string_map,
                        "resources": {"type": "object"},
                        "timeoutSeconds": timeout,
                        **workspace_properties,
                        **runner_properties,
                    },
                    required=("source",),
                ),
                title=f"{title} script",
                description=f"Run a {title} script through the selected task runner.",
                category="Scripts",
                property_order=(
                    "source",
                    "args",
                    "interpreter",
                    "dependencies",
                    "dependencyCommand",
                    "image",
                    "environment",
                    "inputFiles",
                    "outputFiles",
                    "outputManifest",
                    "workspaceQuotaBytes",
                    "retainDiagnosticsOnFailure",
                    "taskRunner",
                    "runnerCredentials",
                    "networkPolicy",
                    "securityPolicy",
                    "resources",
                    "timeoutSeconds",
                ),
            )
            for language, title in (
                ("shell", "Shell"),
                ("python", "Python"),
                ("node", "Node.js"),
                ("java", "Java"),
                ("r", "R"),
                ("powershell", "PowerShell"),
            )
        ),
        _descriptor(
            "core.workingDirectory",
            ResourceKind.TASK,
            _object_schema(
                {
                    **workspace_properties,
                    "failurePolicy": {
                        "type": "string",
                        "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                    },
                    "maxConcurrency": {"type": "integer", "const": 1},
                    "timeoutSeconds": timeout,
                }
            ),
            title="Shared working directory",
            description="Run child tasks sequentially in one bounded execution workspace.",
            category="Flow control",
            property_order=(
                "inputFiles",
                "outputFiles",
                "outputManifest",
                "workspaceQuotaBytes",
                "retainDiagnosticsOnFailure",
                "failurePolicy",
                "maxConcurrency",
                "timeoutSeconds",
            ),
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
            "core.if",
            ResourceKind.TASK,
            _object_schema(
                {
                    "failurePolicy": {
                        "type": "string",
                        "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                    },
                    "maxConcurrency": {"type": "integer", "minimum": 1, "maximum": 10_000},
                    "timeoutSeconds": timeout,
                }
            ),
            title="If",
            description="Select the first matching boolean branch.",
            category="Flow control",
            property_order=("failurePolicy", "maxConcurrency", "timeoutSeconds"),
        ),
        _descriptor(
            "core.switch",
            ResourceKind.TASK,
            _object_schema(
                {
                    "value": {},
                    "failurePolicy": {
                        "type": "string",
                        "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                    },
                    "maxConcurrency": {"type": "integer", "minimum": 1, "maximum": 10_000},
                    "timeoutSeconds": timeout,
                },
                required=("value",),
            ),
            title="Switch",
            description="Select an exact, ordered predicate or default branch.",
            category="Flow control",
            property_order=("value", "failurePolicy", "maxConcurrency", "timeoutSeconds"),
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
            "agent.chat",
            ResourceKind.TASK,
            _object_schema(
                {
                    **bounded_model_properties,
                    "prompt": {"type": "string", "minLength": 1},
                    "messages": model_messages,
                },
                required=("provider", "model", "budget", "dataHandling"),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
            ),
            title="Bounded chat",
            description="Call a provider-neutral chat model with explicit budgets and data policy.",
            category="Agents",
            property_order=(
                "provider",
                "model",
                "prompt",
                "messages",
                "parameters",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.embedding",
            ResourceKind.TASK,
            _object_schema(
                {
                    **bounded_model_properties,
                    "input": {
                        "oneOf": [
                            {"type": "string", "minLength": 1},
                            {
                                "type": "array",
                                "minItems": 1,
                                "items": {"type": "string", "minLength": 1},
                            },
                        ]
                    },
                },
                required=("provider", "model", "budget", "dataHandling", "input"),
            ),
            title="Bounded embedding",
            description="Create embeddings through a provider-neutral bounded model contract.",
            category="Agents",
            property_order=(
                "provider",
                "model",
                "input",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.structured",
            ResourceKind.TASK,
            _object_schema(
                {
                    **bounded_model_properties,
                    "prompt": {"type": "string", "minLength": 1},
                    "messages": model_messages,
                    "outputSchema": {"type": "object"},
                    "schemaName": {"type": "string", "minLength": 1},
                },
                required=(
                    "provider",
                    "model",
                    "budget",
                    "dataHandling",
                    "outputSchema",
                ),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
            ),
            title="Structured model output",
            description="Require Draft 2020-12 validated structured model output.",
            category="Agents",
            property_order=(
                "provider",
                "model",
                "prompt",
                "messages",
                "outputSchema",
                "schemaName",
                "parameters",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.toolCall",
            ResourceKind.TASK,
            _object_schema(
                {
                    **bounded_model_properties,
                    "prompt": {"type": "string", "minLength": 1},
                    "messages": model_messages,
                    "tools": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "minLength": 1},
                                "description": {"type": "string"},
                                "inputSchema": {"type": "object"},
                            },
                            "required": ["name", "inputSchema"],
                            "additionalProperties": False,
                        },
                    },
                    "toolChoice": {"type": "string", "minLength": 1},
                },
                required=("provider", "model", "budget", "dataHandling", "tools"),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
            ),
            title="Bounded tool proposal",
            description="Ask a model to propose schema-validated tool calls without executing them.",
            category="Agents",
            property_order=(
                "provider",
                "model",
                "prompt",
                "messages",
                "tools",
                "toolChoice",
                "parameters",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.mcp",
            ResourceKind.TASK,
            _object_schema(
                {
                    "endpoint": {"type": "string", "minLength": 1},
                    "connection": {"type": "string", "minLength": 1},
                    "revision": {"type": "integer", "minimum": 1},
                    "tool": {"type": "string", "minLength": 1},
                    "arguments": {"type": "object"},
                    "dataHandling": {
                        "type": "string",
                        "enum": ["DENY_SECRETS", "REDACT_SECRETS", "ALLOW"],
                    },
                    "allowWrite": {"type": "boolean"},
                    "approvalTask": {"type": "string", "minLength": 1},
                    "timeoutSeconds": timeout,
                },
                required=("tool",),
                any_of=({"required": ["endpoint"]}, {"required": ["connection"]}),
            ),
            title="MCP tool",
            description="Invoke a legacy endpoint or a governed, pinned MCP connection.",
            category="Agents",
            property_order=(
                "connection",
                "revision",
                "endpoint",
                "tool",
                "arguments",
                "dataHandling",
                "allowWrite",
                "approvalTask",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.mesh",
            ResourceKind.TASK,
            _object_schema(
                {
                    "topology": {
                        "type": "string",
                        "enum": [
                            "SUPERVISOR",
                            "ROUTER",
                            "PEER_TO_PEER",
                            "HIERARCHICAL",
                            "SWARM",
                        ],
                    },
                    "members": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 1_000,
                        "items": {
                            "type": "object",
                            "properties": {
                                "memberId": {"type": "string", "minLength": 1},
                                "task": {"type": "string", "minLength": 1},
                                "agent": {"type": "string", "minLength": 1},
                                "agentRevision": {"type": "integer", "minimum": 1},
                                "role": {
                                    "type": "string",
                                    "enum": ["SUPERVISOR", "ROUTER", "WORKER", "PEER"],
                                },
                                "capabilities": {
                                    "type": "array",
                                    "uniqueItems": True,
                                    "items": {"type": "string", "minLength": 1},
                                },
                                "parentMemberId": {"type": "string", "minLength": 1},
                            },
                            "required": [
                                "memberId",
                                "task",
                                "agent",
                                "agentRevision",
                                "role",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    "budget": {
                        **mesh_session_budget,
                        "properties": {
                            **mesh_session_budget["properties"],
                            "maxSessions": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1_000,
                            },
                            "maxConcurrency": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1_000,
                            },
                        },
                        "required": [
                            *mesh_session_budget["required"],
                            "maxSessions",
                            "maxConcurrency",
                        ],
                    },
                    "failurePolicy": {
                        "type": "string",
                        "enum": ["FAIL_FAST", "CONTINUE_ON_ERROR", "COLLECT_ALL"],
                    },
                    "maxConcurrency": {"type": "integer", "minimum": 1, "maximum": 1_000},
                    "timeoutSeconds": timeout,
                },
                required=("topology", "members", "budget", "maxConcurrency"),
            ),
            title="Agent mesh",
            description="Run a statically bounded multi-agent topology on the durable reducer.",
            category="Agents",
            property_order=(
                "topology",
                "members",
                "budget",
                "failurePolicy",
                "maxConcurrency",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.route",
            ResourceKind.TASK,
            _object_schema(
                {
                    "requiredCapabilities": {
                        "type": "array",
                        "minItems": 1,
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "candidates": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 1_000,
                        "items": {
                            "type": "object",
                            "properties": {
                                "memberId": {"type": "string", "minLength": 1},
                                "task": {"type": "string", "minLength": 1},
                                "agent": {"type": "string", "minLength": 1},
                                "agentRevision": {"type": "integer", "minimum": 1},
                                "capabilities": {
                                    "type": "array",
                                    "uniqueItems": True,
                                    "items": {"type": "string", "minLength": 1},
                                },
                                "policy": route_policy,
                                "projectedCostUsd": {"type": ["number", "string"]},
                                "projectedLatencyMs": {"type": "integer", "minimum": 0},
                                "availability": {
                                    "type": "object",
                                    "properties": {
                                        "available": {"type": "boolean"},
                                        "source": {"type": "string", "minLength": 1},
                                        "checkedAt": {
                                            "type": "string",
                                            "format": "date-time",
                                        },
                                    },
                                    "required": ["available", "source", "checkedAt"],
                                    "additionalProperties": False,
                                },
                                "evaluation": {
                                    "type": "object",
                                    "properties": {
                                        "key": {"type": "string", "minLength": 1},
                                        "revision": {"type": "integer", "minimum": 1},
                                        "score": {"type": ["number", "string"]},
                                    },
                                    "required": ["key", "revision", "score"],
                                    "additionalProperties": False,
                                },
                            },
                            "required": [
                                "memberId",
                                "task",
                                "agent",
                                "agentRevision",
                                "capabilities",
                                "policy",
                                "projectedCostUsd",
                                "projectedLatencyMs",
                                "availability",
                                "evaluation",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    "timeoutSeconds": timeout,
                },
                required=("requiredCapabilities", "candidates"),
            ),
            title="Agent route",
            description="Choose an eligible mesh member using durable, explainable signals.",
            category="Agents",
            property_order=("requiredCapabilities", "candidates", "timeoutSeconds"),
        ),
        _descriptor(
            "agent.handoff",
            ResourceKind.TASK,
            _object_schema(
                {
                    "source": agent_endpoint,
                    "destination": agent_endpoint,
                    "payload": {"type": "object"},
                    "schema": {"type": "object"},
                    "rationale": {"type": "string", "minLength": 1, "maxLength": 4096},
                    "contextKeys": {
                        "type": "array",
                        "uniqueItems": True,
                        "maxItems": 100,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "redactKeys": {
                        "type": "array",
                        "uniqueItems": True,
                        "maxItems": 100,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "requiredCapabilities": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "policy": route_policy,
                    "timeoutSeconds": timeout,
                },
                required=(
                    "source",
                    "destination",
                    "payload",
                    "schema",
                    "rationale",
                    "policy",
                ),
            ),
            title="Typed agent hand-off",
            description="Validate, authorize and redact context before another agent sees it.",
            category="Agents",
            property_order=(
                "source",
                "destination",
                "payload",
                "schema",
                "rationale",
                "contextKeys",
                "redactKeys",
                "requiredCapabilities",
                "policy",
                "timeoutSeconds",
            ),
        ),
        _descriptor(
            "agent.session",
            ResourceKind.TASK,
            _object_schema(
                {
                    "agent": {"type": "string", "minLength": 1},
                    "agentRevision": {"type": "integer", "minimum": 1},
                    "input": {"type": "object"},
                    "invalidOutputPolicy": {
                        "type": "string",
                        "enum": ["FAIL", "REPAIR"],
                    },
                    "maxRepairAttempts": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 20,
                    },
                    "approvalTask": {"type": "string", "minLength": 1},
                    "dataHandling": {
                        "type": "string",
                        "enum": ["DENY_SECRETS", "REDACT_SECRETS", "ALLOW"],
                    },
                    "businessAssertions": {
                        "type": "array",
                        "maxItems": 100,
                        "items": {"type": "object"},
                    },
                    "memoryReadKeys": {
                        "type": "array",
                        "maxItems": 100,
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "memoryWriteKey": {"type": "string", "minLength": 1},
                    "meshId": {"type": "string", "minLength": 1},
                    "memberId": {"type": "string", "minLength": 1},
                    "meshBudget": mesh_session_budget,
                    "contextPolicy": _object_schema(
                        {
                            "maxMessages": {
                                "type": "integer",
                                "minimum": 3,
                                "maximum": 10_000,
                            },
                            "maxBytes": {
                                "type": "integer",
                                "minimum": 256,
                                "maximum": 100_000_000,
                            },
                            "maxEstimatedTokens": {
                                "type": "integer",
                                "minimum": 64,
                                "maximum": 10_000_000,
                            },
                        }
                    ),
                    "timeoutSeconds": timeout,
                },
                required=("agent", "agentRevision", "input"),
            ),
            title="Bounded agent session",
            description=(
                "Run one durable, checkpointed agent against an exact capability envelope."
            ),
            category="Agents",
            property_order=(
                "agent",
                "agentRevision",
                "input",
                "invalidOutputPolicy",
                "maxRepairAttempts",
                "businessAssertions",
                "memoryReadKeys",
                "memoryWriteKey",
                "meshId",
                "memberId",
                "meshBudget",
                "contextPolicy",
                "approvalTask",
                "dataHandling",
                "timeoutSeconds",
            ),
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
            _object_schema(
                {
                    "maxPending": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "maxAttempts": {"type": "integer", "minimum": 1, "maximum": 100},
                    "retryDelay": {"type": "string", "format": "duration"},
                }
            ),
            title="Webhook",
            description="Start a flow from its authenticated webhook endpoint.",
            category="Core",
            property_order=("maxPending", "maxAttempts", "retryDelay"),
        ),
        _descriptor(
            "core.manual",
            ResourceKind.TRIGGER,
            _object_schema({}),
            title="Manual execution",
            description="Declare the built-in authorized API and UI manual execution entry point.",
            category="Core",
        ),
        _descriptor(
            "core.flow",
            ResourceKind.TRIGGER,
            _object_schema(
                {
                    "namespace": {"type": "string", "minLength": 1},
                    "flowId": {"type": "string", "minLength": 1},
                    "states": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["CANCELLED", "SUCCESS", "FAILED", "WARNING"],
                        },
                        "minItems": 1,
                        "uniqueItems": True,
                    },
                    "inputs": {"type": "object"},
                    "maxPending": {"type": "integer", "minimum": 1, "maximum": 100000},
                    "maxAttempts": {"type": "integer", "minimum": 1, "maximum": 100},
                    "retryDelay": {"type": "string", "format": "duration"},
                    "maxDepth": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                required=("flowId",),
            ),
            title="Flow completion",
            description="Start a flow from a matching terminal event emitted by another flow.",
            category="Core",
            property_order=(
                "namespace",
                "flowId",
                "states",
                "inputs",
                "maxPending",
                "maxAttempts",
                "retryDelay",
                "maxDepth",
            ),
        ),
        *(
            _descriptor(
                input_type,
                ResourceKind.INPUT,
                _object_schema(
                    {
                        "default": default_schema,
                        "displayName": {"type": "string", "maxLength": 256},
                        "placeholder": {"type": "string", "maxLength": 512},
                        "prefill": default_schema,
                        "validation": {"type": "object"},
                        "values": {"type": "array"},
                        "itemType": {"type": "string", "minLength": 1},
                        "schema": {"type": "object"},
                        "maxBytes": {"type": "integer", "minimum": 1},
                    }
                ),
                title=f"{input_type.title()} input",
                description=f"Declare a {input_type} flow input.",
                category="Inputs",
                property_order=(
                    "displayName",
                    "default",
                    "prefill",
                    "placeholder",
                    "values",
                    "itemType",
                    "schema",
                    "validation",
                    "maxBytes",
                ),
            )
            for input_type, default_schema in (
                ("string", {"type": "string"}),
                ("STRING", {"type": "string"}),
                ("integer", {"type": "integer"}),
                ("INTEGER", {"type": "integer"}),
                ("number", {"type": "number"}),
                ("NUMBER", {"type": "number"}),
                ("boolean", {"type": "boolean"}),
                ("BOOLEAN", {"type": "boolean"}),
                ("datetime", {"type": "string", "format": "date-time"}),
                ("DATETIME", {"type": "string", "format": "date-time"}),
                ("duration", {"type": "string", "format": "duration"}),
                ("DURATION", {"type": "string", "format": "duration"}),
                ("enum", {}),
                ("ENUM", {}),
                ("object", {"type": "object"}),
                ("OBJECT", {"type": "object"}),
                ("array", {"type": "array"}),
                ("ARRAY", {"type": "array"}),
                ("file", {"type": "object"}),
                ("FILE", {"type": "object"}),
                ("secret", {"type": "string"}),
                ("SECRET", {"type": "string"}),
            )
        ),
    )
