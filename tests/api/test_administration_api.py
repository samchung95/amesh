from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx
from pydantic import SecretStr
from tests.fixtures.api_stubs import TenantQuotaStub

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_feature_flag_repository,
    get_tenant_service,
)
from amesh.config import Settings, get_settings
from amesh.domain import (
    ActorContext,
    AdministrationAuditEntry,
    AuthorizationDecision,
    AuthorizationRequest,
    FeatureFlag,
    PermissionAction,
    PrincipalType,
)


class AdministrationAuthorizationStub:
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision:
        allowed = (request.resource_type, request.action) in {
            ("configuration", PermissionAction.VIEW),
            ("configuration", PermissionAction.MANAGE),
            ("audit", PermissionAction.VIEW),
        }
        return AuthorizationDecision(
            allowed=allowed,
            reason_code="allowed" if allowed else "denied",
            summary="administration API test",
            policy_version=1,
        )

    async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
        decision = await self.decide(request)
        if not decision.allowed:
            raise AssertionError("test attempted a denied administration operation")
        return decision


class AdministrationFeatureFlagStub:
    def __init__(self) -> None:
        self.flags: tuple[FeatureFlag, ...] = ()
        self.audit: list[AdministrationAuditEntry] = []

    async def list_for_context(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
    ) -> tuple[FeatureFlag, ...]:
        del tenant_id, namespace
        return self.flags

    async def upsert(
        self,
        flag: FeatureFlag,
        *,
        actor_id: str,
        expected_version: int | None = None,
        administration_audit: dict[str, object] | None = None,
    ) -> FeatureFlag:
        del expected_version
        persisted = flag.model_copy(update={"version": 1})
        self.flags = (persisted,)
        assert administration_audit is not None
        evidence = administration_audit["evidence"]
        assert isinstance(evidence, dict)
        self.audit.append(
            AdministrationAuditEntry(
                eventId=str(uuid4()),
                actorId=actor_id,
                action=str(administration_audit["action"]),
                resourceId=str(administration_audit["resourceId"]),
                outcome="SUCCESS",
                reason=str(administration_audit["reason"]),
                evidence=evidence,
                occurredAt=datetime.now(UTC),
            )
        )
        return persisted

    async def audit_administration_action(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        action: str,
        resource_id: str,
        outcome: str,
        reason: str,
        evidence: dict[str, object],
    ) -> None:
        del tenant_id
        self.audit.append(
            AdministrationAuditEntry(
                eventId=str(uuid4()),
                actorId=actor_id,
                action=action,
                resourceId=resource_id,
                outcome=outcome,
                reason=reason,
                evidence=evidence,
                occurredAt=datetime.now(UTC),
            )
        )

    async def list_administration_audit(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[AdministrationAuditEntry, ...]:
        del tenant_id
        return tuple(reversed(self.audit[-limit:]))


def test_administration_control_preview_apply_rejection_and_audit_contract() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="tenant-admin",
    )
    repository = AdministrationFeatureFlagStub()
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = AdministrationAuthorizationStub
    app.dependency_overrides[get_feature_flag_repository] = lambda: repository
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub
    app.dependency_overrides[get_settings] = lambda: Settings(
        amesh_token_pepper=SecretStr("administration-api-test-key"),
    )

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        headers = {"X-Amesh-Tenant": "default"}
        async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
            listed = await client.get("/api/v1/admin/controls", headers=headers)
            assert listed.status_code == 200
            assert listed.json()[0] == {
                "key": "RETENTION",
                "flagKey": "admin-retention-executions",
                "enabled": False,
                "value": 30,
                "version": None,
                "updatedBy": None,
                "updatedAt": None,
            }

            draft = {
                "key": "KILL_SWITCH",
                "enabled": True,
                "value": None,
                "reason": "stop new execution admission",
            }
            preview = await client.post(
                "/api/v1/admin/controls/preview",
                headers=headers,
                json=draft,
            )
            assert preview.status_code == 200
            assert "new execution admission is stopped" in preview.text

            applied = await client.put(
                "/api/v1/admin/controls/KILL_SWITCH",
                headers=headers,
                json={
                    "draft": draft,
                    "approval": preview.json()["approval"],
                    "confirmation": preview.json()["confirmation"],
                },
            )
            assert applied.status_code == 200
            assert applied.json()["enabled"] is True

            rejected = await client.put(
                "/api/v1/admin/controls/KILL_SWITCH",
                headers=headers,
                json={
                    "draft": draft,
                    "approval": preview.json()["approval"],
                    "confirmation": "APPLY SOMETHING_ELSE",
                },
            )
            assert rejected.status_code == 409

            audit = await client.get("/api/v1/admin/audit", headers=headers)
            assert audit.status_code == 200
            assert [item["outcome"] for item in audit.json()] == ["REJECTED", "SUCCESS"]

    try:
        asyncio.run(scenario())
    finally:
        app.dependency_overrides.clear()
