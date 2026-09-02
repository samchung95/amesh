from __future__ import annotations

import pytest

from amesh.adapters.agent_session_harness import PiAgentSessionHarness
from amesh.adapters.agent_session_registry import create_agent_session_harness


def test_pi_is_the_explicit_default_registered_harness() -> None:
    harness = create_agent_session_harness(
        "pi",
        ("node", "worker.mjs"),
        max_frame_bytes=2_097_152,
        operation_timeout_seconds=30,
        cancel_grace_seconds=0.5,
        environment={"LANG": "C.UTF-8"},
    )

    assert isinstance(harness, PiAgentSessionHarness)
    assert harness._max_frame_bytes == 2_097_152
    assert harness._operation_timeout_seconds == 30
    assert harness._cancel_grace_seconds == 0.5
    assert harness._environment == {"LANG": "C.UTF-8"}


def test_unknown_harness_adapter_fails_closed_without_fallback() -> None:
    with pytest.raises(ValueError, match="is not registered"):
        create_agent_session_harness("unknown", ("node", "worker.mjs"))
