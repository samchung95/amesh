from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SOURCE_ROOT = _PROJECT_ROOT / "src"
_IMPORT_CODE = "import importlib, sys; importlib.import_module(sys.argv[1])"


def _production_modules() -> tuple[str, ...]:
    package_root = _SOURCE_ROOT / "amesh"
    modules: set[str] = set()
    for path in package_root.rglob("*.py"):
        relative = path.relative_to(package_root).with_suffix("").as_posix().replace("/", ".")
        if relative == "__main__":
            continue
        if relative == "__init__":
            modules.add("amesh")
        elif relative.endswith(".__init__"):
            modules.add(f"amesh.{relative[:-9]}")
        else:
            modules.add(f"amesh.{relative}")
    return tuple(sorted(modules))


def _import_in_fresh_process(module_name: str) -> tuple[str, str]:
    python_path = os.pathsep.join(
        item for item in (str(_SOURCE_ROOT), os.environ.get("PYTHONPATH", "")) if item
    )
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("COV_CORE_", "COVERAGE_"))
    }
    environment["PYTHONPATH"] = python_path
    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_CODE, module_name],
        cwd=_PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode:
        return module_name, result.stderr or result.stdout
    return module_name, ""


def test_every_production_module_imports_in_a_fresh_process() -> None:
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(_import_in_fresh_process, module_name)
            for module_name in _production_modules()
        ]
        for future in as_completed(futures):
            module_name, output = future.result()
            if output:
                failures.append((module_name, output))
    if failures:
        details = "\n\n".join(f"{name}:\n{output}" for name, output in sorted(failures))
        pytest.fail(f"production modules failed fresh-process import:\n{details}")
