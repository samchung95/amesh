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
    ImageArtifactRef,
    ImageDisplayMetadata,
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


def _image() -> ImageArtifactRef:
    artifact = _artifact().model_copy(
        update={
            "path": "images/chart.png",
            "reference": ("nsfile:///images/chart.png?version=2&sha256=" + "a" * 64),
            "media_type": "image/png",
        }
    )
    return ImageArtifactRef(
        artifact=artifact,
        display=ImageDisplayMetadata(
            filename="chart.png",
            altText="Quarterly chart",
            widthPixels=640,
            heightPixels=480,
        ),
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

    async def upload_image(
        self,
        namespace: str,
        path: str,
        content: bytes,
        **kwargs: object,
    ) -> ImageArtifactRef:
        assert namespace == "reports"
        assert path == "images/chart.png"
        assert content == b"image-bytes"
        assert kwargs["content_type"] == "image/png"
        assert kwargs["expected_version"] == 0
        assert kwargs["alt_text"] == "Quarterly chart"
        return _image()

    async def get_image_artifact(
        self,
        namespace: str,
        path: str,
        **kwargs: object,
    ) -> ImageArtifactRef:
        assert namespace == "reports"
        assert path == "images/chart.png"
        assert kwargs["version"] == 2
        assert kwargs["alt_text"] == "Quarterly chart"
        return _image()


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

                uploaded_image = await client.put(
                    "/api/v1/namespaces/reports/images/images/chart.png",
                    params={"expectedVersion": 0, "altText": "Quarterly chart"},
                    content=b"image-bytes",
                    headers={
                        "X-Amesh-Tenant": "tenant-a",
                        "content-type": "image/png",
                    },
                )
                assert uploaded_image.status_code == 200, uploaded_image.text
                assert uploaded_image.json()["artifact"]["mediaType"] == "image/png"
                assert uploaded_image.json()["display"]["widthPixels"] == 640
                assert "objectUri" not in uploaded_image.text

                described_image = await client.get(
                    "/api/v1/namespaces/reports/images/images/chart.png",
                    params={"version": 2, "altText": "Quarterly chart"},
                    headers={"X-Amesh-Tenant": "tenant-a"},
                )
                assert described_image.status_code == 200, described_image.text
                assert described_image.json() == uploaded_image.json()
        finally:
            for dependency in overrides:
                app.dependency_overrides.pop(dependency, None)

    asyncio.run(scenario())
