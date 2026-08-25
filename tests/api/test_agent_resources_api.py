from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_resource_repository,
    get_authorization_service,
    get_operational_control_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AgentCapabilityPin,
    AgentDefinitionSpec,
    AgentEnvelopePreview,
    AgentResolutionRequest,
    AgentResourceKind,
    AgentResourceRevision,
    AgentResourceSpec,
    AuthorizationDecision,
    AuthorizationRequest,
    OperationalBoundary,
    OperationalControlDecision,
    PrincipalType,
    RunningWorkPolicy,
    agent_resource_digest,
    resolve_capability_envelope,
)


class _Authorization:
    def __init__(self, allow: bool = True) -> None:
        self.allow = allow
        self.requests: list[AuthorizationRequest] = []

    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(
            allowed=self.allow,
            reason_code="test_allow" if self.allow else "test_deny",
            summary="agent resource API fixture",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug
        return 1


class _Controls:
    async def evaluate(
        self,
        boundary: OperationalBoundary,
        **kwargs: object,
    ) -> OperationalControlDecision:
        del kwargs
        return OperationalControlDecision(
            blocked=False,
            boundary=boundary,
            runningWorkPolicy=RunningWorkPolicy.CONTINUE,
        )


class _Repository:
    def __init__(self) -> None:
        self.saved: list[AgentResourceRevision] = []

    async def save_resource(
        self,
        tenant_id: str,
        spec: AgentResourceSpec,
        *,
        actor_id: str,
    ) -> AgentResourceRevision:
        previous = [
            item
            for item in self.saved
            if item.tenant_id == tenant_id
            and item.namespace == spec.namespace
            and item.kind is spec.kind
            and item.key == spec.key
        ]
        revision = AgentResourceRevision(
            resourceId=previous[-1].resource_id if previous else uuid4(),
            tenantId=tenant_id,
            namespace=spec.namespace,
            kind=spec.kind,
            key=spec.key,
            revision=len(previous) + 1,
            digest=agent_resource_digest(spec),
            spec=spec,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )
        self.saved.append(revision)
        return revision

    async def get_resource(
        self,
        tenant_id: str,
        namespace: str,
        kind: AgentResourceKind,
        key: str,
        *,
        revision: int | None = None,
    ) -> AgentResourceRevision:
        matches = [
            item
            for item in self.saved
            if item.tenant_id == tenant_id
            and item.namespace == namespace
            and item.kind is kind
            and item.key == key
            and (revision is None or item.revision == revision)
        ]
        if not matches:
            raise LookupError("resource not found")
        return matches[-1]

    async def list_resources(
        self,
        tenant_id: str,
        namespace: str,
        *,
        kind: AgentResourceKind | None = None,
    ) -> tuple[AgentResourceRevision, ...]:
        latest: dict[tuple[AgentResourceKind, str], AgentResourceRevision] = {}
        for item in self.saved:
            if (
                item.tenant_id == tenant_id
                and item.namespace == namespace
                and (kind is None or item.kind is kind)
            ):
                latest[(item.kind, item.key)] = item
        return tuple(latest.values())

    async def resolve_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        request: AgentResolutionRequest,
        *,
        actor_id: str,
    ) -> AgentCapabilityPin:
        agent = await self.get_resource(
            tenant_id,
            namespace,
            AgentResourceKind.AGENT,
            key,
            revision=request.agent_revision,
        )
        assert isinstance(agent.spec, AgentDefinitionSpec)
        policy = await self.get_resource(
            tenant_id,
            namespace,
            AgentResourceKind.MODEL_POLICY,
            agent.spec.model_policy.key,
            revision=agent.spec.model_policy.revision,
        )
        prompts = tuple(
            [
                await self.get_resource(
                    tenant_id,
                    namespace,
                    AgentResourceKind.PROMPT,
                    ref.key,
                    revision=ref.revision,
                )
                for ref in agent.spec.prompts
            ]
        )
        evaluations = tuple(
            [
                await self.get_resource(
                    tenant_id,
                    namespace,
                    AgentResourceKind.EVALUATION,
                    ref.key,
                    revision=ref.revision,
                )
                for ref in agent.spec.evaluation_policy.evaluations
            ]
        )
        envelope = resolve_capability_envelope(
            agent,
            policy,
            prompts,
            (),
            (),
            evaluations,
            (),
        )
        return AgentCapabilityPin(
            tenantId=tenant_id,
            namespace=namespace,
            subjectRef=request.subject_ref,
            envelopeDigest=envelope.digest,
            envelope=envelope,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )

    async def preview_agent(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        *,
        agent_revision: int,
    ) -> AgentEnvelopePreview:
        pin = await self.resolve_agent(
            tenant_id,
            namespace,
            key,
            AgentResolutionRequest(
                agentRevision=agent_revision,
                subjectRef="side-effect-free-preview",
            ),
            actor_id="preview",
        )
        return AgentEnvelopePreview(
            agentRevision=agent_revision,
            envelopeDigest=pin.envelope_digest,
            envelope=pin.envelope,
        )


def _overrides(repository: _Repository, authorization: _Authorization) -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="agent-author",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_agent_resource_repository] = lambda: repository
    app.dependency_overrides[get_tenant_service] = _TenantQuota
    app.dependency_overrides[get_operational_control_repository] = _Controls


