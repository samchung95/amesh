from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest

from amesh.domain.agent_primitives import (
    McpConnectionRevision,
    McpConnectionSpec,
    McpToolPin,
    ModelProviderSpec,
)
from amesh.domain.agent_resources import (
    AgentDefinitionSpec,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    AgentResourceKind,
    AgentResourceRef,
    AgentResourceRevision,
    AgentToolRef,
    ModelPolicySpec,
    ModelRoute,
    OrderedPromptRef,
    PromptSpec,
    agent_resource_digest,
)
from amesh.profile_transfer import (
    ProfileCompatibilityError,
    ProfileTransferService,
)


class FakeResources:
    def __init__(self, items: tuple[AgentResourceRevision, ...] = ()) -> None:
        self.items = {(item.kind, item.key, item.revision): item for item in items}
        self.save_calls = 0

    async def get_resource(
        self,
        tenant_id: str,
        namespace: str,
        kind: AgentResourceKind,
        key: str,
        *,
        revision: int | None = None,
    ) -> AgentResourceRevision:
        selected = [item for item in self.items.values() if item.kind is kind and item.key == key]
        if revision is not None:
            selected = [item for item in selected if item.revision == revision]
        if not selected:
            raise LookupError("missing")
        return max(selected, key=lambda item: item.revision)

    async def list_resources(
        self, tenant_id: str, namespace: str, *, kind: AgentResourceKind | None = None
    ) -> tuple[AgentResourceRevision, ...]:
        selected = [item for item in self.items.values() if kind is None or item.kind is kind]
        latest: dict[tuple[AgentResourceKind, str], AgentResourceRevision] = {}
        for item in selected:
            latest[(item.kind, item.key)] = max(
                item,
                latest.get((item.kind, item.key), item),
                key=lambda candidate: candidate.revision,
            )
        return tuple(latest.values())

    async def save_resource(
        self, tenant_id: str, spec: Any, *, actor_id: str
    ) -> AgentResourceRevision:
        self.save_calls += 1
        existing = [
            item for item in self.items.values() if item.kind is spec.kind and item.key == spec.key
        ]
        revision = max((item.revision for item in existing), default=0) + 1
        item = AgentResourceRevision(
            resourceId=uuid4(),
            tenantId=tenant_id,
            namespace=spec.namespace,
            kind=spec.kind,
            key=spec.key,
            revision=revision,
            digest=agent_resource_digest(spec),
            spec=spec,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )
        self.items[(item.kind, item.key, item.revision)] = item
        return item


class FakePrimitives:
    def __init__(self, items: tuple[McpConnectionRevision, ...] = ()) -> None:
        self.items = {(item.spec.key, item.revision): item for item in items}
        self.save_calls = 0

    async def get_mcp_connection(
        self, tenant_id: str, namespace: str, key: str, *, revision: int | None = None
    ) -> McpConnectionRevision:
        selected = [item for item in self.items.values() if item.spec.key == key]
        if revision is not None:
            selected = [item for item in selected if item.revision == revision]
        if not selected:
            raise LookupError("missing")
        return max(selected, key=lambda item: item.revision)

    async def list_mcp_connections(
        self, tenant_id: str, namespace: str
    ) -> tuple[McpConnectionRevision, ...]:
        latest: dict[str, McpConnectionRevision] = {}
        for item in self.items.values():
            latest[item.spec.key] = max(
                item, latest.get(item.spec.key, item), key=lambda candidate: candidate.revision
            )
        return tuple(latest.values())

    async def save_mcp_connection(
        self, tenant_id: str, spec: McpConnectionSpec, *, actor_id: str
    ) -> McpConnectionRevision:
        self.save_calls += 1
        existing = [item for item in self.items.values() if item.spec.key == spec.key]
        revision = max((item.revision for item in existing), default=0) + 1
        item = McpConnectionRevision(
            connectionId=uuid4(),
            tenantId=tenant_id,
            revision=revision,
            digest=spec.digest,
            spec=spec,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )
        self.items[(item.spec.key, item.revision)] = item
        return item


