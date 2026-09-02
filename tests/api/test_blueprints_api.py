from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from tests.fixtures.api_stubs import TenantQuotaStub

from amesh.app import app, authenticate_actor, get_authorization_service, get_tenant_service
from amesh.domain import ActorContext, AuthorizationDecision, PrincipalType


class BlueprintAuthorizationStub:
    async def require(self, request: object) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="allowed",
            summary="blueprint acceptance",
            policy_version=1,
        )


def _client() -> TestClient:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="blueprint-user",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = BlueprintAuthorizationStub
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub
    return TestClient(app)


def test_catalog_preview_and_draft_instantiation_are_read_only() -> None:
    client = _client()
    headers = {"X-Amesh-Tenant": "default"}
    try:
        catalog = client.get(
            "/api/v1/blueprints?source=BUILTIN&q=hello",
            headers=headers,
        )
        assert catalog.status_code == 200
        assert [item["blueprintId"] for item in catalog.json()] == ["hello-world"]

        preview = client.get("/api/v1/blueprints/hello-world/1.0.0", headers=headers)
        assert preview.status_code == 200
        assert preview.json()["license"] == "Apache-2.0"
        assert preview.json()["provenance"]["digest"].startswith("sha256:")

        draft = client.post(
            "/api/v1/blueprints/hello-world/1.0.0/instantiate",
            headers=headers,
            json={
                "parameters": {
                    "namespace": "tests.onboarding",
                    "flow_id": "hello_draft",
                    "greeting": "Welcome",
                }
            },
        )
        assert draft.status_code == 200
        assert draft.json()["validation"]["valid"] is True
        assert "id: hello_draft" in draft.json()["document"]
        assert "Welcome" in draft.json()["document"]
    finally:
        app.dependency_overrides.clear()


def test_playground_redacts_context_and_never_touches_runtime_resources() -> None:
    client = _client()
    try:
        response = client.post(
            "/api/v1/playground/simulate",
            headers={"X-Amesh-Tenant": "default"},
            json={
                "expression": "{{ inputs.apiToken }}",
                "context": {
                    "inputs": {"apiToken": "must-not-escape"},
                    "secrets": {"production": "must-not-resolve"},
                },
                "fragment": "id: done\ntype: core.return\nvalue: local\n",
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["expressionResult"] == "[REDACTED]"
        assert payload["redactedContext"] == {"inputs": {"apiToken": "[REDACTED]"}}
        assert payload["validation"]["valid"] is True
        assert payload["steps"][0]["simulated"] is True
        assert set(payload["safety"].values()) == {False}
        assert "must-not" not in response.text
    finally:
        app.dependency_overrides.clear()
