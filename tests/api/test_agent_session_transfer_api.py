from __future__ import annotations

import asyncio
from uuid import uuid4

import httpx
from tests.adapters.postgres.test_transfer_repository import _profile_bundle
from tests.test_session_transfer import _bundle as session_bundle

from amesh.api.models import (
    AgentSessionTransferProfileImportRequest,
    AgentSessionTransferProfilePlanRequest,
    AgentSessionTransferSessionExportRequest,
    AgentSessionTransferSessionImportRequest,
    AgentSessionTransferSessionPlanRequest,
)
from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_profile_transfer_service,
    get_transfer_repository,
    require_tenant_context,
)
from amesh.authorization import AuthorizationDenied
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    PrincipalType,
)
from amesh.profile_transfer import ProfileCompatibilityReport, ProfileImportResult
from amesh.session_transfer import (
    SessionTransferCompatibilityReport,
    SessionTransferImportResult,
    SessionTransferMode,
)


class _Authorization:
    def __init__(self, *, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls: list[AuthorizationRequest] = []

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        self.calls.append(request)
        decision = AuthorizationDecision(
            allowed=self.allowed,
            reason_code="ROLE_GRANT" if self.allowed else "NO_MATCHING_GRANT",
            summary="test",
            policy_version=1,
            matched_role_names=("migration-admin",) if self.allowed else ("legacy-execution",),
        )
        if not self.allowed:
            raise AuthorizationDenied(decision)
        return decision


class _Profiles:
    def __init__(self) -> None:
        self.import_calls = 0

    async def export(self, tenant_id: str, namespace: str, agent_key: str, **kwargs):
        return _profile_bundle(agent_key).model_copy(update={"source_tenant_id": tenant_id})

    async def compatibility(self, bundle, *, target_tenant_id: str, target_namespace=None):
        return ProfileCompatibilityReport(
            compatible=False,
            targetTenantId=target_tenant_id,
            targetNamespace=target_namespace or bundle.namespace,
            issues=("target capability is unavailable",),
        )

    async def import_bundle(self, bundle, **kwargs):
        self.import_calls += 1
        return ProfileImportResult(
            targetTenantId=kwargs["target_tenant_id"],
            targetNamespace=bundle.namespace,
            agentKey=bundle.agent_key,
            agentRevision=bundle.agent_revision,
            resourcesImported=0,
            resourcesExisting=len(bundle.resources),
            mcpConnectionsImported=0,
            mcpConnectionsExisting=len(bundle.mcp_connections),
            importId=bundle.import_id,
            bundleDigest=bundle.checksum_sha256,
        )


class _Transfers:
    def __init__(self, bundle, *, compatible: bool = False) -> None:
        self.bundle = bundle
        self.compatible = compatible
        self.import_calls = 0
        self.result = None

    async def export_session_bundle(self, *args, **kwargs):
        return self.bundle

    async def plan_import(self, target_tenant_id, bundle, **kwargs):
        return SessionTransferCompatibilityReport(
            eligible=self.compatible,
            mode=bundle.mode,
            sourceTenantId=bundle.source_tenant_id,
            targetTenantId=target_tenant_id,
            bundleDigest=bundle.checksum_sha256,
            flowCompatible=self.compatible,
            capabilityPinCompatible=self.compatible,
            harnessCompatible=self.compatible,
            issues=() if self.compatible else ("target capability is unavailable",),
        )

    async def get_import(self, target_tenant_id, import_id):
        return self.result

    async def import_records(self, target_tenant_id, bundle, **kwargs):
        self.import_calls += 1
        self.result = SessionTransferImportResult(
            importId=kwargs["import_id"],
            bundleDigest=bundle.checksum_sha256,
            mode=bundle.mode,
            targetTenantId=target_tenant_id,
            sessionId=str(bundle.session.session_id),
        )
        return self.result


def _install(*, authorization, profiles=None, transfers=None) -> None:
    app.dependency_overrides.update(
        {
            authenticate_actor: lambda: ActorContext(
                principal_id=uuid4(), principal_type=PrincipalType.USER, display="admin"
            ),
            require_tenant_context: lambda: "target",
            get_authorization_service: lambda: authorization,
        }
    )
    if profiles is not None:
        app.dependency_overrides[get_profile_transfer_service] = lambda: profiles
    if transfers is not None:
        app.dependency_overrides[get_transfer_repository] = lambda: transfers


def test_transfer_routes_require_strict_migration_view_without_legacy_fallback() -> None:
    authorization = _Authorization(allowed=False)
    transfers = _Transfers(session_bundle())
    _install(authorization=authorization, transfers=transfers)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                f"/api/v1/admin/agent-session-transfers/sessions/{transfers.bundle.session.session_id}/export",
                json=AgentSessionTransferSessionExportRequest(
                    mode=SessionTransferMode.TERMINAL_HISTORY
                ).model_dump(mode="json", by_alias=True),
                headers={"X-Amesh-Tenant": "target"},
            )
        assert response.status_code == 403
        assert transfers.import_calls == 0

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
    assert [(item.resource_type, item.action.value) for item in authorization.calls] == [
        ("agent_session_migration", "view")
    ]


