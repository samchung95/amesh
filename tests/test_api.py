from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from amesh.app import (
    _authentication_source,
    _build_flow_graph,
    _problem_response,
    _public_execution,
    app,
    get_read_repository,
    get_service_registry_repository,
)
from amesh.config import Settings, get_settings
from amesh.domain import ExecutionState, ServiceLiveness, ServiceRole, ServiceState
from amesh.dsl import FlowDefinition
from amesh.ports import PersistedExecution, PersistedIterationSummary

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_requires_every_enabled_role_and_reports_disabled_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def ready_preflight(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(
            ready=True,
            status="ready",
            dependency_states={"database": "READY", "migrations": "READY"},
            migrations_applied=60,
            migrations_expected=60,
            latest_migration="0060_service_role_health.sql",
            degraded_dependencies=(),
            error=None,
        )

    class Registry:
        scheduler_state = ServiceState.DEGRADED

        async def topology(self) -> SimpleNamespace:
            return SimpleNamespace(
                instances=(
                    SimpleNamespace(
                        role=ServiceRole.WEBSERVER,
                        instance_name="api",
                        liveness=ServiceLiveness.LIVE,
                        state=ServiceState.READY,
                    ),
                    SimpleNamespace(
                        role=ServiceRole.SCHEDULER,
                        instance_name="scheduler",
                        liveness=ServiceLiveness.LIVE,
                        state=self.scheduler_state,
                    ),
                )
            )

    registry = Registry()
    monkeypatch.setattr("amesh.app.run_preflight", ready_preflight)
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        service_instance_name="api",
        service_enabled_roles=("webserver", "scheduler"),
    )
    app.dependency_overrides[get_service_registry_repository] = lambda: registry
    try:
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["roles"] == {
            "executor": "DISABLED",
            "indexer": "DISABLED",
            "maintenance": "DISABLED",
            "scheduler": "DEGRADED",
            "webserver": "READY",
            "worker": "DISABLED",
        }

        registry.scheduler_state = ServiceState.READY
        recovered = client.get("/ready")
        assert recovered.status_code == 200
        assert recovered.json()["roles"]["scheduler"] == "READY"
    finally:
        app.dependency_overrides.clear()


def test_http_errors_use_problem_details() -> None:
    response = client.get("/api/v1/not-a-resource")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:amesh:problem:http_404",
        "title": "Not Found",
        "status": 404,
        "detail": "Not Found",
        "code": "HTTP_404",
        "instance": "/api/v1/not-a-resource",
    }


def test_public_execution_redacts_webhook_body_when_inputs_are_already_redacted() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "webhook",
            "namespace": "tests",
            "inputs": [{"id": "token", "type": "STRING", "sensitive": True}],
            "tasks": [{"id": "echo", "type": "core.return"}],
        }
    )
    now = datetime.now(UTC)
    execution = PersistedExecution(
        execution_id=uuid4(),
        tenant_id="default",
        state=ExecutionState.SUCCESS,
        epoch=1,
        version=1,
        namespace=flow.namespace,
        flow_id=flow.id,
        inputs={"token": "[REDACTED]"},
        trigger={"type": "core.webhook", "body": {"token": "webhook-canary"}},
        created_at=now,
        updated_at=now,
    )

    public = _public_execution(flow, execution)

    assert public.trigger["body"] == {"token": "[REDACTED]"}
    assert "webhook-canary" not in public.model_dump_json()


def test_problem_details_preserve_structured_validation_detail() -> None:
    detail = [{"code": "MISSING_FIELD", "path": ["namespace"]}]
    request = Request(
        {
            "type": "http",
            "method": "PUT",
            "scheme": "http",
            "server": ("amesh.test", 80),
            "path": "/api/v1/flows",
            "query_string": b"",
            "headers": [],
        }
    )
    response = _problem_response(
        request,
        status_code=422,
        detail=detail,
    )

    assert response.status_code == 422
    assert response.media_type == "application/problem+json"
    assert detail[0]["code"].encode() in response.body


def test_validate_endpoint() -> None:
    response = client.post(
        "/api/v1/flows/validate",
        content=b"id: x\nnamespace: tests\ntasks:\n  - id: a\n    type: core.return\n",
        headers={"content-type": "application/yaml"},
    )
    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_validate_endpoint_rejects_oversized_body_before_validation() -> None:
    response = client.post(
        "/api/v1/flows/validate",
        content=b"x" * (2 * 1024 * 1024 + 1),
        headers={"content-type": "application/yaml"},
    )

    assert response.status_code == 413


def test_login_throttle_source_ignores_user_agent() -> None:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "server": ("amesh.test", 80),
            "client": ("127.0.0.1", 50000),
            "path": "/api/v1/auth/login",
            "query_string": b"",
            "headers": [(b"user-agent", b"attacker-controlled")],
        }
    )

    assert _authentication_source(request) == "127.0.0.1"


def test_loop_graph_uses_aggregated_template_nodes() -> None:
    flow = FlowDefinition.model_validate(
        {
            "id": "loop_graph",
            "namespace": "tests",
            "tasks": [
                {
                    "id": "each",
                    "type": "core.foreach",
                    "items": [1, 2, 3],
                    "tasks": [{"id": "capture", "type": "core.return"}],
                }
            ],
        }
    )
    graph = _build_flow_graph(
        flow,
        iteration_summaries=[
            PersistedIterationSummary(
                loop_id="each",
                task_id="capture",
                iteration_count=3,
                waiting=0,
                running=0,
                succeeded=3,
                failed=0,
                cancelled=0,
            )
        ],
    )

    assert [node.task_id for node in graph.nodes] == [
        "each",
        "each--template--capture",
    ]
    assert graph.nodes[1].label == "capture"
    assert graph.nodes[1].iteration_count == 3
    assert graph.nodes[1].state == "SUCCESS"


def test_read_repository_uses_primary_unless_replica_is_configured(monkeypatch) -> None:
    primary = object()
    replica = object()
    monkeypatch.setattr(
        "amesh.app.get_settings",
        lambda: Settings(_env_file=None),
    )
    assert get_read_repository(primary) is primary

    monkeypatch.setattr(
        "amesh.app.get_settings",
        lambda: Settings(
            _env_file=None,
            database_read_replica_url="postgresql+asyncpg://replica/amesh",
        ),
    )
    monkeypatch.setattr("amesh.app.get_replica_repository", lambda: replica)
    assert get_read_repository(primary) is replica