def _resources(
    tenant_id: str = "source",
) -> tuple[tuple[AgentResourceRevision, ...], McpConnectionRevision]:
    namespace = "agents.demo"
    now = datetime.now(UTC)
    prompt = PromptSpec(key="welcome", namespace=namespace, title="Welcome", content="Hello")
    policy = ModelPolicySpec(
        key="default",
        namespace=namespace,
        title="Default",
        routes=(
            ModelRoute(
                routeId="primary",
                provider=ModelProviderSpec(
                    endpoint="https://model.test", credentialRef="model-key"
                ),
                model="test",
            ),
        ),
        outputNondeterminismDisclosure="Model output may vary.",
    )
    connection_spec = McpConnectionSpec(
        key="tools",
        namespace=namespace,
        endpoint="https://mcp.test",
        credentialRef="mcp-key",
        toolAllowlist=("search",),
        tools=(McpToolPin(name="search", inputSchema={"type": "object"}),),
    )
    agent = AgentDefinitionSpec(
        key="researcher",
        namespace=namespace,
        title="Researcher",
        instructions="Research.",
        inputSchema={"type": "object"},
        outputSchema={"type": "object"},
        modelPolicy=AgentResourceRef(key=policy.key, revision=1),
        prompts=(OrderedPromptRef(key=prompt.key, revision=1, order=1),),
        tools=(
            AgentToolRef(
                connectionKey="tools",
                connectionRevision=1,
                toolName="search",
                schemaDigest=connection_spec.tools[0].schema_digest,
            ),
        ),
        memoryPolicy=AgentMemoryPolicy(),
        permissions=AgentPermissions(
            toolAllowlist=("search",), secretScopes=("model-key", "mcp-key")
        ),
        hardLimits=AgentHardLimits(
            maxTotalTokens=100,
            maxCostUsd=Decimal("1"),
            maxDurationSeconds=10,
            maxToolCalls=2,
            maxTurns=1,
            maxLoopIterations=1,
            maxRecursionDepth=1,
            maxConcurrency=1,
        ),
        evaluationPolicy=AgentEvaluationPolicy(),
    )

    def revision(spec: Any, kind: AgentResourceKind) -> AgentResourceRevision:
        return AgentResourceRevision(
            resourceId=uuid4(),
            tenantId=tenant_id,
            namespace=namespace,
            kind=kind,
            key=spec.key,
            revision=1,
            digest=agent_resource_digest(spec),
            spec=spec,
            createdBy="author",
            createdAt=now,
        )

    return (
        revision(prompt, AgentResourceKind.PROMPT),
        revision(policy, AgentResourceKind.MODEL_POLICY),
        revision(agent, AgentResourceKind.AGENT),
    ), McpConnectionRevision(
        connectionId=uuid4(),
        tenantId=tenant_id,
        revision=1,
        digest=connection_spec.digest,
        spec=connection_spec,
        createdBy="author",
        createdAt=now,
    )


def test_profile_round_trip_is_canonical_and_idempotent() -> None:
    async def scenario() -> None:
        source_items, source_connection = _resources()
        service = ProfileTransferService(
            FakeResources(source_items), FakePrimitives((source_connection,))
        )
        bundle = await service.export("source", "agents.demo", "researcher")

        bundle.verify()
        with pytest.raises(ValueError, match="checksum"):
            bundle.model_copy(update={"agent_key": "tampered"}).verify()
        assert bundle.canonical_bytes() == bundle.model_copy().canonical_bytes()
        assert bundle.model_dump_json() == bundle.model_copy().model_dump_json()
        assert {item.kind for item in bundle.resources} == {
            AgentResourceKind.PROMPT,
            AgentResourceKind.MODEL_POLICY,
            AgentResourceKind.AGENT,
        }
        assert bundle.mcp_connections[0].spec.credential_ref == "mcp-key"
        assert "apiKey" not in bundle.model_dump_json()

        target_resources = FakeResources()
        target_primitives = FakePrimitives()
        target = ProfileTransferService(target_resources, target_primitives)
        first = await target.import_bundle(bundle, target_tenant_id="target", actor_id="importer")
        second = await target.import_bundle(bundle, target_tenant_id="target", actor_id="importer")
        assert first.resources_imported == 3
        assert first.mcp_connections_imported == 1
        assert second.resources_imported == 0
        assert second.mcp_connections_imported == 0
        assert target_resources.save_calls == 3
        assert target_primitives.save_calls == 1

    asyncio.run(scenario())


def test_profile_rejects_secret_bearing_options_before_export() -> None:
    async def scenario() -> None:
        for field in ("apiKey", "clientSecret", "accessTokenValue"):
            source_items, source_connection = _resources()
            policy = source_items[1]
            unsafe = policy.spec.model_copy(
                update={
                    "routes": (
                        policy.spec.routes[0].model_copy(
                            update={"parameters": {"providerOptions": {field: "plaintext"}}}
                        ),
                    )
                }
            )
            source_items = (
                *source_items[:1],
                policy.model_copy(update={"spec": unsafe, "digest": agent_resource_digest(unsafe)}),
                source_items[2],
            )
            service = ProfileTransferService(
                FakeResources(source_items), FakePrimitives((source_connection,))
            )
            with pytest.raises(ValueError, match="secret-bearing"):
                await service.export("source", "agents.demo", "researcher")

    asyncio.run(scenario())


def test_profile_compatibility_failure_happens_before_mutation() -> None:
    async def scenario() -> None:
        source_items, source_connection = _resources()
        bundle = await ProfileTransferService(
            FakeResources(source_items), FakePrimitives((source_connection,))
        ).export("source", "agents.demo", "researcher")
        conflicting = source_items[0].spec.model_copy(update={"content": "different"})
        target_item = source_items[0].model_copy(
            update={
                "tenant_id": "target",
                "spec": conflicting,
                "digest": agent_resource_digest(conflicting),
            }
        )
        target_resources = FakeResources((target_item,))
        target_primitives = FakePrimitives()
        with pytest.raises(ProfileCompatibilityError) as error:
            await ProfileTransferService(target_resources, target_primitives).import_bundle(
                bundle, target_tenant_id="target", actor_id="importer"
            )
        assert not error.value.report.compatible
        assert target_resources.save_calls == 0
        assert target_primitives.save_calls == 0

    asyncio.run(scenario())
