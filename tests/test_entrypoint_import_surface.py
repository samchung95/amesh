from __future__ import annotations

import importlib
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

ENTRYPOINT_MODULES = (
    "cli",
    "compact",
    "deployment_profile",
    "migrations",
    "preflight",
    "role",
    "server",
    "worker",
)


@pytest.mark.parametrize("module_name", ENTRYPOINT_MODULES)
def test_legacy_entrypoint_import_is_canonical_module(module_name: str) -> None:
    canonical = importlib.import_module(f"amesh.entrypoints.{module_name}")
    legacy = importlib.import_module(f"amesh.{module_name}")

    assert legacy is canonical


def test_entrypoint_identity_is_stable_when_canonical_modules_load_first() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src"
    script = "\n".join(
        (
            "import importlib",
            f"modules = {ENTRYPOINT_MODULES!r}",
            "for name in modules:",
            "    canonical = importlib.import_module(f'amesh.entrypoints.{name}')",
            "    legacy = importlib.import_module(f'amesh.{name}')",
            "    assert legacy is canonical, name",
        )
    )

    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=source_root,
        capture_output=True,
        check=False,
        env={
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("COV_CORE_", "COVERAGE_"))
        },
        text=True,
    )

    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize("module_name", ENTRYPOINT_MODULES)
def test_legacy_module_runner_delegates_to_canonical_main(
    module_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = importlib.import_module(f"amesh.entrypoints.{module_name}")
    calls: list[str] = []

    def fake_main() -> int:
        calls.append(module_name)
        return 0

    monkeypatch.setattr(canonical, "main", fake_main)
    legacy_path = Path(__file__).resolve().parents[1] / "src" / "amesh" / f"{module_name}.py"
    if module_name == "cli":
        with pytest.raises(SystemExit) as raised:
            runpy.run_path(str(legacy_path), run_name="__main__")
        assert raised.value.code == 0
    else:
        runpy.run_path(str(legacy_path), run_name="__main__")

    assert calls == [module_name]
