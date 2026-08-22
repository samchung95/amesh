from __future__ import annotations

import asyncio
import importlib
import os
import signal
import subprocess
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass
from itertools import count
from time import perf_counter
from typing import Any, cast

import psutil
from pydantic import ValidationError

from amesh.ports import (
    LocalProcessResourceLimits,
    LocalProcessRunnerExtension,
    RunnerCapabilities,
    RunnerDiagnostics,
    RunnerId,
    RunnerLog,
    RunnerLogStream,
    RunnerMetrics,
    RunnerReconciliationResult,
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    StaleRunnerAttemptError,
    TaskRunner,
    UnsupportedRunnerRequest,
    validate_runner_request,
)

_SAFE_HOST_ENVIRONMENT = (
    "COMSPEC",
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
)

_CAPABILITIES = RunnerCapabilities(
    runner=RunnerId.LOCAL,
    acceptsCommand=True,
    requiresCommand=True,
    acceptsImage=False,
    supportsFiles=True,
    supportsWorkingDirectory=True,
    supportsStandardInput=True,
    supportsResources=True,
    supportsSecurityPolicy=True,
    supportsScopedCredentials=True,
    supportsReconciliation=True,
    extensionType=RunnerId.LOCAL,
    cancellationEscalation=("terminate", "wait-grace", "kill"),
    platforms=("linux", "macos", "windows-constrained"),
    features=(
        "argv",
        "explicit-shell",
        "ordered-stdout-stderr",
        "process-groups",
        "resource-usage",
        "posix-resource-limits",
        "posix-run-as-user",
    ),
)

RunnerLogSink = Callable[[RunnerLog], Awaitable[None]]


@dataclass
class _ActiveProcess:
    process: asyncio.subprocess.Process
    fencing_token: int
    cancel_grace_seconds: float
    is_cancel_requested: bool = False


@dataclass
class _ProcessUsage:
    cpu_seconds: float = 0
    peak_memory_bytes: int = 0


