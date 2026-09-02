from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any, cast
from uuid import UUID, uuid4

import httpx
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresRealtimeRepository,
    PostgresTenantRepository,
)
from amesh.api.contracts import _encode_cursor
from amesh.app import (
    app,
    get_authorization_service,
    get_realtime_repository,
    get_repository,
    get_tenant_service,
    stream_realtime_events,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.domain import ActorContext, AuthorizationDecision, PrincipalType
from amesh.dsl import FlowDefinition
from amesh.realtime import (
    RealtimeFilter,
    WebhookDeliveryKind,
    WebhookDeliveryStatus,
    WebhookDispatcher,
    derive_webhook_secret,
    webhook_signature,
)
from amesh.tasks import HttpTaskPolicy
from amesh.tenancy import TenantService


class _GapRealtime:
    async def cursor_bounds(self, *, tenant_id: str) -> tuple[int, int]:
        del tenant_id
        return 10, 20

    async def list_events(self, **kwargs: object) -> tuple[()]:
        del kwargs
        return ()


class _AllowAuthorization:
    async def require(self, request: object) -> AuthorizationDecision:
        del request
        return self._decision()

    async def decide(self, request: object) -> AuthorizationDecision:
        del request
        return self._decision()

    @staticmethod
    def _decision() -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            reason_code="test",
            summary="allowed",
            policy_version=1,
        )


class _ConnectedRequest:
    async def is_disconnected(self) -> bool:
        return False


def test_urs_f_0412_explicit_gap_signal_advances_to_oldest_retained_cursor() -> None:
    async def scenario() -> None:
        response = await stream_realtime_events(
            request=cast(Any, _ConnectedRequest()),
            realtime=cast(Any, _GapRealtime()),
            repository=cast(Any, object()),
            actor=ActorContext(
                principal_id=uuid4(),
                principal_type=PrincipalType.USER,
                display="gap tester",
            ),
            authorization_service=cast(Any, _AllowAuthorization()),
            tenant_id="default",
            cursor=_encode_cursor(1),
            last_event_id=None,
            namespace=None,
            flow_id=None,
            execution_id=None,
            event_types=None,
            severities=None,
            include_audit=False,
            buffer_events=1,
            max_events=1,
            heartbeat_seconds=1,
            stream_seconds=1,
        )
        iterator = cast(AsyncIterator[str], response.body_iterator)
        first = await anext(iterator)
        assert "event: gap" in first
        assert '"oldestAvailable"' in first
        assert _encode_cursor(9) in first
        if hasattr(iterator, "aclose"):
            await iterator.aclose()

    asyncio.run(scenario())


async def _cleanup(
    engine: AsyncEngine,
    execution_ids: list[UUID],
    subscription_ids: list[UUID],
) -> None:
    async with engine.begin() as connection:
        if subscription_ids:
            await connection.execute(
                text(
                    "DELETE FROM realtime_events WHERE payload ->> 'resourceId' "
                    "= ANY(CAST(:subscription_ids AS text[]))"
                ),
                {"subscription_ids": [str(item) for item in subscription_ids]},
            )
            await connection.execute(
                text(
                    "DELETE FROM audit_events WHERE resource_type = 'webhook_subscription' "
                    "AND resource_id = ANY(CAST(:subscription_ids AS text[]))"
                ),
                {"subscription_ids": [str(item) for item in subscription_ids]},
            )
            await connection.execute(
                text("DELETE FROM webhook_subscriptions WHERE id = ANY(CAST(:ids AS uuid[]))"),
                {"ids": subscription_ids},
            )
        for execution_id in execution_ids:
            await connection.execute(
                text("DELETE FROM messages_outbox WHERE partition_key = :partition_key"),
                {"partition_key": f"execution:{execution_id}"},
            )
            await connection.execute(
                text("DELETE FROM task_run_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text(
                    "DELETE FROM task_attempts WHERE task_run_id IN "
                    "(SELECT id FROM task_runs WHERE execution_id = :execution_id)"
                ),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM task_runs WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM execution_events WHERE execution_id = :execution_id"),
                {"execution_id": execution_id},
            )
            await connection.execute(
                text("DELETE FROM executions WHERE id = :execution_id"),
                {"execution_id": execution_id},
            )


