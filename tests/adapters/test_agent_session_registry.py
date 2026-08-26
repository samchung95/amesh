from __future__ import annotations

import pytest

from amesh.adapters.agent_session_harness import PiAgentSessionHarness
from amesh.adapters.agent_session_registry import create_agent_session_harness


def test_pi_is_the_explicit_default_registered_harness() -> None:
    harness = create_agent_session_harness("pi", ("node", "worker.mjs"))

    assert isinstance(harness, PiAgentSessionHarness)


def test_unknown_harness_adapter_fails_closed_without_fallback() -> None:
    with pytest.raises(ValueError, match="is not registered"):
        create_agent_session_harness("unknown", ("node", "worker.mjs"))
