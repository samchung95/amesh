from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "amesh"


def _yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_chart_declares_independent_fenced_service_roles() -> None:
    values = _yaml(CHART / "values.yaml")
    roles = values["serviceRoles"]
    assert isinstance(roles, dict)
    assert set(roles) == {"executor", "scheduler", "worker", "indexer", "maintenance"}
    assert all(config["enabled"] for config in roles.values())

    role_template = (CHART / "templates" / "deployment-roles.yaml").read_text(encoding="utf-8")
    for required in (
        'command: ["python", "-m", "amesh.role"]',
        'command: ["python", "-m", "amesh.role", "--drain"]',
        'command: ["python", "-m", "amesh.role", "--check", "liveness"]',
        'command: ["python", "-m", "amesh.role", "--check", "readiness"]',
        "topologySpreadConstraints:",
        "maxUnavailable:",
        "SERVICE_INSTANCE_NAME",
        "SERVICE_FAILURE_ZONE",
    ):
        assert required in role_template
    helpers = (CHART / "templates" / "_helpers.tpl").read_text(encoding="utf-8")
    assert 'define "amesh.enabledRolesJson"' in helpers
    assert "SERVICE_ENABLED_ROLES" in helpers
    assert "kind: PodDisruptionBudget" in (
        CHART / "templates" / "poddisruptionbudgets.yaml"
    ).read_text(encoding="utf-8")


def test_small_medium_and_large_profiles_have_monotonic_replica_capacity() -> None:
    profiles = {
        name: _yaml(CHART / "profiles" / f"{name}.yaml") for name in ("small", "medium", "large")
    }
    for role in ("executor", "scheduler", "worker", "indexer", "maintenance"):
        counts = [profiles[name]["serviceRoles"][role]["replicas"] for name in profiles]
        assert counts == sorted(counts)
        assert counts[0] >= 1
    assert profiles["small"]["server"]["replicas"] == 1
    assert profiles["medium"]["server"]["replicas"] >= 2
    assert profiles["large"]["server"]["replicas"] >= 4
    assert profiles["medium"]["highAvailability"]["whenUnsatisfiable"] == "DoNotSchedule"
    assert profiles["large"]["highAvailability"]["whenUnsatisfiable"] == "DoNotSchedule"


def test_recovery_cronjob_is_opt_in_and_runs_the_qualified_cli() -> None:
    values = _yaml(CHART / "values.yaml")
    recovery = values["recovery"]
    assert recovery["enabled"] is False
    assert recovery["concurrencyPolicy"] == "Forbid"
    assert recovery["schedule"] == "0 3 * * *"

    template = (CHART / "templates" / "recovery-cronjob.yaml").read_text(encoding="utf-8")
    for required in (
        "kind: CronJob",
        ".Values.recovery.enabled",
        "concurrencyPolicy:",
        "- recovery",
        "- exercise",
        "- --scheduled",
        "emptyDir: {}",
    ):
        assert required in template
