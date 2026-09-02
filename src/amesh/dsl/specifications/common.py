from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from amesh.dsl.registry import EditorMetadata, ResourceKind, ResourceSchemaDescriptor


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
    schema: Mapping[str, Any],
    *,
    title: str,
    description: str,
    category: str,
    property_order: tuple[str, ...] = (),
) -> TaskSpecification:
    return TaskSpecification(
        type=resource_type,
        kind=kind,
        configuration_schema=schema,
        editor=EditorMetadata(
            title=title,
            description=description,
            category=category,
            property_order=property_order,
        ),
        handler_name=resource_type,
    )


timeout = {"type": "number", "exclusiveMinimum": 0}
timeout_mode = {"type": "string", "enum": ["BOUNDED", "DISABLED"]}
disabled_timeout_constraint = {
    "if": {
        "properties": {"timeoutMode": {"const": "DISABLED"}},
        "required": ["timeoutMode"],
    },
    "then": {"not": {"required": ["timeoutSeconds"]}},
}
string_map = {"type": "object", "additionalProperties": {"type": "string"}}
model_provider = {
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "adapter": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9.-]*$",
                },
                "endpoint": {"type": "string", "format": "uri", "minLength": 1},
                "embeddingEndpoint": {
                    "type": "string",
                    "format": "uri",
                    "minLength": 1,
                },
                "credentialRef": {"type": "string", "minLength": 1},
            },
            "required": ["endpoint", "credentialRef"],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "adapter": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9.-]*$",
                },
                "engineRef": {"type": "string", "minLength": 1},
            },
            "required": ["adapter", "engineRef"],
            "additionalProperties": False,
        },
    ],
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
        "providerOptions": {
            "type": "object",
            "maxProperties": 16,
            "propertyNames": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
            },
        },
        "requestOptions": {
            "type": "object",
            "maxProperties": 16,
            "propertyNames": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "not": {
                    "enum": [
                        "model",
                        "messages",
                        "input",
                        "response_format",
                        "tools",
                        "tool_choice",
                        "max_completion_tokens",
                        "max_tokens",
                        "max_output_tokens",
                        "provider",
                        "seed",
                        "stream",
                        "stream_options",
                        "temperature",
                        "top_p",
                    ]
                },
            },
        },
    },
    "additionalProperties": False,
}
model_messages = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "object",
        "properties": {
            "role": {"enum": ["system", "developer", "user", "assistant", "tool"]},
            "content": {
                "oneOf": [
                    {"type": "string", "minLength": 1, "maxLength": 1_000_000},
                    {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 100,
                        "items": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "text"},
                                        "text": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 1_000_000,
                                        },
                                    },
                                    "required": ["text"],
                                    "additionalProperties": False,
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "image_ref"},
                                        "image": {
                                            "type": "object",
                                            "required": ["artifact", "display"],
                                            "properties": {
                                                "schemaVersion": {"const": "amesh.image-ref/v1"},
                                                "artifact": {"type": "object"},
                                                "display": {"type": "object"},
                                            },
                                            "additionalProperties": False,
                                        },
                                    },
                                    "required": ["image"],
                                    "additionalProperties": False,
                                },
                            ]
                        },
                    },
                ]
            },
        },
        "required": ["role", "content"],
        "additionalProperties": False,
    },
}
bounded_model_properties = {
    "provider": model_provider,
    "model": {"type": "string", "minLength": 1},
    "ceilingMode": {
        "type": "string",
        "enum": ["BOUNDED", "PROVIDER_BOUNDED"],
    },
    "budget": model_budget,
    "dataHandling": model_data_handling,
    "parameters": model_parameters,
    "timeoutSeconds": timeout,
}
bounded_model_budget_requirement = {
    "anyOf": [
        {"required": ["budget"]},
        {
            "properties": {"ceilingMode": {"const": "PROVIDER_BOUNDED"}},
            "required": ["ceilingMode"],
        },
    ]
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