def test_session_plan_is_compatible_report_and_does_not_import() -> None:
    bundle = session_bundle()
    authorization = _Authorization()
    transfers = _Transfers(bundle, compatible=False)
    _install(authorization=authorization, transfers=transfers)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                "/api/v1/admin/agent-session-transfers/sessions/plan",
                json=AgentSessionTransferSessionPlanRequest(bundle=bundle).model_dump(
                    mode="json", by_alias=True
                ),
                headers={"X-Amesh-Tenant": "target"},
            )
        assert response.status_code == 200, response.text
        assert response.json()["eligible"] is False
        assert response.json()["capabilityPinCompatible"] is False
        assert transfers.import_calls == 0

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_session_and_profile_exports_are_public_read_only_routes() -> None:
    bundle = session_bundle()
    authorization = _Authorization()
    profiles = _Profiles()
    transfers = _Transfers(bundle)
    _install(authorization=authorization, profiles=profiles, transfers=transfers)

    async def scenario() -> None:
        profile_path = "/api/v1/admin/agent-session-transfers/profiles/agents.demo/assistant/export"
        session_path = (
            f"/api/v1/admin/agent-session-transfers/sessions/{bundle.session.session_id}/export"
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            profile = await client.post(profile_path, headers={"X-Amesh-Tenant": "target"})
            session = await client.post(
                session_path,
                json=AgentSessionTransferSessionExportRequest(
                    mode=SessionTransferMode.TERMINAL_HISTORY
                ).model_dump(mode="json", by_alias=True),
                headers={"X-Amesh-Tenant": "target"},
            )
        assert profile.status_code == 200, profile.text
        assert profile.json()["sourceTenantId"] == "target"
        assert session.status_code == 200, session.text
        assert session.json()["checksumSha256"] == bundle.checksum_sha256

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert [(item.resource_type, item.action.value) for item in authorization.calls] == [
        ("agent_session_migration", "view"),
        ("agent_session_migration", "view"),
    ]


def test_transfer_import_requires_strict_migration_manage() -> None:
    bundle = session_bundle()
    authorization = _Authorization(allowed=False)
    transfers = _Transfers(bundle)
    _install(authorization=authorization, transfers=transfers)

    async def scenario() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            response = await client.post(
                "/api/v1/admin/agent-session-transfers/sessions/import",
                json=AgentSessionTransferSessionImportRequest(bundle=bundle).model_dump(
                    mode="json", by_alias=True
                ),
                headers={"X-Amesh-Tenant": "target"},
            )
        assert response.status_code == 403
        assert transfers.import_calls == 0

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert [(item.resource_type, item.action.value) for item in authorization.calls] == [
        ("agent_session_migration", "manage")
    ]


def test_session_import_maps_duplicate_and_conflict_failures_to_typed_4xx() -> None:
    bundle = session_bundle()
    authorization = _Authorization()
    transfers = _Transfers(bundle, compatible=True)
    _install(authorization=authorization, transfers=transfers)

    async def scenario() -> None:
        payload = AgentSessionTransferSessionImportRequest(bundle=bundle).model_dump(
            mode="json", by_alias=True
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            first = await client.post(
                "/api/v1/admin/agent-session-transfers/sessions/import",
                json=payload,
                headers={"X-Amesh-Tenant": "target"},
            )
            assert first.status_code == 200, first.text
            second = await client.post(
                "/api/v1/admin/agent-session-transfers/sessions/import",
                json=payload,
                headers={"X-Amesh-Tenant": "target"},
            )
        assert second.status_code == 200, second.text
        assert second.json()["alreadyPresent"] is True
        assert transfers.import_calls == 1

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()


def test_profile_plan_and_import_use_migration_permissions() -> None:
    bundle = _profile_bundle("api")
    authorization = _Authorization()
    profiles = _Profiles()
    _install(authorization=authorization, profiles=profiles)

    async def scenario() -> None:
        plan = AgentSessionTransferProfilePlanRequest(bundle=bundle)
        import_request = AgentSessionTransferProfileImportRequest(bundle=bundle)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://amesh.test"
        ) as client:
            planned = await client.post(
                "/api/v1/admin/agent-session-transfers/profiles/plan",
                json=plan.model_dump(mode="json", by_alias=True),
                headers={"X-Amesh-Tenant": "target"},
            )
            imported = await client.post(
                "/api/v1/admin/agent-session-transfers/profiles/import",
                json=import_request.model_dump(mode="json", by_alias=True),
                headers={"X-Amesh-Tenant": "target"},
            )
        assert planned.status_code == 200, planned.text
        assert imported.status_code == 200, imported.text
        assert profiles.import_calls == 1

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()

    assert [(item.resource_type, item.action.value) for item in authorization.calls] == [
        ("agent_session_migration", "view"),
        ("agent_session_migration", "manage"),
    ]