class LocalProcessRunner(TaskRunner):
    """Runs one task attempt as a fenced local process group."""

    CAPABILITIES = _CAPABILITIES

    def __init__(self, *, log_sink: RunnerLogSink | None = None) -> None:
        self._active: dict[str, _ActiveProcess] = {}
        self._lock = asyncio.Lock()
        self._log_sink = log_sink

    @property
    def capabilities(self) -> RunnerCapabilities:
        return self.CAPABILITIES

    async def run(self, request: RunnerRequest) -> RunnerResult:
        validate_runner_request(self.capabilities, request)
        extension, limits = _validate_local_request(request)

        started_at = perf_counter()
        environment = _process_environment(request, extension)
        process = await _create_process(request, extension, limits, environment)
        active = _ActiveProcess(
            process=process,
            fencing_token=request.fencing_token,
            cancel_grace_seconds=request.cancel_grace_seconds,
        )
        async with self._lock:
            if request.attempt_id in self._active:
                await _stop_process_group(process, request.cancel_grace_seconds)
                raise RuntimeError(f"attempt {request.attempt_id!r} is already running")
            self._active[request.attempt_id] = active

        capture = asyncio.create_task(_capture_output(process, self._log_sink))
        write_input = asyncio.create_task(_write_standard_input(process, request.standard_input))
        usage = asyncio.create_task(_monitor_usage(process))
        waiter = asyncio.create_task(process.wait())
        is_timed_out = False
        try:
            if request.timeout_seconds is None:
                await waiter
            else:
                done, _ = await asyncio.wait({waiter}, timeout=request.timeout_seconds)
                if waiter not in done:
                    is_timed_out = True
                    await _stop_process_group(process, request.cancel_grace_seconds)
                await waiter
            stdout, stderr, logs = await capture
            await write_input
            measured = await usage
        except asyncio.CancelledError:
            active.is_cancel_requested = True
            await _stop_process_group(process, request.cancel_grace_seconds)
            for pending in (capture, write_input, usage, waiter):
                pending.cancel()
            for pending in (capture, write_input, usage, waiter):
                with suppress(asyncio.CancelledError):
                    await pending
            raise
        finally:
            async with self._lock:
                current = self._active.get(request.attempt_id)
                if current is active:
                    del self._active[request.attempt_id]

        if active.is_cancel_requested:
            status = RunnerStatus.CANCELLED
        elif is_timed_out:
            status = RunnerStatus.TIMED_OUT
        elif process.returncode == 0:
            status = RunnerStatus.SUCCESS
        else:
            status = RunnerStatus.FAILED
        termination_signal = (
            -process.returncode
            if os.name == "posix" and process.returncode is not None and process.returncode < 0
            else None
        )
        return RunnerResult(
            runner=RunnerId.LOCAL,
            exit_code=process.returncode,
            signal=termination_signal,
            status=status,
            logs=logs,
            metrics=RunnerMetrics(
                duration_seconds=perf_counter() - started_at,
                cpu_seconds=measured.cpu_seconds,
                peak_memory_bytes=measured.peak_memory_bytes,
            ),
            outputs={
                "stdout": stdout,
                "stderr": stderr,
            },
            diagnostics=RunnerDiagnostics(
                runner=RunnerId.LOCAL,
                details={
                    "pid": process.pid,
                    "shell": extension.shell,
                    "resourceLimits": limits.model_dump(
                        mode="json", by_alias=True, exclude_none=True
                    ),
                },
            ),
        )

    async def cancel(self, attempt_id: str, fencing_token: int) -> None:
        async with self._lock:
            active = self._active.get(attempt_id)
            if active is None or active.fencing_token != fencing_token:
                raise StaleRunnerAttemptError(
                    f"attempt {attempt_id!r} is inactive or fenced by a newer token"
                )
            active.is_cancel_requested = True
        await _stop_process_group(active.process, active.cancel_grace_seconds)

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult:
        async with self._lock:
            orphans = [
                (attempt_id, active)
                for attempt_id, active in self._active.items()
                if active_attempts.get(attempt_id) != active.fencing_token
            ]
            retained = tuple(
                sorted(
                    attempt_id
                    for attempt_id, active in self._active.items()
                    if active_attempts.get(attempt_id) == active.fencing_token
                )
            )
            for _, active in orphans:
                active.is_cancel_requested = True
        for _, active in orphans:
            await _stop_process_group(active.process, active.cancel_grace_seconds)
        return RunnerReconciliationResult(
            runner=RunnerId.LOCAL,
            cleanedAttempts=tuple(sorted(attempt_id for attempt_id, _ in orphans)),
            retainedAttempts=retained,
        )


def _validate_local_request(
    request: RunnerRequest,
) -> tuple[LocalProcessRunnerExtension, LocalProcessResourceLimits]:
    extension = (
        request.extension
        if isinstance(request.extension, LocalProcessRunnerExtension)
        else LocalProcessRunnerExtension(type=RunnerId.LOCAL)
    )
    reasons: list[str] = []
    if extension.shell and len(request.command) != 1:
        reasons.append("explicit shell mode requires one command string")
    if request.security_policy.privileged:
        reasons.append("privileged security policy")
    if request.security_policy.read_only_root_filesystem:
        reasons.append("read-only root filesystem security policy")
    if request.security_policy.capability_add:
        reasons.append("capability-add security policy")
    if request.security_policy.capability_drop != ("ALL",):
        reasons.append("capability-drop security policy")
    if not request.security_policy.no_new_privileges:
        reasons.append("no-new-privileges security policy")
    try:
        limits = LocalProcessResourceLimits.model_validate(request.resource_limits)
    except ValidationError as exc:
        fields = sorted({".".join(str(item) for item in error["loc"]) for error in exc.errors()})
        reasons.append("resource limits " + ", ".join(fields))
        limits = LocalProcessResourceLimits()
    if os.name != "posix":
        if request.security_policy.run_as_user is not None:
            reasons.append("runAsUser is available only on Linux and macOS")
        if request.resource_limits:
            reasons.append("resource limits are available only on Linux and macOS")
    elif request.security_policy.run_as_user is not None:
        getuid = cast(Callable[[], int], os.__dict__["getuid"])
        current_user = getuid()
        if current_user != 0 and request.security_policy.run_as_user != current_user:
            reasons.append("runAsUser requires root or the worker's current uid")
    if reasons:
        raise UnsupportedRunnerRequest(RunnerId.LOCAL, tuple(reasons))
    return extension, limits


