from __future__ import annotations

import asyncio
import hashlib
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import cast
from uuid import uuid4

import pytest

from amesh.adapters.local import LocalProcessRunner
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskCompletion,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskFileReference,
)
from amesh.executor.runner_handler import local_process_handler
from amesh.ports import (
    ObjectMetadata,
    RunnerRequest,
    RunnerStatus,
    StaleRunnerAttemptError,
    StorageBackend,
)
from amesh.workflow.working_directory import WorkingDirectoryManager


class MemoryObjectStore:
    def __init__(self, objects: dict[str, bytes] | None = None) -> None:
        self.objects = dict(objects or {})

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
        return self._metadata(tenant_id, uri, content, content_type)

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        del tenant_id

        async def chunks() -> AsyncIterator[bytes]:
            yield self.objects[uri]

        return chunks()

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return self._metadata(tenant_id, uri, self.objects[uri], None)

    async def delete(self, tenant_id: str, uri: str) -> None:
        del tenant_id
        self.objects.pop(uri, None)

    @staticmethod
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


def request(*command: str, timeout_seconds: float | None = None) -> RunnerRequest:
    return RunnerRequest(
        tenant_id="default",
        execution_id="execution-1",
        task_run_id="task-1",
        attempt_id="attempt-1",
        fencing_token=1,
        command=list(command),
        timeout_seconds=timeout_seconds,
        cancel_grace_seconds=0.1,
    )


def test_local_process_captures_successful_output() -> None:
    async def scenario() -> None:
        runner = LocalProcessRunner()
        result = await runner.run(request(sys.executable, "-c", "print('AMESH_OK')"))
        assert result.status is RunnerStatus.SUCCESS
        assert result.exit_code == 0
        assert result.outputs["stdout"].strip() == "AMESH_OK"
        assert result.outputs["stderr"] == ""

    asyncio.run(scenario())


def test_local_process_timeout_terminates_attempt() -> None:
    async def scenario() -> None:
        runner = LocalProcessRunner()
        result = await runner.run(
            request(
                sys.executable,
                "-c",
                "import time; time.sleep(5)",
                timeout_seconds=0.05,
            )
        )
        assert result.status is RunnerStatus.TIMED_OUT
        assert result.exit_code is not None

    asyncio.run(scenario())


def test_local_process_cancel_requires_current_fencing_token() -> None:
    async def scenario() -> None:
        runner = LocalProcessRunner()
        running = asyncio.create_task(
            runner.run(request(sys.executable, "-c", "import time; time.sleep(5)"))
        )
        await asyncio.sleep(0.05)
        with pytest.raises(StaleRunnerAttemptError):
            await runner.cancel("attempt-1", 2)
        await runner.cancel("attempt-1", 1)
        result = await running
        assert result.status is RunnerStatus.CANCELLED
        assert result.exit_code is not None

    asyncio.run(scenario())


def test_local_handler_materializes_collects_and_cleans_attempt_workspace(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        source_uri = "s3://memory/source.txt"
        source = b"hello workspace"
        store = MemoryObjectStore({source_uri: source})
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        task = TaskDefinition(
            id="transform",
            type="core.shell",
            command=[
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "Path('result.txt').write_text(Path('input.txt').read_text().upper())"
                ),
            ],
            inputFiles={"input.txt": source_uri},
            outputFiles=("result.txt",),
        )
        context = TaskExecutionContext(
            tenant_id="default",
            execution_id=uuid4(),
            task_run_id=uuid4(),
            attempt=1,
            attempt_id=uuid4(),
            inputs={},
            outputs={},
            variables={},
            files={"input.txt": source_uri},
            file_references={
                "input.txt": TaskFileReference(
                    uri=source_uri,
                    sizeBytes=len(source),
                    checksumSha256=hashlib.sha256(source).hexdigest(),
                )
            },
        )

        completion = await local_process_handler(LocalProcessRunner(), manager)(task, context)

        assert isinstance(completion, TaskCompletion)
        output_uri = completion.output["outputFiles"]["result.txt"]
        assert store.objects[output_uri] == b"HELLO WORKSPACE"
        assert completion.artifacts[0].logical_path == "result.txt"
        assert source_uri in completion.artifacts[0].lineage
        assert not list((tmp_path / "workspaces").rglob("attempt-*"))

    asyncio.run(scenario())


def test_local_handler_retains_failure_diagnostics_before_cleanup(tmp_path: Path) -> None:
    async def scenario() -> None:
        store = MemoryObjectStore()
        manager = WorkingDirectoryManager(store, root=tmp_path / "workspaces")
        task = TaskDefinition(
            id="fail",
            type="core.shell",
            command=[
                sys.executable,
                "-c",
                "from pathlib import Path; Path('partial.txt').write_text('partial'); raise SystemExit(7)",
            ],
            retainDiagnosticsOnFailure=True,
        )
        context = TaskExecutionContext(
            tenant_id="default",
            execution_id=uuid4(),
            task_run_id=uuid4(),
            attempt=1,
            attempt_id=uuid4(),
            inputs={},
            outputs={},
            variables={},
        )

        with pytest.raises(TaskExecutionFailure) as captured:
            await local_process_handler(LocalProcessRunner(), manager)(task, context)

        evidence = captured.value.evidence or {}
        artifacts = cast(list[dict[str, object]], evidence["artifacts"])
        assert artifacts[0].get("logicalPath") == ".amesh/diagnostics.json"
        assert b'"partial.txt"' in next(
            content for uri, content in store.objects.items() if uri.endswith("diagnostics.json")
        )
        assert not list((tmp_path / "workspaces").rglob("attempt-*"))

    asyncio.run(scenario())
