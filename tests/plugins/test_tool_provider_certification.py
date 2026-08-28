from __future__ import annotations

import pytest

from amesh.plugin_sdk import certify_tool_provider


def _document() -> dict[str, object]:
    provider = {"kind": "plugin", "key": "example.tools", "revision": 1}
    return {
        "provider": provider,
        "tenantId": "tenant-a",
        "namespace": "examples",
        "digest": "sha256:" + "a" * 64,
        "tools": [
            {
                "provider": provider,
                "name": "echo",
                "inputSchema": {"type": "object"},
                "impact": "READ_ONLY",
            }
        ],
    }


def test_provider_neutral_certification_checks_shared_contract() -> None:
    report = certify_tool_provider(_document())

    assert report.passed
    assert report.tool_count == 1
    assert report.discovery_digest.startswith("sha256:")


def test_provider_certification_rejects_mismatched_tool_identity() -> None:
    document = _document()
    document["tools"] = [
        {
            **document["tools"][0],  # type: ignore[index]
            "provider": {"kind": "plugin", "key": "other.tools", "revision": 1},
        }
    ]

    with pytest.raises(ValueError, match="does not match"):
        certify_tool_provider(document)
