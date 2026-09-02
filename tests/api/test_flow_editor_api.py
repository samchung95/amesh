from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from tests.fixtures.api_stubs import TenantQuotaStub

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_tenant_service,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    PrincipalType,
)


class FlowEditorAuthorizationStub:
    async def require(self, request: object) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="allowed",
            summary="flow editor acceptance",
            policy_version=1,
        )


def test_editor_schema_format_ranges_and_redacted_expression_preview() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="flow-editor",
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = FlowEditorAuthorizationStub
    app.dependency_overrides[get_tenant_service] = TenantQuotaStub
    client = TestClient(app)
    headers = {"X-Amesh-Tenant": "default"}
    try:
        schema = client.get("/api/v1/flows/editor/schema", headers=headers)
        assert schema.status_code == 200
        assert schema.json()["schemaVersion"] == "amesh.flow-editor/v1"
        assert any(
            resource["type"] == "core.return"
            for resource in schema.json()["resourceCatalog"]["resources"]
        )

        invalid = client.post(
            "/api/v1/flows/validate",
            headers={**headers, "content-type": "application/yaml"},
            content="id: editor\nnamespace: tests\nunknown: value\ntasks: []\n",
        )
        assert invalid.status_code == 200
        assert invalid.json()["valid"] is False
        issue = invalid.json()["issues"][0]
        assert issue["sourceRange"]["start"]["offset"] >= 0
        assert issue["hint"]

        formatted = client.post(
            "/api/v1/flows/format",
            headers={**headers, "content-type": "application/yaml"},
            content=(
                "namespace: tests\nid: editor\ntasks:\n"
                "  - type: core.return\n    id: done\n    value: ok\n"
            ),
        )
        assert formatted.status_code == 200
        assert formatted.json()["validation"]["valid"] is True
        assert formatted.json()["document"].startswith(
            "apiVersion: amesh.flow/v1\nid: editor\nnamespace: tests\n"
        )

        preview = client.post(
            "/api/v1/flows/expressions/preview",
            headers={**headers, "content-type": "application/json"},
            json={
                "expression": "{{ inputs.apiToken }}",
                "context": {
                    "inputs": {"apiToken": "must-not-escape"},
                    "secrets": {"production": "must-not-be-resolved"},
                },
            },
        )
        assert preview.status_code == 200
        assert preview.json()["result"] == "[REDACTED]"
        assert preview.json()["redactedContext"] == {"inputs": {"apiToken": "[REDACTED]"}}
        assert "must-not" not in preview.text
    finally:
        app.dependency_overrides.clear()
