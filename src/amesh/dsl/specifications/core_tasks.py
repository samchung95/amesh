from __future__ import annotations

from amesh.domain.scripts import script_catalog_schema
from amesh.dsl.descriptors import ResourceKind

from .common import (
    TaskSpecification,
    _object_schema,
    _task,
    http_properties,
    input_files,
    output_files,
    runner_properties,
    string_map,
    timeout,
    workspace_properties,
)


def core_task_specifications() -> tuple[TaskSpecification, ...]:
    return (
        _task(
            "core.return",
            ResourceKind.TASK,
            _object_schema({"value": {}, "timeoutSeconds": timeout}),
            title="Return value",
            description="Return a value as task output.",
            category="Core",
            property_order=("value",),
        ),
        _task(
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
        _task(
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
        _task(
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
        _task(
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
        _task(
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
        _task(
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
            _task(
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
            _task(
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
        _task(
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
        _task(
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
        _task(
            "core.fail",
            ResourceKind.TASK,
            _object_schema({"message": {"type": "string", "minLength": 1}}),
            title="Fail",
            description="Fail the task with a workflow-authored message.",
            category="Core",
            property_order=("message",),
        ),
        _task(
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
        _task(
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
        _task(
            "core.notify.webhook",
            ResourceKind.TASK,
            _object_schema(http_properties, required=("url",)),
            title="Webhook notification",
            description="Deliver a protected generic webhook notification.",
            category="Notifications",
            property_order=("method", "url", "headers", "auth", "body", "maxResponseBytes"),
        ),
        _task(
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
        _task(
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
            _task(
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
        _task(
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
        _task(
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
            _task(
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
        _task(
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
        _task(
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
        _task(
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
            _task(
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
    )
