from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_agent_session_repository,
    get_authorization_service,
    get_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AgentSessionDetail,
    AgentSessionEvent,
    AgentSessionRecord,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)


class _Authorization:
    def __init__(self, *, allow: bool = True) -> None:
        self.allow = allow
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        decision = AuthorizationDecision(
            allowed=self.allow,
            reason_code="test_allow" if self.allow else "test_deny",
            summary="agent session fixture",
            policy_version=1,
            matched_role_names=("operator",),
        )
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug
        return 1


class _Executions:
    async def get_execution(self, execution_id: UUID, *, tenant_id: str) -> object:
        assert tenant_id == "default"
        assert execution_id
        return object()


class _Sessions:
    def __init__(
        self,
        record: AgentSessionRecord,
        detail: AgentSessionDetail | None = None,
    ) -> None:
        self.record = record
        self.detail = detail or AgentSessionDetail(session=record, events=())

    async def list_execution_sessions(
        self,
        tenant_id: str,
        execution_id: UUID,
    ) -> tuple[AgentSessionRecord, ...]:
        assert tenant_id == "default"
        assert execution_id == self.record.execution_id
        return (self.record,)

    async def get_session(
        self,
        tenant_id: str,
        task_run_id: UUID,
        attempt: int,
    ) -> AgentSessionDetail:
        assert tenant_id == "default"
        assert task_run_id == self.record.task_run_id
        assert attempt == self.record.attempt
        return self.detail


def test_execution_agent_sessions_are_authorized_and_inspectable() -> None:
    execution_id = uuid4()
    record = AgentSessionRecord(
        tenantId="default",
        namespace="agents.demo",
        executionId=execution_id,
        taskRunId=uuid4(),
        attempt=1,
        capabilityPinId=uuid4(),
        envelopeDigest="sha256:" + "1" * 64,
        createdAt=datetime.now(UTC),
        updatedAt=datetime.now(UTC),
    )
    authorization = _Authorization()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_repository] = _Executions
    app.dependency_overrides[get_agent_session_repository] = lambda: _Sessions(record)
    app.dependency_overrides[get_tenant_service] = _TenantQuota

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/executions/{execution_id}/agent-sessions",
                headers={"X-Amesh-Tenant": "default"},
            )
        assert response.status_code == 200, response.text
        assert response.json()[0]["envelopeDigest"] == record.envelope_digest
        assert response.json()[0]["state"] == "RUNNING"
        assert "checkpoint" not in response.text

    try:
        asyncio.run(scenario())
        assert authorization.requests[0].resource_type == "execution"
    finally:
        app.dependency_overrides.clear()


def test_execution_agent_session_detail_is_bounded_redacted_and_owned() -> None:
    execution_id = uuid4()
    record = AgentSessionRecord(
        tenantId="default",
        namespace="agents.demo",
        executionId=execution_id,
        taskRunId=uuid4(),
        attempt=1,
        capabilityPinId=uuid4(),
        envelopeDigest="sha256:" + "2" * 64,
        createdAt=datetime.now(UTC),
        updatedAt=datetime.now(UTC),
    )
    detail = AgentSessionDetail(
        session=record,
        events=(
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=1,
                eventKey="started",
                eventType="session.started",
                payload={"safe": True},
            ),
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=2,
                eventKey="model",
                eventType="model.response",
                payload={
                    "continuation": {"tokenDigest": "private"},
                    "reasoning": "hidden",
                    "token": "secret",
                    "safe": "visible",
                },
            ),
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=3,
                eventKey="completed",
                eventType="output.accepted",
                payload={"result": {"answer": "safe"}},
            ),
            AgentSessionEvent(
                sessionId=record.session_id,
                eventIndex=4,
                eventKey="large",
                eventType="diagnostic",
                payload={"large": "x" * (64 * 1024 + 1)},
            ),
        ),
    )
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = _Authorization
    app.dependency_overrides[get_repository] = _Executions
    app.dependency_overrides[get_agent_session_repository] = lambda: _Sessions(record, detail)
    app.dependency_overrides[get_tenant_service] = _TenantQuota

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/executions/{execution_id}/agent-sessions/{record.task_run_id}",
                params={"afterEventIndex": 1, "limit": 1},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert response.status_code == 200, response.text
            body = response.json()
            assert body["nextEventIndex"] == 2
            assert body["events"][0]["eventIndex"] == 2
            assert body["events"][0]["payload"] == {
                "safe": "visible",
                "token": "[REDACTED]",
            }
            assert "checkpoint" not in body["session"]
            assert "modelContinuation" not in response.text

            large = await client.get(
                f"/api/v1/executions/{execution_id}/agent-sessions/{record.task_run_id}",
                params={"afterEventIndex": 3},
                headers={"X-Amesh-Tenant": "default"},
            )
            assert large.status_code == 200, large.text
            assert large.json()["events"][0]["payload"]["truncated"] is True
            assert large.json()["nextEventIndex"] is None

            wrong_execution = await client.get(
                f"/api/v1/executions/{uuid4()}/agent-sessions/{record.task_run_id}",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert wrong_execution.status_code == 404

            denied = _Authorization(allow=False)
            app.dependency_overrides[get_authorization_service] = lambda: denied
            forbidden = await client.get(
                f"/api/v1/executions/{execution_id}/agent-sessions/{record.task_run_id}",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert forbidden.status_code == 403
            assert denied.requests[0].resource_type == "execution"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
