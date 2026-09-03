from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.package_sdks import deterministic_zip  # noqa: E402

from scripts import generate_sdks  # noqa: E402


def test_urs_f_0417_0418_generated_sdk_manifest_matches_supported_contract() -> None:
    sdk_root = ROOT / "sdks" / "api"
    openapi = ROOT / "docs" / "api" / "openapi.json"
    manifest = json.loads((sdk_root / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["apiVersion"] == "0.2.0"
    assert manifest["compatibleApiVersions"] == ">=0.2.0,<0.3.0"
    assert manifest["openapiSha256"] == hashlib.sha256(openapi.read_bytes()).hexdigest()
    assert manifest["generatorImage"].endswith(
        "@sha256:5bf3dc75f764c584da8e3344c51b2f3f1e74703461d46a035b5ac1d31515cc88"
    )
    assert {item["language"] for item in manifest["clients"]} == {
        "python",
        "typescript",
        "java",
        "go",
    }
    assert all(item["paginationHelper"] for item in manifest["clients"])

    expected = (
        sdk_root / "python" / "amesh_client" / "api" / "flows_api.py",
        sdk_root / "typescript" / "src" / "apis" / "FlowsApi.ts",
        sdk_root
        / "java"
        / "src"
        / "main"
        / "java"
        / "io"
        / "amesh"
        / "client"
        / "api"
        / "FlowsApi.java",
        sdk_root / "go" / "api_flows.go",
        sdk_root / "python" / "amesh_client" / "pagination.py",
        sdk_root / "typescript" / "src" / "pagination.ts",
        sdk_root / "java" / "src" / "main" / "java" / "io" / "amesh" / "client" / "Pagination.java",
        sdk_root / "go" / "pagination.go",
    )
    assert all(path.is_file() for path in expected)
    assert all(
        (sdk_root / language / "LICENSE").is_file()
        for language in {
            "python",
            "typescript",
            "java",
            "go",
        }
    )
    assert all(
        (sdk_root / language / "docs").is_dir()
        for language in {
            "python",
            "typescript",
            "java",
            "go",
        }
    )
    generate_sdks.verify_sdk_integrity(sdk_root)


@pytest.mark.parametrize("mutation", ["change", "add", "remove"])
def test_generated_sdk_integrity_receipt_rejects_output_tampering(
    tmp_path: Path,
    mutation: str,
) -> None:
    sdk_root = tmp_path / "api"
    sdk_root.mkdir()
    generated = sdk_root / "client.txt"
    generated.write_text("generated client\n", encoding="utf-8")
    (sdk_root / "manifest.json").write_text(
        json.dumps(generate_sdks._manifest_document(sdk_root), indent=2) + "\n",
        encoding="utf-8",
    )

    generate_sdks.verify_sdk_integrity(sdk_root)
    if mutation == "change":
        generated.write_text("manually changed\n", encoding="utf-8")
    elif mutation == "add":
        (sdk_root / "unrecorded.txt").write_text("manual addition\n", encoding="utf-8")
    else:
        generated.unlink()

    with pytest.raises(RuntimeError, match="generationIntegrity"):
        generate_sdks.verify_sdk_integrity(sdk_root)


def test_generated_sdk_integrity_receipt_rejects_openapi_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    openapi = tmp_path / "openapi.json"
    openapi.write_text('{"info":{"version":"0.2.0"}}\n', encoding="utf-8")
    monkeypatch.setattr(generate_sdks, "OPENAPI", openapi)
    sdk_root = tmp_path / "api"
    sdk_root.mkdir()
    (sdk_root / "manifest.json").write_text(
        json.dumps(generate_sdks._manifest_document(sdk_root), indent=2) + "\n",
        encoding="utf-8",
    )

    openapi.write_text('{"info":{"version":"0.2.1"}}\n', encoding="utf-8")

    with pytest.raises(RuntimeError, match=r"apiVersion|openapiSha256"):
        generate_sdks.verify_sdk_integrity(sdk_root)


def test_urs_f_0418_sdk_release_archives_are_reproducible(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "client.txt").write_text("typed client\n", encoding="utf-8")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    deterministic_zip(source, first)
    deterministic_zip(source, second)
    assert first.read_bytes() == second.read_bytes()
