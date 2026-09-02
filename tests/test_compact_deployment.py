from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _yaml(name: str) -> dict[str, object]:
    value = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_compact_compose_has_one_amesh_process_and_only_postgresql_dependency() -> None:
    compact = _yaml("compose.compact.yaml")
    services = compact["services"]
    assert isinstance(services, dict)
    assert set(services) == {"compact", "compact-volume-init", "postgres"}
    runtime = services["compact"]
    assert runtime["environment"]["OBJECT_STORAGE_BACKEND"] == "local"
    assert runtime["environment"]["READINESS_CHECK_STORAGE"] == "true"
    assert runtime["command"][-1] == "python -m amesh.migrations && exec python -m amesh.compact"
    assert runtime["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert runtime["healthcheck"]["test"][-1].find("/ready") >= 0
    assert runtime["stop_grace_period"] == "45s"

    distributed = _yaml("compose.yaml")["services"]
    assert {
        "api",
        "executor",
        "scheduler",
        "worker",
        "indexer",
        "maintenance",
        "migrate",
        "postgres",
    }.issubset(distributed)


def test_distributed_compose_uses_manifest_aware_migration_gate() -> None:
    services = _yaml("compose.yaml")["services"]
    assert services["migrate"]["command"] == ["python", "-m", "amesh.migrations"]
    assert services["migrate"]["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert services["postgres"]["volumes"] == ["postgres-data:/var/lib/postgresql/data"]
    for role in ("api", "executor", "scheduler", "worker", "indexer", "maintenance"):
        assert (
            services[role]["depends_on"]["migrate"]["condition"] == "service_completed_successfully"
        )


def test_native_package_declares_compact_preflight_migration_and_resource_paths() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = project["project"]["scripts"]
    assert scripts["amesh-compact"] == "amesh.compact:main"
    assert scripts["amesh-preflight"] == "amesh.preflight:main"
    assert scripts["amesh-migrate"] == "amesh.migrations:main"
    assert project["tool"]["setuptools"]["data-files"]["share/amesh/migrations"] == [
        "migrations/*.sql",
        "migrations/manifest.json",
    ]

    runbook = (ROOT / "docs/operations/compact-deployment.md").read_text(encoding="utf-8")
    for required in (
        "Development minimum",
        "Development recommended",
        "Compact production minimum",
        "Compact production recommended",
        "amesh-preflight",
        "amesh-compact",
        "GET /health",
        "GET /ready",
    ):
        assert required in runbook
