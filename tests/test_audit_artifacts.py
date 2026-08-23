from __future__ import annotations

import asyncio
import hashlib
import io
import json
import zipfile
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from amesh.audit import AuditArtifactService
from amesh.domain.audit import (
    AuditEvent,
    AuditEventPage,
    AuditExportDestination,
    AuditExportFormat,
    AuditExportReceipt,
    ComplianceSnapshot,
)
from amesh.ports import ObjectMetadata, StorageBackend


class AuditRepositoryStub:
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.page = AuditEventPage(
            items=(
                AuditEvent(
                    cursor=1,
                    eventId=uuid4(),
                    tenantId="default",
                    actorId="user:test",
                    action="secret.use",
                    resourceType="secret",
                    resourceId="database",
                    outcome="SUCCESS",
                    reason="completed",
                    correlationId=uuid4(),
                    traceId=uuid4(),
                    source={"component": "test"},
                    evidence={"token": "canary-token", "safe": "visible"},
                    occurredAt=now,
                    eventHash="a" * 64,
                    retentionUntil=now + timedelta(days=365),
                ),
            )
        )
        self.snapshot = ComplianceSnapshot(
            accessReviews=({"review": "complete"},),
            changeEvidence=({"change": "approved"},),
            auditRecords=({"password": "canary-password", "event": "recorded"},),
            backupRestoreEvidence=({"restore": "passed"},),
            vulnerabilityResults=({"scan": "passed"},),
            incidentRecords=({"incident": "closed"},),
            provenance=({"build": "signed"},),
        )
        self.receipts: list[AuditExportReceipt] = []

    async def list_events(self, *_args: object, **_kwargs: object) -> AuditEventPage:
        return self.page

    async def compliance_snapshot(self, *_args: object, **_kwargs: object) -> ComplianceSnapshot:
        return self.snapshot

    async def record_export(self, receipt: AuditExportReceipt) -> AuditExportReceipt:
        self.receipts.append(receipt)
        return receipt


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([chunk async for chunk in chunks])
        uri = f"s3://memory/{key}"
        self.objects[uri] = content
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            key=key,
            backend=StorageBackend.S3,
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            yield self.objects[uri]

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        del tenant_id
        self.objects.pop(uri, None)


def test_signed_audit_and_compliance_artifacts_are_redacted_and_uploadable() -> None:
    async def scenario() -> None:
        repository = AuditRepositoryStub()
        object_store = MemoryObjectStore()
        service = AuditArtifactService(  # type: ignore[arg-type]
            repository,
            signing_key="test-signing-key",
            object_store=object_store,
        )

        audit = await service.export_audit(
            "default",
            actor_id="user:auditor",
            destination=AuditExportDestination.FILE,
            format=AuditExportFormat.NDJSON,
            limit=100,
        )
        assert b"canary-token" not in audit.content
        assert b'"token":"[REDACTED]"' in audit.content
        assert audit.receipt.signature.startswith("v1=")
        assert audit.receipt.checksum_sha256 == hashlib.sha256(audit.content).hexdigest()

        package = await service.export_compliance_package(
            "default",
            actor_id="user:auditor",
            destination=AuditExportDestination.OBJECT_STORAGE,
            occurred_from=None,
            occurred_to=None,
            max_audit_events=100,
        )
        assert package.receipt.object_uri in object_store.objects
        with zipfile.ZipFile(io.BytesIO(package.content)) as archive:
            assert set(archive.namelist()) == {
                "access_reviews.json",
                "audit_records.json",
                "backup_restore_evidence.json",
                "change_evidence.json",
                "incident_records.json",
                "manifest.json",
                "provenance.json",
                "vulnerability_results.json",
            }
            manifest = json.loads(archive.read("manifest.json"))
            audit_records = archive.read("audit_records.json")
        assert manifest["qualification"] == "readiness evidence; not a certification claim"
        assert manifest["signature"].startswith("v1=")
        assert b"canary-password" not in audit_records
        assert b'"password":"[REDACTED]"' in audit_records
        assert len(repository.receipts) == 2

    asyncio.run(scenario())
