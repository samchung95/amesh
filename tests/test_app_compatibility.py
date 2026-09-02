from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path


def test_legacy_app_alias_preserves_monkeypatches_and_openapi_in_fresh_process(
    monkeypatch,
) -> None:
    legacy = importlib.import_module("amesh.app")
    implementation = importlib.import_module("amesh.api.application")

    assert legacy is implementation
    assert legacy.app is implementation.app

    replacement = object()
    monkeypatch.setattr(legacy, "external_orchestration_profile", replacement)
    endpoint = next(
        route.endpoint
        for route in legacy.app.routes
        if getattr(route, "path", None) == "/api/v1/orchestration/profile"
    )
    assert endpoint.__globals__["external_orchestration_profile"] is replacement

    canonical = json.dumps(
        legacy.app.openapi(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    assert len(canonical) == 772147
    assert hashlib.sha256(canonical).hexdigest() == (
        "4e66ab75960907a0890436381fc3b09aa7e161c7c3d4d2b382adfc541984da04"
    )

    source_root = Path(__file__).resolve().parents[1] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source_root), environment.get("PYTHONPATH")) if part
    )
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import hashlib
import importlib
import json

import amesh.app as legacy
from amesh.app import app

implementation = importlib.import_module("amesh.api.application")
document = json.dumps(
    app.openapi(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
).encode()
assert legacy is implementation
assert app is implementation.app
print(len(document), hashlib.sha256(document).hexdigest())
""",
        ],
        cwd=source_root.parent,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )
    assert probe.stdout.strip() == (
        "772147 4e66ab75960907a0890436381fc3b09aa7e161c7c3d4d2b382adfc541984da04"
    )
