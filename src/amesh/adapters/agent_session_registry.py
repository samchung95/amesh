from __future__ import annotations

from collections.abc import Callable

from amesh.ports import AgentSessionHarness

from .agent_session_harness import PI_ADAPTER_VERSION, PI_WORKER_PROTOCOL, PiAgentSessionHarness

AgentSessionHarnessFactory = Callable[[tuple[str, ...], int], AgentSessionHarness]

AGENT_SESSION_HARNESS_REGISTRY = {
    "pi": {
        "adapter": "pi-agent-core",
        "adapterVersion": PI_ADAPTER_VERSION,
        "protocol": PI_WORKER_PROTOCOL,
    }
}


def _build_pi(worker_command: tuple[str, ...], max_frame_bytes: int) -> AgentSessionHarness:
    return PiAgentSessionHarness(worker_command, max_frame_bytes=max_frame_bytes)


_HARNESS_FACTORIES: dict[str, AgentSessionHarnessFactory] = {"pi": _build_pi}


def create_agent_session_harness(
    adapter: str,
    worker_command: tuple[str, ...],
    *,
    max_frame_bytes: int = 1_048_576,
) -> AgentSessionHarness:
    """Create an explicitly registered agent-session harness, failing closed."""

    factory = _HARNESS_FACTORIES.get(adapter)
    if factory is None:
        raise ValueError(f"agent-session harness adapter {adapter!r} is not registered")
    return factory(worker_command, max_frame_bytes)
