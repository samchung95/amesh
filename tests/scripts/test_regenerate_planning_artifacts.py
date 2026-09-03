from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts import regenerate_planning_artifacts as generator

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _planning_tree(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    shutil.copy2(REPOSITORY_ROOT / "project-baseline.json", root)
    shutil.copytree(REPOSITORY_ROOT / "backlog", root / "backlog")
    shutil.copytree(REPOSITORY_ROOT / "requirements", root / "requirements")
    roadmap = root / "docs/product/roadmap.md"
    roadmap.parent.mkdir(parents=True)
    shutil.copy2(REPOSITORY_ROOT / "docs/product/roadmap.md", roadmap)
    generator.regenerate(root)
    return root


def _snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def test_check_accepts_current_artifacts_without_writing_checked_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _planning_tree(tmp_path)
    before = _snapshot(root)
    written_roots: list[Path] = []
    real_write_text = generator.write_text
    real_write_epic_catalog = generator.write_epic_catalog

    def guarded_write_text(target_root: Path, relative_path: str, value: str) -> None:
        written_roots.append(target_root)
        assert target_root != root
        real_write_text(target_root, relative_path, value)

    def guarded_write_epic_catalog(
        target_root: Path,
        manifest: dict[str, object],
        epics: list[dict[str, object]],
    ) -> None:
        written_roots.append(target_root)
        assert target_root != root
        real_write_epic_catalog(target_root, manifest, epics)

    monkeypatch.setattr(generator, "write_text", guarded_write_text)
    monkeypatch.setattr(generator, "write_epic_catalog", guarded_write_epic_catalog)

    assert generator.main(["--check"], root=root) == 0
    assert written_roots
    assert _snapshot(root) == before


def test_check_reports_drift_without_repairing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _planning_tree(tmp_path)
    drifted_path = root / "requirements/URS.md"
    drifted_path.write_text("drifted\n", encoding="utf-8")
    before = _snapshot(root)

    assert generator.main(["--check"], root=root) == 1

    assert "requirements/URS.md" in capsys.readouterr().out
    assert _snapshot(root) == before


def test_check_reports_orphaned_epic_body_without_removing_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _planning_tree(tmp_path)
    orphaned_path = root / "backlog/epics/epic-stale-generated.md"
    orphaned_path.write_text("stale generated body\n", encoding="utf-8")
    before = _snapshot(root)

    assert generator.main(["--check"], root=root) == 1

    assert "backlog/epics/epic-stale-generated.md" in capsys.readouterr().out
    assert _snapshot(root) == before
