from __future__ import annotations

from amesh.dsl.descriptors import ResourceKind

from .common import (
    TaskSpecification,
    _object_schema,
    _task,
    agent_endpoint,
    bounded_model_budget_requirement,
    bounded_model_properties,
    disabled_timeout_constraint,
    mesh_session_budget,
    model_messages,
    route_policy,
    timeout,
    timeout_mode,
)


def agent_task_specifications() -> tuple[TaskSpecification, ...]:
    return (
        _task(
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
        _task(
            "agent.chat",
            ResourceKind.TASK,
            _object_schema(
                {
                    **bounded_model_properties,
                    "prompt": {"type": "string", "minLength": 1},
                    "messages": model_messages,
                },
                required=("provider", "model", "dataHandling"),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
                all_of=(bounded_model_budget_requirement,),
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
                "ceilingMode",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _task(
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
                required=("provider", "model", "dataHandling", "input"),
                all_of=(bounded_model_budget_requirement,),
            ),
            title="Bounded embedding",
            description="Create embeddings through a provider-neutral bounded model contract.",
            category="Agents",
            property_order=(
                "provider",
                "model",
                "input",
                "ceilingMode",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _task(
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
                    "dataHandling",
                    "outputSchema",
                ),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
                all_of=(bounded_model_budget_requirement,),
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
                "ceilingMode",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _task(
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
                required=("provider", "model", "dataHandling", "tools"),
                any_of=({"required": ["prompt"]}, {"required": ["messages"]}),
                all_of=(bounded_model_budget_requirement,),
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
                "ceilingMode",
                "budget",
                "dataHandling",
                "timeoutSeconds",
            ),
        ),
        _task(
            "agent.mcp",
            ResourceKind.TASK,
            {
                **_object_schema(
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
                        "timeoutMode": timeout_mode,
                        "timeoutSeconds": timeout,
                    },
                    required=("tool",),
                    any_of=({"required": ["endpoint"]}, {"required": ["connection"]}),
                ),
                "allOf": [disabled_timeout_constraint],
            },
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
                "timeoutMode",
                "timeoutSeconds",
            ),
        ),
        _task(
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
        _task(
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
        _task(
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
        _task(
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
                        "anyOf": [
                            {"type": "integer", "minimum": 0, "maximum": 20},
                            {"type": "null"},
                        ],
                    },
                    "requiredToolPlan": _object_schema(
                        {
                            "schemaVersion": {
                                "type": "string",
                                "const": "amesh.agent-tool-plan/v1",
                            },
                            "steps": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": 100,
                                "items": _object_schema(
                                    {
                                        "stepId": {"type": "string", "minLength": 1},
                                        "toolName": {"type": "string", "minLength": 1},
                                        "arguments": {"type": "object"},
                                        "argumentBindings": {
                                            "type": "object",
                                            "maxProperties": 100,
                                            "additionalProperties": {"type": "string"},
                                        },
                                        "itemArgumentBindings": {
                                            "type": "object",
                                            "maxProperties": 100,
                                            "additionalProperties": {"type": "string"},
                                        },
                                        "forEach": {"type": "string"},
                                        "maxOccurrences": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 1000,
                                        },
                                    },
                                    required=("stepId", "toolName"),
                                ),
                            },
                            "maxOccurrences": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1000,
                            },
                        },
                        required=("steps",),
                    ),
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
                            "ceilingMode": {
                                "type": "string",
                                "enum": ["BOUNDED", "PROVIDER_BOUNDED"],
                            },
                            "maxMessages": {
                                "anyOf": [
                                    {"type": "integer", "minimum": 3, "maximum": 10_000},
                                    {"type": "null"},
                                ],
                            },
                            "maxBytes": {
                                "anyOf": [
                                    {
                                        "type": "integer",
                                        "minimum": 256,
                                        "maximum": 100_000_000,
                                    },
                                    {"type": "null"},
                                ],
                            },
                            "maxEstimatedTokens": {
                                "anyOf": [
                                    {
                                        "type": "integer",
                                        "minimum": 64,
                                        "maximum": 10_000_000,
                                    },
                                    {"type": "null"},
                                ],
                            },
                            "contextWindowTokens": {
                                "type": "integer",
                                "minimum": 65,
                                "maximum": 10_000_000,
                            },
                            "reservedCompletionTokens": {
                                "anyOf": [
                                    {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 1_000_000,
                                    },
                                    {"type": "null"},
                                ],
                            },
                        }
                    ),
                    "timeoutMode": timeout_mode,
                    "timeoutSeconds": timeout,
                },
                required=("agent", "agentRevision", "input"),
            )
            | {"allOf": [disabled_timeout_constraint]},
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
                "requiredToolPlan",
                "businessAssertions",
                "memoryReadKeys",
                "memoryWriteKey",
                "meshId",
                "memberId",
                "meshBudget",
                "contextPolicy",
                "approvalTask",
                "dataHandling",
                "timeoutMode",
                "timeoutSeconds",
            ),
        ),
    )
