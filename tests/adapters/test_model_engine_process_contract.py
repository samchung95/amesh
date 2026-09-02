from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

import amesh.adapters.codex_app_server as codex_app_server
import amesh.adapters.copilot_cli as copilot_cli
from amesh.adapters.codex_app_server import (
    CodexAppServerConfig,
    CodexAppServerError,
    CodexAppServerProtocolError,
    CodexAppServerRpcError,
    CodexAppServerTimeout,
)
from amesh.adapters.copilot_cli import (
    CopilotCliConfig,
    CopilotCliError,
    CopilotCliProtocolError,
    CopilotCliTimeout,
)
from amesh.ports.model_engines import (
    ProviderProcessError,
    ProviderProtocolError,
    ProviderTimeoutError,
)


@pytest.mark.parametrize(
    ("adapter_error", "provider_error"),
    (
        (CodexAppServerError, ProviderProcessError),
        (CodexAppServerProtocolError, ProviderProtocolError),
        (CodexAppServerRpcError, ProviderProcessError),
        (CodexAppServerTimeout, ProviderTimeoutError),
        (CopilotCliError, ProviderProcessError),
        (CopilotCliProtocolError, ProviderProtocolError),
        (CopilotCliTimeout, ProviderTimeoutError),
    ),
)
def test_model_engine_errors_use_provider_neutral_process_hierarchy(
    adapter_error: type[Exception],
    provider_error: type[Exception],
) -> None:
    assert issubclass(adapter_error, provider_error)


def test_codex_process_uses_configured_safe_environment_without_host_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeManagedProcess:
        def __init__(self, command: tuple[str, ...], **kwargs: Any) -> None:
            captured["command"] = command
            captured.update(kwargs)

        async def start(self) -> object:
            return object()

    monkeypatch.setenv("AMESH_HOST_SECRET", "must-not-reach-child")
    monkeypatch.setattr(codex_app_server, "ManagedProcess", FakeManagedProcess)
    monkeypatch.setattr(codex_app_server.shutil, "which", lambda command: command)

    config = CodexAppServerConfig(
        command=("codex", "app-server"),
        state_root=tmp_path,
        environment={"LANG": "configured-locale"},
    )
    rpc = codex_app_server._JsonRpcProcess(config, tmp_path / "home", tmp_path / "work")

    asyncio.run(rpc.start())

    environment = captured["environment"]
    assert environment["LANG"] == "configured-locale"
    assert environment["HOME"] == str(tmp_path / "home")
    assert environment["CODEX_HOME"] == str(tmp_path / "home")
    assert "AMESH_HOST_SECRET" not in environment


def test_codex_account_process_delegates_to_an_owned_temporary_cwd(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeManagedProcess:
        def __init__(self, command: tuple[str, ...], **kwargs: Any) -> None:
            del command
            captured.update(kwargs)

        async def start(self) -> object:
            return object()

    monkeypatch.setattr(codex_app_server, "ManagedProcess", FakeManagedProcess)
    monkeypatch.setattr(codex_app_server.shutil, "which", lambda command: command)

    rpc = codex_app_server._JsonRpcProcess(
        CodexAppServerConfig(command=("codex", "app-server"), state_root=tmp_path),
        tmp_path / "home",
    )

    asyncio.run(rpc.start())

    assert captured["cwd"] is None


def test_copilot_process_uses_configured_safe_environment_without_host_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeManagedProcess:
        def __init__(self, command: tuple[str, ...], **kwargs: Any) -> None:
            captured["command"] = command
            captured.update(kwargs)

        async def start(self) -> object:
            return object()

    monkeypatch.setenv("AMESH_HOST_SECRET", "must-not-reach-child")
    monkeypatch.setattr(copilot_cli, "ManagedProcess", FakeManagedProcess)
    monkeypatch.setattr(
        copilot_cli,
        "_resolve_copilot_executable",
        lambda command, environment: command,
    )

    config = CopilotCliConfig(
        command=("copilot",),
        state_root=tmp_path,
        environment={"LANG": "configured-locale"},
    )
    process = copilot_cli._CopilotProcess(
        config,
        home=tmp_path / "home",
        cwd=tmp_path / "cwd",
        args=("copilot",),
    )

    asyncio.run(process.start())

    environment = captured["environment"]
    assert environment["LANG"] == "configured-locale"
    assert environment["HOME"] == str(tmp_path / "home")
    assert environment["COPILOT_HOME"] == str(tmp_path / "home")
    assert environment["COPILOT_AUTO_UPDATE"] == "false"
    assert "AMESH_HOST_SECRET" not in environment
