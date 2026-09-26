from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from scripts.backlog_io import load_epic_catalog

ROOT = Path(__file__).resolve().parents[2]


def _epic_counts() -> tuple[int, int, int]:
    states = Counter(epic.get("state") for epic in load_epic_catalog(ROOT).epics)
    total = sum(states.values())
    return total, states["done"], total - states["done"]


def test_implementation_status_epic_counts_match_catalog() -> None:
    total, done, remaining = _epic_counts()
    status = (ROOT / "IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")

    assert f"{total} epics ({done} done, {remaining} open)" in status
    for pattern, expected in (
        (r"(\d+) epics", total),
        (r"(\d+) done", done),
        (r"(\d+) open", remaining),
    ):
        for match in re.finditer(pattern, status):
            assert int(match.group(1)) == expected, match.group(0)


def test_readme_epic_count_matches_catalog() -> None:
    total, _, _ = _epic_counts()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert f"**{total} implementation epics**" in readme
