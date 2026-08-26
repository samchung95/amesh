from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_evidence_bundle_repository,
    get_metadata_repository,
    get_operational_control_repository,
    get_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    OperationalBoundary,
    OperationalControlDecision,
    PermissionAction,
    PrincipalType,
    RunningWorkPolicy,
)
from amesh.evidence_bundle import EvidenceBundle, EvidencePage, EvidenceRecord


class _Authorization:
    def __init__(self) -> None:
        self.allow = True
        self.requests: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.requests.append(request)
        decision = AuthorizationDecision(
            allowed=self.allow,
            reason_code="test_allow" if self.allow else "test_deny",
            summary="evidence API fixture",
            policy_version=1,
            matched_role_names=("operator",),
        )
        if not decision.allowed:
            raise AuthorizationDenied(decision)
        return decision


class _TenantQuota:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug == "default"
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


def test_evidence_bundle_api_is_authorized_bounded_redacted_and_tenant_scoped() -> None:
    execution_id = uuid4()
    now = datetime.now(UTC)
    record = EvidenceRecord(
        recordId="event-1",
        kind="log.info",
        sequence=1,
        correlationId=execution_id,
        occurredAt=now,
        payload={"message": "safe", "authorization": "[REDACTED]"},
    )
    bundle = EvidenceBundle(
        executionId=execution_id,
        tenantId="default",
        correlationId=execution_id,
        createdAt=now,
        trace=(record,),
    ).sealed()
    authorization = _Authorization()
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="operator",
    )

    class _Executions:
        async def get_execution(self, requested: object, *, tenant_id: str) -> object:
            assert requested == execution_id
            assert tenant_id == "default"
            return SimpleNamespace(
                execution_id=execution_id,
                created_at=now,
                namespace="tests",
                flow_id="evidence",
                flow_revision=1,
                inputs={},
                outputs={},
            )

    class _Evidence:
        async def get(self, requested: object, *, tenant_id: str) -> EvidenceBundle:
            assert requested == execution_id
            assert tenant_id == "default"
            return bundle

        async def page(
            self,
            requested: object,
            *,
            tenant_id: str,
            section: str,
            cursor: str | None,
            limit: int,
        ) -> EvidencePage[EvidenceRecord]:
            assert (requested, tenant_id, section, cursor, limit) == (
                execution_id,
                "default",
                "trace",
                None,
                1,
            )
            return EvidencePage[EvidenceRecord](items=(record,), nextCursor="1", limit=1, total=2)

    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    app.dependency_overrides[get_repository] = _Executions
    app.dependency_overrides[get_metadata_repository] = lambda: object()
    app.dependency_overrides[get_evidence_bundle_repository] = _Evidence
    app.dependency_overrides[get_tenant_service] = _TenantQuota
    app.dependency_overrides[get_operational_control_repository] = _Controls

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://amesh.test",
        ) as client:
            response = await client.get(
                f"/api/v1/executions/{execution_id}/evidence-bundle",
                headers={"X-Amesh-Tenant": "default"},
                params={"section": "trace", "limit": 1},
            )
            assert response.status_code == 200, response.text
            assert response.json()["nextCursor"] == "1"
            assert response.json()["items"][0]["payload"]["authorization"] == "[REDACTED]"

            authorization.allow = False
            denied = await client.get(
                f"/api/v1/executions/{execution_id}/evidence-bundle",
                headers={"X-Amesh-Tenant": "default"},
                params={"limit": 1},
            )
            assert denied.status_code == 403

    try:
        asyncio.run(scenario())
        assert authorization.requests[0].action is PermissionAction.VIEW
        assert authorization.requests[0].namespace == "tests"
    finally:
        app.dependency_overrides.clear()
