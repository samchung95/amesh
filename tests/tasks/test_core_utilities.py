from __future__ import annotations

import asyncio
import threading
import zipfile
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from amesh.dsl import ResourceKind, TaskDefinition, default_resource_registry
from amesh.executor import TaskExecutionContext, TaskUserCodeError
from amesh.tasks import (
    SmtpDelivery,
    core_control_handlers,
    core_data_handlers,
    core_download_handler,
    core_file_handlers,
    core_http_handler,
    core_notification_handlers,
)
from amesh.tasks import files as file_tasks
from amesh.workflow.working_directory import WorkingDirectoryManager


def _context(*, workspace: bool = False) -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={"message": "hello"},
        outputs={"seed": {"value": 1}},
        variables={"region": "sg"},
        labels={"team": "platform"},
        trigger={"source": "manual"},
        secret_scopes=("NOTIFY",),
        secrets={"NOTIFY": "hidden"},
        workspace_scope_id="fixture" if workspace else None,
    )


def _task(task_type: str, **configuration: object) -> TaskDefinition:
    return TaskDefinition.model_validate({"id": "utility", "type": task_type, **configuration})


def test_http_auth_pagination_limits_and_ssrf_policy() -> None:
    requests: list[httpx.Request] = []

    async def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        page = request.url.params.get("page", "1")
        if page == "1":
            return httpx.Response(
                200,
                headers={"content-type": "application/json"},
                json={"items": [1, 2], "next": "?page=2"},
            )
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            json={"items": [3], "next": None},
        )

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            handler = core_http_handler(client)
            result = await handler(
                _task(
                    "core.http",
                    url="https://example.test/items?page=1",
                    auth={"type": "bearer", "token": "fixture-token"},
                    pagination={"nextUrlPath": "next", "itemsPath": "items", "maxPages": 3},
                ),
                _context(),
            )
            assert result["items"] == [1, 2, 3]
            assert result["pageCount"] == 2
            assert all(
                request.headers["authorization"] == "Bearer fixture-token" for request in requests
            )

            with pytest.raises(ValueError, match="payload limit"):
                await handler(
                    _task("core.http", url="https://example.test/items", maxResponseBytes=2),
                    _context(),
                )
            with pytest.raises(ValueError, match="blocked private"):
                await handler(_task("core.http", url="http://127.0.0.1/private"), _context())

    asyncio.run(scenario())


