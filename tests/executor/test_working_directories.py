from __future__ import annotations

import asyncio
import hashlib
import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.local import LocalProcessRunner
from amesh.adapters.postgres import PostgresExecutionRepository, PostgresMetadataRepository
from amesh.domain import ExecutionState
from amesh.dsl.models import FlowDefinition
from amesh.executor import InProcessExecutor, local_process_handler
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.ports import ObjectMetadata, StorageBackend
from amesh.workflow.working_directory import WorkingDirectoryManager

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class MemoryObjectStore:
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
        return _metadata(tenant_id, uri, content, content_type)

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            yield self.objects[uri]

        return chunks()

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return _metadata(tenant_id, uri, self.objects[uri], None)

    async def delete(self, tenant_id: str, uri: str) -> None:
        del tenant_id
        self.objects.pop(uri, None)


def _metadata(
    tenant_id: str,
    uri: str,
    content: bytes,
    content_type: str | None,
) -> ObjectMetadata:
    return ObjectMetadata(
        uri=uri,
        tenant_id=tenant_id,
        size=len(content),
        checksum_sha256=hashlib.sha256(content).hexdigest(),
        content_type=content_type,
        backend=StorageBackend.S3,
    )


def test_shared_working_directory_moves_files_and_persists_lineage(tmp_path: Path) -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, migration_directory())
        engine = create_async_engine(database.database_url)
        source_uri = "s3://memory/source.txt"
        store = MemoryObjectStore({source_uri: b"hello shared directory"})
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        repository = PostgresExecutionRepository(engine)
        metadata = PostgresMetadataRepository(engine)
        flow = FlowDefinition.model_validate(
            {
                "id": "shared_workspace",
                "namespace": "tests.workspace",
                "tasks": [
                    {
                        "id": "workspace",
                        "type": "core.workingDirectory",
                        "inputFiles": {"source.txt": source_uri},
                        "outputFiles": ["final.txt"],
                        "workspaceQuotaBytes": 1_000_000,
                        "maxConcurrency": 1,
                        "tasks": [
                            {
                                "id": "prepare",
                                "type": "core.shell",
                                "command": [
                                    sys.executable,
                                    "-c",
                                    (
                                        "from pathlib import Path; "
                                        "Path('intermediate.txt').write_text("
                                        "Path('source.txt').read_text().upper())"
                                    ),
                                ],
                            },
                            {
                                "id": "finish",
                                "type": "core.shell",
                                "command": [
                                    sys.executable,
                                    "-c",
                                    (
                                        "from pathlib import Path; "
                                        "Path('final.txt').write_text("
                                        "Path('intermediate.txt').read_text() + '!')"
                                    ),
                                ],
                            },
                        ],
                    }
                ],
            }
        )
        executor = InProcessExecutor(
            repository,
            handlers={
                "core.shell": local_process_handler(LocalProcessRunner(), manager),
            },
            object_store=store,
            workspace_manager=manager,
        )
        try:
            execution_id = await executor.create_execution(flow, tenant_id="default")
            completed = await executor.run_to_completion(
                flow,
                execution_id,
                tenant_id="default",
            )

            assert completed.state is ExecutionState.SUCCESS
            parent = next(item for item in completed.task_runs if item.task_id == "workspace")
            assert parent.result is not None
            output_uri = parent.result["outputFiles"]["final.txt"]
            assert store.objects[output_uri] == b"HELLO SHARED DIRECTORY!"
            artifacts = await metadata.list_artifacts(execution_id, tenant_id="default")
            assert len(artifacts) == 1
            assert artifacts[0].logical_path == "final.txt"
            assert source_uri in artifacts[0].lineage
            assert not list((tmp_path / "workspaces").rglob("shared-*"))
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
