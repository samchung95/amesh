from __future__ import annotations

import importlib
import os
import subprocess
import sys


def test_legacy_kestra_module_is_the_canonical_feature_module() -> None:
    legacy = importlib.import_module("amesh.kestra_compatibility")
    canonical = importlib.import_module("amesh.compatibility.kestra")

    assert legacy is canonical
    assert legacy.import_kestra_flow is canonical.import_kestra_flow

    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import importlib; "
                "canonical = importlib.import_module('amesh.compatibility.kestra'); "
                "legacy = importlib.import_module('amesh.kestra_compatibility'); "
                "assert legacy is canonical"
            ),
        ],
        check=True,
        env={
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("COV_CORE_", "COVERAGE_"))
        },
    )