def test_download_and_file_pack_are_workspace_confined(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    write_threads: list[int] = []
    original_write_bytes = Path.write_bytes

    def write_bytes(self: Path, data: bytes) -> int:
        write_threads.append(threading.get_ident())
        return original_write_bytes(self, data)

    monkeypatch.setattr(Path, "write_bytes", write_bytes)

    async def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "example.test"
        return httpx.Response(200, content=b"fixture-data")

    async def scenario() -> None:
        manager = WorkingDirectoryManager(None, root=tmp_path / "workspaces")
        context = _context(workspace=True)
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            downloaded = await core_download_handler(manager, client)(
                _task(
                    "core.download",
                    url="https://example.test/file",
                    destination="input/data.txt",
                ),
                context,
            )
        assert downloaded.output["sizeBytes"] == 12

        handlers = core_file_handlers(manager)
        checksum = await handlers["core.files.checksum"](
            _task("core.files.checksum", source="input/data.txt"), context
        )
        assert checksum.output["checksum"] == (
            "85638a90a2b6d1e2f6be9814c961764f8a1be74871b15d9b05bc1c4017fd38b1"
        )
        await handlers["core.files.copy"](
            _task("core.files.copy", source="input/data.txt", destination="input/copy.txt"),
            context,
        )
        await handlers["core.files.move"](
            _task("core.files.move", source="input/copy.txt", destination="input/moved.txt"),
            context,
        )
        compressed = await handlers["core.files.compress"](
            _task(
                "core.files.compress",
                sources=["input/data.txt", "input/moved.txt"],
                destination="bundle.zip",
            ),
            context,
        )
        assert compressed.output["sizeBytes"] > 0
        extracted = await handlers["core.files.extract"](
            _task("core.files.extract", source="bundle.zip", destination="expanded"), context
        )
        assert sorted(extracted.output["files"]) == [
            "expanded/input/data.txt",
            "expanded/input/moved.txt",
        ]
        await handlers["core.files.delete"](
            _task("core.files.delete", source="input/moved.txt"), context
        )
        archive = next(tmp_path.rglob("bundle.zip"))
        assert not (archive.parent / "input" / "moved.txt").exists()

        with pytest.raises(ValueError, match="traverse"):
            await handlers["core.files.copy"](
                _task("core.files.copy", source="../escape", destination="copy"), context
            )

        bomb = archive.with_name("bomb.zip")
        with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as output:
            output.writestr("large.txt", b"0" * 20_000)
        with pytest.raises(ValueError, match="compression ratio"):
            await handlers["core.files.extract"](
                _task("core.files.extract", source="bomb.zip", destination="bomb"), context
            )

    asyncio.run(scenario())
    assert write_threads
    assert any(thread_id != threading.get_ident() for thread_id in write_threads)


def test_download_cleanup_runs_off_event_loop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = WorkingDirectoryManager(None, root=tmp_path / "workspaces")
    cleanup_threads: list[int] = []
    original_cleanup = manager.cleanup

    def cleanup(path: Path) -> None:
        cleanup_threads.append(threading.get_ident())
        original_cleanup(path)

    monkeypatch.setattr(manager, "cleanup", cleanup)

    async def respond(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"fixture-data")

    async def scenario() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            await core_download_handler(manager, client)(
                _task(
                    "core.download",
                    url="https://example.test/file",
                    destination="input/data.txt",
                ),
                _context(),
            )

    asyncio.run(scenario())
    assert cleanup_threads
    assert all(thread_id != threading.get_ident() for thread_id in cleanup_threads)


def test_file_operations_run_off_event_loop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = WorkingDirectoryManager(None, root=tmp_path / "workspaces")
    context = _context(workspace=True)
    main_thread = threading.get_ident()
    operation_threads: list[int] = []
    original_operate = file_tasks._operate

    def operate(*args: object, **kwargs: object) -> dict[str, object]:
        operation_threads.append(threading.get_ident())
        return original_operate(*args, **kwargs)

    monkeypatch.setattr(file_tasks, "_operate", operate)

    async def scenario() -> None:
        workspace = await manager.prepare(
            tenant_id=context.tenant_id,
            execution_id=str(context.execution_id),
            task_run_id=str(context.task_run_id),
            attempt_id=str(context.attempt_id),
            scope_id=context.workspace_scope_id,
            input_files={},
            file_references={},
            quota_bytes=10 * 1024 * 1024,
        )
        (workspace.path / "input.txt").write_text("input", encoding="utf-8")
        await file_tasks.core_file_handlers(manager)["core.files.copy"](
            _task("core.files.copy", source="input.txt", destination="copy.txt"), context
        )

    asyncio.run(scenario())
    assert operation_threads
    assert all(thread_id != main_thread for thread_id in operation_threads)


def test_data_control_and_notification_fixtures_are_deterministic() -> None:
    delivered: list[tuple[EmailMessage, SmtpDelivery]] = []

    async def send(message: EmailMessage, delivery: SmtpDelivery) -> None:
        delivered.append((message, delivery))

    async def webhook(request: httpx.Request) -> httpx.Response:
        return httpx.Response(202, json={"accepted": True})

    async def scenario() -> None:
        data = core_data_handlers()
        parsed_json = await data["core.data.json"](
            _task("core.data.json", operation="parse", input='{"b":2,"a":1}'), _context()
        )
        assert parsed_json["value"] == {"a": 1, "b": 2}
        parsed_yaml = await data["core.data.yaml"](
            _task("core.data.yaml", operation="parse", input="name: amesh\nready: true\n"),
            _context(),
        )
        assert parsed_yaml["value"] == {"name": "amesh", "ready": True}
        parsed_csv = await data["core.data.csv"](
            _task("core.data.csv", operation="parse", input="name,value\nalpha,1\n"),
            _context(),
        )
        assert parsed_csv["value"] == [{"name": "alpha", "value": "1"}]
        parsed_xml = await data["core.data.xml"](
            _task("core.data.xml", operation="parse", input='<root id="1"><item>ok</item></root>'),
            _context(),
        )
        assert parsed_xml["value"]["children"][0]["text"] == "ok"
        transformed = await data["core.data.text"](
            _task(
                "core.data.text",
                operation="replace",
                input="hello world",
                search="world",
                replacement="amesh",
            ),
            _context(),
        )
        assert transformed["value"] == "hello amesh"
        with pytest.raises(ValueError, match="document type"):
            await data["core.data.xml"](
                _task("core.data.xml", operation="parse", input="<!DOCTYPE x><x/>"), _context()
            )

        control = core_control_handlers()
        assert (await control["core.sleep"](_task("core.sleep", seconds=0), _context()))[
            "sleptSeconds"
        ] == 0
        assert (await control["core.assert"](_task("core.assert", value=True), _context())) == {
            "asserted": True
        }
        debug = await control["core.debug"](_task("core.debug", include=["inputs"]), _context())
        assert debug == {
            "context": {"inputs": {"message": "hello"}},
            "secretScopes": ["NOTIFY"],
            "secretsRedacted": True,
        }
        with pytest.raises(TaskUserCodeError, match="expected failure"):
            await control["core.fail"](_task("core.fail", message="expected failure"), _context())

        async with httpx.AsyncClient(transport=httpx.MockTransport(webhook)) as client:
            notifications = core_notification_handlers(http_client=client, email_sender=send)
            webhook_result = await notifications["core.notify.webhook"](
                _task("core.notify.webhook", url="https://example.test/hook", method="POST"),
                _context(),
            )
            assert webhook_result["statusCode"] == 202
            email_result = await notifications["core.notify.email"](
                _task(
                    "core.notify.email",
                    smtpHost="smtp.example.test",
                    sender="amesh@example.test",
                    recipients=["operator@example.test"],
                    subject="Workflow finished",
                    text="Success",
                ),
                _context(),
            )
        assert email_result["accepted"] is True
        assert delivered[0][1].host == "smtp.example.test"
        assert delivered[0][0].get_content().strip() == "Success"

    asyncio.run(scenario())


def test_core_catalog_exposes_utility_and_trigger_pack() -> None:
    registry = default_resource_registry()
    expected_tasks = {
        "core.http",
        "core.download",
        "core.document.extract",
        "core.files.compress",
        "core.files.extract",
        "core.files.checksum",
        "core.files.copy",
        "core.files.move",
        "core.files.delete",
        "core.data.json",
        "core.data.yaml",
        "core.data.csv",
        "core.data.xml",
        "core.data.text",
        "core.sleep",
        "core.fail",
        "core.log",
        "core.return",
        "core.debug",
        "core.assert",
        "core.notify.email",
        "core.notify.webhook",
    }
    assert all(registry.descriptor(ResourceKind.TASK, item) is not None for item in expected_tasks)
    assert all(
        registry.descriptor(ResourceKind.TRIGGER, item) is not None
        for item in {"core.manual", "core.webhook", "core.cron", "core.interval", "core.flow"}
    )
