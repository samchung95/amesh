from __future__ import annotations

from amesh.dsl.registry import ResourceKind, ResourceSchemaDescriptor

from .common import _descriptor, _object_schema


def resource_specifications() -> tuple[ResourceSchemaDescriptor, ...]:
    return (
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
                ("image", {"type": "object"}),
                ("IMAGE", {"type": "object"}),
                ("secret", {"type": "string"}),
                ("SECRET", {"type": "string"}),
            )
        ),
    )
