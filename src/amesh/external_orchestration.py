"""Client-neutral external orchestration contract metadata.

The profile describes the existing versioned AMESH resources that an external
client uses.  It is deliberately metadata-only: workflow semantics and domain
validation remain owned by the client and the normal flow API.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExternalOperation(BaseModel):
    """One stable operation in the external-client profile."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str = Field(min_length=1)
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(min_length=1)
    authorization: str = Field(min_length=1)
    idempotent: bool
    retryable: bool


class ExternalOrchestrationProfile(BaseModel):
    """Published, client-neutral orchestration profile."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.external-orchestration/v1"] = Field(alias="schemaVersion")
    api_version: str = Field(alias="apiVersion", min_length=1)
    operations: tuple[ExternalOperation, ...]
    request_headers: tuple[str, ...] = Field(alias="requestHeaders")
    response_headers: tuple[str, ...] = Field(alias="responseHeaders")
    error_categories: dict[str, str] = Field(alias="errorCategories")
    realtime: dict[str, str]
    webhooks: dict[str, str]
    guarantees: tuple[str, ...]


def external_orchestration_profile() -> ExternalOrchestrationProfile:
    """Return the stable profile without inspecting tenant or client state."""

    return ExternalOrchestrationProfile(
        schemaVersion="amesh.external-orchestration/v1",
        apiVersion="v1",
        operations=(
            ExternalOperation(
                name="validate",
                method="POST",
                path="/api/v1/flows/validate",
                authorization="none",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="apply",
                method="PUT",
                path="/api/v1/flows",
                authorization="flow:create|flow:update",
                idempotent=True,
                retryable=False,
            ),
            ExternalOperation(
                name="read_exact_revision",
                method="GET",
                path="/api/v1/flows/{namespace}/{flow_id}/document?revision={revision}",
                authorization="flow:view",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="launch",
                method="POST",
                path="/api/v1/executions",
                authorization="execution:execute",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="inspect",
                method="GET",
                path="/api/v1/executions/{execution_id}",
                authorization="execution:view",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="preview_control",
                method="POST",
                path="/api/v1/executions/{execution_id}/interventions/preview",
                authorization="execution:manage",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="apply_control",
                method="POST",
                path="/api/v1/executions/{execution_id}/interventions",
                authorization="execution:manage",
                idempotent=False,
                retryable=False,
            ),
            ExternalOperation(
                name="events",
                method="GET",
                path="/api/v1/realtime/stream",
                authorization="realtime:view",
                idempotent=True,
                retryable=True,
            ),
            ExternalOperation(
                name="webhook_subscription",
                method="POST",
                path="/api/v1/webhook-subscriptions",
                authorization="webhook_subscription:manage",
                idempotent=False,
                retryable=False,
            ),
        ),
        requestHeaders=(
            "Authorization",
            "X-Amesh-Tenant",
            "X-Correlation-ID",
            "Idempotency-Key",
            "If-Match",
        ),
        responseHeaders=(
            "X-Correlation-ID",
            "X-Amesh-Error-Category",
            "ETag",
            "X-Next-Cursor",
            "Last-Event-ID",
        ),
        errorCategories={
            "terminal": "The requested operation reached a terminal failure; do not retry.",
            "retryable": "The operation may be retried with the same correlation and idempotency keys.",
            "conflict": "The request conflicts with current state or optimistic concurrency.",
            "ambiguous": "The outcome is unknown; inspect the logical run before retrying.",
        },
        realtime={
            "transport": "server-sent-events",
            "cursor": "Use the SSE id as Last-Event-ID or pass cursor; resume after that cursor.",
            "gap": "A gap event identifies the oldest retained cursor; resume from resumeCursor.",
            "duplicateDelivery": "Consumers deduplicate by event id and advance the cursor only after durable handling.",
        },
        webhooks={
            "signature": "X-Amesh-Timestamp, X-Amesh-Delivery-Id and X-Amesh-Signature (v1 HMAC-SHA256).",
            "delivery": "Delivery is at least once; deduplicate by delivery id.",
            "rotation": "Signing versions rotate without invalidating the prior delivery history.",
        },
        guarantees=(
            "The same tenant and idempotency key resolves to one logical execution.",
            "Exact flow revisions are selected by revision and remain immutable after launch.",
            "Authorization and tenant isolation are enforced by the server for every data operation.",
            "Public realtime and webhook payloads are redacted before delivery.",
            "Optimistic writes require the published ETag or expected version contract.",
        ),
    )


def correlation_id_is_valid(value: str | None) -> bool:
    """Validate a client correlation value before reflecting it in a header."""

    return value is None or (
        0 < len(value) <= 255 and "\r" not in value and "\n" not in value and value.strip() == value
    )


def error_category(status_code: int, code: str | None = None) -> str:
    """Classify a public HTTP outcome for neutral client retry decisions."""

    normalized = (code or "").upper()
    if "AMBIGUOUS" in normalized or status_code == 425:
        return "ambiguous"
    if status_code == 409 or status_code == 412:
        return "conflict"
    if status_code in {408, 425, 429, 500, 502, 503, 504}:
        return "retryable"
    if status_code >= 400:
        return "terminal"
    return "success"
