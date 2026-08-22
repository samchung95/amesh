from __future__ import annotations

import base64
import hashlib
import hmac
import json
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime
from enum import StrEnum
from time import perf_counter
from typing import Any, Protocol
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.tasks.http import HttpTaskPolicy, validate_http_destination


class RealtimeSeverity(StrEnum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class RealtimeFilter(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    namespace: str | None = Field(default=None, min_length=1, max_length=255)
    flow_id: str | None = Field(default=None, alias="flowId", min_length=1, max_length=128)
    execution_id: UUID | None = Field(default=None, alias="executionId")
    event_types: tuple[str, ...] = Field(default=(), alias="eventTypes", max_length=64)
    severities: tuple[RealtimeSeverity, ...] = ()
    include_audit: bool = Field(default=True, alias="includeAudit")

    @model_validator(mode="after")
    def unique_values(self) -> RealtimeFilter:
        if len(self.event_types) != len(set(self.event_types)):
            raise ValueError("eventTypes must be unique")
        if len(self.severities) != len(set(self.severities)):
            raise ValueError("severities must be unique")
        return self


class RealtimeEvent(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    cursor: int = Field(ge=1)
    event_id: UUID = Field(alias="eventId")
    namespace: str | None = None
    flow_id: str | None = Field(default=None, alias="flowId")
    execution_id: UUID | None = Field(default=None, alias="executionId")
    task_run_id: UUID | None = Field(default=None, alias="taskRunId")
    event_type: str = Field(alias="eventType")
    severity: RealtimeSeverity
    payload: dict[str, Any]
    occurred_at: datetime = Field(alias="occurredAt")
    ingested_at: datetime = Field(alias="ingestedAt")


class RealtimeEventPage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    items: tuple[RealtimeEvent, ...]
    next_cursor: str | None = Field(default=None, alias="nextCursor")
    oldest_cursor: str | None = Field(default=None, alias="oldestCursor")
    latest_cursor: str | None = Field(default=None, alias="latestCursor")
    gap: bool = False


class WebhookSubscriptionCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$", max_length=128)
    url: str = Field(min_length=8, max_length=2048)
    filters: RealtimeFilter = Field(default_factory=RealtimeFilter)
    enabled: bool = True
    max_attempts: int = Field(default=8, alias="maxAttempts", ge=1, le=25)


class WebhookSubscription(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    subscription_id: UUID = Field(alias="id")
    name: str
    url: str
    filters: RealtimeFilter
    enabled: bool
    max_attempts: int = Field(alias="maxAttempts")
    signing_version: int = Field(alias="signingVersion")
    last_enqueued_cursor: int = Field(alias="lastEnqueuedCursor")
    resource_version: int = Field(alias="resourceVersion")
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ProvisionedWebhookSubscription(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    subscription: WebhookSubscription
    signing_secret: str = Field(alias="signingSecret")


class WebhookDeliveryKind(StrEnum):
    EVENT = "EVENT"
    TEST = "TEST"
    REPLAY = "REPLAY"


class WebhookDeliveryStatus(StrEnum):
    PENDING = "PENDING"
    DELIVERING = "DELIVERING"
    RETRY = "RETRY"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class WebhookDelivery(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    delivery_id: UUID = Field(alias="id")
    subscription_id: UUID = Field(alias="subscriptionId")
    event_cursor: int | None = Field(default=None, alias="eventCursor")
    event_id: UUID | None = Field(default=None, alias="eventId")
    event_type: str = Field(alias="eventType")
    event_occurred_at: datetime = Field(alias="eventOccurredAt")
    delivery_kind: WebhookDeliveryKind = Field(alias="deliveryKind")
    original_delivery_id: UUID | None = Field(default=None, alias="originalDeliveryId")
    signing_version: int = Field(alias="signingVersion")
    status: WebhookDeliveryStatus
    attempts: int
    next_attempt_at: datetime = Field(alias="nextAttemptAt")
    response_status: int | None = Field(default=None, alias="responseStatus")
    error_code: str | None = Field(default=None, alias="errorCode")
    created_at: datetime = Field(alias="createdAt")
    delivered_at: datetime | None = Field(default=None, alias="deliveredAt")


class WebhookDeliveryAttempt(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    delivery_id: UUID = Field(alias="deliveryId")
    attempt: int = Field(ge=1)
    request_timestamp: int = Field(alias="requestTimestamp")
    response_status: int | None = Field(default=None, alias="responseStatus")
    outcome: WebhookDeliveryStatus
    error_code: str | None = Field(default=None, alias="errorCode")
    attempted_at: datetime = Field(alias="attemptedAt")
    duration_ms: int = Field(alias="durationMs", ge=0)


class WebhookDeliveryHistory(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    delivery: WebhookDelivery
    attempts: tuple[WebhookDeliveryAttempt, ...]


class WebhookDeliveryClaim(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")
    delivery_id: UUID = Field(alias="id")
    subscription_id: UUID = Field(alias="subscriptionId")
    url: str
    max_attempts: int = Field(alias="maxAttempts")
    signing_version: int = Field(alias="signingVersion")
    attempt: int = Field(ge=1)
    event_cursor: int | None = Field(default=None, alias="eventCursor")
    event_id: UUID | None = Field(default=None, alias="eventId")
    event_type: str = Field(alias="eventType")
    event_occurred_at: datetime = Field(alias="eventOccurredAt")
    payload: dict[str, Any]
    sensitive_values: tuple[str, ...] = Field(default=(), alias="sensitiveValues")
    delivery_kind: WebhookDeliveryKind = Field(alias="deliveryKind")


class WebhookDeliveryRepository(Protocol):
    async def prepare_deliveries(self, *, tenant_id: str, limit: int) -> int: ...

    async def claim_deliveries(
        self, *, tenant_id: str, worker_id: str, limit: int
    ) -> tuple[WebhookDeliveryClaim, ...]: ...

    async def record_delivery_result(
        self,
        claim: WebhookDeliveryClaim,
        *,
        request_timestamp: int,
        response_status: int | None,
        error_code: str | None,
        duration_ms: int,
    ) -> WebhookDelivery: ...


PayloadRedactor = Callable[[WebhookDeliveryClaim], Awaitable[dict[str, Any]]]


def derive_webhook_secret(
    master_key: str,
    tenant_id: str,
    subscription_id: UUID,
    signing_version: int,
) -> str:
    if len(master_key.encode("utf-8")) < 32:
        raise ValueError("webhook signing key must contain at least 32 bytes")
    context = f"amesh-webhook:{tenant_id}:{subscription_id}:{signing_version}".encode()
    return (
        base64.urlsafe_b64encode(hmac.new(master_key.encode(), context, hashlib.sha256).digest())
        .decode("ascii")
        .rstrip("=")
    )


def webhook_signature(secret: str, timestamp: int, delivery_id: UUID, body: bytes) -> str:
    signed = f"{timestamp}.{delivery_id}.".encode() + body
    return "v1=" + hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()


def redact_realtime_payload(value: Any, sensitive_values: Sequence[str] = ()) -> Any:
    sensitive_keys = {
        "authorization",
        "credential",
        "credentials",
        "password",
        "secret",
        "secrets",
        "token",
        "apikey",
        "api_key",
    }
    values = {item for item in sensitive_values if item}
    if isinstance(value, dict):
        sensitive_record = value.get("sensitive") is True
        return {
            str(key): (
                "[REDACTED]"
                if str(key).replace("-", "_").lower() in sensitive_keys
                or (sensitive_record and str(key) == "value")
                else redact_realtime_payload(item, sensitive_values)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_realtime_payload(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_realtime_payload(item, sensitive_values) for item in value)
    if isinstance(value, str) and value in values:
        return "[REDACTED]"
    return value


class WebhookDispatcher:
    def __init__(
        self,
        repository: WebhookDeliveryRepository,
        *,
        signing_key: str,
        policy: HttpTaskPolicy,
        timeout_seconds: float,
        payload_redactor: PayloadRedactor | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._repository = repository
        self._signing_key = signing_key
        self._policy = policy
        self._timeout_seconds = timeout_seconds
        self._payload_redactor = payload_redactor
        self._client = client

    async def run_once(
        self,
        tenant_ids: Sequence[str],
        *,
        worker_id: str,
        limit: int,
    ) -> int:
        delivered = 0
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(follow_redirects=False)
        try:
            for tenant_id in tenant_ids:
                await self._repository.prepare_deliveries(tenant_id=tenant_id, limit=limit)
                claims = await self._repository.claim_deliveries(
                    tenant_id=tenant_id,
                    worker_id=worker_id,
                    limit=limit,
                )
                for claim in claims:
                    delivered += await self._deliver(client, claim)
        finally:
            if owns_client:
                await client.aclose()
        return delivered

    async def _deliver(self, client: httpx.AsyncClient, claim: WebhookDeliveryClaim) -> int:
        payload = (
            await self._payload_redactor(claim)
            if self._payload_redactor is not None
            else redact_realtime_payload(claim.payload, claim.sensitive_values)
        )
        envelope = {
            "schemaVersion": "amesh.webhook-event/v1",
            "deliveryId": str(claim.delivery_id),
            "eventId": str(claim.event_id) if claim.event_id is not None else None,
            "eventType": claim.event_type,
            "eventCursor": claim.event_cursor,
            "occurredAt": claim.event_occurred_at.isoformat(),
            "payload": payload,
        }
        body = json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode()
        timestamp = int(datetime.now(UTC).timestamp())
        secret = derive_webhook_secret(
            self._signing_key,
            claim.tenant_id,
            claim.subscription_id,
            claim.signing_version,
        )
        headers = {
            "Content-Type": "application/json",
            "X-Amesh-Delivery-Id": str(claim.delivery_id),
            "X-Amesh-Event-Id": str(claim.event_id or claim.delivery_id),
            "X-Amesh-Timestamp": str(timestamp),
            "X-Amesh-Signature": webhook_signature(secret, timestamp, claim.delivery_id, body),
        }
        started = perf_counter()
        response_status: int | None = None
        error_code: str | None = None
        try:
            validate_http_destination(claim.url, self._policy, resolve_dns=self._client is None)
            response = await client.post(
                claim.url,
                content=body,
                headers=headers,
                timeout=self._timeout_seconds,
            )
            response_status = response.status_code
            if not 200 <= response.status_code < 300:
                error_code = "HTTP_RESPONSE"
        except (httpx.HTTPError, OSError, ValueError) as exc:
            error_code = type(exc).__name__.upper()
        duration_ms = max(0, round((perf_counter() - started) * 1000))
        result = await self._repository.record_delivery_result(
            claim,
            request_timestamp=timestamp,
            response_status=response_status,
            error_code=error_code,
            duration_ms=duration_ms,
        )
        return int(result.status is WebhookDeliveryStatus.DELIVERED)
