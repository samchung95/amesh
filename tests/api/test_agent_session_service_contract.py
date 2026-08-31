from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import HTTPException

from amesh.adapters.agent_session_registry import AGENT_SESSION_HARNESS_REGISTRY
from amesh.adapters.openai_session import (
    CanonicalInlineImageUpload,
    CanonicalSessionRequest,
)
from amesh.api.models import (
    AgentSessionCreateRequest,
    AgentSessionHarnessCatalogEntry,
    AgentSessionLaunchResponse,
)
from amesh.app import (
    _stage_openai_session_images,
    app,
    authenticate_actor,
    authorize_agent_session_request,
    get_agent_resource_repository,
    get_agent_session_repository,
    get_authorization_service,
    get_operational_control_repository,
    get_repository,
    get_shared_resource_repository,
    get_task_cache_repository,
    require_tenant_context,
)
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AgentHardLimits,
    AgentSessionEvent,
    AgentSessionPhase,
    AgentSessionState,
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    AuthorizationDecision,
    AuthorizationRequest,
    ExecutionState,
    ImageArtifactRef,
    ImageDisplayMetadata,
    ModelProviderSpec,
    ModelRoute,
    PermissionAction,
    PrincipalType,
    TaskRunState,
    build_artifact_reference,
)
from amesh.dsl import FlowDefinition
from amesh.ports import PersistedExecution, PersistedTaskRun


def test_session_authorization_uses_legacy_execution_grant_during_upgrade() -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="legacy-client"
    )

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            allowed = request.resource_type == "execution"
            return AuthorizationDecision(
                allowed=allowed,
                reason_code="ROLE_GRANT" if allowed else "NO_MATCHING_GRANT",
                summary="upgrade compatibility",
                policy_version=1,
                matched_role_names=("flow-author",),
            )

    decision = asyncio.run(
        authorize_agent_session_request(
            Authorization(),  # type: ignore[arg-type]
            actor,
            action=PermissionAction.CREATE,
            legacy_actions=(PermissionAction.EXECUTE,),
            tenant_id="default",
            namespace="research",
        )
    )

    assert decision.allowed
    assert decision.matched_role_names == ("flow-author",)


def test_explicit_session_deny_never_falls_back_to_execution_grant() -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="denied-client"
    )
    requests: list[AuthorizationRequest] = []

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            requests.append(request)
            allowed = request.resource_type == "execution"
            return AuthorizationDecision(
                allowed=allowed,
                reason_code="ROLE_GRANT" if allowed else "EXPLICIT_DENY",
                summary="explicit session deny",
                policy_version=1,
                matched_role_names=("session-deny",),
            )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            authorize_agent_session_request(
                Authorization(),  # type: ignore[arg-type]
                actor,
                action=PermissionAction.CREATE,
                legacy_actions=(PermissionAction.EXECUTE,),
                tenant_id="default",
                namespace="research",
            )
        )

    assert exc_info.value.status_code == 403
    assert [request.resource_type for request in requests] == ["agent_session"]


def test_agent_ref_is_the_harness_neutral_revision_pin() -> None:
    request = AgentSessionCreateRequest.model_validate(
        {"agentRef": "research/analyst@7", "input": {"document": "brief"}}
    )

    assert request.namespace == "research"
    assert request.agent == "analyst"
    assert request.agent_revision == 7


def test_agent_ref_rejects_conflicting_explicit_revision() -> None:
    with pytest.raises(ValueError, match="conflicts"):
        AgentSessionCreateRequest.model_validate(
            {
                "agentRef": "research/analyst@7",
                "namespace": "research",
                "agent": "analyst",
                "agentRevision": 8,
            }
        )


def test_generated_session_flow_id_is_stable_per_revision() -> None:
    from amesh.app import _agent_session_flow_id

    assert _agent_session_flow_id("research", "analyst", 7) == _agent_session_flow_id(
        "research", "analyst", 7
    )
    assert _agent_session_flow_id("research", "analyst", 7) != _agent_session_flow_id(
        "research", "analyst", 8
    )


