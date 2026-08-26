from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest
from pypdf import PdfWriter

from amesh.dsl import ResourceKind, TaskDefinition, default_resource_registry
from amesh.executor import TaskExecutionContext, TaskFileReference
from amesh.ports import ObjectMetadata, StorageBackend
from amesh.tasks import core_document_extract_handler
from amesh.workflow.working_directory import WorkingDirectoryManager


class _MemoryObjectStore:
    def __init__(self, objects: dict[str, bytes]) -> None:
        self.objects = dict(objects)

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
        return _metadata(tenant_id, uri, content, content_type=content_type)

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            yield self.objects[uri]

        return chunks()

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return _metadata(tenant_id, uri, self.objects[uri])


def _metadata(
    tenant_id: str, uri: str, content: bytes, *, content_type: str | None = None
) -> ObjectMetadata:
    return ObjectMetadata(
        uri=uri,
        tenant_id=tenant_id,
        size=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        content_type=content_type,
        backend=StorageBackend.S3,
    )


def _pdf(text: str) -> bytes:
    return _pdf_pages(text)


def _pdf_pages(*texts: str) -> bytes:
    page_count = len(texts)
    font_number = 3 + 2 * page_count
    kids = " ".join(f"{3 + 2 * index} 0 R" for index in range(page_count))
    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {page_count} >>".encode(),
    ]
    for index, text in enumerate(texts):
        page_number = 3 + 2 * index
        content_number = page_number + 1
        stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
        bodies.extend(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_number} 0 R >> >> /Contents {content_number} 0 R >>".encode(),
                b"<< /Length "
                + str(len(stream)).encode()
                + b" >>\nstream\n"
                + stream
                + b"\nendstream",
            )
        )
    bodies.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(payload))
        payload.extend(f"{number} 0 obj\n".encode())
        payload.extend(body)
        payload.extend(b"\nendobj\n")
    xref = len(payload)
    payload.extend(f"xref\n0 {len(bodies) + 1}\n".encode())
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode())
    payload.extend(
        f"trailer\n<< /Size {len(bodies) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(payload)


def _encrypted_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("password")
    from io import BytesIO

    stream = BytesIO()
    writer.write(stream)
    return stream.getvalue()


def _artifact(
    *, checksum: str, size: int, tenant: str = "default", namespace: str = "docs"
) -> dict[str, object]:
    return {
        "schemaVersion": "amesh.artifact-ref/v1",
        "reference": f"nsfile:///documents/report.pdf?version=1&sha256={checksum}",
        "contentAddress": f"sha256:{checksum}",
        "tenantId": tenant,
        "namespace": namespace,
        "path": "documents/report.pdf",
        "version": 1,
        "mediaType": "application/pdf",
        "sizeBytes": size,
        "checksumSha256": checksum,
        "provenance": {
            "source": "namespace-file",
            "originNamespace": namespace,
            "createdBy": "test",
            "createdAt": "2026-08-26T00:00:00Z",
            "lineage": ["namespace-file", namespace, "documents/report.pdf"],
        },
        "retention": {"retentionUntil": None, "legalHold": False},
    }


def _context(uri: str, content: bytes) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
        namespace="docs",
        files={"document.pdf": uri},
        file_references={
            "document.pdf": TaskFileReference(
                uri=uri,
                sizeBytes=len(content),
                checksumSha256=hashlib.sha256(content).hexdigest(),
            )
        },
    )


def test_document_extractor_returns_typed_pages_chunks_and_provenance(tmp_path: Path) -> None:
    content = _pdf("Hello AMESH document")
    uri = "s3://memory/source/report.pdf"
    store = _MemoryObjectStore({uri: content})
    manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
    task = TaskDefinition.model_validate(
        {
            "id": "extract",
            "type": "core.document.extract",
            "artifact": _artifact(checksum=hashlib.sha256(content).hexdigest(), size=len(content)),
            "source": "document.pdf",
            "limits": {
                "maxBytes": 100_000,
                "maxPages": 5,
                "maxTokens": 100,
                "chunkTokens": 3,
                "wallTimeSeconds": 10,
            },
            "inputFiles": {"document.pdf": "nsfile:///documents/report.pdf?version=1"},
        }
    )

    async def scenario() -> None:
        completion = await core_document_extract_handler(manager)(task, _context(uri, content))
        assert "uri" not in completion.output["source"]
        assert completion.output["source"]["reference"].startswith("nsfile:///")
        assert completion.output["extractor"]["parserVersion"] == "6.16.1"
        assert completion.output["extractor"]["parserContentDigest"].startswith("sha256:")
        assert completion.output["pages"][0]["pageNumber"] == 1
        assert completion.output["pages"][0]["text"]
        assert completion.output["chunks"]
        assert completion.output["chunks"][0]["sourceLocators"][0]["pageNumber"] == 1
        assert len(completion.artifacts) == 1
        assert completion.artifacts[0].logical_path == "document-result.json"

    asyncio.run(scenario())


