"""Cohesive realtime API definitions extracted from the composition root."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from starlette.responses import StreamingResponse

from amesh.api.contracts import (
    _decode_cursor,
    _encode_cursor,
)
from amesh.api.dependencies import (
    ActorDependency,
    AuthorizationServiceDependency,
    RealtimeRepositoryDependency,
    RepositoryDependency,
    SettingsDependency,
    TenantDependency,
    authorize_request,
)
from amesh.authorization import AuthorizationService
from amesh.domain import (
    ActorContext,
    AuthorizationRequest,
    PermissionAction,
)
from amesh.ports import (
    ExecutionRepository,
)
from amesh.realtime import (
    ProvisionedWebhookSubscription,
    RealtimeEvent,
    RealtimeEventPage,
    RealtimeFilter,
    RealtimeSeverity,
    WebhookDelivery,
    WebhookDeliveryHistory,
    WebhookSubscription,
    WebhookSubscriptionCreate,
    derive_webhook_secret,
    redact_realtime_payload,
)
from amesh.tasks import (
    HttpTaskPolicy,
)
from amesh.tasks.http import validate_http_destination
from amesh.workflow.data_contracts import (
    sensitive_execution_values,
)

router_1 = APIRouter()


async def _authorized_realtime_filter(
    filters: RealtimeFilter,
    *,
    repository: ExecutionRepository,
    authorization_service: AuthorizationService,
    actor: ActorContext,
    tenant_id: str,
) -> RealtimeFilter:
    namespace = filters.namespace
    if filters.execution_id is not None:
        try:
            execution = await repository.get_execution(filters.execution_id, tenant_id=tenant_id)
        except LookupError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        if namespace is not None and namespace != execution.namespace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="execution unavailable"
            )
        if filters.flow_id is not None and filters.flow_id != execution.flow_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="execution unavailable"
            )
        namespace = execution.namespace
    await authorize_request(
        authorization_service,
        actor,
        resource_type="execution",
        action=PermissionAction.VIEW,
        tenant_id=tenant_id,
        namespace=namespace,
    )
    audit_decision = await authorization_service.decide(
        AuthorizationRequest(
            actor=actor,
            tenant_id=tenant_id,
            namespace=namespace,
            resource_type="audit",
            action=PermissionAction.VIEW,
        )
    )
    return filters.model_copy(
        update={
            "namespace": namespace if filters.execution_id is not None else filters.namespace,
            "include_audit": filters.include_audit and audit_decision.allowed,
        }
    )


@router_1.get(
    "/api/v1/realtime/events",
    response_model=RealtimeEventPage,
    tags=["realtime"],
)
async def list_realtime_events(
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
    namespace: str | None = None,
    flow_id: Annotated[str | None, Query(alias="flowId")] = None,
    execution_id: Annotated[UUID | None, Query(alias="executionId")] = None,
    event_types: Annotated[list[str] | None, Query(alias="eventType")] = None,
    severities: Annotated[list[RealtimeSeverity] | None, Query(alias="severity")] = None,
    include_audit: Annotated[bool, Query(alias="includeAudit")] = True,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> RealtimeEventPage:
    filters = await _authorized_realtime_filter(
        RealtimeFilter(
            namespace=namespace,
            flowId=flow_id,
            executionId=execution_id,
            eventTypes=tuple(event_types or ()),
            severities=tuple(severities or ()),
            includeAudit=include_audit,
        ),
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    after_cursor = _decode_cursor(cursor)
    oldest, latest = await realtime.cursor_bounds(tenant_id=tenant_id)
    if latest is not None and after_cursor > latest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cursor is ahead")
    events = await realtime.list_events(
        tenant_id=tenant_id,
        after_cursor=after_cursor,
        filters=filters,
        limit=limit,
    )
    public_events = await _public_realtime_events(
        repository,
        events,
        tenant_id=tenant_id,
    )
    return RealtimeEventPage(
        items=public_events,
        nextCursor=_encode_cursor(events[-1].cursor) if events else cursor,
        oldestCursor=_encode_cursor(oldest) if oldest is not None else None,
        latestCursor=_encode_cursor(latest) if latest is not None else None,
        gap=after_cursor > 0 and oldest is not None and after_cursor < oldest - 1,
    )


@router_1.get(
    "/api/v1/realtime/stream",
    response_class=StreamingResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {"text/event-stream": {}},
            "description": "Cursor-resumable server-sent event stream",
        }
    },
    tags=["realtime"],
)
async def stream_realtime_events(
    request: Request,
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    cursor: Annotated[str | None, Query(description="Opaque reconnect cursor")] = None,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    namespace: str | None = None,
    flow_id: Annotated[str | None, Query(alias="flowId")] = None,
    execution_id: Annotated[UUID | None, Query(alias="executionId")] = None,
    event_types: Annotated[list[str] | None, Query(alias="eventType")] = None,
    severities: Annotated[list[RealtimeSeverity] | None, Query(alias="severity")] = None,
    include_audit: Annotated[bool, Query(alias="includeAudit")] = True,
    buffer_events: Annotated[int, Query(alias="bufferEvents", ge=1, le=1000)] = 100,
    max_events: Annotated[int, Query(alias="maxEvents", ge=1, le=10000)] = 1000,
    heartbeat_seconds: Annotated[float, Query(alias="heartbeatSeconds", ge=0.1, le=30)] = 10,
    stream_seconds: Annotated[float, Query(alias="streamSeconds", ge=1, le=60)] = 15,
) -> StreamingResponse:
    if cursor is not None and last_event_id is not None and cursor != last_event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cursor and Last-Event-ID do not match",
        )
    filters = await _authorized_realtime_filter(
        RealtimeFilter(
            namespace=namespace,
            flowId=flow_id,
            executionId=execution_id,
            eventTypes=tuple(event_types or ()),
            severities=tuple(severities or ()),
            includeAudit=include_audit,
        ),
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    after_cursor = _decode_cursor(last_event_id or cursor)
    oldest, latest = await realtime.cursor_bounds(tenant_id=tenant_id)
    if latest is not None and after_cursor > latest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cursor is ahead")

    async def events() -> AsyncIterator[str]:
        nonlocal after_cursor
        loop = asyncio.get_running_loop()
        deadline = loop.time() + stream_seconds
        next_heartbeat = loop.time() + heartbeat_seconds
        sent = 0
        if after_cursor > 0 and oldest is not None and after_cursor < oldest - 1:
            after_cursor = oldest - 1
            yield _sse_event(
                "gap",
                _encode_cursor(after_cursor),
                {
                    "requestedCursor": last_event_id or cursor,
                    "oldestAvailable": _encode_cursor(oldest),
                    "resumeCursor": _encode_cursor(after_cursor),
                },
            )
        while loop.time() < deadline and sent < max_events:
            if await request.is_disconnected():
                break
            batch = await realtime.list_events(
                tenant_id=tenant_id,
                after_cursor=after_cursor,
                filters=filters,
                limit=min(buffer_events, max_events - sent),
            )
            if batch:
                public_batch = await _public_realtime_events(
                    repository,
                    batch,
                    tenant_id=tenant_id,
                )
                for event in public_batch:
                    after_cursor = event.cursor
                    sent += 1
                    yield _sse_event(
                        event.event_type,
                        _encode_cursor(event.cursor),
                        event.model_dump(mode="json", by_alias=True),
                    )
                next_heartbeat = loop.time() + heartbeat_seconds
                continue
            if loop.time() >= next_heartbeat:
                yield f": heartbeat {datetime.now(UTC).isoformat()}\n\n"
                next_heartbeat = loop.time() + heartbeat_seconds
            await asyncio.sleep(min(0.25, heartbeat_seconds))

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "X-Amesh-Buffer-Limit": str(buffer_events),
        },
    )


@router_1.post(
    "/api/v1/webhook-subscriptions",
    response_model=ProvisionedWebhookSubscription,
    status_code=status.HTTP_201_CREATED,
    tags=["realtime"],
)
async def create_webhook_subscription(
    request: WebhookSubscriptionCreate,
    realtime: RealtimeRepositoryDependency,
    repository: RepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
) -> ProvisionedWebhookSubscription:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
        namespace=request.filters.namespace,
    )
    filters = await _authorized_realtime_filter(
        request.filters,
        repository=repository,
        authorization_service=authorization_service,
        actor=actor,
        tenant_id=tenant_id,
    )
    try:
        validate_http_destination(
            request.url,
            HttpTaskPolicy(
                allowed_hosts=settings.network_egress_allowed_hosts,
                allowed_private_hosts=frozenset(settings.core_http_allowed_private_hosts),
            ),
            resolve_dns=False,
        )
        subscription = await realtime.create_subscription(
            request.model_copy(update={"filters": filters}),
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ProvisionedWebhookSubscription(
        subscription=subscription,
        signingSecret=derive_webhook_secret(
            settings.webhook_signing_key.get_secret_value(),
            tenant_id,
            subscription.subscription_id,
            subscription.signing_version,
        ),
    )


@router_1.get(
    "/api/v1/webhook-subscriptions",
    response_model=tuple[WebhookSubscription, ...],
    tags=["realtime"],
)
async def list_webhook_subscriptions(
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> tuple[WebhookSubscription, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    return await realtime.list_subscriptions(tenant_id=tenant_id)


@router_1.post(
    "/api/v1/webhook-subscriptions/{subscription_id}/rotate-secret",
    response_model=ProvisionedWebhookSubscription,
    tags=["realtime"],
)
async def rotate_webhook_subscription_secret(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    settings: SettingsDependency,
    tenant_id: TenantDependency,
    expected_version: Annotated[int, Query(alias="expectedVersion", ge=1)],
) -> ProvisionedWebhookSubscription:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    await realtime.get_subscription(subscription_id, tenant_id=tenant_id)
    try:
        subscription = await realtime.rotate_subscription(
            subscription_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
            expected_version=expected_version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ProvisionedWebhookSubscription(
        subscription=subscription,
        signingSecret=derive_webhook_secret(
            settings.webhook_signing_key.get_secret_value(),
            tenant_id,
            subscription.subscription_id,
            subscription.signing_version,
        ),
    )


@router_1.post(
    "/api/v1/webhook-subscriptions/{subscription_id}/test",
    response_model=WebhookDelivery,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["realtime"],
)
async def test_webhook_subscription(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WebhookDelivery:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await realtime.enqueue_test(
            subscription_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router_1.get(
    "/api/v1/webhook-subscriptions/{subscription_id}/deliveries",
    response_model=tuple[WebhookDeliveryHistory, ...],
    tags=["realtime"],
)
async def list_webhook_delivery_history(
    subscription_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> tuple[WebhookDeliveryHistory, ...]:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        await realtime.get_subscription(subscription_id, tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return await realtime.list_delivery_history(
        subscription_id,
        tenant_id=tenant_id,
        limit=limit,
    )


@router_1.post(
    "/api/v1/webhook-deliveries/{delivery_id}/replay",
    response_model=WebhookDelivery,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["realtime"],
)
async def replay_webhook_delivery(
    delivery_id: UUID,
    realtime: RealtimeRepositoryDependency,
    actor: ActorDependency,
    authorization_service: AuthorizationServiceDependency,
    tenant_id: TenantDependency,
) -> WebhookDelivery:
    await authorize_request(
        authorization_service,
        actor,
        resource_type="webhook_subscription",
        action=PermissionAction.MANAGE,
        tenant_id=tenant_id,
    )
    try:
        return await realtime.replay_delivery(
            delivery_id,
            tenant_id=tenant_id,
            actor_id=str(actor.principal_id),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


async def _public_realtime_events(
    repository: ExecutionRepository,
    events: tuple[RealtimeEvent, ...],
    *,
    tenant_id: str,
) -> tuple[RealtimeEvent, ...]:
    sensitive_by_execution: dict[UUID, tuple[str, ...]] = {}
    public_events: list[RealtimeEvent] = []
    for event in events:
        sensitive_values: tuple[str, ...] = ()
        if event.execution_id is not None:
            if event.execution_id not in sensitive_by_execution:
                try:
                    execution = await repository.get_execution(
                        event.execution_id,
                        tenant_id=tenant_id,
                    )
                    flow = await repository.get_flow(
                        execution.namespace,
                        execution.flow_id,
                        tenant_id=tenant_id,
                        revision=execution.flow_revision,
                    )
                    sensitive_by_execution[event.execution_id] = tuple(
                        sensitive_execution_values(flow, execution.inputs, execution.outputs)
                    )
                except LookupError:
                    sensitive_by_execution[event.execution_id] = ()
            sensitive_values = sensitive_by_execution[event.execution_id]
        payload = redact_realtime_payload(event.payload, sensitive_values)
        public_events.append(
            event.model_copy(update={"payload": payload if isinstance(payload, dict) else {}})
        )
    return tuple(public_events)


def _sse_event(event_type: str, cursor: str, payload: dict[str, object]) -> str:
    safe_event_type = event_type.replace("\r", "").replace("\n", "")
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return f"id: {cursor}\nevent: {safe_event_type}\ndata: {data}\n\n"
