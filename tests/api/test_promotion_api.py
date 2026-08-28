from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from amesh.app import (
    app,
    authenticate_actor,
    get_promotion_authorizer,
    get_promotion_service,
    require_tenant_context,
)
from amesh.domain import ActorContext, PrincipalType
from amesh.domain.promotion import (
    PromotionGate,
    PromotionPolicy,
    PromotionTargetKind,
    ReleaseTarget,
)


class FakePromotionService:
    def __init__(self) -> None:
        self.policy = PromotionPolicy(
            tenantId="tenant-a",
            targetKind=PromotionTargetKind.WORKFLOW,
            targetKey="checkout",
            targetRevision=2,
            configurationDigest="sha256:" + "a" * 64,
            createdBy="release-manager",
        )

    async def create_policy(self, policy: PromotionPolicy) -> PromotionPolicy:
        self.policy = policy
        return policy

    async def get_policy(self, tenant_id: str, policy_id: Any) -> PromotionPolicy:
        assert tenant_id == "tenant-a"
        assert policy_id == self.policy.policy_id
        return self.policy

    async def preview(self, policy: PromotionPolicy, **_: Any) -> PromotionGate:
        return PromotionGate(
            tenantId=policy.tenant_id,
            policyId=policy.policy_id,
            policyDigest=policy.digest,
            targetKind=policy.target_kind,
            targetKey=policy.target_key,
            targetRevision=policy.target_revision,
            configurationDigest=policy.configuration_digest,
            evidenceDigests=(),
            passed=True,
            evaluatedAt=datetime.now(UTC),
        )

    async def record_evidence(self, artifact: Any) -> Any:
        return artifact

    async def apply(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("apply is not part of this contract test")

    async def get_target(self, *args: Any, **kwargs: Any) -> ReleaseTarget:
        raise AssertionError("target is not part of this contract test")


def test_authenticated_preview_is_tenant_scoped_and_separately_authorized() -> None:
    service = FakePromotionService()
    actions: list[str] = []

    async def authorize(action: str) -> None:
        actions.append(action)

    app.dependency_overrides[get_promotion_service] = lambda: service
    app.dependency_overrides[require_tenant_context] = lambda: "tenant-a"
    app.dependency_overrides[get_promotion_authorizer] = lambda: authorize
    app.dependency_overrides[authenticate_actor] = lambda: ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="release-manager"
    )
    try:
        response = TestClient(app).post(
            f"/api/v1/releases/policies/{service.policy.policy_id}/preview"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["passed"] is True
    assert actions == ["preview"]


def test_policy_create_rejects_a_different_tenant_before_persistence() -> None:
    service = FakePromotionService()

    async def authorize(_: str) -> None:
        return None

    app.dependency_overrides[get_promotion_service] = lambda: service
    app.dependency_overrides[require_tenant_context] = lambda: "tenant-a"
    app.dependency_overrides[get_promotion_authorizer] = lambda: authorize
    app.dependency_overrides[authenticate_actor] = lambda: ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="release-manager"
    )
    try:
        payload = service.policy.model_dump(mode="json", by_alias=True)
        payload["policyId"] = str(uuid4())
        payload["tenantId"] = "tenant-b"
        response = TestClient(app).post("/api/v1/releases/policies", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
