from __future__ import annotations

import asyncio
import os
import signal
import sys
from pathlib import Path

import pytest

from amesh.adapters.local import LocalProcessRunner
from amesh.config import Settings
from amesh.domain.runner import (
    LocalProcessRunnerExtension,
    RunnerId,
    RunnerPolicySet,
    RunnerPolicyViolation,
    RunnerSecurityPolicy,
)
from amesh.dsl import validate_flow_document
from amesh.dsl.models import TaskDefinition
from amesh.executor import required_runner_ids
from amesh.ports import (
    RunnerLog,
    RunnerLogStream,
    RunnerRequest,
    RunnerStatus,
    UnsupportedRunnerRequest,
)


def request(*command: str, **updates: object) -> RunnerRequest:
    values: dict[str, object] = {
        "tenant_id": "default",
        "execution_id": "execution-220",
        "task_run_id": "task-220",
        "attempt_id": "attempt-220",
        "fencing_token": 1,
        "command": list(command),
        "cancel_grace_seconds": 0.2,
    }
    values.update(updates)
    return RunnerRequest.model_validate(values)


def test_urs_f_0258_argv_is_literal_and_shell_requires_explicit_single_string(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "shell-must-not-run"
    literal = f"value; echo injected > {marker}"
    result = asyncio.run(
        LocalProcessRunner().run(
            request(sys.executable, "-c", "import sys; print(sys.argv[1])", literal)
        )
    )

    assert result.outputs["stdout"].strip() == literal
    assert not marker.exists()

    shell_result = asyncio.run(
        LocalProcessRunner().run(
            request(
                "echo EPIC220_SHELL",
                extension=LocalProcessRunnerExtension(type=RunnerId.LOCAL, shell=True),
            )
        )
    )
    assert shell_result.outputs["stdout"].strip() == "EPIC220_SHELL"

    with pytest.raises(UnsupportedRunnerRequest, match="one command string"):
        asyncio.run(
            LocalProcessRunner().run(
                request(
                    "echo",
                    "invalid",
                    extension=LocalProcessRunnerExtension(type=RunnerId.LOCAL, shell=True),
                )
            )
        )

    validation = validate_flow_document(
        """
id: explicit_shell
namespace: tests.local
tasks:
  - id: shell
    type: core.shell
    command: ["printf hello | grep hello"]
    stdin: ignored
    taskRunner: {type: local, shell: true}
"""
    )
    assert validation.valid, validation.issues


def test_urs_f_0259_working_directory_environment_and_standard_input(tmp_path: Path) -> None:
    result = asyncio.run(
        LocalProcessRunner().run(
            request(
                sys.executable,
                "-c",
                (
                    "import os, pathlib, sys; "
                    "print(pathlib.Path.cwd().name); "
                    "print(os.environ['EPIC220_ENV']); "
                    "print(sys.stdin.read())"
                ),
                working_directory=str(tmp_path),
                environment={"EPIC220_ENV": "scoped"},
                standard_input="from-stdin",
            )
        )
    )

    assert result.outputs["stdout"].splitlines() == [tmp_path.name, "scoped", "from-stdin"]


@pytest.mark.skipif(os.name != "posix", reason="POSIX UID and rlimit qualification")
def test_urs_f_0259_posix_user_and_resource_limit() -> None:
    result = asyncio.run(
        LocalProcessRunner().run(
            request(
                sys.executable,
                "-c",
                "import os, resource; print(os.getuid(), resource.getrlimit(resource.RLIMIT_NOFILE)[0])",
                security_policy=RunnerSecurityPolicy(runAsUser=os.getuid()),
                resource_limits={"openFiles": 32},
            )
        )
    )

    assert result.outputs["stdout"].strip() == f"{os.getuid()} 32"


@pytest.mark.skipif(os.name == "posix", reason="Windows constraint qualification")
def test_urs_f_0259_0262_windows_rejects_posix_only_controls() -> None:
    with pytest.raises(UnsupportedRunnerRequest, match="resource limits are available only"):
        asyncio.run(
            LocalProcessRunner().run(
                request(
                    sys.executable, "-c", "print('no dispatch')", resource_limits={"openFiles": 8}
                )
            )
        )
    with pytest.raises(UnsupportedRunnerRequest, match="runAsUser is available only"):
        asyncio.run(
            LocalProcessRunner().run(
                request(
                    sys.executable,
                    "-c",
                    "print('no dispatch')",
                    security_policy=RunnerSecurityPolicy(runAsUser=1000),
                )
            )
        )


def test_urs_f_0260_streams_ordered_stdout_stderr_before_process_exit() -> None:
    async def scenario() -> None:
        streamed: list[RunnerLog] = []
        first = asyncio.Event()

        async def receive(entry: RunnerLog) -> None:
            streamed.append(entry)
            first.set()

        runner = LocalProcessRunner(log_sink=receive)
        running = asyncio.create_task(
            runner.run(
                request(
                    sys.executable,
                    "-c",
                    (
                        "import sys, time; "
                        "print('first', flush=True); "
                        "time.sleep(0.2); "
                        "print('second', file=sys.stderr, flush=True)"
                    ),
                )
            )
        )
        await asyncio.wait_for(first.wait(), timeout=1)
        assert not running.done()
        result = await running

        assert [entry.sequence for entry in streamed] == [0, 1]
        assert [entry.stream for entry in streamed] == [
            RunnerLogStream.STDOUT,
            RunnerLogStream.STDERR,
        ]
        assert [entry.level for entry in streamed] == ["INFO", "ERROR"]
        assert result.logs == tuple(streamed)

    asyncio.run(scenario())


@pytest.mark.parametrize("mode", ["cancel", "timeout"])
def test_urs_f_0261_cancellation_and_timeout_terminate_descendant_processes(
    tmp_path: Path,
    mode: str,
) -> None:
    async def scenario() -> None:
        marker = tmp_path / f"descendant-{mode}"
        child = (
            "import pathlib,time; time.sleep(0.5); "
            f"pathlib.Path({str(marker)!r}).write_text('orphan')"
        )
        parent = (
            "import subprocess,sys,time; "
            f"subprocess.Popen([sys.executable, '-c', {child!r}]); "
            "time.sleep(30)"
        )
        runner = LocalProcessRunner()
        running = asyncio.create_task(
            runner.run(
                request(
                    sys.executable,
                    "-c",
                    parent,
                    timeout_seconds=0.1 if mode == "timeout" else None,
                )
            )
        )
        if mode == "cancel":
            for _ in range(100):
                if runner._active:
                    break
                await asyncio.sleep(0.01)
            await runner.cancel("attempt-220", 1)
        result = await running
        await asyncio.sleep(0.6)

        expected = RunnerStatus.CANCELLED if mode == "cancel" else RunnerStatus.TIMED_OUT
        assert result.status is expected
        assert not marker.exists()

    asyncio.run(scenario())


def test_urs_f_0262_0263_platform_contract_and_multitenant_fail_closed() -> None:
    capabilities = LocalProcessRunner.CAPABILITIES
    assert capabilities.platforms == ("linux", "macos", "windows-constrained")
    assert "posix-resource-limits" in capabilities.features

    single = Settings(_env_file=None, tenancy_mode="single")
    untrusted_multi = Settings(_env_file=None, tenancy_mode="multi")
    trusted_multi = Settings(
        _env_file=None,
        tenancy_mode="multi",
        local_process_runner_enabled=True,
    )
    assert single.is_local_process_runner_enabled
    assert not untrusted_multi.is_local_process_runner_enabled
    assert trusted_multi.is_local_process_runner_enabled

    task = TaskDefinition(id="local", type="core.shell", command=["true"])
    with pytest.raises(RunnerPolicyViolation, match="not available"):
        required_runner_ids(
            (task,),
            RunnerPolicySet(),
            namespace="tenant.flow",
            fallback=RunnerId.LOCAL,
            available=frozenset({RunnerId.KUBERNETES}),
        )


def test_urs_f_0264_captures_exit_duration_cpu_and_peak_memory() -> None:
    result = asyncio.run(
        LocalProcessRunner().run(
            request(
                sys.executable,
                "-c",
                "data = bytearray(4 * 1024 * 1024); print(len(data))",
            )
        )
    )

    assert result.status is RunnerStatus.SUCCESS
    assert result.exit_code == 0
    assert result.signal is None
    assert result.metrics.duration_seconds > 0
    assert result.metrics.cpu_seconds is not None
    assert result.metrics.peak_memory_bytes is not None
    assert result.metrics.peak_memory_bytes > 0


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal qualification")
def test_urs_f_0264_captures_posix_termination_signal() -> None:
    result = asyncio.run(
        LocalProcessRunner().run(
            request(
                sys.executable,
                "-c",
                f"import os; os.kill(os.getpid(), {signal.SIGTERM})",
            )
        )
    )

    assert result.status is RunnerStatus.FAILED
    assert result.exit_code == -signal.SIGTERM
    assert result.signal == signal.SIGTERM