def test_create_agent_session_accepts_required_tool_plan_and_launches_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from amesh import app as app_module

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    captured_flows: list[FlowDefinition] = []
    execution_id = uuid4()
    task_run_id = uuid4()
    now = datetime.now(UTC)

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            del request
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="session launch test",
                policy_version=1,
                matched_role_names=("session-operator",),
            )

        async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return await self.decide(request)

    class Resources:
        async def preview_agent(
            self,
            tenant_id: str,
            namespace: str,
            key: str,
            *,
            agent_revision: int,
        ) -> object:
            assert (tenant_id, namespace, key, agent_revision) == (
                "default",
                "research",
                "analyst",
                7,
            )
            return SimpleNamespace(
                envelope=SimpleNamespace(
                    input_schema={},
                    model_routes=(),
                    tools=(),
                    hard_limits=AgentHardLimits(
                        maxTotalTokens=1000,
                        maxCostUsd=Decimal("1"),
                        maxDurationSeconds=60,
                        maxToolCalls=10,
                        maxTurns=4,
                        maxLoopIterations=4,
                        maxRecursionDepth=1,
                        maxConcurrency=2,
                    ),
                    permissions=SimpleNamespace(secret_scopes=()),
                )
            )

    class Policies:
        async def effective_revisions(
            self,
            tenant_id: str,
            *,
            namespace: str,
            application_id: str,
        ) -> tuple[object, ...]:
            assert (tenant_id, namespace, application_id) == (
                "default",
                "research",
                "operator",
            )
            return ()

    class Sessions:
        async def get_execution_by_service_session_id(
            self,
            tenant_id: str,
            service_session_id: UUID,
        ) -> UUID:
            del tenant_id, service_session_id
            raise LookupError("session detail not started")

    async def fake_execute_flow(*args: object, **kwargs: object) -> object:
        del kwargs
        flow = args[2]
        assert isinstance(flow, FlowDefinition)
        captured_flows.append(flow)
        return SimpleNamespace(
            execution=PersistedExecution(
                execution_id=execution_id,
                tenant_id="default",
                state=ExecutionState.RUNNING,
                epoch=1,
                version=1,
                namespace="research",
                flow_id="agent_session_stable",
                created_at=now,
                updated_at=now,
                trigger={},
            ),
            task_runs=[
                PersistedTaskRun(
                    task_run_id=task_run_id,
                    execution_id=execution_id,
                    task_id="agent",
                    state=TaskRunState.RUNNING,
                    current_attempt=1,
                    version=1,
                )
            ],
        )

    monkeypatch.setattr(app_module, "_execute_flow", fake_execute_flow)
    monkeypatch.setattr(app_module, "get_agent_session_policy_repository", lambda: Policies())
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_settings: lambda: Settings(_env_file=None),  # type: ignore[call-arg]
            get_authorization_service: Authorization,
            get_repository: lambda: object(),
            get_task_cache_repository: lambda: object(),
            get_shared_resource_repository: lambda: object(),
            get_operational_control_repository: lambda: object(),
            get_agent_session_repository: Sessions,
            get_agent_resource_repository: Resources,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                "/api/v1/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
                json={
                    "agentRef": "research/analyst@7",
                    "input": {"question": "latest earnings"},
                    "requiredToolPlan": {
                        "schemaVersion": "amesh.agent-tool-plan/v1",
                        "steps": [
                            {
                                "stepId": "lookup",
                                "toolName": "market.search",
                                "arguments": {"query": "latest earnings"},
                            }
                        ],
                        "maxOccurrences": 1,
                    },
                },
            )
        assert response.status_code == 200, response.text
        assert response.json()["executionId"] == str(execution_id)
        assert len(captured_flows) == 1
        task = captured_flows[0].tasks[0]
        assert task.model_dump(mode="json", by_alias=True)["requiredToolPlan"] == {
            "schemaVersion": "amesh.agent-tool-plan/v1",
            "steps": [
                {
                    "stepId": "lookup",
                    "toolName": "market.search",
                    "arguments": {"query": "latest earnings"},
                    "argumentBindings": {},
                    "itemArgumentBindings": {},
                    "maxOccurrences": 1000,
                }
            ],
            "maxOccurrences": 1,
        }

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_public_idempotency_keys_are_scoped_to_the_service_session_identity() -> None:
    from amesh.app import (
        _agent_session_execution_idempotency_key,
        _agent_session_service_session_id,
    )

    first = _agent_session_service_session_id("tenant-a", "research", "actor-a", "same-key")
    second = _agent_session_service_session_id("tenant-a", "trading", "actor-a", "same-key")
    other_actor = _agent_session_service_session_id("tenant-a", "research", "actor-b", "same-key")

    assert first != second
    assert first != other_actor
    assert _agent_session_execution_idempotency_key(first, "same-key") != (
        _agent_session_execution_idempotency_key(second, "same-key")
    )
    assert _agent_session_execution_idempotency_key(first, None) is None


def test_session_admission_buckets_share_envelope_hard_concurrency_ceiling() -> None:
    from types import SimpleNamespace

    from amesh.app import _agent_session_admission_limits

    envelope = SimpleNamespace(
        hard_limits=AgentHardLimits(
            maxTotalTokens=1000,
            maxCostUsd="1",
            maxDurationSeconds=60,
            maxToolCalls=10,
            maxTurns=4,
            maxLoopIterations=4,
            maxRecursionDepth=1,
            maxConcurrency=3,
        ),
        model_routes=(
            ModelRoute(
                routeId="primary",
                provider=ModelProviderSpec(
                    adapter="openrouter",
                    revision="v1",
                    endpoint="https://example.test/v1",
                    credentialRef="openrouter",
                ),
                model="deepseek",
            ),
        ),
    )

    limits, providers = _agent_session_admission_limits(envelope)
    assert [limit.scope.value for limit in limits] == ["FLOW", "KEY", "KEY"]
    assert {limit.limit for limit in limits} == {3}
    assert limits[1].key == "{{ trigger.ameshActorId }}"
    assert limits[2].key == "{{ trigger.ameshProviderId }}"
    assert providers == ("openrouter:v1",)


def test_materialized_control_projection_keeps_pins_and_authoritative_budget() -> None:
    from types import SimpleNamespace

    from amesh.app import _control_agent_session_summary

    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=uuid4(),
        tenant_id="default",
        state=ExecutionState.RUNNING,
        epoch=2,
        version=7,
        namespace="research",
        flow_id="agent_session_stable",
        created_at=now,
        updated_at=now,
        trigger={"ameshBudget": {"maxTotalTokens": 100, "maxConcurrency": 2}},
    )
    summary = SimpleNamespace(
        tenant_id="default",
        namespace="research",
        execution_id=execution.execution_id,
        task_run_id=uuid4(),
        attempt=1,
        capability_pin_id=uuid4(),
        envelope_digest="sha256:" + "a" * 64,
        agent_ref=None,
        model_profile=None,
        harness=None,
        state=AgentSessionState.RUNNING,
        phase=AgentSessionPhase.MODEL,
        created_at=now,
        updated_at=now,
        completed_at=None,
        counters=None,
        final_result=None,
        error=None,
    )

    projected = _control_agent_session_summary(
        uuid4(), execution, summary, agent_ref="research/analyst@7"
    )

    assert projected.execution_id == execution.execution_id
    assert projected.task_run_id == summary.task_run_id
    assert projected.capability_pin_id == summary.capability_pin_id
    assert projected.envelope_digest == summary.envelope_digest
    assert projected.budgets == execution.trigger["ameshBudget"]