def test_document_extractor_rejects_cross_tenant_artifact(tmp_path: Path) -> None:
    content = _pdf("Hello AMESH document")
    uri = "s3://memory/source/report.pdf"
    store = _MemoryObjectStore({uri: content})
    manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
    base = {
        "id": "extract",
        "type": "core.document.extract",
        "artifact": _artifact(
            checksum=hashlib.sha256(content).hexdigest(), size=len(content), tenant="other"
        ),
        "source": "document.pdf",
        "limits": {"maxTokens": 100, "wallTimeSeconds": 10},
    }

    async def scenario() -> None:
        with pytest.raises(ValueError, match="another tenant"):
            await core_document_extract_handler(manager)(
                TaskDefinition.model_validate(base), _context(uri, content)
            )

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("content", "media_type", "limits", "message"),
    [
        (b"not-a-pdf", "application/pdf", {}, "not a PDF"),
        (b"%PDF-1.4\nmalformed", "application/pdf", {}, "parser failed"),
        (_pdf("one two three"), "text/plain", {}, "unsupported document media type"),
        (_pdf("one two three"), "application/pdf", {"maxBytes": 1}, "maxBytes"),
        (_pdf("one two three"), "application/pdf", {"maxTokens": 1}, "maxTokens"),
        (_pdf_pages("first", "second"), "application/pdf", {"maxPages": 1}, "maxPages"),
        (_encrypted_pdf(), "application/pdf", {}, "encrypted PDFs"),
    ],
)
def test_document_extractor_enforces_format_and_resource_limits(
    tmp_path: Path,
    content: bytes,
    media_type: str,
    limits: dict[str, object],
    message: str,
) -> None:
    uri = "s3://memory/source/report.pdf"
    checksum = hashlib.sha256(content).hexdigest()
    store = _MemoryObjectStore({uri: content})
    manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
    artifact = _artifact(checksum=checksum, size=len(content))
    artifact["mediaType"] = media_type
    task = TaskDefinition.model_validate(
        {
            "id": "extract",
            "type": "core.document.extract",
            "artifact": artifact,
            "source": "document.pdf",
            "limits": limits,
        }
    )

    async def scenario() -> None:
        with pytest.raises(ValueError, match=message):
            await core_document_extract_handler(manager)(task, _context(uri, content))

    asyncio.run(scenario())


def test_document_extractor_rejects_unsafe_source_and_timeout(tmp_path: Path) -> None:
    content = _pdf("hello")
    uri = "s3://memory/source/report.pdf"
    store = _MemoryObjectStore({uri: content})
    manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
    artifact = _artifact(checksum=hashlib.sha256(content).hexdigest(), size=len(content))

    async def scenario() -> None:
        unsafe = TaskDefinition.model_validate(
            {
                "id": "extract",
                "type": "core.document.extract",
                "artifact": artifact,
                "source": "../report.pdf",
                "limits": {},
            }
        )
        with pytest.raises(ValueError, match="relative POSIX"):
            await core_document_extract_handler(manager)(unsafe, _context(uri, content))
        timeout = TaskDefinition.model_validate(
            {
                "id": "extract",
                "type": "core.document.extract",
                "artifact": artifact,
                "source": "document.pdf",
                "limits": {"wallTimeSeconds": 0.0001},
            }
        )
        with pytest.raises(ValueError, match="timed out"):
            await core_document_extract_handler(manager)(timeout, _context(uri, content))

    asyncio.run(scenario())


def test_document_extractor_enforces_task_output_limit_before_collecting(tmp_path: Path) -> None:
    content = _pdf("hello output")
    uri = "s3://memory/source/report.pdf"
    store = _MemoryObjectStore({uri: content})
    manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
    task = TaskDefinition.model_validate(
        {
            "id": "extract",
            "type": "core.document.extract",
            "artifact": _artifact(checksum=hashlib.sha256(content).hexdigest(), size=len(content)),
            "source": "document.pdf",
            "limits": {"wallTimeSeconds": 10},
            "contract": {"resourceLimits": {"maxOutputBytes": 10}},
        }
    )

    async def scenario() -> None:
        with pytest.raises(ValueError, match="maxOutputBytes"):
            await core_document_extract_handler(manager)(task, _context(uri, content))
        assert list(store.objects) == [uri]

    asyncio.run(scenario())


def test_document_extractor_registry_accepts_guided_workflow_shape() -> None:
    content = _pdf("guided")
    checksum = hashlib.sha256(content).hexdigest()
    configuration = {
        "artifact": _artifact(checksum=checksum, size=len(content)),
        "source": "document.pdf",
        "limits": {"maxBytes": 100_000, "maxPages": 10, "maxTokens": 100},
        "inputFiles": {"document.pdf": "nsfile:///documents/report.pdf?version=1"},
        "outputFiles": ["document-result.json"],
    }
    issues = default_resource_registry().validate(
        ResourceKind.TASK, "core.document.extract", configuration
    )
    assert issues == ()
