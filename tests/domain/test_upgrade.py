from __future__ import annotations

from typing import Any, cast

import pytest

from amesh.domain import ConfigurationMigrationKind, ServiceCompatibility
from amesh.plugin_sdk import PluginCatalogManager
from amesh.release_policy import component_compatibility, load_upgrade_policy
from amesh.upgrade import UpgradeService


def test_release_policy_classifies_current_rolling_and_unsafe_versions() -> None:
    policy = load_upgrade_policy()

    assert policy.current_version == "0.2.0"
    assert policy.path("0.1.0", "0.2.0").rolling_compatible
    assert component_compatibility("0.2.0").compatibility is ServiceCompatibility.CURRENT
    assert component_compatibility("0.1.0").compatibility is ServiceCompatibility.ROLLING_COMPATIBLE
    unsafe = component_compatibility("9.0.0")
    assert unsafe.compatibility is ServiceCompatibility.UNSAFE
    assert unsafe.remediation and "install 0.2.0" in unsafe.remediation


def test_explicit_flow_and_plugin_configuration_migration_is_canonical() -> None:
    service = UpgradeService(
        cast(Any, object()),
        cast(Any, object()),
        PluginCatalogManager(),
        cast(Any, object()),
    )
    flow = service.migrate_configuration(
        ConfigurationMigrationKind.FLOW,
        {
            "id": "upgrade",
            "namespace": "tests.upgrade",
            "tasks": [{"id": "return", "type": "core.return", "value": "ok"}],
        },
        target_version="0.2.0",
    )
    assert flow.canonical["id"] == "upgrade"
    assert flow.target_version == "0.2.0"

    plugin = service.migrate_configuration(
        ConfigurationMigrationKind.PLUGIN,
        {
            "schemaVersion": "amesh.plugin/v1",
            "name": "example.upgrade",
            "version": "1.0.0",
            "vendor": "Example",
            "license": "Apache-2.0",
            "compatibility": {
                "platformVersion": ">=0.2.0,<1.0.0",
                "protocolVersions": ["amesh.plugin.rpc/v1"],
            },
            "entryPoints": [
                {
                    "name": "task.main",
                    "type": "task",
                    "transport": "stdio",
                    "target": "bin/plugin",
                    "configurationSchema": {"type": "object"},
                    "documentation": {
                        "title": "Upgrade fixture",
                        "description": "Fixture for upgrade configuration migration.",
                        "category": "Tests",
                    },
                }
            ],
        },
        target_version="0.2.0",
    )
    assert plugin.canonical["compatibility"]["platformVersion"] == ">=0.2.0,<1.0.0"
    assert plugin.warnings

    incompatible = dict(plugin.canonical)
    incompatible["compatibility"] = {
        "platformVersion": "<0.2.0",
        "protocolVersions": ["amesh.plugin.rpc/v1"],
    }
    with pytest.raises(ValueError, match="does not include target"):
        service.migrate_configuration(
            ConfigurationMigrationKind.PLUGIN,
            incompatible,
            target_version="0.2.0",
        )
