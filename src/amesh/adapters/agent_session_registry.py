from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

from amesh.ports import AgentSessionHarness

from .agent_session_harness import PI_ADAPTER_VERSION, PI_WORKER_PROTOCOL, PiAgentSessionHarness

AgentSessionHarnessFactory = Callable[
    [tuple[str, ...], int, float, float, Mapping[str, str]],
    AgentSessionHarness,
]

AGENT_SESSION_HARNESS_REGISTRY = {
    "pi": {
        "adapter": "pi-agent-core",
        "adapterVersion": PI_ADAPTER_VERSION,
        "protocol": PI_WORKER_PROTOCOL,
    }
}


def _build_pi(
    worker_command: tuple[str, ...],
    max_frame_bytes: int,
    operation_timeout_seconds: float,
    cancel_grace_seconds: float,
    environment: Mapping[str, str],
) -> AgentSessionHarness:
    return PiAgentSessionHarness(
        worker_command,
        max_frame_bytes=max_frame_bytes,
        operation_timeout_seconds=operation_timeout_seconds,
        cancel_grace_seconds=cancel_grace_seconds,
        environment=environment,
    )


_HARNESS_FACTORIES: dict[str, AgentSessionHarnessFactory] = {"pi": _build_pi}
_DEFAULT_PI_WORKER_COMMAND = ("node", "harnesses/pi/src/worker.mjs")


def _resolve_worker_command(
    adapter: str,
    worker_command: tuple[str, ...],
) -> tuple[str, ...]:
    if adapter != "pi" or worker_command != _DEFAULT_PI_WORKER_COMMAND:
        return worker_command
    return (worker_command[0], str(Path(worker_command[1]).resolve()))


def create_agent_session_harness(
    adapter: str,
    worker_command: tuple[str, ...],
    *,
    max_frame_bytes: int = 1_048_576,
    operation_timeout_seconds: float = 120.0,
    cancel_grace_seconds: float = 2.0,
    environment: Mapping[str, str] | None = None,
) -> AgentSessionHarness:
    """Create an explicitly registered agent-session harness, failing closed."""

    factory = _HARNESS_FACTORIES.get(adapter)
    if factory is None:
        raise ValueError(f"agent-session harness adapter {adapter!r} is not registered")
    return factory(
        _resolve_worker_command(adapter, worker_command),
        max_frame_bytes,
        operation_timeout_seconds,
        cancel_grace_seconds,
        environment or {},
    )
