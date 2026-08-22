from __future__ import annotations

import asyncio
import os
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from time import perf_counter

from amesh.ports import (
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
    supportsResources=False,
    supportsSecurityPolicy=False,
    supportsScopedCredentials=True,
    supportsReconciliation=True,
    extensionType=RunnerId.LOCAL,
    cancellationEscalation=("terminate", "wait-grace", "kill"),
)


@dataclass
class _ActiveProcess:
    process: asyncio.subprocess.Process
    fencing_token: int
    cancel_grace_seconds: float
    is_cancel_requested: bool = False


class LocalProcessRunner(TaskRunner):
    """Runs one task attempt as a fenced local subprocess."""

    CAPABILITIES = _CAPABILITIES

    def __init__(self) -> None:
        self._active: dict[str, _ActiveProcess] = {}
        self._lock = asyncio.Lock()

    @property
    def capabilities(self) -> RunnerCapabilities:
        return self.CAPABILITIES

    async def run(self, request: RunnerRequest) -> RunnerResult:
        validate_runner_request(self.capabilities, request)

        started_at = perf_counter()
        extension = (
            request.extension
            if isinstance(request.extension, LocalProcessRunnerExtension)
            else LocalProcessRunnerExtension(type=RunnerId.LOCAL)
        )
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
        process = await asyncio.create_subprocess_exec(
            *request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
            cwd=request.working_directory,
        )
        active = _ActiveProcess(
            process=process,
            fencing_token=request.fencing_token,
            cancel_grace_seconds=request.cancel_grace_seconds,
        )
        async with self._lock:
            if request.attempt_id in self._active:
                await _stop_process(process, request.cancel_grace_seconds)
                raise RuntimeError(f"attempt {request.attempt_id!r} is already running")
            self._active[request.attempt_id] = active

        communicate = asyncio.create_task(process.communicate())
        is_timed_out = False
        try:
            if request.timeout_seconds is None:
                stdout, stderr = await communicate
            else:
                done, _ = await asyncio.wait({communicate}, timeout=request.timeout_seconds)
                if communicate not in done:
                    is_timed_out = True
                    await _stop_process(process, request.cancel_grace_seconds)
                stdout, stderr = await communicate
        except asyncio.CancelledError:
            active.is_cancel_requested = True
            await _stop_process(process, request.cancel_grace_seconds)
            communicate.cancel()
            with suppress(asyncio.CancelledError):
                await communicate
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
        stdout_text = stdout.decode(errors="replace")
        stderr_text = stderr.decode(errors="replace")
        logs = tuple(
            RunnerLog(sequence=sequence, stream=stream, message=message)
            for sequence, (stream, message) in enumerate(
                (
                    (RunnerLogStream.STDOUT, stdout_text),
                    (RunnerLogStream.STDERR, stderr_text),
                )
            )
            if message
        )
        return RunnerResult(
            runner=RunnerId.LOCAL,
            exit_code=process.returncode,
            status=status,
            logs=logs,
            metrics=RunnerMetrics(duration_seconds=perf_counter() - started_at),
            outputs={
                "stdout": stdout_text,
                "stderr": stderr_text,
            },
            diagnostics=RunnerDiagnostics(runner=RunnerId.LOCAL),
        )

    async def cancel(self, attempt_id: str, fencing_token: int) -> None:
        async with self._lock:
            active = self._active.get(attempt_id)
            if active is None or active.fencing_token != fencing_token:
                raise StaleRunnerAttemptError(
                    f"attempt {attempt_id!r} is inactive or fenced by a newer token"
                )
            active.is_cancel_requested = True
        await _stop_process(active.process, active.cancel_grace_seconds)

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
            await _stop_process(active.process, active.cancel_grace_seconds)
        return RunnerReconciliationResult(
            runner=RunnerId.LOCAL,
            cleanedAttempts=tuple(sorted(attempt_id for attempt_id, _ in orphans)),
            retainedAttempts=retained,
        )


async def _stop_process(process: asyncio.subprocess.Process, grace_seconds: float) -> None:
    if process.returncode is not None:
        return
    try:
        process.terminate()
    except ProcessLookupError:
        return
    try:
        await asyncio.wait_for(process.wait(), timeout=grace_seconds)
    except TimeoutError:
        try:
            process.kill()
        except ProcessLookupError:
            return
        await process.wait()
