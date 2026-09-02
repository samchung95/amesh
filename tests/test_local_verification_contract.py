from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_local_verification_aggregate_enforces_repository_quality_gates() -> None:
    script = (ROOT / "scripts" / "verify-local.sh").read_text(encoding="utf-8")
    all_suite = script.split("  all)", maxsplit=1)[1].split("  *)", maxsplit=1)[0]

    assert "--deselect" not in script
    assert "--cov-fail-under=0" not in script
    assert all_suite.index("run_format") < all_suite.index("run_backend")
    assert all_suite.index("run_frontend_lint") < all_suite.index("run_backend")
    assert "python scripts/generate_sdks.py --integrity-check" in script
    assert "npm run check --prefix tools/frontend-contracts" in script
    assert "npm run test --prefix frontend" in script
    assert "test_execution_and_task_deadlines_persist_timeout_category" in script

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["tool"]["coverage"]["report"]["fail_under"] > 0
    assert "postgres:17-alpine" in (ROOT / "docker/compose.verify.yaml").read_text(encoding="utf-8")

    ignored_paths = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".agent-hotel/" in ignored_paths
    assert ".claude/" in ignored_paths
