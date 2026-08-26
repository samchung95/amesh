from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime, timedelta

import pytest

from amesh.domain import NamespaceFile, NamespaceFileVersion, build_artifact_reference
from amesh.executor.contracts import TaskContextRequest
from amesh.ports import ObjectMetadata, StorageBackend
from amesh.workflow.shared_resources import NamespaceResourceService, SharedResourceContextProvider


class FakeRepository:
    def __init__(self) -> None:
        self.version = NamespaceFileVersion(
            namespace="reports",
            path="reports/quarter 1.pdf",
            version=2,
            sizeBytes=7,
            checksumSha256=hashlib.sha256(b"content").hexdigest(),
            contentType="application/pdf",
            objectUri="s3://bucket/tenants/tenant-a/namespace/report",
            createdBy="operator",
            createdAt=datetime(2026, 8, 26, tzinfo=UTC),
        )

    async def list_files(
        self, namespace: str, *, tenant_id: str, actor_id: str, inherited: bool = True
    ):
        return [
            NamespaceFile(
                namespace=namespace,
                path=self.version.path,
                version=self.version.version,
                resourceVersion=3,
                sizeBytes=self.version.size_bytes,
                checksumSha256=self.version.checksum_sha256,
                contentType=self.version.content_type,
                originNamespace="reports",
                createdAt=self.version.created_at,
                updatedAt=self.version.created_at,
            )
        ]

    async def get_file_version(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> NamespaceFileVersion:
        if path != self.version.path or (version is not None and version != self.version.version):
            raise LookupError("namespace file version does not exist")
        return self.version


class FakeObjectStore:
    def __init__(self, *, checksum: str | None = None) -> None:
        self.checksum = checksum

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        assert tenant_id == "tenant-a"
        assert uri.startswith("s3://bucket/tenants/tenant-a/")
        checksum = self.checksum or hashlib.sha256(b"content").hexdigest()
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=7,
            checksum_sha256=checksum,
            content_type="application/pdf",
            backend=StorageBackend.S3,
            retention_until=datetime.now(UTC) + timedelta(days=1),
            legal_hold=True,
            lineage=("namespace-file", "reports", "reports/quarter 1.pdf"),
        )


def test_namespace_artifact_service_describes_without_exposing_object_uri() -> None:
    async def scenario() -> None:
        service = NamespaceResourceService(FakeRepository(), FakeObjectStore())
        artifact = (
            await service.list_artifacts("reports", tenant_id="tenant-a", actor_id="operator")
        )[0]
        payload = artifact.model_dump(mode="json", by_alias=True)
        assert payload["reference"] == build_artifact_reference(
            "reports/quarter 1.pdf", 2, artifact.checksum_sha256
        )
        assert payload["contentAddress"] == f"sha256:{artifact.checksum_sha256}"
        assert payload["provenance"]["lineage"][0] == "namespace-file"
        assert payload["retention"]["legalHold"] is True
        assert "objectUri" not in payload
        assert "s3://" not in str(payload)

    asyncio.run(scenario())


def test_context_provider_resolves_exact_version_and_digest() -> None:
    async def scenario() -> None:
        repository = FakeRepository()
        provider = SharedResourceContextProvider(repository, object_store=None)
        checksum = repository.version.checksum_sha256
        request = TaskContextRequest(
            tenantId="tenant-a",
            namespace="reports",
            executionId="execution",
            taskRunId="task",
            attempt=1,
            taskType="plugin.extract",
            secretScopes=(),
            declaredFiles={
                "report.pdf": build_artifact_reference(repository.version.path, 2, checksum)
            },
        )
        resources = await provider.resolve(request)
        assert resources.files == {"report.pdf": repository.version.object_uri}
        assert resources.file_references["report.pdf"].checksum_sha256 == checksum

        bad_request = request.model_copy(
            update={
                "declared_files": {
                    "report.pdf": build_artifact_reference(repository.version.path, 2, "b" * 64)
                }
            }
        )
        with pytest.raises(ValueError, match="digest"):
            await provider.resolve(bad_request)

    asyncio.run(scenario())
