from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import yaml
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import (
    PostgresAuthorizationRepository,
    PostgresExecutionRepository,
    PostgresMetadataRepository,
    PostgresSharedResourceRepository,
    PostgresTaskCacheRepository,
    PostgresTenantRepository,
)
from amesh.app import (
    app,
    get_authorization_service,
    get_metadata_repository,
    get_namespace_resource_service,
    get_repository,
    get_shared_resource_repository,
    get_task_cache_repository,
    get_tenant_service,
)
from amesh.authorization import AuthorizationService
from amesh.config import Settings, get_settings
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.plugin_sdk import DocumentArtifactRef, DocumentExtractResult
from amesh.storage.factory import build_object_store
from amesh.tenancy import TenantService
from amesh.workflow.shared_resources import NamespaceResourceService

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def _pdf(text: str) -> bytes:
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    bodies = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
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


def test_uploaded_pdf_flows_through_typed_extraction_and_evidence() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")

        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        settings = Settings(
            database_url=database.database_url,
            amesh_admin_token="test-token",
            object_storage_backend="s3",
            object_storage_endpoint="http://localhost:9000",
            object_storage_bucket="amesh",
            object_storage_access_key="minio",
            object_storage_secret_key="minio-development-only",
        )
        repository = PostgresExecutionRepository(engine)
        shared_resources = PostgresSharedResourceRepository(engine)
        resource_service = NamespaceResourceService(
            shared_resources,
            build_object_store(settings),
        )
        app.dependency_overrides[get_repository] = lambda: repository
        app.dependency_overrides[get_task_cache_repository] = lambda: PostgresTaskCacheRepository(
            engine
        )
        app.dependency_overrides[get_shared_resource_repository] = lambda: shared_resources
        app.dependency_overrides[get_namespace_resource_service] = lambda: resource_service
        app.dependency_overrides[get_metadata_repository] = lambda: PostgresMetadataRepository(
            engine
        )
        app.dependency_overrides[get_authorization_service] = lambda: AuthorizationService(
            PostgresAuthorizationRepository(engine)
        )
        app.dependency_overrides[get_tenant_service] = lambda: TenantService(
            PostgresTenantRepository(engine)
        )
        app.dependency_overrides[get_settings] = lambda: settings

        namespace = f"tests.documents.{uuid4().hex}"
        headers = {"authorization": "Bearer test-token"}
        content = _pdf("Hello AMESH document")
        checksum = hashlib.sha256(content).hexdigest()
        transport = httpx.ASGITransport(app=app)
        try:
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://amesh.test",
            ) as client:
                uploaded = await client.put(
                    f"/api/v1/namespaces/{namespace}/files/documents/report.pdf",
                    content=content,
                    headers={**headers, "content-type": "application/pdf"},
                )
                assert uploaded.status_code == 200, uploaded.text
                assert uploaded.json()["version"] == 1

                listed = await client.get(
                    f"/api/v1/namespaces/{namespace}/artifacts",
                    headers=headers,
                )
                assert listed.status_code == 200, listed.text
                assert len(listed.json()) == 1
                artifact_payload = listed.json()[0]
                artifact = DocumentArtifactRef.model_validate(artifact_payload)
                assert artifact.reference.startswith("nsfile:///documents/report.pdf?")
                assert artifact.content_address == f"sha256:{checksum}"
                assert artifact.checksum_sha256 == checksum
                assert artifact.size_bytes == len(content)
                assert artifact.media_type == "application/pdf"
                assert artifact.namespace == namespace
                assert artifact.provenance.source == "namespace-file"
                assert artifact.provenance.origin_namespace == namespace
                assert artifact.provenance.lineage[:3] == (
                    "namespace-file",
                    namespace,
                    "documents/report.pdf",
                )
                assert "objectUri" not in listed.text
                assert '"uri"' not in listed.text
                assert "s3://" not in listed.text

                described = await client.get(
                    f"/api/v1/namespaces/{namespace}/artifacts/documents/report.pdf",
                    params={"version": artifact.version},
                    headers=headers,
                )
                assert described.status_code == 200, described.text
                assert described.json() == artifact_payload

                flow_document = {
                    "id": "document-pipeline",
                    "namespace": namespace,
                    "tasks": [
                        {
                            "id": "extract",
                            "type": "core.document.extract",
                            "source": "document.pdf",
                            "artifact": artifact_payload,
                            "inputFiles": {"document.pdf": artifact.reference},
                            "limits": {
                                "maxBytes": 100_000,
                                "maxPages": 5,
                                "maxTokens": 100,
                                "chunkTokens": 3,
                                "wallTimeSeconds": 10,
                            },
                        },
                        {
                            "id": "consume",
                            "type": "core.return",
                            "dependsOn": ["extract"],
                            "value": {
                                "text": "{{ outputs.extract.text }}",
                                "tokenCount": "{{ outputs.extract.tokenCount }}",
                                "sourceReference": "{{ outputs.extract.source.reference }}",
                            },
                        },
                    ],
                }
                applied = await client.put(
                    "/api/v1/flows",
                    content=yaml.safe_dump(flow_document, sort_keys=False),
                    headers={**headers, "content-type": "application/yaml"},
                )
                assert applied.status_code == 200, applied.text

                executed = await client.post(
                    "/api/v1/executions",
                    json={"namespace": namespace, "flowId": "document-pipeline"},
                    headers=headers,
                )
                assert executed.status_code == 200, executed.text
                execution_payload = executed.json()
                assert execution_payload["execution"]["state"] == "SUCCESS"
                execution_id = execution_payload["execution"]["execution_id"]
                task_runs = {item["task_id"]: item for item in execution_payload["taskRuns"]}

                extracted = DocumentExtractResult.model_validate(task_runs["extract"]["result"])
                assert extracted.source == artifact
                assert extracted.text == "Hello AMESH document"
                assert extracted.token_count == 3
                assert extracted.pages[0].text == "Hello AMESH document"
                assert extracted.pages[0].source_locator.page_number == 1
                assert extracted.chunks[0].source_locators[0].page_number == 1
                assert "s3://" not in json.dumps(extracted.model_dump(mode="json"))

                assert task_runs["consume"]["result"] == {
                    "value": {
                        "text": "Hello AMESH document",
                        "tokenCount": 3,
                        "sourceReference": artifact.reference,
                    }
                }

                files = await client.get(
                    f"/api/v1/executions/{execution_id}/files",
                    headers=headers,
                )
                assert files.status_code == 200, files.text
                assert len(files.json()) == 1
                result_file = files.json()[0]
                assert result_file["logical_path"] == "document-result.json"
                assert result_file["media_type"] == "application/json"
                assert result_file["size_bytes"] > 0
                assert f"execution:{execution_id}" in result_file["lineage"]
                assert "workspace-path:document-result.json" in result_file["lineage"]

                downloaded = await client.get(
                    f"/api/v1/executions/{execution_id}/files/{result_file['artifact_id']}",
                    headers=headers,
                )
                assert downloaded.status_code == 200, downloaded.text
                assert (
                    result_file["checksum_sha256"] == hashlib.sha256(downloaded.content).hexdigest()
                )
                assert json.loads(downloaded.content) == extracted.model_dump(
                    mode="json", by_alias=True
                )

                evidence = await client.get(
                    f"/api/v1/executions/{execution_id}/evidence",
                    headers=headers,
                )
                assert evidence.status_code == 200, evidence.text
                evidence_items = evidence.json()["items"]
                assert {item["kind"] for item in evidence_items} >= {
                    "STATE",
                    "OUTPUT",
                    "ARTIFACT",
                }
                assert [item["cursor"] for item in evidence_items] == sorted(
                    item["cursor"] for item in evidence_items
                )
                assert artifact.reference in evidence.text
        finally:
            app.dependency_overrides.clear()
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
