from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

from amesh.adapters._managed_process import (
    SAFE_HOST_ENVIRONMENT_KEYS,
    ManagedProcess,
    ManagedProcessProtocolError,
    ManagedProcessTimeout,
    managed_process_environment,
)


def _command(script: str) -> tuple[str, ...]:
    return (sys.executable, "-c", script)


def _environment() -> dict[str, str]:
    return managed_process_environment(
        host_environment={"PATH": os.environ.get("PATH", "")},
    )


def _process(
    command: tuple[str, ...],
    *,
    frame_limit_bytes: int = 128,
    timeout_seconds: float = 1,
    cancel_grace_seconds: float = 0.05,
    cwd: Path | None = None,
    owns_cwd: bool = False,
) -> ManagedProcess:
    return ManagedProcess(
        command,
        environment=_environment(),
        frame_limit_bytes=frame_limit_bytes,
        timeout_seconds=timeout_seconds,
        cancel_grace_seconds=cancel_grace_seconds,
        cwd=cwd,
        owns_cwd=owns_cwd,
    )


def test_managed_environment_is_exactly_allowlisted_and_excludes_host_secrets() -> None:
    source = {key: f"safe-{key.lower()}" for key in SAFE_HOST_ENVIRONMENT_KEYS}
    source.update(
        {
            "HOME": "host-home",
            "OPENROUTER_API_KEY": "host-secret",
            "GITHUB_TOKEN": "host-secret",
            "AWS_SECRET_ACCESS_KEY": "host-secret",
        }
    )

    environment = managed_process_environment(host_environment=source)

    assert set(environment) == set(SAFE_HOST_ENVIRONMENT_KEYS)
    assert environment["PATH"] == "safe-path"
    assert "HOME" not in environment
    assert "OPENROUTER_API_KEY" not in environment
    assert "GITHUB_TOKEN" not in environment
    assert "AWS_SECRET_ACCESS_KEY" not in environment


def test_managed_environment_accepts_only_configured_safe_keys_and_explicit_overrides() -> None:
    environment = managed_process_environment(
        {"PATH": "configured-path", "LANG": "configured-lang"},
        overrides={"HOME": "derived-home"},
        host_environment={"PATH": "host-path", "LANG": "host-lang"},
    )

    assert environment["PATH"] == "configured-path"
    assert environment["LANG"] == "configured-lang"
    assert environment["HOME"] == "derived-home"

    with pytest.raises(ValueError, match=r"unsupported keys.*OPENROUTER_API_KEY"):
        managed_process_environment(
            {"OPENROUTER_API_KEY": "must-be-rejected"},
            host_environment={},
        )


@pytest.mark.parametrize(
    "script",
    (
        "import sys; sys.stdout.write('x' * 4096 + '\\n'); sys.stdout.flush()",
        "import sys, time; sys.stdout.write('x' * 4096); sys.stdout.flush(); time.sleep(10)",
    ),
    ids=("terminated-line", "unterminated-line"),
)
def test_oversized_stdout_fails_before_unbounded_buffering_and_tears_down(
    script: str,
) -> None:
    async def scenario() -> None:
        managed = _process(_command(script))
        process = await managed.start()
        try:
            with pytest.raises(ManagedProcessProtocolError, match="frame exceeds"):
                await managed.readline()
        finally:
            await managed.close()
        assert process.returncode is not None

    asyncio.run(scenario())


def test_managed_process_read_and_wait_have_per_operation_timeouts() -> None:
    async def scenario() -> None:
        for operation in ("read", "wait"):
            managed = _process(_command("import time; time.sleep(10)"))
            await managed.start()
            try:
                with pytest.raises(ManagedProcessTimeout, match="timed out"):
                    if operation == "read":
                        await managed.readline(timeout_seconds=0.01)
                    else:
                        await managed.wait(timeout_seconds=0.01)
            finally:
                await managed.close()

    asyncio.run(scenario())


def test_stdout_eof_cannot_bypass_the_managed_timeout() -> None:
    async def scenario() -> None:
        managed = _process(
            _command("import os, sys, time; os.close(sys.stdout.fileno()); time.sleep(10)"),
            timeout_seconds=0.05,
        )
        process = await managed.start()
        try:
            with pytest.raises(ManagedProcessTimeout, match="closed stdout"):
                await managed.readline()
        finally:
            await managed.close()
        assert process.returncode is not None

    asyncio.run(scenario())


def test_default_working_directory_is_empty_owned_and_removed() -> None:
    async def scenario() -> None:
        managed = _process(
            _command(
                "import json, os; print(json.dumps({'cwd': os.getcwd(), 'entries': os.listdir()}), flush=True)"
            )
        )
        await managed.start()
        observed = json.loads((await managed.readline()).decode("utf-8"))
        cwd = Path(observed["cwd"])
        assert observed["entries"] == []
        assert cwd.is_dir()

        await managed.close()

        assert not cwd.exists()

    asyncio.run(scenario())


def test_close_escalates_and_is_idempotent() -> None:
    async def scenario() -> None:
        managed = _process(
            _command(
                "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(10)"
            ),
        )
        process = await managed.start()

        await managed.close()
        await managed.close()

        assert process.returncode is not None

    asyncio.run(scenario())


def test_close_removes_owned_working_directory(tmp_path: Path) -> None:
    async def scenario() -> None:
        cwd = tmp_path / "owned-cwd"
        cwd.mkdir()
        managed = _process(
            _command("import sys; sys.stdout.write('done\\n'); sys.stdout.flush()"),
            cwd=cwd,
            owns_cwd=True,
        )
        await managed.start()
        try:
            await managed.wait()
        finally:
            await managed.close()

        assert not cwd.exists()

    asyncio.run(scenario())
