from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import amesh.harness_probe as harness_probe


@pytest.mark.parametrize(
    ("arguments", "expected_command"),
    (
        ((), ("configured-node", "configured/worker.mjs")),
        (("--worker", "override/worker.mjs"), ("node", str(Path("override/worker.mjs")))),
    ),
)
def test_probe_uses_settings_by_default_and_worker_argument_as_override(
    monkeypatch: pytest.MonkeyPatch,
    arguments: tuple[str, ...],
    expected_command: tuple[str, ...],
) -> None:
    observed: list[tuple[str, ...]] = []
    settings = SimpleNamespace(
        agent_session_pi_worker_command=("configured-node", "configured/worker.mjs")
    )

    async def probe(worker_command: tuple[str, ...]) -> dict[str, bool]:
        observed.append(worker_command)
        return {"passed": True}

    monkeypatch.setattr(harness_probe, "Settings", lambda: settings)
    monkeypatch.setattr(harness_probe, "_probe", probe)
    monkeypatch.setattr(sys, "argv", ["amesh-harness-probe", *arguments])

    assert harness_probe.main() == 0
    assert observed == [expected_command]
