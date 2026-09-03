"""Cohesive http API definitions extracted from the composition root."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping
from http import HTTPStatus
from time import perf_counter

from fastapi import (
    FastAPI,
    Request,
    Response,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from opentelemetry.trace import SpanKind
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from amesh.config import (
    get_settings,
)
from amesh.domain import (
    new_runtime_id,
)
from amesh.external_orchestration import (
    correlation_id_is_valid,
    error_category,
)
from amesh.networking import (
    ForwardedHeaderRejected,
    apply_trusted_forwarded_headers,
)
from amesh.observability import (
    HTTP_REQUEST_DURATION,
    HTTP_REQUESTS,
    observe_operation,
    propagated_trace_context,
)
from amesh.ports import (
    TenantUnavailableError,
)

LOGGER = logging.getLogger("amesh.api")


def _problem_response(
    request: Request,
    *,
    status_code: int,
    detail: str | list[dict[str, object]],
    code: str | None = None,
    headers: Mapping[str, str] | None = None,
    errors: object | None = None,
) -> JSONResponse:
    title = HTTPStatus(status_code).phrase
    problem_code = code or f"HTTP_{status_code}"
    content: dict[str, object] = {
        "type": f"urn:amesh:problem:{problem_code.lower()}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "code": problem_code,
        "instance": request.url.path,
    }
    if errors is not None:
        content["errors"] = errors
    response_headers = dict(headers or {})
    response_headers.setdefault(
        "X-Amesh-Error-Category",
        error_category(status_code, problem_code),
    )
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=response_headers,
        media_type="application/problem+json",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, (str, list)) else str(exc.detail)
    if request.url.path.startswith("/v1/"):
        return _openai_error_response(
            status_code=exc.status_code,
            message=str(detail),
            code=None,
            headers=exc.headers,
        )
    return _problem_response(
        request,
        status_code=exc.status_code,
        detail=detail,
        headers=exc.headers,
    )


async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    if request.url.path.startswith("/v1/"):
        return _openai_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed",
            code="REQUEST_VALIDATION_FAILED",
        )
    return _problem_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Request validation failed",
        code="REQUEST_VALIDATION_FAILED",
        errors=jsonable_encoder(exc.errors()),
    )


def _openai_error_response(
    *,
    status_code: int,
    message: str,
    code: str | None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": "invalid_request_error" if status_code < 500 else "server_error",
                "param": None,
                "code": code,
            }
        },
        headers=headers,
    )


async def tenant_unavailable_handler(
    request: Request,
    exc: TenantUnavailableError,
) -> JSONResponse:
    del exc
    return _problem_response(
        request,
        status_code=status.HTTP_404_NOT_FOUND,
        detail="tenant unavailable",
    )


async def observe_http(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = perf_counter()
    client_correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id_is_valid(client_correlation_id):
        invalid_response = _problem_response(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Correlation-ID must be 1-255 characters without surrounding whitespace",
            code="INVALID_CORRELATION_ID",
        )
        invalid_response.headers["X-Amesh-Error-Category"] = "terminal"
        return invalid_response
    if client_correlation_id is None:
        client_correlation_id = str(new_runtime_id())
    request.state.client_correlation_id = client_correlation_id
    try:
        settings = get_settings()
        apply_trusted_forwarded_headers(
            request.scope,
            request.headers,
            settings.network_trusted_proxy_ranges,
        )
    except ForwardedHeaderRejected as exc:
        return _problem_response(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
            code="UNTRUSTED_FORWARDED_HEADERS",
        )
    with observe_operation(
        "api",
        "request",
        carrier=request.headers,
        kind=SpanKind.SERVER,
        attributes={"http.request.method": request.method},
    ) as span:
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        status_code = str(response.status_code)
        span.set_attribute("http.route", route_path)
        span.set_attribute("http.response.status_code", response.status_code)
        HTTP_REQUESTS.labels(request.method, route_path, status_code).inc()
        HTTP_REQUEST_DURATION.labels(request.method, route_path).inc(perf_counter() - started)
        trace_context = propagated_trace_context()
        if "traceparent" in trace_context:
            response.headers["traceparent"] = trace_context["traceparent"]
        response.headers["X-Correlation-ID"] = client_correlation_id
        if response.status_code >= 400 and "X-Amesh-Error-Category" not in response.headers:
            response.headers["X-Amesh-Error-Category"] = error_category(response.status_code)
        LOGGER.info(
            "http request",
            extra={
                "http_method": request.method,
                "http_route": route_path,
                "http_status": response.status_code,
            },
        )
        return response


def install_http_handlers(application: FastAPI) -> None:
    application.exception_handler(StarletteHTTPException)(http_exception_handler)
    application.exception_handler(RequestValidationError)(request_validation_handler)
    application.exception_handler(TenantUnavailableError)(tenant_unavailable_handler)
    application.middleware("http")(observe_http)
