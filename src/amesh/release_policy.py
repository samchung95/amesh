from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from amesh.domain.service_topology import ServiceCompatibility
from amesh.domain.upgrade import UpgradePolicy


@dataclass(frozen=True)
class ComponentCompatibilityDecision:
    compatibility: ServiceCompatibility
    remediation: str | None


def upgrade_policy_path() -> Path:
    return Path(__file__).resolve().parent / "resources" / "upgrade-policy.json"


@lru_cache
def load_upgrade_policy(path: Path | None = None) -> UpgradePolicy:
    selected = path or upgrade_policy_path()
    return UpgradePolicy.model_validate(json.loads(selected.read_text(encoding="utf-8")))


def component_compatibility(
    version: str,
    *,
    policy: UpgradePolicy | None = None,
) -> ComponentCompatibilityDecision:
    selected = policy or load_upgrade_policy()
    if version == selected.current_version:
        return ComponentCompatibilityDecision(ServiceCompatibility.CURRENT, None)
    rolling_path = next(
        (
            path
            for path in selected.paths
            if path.from_version == version
            and path.to_version == selected.current_version
            and path.rolling_compatible
        ),
        None,
    )
    if rolling_path is not None:
        return ComponentCompatibilityDecision(
            ServiceCompatibility.ROLLING_COMPATIBLE,
            (
                f"drain the {version} instance after its {selected.current_version} replacement "
                "is ready"
            ),
        )
    supported = ", ".join(release.version for release in selected.releases)
    return ComponentCompatibilityDecision(
        ServiceCompatibility.UNSAFE,
        (
            f"install {selected.current_version}, or first follow a declared upgrade path from one "
            f"of: {supported}"
        ),
    )
