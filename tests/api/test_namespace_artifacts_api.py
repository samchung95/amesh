from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from amesh.app import (
    app,
    authenticate_actor,
    get_authorization_service,
    get_namespace_resource_service,
    get_operational_control_repository,
    get_settings,
    get_tenant_service,
)
from amesh.config import Settings
from amesh.domain import (
    ActorContext,
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    PrincipalType,
)


def _artifact() -> ArtifactRef:
    checksum = "a" * 64
    return ArtifactRef(
        reference=f"nsfile:///reports%2Fquarter.pdf?version=2&sha256={checksum}",
        contentAddress=f"sha256:{checksum}",
        tenantId="tenant-a",
        namespace="reports",
        path="reports/quarter.pdf",
        version=2,
        mediaType="application/pdf",
        sizeBytes=12,
        checksumSha256=checksum,
        provenance=ArtifactProvenance(
            source="namespace-file",
            originNamespace="reports",
            createdBy="operator",
            createdAt=datetime(2026, 8, 26, tzinfo=UTC),
        ),
        retention=ArtifactRetention(),
    )


class _Service:
    async def list_artifacts(self, namespace: str, **kwargs: object) -> list[ArtifactRef]:
        assert namespace == "reports"
        assert kwargs["tenant_id"] == "tenant-a"
        return [_artifact()]

    async def get_artifact(self, namespace: str, path: str, **kwargs: object) -> ArtifactRef:
        assert namespace == "reports"
        assert path == "reports/quarter.pdf"
        assert kwargs["version"] == 2
        return _artifact()


class _Authorization:
    async def require(self, *args: object, **kwargs: object) -> None:
        del args, kwargs


class _Tenant:
    async def consume_api_request(self, tenant_id: str) -> None:
        assert tenant_id == "tenant-a"


class _Controls:
    async def evaluate(self, *args: object, **kwargs: object):
        del args, kwargs
        return type("Decision", (), {"blocked": False})()


def test_namespace_artifact_routes_return_tenant_safe_typed_references() -> None:
    async def scenario() -> None:
        settings = Settings(tenancy_mode="single", single_tenant_slug="tenant-a")
        actor = ActorContext(
            principal_id=uuid4(),
            principal_type=PrincipalType.USER,
            display="operator",
        )
        overrides = {
            get_namespace_resource_service: lambda: _Service(),
            get_authorization_service: lambda: _Authorization(),
            get_tenant_service: lambda: _Tenant(),
            get_operational_control_repository: lambda: _Controls(),
            get_settings: lambda: settings,
            authenticate_actor: lambda: actor,
        }
        app.dependency_overrides.update(overrides)
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport, base_url="http://amesh.test"
            ) as client:
                listed = await client.get(
                    "/api/v1/namespaces/reports/artifacts",
                    headers={"X-Amesh-Tenant": "tenant-a"},
                )
                assert listed.status_code == 200, listed.text
                assert listed.json()[0]["reference"].startswith("nsfile:///")
                assert "objectUri" not in listed.text
                assert "tenant-a" in listed.json()[0]["tenantId"]

                described = await client.get(
                    "/api/v1/namespaces/reports/artifacts/reports/quarter.pdf",
                    params={"version": 2},
                    headers={"X-Amesh-Tenant": "tenant-a"},
                )
                assert described.status_code == 200, described.text
                assert described.json()["version"] == 2
                assert "s3://" not in described.text
        finally:
            for dependency in overrides:
                app.dependency_overrides.pop(dependency, None)

    asyncio.run(scenario())