def test_agent_resource_api_creates_compares_and_explains_exact_envelopes() -> None:
    repository = _Repository()
    authorization = _Authorization()
    _overrides(repository, authorization)

    async def scenario() -> None:
        headers = {"X-Amesh-Tenant": "default"}
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            prompt = await client.post(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                json={
                    "kind": "PROMPT",
                    "key": "house-style",
                    "namespace": "agents.demo",
                    "title": "House style",
                    "content": "Be concise.",
                },
            )
            assert prompt.status_code == 201, prompt.text
            policy = await client.post(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                json={
                    "kind": "MODEL_POLICY",
                    "key": "openrouter-luna",
                    "namespace": "agents.demo",
                    "title": "OpenRouter Luna",
                    "routes": [
                        {
                            "routeId": "primary",
                            "provider": {
                                "endpoint": "https://openrouter.ai/api/v1",
                                "credentialRef": "openrouter-api-key",
                            },
                            "model": "openai/gpt-5.6-luna",
                        }
                    ],
                    "outputNondeterminismDisclosure": "Model output can vary.",
                },
            )
            assert policy.status_code == 201, policy.text
            evaluation = await client.post(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                json={
                    "kind": "EVALUATION",
                    "key": "quality",
                    "namespace": "agents.demo",
                    "title": "Quality gate",
                    "assertions": [
                        {
                            "type": "object",
                            "properties": {"answer": {"type": "string"}},
                            "required": ["answer"],
                        }
                    ],
                    "fixtures": [
                        {
                            "key": "passing",
                            "input": {"question": "test"},
                            "recordedOutput": {"answer": "bounded"},
                        }
                    ],
                },
            )
            assert evaluation.status_code == 201, evaluation.text
            agent_spec = {
                "kind": "AGENT",
                "key": "researcher",
                "namespace": "agents.demo",
                "title": "Researcher",
                "instructions": "Return structured evidence.",
                "inputSchema": {"type": "object"},
                "outputSchema": {"type": "object"},
                "modelPolicy": {"key": "openrouter-luna", "revision": 1},
                "prompts": [{"key": "house-style", "revision": 1, "order": 10}],
                "memoryPolicy": {"scope": "NONE"},
                "permissions": {
                    "secretScopes": ["openrouter-api-key"],
                    "networkHosts": ["openrouter.ai"],
                },
                "hardLimits": {
                    "maxTotalTokens": 4000,
                    "maxCostUsd": "0.20",
                    "maxDurationSeconds": 120,
                    "maxToolCalls": 0,
                    "maxTurns": 3,
                    "maxLoopIterations": 0,
                    "maxRecursionDepth": 0,
                    "maxConcurrency": 1,
                },
                "evaluationPolicy": {
                    "requiredEvaluations": ["schema", "quality"],
                    "evaluations": [{"key": "quality", "revision": 1}],
                },
            }
            first = await client.post(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                json=agent_spec,
            )
            assert first.status_code == 201, first.text
            second = await client.post(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                json={**agent_spec, "title": "Researcher v2", "prompts": []},
            )
            assert second.status_code == 201, second.text

            listed = await client.get(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers=headers,
                params={"kind": "AGENT"},
            )
            assert [item["revision"] for item in listed.json()] == [2]
            comparison = await client.get(
                "/api/v1/namespaces/agents.demo/agent/definitions/researcher/compare",
                headers=headers,
                params={"fromRevision": 1, "toRevision": 2},
            )
            assert comparison.status_code == 200, comparison.text
            assert comparison.json()["removedPrompts"] == ["house-style@1"]
            resolved = await client.post(
                "/api/v1/namespaces/agents.demo/agent/definitions/researcher/resolve",
                headers=headers,
                json={"agentRevision": 1, "subjectRef": "session:test-1"},
            )
            assert resolved.status_code == 200, resolved.text
            assert resolved.json()["envelope"]["modelRoutes"][0]["model"] == ("openai/gpt-5.6-luna")
            assert "actual-openrouter-secret" not in resolved.text
            preview = await client.get(
                "/api/v1/namespaces/agents.demo/agent/definitions/researcher/preview",
                headers=headers,
                params={"agentRevision": 1},
            )
            assert preview.status_code == 200, preview.text
            assert preview.json()["externalCallsSuppressed"] is True
            assert preview.json()["modelBehaviorUnknown"] is True
            assert preview.json()["envelope"]["evaluations"][0]["resource"]["key"] == ("quality")
            fixture = await client.get(
                "/api/v1/namespaces/agents.demo/agent/evaluations/quality/fixtures/passing/preview",
                headers=headers,
                params={"revision": 1},
            )
            assert fixture.status_code == 200, fixture.text
            assert fixture.json()["deterministic"]["passed"] is True
            assert fixture.json()["externalCallsSuppressed"] is True

            cross_tenant = await client.get(
                "/api/v1/namespaces/agents.demo/agent/resources/AGENT/researcher",
                headers={"X-Amesh-Tenant": "amesh-system"},
            )
            assert cross_tenant.status_code == 404

    try:
        asyncio.run(scenario())
        assert {request.resource_type for request in authorization.requests} == {"agent"}
    finally:
        app.dependency_overrides.clear()


def test_agent_resource_api_authorization_denial_is_closed() -> None:
    repository = _Repository()
    _overrides(repository, _Authorization(allow=False))

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                "/api/v1/namespaces/agents.demo/agent/resources",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert response.status_code == 404

    try:
        asyncio.run(scenario())
        assert repository.saved == []
    finally:
        app.dependency_overrides.clear()
