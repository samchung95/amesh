from __future__ import annotations

from pathlib import Path

from amesh.plugin_sdk import PLUGIN_WIRE_VERSION, REQUIRED_WIRE_FEATURES

ROOT = Path(__file__).resolve().parents[2]
SDK_FILES = (
    ROOT / "sdks/plugin-wire/typescript/index.ts",
    ROOT / "sdks/plugin-wire/java/io/amesh/plugin/Wire.java",
    ROOT / "sdks/plugin-wire/go/wire.go",
)


def test_language_sdk_contracts_pin_wire_version_and_required_features() -> None:
    for path in SDK_FILES:
        content = path.read_text(encoding="utf-8")
        assert PLUGIN_WIRE_VERSION in content
        for feature in REQUIRED_WIRE_FEATURES:
            assert feature.value in content
        assert "capability" in content.lower()
        assert "workloadToken" in content