def test_harness_catalog_contains_provenance_only() -> None:
    catalog = {
        alias: AgentSessionHarnessCatalogEntry.model_validate(metadata)
        for alias, metadata in AGENT_SESSION_HARNESS_REGISTRY.items()
    }

    assert catalog
    for entry in catalog.values():
        assert entry.adapter and entry.adapter_version and entry.protocol
        assert "command" not in entry.model_dump()
        assert "credentials" not in entry.model_dump()


def test_app_exposes_reconnectable_session_routes() -> None:
    from amesh.app import app

    paths = {
        (route.path, tuple(sorted(getattr(route, "methods", ()) or ())))
        for route in app.routes
        if hasattr(route, "path")
    }
    assert ("/api/v1/agent-sessions/{service_session_id}/progress", ("GET",)) in paths
    assert (
        "/api/v1/agent-sessions/{service_session_id}/progress/stream",
        ("GET",),
    ) in paths
    assert ("/api/v1/agent-sessions/{service_session_id}/events/stream", ("GET",)) in paths
    assert ("/api/v1/agent-sessions/{service_session_id}/messages", ("POST",)) in paths


def test_openai_http_rejects_unpinned_tuning_with_openai_error_envelope() -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: lambda: object(),
            get_repository: lambda: object(),
            get_task_cache_repository: lambda: object(),
            get_shared_resource_repository: lambda: object(),
            get_operational_control_repository: lambda: object(),
            get_agent_session_repository: lambda: object(),
            get_agent_resource_repository: lambda: object(),
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                "/v1/chat/completions",
                headers={"X-Amesh-Tenant": "default"},
                json={
                    "model": "research/analyst@7",
                    "messages": [{"role": "user", "content": "hello"}],
                    "temperature": 0.2,
                },
            )
        assert response.status_code == 422
        assert response.json()["error"]["type"] == "invalid_request_error"
        assert "temperature" in response.json()["error"]["message"]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_openai_inline_images_are_content_addressed_and_cleared_before_launch() -> None:
    content = b"inline-image-fixture"
    checksum = hashlib.sha256(content).hexdigest()
    path = f"openai-inputs/{checksum}"
    image = ImageArtifactRef(
        artifact=ArtifactRef(
            reference=build_artifact_reference(path, 1, checksum),
            contentAddress=f"sha256:{checksum}",
            tenantId="default",
            namespace="research",
            path=path,
            version=1,
            mediaType="image/png",
            sizeBytes=len(content),
            checksumSha256=checksum,
            provenance=ArtifactProvenance(
                source="namespace-file",
                originNamespace="research",
                createdBy="user:test",
                createdAt=datetime(2026, 8, 31, tzinfo=UTC),
            ),
            retention=ArtifactRetention(),
        ),
        display=ImageDisplayMetadata(
            filename=checksum,
            widthPixels=1,
            heightPixels=1,
        ),
    )

    class Service:
        def __init__(self) -> None:
            self.current: ImageArtifactRef | None = None
            self.upload_count = 0

        async def get_image_artifact(
            self,
            namespace: str,
            requested_path: str,
            **kwargs: object,
        ) -> ImageArtifactRef:
            assert namespace == "research" and requested_path == path
            assert kwargs == {"tenant_id": "default", "actor_id": "user:test"}
            if self.current is None:
                raise LookupError("not staged")
            return self.current

        async def upload_image(
            self,
            namespace: str,
            requested_path: str,
            supplied: bytes,
            **kwargs: object,
        ) -> ImageArtifactRef:
            assert namespace == "research" and requested_path == path
            assert supplied == content
            assert kwargs == {
                "tenant_id": "default",
                "actor_id": "user:test",
                "content_type": "image/png",
                "expected_version": 0,
            }
            self.upload_count += 1
            self.current = image
            return image

    request = CanonicalSessionRequest(
        profile="research/vision@1",
        messages=(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Compare these."},
                    {"type": "inline_image_upload", "uploadId": "inline-image-0000"},
                    {"type": "text", "text": "Then check again."},
                    {"type": "inline_image_upload", "uploadId": "inline-image-0001"},
                ],
            },
        ),
        inline_images=(
            CanonicalInlineImageUpload(
                upload_id="inline-image-0000",
                media_type="image/png",
                content=content,
            ),
            CanonicalInlineImageUpload(
                upload_id="inline-image-0001",
                media_type="image/png",
                content=content,
            ),
        ),
    )
    service = Service()

    staged = asyncio.run(
        _stage_openai_session_images(
            request,
            service,  # type: ignore[arg-type]
            tenant_id="default",
            namespace="research",
            actor_id="user:test",
        )
    )

    assert service.upload_count == 1
    assert staged.inline_images == ()
    parts = staged.messages[0]["content"]
    assert [part["type"] for part in parts] == [
        "text",
        "image_ref",
        "text",
        "image_ref",
    ]
    assert parts[1]["image"]["artifact"]["checksumSha256"] == checksum
    assert parts[3]["image"]["artifact"]["checksumSha256"] == checksum
    persisted = staged.model_dump_json(by_alias=True)
    assert "inline-image-fixture" not in persisted
    assert "inline_image_upload" not in persisted


