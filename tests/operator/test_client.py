from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

import httpx
import pytest

from amesh.operator.client import AmeshApiClient, AmeshApiError, ResourceIdentity
from amesh.operator.model import RESOURCE_DESCRIPTORS, OperatorTarget, SecretReference


def _async_test[**P](function: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(function)
    def run(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(function(*args, **kwargs))

    return run


def _descriptor(kind: str):
    return next(item for item in RESOURCE_DESCRIPTORS if item.kind == kind)


def _target() -> OperatorTarget:
    return OperatorTarget(
        tenant="default",
        endpoint="https://amesh.test",
        credential=SecretReference("amesh-system", "admin", "token"),
    )


@_async_test
async def test_client_reads_flow_document_and_revision_without_server_defaults() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer secret-token"
        assert request.headers["x-amesh-tenant"] == "default"
        return httpx.Response(
            200,
            request=request,
            json={
                "namespace": "examples",
                "flowId": "hello",
                "revision": 7,
                "semanticHash": "sha256:server",
                "document": {"id": "hello", "namespace": "examples", "tasks": []},
            },
        )

    client = AmeshApiClient(transport=httpx.MockTransport(handler))
    try:
        remote = await client.read(
            _descriptor("AmeshFlow"),
            ResourceIdentity("default", "examples", "hello"),
            _target(),
            "secret-token",
        )
    finally:
        await client.close()

    assert remote is not None
    assert remote.revision == "7"
    assert remote.document == {"id": "hello", "namespace": "examples", "tasks": []}


@_async_test
async def test_client_error_never_includes_response_body() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request, text="plaintext-secret-in-response")

    client = AmeshApiClient(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(AmeshApiError) as raised:
            await client.read(
                _descriptor("AmeshKeyValue"),
                ResourceIdentity("default", "examples", "hello"),
                _target(),
                "secret-token",
            )
    finally:
        await client.close()

    assert "plaintext-secret-in-response" not in str(raised.value)
    assert "secret-token" not in str(raised.value)
