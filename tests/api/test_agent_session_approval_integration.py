from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from mcp.server import MCPServer
from sqlalchemy.ext.asyncio import create_async_engine

from amesh import app as app_module
from amesh.adapters.agent_session_harness import PiAgentSessionHarness
from amesh.adapters.postgres import (
    PostgresAgentPrimitiveRepository,
    PostgresAgentProgressSink,
    PostgresAgentResourceRepository,
    PostgresAgentSessionPolicyRepository,
    PostgresAgentSessionRepository,
    PostgresExecutionRepository,
    PostgresHumanTaskRepository,
)
from amesh.api.models import ExecutionDetail
from amesh.application.execution_launch import ExecutionLaunchService
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceRef,
    AgentToolRef,
    AuthorizationDecision,
    AuthorizationRequest,
    McpConnectionSpec,
    McpToolImpact,
    ModelPolicySpec,
    ModelProviderSpec,
    ModelRoute,
    PrincipalType,
)
from amesh.executor import (
    InProcessExecutor,
    TaskContextRequest,
    TaskContextResources,
    TaskExecutionError,
)
from amesh.human_tasks import HumanTaskService, approval_task_handler
from amesh.ports import ModelProviderResponse
from amesh.tasks import (
    agent_llm_handler,
    agent_mcp_handler,
    agent_session_handler,
    discover_mcp_server,
)


class _FixtureProvider:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def invoke(self, request: Any, access: Any) -> ModelProviderResponse:
        self.requests.append(request)
        last = str(request.payload["messages"][-1]["content"])
        final = '"tool"' in last and '"result"' in last
        return ModelProviderResponse(
            payload={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "action": "final" if final else "tool",
                                    "tool": "write",
                                    "arguments": None
                                    if final
                                    else json.dumps({"value": "approved"}),
                                    "output": {"answer": "written"} if final else None,
                                    "rationale": "Fixture action",
                                }
                            )
                        }
                    }
                ],
                "usage": {"total_tokens": 5, "cost": 0.001},
            }
        )


class _FixtureContext:
    async def resolve(self, request: TaskContextRequest) -> TaskContextResources:
        return TaskContextResources(secrets={key: "fixture-only" for key in request.secret_scopes})


class _Authorization:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=request.action.value != "manage",
            reason_code="fixture",
            summary="Participant permissions without human-task administration",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        return await self.decide(request)