def test_urs_f_0406_0407_0408_0411_0412_reconnectable_filtered_sse(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        realtime = PostgresRealtimeRepository(engine)
        authorization = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenant_service = TenantService(PostgresTenantRepository(engine))
        settings = Settings(
            database_url=migrated_test_database_url,
            amesh_admin_token=SecretStr("test-token"),
            webhook_signing_key=SecretStr("test-webhook-signing-key-at-least-32-bytes"),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_realtime_repository] = lambda: realtime
        app.dependency_overrides[get_authorization_service] = lambda: authorization
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_settings] = lambda: settings
        execution_ids: list[UUID] = []
        flow = FlowDefinition.model_validate(
            {
                "id": "realtime_api",
                "namespace": f"tests.realtime.{uuid4().hex}",
                "tasks": [{"id": "one", "type": "core.return", "value": "ok"}],
            }
        )
        execution = await repository.create_execution(flow, tenant_id="default", inputs={})
        execution_ids.append(execution.execution_id)
        injected_event_id = uuid4()
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "INSERT INTO realtime_events ("
                    "tenant_id, event_id, namespace_name, flow_id, execution_id, "
                    "event_type, severity, payload, occurred_at) "
                    "SELECT id, :event_id, :namespace, :flow_id, :execution_id, "
                    "'log.info', 'INFO', CAST(:payload AS jsonb), clock_timestamp() "
                    "FROM tenants WHERE slug = 'default'"
                ),
                {
                    "event_id": injected_event_id,
                    "namespace": flow.namespace,
                    "flow_id": flow.id,
                    "execution_id": execution.execution_id,
                    "payload": json.dumps({"safe": "visible", "token": "must-not-escape"}),
                },
            )
        headers = {"authorization": "Bearer test-token"}
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                unauthorized = await client.get("/api/v1/realtime/events")
                assert unauthorized.status_code == 401

                page = await client.get(
                    "/api/v1/realtime/events",
                    headers=headers,
                    params={
                        "executionId": str(execution.execution_id),
                        "eventType": "log.info",
                        "includeAudit": "false",
                    },
                )
                assert page.status_code == 200
                payload = page.json()
                assert len(payload["items"]) == 1
                assert payload["items"][0]["eventId"] == str(injected_event_id)
                assert payload["items"][0]["payload"] == {
                    "safe": "visible",
                    "token": "[REDACTED]",
                }

                stream = await client.get(
                    "/api/v1/realtime/stream",
                    headers=headers,
                    params={
                        "executionId": str(execution.execution_id),
                        "eventType": "log.info",
                        "includeAudit": "false",
                        "bufferEvents": 1,
                        "maxEvents": 1,
                        "streamSeconds": 1,
                    },
                )
                assert stream.status_code == 200
                assert stream.headers["content-type"].startswith("text/event-stream")
                assert stream.headers["x-amesh-buffer-limit"] == "1"
                assert "event: log.info" in stream.text
                assert "must-not-escape" not in stream.text

                cursor = _encode_cursor(payload["items"][0]["cursor"])
                heartbeat = await client.get(
                    "/api/v1/realtime/stream",
                    headers={**headers, "Last-Event-ID": cursor},
                    params={
                        "executionId": str(execution.execution_id),
                        "eventType": "does.not.exist",
                        "includeAudit": "false",
                        "heartbeatSeconds": 0.1,
                        "streamSeconds": 1,
                    },
                )
                assert heartbeat.status_code == 200
                assert ": heartbeat " in heartbeat.text

                filtered = await client.get(
                    "/api/v1/realtime/events",
                    headers=headers,
                    params={"namespace": "unrelated.namespace", "includeAudit": "false"},
                )
                assert filtered.status_code == 200
                assert filtered.json()["items"] == []
        finally:
            app.dependency_overrides.clear()
            await _cleanup(engine, execution_ids, [])
            await engine.dispose()

    asyncio.run(scenario())