def _process_environment(
    request: RunnerRequest,
    extension: LocalProcessRunnerExtension,
) -> dict[str, str]:
    allowed_environment = set(_SAFE_HOST_ENVIRONMENT).union(extension.allowed_host_environment)
    environment = (
        os.environ.copy()
        if extension.inherit_host_environment
        else {name: os.environ[name] for name in allowed_environment if name in os.environ}
    )
    environment.update(request.environment)
    environment.update(
        {
            credential.environment_variable: credential.value.get_secret_value()
            for credential in request.credentials
        }
    )
    if request.working_directory is not None:
        environment.setdefault("WORKING_DIR", request.working_directory)
        environment.setdefault("OUTPUT_DIR", request.working_directory)
    return environment


async def _create_process(
    request: RunnerRequest,
    extension: LocalProcessRunnerExtension,
    limits: LocalProcessResourceLimits,
    environment: dict[str, str],
) -> asyncio.subprocess.Process:
    options: dict[str, Any] = {
        "stdin": asyncio.subprocess.PIPE if request.standard_input is not None else None,
        "stdout": asyncio.subprocess.PIPE,
        "stderr": asyncio.subprocess.PIPE,
        "env": environment,
        "cwd": request.working_directory,
    }
    if os.name == "posix":
        options["start_new_session"] = True
        preexec_fn = _posix_preexec_fn(limits, request.security_policy.run_as_user)
        if preexec_fn is not None:
            options["preexec_fn"] = preexec_fn
    elif os.name == "nt":
        options["creationflags"] = cast(
            int,
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200),
        )
    if extension.shell:
        return await asyncio.create_subprocess_shell(request.command[0], **options)
    return await asyncio.create_subprocess_exec(*request.command, **options)


def _posix_preexec_fn(
    limits: LocalProcessResourceLimits,
    run_as_user: int | None,
) -> Callable[[], None] | None:
    values = limits.model_dump(exclude_none=True)
    if not values and run_as_user is None:
        return None
    resource_module = importlib.import_module("resource")
    setrlimit = cast(
        Callable[[int, tuple[int, int]], None],
        resource_module.__dict__["setrlimit"],
    )
    limit_pairs = tuple(
        (cast(int, resource_module.__dict__[constant]), int(value))
        for field, constant in (
            ("cpu_seconds", "RLIMIT_CPU"),
            ("memory_bytes", "RLIMIT_AS"),
            ("file_size_bytes", "RLIMIT_FSIZE"),
            ("open_files", "RLIMIT_NOFILE"),
            ("processes", "RLIMIT_NPROC"),
        )
        if (value := getattr(limits, field)) is not None
    )
    setuid = cast(Callable[[int], None], os.__dict__["setuid"])

    def configure_child() -> None:
        for resource_id, value in limit_pairs:
            setrlimit(resource_id, (value, value))
        if run_as_user is not None:
            setuid(run_as_user)

    return configure_child


async def _write_standard_input(
    process: asyncio.subprocess.Process,
    standard_input: str | None,
) -> None:
    if standard_input is None or process.stdin is None:
        return
    with suppress(BrokenPipeError, ConnectionResetError):
        process.stdin.write(standard_input.encode())
        await process.stdin.drain()
    process.stdin.close()
    with suppress(BrokenPipeError, ConnectionResetError):
        await process.stdin.wait_closed()