def test_public_canonical_approval_and_continuation_use_durable_authorities(
    migrated_test_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real API, launch service, PostgreSQL, Pi and MCP; model/credentials are fixtures."""

    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        resources = PostgresAgentResourceRepository(engine)
        invocations = PostgresAgentPrimitiveRepository(engine)
        sessions = PostgresAgentSessionRepository(engine)
        executions = PostgresExecutionRepository(engine)
        human_tasks = PostgresHumanTaskRepository(engine)
        provider = _FixtureProvider()
        actor = ActorContext(
            principal_id=uuid4(), principal_type=PrincipalType.USER, display="owner"
        )
        current_actor = actor
        server = MCPServer("approved-write")
        writes: list[str] = []

        @server.tool()
        def write(value: str) -> dict[str, str]:
            writes.append(value)
            return {"value": value}

        node = shutil.which("node")
        assert node is not None
        harness = PiAgentSessionHarness(
            (node, str(Path(__file__).resolve().parents[2] / "harnesses/pi/src/worker.mjs"))
        )
        progress = PostgresAgentProgressSink(sessions)
        pepper = "canonical-approval-fixture"

        def executor() -> InProcessExecutor:
            return InProcessExecutor(
                executions,
                context_provider=_FixtureContext(),
                handlers={
                    "core.approval": approval_task_handler(
                        human_tasks, executions, token_pepper=pepper
                    ),
                    "agent.session": agent_session_handler(
                        resources=resources,
                        sessions=sessions,
                        model_handler=agent_llm_handler(
                            provider=provider, repository=invocations, progress_sink=progress
                        ),
                        mcp_handler=agent_mcp_handler(lambda _: server, repository=invocations),
                        harness=harness,
                        progress_sink=progress,
                    ),
                },
            )

        async def close_runtime() -> None:
            pass

        async def launch(*args: Any, **kwargs: Any) -> ExecutionDetail:
            # Replace only environment composition with the provider-free runtime above.
            flow = args[2]
            result = await ExecutionLaunchService(
                executions,
                executor,
                schedule_background=kwargs["background_tasks"].add_task,
                close_runtime=close_runtime,
            ).launch(
                flow,
                tenant_id=kwargs["tenant_id"],
                actor_id=kwargs["actor_id"],
                inputs={},
                trigger=kwargs["trigger_context"],
                launch_source=kwargs["launch_source"],
                idempotency_key=kwargs["idempotency_key"],
            )
            return ExecutionDetail(execution=result.execution, taskRuns=list(result.task_runs))

        async def drive(execution_id: str) -> None:
            record = await executions.get_execution(UUID(execution_id), tenant_id="default")
            flow = await executions.get_flow(
                record.namespace, record.flow_id, tenant_id="default", revision=record.flow_revision
            )
            try:
                await executor().run_to_completion(flow, record.execution_id, tenant_id="default")
            except TaskExecutionError as exc:
                details = await sessions.list_execution_sessions("default", record.execution_id)
                raise TaskExecutionError(
                    str([(item.state, item.error) for item in details])
                ) from exc

        previous_overrides = dict(app_module.app.dependency_overrides)
        try:
            discovery = await discover_mcp_server(
                "in-process://write", "fixture-only", target_resolver=lambda _: server
            )
            tool = discovery.tools[0].model_copy(update={"impact": McpToolImpact.HIGH_IMPACT})
            connection = await invocations.save_mcp_connection(
                "default",
                McpConnectionSpec(
                    key="gateway",
                    namespace="tests.canonical",
                    endpoint="https://mcp.example.test/mcp",
                    credentialRef="mcp",
                    toolAllowlist=("write",),
                    tools=(tool,),
                ),
                actor_id="fixture",
            )
            policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="model",
                    namespace="tests.canonical",
                    title="Fixture model",
                    routes=(
                        ModelRoute(
                            routeId="primary",
                            model="openai/gpt-5.6-luna",
                            provider=ModelProviderSpec(
                                endpoint="https://openrouter.ai/api/v1/chat/completions",
                                credentialRef="model",
                            ),
                        ),
                    ),
                    outputNondeterminismDisclosure="Fixture provider; no external model call.",
                ),
                actor_id="fixture",
            )
            await resources.save_resource(
                "default",
                AgentDefinitionSpec(
                    key="helper",
                    namespace="tests.canonical",
                    title="Approved helper",
                    instructions="Write after approval and return a structured answer.",
                    inputSchema={"type": "object"},
                    outputSchema={
                        "type": "object",
                        "required": ["answer"],
                        "properties": {"answer": {"type": "string"}},
                        "additionalProperties": False,
                    },
                    modelPolicy=AgentResourceRef(key=policy.key, revision=policy.revision),
                    tools=(
                        AgentToolRef(
                            connectionKey="gateway",
                            connectionRevision=connection.revision,
                            toolName="write",
                            schemaDigest=tool.schema_digest,
                        ),
                    ),
                    memoryPolicy=AgentMemoryPolicy(),
                    evaluationPolicy=AgentEvaluationPolicy(),
                    permissions=AgentPermissions(
                        allowHighImpactTools=True,
                        toolAllowlist=("write",),
                        secretScopes=("model", "mcp"),
                        networkHosts=("openrouter.ai", "mcp.example.test"),
                    ),
                    hardLimits=AgentHardLimits(
                        maxTotalTokens=1000,
                        maxCostUsd="1",
                        maxDurationSeconds=120,
                        maxToolCalls=4,
                        maxTurns=8,
                        maxLoopIterations=8,
                        maxRecursionDepth=0,
                        maxConcurrency=1,
                    ),
                ),
                actor_id="fixture",
            )
            monkeypatch.setattr(app_module, "_execute_flow", launch)
            monkeypatch.setattr(
                app_module,
                "get_agent_session_policy_repository",
                lambda: PostgresAgentSessionPolicyRepository(engine),
            )
            app_module.app.dependency_overrides.update(
                {
                    app_module.authenticate_actor: lambda: current_actor,
                    app_module.require_tenant_context: lambda: "default",
                    app_module.get_authorization_service: _Authorization,
                    get_settings: lambda: Settings(_env_file=None),
                    app_module.get_repository: lambda: executions,
                    app_module.get_agent_resource_repository: lambda: resources,
                    app_module.get_agent_session_repository: lambda: sessions,
                    app_module.get_task_cache_repository: lambda: object(),
                    app_module.get_shared_resource_repository: lambda: object(),
                    app_module.get_operational_control_repository: lambda: object(),
                    app_module.get_human_task_repository: lambda: human_tasks,
                    app_module.get_human_task_service: lambda: HumanTaskService(
                        human_tasks, executions, token_pepper=pepper
                    ),
                    app_module.get_namespace_resource_service: lambda: object(),
                }
            )
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app_module.app), base_url="http://amesh.test"
            ) as client:
                request = {
                    "agentRef": "tests.canonical/helper@1",
                    "input": {"question": "Remember Cedar Finch"},
                    "approvalTask": "approve",
                    "idempotencyKey": "canonical-approved",
                }
                created = await client.post("/api/v1/agent-sessions", json=request)
                assert created.status_code == 200, created.text
                first = created.json()
                duplicate = await client.post("/api/v1/agent-sessions", json=request)
                assert duplicate.json()["executionId"] == first["executionId"]
                assert writes == [] and provider.requests == []
                pending = (await client.get("/api/v1/human-tasks")).json()
                assert len(pending) == 1
                assert first["sessionId"] in pending[0]["description"]
                action_path = f"/api/v1/human-tasks/{pending[0]['humanTaskId']}/actions"
                current_actor = actor.model_copy(update={"principal_id": uuid4()})
                denied = await client.post(
                    action_path, json={"action": "APPROVE", "idempotencyKey": "outsider-approval"}
                )
                assert denied.status_code == 404, denied.text
                current_actor = actor
                approved = await client.post(
                    action_path, json={"action": "APPROVE", "idempotencyKey": "approved-first"}
                )
                assert approved.status_code == 200, approved.text
                await drive(first["executionId"])
                assert writes == ["approved"]
                first_record = (
                    await sessions.get_session("default", UUID(first["taskRunId"]), 1)
                ).session
                assert first_record.final_result == {"answer": "written"}

                path = f"/api/v1/agent-sessions/{first['sessionId']}/messages"
                follow = await client.post(
                    path,
                    headers={"Idempotency-Key": "message-two"},
                    json={"input": {"question": "Use that label again"}},
                )
                assert follow.status_code == 200, follow.text
                second = follow.json()
                assert second["sessionId"] == first["sessionId"]
                assert second["executionId"] != first["executionId"]
                assert writes == ["approved"]
                pending = (await client.get("/api/v1/human-tasks")).json()
                assert len(pending) == 1 and pending[0]["executionId"] == second["executionId"]
                approved = await client.post(
                    f"/api/v1/human-tasks/{pending[0]['humanTaskId']}/actions",
                    json={"action": "APPROVE", "idempotencyKey": "approved-second"},
                )
                assert approved.status_code == 200, approved.text
                await drive(second["executionId"])
                assert writes == ["approved", "approved"]
                second_record = (
                    await sessions.get_session("default", UUID(second["taskRunId"]), 2)
                ).session
                assert second_record.capability_pin_id == first_record.capability_pin_id
                assert second_record.envelope_digest == first_record.envelope_digest
                assert second_record.harness == first_record.harness
                assert "Cedar Finch" in str(provider.requests[2].payload["messages"])
                replay = await client.post(
                    path,
                    headers={"Idempotency-Key": "message-two"},
                    json={"input": {"question": "Use that label again"}},
                )
                assert replay.json()["executionId"] == second["executionId"]
                await drive(second["executionId"])
                assert writes == ["approved", "approved"] and len(provider.requests) == 4
                third = await client.post(
                    path,
                    headers={"Idempotency-Key": "message-three"},
                    json={"input": {"question": "Write once more"}},
                )
                assert third.status_code == 200, third.text
                pending = (await client.get("/api/v1/human-tasks")).json()
                assert len(pending) == 1
                # Replaying an earlier decision cannot release the new execution.
                await client.post(
                    action_path, json={"action": "APPROVE", "idempotencyKey": "approved-first"}
                )
                await drive(third.json()["executionId"])
                assert writes == ["approved", "approved"] and len(provider.requests) == 4
                rejected = await client.post(
                    f"/api/v1/human-tasks/{pending[0]['humanTaskId']}/actions",
                    json={"action": "REJECT", "idempotencyKey": "rejected-third"},
                )
                assert rejected.status_code == 200, rejected.text
                with pytest.raises(TaskExecutionError, match="requires an APPROVED"):
                    await drive(third.json()["executionId"])
                assert writes == ["approved", "approved"]
        finally:
            app_module.app.dependency_overrides.clear()
            app_module.app.dependency_overrides.update(previous_overrides)
            await engine.dispose()

    asyncio.run(scenario())
