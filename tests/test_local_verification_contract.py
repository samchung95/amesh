from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_local_verification_aggregate_enforces_repository_quality_gates() -> None:
    script = (ROOT / "scripts" / "verify-local.sh").read_text(encoding="utf-8")
    backend_suite = script.split("run_backend() {", maxsplit=1)[1].split("\n}", maxsplit=1)[0]
    all_suite = script.split("  all)", maxsplit=1)[1].split("  *)", maxsplit=1)[0]

    assert "--deselect" not in script
    assert "--cov-fail-under=0" not in script
    assert 'AMESH_TEST_DATABASE_URL="$DATABASE_URL"' in backend_suite
    assert "--fail-on-missing-postgres" in backend_suite
    assert all_suite.index("run_format") < all_suite.index("run_backend")
    assert all_suite.index("run_frontend_lint") < all_suite.index("run_backend")
    assert "python scripts/generate_sdks.py --integrity-check" in script
    assert "python scripts/validate_env_example.py" in script
    assert "npm run check --prefix tools/frontend-contracts" in script
    assert "npm run test --prefix frontend" in script
    assert "test_execution_and_task_deadlines_persist_timeout_category" in script

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["tool"]["coverage"]["report"]["fail_under"] >= 75
    assert "postgres:17-alpine" in (ROOT / "docker/compose.verify.yaml").read_text(encoding="utf-8")

    ignored_paths = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".agent-hotel/" in ignored_paths
    assert ".claude/" in ignored_paths


@pytest.mark.parametrize(
    "test_target",
    (
        "tests/test_observability.py::"
        "test_database_readiness_pool_slow_query_and_migration_metrics",
        "tests/test_agent_session_scale_qualification.py::"
        "test_live_postgres_projection_passes_the_small_reference_workload",
        "tests/test_restart_qualification.py::"
        "test_live_restart_qualification_produces_passing_report",
    ),
)
def test_backend_gate_fails_for_every_missing_postgres_skip_reason(test_target: str) -> None:
    environment = os.environ.copy()
    environment.pop("AMESH_TEST_DATABASE_URL", None)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--fail-on-missing-postgres",
            test_target,
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 1
    assert "PostgreSQL verification requires AMESH_TEST_DATABASE_URL" in result.stdout
