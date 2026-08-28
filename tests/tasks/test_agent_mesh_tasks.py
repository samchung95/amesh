import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from amesh.domain import (
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceKind,
    AgentResourceRef,
    AgentResourceRevision,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext
from amesh.tasks import agent_mesh_handlers


class DestinationResources:
    def __init__(self) -> None:
        definition = AgentDefinitionSpec(
            key="supervisor",
            namespace="agents.demo",
            title="Supervisor",
            instructions="Review validated findings.",
            inputSchema={"type": "object"},
            outputSchema={"type": "object"},
            modelPolicy=AgentResourceRef(key="luna", revision=1),
            memoryPolicy=AgentMemoryPolicy(),
            permissions=AgentPermissions(delegatedCapabilities=("incident-response",)),
            hardLimits=AgentHardLimits(
                maxTotalTokens=1_000,
                maxCostUsd=Decimal("1"),
                maxDurationSeconds=60,
                maxToolCalls=0,
                maxTurns=2,
                maxLoopIterations=1,
                maxRecursionDepth=0,
                maxConcurrency=1,
            ),
            evaluationPolicy=AgentEvaluationPolicy(),
        )
        self.revision = AgentResourceRevision(
            tenantId="default",
            namespace="agents.demo",
            kind=AgentResourceKind.AGENT,
            key="supervisor",
            revision=4,
            digest="sha256:" + "d" * 64,
            spec=definition,
            createdBy="tester",
            createdAt=datetime.now(UTC),
        )

    async def get_resource(self, *args: Any, **kwargs: Any) -> AgentResourceRevision:
        assert args[:4] == ("default", "agents.demo", "AGENT", "supervisor")
        assert kwargs == {"revision": 4}
        return self.revision

    async def save_resource(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def list_resources(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def resolve_agent(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def preview_agent(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


def _context(*, outputs: dict[str, dict[str, Any]] | None = None) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        namespace="agents.demo",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs=outputs or {},
        variables={},
        secrets={"provider": "secret-value"},
    )


def test_route_handler_returns_durable_explainable_evidence() -> None:
    async def scenario() -> None:
        handler = agent_mesh_handlers(DestinationResources())["agent.route"]
        task = TaskDefinition.model_validate(
            {
                "id": "route",
                "type": "agent.route",
                "requiredCapabilities": ["incident-response"],
                "candidates": [
                    {
                        "memberId": "supervisor",
                        "task": "supervisor-session",
                        "agent": "supervisor",
                        "agentRevision": 4,
                        "capabilities": ["incident-response"],
                        "policy": {
                            "outcome": "ALLOW",
                            "decisionId": "route-policy-1",
                            "policyDigest": "sha256:" + "a" * 64,
                        },
                        "projectedCostUsd": "0.10",
                        "projectedLatencyMs": 500,
                        "availability": {
                            "available": True,
                            "source": "worker-heartbeat",
                            "checkedAt": "2026-08-25T00:00:00Z",
                        },
                        "evaluation": {"key": "quality", "revision": 3, "score": "0.9"},
                    }
                ],
            }
        )

        completion = await handler(task, _context())

        assert isinstance(completion, TaskCompletion)
        assert completion.output["agentRoute"]["selectedMemberId"] == "supervisor"
        assert completion.output["agentRoute"]["decisionDigest"].startswith("sha256:")

    asyncio.run(scenario())


def test_handoff_handler_uses_exact_source_and_redacts_before_persisting() -> None:
    async def scenario() -> None:
        handler = agent_mesh_handlers(DestinationResources())["agent.handoff"]
        task = TaskDefinition.model_validate(
            {
                "id": "handoff",
                "type": "agent.handoff",
                "dependsOn": ["analyst-session"],
                "source": {
                    "task": "analyst-session",
                    "agent": "analyst",
                    "agentRevision": 2,
                },
                "destination": {
                    "task": "supervisor-session",
                    "agent": "supervisor",
                    "agentRevision": 4,
                },
                "payload": {"finding": "credential=secret-value", "private": "omit"},
                "schema": {
                    "type": "object",
                    "required": ["finding"],
                    "properties": {"finding": {"type": "string"}},
                },
                "rationale": "Escalate a validated finding.",
                "contextKeys": ["finding"],
                "requiredCapabilities": ["incident-response"],
                "policy": {
                    "outcome": "ALLOW",
                    "decisionId": "handoff-policy-1",
                    "policyDigest": "sha256:" + "b" * 64,
                },
            }
        )
        context = _context(
            outputs={"analyst-session": {"session": {"agentKey": "analyst", "agentRevision": 2}}}
        )

        completion = await handler(task, context)

        assert isinstance(completion, TaskCompletion)
        assert completion.output["payload"] == {"finding": "credential=[REDACTED]"}
        assert "secret-value" not in repr(completion)
        assert completion.output["agentHandoff"]["source"]["task"] == "analyst-session"
        assert completion.output["agentHandoff"]["destination"]["task"] == ("supervisor-session")

    asyncio.run(scenario())
