from __future__ import annotations

import asyncio
import os
from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAgentPrimitiveRepository,
    PostgresAgentResourceRepository,
)
from amesh.domain import (
    AgentDefinitionSpec,
    AgentEvaluationFixture,
    AgentEvaluationPolicy,
    AgentEvaluationSpec,
    AgentHardLimits,
    AgentJudgePolicy,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRef,
    AgentToolRef,
    McpConnectionSpec,
    McpToolImpact,
    McpToolPin,
    ModelPolicySpec,
    ModelProviderSpec,
    ModelRoute,
    OrderedPromptRef,
    PromptSpec,
    SkillSpec,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_resource_revisions_resolve_atomically_and_remain_tenant_scoped() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = create_async_engine(database.database_url)
        resources = PostgresAgentResourceRepository(engine)
        primitives = PostgresAgentPrimitiveRepository(engine)
        try:
            await apply_migrations(database.database_url, migration_directory())
            tool = McpToolPin(
                name="search",
                inputSchema={"type": "object", "additionalProperties": False},
                impact=McpToolImpact.READ_ONLY,
            )
            connection = await primitives.save_mcp_connection(
                "default",
                McpConnectionSpec(
                    key="catalog",
                    namespace="agents.demo",
                    endpoint="https://mcp.example.test/mcp",
                    credentialRef="mcp-token",
                    toolAllowlist=("search",),
                    tools=(tool,),
                ),
                actor_id="author",
            )
            prompt = await resources.save_resource(
                "default",
                PromptSpec(
                    key="house-style",
                    namespace="agents.demo",
                    title="House style",
                    content="Answer concisely.",
                ),
                actor_id="author",
            )
            skill = await resources.save_resource(
                "default",
                SkillSpec(
                    key="citation",
                    namespace="agents.demo",
                    title="Citation",
                    instructions="Cite evidence.",
                    requestedCapabilities=("cite",),
                ),
                actor_id="author",
            )
            policy = await resources.save_resource(
                "default",
                ModelPolicySpec(
                    key="openrouter-luna",
                    namespace="agents.demo",
                    title="OpenRouter Luna",
                    routes=(
                        ModelRoute(
                            routeId="primary",
                            provider=ModelProviderSpec(
                                endpoint="https://openrouter.ai/api/v1",
                                credentialRef="openrouter-api-key",
                            ),
                            model="openai/gpt-5.6-luna",
                        ),
                    ),
                    outputNondeterminismDisclosure="Model output can vary.",
                ),
                actor_id="author",
            )
            evaluation = await resources.save_resource(
                "default",
                AgentEvaluationSpec(
                    key="quality",
                    namespace="agents.demo",
                    title="Quality gate",
                    assertions=(
                        {
                            "type": "object",
                            "properties": {"answer": {"type": "string"}},
                            "required": ["answer"],
                        },
                    ),
                    fixtures=(
                        AgentEvaluationFixture(
                            key="passing",
                            input={"question": "test"},
                            recordedOutput={"answer": "bounded"},
                        ),
                    ),
                    judge=AgentJudgePolicy(
                        modelPolicy=AgentResourceRef(
                            key=policy.key,
                            revision=policy.revision,
                        ),
                        prompt="Score output quality and report uncertainty.",
                        minimumScore="0.8",
                        maximumUncertainty="0.2",
                        maxCompletionTokens=250,
                    ),
                ),
                actor_id="author",
            )
            agent_spec = AgentDefinitionSpec(
                key="researcher",
                namespace="agents.demo",
                title="Researcher",
                instructions="Return structured evidence.",
                inputSchema={"type": "object"},
                outputSchema={"type": "object"},
                modelPolicy=AgentResourceRef(key=policy.key, revision=policy.revision),
                prompts=(OrderedPromptRef(key=prompt.key, revision=prompt.revision, order=10),),
                skills=(AgentResourceRef(key=skill.key, revision=skill.revision),),
                tools=(
                    AgentToolRef(
                        connectionKey=connection.spec.key,
                        connectionRevision=connection.revision,
                        toolName=tool.name,
                        schemaDigest=tool.schema_digest,
                    ),
                ),
                memoryPolicy=AgentMemoryPolicy(),
                permissions=AgentPermissions(
                    delegatedCapabilities=("cite",),
                    toolAllowlist=("search",),
                    secretScopes=("openrouter-api-key", "mcp-token"),
                    networkHosts=("openrouter.ai", "mcp.example.test"),
                ),
                hardLimits=AgentHardLimits(
                    maxTotalTokens=4000,
                    maxCostUsd=Decimal("0.20"),
                    maxDurationSeconds=120,
                    maxToolCalls=4,
                    maxTurns=3,
                    maxLoopIterations=0,
                    maxRecursionDepth=0,
                    maxConcurrency=1,
                ),
                evaluationPolicy=AgentEvaluationPolicy(
                    requiredEvaluations=("schema", "quality"),
                    evaluations=(
                        AgentResourceRef(
                            key=evaluation.key,
                            revision=evaluation.revision,
                        ),
                    ),
                ),
            )
            first_agent = await resources.save_resource(
                "default",
                agent_spec,
                actor_id="author",
            )
            second_agent = await resources.save_resource(
                "default",
                agent_spec.model_copy(update={"title": "Researcher v2"}),
                actor_id="author",
            )
            assert first_agent.resource_id == second_agent.resource_id
            assert (first_agent.revision, second_agent.revision) == (1, 2)
            assert len(await resources.list_resources("default", "agents.demo")) == 5
            assert (
                await resources.get_resource(
                    "default",
                    "agents.demo",
                    AgentResourceKind.AGENT,
                    "researcher",
                )
            ).revision == 2

            request = AgentResolutionRequest(agentRevision=1, subjectRef="session:test-1")
            pin = await resources.resolve_agent(
                "default",
                "agents.demo",
                "researcher",
                request,
                actor_id="runner",
            )
            restarted_repository = PostgresAgentResourceRepository(engine)
            duplicate = await restarted_repository.resolve_agent(
                "default",
                "agents.demo",
                "researcher",
                request,
                actor_id="runner",
            )
            assert duplicate.pin_id == pin.pin_id
            assert duplicate.envelope_digest == pin.envelope.digest
            assert duplicate.envelope.model_routes[0].model == "openai/gpt-5.6-luna"
            assert duplicate.envelope.evaluations[0].resource.key == "quality"
            assert duplicate.envelope.evaluations[0].judge_model_routes[0].model == (
                "openai/gpt-5.6-luna"
            )
            preview = await resources.preview_agent(
                "default",
                "agents.demo",
                "researcher",
                agent_revision=1,
            )
            assert preview.external_calls_suppressed is True
            assert preview.model_behavior_unknown is True
            assert preview.envelope_digest == pin.envelope_digest

            with pytest.raises(ValueError, match="different envelope"):
                await resources.resolve_agent(
                    "default",
                    "agents.demo",
                    "researcher",
                    AgentResolutionRequest(agentRevision=2, subjectRef="session:test-1"),
                    actor_id="runner",
                )
            with pytest.raises(LookupError):
                await resources.get_resource(
                    "amesh-system",
                    "agents.demo",
                    AgentResourceKind.AGENT,
                    "researcher",
                )
            async with engine.connect() as sql:
                evidence = await sql.scalar(
                    text(
                        "SELECT evidence FROM audit_events "
                        "WHERE action = 'agent.capability_envelope.pin' LIMIT 1"
                    )
                )
            assert "openrouter-api-key" not in str(evidence)
            assert "mcp-token" not in str(evidence)
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
