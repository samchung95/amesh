from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "charts" / "amesh" / "observability"


def test_reference_dashboard_covers_required_operational_signals_without_id_labels() -> None:
    dashboard = json.loads((ASSETS / "grafana-dashboard.json").read_text(encoding="utf-8"))
    titles = {panel["title"] for panel in dashboard["panels"]}
    assert titles == {
        "Availability",
        "Operation p95 latency",
        "Database and admission saturation",
        "Failures",
        "Queue and search lag",
        "Stuck work",
        "Worker capacity",
    }
    expressions = "\n".join(
        target["expr"] for panel in dashboard["panels"] for target in panel.get("targets", [])
    )
    for forbidden in (
        "tenant_id",
        "flow_id",
        "execution_id",
        "task_run_id",
        "correlation_id",
        "trace_id",
    ):
        assert forbidden not in expressions


def test_reference_alerts_are_actionable_and_link_to_existing_runbook_sections() -> None:
    rules = yaml.safe_load((ASSETS / "prometheus-alerts.yaml").read_text(encoding="utf-8"))[
        "groups"
    ][0]["rules"]
    assert {rule["labels"]["signal"] for rule in rules} == {
        "availability",
        "latency",
        "saturation",
        "failures",
        "lag",
        "stuck-work",
    }
    for rule in rules:
        annotations = rule["annotations"]
        assert annotations["summary"]
        assert annotations["likely_causes"]
        assert annotations["impact"]
        path_text, fragment = annotations["runbook_url"].split("#", maxsplit=1)
        runbook = (ROOT / path_text).read_text(encoding="utf-8").casefold()
        assert f"### {fragment.replace('-', ' ')}" in runbook


def test_helm_configmap_packages_dashboard_and_alert_assets() -> None:
    template = (ROOT / "charts" / "amesh" / "templates" / "observability-configmap.yaml").read_text(
        encoding="utf-8"
    )
    assert "grafana-dashboard.json" in template
    assert "prometheus-alerts.yaml" in template
    assert 'grafana_dashboard: "1"' in template