def test_urs_f_0409_0410_0413_signed_retry_rotation_replay_and_outage_isolation(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        repository = PostgresExecutionRepository(engine)
        realtime = PostgresRealtimeRepository(engine)
        authorization = AuthorizationService(PostgresAuthorizationRepository(engine))
        tenant_service = TenantService(PostgresTenantRepository(engine))
        signing_key = "test-webhook-signing-key-at-least-32-bytes"
        settings = Settings(
            database_url=migrated_test_database_url,
            amesh_admin_token=SecretStr("test-token"),
            webhook_signing_key=SecretStr(signing_key),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_realtime_repository] = lambda: realtime
        app.dependency_overrides[get_authorization_service] = lambda: authorization
        app.dependency_overrides[get_tenant_service] = lambda: tenant_service
        app.dependency_overrides[get_settings] = lambda: settings
        subscription_ids: list[UUID] = []
        execution_ids: list[UUID] = []
        headers = {"authorization": "Bearer test-token"}
        transport = httpx.ASGITransport(app=app)
        captured: list[httpx.Request] = []

        async def webhook(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(503 if len(captured) == 1 else 204)

        mock_client = httpx.AsyncClient(transport=httpx.MockTransport(webhook))
        dispatcher = WebhookDispatcher(
            realtime,
            signing_key=signing_key,
            policy=HttpTaskPolicy(),
            timeout_seconds=1,
            client=mock_client,
        )
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                denied = await client.post(
                    "/api/v1/webhook-subscriptions",
                    headers=headers,
                    json={"name": "blocked.private", "url": "http://127.0.0.1/hook"},
                )
                assert denied.status_code == 422

                created = await client.post(
                    "/api/v1/webhook-subscriptions",
                    headers=headers,
                    json={
                        "name": f"test.endpoint.{uuid4().hex}",
                        "url": "https://example.test/hook",
                        "filters": {
                            "eventTypes": ["does.not.match"],
                            "includeAudit": False,
                        },
                        "maxAttempts": 2,
                    },
                )
                assert created.status_code == 201
                provisioned = created.json()
                subscription_id = UUID(provisioned["subscription"]["id"])
                subscription_ids.append(subscription_id)
                first_secret = provisioned["signingSecret"]

                rotated = await client.post(
                    f"/api/v1/webhook-subscriptions/{subscription_id}/rotate-secret",
                    headers=headers,
                    params={"expectedVersion": provisioned["subscription"]["resourceVersion"]},
                )
                assert rotated.status_code == 200
                rotated_payload = rotated.json()
                assert rotated_payload["signingSecret"] != first_secret

                test_delivery = await client.post(
                    f"/api/v1/webhook-subscriptions/{subscription_id}/test",
                    headers=headers,
                )
                assert test_delivery.status_code == 202
                delivery_id = UUID(test_delivery.json()["id"])

                assert (
                    await dispatcher.run_once(["default"], worker_id="test-indexer", limit=10) == 0
                )
                history = await client.get(
                    f"/api/v1/webhook-subscriptions/{subscription_id}/deliveries",
                    headers=headers,
                )
                assert history.status_code == 200
                assert history.json()[0]["delivery"]["status"] == "RETRY"
                assert history.json()[0]["attempts"][0]["outcome"] == "RETRY"

                flow = FlowDefinition.model_validate(
                    {
                        "id": "webhook_outage",
                        "namespace": f"tests.webhook.{uuid4().hex}",
                        "inputs": [{"id": "privateValue", "type": "STRING", "sensitive": True}],
                        "tasks": [{"id": "one", "type": "core.return", "value": "ok"}],
                    }
                )
                execution = await repository.create_execution(
                    flow,
                    tenant_id="default",
                    inputs={"privateValue": "webhook-sensitive-value"},
                )
                execution_ids.append(execution.execution_id)
                assert execution.execution_id is not None

                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            "UPDATE webhook_deliveries SET next_attempt_at = clock_timestamp() "
                            "WHERE id = :delivery_id"
                        ),
                        {"delivery_id": delivery_id},
                    )
                assert (
                    await dispatcher.run_once(["default"], worker_id="test-indexer", limit=10) == 1
                )
                history = await client.get(
                    f"/api/v1/webhook-subscriptions/{subscription_id}/deliveries",
                    headers=headers,
                )
                final_history = history.json()[0]
                assert final_history["delivery"]["status"] == "DELIVERED"
                assert [item["outcome"] for item in final_history["attempts"]] == [
                    "RETRY",
                    "DELIVERED",
                ]

                final_request = captured[-1]
                timestamp = int(final_request.headers["X-Amesh-Timestamp"])
                current_secret = derive_webhook_secret(
                    signing_key,
                    "default",
                    subscription_id,
                    rotated_payload["subscription"]["signingVersion"],
                )
                assert final_request.headers["X-Amesh-Delivery-Id"] == str(delivery_id)
                assert final_request.headers["X-Amesh-Signature"] == webhook_signature(
                    current_secret,
                    timestamp,
                    delivery_id,
                    final_request.content,
                )

                replay = await client.post(
                    f"/api/v1/webhook-deliveries/{delivery_id}/replay",
                    headers=headers,
                )
                assert replay.status_code == 202
                assert replay.json()["deliveryKind"] == WebhookDeliveryKind.REPLAY.value
                assert replay.json()["status"] == WebhookDeliveryStatus.PENDING.value

                sensitive_event_id = uuid4()
                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            "INSERT INTO realtime_events ("
                            "tenant_id, event_id, namespace_name, flow_id, execution_id, "
                            "event_type, severity, payload, occurred_at) "
                            "SELECT id, :event_id, :namespace, :flow_id, :execution_id, "
                            "'log.sensitive', 'INFO', CAST(:payload AS jsonb), clock_timestamp() "
                            "FROM tenants WHERE slug = 'default'"
                        ),
                        {
                            "event_id": sensitive_event_id,
                            "namespace": flow.namespace,
                            "flow_id": flow.id,
                            "execution_id": execution.execution_id,
                            "payload": json.dumps(
                                {
                                    "note": "webhook-sensitive-value",
                                    "safe": "visible",
                                }
                            ),
                        },
                    )
                events = await realtime.list_events(
                    tenant_id="default",
                    after_cursor=0,
                    filters=RealtimeFilter(
                        executionId=execution.execution_id,
                        eventTypes=("log.sensitive",),
                        includeAudit=False,
                    ),
                    limit=100,
                )
                assert events
                event_subscription = await client.post(
                    "/api/v1/webhook-subscriptions",
                    headers=headers,
                    json={
                        "name": f"event.endpoint.{uuid4().hex}",
                        "url": "https://example.test/event",
                        "filters": {
                            "executionId": str(execution.execution_id),
                            "eventTypes": ["log.sensitive"],
                            "includeAudit": False,
                        },
                    },
                )
                assert event_subscription.status_code == 201
                event_subscription_id = UUID(event_subscription.json()["subscription"]["id"])
                subscription_ids.append(event_subscription_id)
                delivered = await dispatcher.run_once(
                    ["default"], worker_id="test-indexer", limit=100
                )
                assert delivered >= 1
                event_history = await realtime.list_delivery_history(
                    event_subscription_id,
                    tenant_id="default",
                )
                assert any(
                    item.delivery.delivery_kind is WebhookDeliveryKind.EVENT
                    and item.delivery.status is WebhookDeliveryStatus.DELIVERED
                    for item in event_history
                )
                event_payloads = [
                    json.loads(request.content)
                    for request in captured
                    if json.loads(request.content)["eventType"] == "log.sensitive"
                ]
                assert event_payloads[-1]["payload"] == {
                    "note": "[REDACTED]",
                    "safe": "visible",
                }
        finally:
            app.dependency_overrides.clear()
            await mock_client.aclose()
            await _cleanup(engine, execution_ids, subscription_ids)
            await engine.dispose()

    asyncio.run(scenario())
