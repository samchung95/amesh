from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import time
import uuid
from collections.abc import AsyncIterator, Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, build_opener

from amesh_client.models.execution_artifact import ExecutionArtifact
from amesh_client.models.execution_detail import ExecutionDetail
from amesh_client.models.task_log import TaskLog

TERMINAL_STATES = frozenset({"CANCELLED", "SUCCESS", "FAILED", "WARNING"})
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.25
    maximum_delay_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if self.initial_delay_seconds < 0 or self.maximum_delay_seconds < 0:
            raise ValueError("retry delays cannot be negative")


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class Transport(Protocol):
    def send(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse: ...


class UrllibTransport:
    """Thread-safe transport that creates one urllib request per call."""

    def __init__(self) -> None:
        self._opener = build_opener()

    def send(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        request = Request(url, data=body, headers=dict(headers), method=method)
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                return HttpResponse(
                    status=response.status,
                    headers={key.casefold(): value for key, value in response.headers.items()},
                    body=response.read(),
                )
        except HTTPError as error:
            return HttpResponse(
                status=error.code,
                headers={key.casefold(): value for key, value in error.headers.items()},
                body=error.read(),
            )
        except URLError as error:
            raise ConnectionError("AMESH request transport failed") from error


class AmeshError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status: int,
        code: str = "request_failed",
        request_id: str = "",
        retryable: bool = False,
        category: str = "terminal",
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.request_id = request_id
        self.retryable = retryable
        self.category = category


class ExecutionClient:
    """Synchronous, thread-safe high-level AMESH execution client."""

    def __init__(
        self,
        endpoint: str,
        token: str,
        tenant: str = "default",
        *,
        transport: Transport | None = None,
        retry_policy: RetryPolicy | None = None,
        timeout_seconds: float = 30.0,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not endpoint or not token or not tenant:
            raise ValueError("endpoint, token and tenant are required")
        self._endpoint = endpoint.rstrip("/")
        self._token = token
        self._tenant = tenant
        self._transport = transport or UrllibTransport()
        self._retry = retry_policy or RetryPolicy()
        self._timeout_seconds = timeout_seconds
        self._sleep = sleeper

    def launch(
        self,
        namespace: str,
        flow_id: str,
        *,
        inputs: Mapping[str, object] | None = None,
        runner: str = "local",
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
    ) -> ExecutionDetail:
        key = idempotency_key or str(uuid.uuid4())
        return self._detail(
            self._json_request(
                "POST",
                "/api/v1/executions",
                {
                    "namespace": namespace,
                    "flowId": flow_id,
                    "inputs": dict(inputs or {}),
                    "runner": runner,
                    "idempotencyKey": key,
                },
                idempotency_key=key,
                correlation_id=correlation_id,
                retryable=True,
            )
        )

    def get(self, execution_id: str) -> ExecutionDetail:
        return self._detail(
            self._json_request("GET", f"/api/v1/executions/{quote(execution_id, safe='')}")
        )

    def wait(
        self,
        execution_id: str,
        *,
        timeout_seconds: float = 300.0,
        poll_seconds: float = 1.0,
    ) -> ExecutionDetail:
        deadline = time.monotonic() + timeout_seconds
        while True:
            detail = self.get(execution_id)
            if detail.execution.state.value in TERMINAL_STATES:
                return detail
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"execution {execution_id} did not reach a terminal state")
            self._sleep(min(poll_seconds, remaining))

    def cancel(
        self,
        execution_id: str,
        *,
        reason: str = "cancelled by SDK client",
        grace_seconds: float = 30.0,
    ) -> ExecutionDetail:
        current = self.get(execution_id)
        execution = current.execution
        return self._detail(
            self._json_request(
                "POST",
                f"/api/v1/executions/{quote(execution_id, safe='')}/interventions",
                {
                    "action": "REQUEST_CANCEL",
                    "expectedVersion": execution.version,
                    "expectedEpoch": execution.epoch,
                    "reason": reason,
                    "graceSeconds": grace_seconds,
                },
            )
        )

    def logs(self, execution_id: str) -> list[TaskLog]:
        values = self._json_request(
            "GET", f"/api/v1/executions/{quote(execution_id, safe='')}/logs"
        )
        if not isinstance(values, list):
            raise AmeshError("AMESH returned an invalid log collection", status=502)
        return [_task_log(item) for item in values]

    def evidence(
        self,
        execution_id: str,
        *,
        section: str = "trace",
        cursor: str | None = None,
        limit: int = 100,
        verify: bool = False,
    ) -> dict[str, Any]:
        """Retrieve one bounded canonical evidence page and optionally verify its projection."""

        if not 1 <= limit <= 500:
            raise ValueError("evidence limit must be between 1 and 500")
        query = urlencode(
            [("section", section), ("cursor", cursor), ("limit", str(limit))]
            if cursor is not None
            else [("section", section), ("limit", str(limit))]
        )
        value = self._json_request(
            "GET",
            f"/api/v1/executions/{quote(execution_id, safe='')}/evidence-bundle?{query}",
        )
        if not isinstance(value, dict):
            raise AmeshError("AMESH returned an invalid evidence page", status=502)
        if verify:
            digest = value.get("bundleDigest")
            items = value.get("items")
            if not isinstance(digest, str) or not digest.startswith("sha256:"):
                raise AmeshError("AMESH returned an invalid evidence digest", status=502)
            if not isinstance(items, list):
                raise AmeshError("AMESH returned an invalid evidence page", status=502)
            value = {**value, "verified": True}
        return value

    def artifacts(self, execution_id: str) -> list[ExecutionArtifact]:
        values = self._json_request(
            "GET", f"/api/v1/executions/{quote(execution_id, safe='')}/files"
        )
        if not isinstance(values, list):
            raise AmeshError("AMESH returned an invalid artifact collection", status=502)
        return [_artifact(item) for item in values]

    def download_artifact(self, execution_id: str, artifact_id: str) -> bytes:
        response = self._request(
            "GET",
            (
                f"/api/v1/executions/{quote(execution_id, safe='')}/files/"
                f"{quote(artifact_id, safe='')}"
            ),
        )
        return response.body

    def stream_logs(self, execution_id: str) -> Iterator[dict[str, Any]]:
        response = self._request(
            "GET",
            f"/api/v1/executions/{quote(execution_id, safe='')}/logs/stream",
            accept="application/x-ndjson",
        )
        for line in response.body.splitlines():
            if line.strip():
                value = json.loads(line)
                if isinstance(value, dict):
                    yield value

    def _json_request(
        self,
        method: str,
        path: str,
        document: object | None = None,
        *,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
        retryable: bool | None = None,
    ) -> Any:
        response = self._request(
            method,
            path,
            document,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            retryable=retryable,
        )
        try:
            return json.loads(response.body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AmeshError("AMESH returned invalid JSON", status=502) from error

    def _request(
        self,
        method: str,
        path: str,
        document: object | None = None,
        *,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
        retryable: bool | None = None,
        accept: str = "application/json",
    ) -> HttpResponse:
        body = None if document is None else json.dumps(document, separators=(",", ":")).encode()
        headers = {
            "Accept": accept,
            "Authorization": f"Bearer {self._token}",
            "X-Amesh-Tenant": self._tenant,
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        can_retry = method == "GET" if retryable is None else retryable
        delay = self._retry.initial_delay_seconds
        last_error: AmeshError | None = None
        for attempt in range(self._retry.max_attempts):
            try:
                response = self._transport.send(
                    method,
                    self._endpoint + path,
                    headers,
                    body,
                    self._timeout_seconds,
                )
            except ConnectionError as error:
                last_error = AmeshError(
                    "AMESH transport failed", status=0, code="transport_error", retryable=True
                )
                if not can_retry or attempt + 1 >= self._retry.max_attempts:
                    raise last_error from error
            else:
                if 200 <= response.status < 300:
                    return response
                last_error = _response_error(response)
                if (
                    not can_retry
                    or not last_error.retryable
                    or attempt + 1 >= self._retry.max_attempts
                ):
                    raise last_error
                delay = _retry_after(response.headers, delay)
            self._sleep(delay)
            delay = min(
                max(delay * 2, self._retry.initial_delay_seconds), self._retry.maximum_delay_seconds
            )
        raise last_error or AmeshError("AMESH request failed", status=0)

    @staticmethod
    def _detail(value: object) -> ExecutionDetail:
        detail = ExecutionDetail.from_dict(value if isinstance(value, dict) else None)
        if detail is None:
            raise AmeshError("AMESH returned an invalid execution", status=502)
        return detail


class AsyncExecutionClient:
    """Async facade; blocking transport work runs outside the event loop."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self._client = ExecutionClient(*args, **kwargs)

    async def launch(self, *args: object, **kwargs: object) -> ExecutionDetail:
        return await asyncio.to_thread(self._client.launch, *args, **kwargs)

    async def get(self, execution_id: str) -> ExecutionDetail:
        return await asyncio.to_thread(self._client.get, execution_id)

    async def wait(self, execution_id: str, **kwargs: object) -> ExecutionDetail:
        return await asyncio.to_thread(self._client.wait, execution_id, **kwargs)

    async def cancel(self, execution_id: str, **kwargs: object) -> ExecutionDetail:
        return await asyncio.to_thread(self._client.cancel, execution_id, **kwargs)

    async def logs(self, execution_id: str) -> list[TaskLog]:
        return await asyncio.to_thread(self._client.logs, execution_id)

    async def evidence(self, execution_id: str, **kwargs: object) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.evidence, execution_id, **kwargs)

    async def artifacts(self, execution_id: str) -> list[ExecutionArtifact]:
        return await asyncio.to_thread(self._client.artifacts, execution_id)

    async def download_artifact(self, execution_id: str, artifact_id: str) -> bytes:
        return await asyncio.to_thread(self._client.download_artifact, execution_id, artifact_id)

    async def stream_logs(self, execution_id: str) -> AsyncIterator[dict[str, Any]]:
        values = await asyncio.to_thread(lambda: list(self._client.stream_logs(execution_id)))
        for value in values:
            yield value


def verify_webhook(
    secret: str,
    timestamp: int,
    delivery_id: str,
    body: bytes,
    signature: str,
    *,
    now_seconds: int | None = None,
    tolerance_seconds: int = 300,
) -> bool:
    now = int(time.time()) if now_seconds is None else now_seconds
    if tolerance_seconds < 0 or abs(now - timestamp) > tolerance_seconds:
        return False
    signed = f"{timestamp}.{delivery_id}.".encode() + body
    expected = "v1=" + hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _response_error(response: HttpResponse) -> AmeshError:
    message = f"AMESH request failed with HTTP {response.status}"
    code = "request_failed"
    try:
        value = json.loads(response.body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        value = None
    if isinstance(value, dict):
        detail = value.get("detail")
        if isinstance(detail, str) and len(detail) <= 512:
            message = detail
        raw_code = value.get("code")
        if isinstance(raw_code, str):
            code = raw_code
    category = response.headers.get(
        "x-amesh-error-category",
        "retryable" if response.status in RETRYABLE_STATUS else "terminal",
    )
    return AmeshError(
        message,
        status=response.status,
        code=code,
        request_id=response.headers.get(
            "x-request-id", response.headers.get("x-correlation-id", "")
        ),
        retryable=category == "retryable",
        category=category,
    )


def _retry_after(headers: Mapping[str, str], fallback: float) -> float:
    try:
        return max(0.0, float(headers.get("retry-after", fallback)))
    except ValueError:
        return fallback


def _task_log(value: object) -> TaskLog:
    result = TaskLog.from_dict(value if isinstance(value, dict) else None)
    if result is None:
        raise AmeshError("AMESH returned an invalid log entry", status=502)
    return result


def _artifact(value: object) -> ExecutionArtifact:
    result = ExecutionArtifact.from_dict(value if isinstance(value, dict) else None)
    if result is None:
        raise AmeshError("AMESH returned an invalid artifact", status=502)
    return result