def test_follow_up_message_is_image_governed_exactly_pinned_and_idempotent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    from fastapi import BackgroundTasks, Response

    from amesh.api.models import AgentSessionMessageRequest, ExecutionDetail
    from amesh.app import post_agent_session_message
    from amesh.domain import (
        AgentSessionCheckpoint,
        AgentSessionCounters,
        AgentSessionDetail,
        AgentSessionRecord,
    )
    from amesh.dsl import FlowDefinition

    service_session_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="session-client"
    )
    source_execution_id = uuid4()
    source_task_run_id = uuid4()
    pin_id = uuid4()
    envelope_digest = "sha256:" + "b" * 64
    now = datetime.now(UTC)
    source_execution = PersistedExecution(
        execution_id=source_execution_id,
        tenant_id="default",
        state=ExecutionState.SUCCESS,
        epoch=1,
        version=4,
        namespace="research",
        flow_id="agent_session_pinned",
        flow_revision=1,
        created_at=now,
        updated_at=now,
        trigger={
            "ameshAgentSessionId": str(service_session_id),
            "ameshAgentSessionTurn": 1,
            "ameshAgentSessionAttemptBase": 0,
            "ameshAgentRef": "research/vision@7",
            "ameshActorId": str(actor.principal_id),
            "ameshHarness": {
                "adapter": "pi-agent-core",
                "adapterVersion": "0.84.3",
                "protocol": "amesh-agent-session-v1",
            },
        },
    )
    source_flow = FlowDefinition.model_validate(
        {
            "id": "agent_session_pinned",
            "namespace": "research",
            "revision": 1,
            "tasks": [
                {
                    "id": "agent",
                    "type": "agent.session",
                    "agent": "vision",
                    "agentRevision": 7,
                    "input": {"question": "first"},
                }
            ],
        }
    )
    source_session = AgentSessionRecord(
        tenantId="default",
        namespace="research",
        executionId=source_execution_id,
        taskRunId=source_task_run_id,
        attempt=1,
        capabilityPinId=pin_id,
        envelopeDigest=envelope_digest,
        state=AgentSessionState.SUCCEEDED,
        phase=AgentSessionPhase.COMPLETE,
        checkpoint=AgentSessionCheckpoint(
            messages=(
                {"role": "system", "content": "Pinned"},
                {"role": "user", "content": "First"},
                {"role": "assistant", "content": '{"action":"final"}'},
            ),
            nextTurn=2,
        ),
        counters=AgentSessionCounters(turns=1, totalTokens=5, costUsd="0.001"),
        finalResult={"answer": "first"},
    )
    image_content = b"governed-image"
    checksum = hashlib.sha256(image_content).hexdigest()
    image = ImageArtifactRef(
        artifact=ArtifactRef(
            reference=build_artifact_reference("images/later.png", 3, checksum),
            contentAddress=f"sha256:{checksum}",
            tenantId="default",
            namespace="research-assets",
            path="images/later.png",
            version=3,
            mediaType="image/png",
            sizeBytes=len(image_content),
            checksumSha256=checksum,
            provenance=ArtifactProvenance(
                source="namespace-file",
                originNamespace="research-assets",
                createdBy="user:test",
                createdAt=now,
            ),
            retention=ArtifactRetention(),
        ),
        display=ImageDisplayMetadata(
            filename="later.png",
            widthPixels=1,
            heightPixels=1,
        ),
    )
    source_task_run = PersistedTaskRun(
        task_run_id=source_task_run_id,
        execution_id=source_execution_id,
        task_id="agent",
        state=TaskRunState.SUCCESS,
        current_attempt=1,
        version=3,
    )

    class Repository:
        def __init__(self) -> None:
            self.current = source_execution
            self.flow = source_flow
            self.task_run = source_task_run

        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == self.current.execution_id and tenant_id == "default"
            return self.current

        async def get_flow(
            self,
            namespace: str,
            flow_id: str,
            *,
            tenant_id: str,
            revision: int,
        ) -> FlowDefinition:
            assert (namespace, flow_id, tenant_id, revision) == (
                "research",
                "agent_session_pinned",
                "default",
                self.current.flow_revision,
            )
            return self.flow

        async def list_task_runs(
            self, requested: UUID, *, tenant_id: str
        ) -> list[PersistedTaskRun]:
            assert requested == self.current.execution_id and tenant_id == "default"
            return [self.task_run]

    repository = Repository()

    class Sessions:
        def __init__(self) -> None:
            self.current = source_session
            self.events: tuple[AgentSessionEvent, ...] = ()

        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: UUID
        ) -> UUID:
            assert tenant_id == "default" and requested == service_session_id
            return repository.current.execution_id

        async def list_execution_sessions(
            self, tenant_id: str, requested: UUID
        ) -> tuple[AgentSessionRecord, ...]:
            assert tenant_id == "default" and requested == repository.current.execution_id
            return (self.current,)

        async def get_session(
            self, tenant_id: str, task_run_id: UUID, attempt: int
        ) -> AgentSessionDetail:
            assert tenant_id == "default"
            assert (task_run_id, attempt) == (self.current.task_run_id, self.current.attempt)
            return AgentSessionDetail(session=self.current, events=self.events)

    sessions = Sessions()

    class Authorization:
        def __init__(self) -> None:
            self.requests: list[AuthorizationRequest] = []

        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            self.requests.append(request)
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="allowed",
                policy_version=1,
                matched_role_names=("session-client",),
            )

        async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
            return await self.decide(request)

    authorization = Authorization()

    class Resources:
        async def preview_agent(self, *args: object, **kwargs: object) -> object:
            assert args == ("default", "research", "vision")
            assert kwargs == {"agent_revision": 7}
            return SimpleNamespace(
                envelope=SimpleNamespace(
                    input_schema={"type": "object"},
                    model_routes=(
                        SimpleNamespace(route_id="primary", required_features=("image-input",)),
                    ),
                )
            )

    class NamespaceResources:
        def __init__(self) -> None:
            self.resolved: list[ImageArtifactRef] = []

        async def resolve_image(
            self,
            requested: ImageArtifactRef,
            *,
            tenant_id: str,
            actor_id: str,
        ) -> bytes:
            assert tenant_id == "default" and actor_id == str(actor.principal_id)
            assert requested == image
            self.resolved.append(requested)
            return image_content

    namespace_resources = NamespaceResources()
    execute_calls: list[dict[str, object]] = []

    async def fake_execute_flow(*args: object, **kwargs: object) -> ExecutionDetail:
        next_flow = args[2]
        assert isinstance(next_flow, FlowDefinition)
        next_task = next_flow.tasks[0]
        assert next_task.model_extra["agent"] == "vision"
        assert next_task.model_extra["agentRevision"] == 7
        assert next_task.model_extra["input"]["image"]["artifact"]["checksumSha256"] == checksum
        trigger = kwargs["trigger_context"]
        assert isinstance(trigger, dict)
        assert trigger["ameshAgentSessionTurn"] == 2
        assert trigger["ameshAgentSessionAttemptBase"] == 1
        assert trigger["ameshAgentSessionResumeFrom"] == {
            "sessionId": str(source_session.session_id),
            "taskRunId": str(source_task_run_id),
            "attempt": 1,
            "capabilityPinId": str(pin_id),
            "envelopeDigest": envelope_digest,
        }
        execute_calls.append(trigger)
        follow_execution_id = uuid4()
        follow_task_run_id = uuid4()
        repository.current = source_execution.model_copy(
            update={
                "execution_id": follow_execution_id,
                "flow_revision": 2,
                "trigger": trigger,
                "updated_at": datetime.now(UTC),
            }
        )
        repository.flow = next_flow.model_copy(update={"revision": 2})
        repository.task_run = PersistedTaskRun(
            task_run_id=follow_task_run_id,
            execution_id=follow_execution_id,
            task_id="agent",
            state=TaskRunState.SUCCESS,
            current_attempt=1,
            version=3,
        )
        sessions.current = source_session.model_copy(
            update={
                "session_id": uuid4(),
                "execution_id": follow_execution_id,
                "task_run_id": follow_task_run_id,
                "attempt": 2,
                "counters": AgentSessionCounters(
                    turns=2,
                    totalTokens=10,
                    costUsd="0.002",
                ),
                "final_result": {"answer": "second"},
            }
        )
        sessions.events = (
            AgentSessionEvent(
                sessionId=sessions.current.session_id,
                eventIndex=1,
                eventKey="turn:2:completed",
                eventType="output.accepted",
                payload={"result": {"answer": "second"}},
            ),
        )
        return ExecutionDetail(
            execution=repository.current,
            taskRuns=[repository.task_run],
        )

    monkeypatch.setattr("amesh.app._execute_flow", fake_execute_flow)
    request = AgentSessionMessageRequest(
        input={
            "prompt": "Inspect the chart",
            "image": image.model_dump(mode="json", by_alias=True),
        }
    )

    async def scenario() -> None:
        first_response = Response()
        first = await post_agent_session_message(
            service_session_id,
            request,
            BackgroundTasks(),
            first_response,
            repository,  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            sessions,  # type: ignore[arg-type]
            Resources(),  # type: ignore[arg-type]
            namespace_resources,  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            actor,
            authorization,  # type: ignore[arg-type]
            "default",
            None,
            "message-2",
            "correlation-2",
        )
        duplicate_response = Response()
        duplicate = await post_agent_session_message(
            service_session_id,
            request,
            BackgroundTasks(),
            duplicate_response,
            repository,  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            sessions,  # type: ignore[arg-type]
            Resources(),  # type: ignore[arg-type]
            namespace_resources,  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            actor,
            authorization,  # type: ignore[arg-type]
            "default",
            None,
            "message-2",
            "correlation-2",
        )

        assert first.execution_id == duplicate.execution_id == repository.current.execution_id
        assert first.session is not None and first.session.final_result == {"answer": "second"}
        assert duplicate.session is not None
        assert len(execute_calls) == 1
        assert namespace_resources.resolved == [image]
        assert first_response.headers["location"].endswith(str(service_session_id))
        assert first_response.headers["x-correlation-id"] == "correlation-2"
        assert [item.action for item in authorization.requests[:3]] == [
            PermissionAction.VIEW,
            PermissionAction.CREATE,
            PermissionAction.READ,
        ]

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        (
            "/v1/chat/completions",
            {
                "model": "research/analyst@not-a-revision",
                "messages": [{"role": "user", "content": "hello"}],
            },
        ),
        (
            "/v1/responses",
            {"model": "research/analyst@not-a-revision", "input": "hello"},
        ),
    ],
)
def test_openai_http_rejects_malformed_agent_revision_with_typed_error(
    path: str,
    payload: dict[str, object],
) -> None:
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: lambda: object(),
            get_repository: lambda: object(),
            get_task_cache_repository: lambda: object(),
            get_shared_resource_repository: lambda: object(),
            get_operational_control_repository: lambda: object(),
            get_agent_session_repository: lambda: object(),
            get_agent_resource_repository: lambda: object(),
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                path,
                headers={"X-Amesh-Tenant": "default"},
                json=payload,
            )
        assert response.status_code == 422, response.text
        assert response.json()["error"]["type"] == "invalid_request_error"
        assert "<namespace>/<key>@<revision>" in response.json()["error"]["message"]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_openai_http_routes_forward_authority_context_and_render_success_shapes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from amesh.adapters.openai_session import CanonicalSessionResult
    from amesh.app import _ApplicationSessionFacade

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    calls: list[dict[str, object]] = []

    async def fake_complete(
        self: object,
        request: object,
        *,
        tenant_id: str,
        namespace: str,
        actor_id: str,
        idempotency_key: str | None,
    ) -> CanonicalSessionResult:
        del self
        calls.append(
            {
                "request": request,
                "tenant_id": tenant_id,
                "namespace": namespace,
                "actor_id": actor_id,
                "idempotency_key": idempotency_key,
            }
        )
        return CanonicalSessionResult(
            sessionId=uuid4(),
            profile=request.profile,
            content="hello from AMESH",
            created=123,
            usage={"inputTokens": 2, "outputTokens": 3, "totalTokens": 5},
        )

    monkeypatch.setattr(_ApplicationSessionFacade, "complete", fake_complete)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "tenant-a",
            get_authorization_service: lambda: object(),
            get_repository: lambda: object(),
            get_task_cache_repository: lambda: object(),
            get_shared_resource_repository: lambda: object(),
            get_operational_control_repository: lambda: object(),
            get_agent_session_repository: lambda: object(),
            get_agent_resource_repository: lambda: object(),
        }
    )

    async def scenario() -> None:
        headers = {
            "X-Amesh-Tenant": "tenant-a",
            "Idempotency-Key": "request-1",
        }
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            chat = await client.post(
                "/v1/chat/completions",
                headers=headers,
                json={
                    "model": "research/analyst@7",
                    "messages": [{"role": "user", "content": "hello"}],
                },
            )
            chat_stream = await client.post(
                "/v1/chat/completions",
                headers=headers,
                json={
                    "model": "research/analyst@7",
                    "messages": [{"role": "user", "content": "hello"}],
                    "stream": True,
                },
            )
            responses = await client.post(
                "/v1/responses",
                headers=headers,
                json={"model": "research/analyst@7", "input": "hello"},
            )
            responses_stream = await client.post(
                "/v1/responses",
                headers=headers,
                json={"model": "research/analyst@7", "input": "hello", "stream": True},
            )

        assert chat.status_code == 200, chat.text
        assert chat.json()["choices"][0]["message"]["content"] == "hello from AMESH"
        assert chat.json()["usage"] == {
            "prompt_tokens": 2,
            "completion_tokens": 3,
            "total_tokens": 5,
        }
        assert chat_stream.status_code == 200, chat_stream.text
        assert "data: [DONE]" in chat_stream.text
        assert responses.status_code == 200, responses.text
        assert responses.json()["status"] == "completed"
        assert responses.json()["output_text"] == "hello from AMESH"
        assert responses.json()["usage"] == {
            "input_tokens": 2,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens": 3,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 5,
        }
        assert responses_stream.status_code == 200, responses_stream.text
        assert "event: response.completed" in responses_stream.text
        assert len(calls) == 4
        assert all(call["tenant_id"] == "tenant-a" for call in calls)
        assert all(call["namespace"] == "research" for call in calls)
        assert all(call["actor_id"] == str(actor.principal_id) for call in calls)
        assert all(call["idempotency_key"] == "request-1" for call in calls)

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        (
            "/v1/chat/completions",
            {
                "model": "research/analyst@7",
                "messages": [{"role": "user", "content": "hello"}],
            },
        ),
        (
            "/v1/responses",
            {"model": "research/analyst@7", "input": "hello"},
        ),
    ],
)
@pytest.mark.parametrize("execution_state", [ExecutionState.QUEUED, ExecutionState.RUNNING])
def test_openai_http_returns_retriable_error_for_accepted_incomplete_session(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    payload: dict[str, object],
    execution_state: ExecutionState,
) -> None:
    from amesh import app as app_module

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    service_id = uuid4()

    async def fake_launch(*args: object, **kwargs: object) -> AgentSessionLaunchResponse:
        del args, kwargs
        return AgentSessionLaunchResponse(
            sessionId=service_id,
            executionId=uuid4(),
            taskRunId=uuid4(),
            executionState=execution_state,
        )

    monkeypatch.setattr(app_module, "_launch_agent_session", fake_launch)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: lambda: object(),
            get_repository: lambda: object(),
            get_task_cache_repository: lambda: object(),
            get_shared_resource_repository: lambda: object(),
            get_operational_control_repository: lambda: object(),
            get_agent_session_repository: lambda: object(),
            get_agent_resource_repository: lambda: object(),
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                path,
                headers={"X-Amesh-Tenant": "default", "Idempotency-Key": "queued-request"},
                json=payload,
            )
        assert response.status_code == 503, response.text
        assert response.headers["location"] == f"/api/v1/agent-sessions/{service_id}"
        assert response.headers["retry-after"] == "1"
        assert response.json()["error"]["type"] == "server_error"
        assert str(service_id) in response.json()["error"]["message"]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_durable_usage_aggregates_normalized_response_events() -> None:
    from amesh.app import _durable_usage

    events = (
        AgentSessionEvent(
            sessionId=uuid4(),
            eventIndex=1,
            eventKey="model-1",
            eventType="model.response",
            payload={"usageNormalized": {"inputTokens": 2, "outputTokens": 3, "totalTokens": 5}},
        ),
        AgentSessionEvent(
            sessionId=uuid4(),
            eventIndex=2,
            eventKey="model-2",
            eventType="model.response",
            payload={"usageNormalized": {"inputTokens": 4, "outputTokens": 1, "totalTokens": 5}},
        ),
    )

    assert _durable_usage(events) == {
        "inputTokens": 6,
        "outputTokens": 4,
        "totalTokens": 10,
    }


