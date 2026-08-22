from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType


def load_clean_room_module() -> ModuleType:
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_clean_room.py"
    spec = importlib.util.spec_from_file_location("amesh_check_clean_room", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("clean-room script could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


clean_room = load_clean_room_module()


def test_repository_governance_records_are_coherent() -> None:
    assert clean_room.governance_findings() == []


def test_governance_gate_rejects_target_drift(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    (tmp_path / "requirements").mkdir()
    for relative in (
        Path("project-baseline.json"),
        Path("requirements/urs.json"),
        Path("requirements/source-provenance.json"),
        Path("requirements/compatibility-inventory.json"),
    ):
        shutil.copyfile(repository / relative, tmp_path / relative)
    baseline_path = tmp_path / "project-baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline["parity_target"]["version"] = "unexpected-target"
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

    findings = clean_room.governance_findings(tmp_path)

    assert findings == [
        "URS target differs from project-baseline.json",
        "source-provenance target differs from project-baseline.json",
        "compatibility-inventory target differs from project-baseline.json",
    ]


def test_lexical_gate_rejects_upstream_implementation_markers(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    marker = "Kestra" + "Exception"
    (source / "copied.py").write_text(f"class {marker}: pass\n", encoding="utf-8")

    findings = clean_room.lexical_findings(tmp_path)

    assert len(findings) == 1
    assert "upstream-specific class name" in findings[0]


def test_similarity_gate_reports_only_paths_and_fingerprint_counts(tmp_path: Path) -> None:
    implementation = tmp_path / "implementation"
    reference = tmp_path / "reference"
    (implementation / "src").mkdir(parents=True)
    reference.mkdir()
    shared_tokens = " ".join(f"distinct_token_{index}" for index in range(40))
    (implementation / "src" / "candidate.py").write_text(shared_tokens, encoding="utf-8")
    (reference / "Reference.java").write_text(shared_tokens, encoding="utf-8")

    findings = clean_room.similarity_findings(
        reference,
        root=implementation,
        require_pinned_reference=False,
    )

    assert len(findings) == 1
    assert "src/candidate.py" in findings[0]
    assert "Reference.java" in findings[0]
    assert "distinct_token" not in findings[0]


def test_similarity_gate_rejects_reference_inside_implementation(tmp_path: Path) -> None:
    (tmp_path / "reference").mkdir()

    assert clean_room.similarity_findings(
        tmp_path / "reference",
        root=tmp_path,
        require_pinned_reference=False,
    ) == ["reference tree must be outside the AMESH implementation repository"]
