from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresEvidenceBundleRepository,
    PostgresExecutionRepository,
    PostgresMetadataRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
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
from amesh.domain import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationRequest,
    OperationalBoundary,
    OperationalControlDecision,
    PrincipalType,
    RunningWorkPolicy,
)
from amesh.dsl import FlowDefinition
from amesh.evidence_bundle import (
    EvidenceBundleError,
    EvidenceConflictError,
    EvidenceNotFoundError,
    EvidenceRecord,
)

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_postgres_evidence_bundle_is_immutable_restart_stable_and_integrity_checked(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            executions = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "evidence-bundle",
                    "namespace": f"tests.evidence.{uuid4().hex}",
                    "tasks": [{"id": "done", "type": "core.return"}],
                }
            )
            execution = await executions.create_execution(flow, tenant_id="default", inputs={})
            occurred_at = datetime.now(UTC)
            event = {
                "event_id": uuid4(),
                "event_type": "log.info",
                "kind": "LOG",
                "cursor": 1,
                "occurred_at": occurred_at,
                "payload": {"message": "safe", "authorization": "redacted"},
            }
            repository = PostgresEvidenceBundleRepository(engine)
            bundle = await repository.build_and_put(
                execution.execution_id,
                "default",
                [event],
                created_at=execution.created_at,
            )
            assert bundle.bundle_digest == bundle.digest
            assert (
                await repository.page(
                    execution.execution_id,
                    tenant_id="default",
                    section="trace",
                    limit=1,
                )
            ).total == 1
            with pytest.raises(EvidenceNotFoundError):
                await repository.get(execution.execution_id, tenant_id="amesh-system")

            conflicting = bundle.model_copy(
                update={
                    "trace": (
                        EvidenceRecord(
                            recordId="different",
                            kind="log.info",
                            sequence=1,
                            correlationId=str(execution.execution_id),
                            occurredAt=occurred_at,
                            payload={"message": "different"},
                        ),
                    ),
                    "bundle_digest": None,
                }
            )
            with pytest.raises(EvidenceConflictError):
                await repository.put(conflicting)

            await engine.dispose()
            engine = create_async_engine(migrated_test_database_url)
            restarted = PostgresEvidenceBundleRepository(engine)
            recovered = await restarted.get(execution.execution_id, tenant_id="default")
            assert recovered.digest == bundle.digest
            with pytest.raises(EvidenceNotFoundError):
                await restarted.get(execution.execution_id, tenant_id="amesh-system")

            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE execution_evidence_bundles "
                        "SET bundle = jsonb_set(bundle, '{trace}', '[]'::jsonb) "
                        "WHERE execution_id = :execution_id"
                    ),
                    {"execution_id": execution.execution_id},
                )
            with pytest.raises(EvidenceBundleError):
                await restarted.get(execution.execution_id, tenant_id="default")
            async with engine.begin() as connection:
                outbox = await connection.scalar(
                    text(
                        "SELECT count(*) FROM messages_outbox "
                        "WHERE subject = 'execution-evidence-bundles' "
                        "AND partition_key = :partition_key"
                    ),
                    {"partition_key": f"execution:{execution.execution_id}"},
                )
            assert outbox == 1
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_postgres_reference_events_build_all_sections_through_rest(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="reference-operator",
        )

        class Authorization:
            async def require(self, request: AuthorizationRequest) -> AuthorizationDecision:
                del request
                return AuthorizationDecision(
                    allowed=True,
                    reason_code="reference_allow",
                    summary="reference evidence export",
                    policy_version=1,
                    matched_role_names=("operator",),
                )

        class TenantQuota:
            async def consume_api_request(self, tenant_slug: str) -> int:
                assert tenant_slug == "default"
                return 1

        class Controls:
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

        try:
            executions = PostgresExecutionRepository(engine)
            flow = FlowDefinition.model_validate(
                {
                    "id": "evidence-reference",
                    "namespace": f"tests.evidence.reference.{uuid4().hex}",
                    "tasks": [{"id": "done", "type": "core.return"}],
                }
            )
            execution = await executions.create_execution(flow, tenant_id="default", inputs={})
            now = datetime.now(UTC)
            events = (
                ("AGENT", "agent.session.started", {"sessionId": "reference-session"}),
                (
                    "MODEL",
                    "model.response",
                    {
                        "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7},
                        "costUsd": "0.0007",
                        "reasoning": "private chain of thought",
                    },
                ),
                ("TOOL", "tool.result", {"result": {"status": "ok"}}),
                ("ERROR", "error.external", {"message": "redacted failure", "token": "secret"}),
                ("APPROVAL", "approval.granted", {"actor": "operator"}),
                ("INTERVENTION", "intervention.requested", {"reason": "review"}),
                ("CONTROL", "control.evaluated", {"allowed": True}),
                ("DECISION", "decision.accepted", {"decision": "approve"}),
            )
            metadata = PostgresMetadataRepository(engine)
            async with tenant_transaction(engine, "default") as (connection, tenant_uuid):
                for kind, event_type, payload in events:
                    await connection.execute(
                        text(
                            """
                            INSERT INTO execution_evidence_events (
                                tenant_id, event_id, execution_id, kind,
                                event_type, payload, occurred_at
                            ) VALUES (
                                :tenant_id, :event_id, :execution_id, :kind,
                                :event_type, CAST(:payload AS jsonb), :occurred_at
                            )
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "event_id": uuid4(),
                            "execution_id": execution.execution_id,
                            "kind": kind,
                            "event_type": event_type,
                            "payload": json.dumps(payload),
                            "occurred_at": now,
                        },
                    )
            persisted = await metadata.list_evidence_events(
                execution.execution_id,
                tenant_id="default",
            )
            assert {
                "AGENT",
                "MODEL",
                "TOOL",
                "ERROR",
                "APPROVAL",
                "INTERVENTION",
                "CONTROL",
                "DECISION",
            } <= {event.kind.value for event in persisted}

            evidence_repository = PostgresEvidenceBundleRepository(engine)
            app.dependency_overrides[authenticate_actor] = lambda: actor
            app.dependency_overrides[get_authorization_service] = Authorization
            app.dependency_overrides[get_repository] = lambda: executions
            app.dependency_overrides[get_metadata_repository] = lambda: metadata
            app.dependency_overrides[get_evidence_bundle_repository] = lambda: evidence_repository
            app.dependency_overrides[get_tenant_service] = TenantQuota
            app.dependency_overrides[get_operational_control_repository] = Controls
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://amesh.test",
            ) as client:
                digests: set[str] = set()
                expected = {
                    "agent_sessions",
                    "external_invocations",
                    "errors",
                    "approvals",
                    "interventions",
                    "controls",
                    "decisions",
                }
                for section in expected:
                    response = await client.get(
                        f"/api/v1/executions/{execution.execution_id}/evidence-bundle",
                        headers={"X-Amesh-Tenant": "default"},
                        params={"section": section, "limit": 10},
                    )
                    assert response.status_code == 200, response.text
                    body = response.json()
                    digests.add(body["bundleDigest"])
                    assert body["total"] >= 1
                    serialized = response.text
                    assert "private chain of thought" not in serialized
                    if section == "external_invocations":
                        model_item = next(
                            item for item in body["items"] if item["kind"] == "model.response"
                        )
                        assert model_item["payload"]["reasoning"] == "[OMITTED]"
                assert len(digests) == 1

            recovered = await evidence_repository.get(execution.execution_id, tenant_id="default")
            assert recovered.digest == next(iter(digests))
            assert any(cost.state.value == "priced" for cost in recovered.costs)
            assert recovered.errors[0].payload["token"] == "[REDACTED]"
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()

    asyncio.run(scenario())