def test_queued_service_session_is_observable_before_attempt_row_exists() -> None:
    execution_id = uuid4()
    service_id = uuid4()
    now = datetime.now(UTC)

    class Repository:
        async def get_execution(self, requested: object, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution_id and tenant_id == "default"
            return PersistedExecution(
                execution_id=execution_id,
                tenant_id=tenant_id,
                state=ExecutionState.QUEUED,
                epoch=1,
                version=3,
                namespace="research",
                flow_id="agent_session_stable",
                created_at=now,
                updated_at=now,
                trigger={
                    "ameshAgentSessionId": str(service_id),
                    "ameshAgentRef": "research/analyst@7",
                },
            )

    class Sessions:
        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: object
        ) -> UUID:
            assert tenant_id == "default" and requested == service_id
            return execution_id

        async def list_execution_sessions(
            self, tenant_id: str, requested: UUID
        ) -> tuple[object, ...]:
            assert tenant_id == "default" and requested == execution_id
            return ()

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            assert request.resource_type == "agent_session"
            assert request.action is PermissionAction.LIST
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="test",
                policy_version=1,
                matched_role_names=("session-operator",),
            )

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_id}",
                headers={"X-Amesh-Tenant": "default"},
            )
            events = await client.get(
                f"/api/v1/agent-sessions/{service_id}/events",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert response.json()["session"]["state"] == "QUEUED"
        assert response.json()["session"]["agentRef"] == "research/analyst@7"
        assert events.status_code == 200, events.text
        assert events.json()["events"] == []

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("method", "suffix", "body"),
    [
        ("GET", "", None),
        ("GET", "/events", None),
        ("GET", "/messages", None),
        ("GET", "/events/stream", None),
        ("GET", "/result", None),
        ("POST", "/messages", {}),
        ("POST", "/cancel", {"reason": "stop"}),
    ],
)
def test_unknown_service_session_routes_return_typed_not_found(
    method: str,
    suffix: str,
    body: dict[str, object] | None,
) -> None:
    service_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )

    class Sessions:
        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: UUID
        ) -> UUID:
            assert tenant_id == "default" and requested == service_id
            raise LookupError("missing")

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: lambda: object(),
            get_repository: lambda: object(),
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.request(
                method,
                f"/api/v1/agent-sessions/{service_id}{suffix}",
                headers={"X-Amesh-Tenant": "default"},
                json=body,
            )
        assert response.status_code == 404, response.text
        assert response.json()["code"] == "HTTP_404"
        assert response.json()["detail"] == "agent session does not exist"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_service_session_list_filters_namespaces_without_view_access() -> None:
    allowed_id = uuid4()
    denied_id = uuid4()
    now = datetime.now(UTC)
    executions = {
        allowed_id: PersistedExecution(
            execution_id=allowed_id,
            tenant_id="default",
            state=ExecutionState.QUEUED,
            epoch=1,
            version=1,
            namespace="allowed",
            flow_id="agent_session_allowed",
            created_at=now,
            updated_at=now,
            trigger={"ameshAgentRef": "allowed/agent@1"},
        ),
        denied_id: PersistedExecution(
            execution_id=denied_id,
            tenant_id="default",
            state=ExecutionState.QUEUED,
            epoch=1,
            version=1,
            namespace="secret",
            flow_id="agent_session_secret",
            created_at=now,
            updated_at=now,
            trigger={"ameshAgentRef": "secret/agent@1"},
        ),
    }

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert tenant_id == "default"
            return executions[requested]

    class Sessions:
        async def list_service_sessions(
            self, tenant_id: str, *, limit: int, owner_id: str | None
        ) -> tuple[tuple[UUID, UUID, str, None], ...]:
            assert tenant_id == "default" and limit == 100 and owner_id == str(actor.principal_id)
            return (
                (allowed_id, allowed_id, "allowed/agent@1", None),
                (denied_id, denied_id, "secret/agent@1", None),
            )

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            allowed = request.namespace == "allowed"
            if request.resource_type == "execution":
                allowed = False
            return AuthorizationDecision(
                allowed=allowed,
                reason_code="ROLE_GRANT" if allowed else "NO_MATCHING_GRANT",
                summary="namespace test",
                policy_version=1,
                matched_role_names=("session-operator",),
            )

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                "/api/v1/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert [item["sessionId"] for item in response.json()] == [str(allowed_id)]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_non_owner_service_session_requires_manage_access_for_list_visibility() -> None:
    execution_id = uuid4()
    service_id = uuid4()
    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=execution_id,
        tenant_id="default",
        state=ExecutionState.QUEUED,
        epoch=1,
        version=1,
        namespace="research",
        flow_id="agent_session_research",
        created_at=now,
        updated_at=now,
        trigger={
            "ameshAgentRef": "research/agent@1",
            "ameshActorId": str(uuid4()),
        },
    )

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def list_service_sessions(
            self, tenant_id: str, *, limit: int, owner_id: str | None
        ) -> tuple[tuple[UUID, UUID, str, None], ...]:
            assert tenant_id == "default" and limit == 100 and owner_id == str(actor.principal_id)
            return ((service_id, execution_id, "research/agent@1", None),)

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            allowed = request.resource_type == "agent_session" and request.action.value == "view"
            return AuthorizationDecision(
                allowed=allowed,
                reason_code="ROLE_GRANT" if allowed else "EXPLICIT_DENY",
                summary="owner boundary test",
                policy_version=1,
                matched_role_names=("session-client",),
            )

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                "/api/v1/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert response.json() == []

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_session_event_stream_uses_namespace_authorization_before_yielding() -> None:
    execution_id = uuid4()
    service_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=execution_id,
        tenant_id="default",
        state=ExecutionState.SUCCESS,
        epoch=1,
        version=1,
        namespace="research",
        flow_id="agent_session_research",
        created_at=now,
        updated_at=now,
        trigger={
            "ameshAgentRef": "research/agent@1",
            "ameshActorId": str(actor.principal_id),
        },
    )

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: UUID
        ) -> UUID:
            assert tenant_id == "default" and requested == service_id
            return execution_id

        async def list_execution_sessions(
            self, tenant_id: str, requested: UUID
        ) -> tuple[object, ...]:
            assert tenant_id == "default" and requested == execution_id
            return ()

    class NamespaceOnlyAuthorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            assert request.namespace == "research"
            assert request.resource_type == "agent_session"
            assert request.action is PermissionAction.VIEW
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="namespace-only test",
                policy_version=1,
                matched_role_names=("namespace-viewer",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: NamespaceOnlyAuthorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_id}/events/stream",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert "heartbeat" in response.text

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_session_event_stream_denies_namespace_before_response_bytes() -> None:
    execution_id = uuid4()
    service_id = uuid4()
    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )
    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=execution_id,
        tenant_id="default",
        state=ExecutionState.RUNNING,
        epoch=1,
        version=1,
        namespace="restricted",
        flow_id="agent_session_restricted",
        created_at=now,
        updated_at=now,
        trigger={"ameshActorId": str(actor.principal_id)},
    )

    class Repository:
        async def get_execution(self, requested: UUID, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution_id and tenant_id == "default"
            return execution

    class Sessions:
        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: UUID
        ) -> UUID:
            assert tenant_id == "default" and requested == service_id
            return execution_id

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            assert request.namespace == "restricted"
            assert request.resource_type == "agent_session"
            return AuthorizationDecision(
                allowed=False,
                reason_code="EXPLICIT_DENY",
                summary="restricted namespace",
                policy_version=1,
                matched_role_names=("viewer",),
            )

    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.get(
                f"/api/v1/agent-sessions/{service_id}/events/stream",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 403, response.text
        assert response.json()["detail"] == "not authorized"
        assert "heartbeat" not in response.text

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_queued_service_session_cancel_returns_control_result_before_attempt_session_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace

    execution_id = uuid4()
    service_id = uuid4()
    task_run_id = uuid4()
    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=execution_id,
        tenant_id="default",
        state=ExecutionState.QUEUED,
        epoch=1,
        version=3,
        namespace="research",
        flow_id="agent_session_stable",
        created_at=now,
        updated_at=now,
        trigger={
            "ameshAgentSessionId": str(service_id),
            "ameshAgentRef": "research/analyst@7",
        },
    )

    class Repository:
        async def get_execution(self, requested: object, *, tenant_id: str) -> PersistedExecution:
            assert requested == execution_id and tenant_id == "default"
            return execution

        async def list_task_runs(
            self, requested: object, *, tenant_id: str
        ) -> list[PersistedTaskRun]:
            assert requested == execution_id and tenant_id == "default"
            return [
                PersistedTaskRun(
                    task_run_id=task_run_id,
                    execution_id=execution_id,
                    task_id="agent",
                    state=TaskRunState.WAITING,
                    current_attempt=0,
                    version=0,
                )
            ]

    class Sessions:
        async def get_execution_by_service_session_id(
            self, tenant_id: str, requested: object
        ) -> UUID:
            assert tenant_id == "default" and requested == service_id
            return execution_id

        async def list_execution_sessions(
            self, tenant_id: str, requested: UUID
        ) -> tuple[object, ...]:
            assert tenant_id == "default" and requested == execution_id
            return ()

    actor = ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="operator"
    )

    async def fake_apply(
        requested: UUID,
        request: object,
        repository: object,
        actor_context: object,
        tenant_id: str,
    ) -> object:
        del request, repository, actor_context
        assert requested == execution_id and tenant_id == "default"
        return SimpleNamespace(
            execution=execution.model_copy(
                update={"state": ExecutionState.CANCELLING, "version": 4}
            )
        )

    class Authorization:
        async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
            assert request.resource_type == "agent_session"
            assert request.action is PermissionAction.MANAGE
            return AuthorizationDecision(
                allowed=True,
                reason_code="ROLE_GRANT",
                summary="session control",
                policy_version=1,
                matched_role_names=("session-operator",),
            )

    monkeypatch.setattr("amesh.app._apply_execution_control_authorized", fake_apply)
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: actor,
            require_tenant_context: lambda: "default",
            get_authorization_service: Authorization,
            get_repository: Repository,
            get_agent_session_repository: Sessions,
        }
    )

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                f"/api/v1/agent-sessions/{service_id}/cancel",
                headers={"X-Amesh-Tenant": "default"},
                json={"reason": "stop queued run"},
            )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["executionState"] == "CANCELLING"
        assert payload["taskRunId"] == str(task_run_id)
        assert response.headers["location"].endswith(f"/agent-sessions/{service_id}")

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
