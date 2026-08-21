from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

from amesh.ports import (
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    StaleRunnerAttemptError,
    TaskRunner,
)


@dataclass
class _ActiveProcess:
    process: asyncio.subprocess.Process
    fencing_token: int
    cancel_grace_seconds: float
    is_cancel_requested: bool = False


class LocalProcessRunner(TaskRunner):
    """Runs one task attempt as a fenced local subprocess."""

    def __init__(self) -> None:
        self._active: dict[str, _ActiveProcess] = {}
        self._lock = asyncio.Lock()

    async def run(self, request: RunnerRequest) -> RunnerResult:
        if request.image is not None:
            raise ValueError("local process runner does not accept a container image")
        if not request.command:
            raise ValueError("local process command must not be empty")

        environment = os.environ.copy()
        environment.update(request.environment)
        process = await asyncio.create_subprocess_exec(
            *request.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
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
        return RunnerResult(
            exit_code=process.returncode,
            status=status,
            outputs={
                "stdout": stdout.decode(errors="replace"),
                "stderr": stderr.decode(errors="replace"),
            },
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
