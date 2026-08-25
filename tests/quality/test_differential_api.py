from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI

from amesh.quality import (
    ConfigurationPin,
    DifferentialClient,
    DifferentialService,
    DifferentialSpec,
    RunObservation,
    ShadowRunContext,
    build_differential_application_router,
    build_differential_router,
)


def _spec() -> DifferentialSpec:
    return DifferentialSpec(
        tenantId="tenant-a",
        namespace="quality",
        left={"key": "flow", "revision": 1, "digest": "sha256:" + "1" * 64},
        right={"key": "flow", "revision": 2, "digest": "sha256:" + "2" * 64},
        inputs={"value": 1},
        idempotencyKey="request-1",
    )


@pytest.mark.anyio
async def test_router_and_client_enforce_auth_tenant_and_idempotency() -> None:
    service = DifferentialService()
    authorized: list[tuple[str, str, str]] = []

    def authorize(tenant_id: str, namespace: str, action: str) -> None:
        authorized.append((tenant_id, namespace, action))

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del configuration, inputs, context
        return RunObservation(output={"ok": True})

    app = FastAPI()
    app.include_router(build_differential_router(service, execute, authorize=authorize))
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as raw:
        client = DifferentialClient(raw, tenant_id="tenant-a")
        first = await client.run(_spec())
        second = await client.run(_spec())
        fetched = await client.get("quality", "request-1")

        assert first == second == fetched
        assert authorized == [
            ("tenant-a", "quality", "execute"),
            ("tenant-a", "quality", "execute"),
            ("tenant-a", "quality", "view"),
        ]

        response = await raw.post(
            "/api/v1/namespaces/quality/differentials",
            headers={"X-Amesh-Tenant": "tenant-b"},
            json=_spec().model_dump(mode="json", by_alias=True),
        )
        assert response.status_code == 422


@pytest.mark.anyio
async def test_router_maps_authorization_denial_to_forbidden() -> None:
    def authorize(tenant_id: str, namespace: str, action: str) -> None:
        del tenant_id, namespace, action
        raise PermissionError("denied")

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del configuration, inputs, context
        return RunObservation()

    app = FastAPI()
    app.include_router(
        build_differential_router(DifferentialService(), execute, authorize=authorize)
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
        response = await client.post(
            "/api/v1/namespaces/quality/differentials",
            headers={"X-Amesh-Tenant": "tenant-a"},
            json=_spec().model_dump(mode="json", by_alias=True),
        )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_application_router_composes_tenant_and_authorization_dependencies() -> None:
    calls: list[str] = []

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del configuration, context
        return RunObservation(output=inputs)

    async def tenant_dependency() -> str:
        return "tenant-a"

    async def authorization_dependency() -> object:
        async def check(action: str) -> None:
            calls.append(action)

        return check

    async def executor_dependency() -> object:
        return execute

    class AsyncService:
        async def run(
            self,
            spec: DifferentialSpec,
            executor: object,
            *,
            actor_id: str,
        ) -> object:
            assert actor_id == "actor-a"
            return service.run(spec, executor)  # type: ignore[arg-type]

        async def get(
            self,
            tenant_id: str,
            namespace: str,
            idempotency_key: str,
        ) -> object:
            return service.get(tenant_id, namespace, idempotency_key)

    async def service_dependency() -> object:
        return AsyncService()

    async def actor_dependency() -> str:
        return "actor-a"

    service = DifferentialService()
    app = FastAPI()
    app.include_router(
        build_differential_application_router(
            service_dependency,
            executor_dependency,
            tenant_dependency,
            authorization_dependency,
            actor_dependency,
        )
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://amesh.test") as client:
        response = await client.post(
            "/api/v1/namespaces/quality/differentials",
            json=_spec().model_dump(mode="json", by_alias=True),
        )
        assert response.status_code == 200
        fetched = await client.get("/api/v1/namespaces/quality/differentials/request-1")

    assert fetched.status_code == 200
    assert calls == ["execute", "view"]
