from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "charts" / "amesh"


def test_operator_profile_is_opt_in_secret_backed_and_namespace_scoped() -> None:
    values = yaml.safe_load((CHART / "values.yaml").read_text(encoding="utf-8"))
    operator = values["operator"]
    assert operator["enabled"] is False
    assert operator["clusterWideRBAC"] is False
    assert operator["targets"] == []
    deployment = (CHART / "templates" / "operator-deployment.yaml").read_text(encoding="utf-8")
    rbac = (CHART / "templates" / "operator-rbac.yaml").read_text(encoding="utf-8")
    assert 'command: ["python", "-m", "amesh.operator"]' in deployment
    assert "AMESH_OPERATOR_TARGETS" in deployment
    assert "secretKeyRef" not in deployment
    assert 'resources: ["secrets"]' in rbac
    assert 'verbs: ["get"]' in rbac
    assert "ameshpluginpolicies/status" in rbac
