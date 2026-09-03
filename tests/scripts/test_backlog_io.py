from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from scripts.backlog_io import EpicCatalogError, load_epic_catalog, write_epic_catalog


def _manifest(*, archive_files: list[str] | None = None) -> dict[str, object]:
    metadata: dict[str, object] = {"generated_on": "2026-09-03"}
    if archive_files is not None:
        metadata["archive_files"] = archive_files
    return {"metadata": metadata, "epics": []}


def _epic(epic_id: str, wave: int, state: str = "open") -> dict[str, object]:
    return {"id": epic_id, "wave": wave, "state": state, "title": epic_id}


def _write_document(root: Path, relative: str, document: dict[str, object]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def test_write_is_deterministic_and_normalizes_json_bytes(tmp_path: Path) -> None:
    manifest = _manifest()
    epics = [_epic("EPIC-002", 2), _epic("EPIC-001", 1), _epic("EPIC-003", 3, "done")]

    write_epic_catalog(tmp_path, manifest, epics)
    first_active = (tmp_path / "backlog/epics.json").read_bytes()
    first_archive = (tmp_path / "backlog/archive/epics.done.json").read_bytes()
    write_epic_catalog(tmp_path, manifest, list(reversed(epics)))

    assert first_active == (tmp_path / "backlog/epics.json").read_bytes()
    assert first_archive == (tmp_path / "backlog/archive/epics.done.json").read_bytes()
    assert first_active.endswith(b"\n") and b"\r\n" not in first_active
    assert json.loads(first_active)["metadata"]["epic_count"] == 3
    assert json.loads(first_active)["metadata"]["active_epic_count"] == 2
    assert json.loads(first_active)["metadata"]["archived_epic_count"] == 1
    assert json.loads(first_active)["metadata"]["archive_files"] == [
        "backlog/archive/epics.done.json"
    ]


def test_write_moves_done_state_to_archive_and_load_combines_sorted_records(tmp_path: Path) -> None:
    manifest = _manifest()
    write_epic_catalog(tmp_path, manifest, [_epic("EPIC-002", 2), _epic("EPIC-001", 1, "done")])

    catalog = load_epic_catalog(tmp_path)

    assert [record["id"] for record in catalog.epics] == ["EPIC-001", "EPIC-002"]
    assert json.loads((tmp_path / "backlog/epics.json").read_text())["epics"] == [
        _epic("EPIC-002", 2)
    ]
    assert json.loads((tmp_path / "backlog/archive/epics.done.json").read_text())["epics"] == [
        _epic("EPIC-001", 1, "done")
    ]


def test_regeneration_mode_loads_state_changes_before_writer_repartitions(tmp_path: Path) -> None:
    archive_path = "backlog/archive/epics.done.json"
    _write_document(
        tmp_path,
        "backlog/epics.json",
        {
            "metadata": {"archive_files": [archive_path]},
            "epics": [_epic("EPIC-001", 1, "done")],
        },
    )
    _write_document(
        tmp_path,
        archive_path,
        {"epics": [_epic("EPIC-002", 2, "open")]},
    )

    catalog = load_epic_catalog(tmp_path, allow_state_moves=True)
    write_epic_catalog(tmp_path, catalog.manifest, catalog.epics)

    active = json.loads((tmp_path / "backlog/epics.json").read_text())["epics"]
    archived = json.loads((tmp_path / archive_path).read_text())["epics"]
    assert active == [_epic("EPIC-002", 2, "open")]
    assert archived == [_epic("EPIC-001", 1, "done")]


@pytest.mark.parametrize(
    ("active", "archived"),
    [
        ([_epic("EPIC-001", 1)], [_epic("EPIC-001", 2, "done")]),
        ([_epic("EPIC-001", 1), _epic("EPIC-001", 2)], []),
    ],
)
def test_load_rejects_duplicate_epic_ids(
    tmp_path: Path, active: list[dict[str, object]], archived: list[dict[str, object]]
) -> None:
    _write_document(
        tmp_path,
        "backlog/epics.json",
        {"metadata": {"archive_files": ["backlog/archive/done.json"]}, "epics": active},
    )
    _write_document(tmp_path, "backlog/archive/done.json", {"epics": archived})

    with pytest.raises(EpicCatalogError, match="duplicate epic id"):
        load_epic_catalog(tmp_path)


@pytest.mark.parametrize(
    "archive_path", ["../outside.json", "/tmp/outside.json", "C:\\outside.json"]
)
def test_load_rejects_unsafe_archive_paths(tmp_path: Path, archive_path: str) -> None:
    _write_document(
        tmp_path, "backlog/epics.json", {"metadata": {"archive_files": [archive_path]}, "epics": []}
    )

    with pytest.raises(EpicCatalogError, match="unsafe archive path"):
        load_epic_catalog(tmp_path)


def test_load_rejects_duplicate_archive_paths_and_missing_archive(tmp_path: Path) -> None:
    _write_document(
        tmp_path,
        "backlog/epics.json",
        {
            "metadata": {
                "archive_files": ["backlog/archive/done.json", "backlog/archive/done.json"]
            },
            "epics": [],
        },
    )
    with pytest.raises(EpicCatalogError, match="duplicate archive path"):
        load_epic_catalog(tmp_path)

    _write_document(
        tmp_path,
        "backlog/epics.json",
        {"metadata": {"archive_files": ["backlog/archive/missing.json"]}, "epics": []},
    )
    with pytest.raises(EpicCatalogError, match="missing"):
        load_epic_catalog(tmp_path)


def test_load_requires_an_explicit_archive_declaration(tmp_path: Path) -> None:
    _write_document(tmp_path, "backlog/epics.json", _manifest())

    with pytest.raises(EpicCatalogError, match="archive_files must declare"):
        load_epic_catalog(tmp_path)

    _write_document(
        tmp_path,
        "backlog/epics.json",
        {"metadata": {"archive_files": []}, "epics": []},
    )
    with pytest.raises(EpicCatalogError, match="non-empty list"):
        load_epic_catalog(tmp_path)


def test_writer_recovers_a_completed_record_after_final_active_publish_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest()
    original = [_epic("EPIC-001", 1), _epic("EPIC-002", 2, "done")]
    write_epic_catalog(tmp_path, manifest, original)
    catalog = load_epic_catalog(tmp_path)
    transitioned = [
        {**record, "state": "done"} if record["id"] == "EPIC-001" else record
        for record in catalog.epics
    ]
    real_replace = os.replace

    active_replacements = 0

    def fail_final_active_replace(source: str | Path, destination: str | Path) -> None:
        nonlocal active_replacements
        if Path(destination) == tmp_path / "backlog/epics.json":
            active_replacements += 1
        if active_replacements == 2:
            raise OSError("simulated active publish failure")
        real_replace(source, destination)

    monkeypatch.setattr("scripts.backlog_io.os.replace", fail_final_active_replace)

    with pytest.raises(EpicCatalogError, match="simulated active publish failure"):
        write_epic_catalog(tmp_path, catalog.manifest, transitioned)

    active = json.loads((tmp_path / "backlog/epics.json").read_text())["epics"]
    archived = json.loads((tmp_path / "backlog/archive/epics.done.json").read_text())["epics"]
    assert {record["id"] for record in active + archived} == {"EPIC-001", "EPIC-002"}
    assert not list((tmp_path / "backlog").rglob("*.tmp"))

    monkeypatch.setattr("scripts.backlog_io.os.replace", real_replace)
    recovered = load_epic_catalog(tmp_path, allow_state_moves=True)
    write_epic_catalog(tmp_path, recovered.manifest, recovered.epics)
    assert json.loads((tmp_path / "backlog/epics.json").read_text())["epics"] == []


def test_writer_does_not_lose_a_reopened_record_when_final_active_publish_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest()
    write_epic_catalog(tmp_path, manifest, [_epic("EPIC-001", 1, "done")])
    catalog = load_epic_catalog(tmp_path)
    reopened = [{**record, "state": "open"} for record in catalog.epics]
    real_replace = os.replace
    active_replacements = 0

    def fail_final_active_replace(source: str | Path, destination: str | Path) -> None:
        nonlocal active_replacements
        if Path(destination) == tmp_path / "backlog/epics.json":
            active_replacements += 1
        if active_replacements == 2:
            raise OSError("simulated active publish failure")
        real_replace(source, destination)

    monkeypatch.setattr("scripts.backlog_io.os.replace", fail_final_active_replace)

    with pytest.raises(EpicCatalogError, match="simulated active publish failure"):
        write_epic_catalog(tmp_path, catalog.manifest, reopened)

    active = json.loads((tmp_path / "backlog/epics.json").read_text())["epics"]
    archived = json.loads((tmp_path / "backlog/archive/epics.done.json").read_text())["epics"]
    assert {record["id"] for record in active + archived} == {"EPIC-001"}
    assert active == [_epic("EPIC-001", 1, "open")]


def test_writer_recovers_a_reopened_record_after_archive_publish_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _manifest()
    write_epic_catalog(tmp_path, manifest, [_epic("EPIC-001", 1, "done")])
    catalog = load_epic_catalog(tmp_path)
    reopened = [{**record, "state": "open"} for record in catalog.epics]
    real_replace = os.replace

    def fail_archive_replace(source: str | Path, destination: str | Path) -> None:
        if Path(destination) == tmp_path / "backlog/archive/epics.done.json":
            raise OSError("simulated archive publish failure")
        real_replace(source, destination)

    monkeypatch.setattr("scripts.backlog_io.os.replace", fail_archive_replace)

    with pytest.raises(EpicCatalogError, match="simulated archive publish failure"):
        write_epic_catalog(tmp_path, catalog.manifest, reopened)

    active_document = json.loads((tmp_path / "backlog/epics.json").read_text())
    archived = json.loads((tmp_path / "backlog/archive/epics.done.json").read_text())["epics"]
    assert active_document["metadata"]["partition_transition"] == 1
    assert active_document["epics"] == [_epic("EPIC-001", 1, "open")]
    assert archived == [_epic("EPIC-001", 1, "done")]

    monkeypatch.setattr("scripts.backlog_io.os.replace", real_replace)
    recovered = load_epic_catalog(tmp_path, allow_state_moves=True)
    write_epic_catalog(tmp_path, recovered.manifest, recovered.epics)
    active_document = json.loads((tmp_path / "backlog/epics.json").read_text())
    assert "partition_transition" not in active_document["metadata"]
    assert active_document["epics"] == [_epic("EPIC-001", 1, "open")]
    assert json.loads((tmp_path / "backlog/archive/epics.done.json").read_text())["epics"] == []


@pytest.mark.parametrize(
    ("active", "archived", "message"),
    [
        ([_epic("EPIC-001", 1, "done")], [], "active catalog contains done"),
        ([], [_epic("EPIC-001", 1, "open")], "contains non-done"),
    ],
)
def test_load_rejects_partition_violations(
    tmp_path: Path,
    active: list[dict[str, object]],
    archived: list[dict[str, object]],
    message: str,
) -> None:
    archive_path = "backlog/archive/done.json"
    _write_document(
        tmp_path,
        "backlog/epics.json",
        {"metadata": {"archive_files": [archive_path]}, "epics": active},
    )
    _write_document(tmp_path, archive_path, {"epics": archived})

    with pytest.raises(EpicCatalogError, match=message):
        load_epic_catalog(tmp_path)
