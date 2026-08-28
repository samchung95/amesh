from __future__ import annotations

import asyncio
import base64
from collections.abc import Callable, Coroutine
from functools import wraps
from types import SimpleNamespace
from typing import Any

from amesh.operator.kubernetes import KubernetesGateway


def _async_test[**P](function: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(function)
    def run(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(function(*args, **kwargs))

    return run


class FakeCore:
    def __init__(self) -> None:
        self.events: list[tuple[str, Any]] = []

    def read_namespaced_secret(self, name: str, namespace: str) -> SimpleNamespace:
        assert (namespace, name) == ("amesh-system", "operator-token")
        return SimpleNamespace(data={"token": base64.b64encode(b"rotated-token").decode()})

    def create_namespaced_event(self, namespace: str, body: object) -> None:
        self.events.append((namespace, body))


@_async_test
async def test_gateway_reads_and_decodes_named_secret_key() -> None:
    gateway = KubernetesGateway(object(), FakeCore())
    assert await gateway.read_secret("amesh-system", "operator-token", "token") == "rotated-token"


@_async_test
async def test_gateway_emits_core_v1_event() -> None:
    core = FakeCore()
    gateway = KubernetesGateway(object(), core)

    await gateway.emit_event(
        {
            "apiVersion": "platform.amesh.io/v1alpha1",
            "kind": "AmeshKeyValue",
            "metadata": {
                "name": "operator-key",
                "namespace": "amesh-system",
                "uid": "resource-uid",
                "resourceVersion": "7",
            },
        },
        event_type="Normal",
        reason="Reconciled",
        message="desired state applied",
    )

    assert core.events[0][0] == "amesh-system"
    event = core.events[0][1]
    assert event.reason == "Reconciled"
    assert event.involved_object.kind == "AmeshKeyValue"
