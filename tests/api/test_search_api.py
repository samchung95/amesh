from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_search_repository,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PermissionAction,
    PrincipalType,
    SearchDocument,
    SearchDocumentType,
    SearchProjectionCondition,
    SearchProjectionStatus,
    SearchProjectionVerification,
    SearchProjectionVerificationItem,
    SearchRequest,
    SearchResponse,
)
from amesh.ports import SearchUnavailableError


class SearchAuthorizationStub:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        allowed = (request.resource_type, request.action) in {
            ("search", PermissionAction.VIEW),
            ("search", PermissionAction.MANAGE),
            ("flow", PermissionAction.VIEW),
            ("execution", PermissionAction.VIEW),
        }
        return AuthorizationDecision(
            allowed=allowed,
            reason_code="allowed" if allowed else "denied",
            summary="search API authorization test",
            policy_version=1,
            matched_role_names=("operator",),
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AssertionError("test attempted to require a denied search permission")
        return decision


class SearchRepositoryStub:
    def __init__(self) -> None:
        self.authorized: tuple[SearchDocumentType, ...] = ()
        self.denied: tuple[SearchDocumentType, ...] = ()
        self.rebuild_reason: str | None = None
        self.rebuild_types: tuple[SearchDocumentType, ...] = ()
        self.enabled = True

    async def search(
        self,
        request: SearchRequest,
        *,
        tenant_id: str,
        authorized_types: tuple[SearchDocumentType, ...],
        denied_types: tuple[SearchDocumentType, ...] = (),
    ) -> SearchResponse:
        del request, tenant_id
        self.authorized = authorized_types
        self.denied = denied_types
        now = datetime(2026, 8, 23, tzinfo=UTC)
        return SearchResponse(
            items=(
                SearchDocument(
                    documentType=SearchDocumentType.FLOW,
                    documentId="flow-1",
                    namespace="team.data",
                    title="team.data.flow",
                    summary="searchable flow",
                    state="ACTIVE",
                    labels={},
                    fields={"flowId": "flow"},
                    occurredAt=now,
                    updatedAt=now,
                    sourceVersion=1,
                    relevance=1.0,
                ),
            ),
            nextCursor=None,
            deniedTypes=denied_types,
            projectionVersion=3,
            projectionCondition=SearchProjectionCondition.READY,
        )

    async def status(self, *, tenant_id: str) -> SearchProjectionStatus:
        del tenant_id
        now = datetime(2026, 8, 23, tzinfo=UTC)
        return SearchProjectionStatus(
            projectionVersion=3,
            condition=SearchProjectionCondition.READY,
            documentsIndexed=10,
            sourceDocuments=10,
            progress=1,
            lastProjectedAt=now,
            latestSourceAt=now,
            lagSeconds=0,
            rebuildStartedAt=None,
            rebuildCompletedAt=now,
            failures=0,
            lastError=None,
        )

    async def request_rebuild(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
        document_types: tuple[SearchDocumentType, ...] = (),
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> SearchProjectionStatus:
        del tenant_id, actor_id, from_time, to_time
        self.rebuild_reason = reason
        self.rebuild_types = document_types
        status = await self.status(tenant_id="default")
        return status.model_copy(update={"condition": SearchProjectionCondition.REBUILDING})

    async def set_enabled(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        enabled: bool,
        reason: str,
    ) -> SearchProjectionStatus:
        del tenant_id, actor_id, reason
        self.enabled = enabled
        status = await self.status(tenant_id="default")
        return status.model_copy(
            update={
                "enabled": enabled,
                "condition": (
                    SearchProjectionCondition.READY
                    if enabled
                    else SearchProjectionCondition.DISABLED
                ),
            }
        )

    async def verify(self, *, tenant_id: str) -> SearchProjectionVerification:
        del tenant_id
        now = datetime(2026, 8, 23, tzinfo=UTC)
        return SearchProjectionVerification(
            projectionVersion=3,
            schemaVersion=2,
            verified=True,
            checksum="verified",
            items=(
                SearchProjectionVerificationItem(
                    documentType=SearchDocumentType.FLOW,
                    sourceCount=1,
                    projectedCount=1,
                    sourceChecksum="same",
                    projectedChecksum="same",
                    lastPosition={"documentId": "flow-1"},
                    verified=True,
                ),
            ),
            verifiedAt=now,
        )


class TenantQuotaStub:
    async def consume_api_request(self, tenant_slug: str) -> int:
        del tenant_slug
        return 1


class UnavailableSearchRepository(SearchRepositoryStub):
    async def search(
        self,
        request: SearchRequest,
        *,
        tenant_id: str,
        authorized_types: tuple[SearchDocumentType, ...],
        denied_types: tuple[SearchDocumentType, ...] = (),
    ) -> SearchResponse:
        del request, tenant_id, authorized_types, denied_types
        raise SearchUnavailableError("search projection unavailable")


def test_search_api_filters_types_by_underlying_permissions_and_controls_rebuild() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="search-operator",
    )
    repository = SearchRepositoryStub()
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = SearchAuthorizationStub
    app.dependency_overrides[get_search_repository] = lambda: repository
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            searched = await client.post(
                "/api/v1/search",
                headers={"X-Amesh-Tenant": "default"},
                json={"query": "flow"},
            )
            assert searched.status_code == 200
            assert searched.json()["items"][0]["documentType"] == "FLOW"
            assert searched.json()["deniedTypes"] == ["ASSET", "AUDIT"]
            assert repository.authorized == (
                SearchDocumentType.FLOW,
                SearchDocumentType.EXECUTION,
                SearchDocumentType.TASK_RUN,
                SearchDocumentType.LOG,
                SearchDocumentType.METRIC,
            )
            assert repository.denied == (
                SearchDocumentType.ASSET,
                SearchDocumentType.AUDIT,
            )

            status = await client.get(
                "/api/v1/search/status",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert status.status_code == 200
            assert status.json()["documentsIndexed"] == 10

            rebuild = await client.post(
                "/api/v1/search/rebuild",
                headers={"X-Amesh-Tenant": "default"},
                json={
                    "reason": "repair projection drift",
                    "types": ["TASK_RUN", "METRIC"],
                    "from": "2026-08-01T00:00:00Z",
                },
            )
            assert rebuild.status_code == 202
            assert rebuild.json()["condition"] == "REBUILDING"
            assert repository.rebuild_reason == "repair projection drift"
            assert repository.rebuild_types == (
                SearchDocumentType.TASK_RUN,
                SearchDocumentType.METRIC,
            )

            verification = await client.get(
                "/api/v1/search/verify",
                headers={"X-Amesh-Tenant": "default"},
            )
            assert verification.status_code == 200
            assert verification.json()["verified"] is True

            disabled = await client.post(
                "/api/v1/search/control",
                headers={"X-Amesh-Tenant": "default"},
                json={"enabled": False, "reason": "exercise authoritative fallback"},
            )
            assert disabled.status_code == 200
            assert disabled.json()["condition"] == "DISABLED"
            assert repository.enabled is False

            invalid = await client.post(
                "/api/v1/search",
                headers={"X-Amesh-Tenant": "default"},
                json={"fields": {"rawSql": "select *"}},
            )
            assert invalid.status_code == 422

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_search_api_reports_projection_unavailability_without_masking_it() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="search-operator",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = SearchAuthorizationStub
    app.dependency_overrides[get_search_repository] = UnavailableSearchRepository
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            response = await client.post(
                "/api/v1/search",
                headers={"X-Amesh-Tenant": "default"},
                json={"query": "anything"},
            )
        assert response.status_code == 503
        assert response.json()["detail"] == "search projection unavailable"

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
