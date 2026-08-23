from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_plugin_policy_service,
    get_repository,
    get_settings,
    get_tenant_service,
)
from amesh.config import Settings
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    FlowRevisionRecord,
    PluginPolicyDecision,
    PluginPolicyStage,
    PrincipalType,
)
from amesh.dsl import FlowDefinition


class _Repository:
    def __init__(self) -> None:
        self.flows = {
            1: FlowDefinition.model_validate(
                {
                    "id": "forecast",
                    "namespace": "team.data",
                    "revision": 1,
                    "tasks": [{"id": "lookup", "type": "vendor.lookup"}],
                }
            ),
            2: FlowDefinition.model_validate(
                {
                    "id": "forecast",
                    "namespace": "team.data",
                    "revision": 2,
                    "tasks": [
                        {"id": "lookup", "type": "vendor.lookup"},
                        {
                            "id": "done",
                            "type": "core.return",
                            "dependsOn": ["lookup"],
                            "value": "ok",
                        },
                    ],
                }
            ),
        }
        now = datetime(2026, 8, 23, tzinfo=UTC)
        self.revisions = [
            FlowRevisionRecord(
                resource_id=uuid4(),
                tenant_id="default",
                namespace="team.data",
                flow_id="forecast",
                revision=revision,
                semantic_hash=f"semantic-{revision}",
                plugin_resolution={"vendor.lookup": f"{revision}.0.0"},
                created_by="test",
                created_at=now,
            )
            for revision in (1, 2)
        ]

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition:
        assert (namespace, flow_id, tenant_id) == ("team.data", "forecast", "default")
        if revision not in self.flows:
            raise LookupError("revision not found")
        return self.flows[revision]

    async def list_flow_revisions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
    ) -> list[FlowRevisionRecord]:
        assert (namespace, flow_id, tenant_id) == ("team.data", "forecast", "default")
        return self.revisions


class _Policy:
    async def preview_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        stage: PluginPolicyStage,
        resolution_payload: dict[str, object] | None = None,
    ) -> PluginPolicyDecision:
        del resolution_payload
        return PluginPolicyDecision(
            tenantId=tenant_id,
            namespace=flow.namespace,
            stage=stage,
            allowed=True,
            flowId=flow.id,
            flowRevision=flow.revision,
            subjects=(),
        )


class _Authorization:
    async def require(self, request: object) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="test",
            summary="simulation test",
            policy_version=1,
        )


class _Tenant:
    async def consume_api_request(self, tenant_slug: str) -> int:
        assert tenant_slug == "default"
        return 1


def test_revision_simulation_and_comparison_are_signed_and_side_effect_free() -> None:
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="simulator",
    )
    repository = _Repository()
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[get_authorization_service] = _Authorization
    app.dependency_overrides[get_tenant_service] = _Tenant
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_plugin_policy_service] = _Policy
    app.dependency_overrides[get_settings] = lambda: Settings()
    request = {
        "fixtures": {"lookup": {"source": "MOCK", "output": {"value": 7}}},
        "estimateModels": {
            "vendor.lookup": {"durationSeconds": 0.25, "apiCalls": 1, "costUsd": 0.01}
        },
    }
    try:
        client = TestClient(app)
        simulated = client.post(
            "/api/v1/flows/team.data/forecast/revisions/1/simulate",
            headers={"X-Amesh-Tenant": "default"},
            json=request,
        )
        assert simulated.status_code == 200, simulated.text
        payload = simulated.json()
        assert payload["sideEffectsSuppressed"] is True
        assert payload["evidence"]["signature"].startswith("v1=")
        assert payload["policyDecisions"][0]["allowed"] is True

        compared = client.post(
            "/api/v1/flows/team.data/forecast/simulations/compare?from=1&to=2",
            headers={"X-Amesh-Tenant": "default"},
            json=request,
        )
        assert compared.status_code == 200, compared.text
        comparison = compared.json()
        assert comparison["diff"]["pluginSetChanged"] is True
        assert comparison["diff"]["addedTasks"] == ["done"]
        assert comparison["before"]["evidence"] is not None
        assert comparison["after"]["evidence"] is not None
    finally:
        app.dependency_overrides.clear()
