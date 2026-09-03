from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ADR_ROOT = ROOT / "docs" / "adr"
ADR_INDEX = ADR_ROOT / "README.md"
UI_AUDIT_ROOT = ROOT / "docs" / "product" / "ui-audit"
SCREENSHOT_ROOT = UI_AUDIT_ROOT / "screenshots"
SCREENSHOT_SUFFIXES = frozenset(
    {".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff", ".webp"}
)
UNTRACKED_BUILD_DIRECTORIES = frozenset({".venv", "node_modules"})


def _nav_targets(node: Any) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, list):
        return [target for child in node for target in _nav_targets(child)]
    if isinstance(node, dict):
        return [target for child in node.values() for target in _nav_targets(child)]
    return []


def _tracked_images() -> tuple[Path, ...]:
    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        tracked = None

    if tracked is not None and tracked.returncode == 0:
        candidates = (ROOT / line for line in tracked.stdout.splitlines())
    else:
        # Docker verification excludes .git but creates dependency trees after COPY.
        candidates = (
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and UNTRACKED_BUILD_DIRECTORIES.isdisjoint(path.relative_to(ROOT).parts)
        )
    return tuple(path for path in candidates if path.suffix.lower() in SCREENSHOT_SUFFIXES)


def test_every_adr_is_indexed_exactly_once() -> None:
    index = ADR_INDEX.read_text(encoding="utf-8")
    indexed = re.findall(r"\]\((\d{3}-[^)]+\.md)\)", index)
    actual = sorted(path.name for path in ADR_ROOT.glob("[0-9][0-9][0-9]-*.md"))
    counts = Counter(indexed)

    assert sorted(counts) == actual
    assert {name: count for name, count in counts.items() if count != 1} == {}


def test_adr_index_is_in_mkdocs_navigation_exactly_once() -> None:
    configuration = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    assert _nav_targets(configuration["nav"]).count("adr/README.md") == 1


def test_tracked_screenshots_live_only_under_canonical_root() -> None:
    outside = sorted(
        path.relative_to(ROOT).as_posix()
        for path in _tracked_images()
        if not path.is_relative_to(SCREENSHOT_ROOT)
    )
    assert outside == []


def test_all_existing_screenshot_sets_are_inventoried_exactly_once() -> None:
    readme = (UI_AUDIT_ROOT / "README.md").read_text(encoding="utf-8")
    inventory = readme.split("## Evidence-set retention", maxsplit=1)[1].split(
        "## Screenshot inventory", maxsplit=1
    )[0]
    documented = re.findall(r"\]\(screenshots/([^/)]+)/\)", inventory)
    actual = sorted(path.name for path in SCREENSHOT_ROOT.iterdir() if path.is_dir())
    counts = Counter(documented)

    assert sorted(counts) == actual
    assert {name: count for name, count in counts.items() if count != 1} == {}
