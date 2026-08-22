from __future__ import annotations

import json
from pathlib import Path

import yaml

from amesh.cli import main
from amesh.plugin_sdk import (
    REFERENCE_FIXTURES,
    PluginQualityLevel,
    certify_plugin,
    generate_plugin_documentation,
    quality_level_criteria,
    sandbox_configuration,
    scaffold_plugin,
)


def _scaffold(tmp_path: Path) -> Path:
    root = tmp_path / "example-plugin"
    scaffold_plugin(root, name="example.certification")
    return root


def _pass_reference_fixtures(root: Path) -> None:
    for name in REFERENCE_FIXTURES:
        (root / "certification" / "evidence" / f"{name}.json").write_text(
            json.dumps({"status": "passed", "test": f"tests/test_{name}.py"}) + "\n",
            encoding="utf-8",
        )


def test_urs_f_0391_scaffold_and_local_configuration_sandbox(tmp_path: Path) -> None:
    root = _scaffold(tmp_path)
    expected = {
        "amesh-plugin.yaml",
        "plugin.py",
        "pyproject.toml",
        "LICENSE",
        "README.md",
        "sample.yaml",
    }
    assert expected.issubset(
        {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    )

    valid = sandbox_configuration(root, "task.echo", {"message": "hello"})
    invalid = sandbox_configuration(root, "task.echo", {})

    assert valid["valid"] is True
    assert valid["catalog"]["uiControls"][0]["property"] == "message"
    assert invalid["valid"] is False
    assert invalid["errors"][0]["code"] == "plugin.configuration.invalid"


def test_urs_f_0392_0393_0395_one_suite_assigns_objective_levels(tmp_path: Path) -> None:
    root = _scaffold(tmp_path)
    initial = certify_plugin(root)
    assert initial.quality_level is PluginQualityLevel.COMMUNITY
    assert initial.passed is False
    assert next(item for item in initial.checks if item.category == "contract").passed is False

    _pass_reference_fixtures(root)
    verified = certify_plugin(root)
    assert verified.passed is True
    assert verified.quality_level is PluginQualityLevel.VERIFIED
    assert verified.fixtures == REFERENCE_FIXTURES
    assert {item.category for item in verified.checks} == {
        "manifest",
        "schema",
        "contract",
        "security",
        "license",
        "compatibility",
    }
    assert set(quality_level_criteria()) == {
        PluginQualityLevel.COMMUNITY,
        PluginQualityLevel.VERIFIED,
        PluginQualityLevel.CERTIFIED,
    }


def test_urs_f_0394_generates_human_docs_and_sample_configuration(tmp_path: Path) -> None:
    root = _scaffold(tmp_path)
    documentation, sample = generate_plugin_documentation(root, tmp_path / "generated")

    assert "# example.certification 0.1.0" in documentation.read_text(encoding="utf-8")
    payload = yaml.safe_load(sample.read_text(encoding="utf-8"))
    assert payload["entryPoints"] == [{"type": "example.certification.echo", "message": "hello"}]


def test_urs_f_0396_public_ci_evidence_promotes_reproducible_result(tmp_path: Path) -> None:
    root = _scaffold(tmp_path)
    _pass_reference_fixtures(root)
    (root / "certification" / "evidence.json").write_text(
        json.dumps(
            {
                "sourceCommit": "a" * 40,
                "runUrl": "https://github.com/example/plugin/actions/runs/123",
                "workflow": "plugin-certification",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    first = certify_plugin(root)
    second = certify_plugin(root)

    assert first.quality_level is PluginQualityLevel.CERTIFIED
    assert first.input_digest == second.input_digest
    assert first.public_ci is not None
    assert first.public_ci.source_commit == "a" * 40


def test_urs_f_0397_release_matrix_tracks_incompatible_platforms(tmp_path: Path) -> None:
    root = _scaffold(tmp_path)
    _pass_reference_fixtures(root)

    report = certify_plugin(root, platform_versions=("0.2.0", "0.3.0"))

    assert [(item.platform_version, item.compatible) for item in report.compatibility] == [
        ("0.2.0", True),
        ("0.3.0", False),
    ]
    assert next(item for item in report.checks if item.category == "compatibility").passed is False
    assert report.quality_level is PluginQualityLevel.COMMUNITY


def test_certification_cli_scaffolds_checks_docs_sandbox_and_criteria(
    tmp_path: Path,
    capsys: object,
) -> None:
    del capsys
    root = tmp_path / "cli-plugin"
    assert main(["plugins", "scaffold", str(root), "--name", "example.cli"]) == 0
    _pass_reference_fixtures(root)
    report_path = tmp_path / "report.json"
    assert (
        main(
            [
                "plugins",
                "certify",
                str(root),
                "--output",
                str(report_path),
            ]
        )
        == 0
    )
    assert json.loads(report_path.read_text(encoding="utf-8"))["qualityLevel"] == "verified"

    config = tmp_path / "config.yaml"
    config.write_text("message: hello\n", encoding="utf-8")
    assert (
        main(
            [
                "plugins",
                "sandbox",
                str(root),
                "task.echo",
                "--configuration",
                str(config),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "plugins",
                "docs",
                str(root),
                "--output-dir",
                str(tmp_path / "docs"),
            ]
        )
        == 0
    )
    assert main(["plugins", "criteria"]) == 0