async def _capture_output(
    process: asyncio.subprocess.Process,
    sink: RunnerLogSink | None,
) -> tuple[str, str, tuple[RunnerLog, ...]]:
    if process.stdout is None or process.stderr is None:
        raise RuntimeError("local process output pipes are unavailable")
    sequence = count()
    logs: list[RunnerLog] = []
    buffers = {
        RunnerLogStream.STDOUT: bytearray(),
        RunnerLogStream.STDERR: bytearray(),
    }

    async def pump(reader: asyncio.StreamReader, stream: RunnerLogStream) -> None:
        while chunk := await reader.read(8192):
            buffers[stream].extend(chunk)
            entry = RunnerLog(
                sequence=next(sequence),
                stream=stream,
                level="INFO" if stream is RunnerLogStream.STDOUT else "ERROR",
                message=chunk.decode(errors="replace"),
            )
            logs.append(entry)
            if sink is not None:
                await sink(entry)

    await asyncio.gather(
        pump(process.stdout, RunnerLogStream.STDOUT),
        pump(process.stderr, RunnerLogStream.STDERR),
    )
    return (
        buffers[RunnerLogStream.STDOUT].decode(errors="replace"),
        buffers[RunnerLogStream.STDERR].decode(errors="replace"),
        tuple(sorted(logs, key=lambda item: item.sequence)),
    )


async def _monitor_usage(process: asyncio.subprocess.Process) -> _ProcessUsage:
    usage = _ProcessUsage()
    try:
        root = psutil.Process(process.pid)
    except psutil.Error:
        return usage
    known: dict[int, psutil.Process] = {root.pid: root}
    while process.returncode is None:
        with suppress(psutil.Error):
            known.update({child.pid: child for child in root.children(recursive=True)})
        current_memory = 0
        current_cpu = 0.0
        for monitored in tuple(known.values()):
            try:
                memory = monitored.memory_info()
                current_memory += int(getattr(memory, "peak_wset", memory.rss))
                cpu = monitored.cpu_times()
                current_cpu += float(cpu.user + cpu.system)
            except psutil.Error:
                continue
        usage.peak_memory_bytes = max(usage.peak_memory_bytes, current_memory)
        usage.cpu_seconds = max(usage.cpu_seconds, current_cpu)
        await asyncio.sleep(0.02)
    return usage


async def _stop_process_group(
    process: asyncio.subprocess.Process,
    grace_seconds: float,
) -> None:
    if os.name == "posix":
        await _stop_posix_process_group(process, grace_seconds)
    else:
        await _stop_process_tree(process, grace_seconds)


async def _stop_posix_process_group(
    process: asyncio.subprocess.Process,
    grace_seconds: float,
) -> None:
    kill_group = cast(Callable[[int, int], None], os.__dict__["killpg"])
    with suppress(ProcessLookupError):
        kill_group(process.pid, signal.SIGTERM)
    try:
        await asyncio.wait_for(process.wait(), timeout=grace_seconds)
        return
    except TimeoutError:
        pass
    with suppress(ProcessLookupError):
        kill_group(process.pid, cast(int, signal.__dict__["SIGKILL"]))
    await process.wait()


async def _stop_process_tree(
    process: asyncio.subprocess.Process,
    grace_seconds: float,
) -> None:
    try:
        root = psutil.Process(process.pid)
        processes = [*root.children(recursive=True), root]
    except psutil.Error:
        processes = []
    for item in reversed(processes):
        with suppress(psutil.Error):
            item.terminate()
    if processes:
        _, alive = await asyncio.to_thread(psutil.wait_procs, processes, timeout=grace_seconds)
        for item in alive:
            with suppress(psutil.Error):
                item.kill()
        if alive:
            await asyncio.to_thread(psutil.wait_procs, alive, timeout=grace_seconds)
    if process.returncode is None:
        with suppress(ProcessLookupError):
            process.kill()
    await process.wait()
