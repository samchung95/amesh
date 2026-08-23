from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from amesh.admission_policy import AdmissionPolicyService
from amesh.app import (
    app,
    authenticate_actor,
    get_admission_policy_repository,
    get_admission_policy_service,
    get_authorization_service,
    require_tenant_context,
)
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    PolicyDecision,
    PolicyDocument,
    PolicyRevision,
    PrincipalType,
)


class _Repository:
    def __init__(self) -> None:
        self.revisions: list[PolicyRevision] = []
        self.decisions: list[PolicyDecision] = []

    async def effective_revisions(
        self,
        tenant_id: str,
        *,
        namespace: str,
    ) -> tuple[PolicyRevision, ...]:
        del namespace
        return tuple(
            item
            for item in self.revisions
            if item.tenant_id in {None, tenant_id} and item is self._active(item.document.policy_key)
        )

    async def save_revision(
        self,
        tenant_id: str,
        document: PolicyDocument,
        *,
        actor_id: str,
    ) -> PolicyRevision:
        active = self._active(document.policy_key)
        record = PolicyRevision(
            policyId=active.policy_id if active is not None else uuid4(),
            tenantId=None if document.scope.value == "INSTANCE" else tenant_id,
            revision=active.revision + 1 if active is not None else 1,
            digest=document.digest,
            document=document,
            createdBy=actor_id,
            createdAt=datetime.now(UTC),
        )
        self.revisions.append(record)
        return record

    async def get_revision(
        self,
        tenant_id: str,
        policy_key: str,
        *,
        revision: int | None = None,
    ) -> PolicyRevision:
        del tenant_id
        candidates = [
            item
            for item in self.revisions
            if item.document.policy_key == policy_key
            and (revision is None or item.revision == revision)
        ]
        if not candidates:
            raise LookupError("admission policy does not exist")
        return max(candidates, key=lambda item: item.revision)

    async def record_decision(
        self,
        decision: PolicyDecision,
        *,
        actor_id: str,
        execution_id: UUID | None = None,
        task_run_id: UUID | None = None,
    ) -> PolicyDecision:
        del actor_id, execution_id, task_run_id
        self.decisions.append(decision)
        return decision

    async def list_decisions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[PolicyDecision, ...]:
        del tenant_id
        return tuple(reversed(self.decisions[-limit:]))

    def _active(self, policy_key: str) -> PolicyRevision | None:
        candidates = [
            item for item in self.revisions if item.document.policy_key == policy_key
        ]
        return max(candidates, key=lambda item: item.revision, default=None)


class _Authorization:
    async def require(self, request: object) -> AuthorizationDecision:
        del request
        return AuthorizationDecision(
            allowed=True,
            reason_code="test_allow",
            summary="policy API acceptance",
            policy_version=1,
        )


def _evaluation_request(stage: str) -> dict[str, object]:
    return {
        "stage": stage,
        "input": {
            "actor": {
                "principalId": str(uuid4()),
                "principalType": "USER",
                "display": "spoofed",
            },
            "tenant": {"id": "spoofed"},
            "namespace": {"id": "governance"},
            "flow": {"id": "governed", "revision": 1},
            "runner": {"requested": "DOCKER"},
        },
    }


def test_policy_api_versions_evaluates_tests_and_explains_decisions() -> None:
    repository = _Repository()
    service = AdmissionPolicyService(repository)
    actor = ActorContext(
        principal_id=uuid4(),
        principal_type=PrincipalType.USER,
        display="security-engineer",
        bootstrap_admin=True,
    )
    app.dependency_overrides[authenticate_actor] = lambda: actor
    app.dependency_overrides[require_tenant_context] = lambda: "default"
    app.dependency_overrides[get_authorization_service] = _Authorization
    app.dependency_overrides[get_admission_policy_repository] = lambda: repository
    app.dependency_overrides[get_admission_policy_service] = lambda: service
    client = TestClient(app)
    document = {
        "schemaVersion": "amesh.policy/v1",
        "policyKey": "security.local",
        "name": "Local security policy",
        "scope": "TENANT",
        "criticality": "ENFORCING",
        "evaluationTimeoutMs": 100,
        "rules": [
            {
                "id": "deny-docker",
                "stages": ["LAUNCH"],
                "conditions": [
                    {
                        "path": "runner.requested",
                        "operator": "EQUALS",
                        "value": "DOCKER",
                    }
                ],
                "outcome": "DENY",
                "reason": "Docker launches are disabled",
            },
            {
                "id": "validate-core",
                "stages": ["VALIDATE"],
                "conditions": [
                    {
                        "path": "plugin.taskTypes",
                        "operator": "CONTAINS",
                        "value": "core.return",
                    }
                ],
                "outcome": "WARN",
                "reason": "Core return task matched validation fixture",
            },
        ],
    }
    try:
        created = client.post("/api/v1/policies", json=document)
        assert created.status_code == 201, created.text
        assert created.json()["revision"] == 1

        revised_document = {**document, "description": "revision two"}
        revised = client.put("/api/v1/policies/security.local", json=revised_document)
        assert revised.status_code == 200, revised.text
        assert revised.json()["revision"] == 2
        assert revised.json()["digest"] != created.json()["digest"]

        listed = client.get("/api/v1/policies", params={"namespace": "governance"})
        assert listed.status_code == 200, listed.text
        assert [item["revision"] for item in listed.json()] == [2]

        evaluated = client.post(
            "/api/v1/policies/evaluate",
            json=_evaluation_request("LAUNCH"),
        )
        assert evaluated.status_code == 200, evaluated.text
        assert evaluated.json()["outcome"] == "DENY"
        assert evaluated.json()["actorId"] == str(actor.principal_id)
        assert evaluated.json()["tenantId"] == "default"
        assert evaluated.json()["pinnedPolicies"][0]["revision"] == 2
        assert evaluated.json()["matchedRules"][0]["ruleId"] == "deny-docker"

        fixture = client.post(
            "/api/v1/policies/security.local/test",
            json={
                "name": "docker denied",
                "request": _evaluation_request("LAUNCH"),
                "expectedOutcome": "DENY",
                "expectedAllowed": False,
            },
        )
        assert fixture.status_code == 200, fixture.text
        assert fixture.json()["passed"] is True

        validation = client.post(
            "/api/v1/policies/flows/validate",
            content=(
                "id: governed\nnamespace: governance\ntasks:\n"
                "  - id: done\n    type: core.return\n    value: ok\n"
            ),
            headers={"Content-Type": "application/yaml"},
        )
        assert validation.status_code == 200, validation.text
        assert validation.json()["outcome"] == "WARN"
        assert validation.json()["matchedRules"][0]["ruleId"] == "validate-core"

        decisions = client.get("/api/v1/policies/decisions")
        assert decisions.status_code == 200, decisions.text
        assert [item["stage"] for item in decisions.json()] == ["VALIDATE", "LAUNCH"]
    finally:
        app.dependency_overrides.clear()
