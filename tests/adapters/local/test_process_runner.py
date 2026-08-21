from __future__ import annotations

import asyncio
import sys

import pytest

from amesh.adapters.local import LocalProcessRunner
from amesh.ports import RunnerRequest, RunnerStatus, StaleRunnerAttemptError


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
