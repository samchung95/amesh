from __future__ import annotations

import hashlib
import hmac
import io
import json
import zipfile
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from amesh.domain.audit import (
    AuditArtifactKind,
    AuditExportDestination,
    AuditExportFormat,
    AuditExportReceipt,
)
from amesh.ports import ObjectStore
from amesh.ports.audit_repository import AuditRepository

_PROTECTED_FIELDS = frozenset(
    {
        "apikey",
        "assertion",
        "authorization",
        "credential",
        "password",
        "privatekey",
        "secret",
        "token",
    }
)


@dataclass(frozen=True)
class AuditArtifact:
    filename: str
    content_type: str
    content: bytes
    receipt: AuditExportReceipt


class AuditArtifactService:
    def __init__(
        self,
        repository: AuditRepository,
        *,
        signing_key: str,
        object_store: ObjectStore | None = None,
    ) -> None:
        if not signing_key:
            raise ValueError("audit export signing key cannot be empty")
        self._repository = repository
        self._signing_key = signing_key.encode("utf-8")
        self._object_store = object_store

    async def export_audit(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        destination: AuditExportDestination,
        format: AuditExportFormat,
        limit: int,
        action: str | None = None,
        resource_type: str | None = None,
        outcome: str | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
    ) -> AuditArtifact:
        page = await self._repository.list_events(
            tenant_id,
            actor_id=actor_id,
            limit=limit,
            action=action,
            resource_type=resource_type,
            outcome=outcome,
            occurred_from=occurred_from,
            occurred_to=occurred_to,
            record_access=False,
        )
        records = [
            redact_protected(event.model_dump(mode="json", by_alias=True))
            for event in reversed(page.items)
        ]
        if format is AuditExportFormat.NDJSON:
            content = b"".join(_canonical(record) + b"\n" for record in records)
            extension = "ndjson"
            content_type = "application/x-ndjson"
        else:
            content = _canonical(
                {
                    "schemaVersion": "amesh.audit.export/v1",
                    "tenantId": tenant_id,
                    "events": records,
                }
            )
            extension = "json"
            content_type = "application/json"
        return await self._finalize(
            tenant_id,
            actor_id=actor_id,
            artifact_kind=AuditArtifactKind.AUDIT,
            destination=destination,
            format=format.value,
            event_count=len(records),
            extension=extension,
            content_type=content_type,
            content=content,
        )

    async def export_compliance_package(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        destination: AuditExportDestination,
        occurred_from: datetime | None,
        occurred_to: datetime | None,
        max_audit_events: int,
    ) -> AuditArtifact:
        snapshot = await self._repository.compliance_snapshot(
            tenant_id,
            actor_id=actor_id,
            occurred_from=occurred_from,
            occurred_to=occurred_to,
            max_audit_events=max_audit_events,
        )
        payload = redact_protected(snapshot.model_dump(mode="json", by_alias=True))
        sections = {f"{_snake(name)}.json": _canonical(value) for name, value in payload.items()}
        manifest_unsigned: dict[str, Any] = {
            "schemaVersion": "amesh.compliance.package/v1",
            "tenantId": tenant_id,
            "generatedAt": datetime.now(UTC).isoformat(),
            "qualification": "readiness evidence; not a certification claim",
            "sections": {
                name: {
                    "records": len(json.loads(content)),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
                for name, content in sorted(sections.items())
            },
        }
        manifest_signature = _signature(self._signing_key, _canonical(manifest_unsigned))
        manifest = {**manifest_unsigned, "signature": manifest_signature}
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in sorted(sections.items()):
                _write_zip_entry(archive, name, content)
            _write_zip_entry(archive, "manifest.json", _canonical(manifest))
        return await self._finalize(
            tenant_id,
            actor_id=actor_id,
            artifact_kind=AuditArtifactKind.COMPLIANCE,
            destination=destination,
            format="ZIP",
            event_count=len(payload["auditRecords"]),
            extension="zip",
            content_type="application/zip",
            content=buffer.getvalue(),
        )

    async def _finalize(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        artifact_kind: AuditArtifactKind,
        destination: AuditExportDestination,
        format: str,
        event_count: int,
        extension: str,
        content_type: str,
        content: bytes,
    ) -> AuditArtifact:
        checksum = hashlib.sha256(content).hexdigest()
        signature = _signature(self._signing_key, content)
        receipt = AuditExportReceipt(
            tenantId=tenant_id,
            artifactKind=artifact_kind,
            destination=destination,
            format=format,
            eventCount=event_count,
            checksumSha256=checksum,
            signature=signature,
            createdBy=actor_id,
        )
        filename = f"{artifact_kind.value.casefold()}-{receipt.export_id}.{extension}"
        if destination is AuditExportDestination.OBJECT_STORAGE:
            if self._object_store is None:
                raise RuntimeError("object storage is unavailable for audit exports")
            metadata = await self._object_store.put(
                tenant_id,
                f"audit-exports/{filename}",
                _chunks(content),
                content_type=content_type,
            )
            receipt = receipt.model_copy(update={"object_uri": metadata.uri})
        await self._repository.record_export(receipt)
        return AuditArtifact(
            filename=filename,
            content_type=content_type,
            content=content,
            receipt=receipt,
        )


def redact_protected(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): (
                "[REDACTED]"
                if str(key).casefold().replace("-", "").replace("_", "").replace(" ", "")
                in _PROTECTED_FIELDS
                else redact_protected(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_protected(item) for item in value]
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _signature(key: bytes, content: bytes) -> str:
    return "v1=" + hmac.new(key, content, hashlib.sha256).hexdigest()


def _snake(value: str) -> str:
    output: list[str] = []
    for character in value:
        if character.isupper() and output:
            output.append("_")
        output.append(character.casefold())
    return "".join(output)


def _write_zip_entry(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o600 << 16
    archive.writestr(info, content)


async def _chunks(content: bytes) -> AsyncIterator[bytes]:
    for offset in range(0, len(content), 64 * 1024):
        yield content[offset : offset + 64 * 1024]
