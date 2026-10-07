from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
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
        self.lookups: list[tuple[str, str]] = []

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

    async def get_target(self, tenant_id: str, kind: Any, key: str) -> dict[str, str]:
        self.lookups.append(("target", key))
        return {}

    async def get_history(self, tenant_id: str, kind: Any, key: str) -> list[object]:
        self.lookups.append(("history", key))
        return []

    async def rollback(self, tenant_id: str, kind: Any, key: str, **_: Any) -> Any:
        self.lookups.append(("rollback", key))
        return SimpleNamespace(target={}, event={})


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


def test_workflow_target_key_with_a_slash_reaches_target_history_and_rollback() -> None:
    service = FakePromotionService()

    async def authorize(_: str) -> None:
        return None

    app.dependency_overrides[get_promotion_service] = lambda: service
    app.dependency_overrides[require_tenant_context] = lambda: "tenant-a"
    app.dependency_overrides[get_promotion_authorizer] = lambda: authorize
    app.dependency_overrides[authenticate_actor] = lambda: ActorContext(
        principal_id=uuid4(), principal_type=PrincipalType.USER, display="release-manager"
    )
    target = "/api/v1/releases/WORKFLOW/examples.safe%2Fresearch"
    try:
        client = TestClient(app)
        responses = [
            client.get(target),
            client.get(f"{target}/history"),
            client.post(
                f"{target}/rollback",
                json={"toRevision": 1, "expectedVersion": 2, "reason": "restore"},
            ),
        ]
    finally:
        app.dependency_overrides.clear()

    assert [response.status_code for response in responses] == [200, 200, 200]
    assert service.lookups == [
        ("target", "examples.safe/research"),
        ("history", "examples.safe/research"),
        ("rollback", "examples.safe/research"),
    ]
