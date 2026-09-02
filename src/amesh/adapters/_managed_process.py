"""Shared bounded lifecycle for model-engine and harness child processes."""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path

from amesh.ports.model_engines import (
    ProviderProcessError,
    ProviderProtocolError,
    ProviderTimeoutError,
)

SAFE_HOST_ENVIRONMENT_KEYS = (
    "COMSPEC",
    "LANG",
    "LC_ALL",
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
    "TZ",
    "WINDIR",
)


class ManagedProcessError(ProviderProcessError):
    """A managed child process could not be started or completed."""


class ManagedProcessProtocolError(ManagedProcessError, ProviderProtocolError):
    """A managed child exceeded a frame bound or violated its transport."""


class ManagedProcessTimeout(ManagedProcessError, ProviderTimeoutError):
    """A managed child operation exceeded its configured timeout."""


def managed_process_environment(
    configured: Mapping[str, str] | None = None,
    *,
    overrides: Mapping[str, str] | None = None,
    host_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Build one allowlisted child environment without copying host credentials."""

    source = os.environ if host_environment is None else host_environment
    source_by_name = {name.upper(): value for name, value in source.items()}
    environment = {
        name: source_by_name[name] for name in SAFE_HOST_ENVIRONMENT_KEYS if name in source_by_name
    }
    if configured:
        unknown = set(configured) - set(SAFE_HOST_ENVIRONMENT_KEYS)
        if unknown:
            raise ValueError(
                "managed process environment contains unsupported keys: "
                + ", ".join(sorted(unknown))
            )
        environment.update(configured)
    if overrides:
        environment.update(overrides)
    return environment


class ManagedProcess:
    """One subprocess with bounded streams, deadlines, and deterministic teardown."""

    def __init__(
        self,
        command: tuple[str, ...],
        *,
        environment: Mapping[str, str],
        frame_limit_bytes: int,
        timeout_seconds: float,
        cancel_grace_seconds: float,
        cwd: Path | None = None,
        stderr: int | None = asyncio.subprocess.DEVNULL,
        owns_cwd: bool = False,
    ) -> None:
        if not command:
            raise ValueError("managed process command cannot be empty")
        if frame_limit_bytes < 1:
            raise ValueError("managed process frame limit must be positive")
        if timeout_seconds <= 0 or cancel_grace_seconds <= 0:
            raise ValueError("managed process timeouts must be positive")
        self._command = command
        self._environment = dict(environment)
        self._frame_limit_bytes = frame_limit_bytes
        self._timeout_seconds = timeout_seconds
        self._cancel_grace_seconds = cancel_grace_seconds
        self._cwd = cwd
        self._stderr = stderr
        self._owns_cwd = owns_cwd
        self._process: asyncio.subprocess.Process | None = None

    @property
    def process(self) -> asyncio.subprocess.Process | None:
        return self._process

    async def start(self) -> asyncio.subprocess.Process:
        if self._process is not None:
            return self._process
        if self._cwd is None:
            self._cwd = Path(tempfile.mkdtemp(prefix="amesh-model-engine-cwd-"))
            self._owns_cwd = True
        try:
            self._process = await asyncio.create_subprocess_exec(
                *self._command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=self._stderr,
                limit=self._frame_limit_bytes,
                env=self._environment,
                cwd=str(self._cwd) if self._cwd is not None else None,
                close_fds=os.name != "nt",
            )
        except OSError as exc:
            if self._owns_cwd and self._cwd is not None:
                await _remove_owned_directory(self._cwd)
            raise ManagedProcessError("managed process could not be started") from exc
        return self._process

    async def readline(self, timeout_seconds: float | None = None) -> bytes:
        process = self._require_process()
        if process.stdout is None:
            raise ManagedProcessError("managed process stdout is unavailable")
        try:
            raw = await asyncio.wait_for(
                process.stdout.readline(),
                self._timeout_seconds if timeout_seconds is None else timeout_seconds,
            )
        except TimeoutError as exc:
            raise ManagedProcessTimeout("timed out waiting for managed process output") from exc
        except (ValueError, asyncio.LimitOverrunError) as exc:
            raise ManagedProcessProtocolError(
                "managed process frame exceeds configured limit"
            ) from exc
        if not raw:
            try:
                code = await asyncio.wait_for(
                    process.wait(),
                    self._timeout_seconds if timeout_seconds is None else timeout_seconds,
                )
            except TimeoutError as exc:
                raise ManagedProcessTimeout(
                    "managed process closed stdout but did not exit before timeout"
                ) from exc
            raise ManagedProcessError(f"managed process exited before a response (code {code})")
        if len(raw) > self._frame_limit_bytes:
            raise ManagedProcessProtocolError("managed process frame exceeds configured limit")
        return raw

    async def write(self, value: bytes, timeout_seconds: float | None = None) -> None:
        if len(value) > self._frame_limit_bytes:
            raise ManagedProcessProtocolError("managed process frame exceeds configured limit")
        process = self._require_process()
        if process.stdin is None:
            raise ManagedProcessError("managed process stdin is unavailable")
        try:
            process.stdin.write(value)
            await asyncio.wait_for(
                process.stdin.drain(),
                self._timeout_seconds if timeout_seconds is None else timeout_seconds,
            )
        except TimeoutError as exc:
            raise ManagedProcessTimeout("timed out writing to managed process") from exc
        except (BrokenPipeError, ConnectionResetError) as exc:
            raise ManagedProcessError("managed process exited while receiving input") from exc

    async def wait(self, timeout_seconds: float | None = None) -> int:
        process = self._require_process()
        try:
            return await asyncio.wait_for(
                process.wait(),
                self._timeout_seconds if timeout_seconds is None else timeout_seconds,
            )
        except TimeoutError as exc:
            raise ManagedProcessTimeout("timed out waiting for managed process") from exc

    async def drain_stderr(self, maximum_bytes: int | None = None) -> None:
        process = self._require_process()
        stream = process.stderr
        if stream is None:
            return
        maximum = self._frame_limit_bytes if maximum_bytes is None else maximum_bytes
        consumed = 0
        while chunk := await stream.read(min(4096, maximum + 1)):
            consumed += len(chunk)
            if consumed > maximum:
                raise ManagedProcessProtocolError("managed process stderr exceeds configured limit")

    async def close(self) -> None:
        process = self._process
        self._process = None
        try:
            if process is None:
                return
            if process.stdin is not None:
                process.stdin.close()
                with suppress(BrokenPipeError, ConnectionResetError, TimeoutError):
                    await asyncio.wait_for(
                        process.stdin.wait_closed(),
                        self._cancel_grace_seconds,
                    )
            if process.returncode is None:
                with suppress(ProcessLookupError):
                    process.terminate()
                await _bounded_wait(process, self._cancel_grace_seconds)
            if process.returncode is None:
                with suppress(ProcessLookupError):
                    process.kill()
                await _bounded_wait(process, self._cancel_grace_seconds)
            _close_process_transports(process)
        finally:
            if self._owns_cwd and self._cwd is not None:
                await _remove_owned_directory(self._cwd)

    def _require_process(self) -> asyncio.subprocess.Process:
        if self._process is None:
            raise ManagedProcessError("managed process is not running")
        return self._process


async def _bounded_wait(process: asyncio.subprocess.Process, timeout_seconds: float) -> None:
    with suppress(TimeoutError):
        await asyncio.wait_for(process.wait(), timeout_seconds)


def _close_process_transports(process: asyncio.subprocess.Process) -> None:
    transport = getattr(process, "_transport", None)
    if transport is not None:
        transport.close()
    for stream in (process.stdout, process.stderr):
        stream_transport = getattr(stream, "_transport", None)
        if stream_transport is not None:
            stream_transport.close()


async def _remove_owned_directory(path: Path) -> None:
    """Remove a process cwd after Windows releases its directory handle."""

    for attempt in range(5):
        try:
            await asyncio.to_thread(shutil.rmtree, path)
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 4:
                return
            await asyncio.sleep(0.05 * (attempt + 1))


__all__ = [
    "SAFE_HOST_ENVIRONMENT_KEYS",
    "ManagedProcess",
    "ManagedProcessError",
    "ManagedProcessProtocolError",
    "ManagedProcessTimeout",
    "managed_process_environment",
]
