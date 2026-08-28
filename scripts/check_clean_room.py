#!/usr/bin/env python3
"""Validate AMESH clean-room provenance and optional reference similarity.

Usage:
    python scripts/check_clean_room.py
    python scripts/check_clean_room.py --reference-tree ../isolated-kestra-checkout

The reference checkout must remain outside this repository. Similarity findings expose only
file paths and one-way token-shingle counts; reference source text is never copied into AMESH.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEXICAL_SCAN_DIRS = ("src", "frontend/src", "tests", "migrations", "examples")
SIMILARITY_SCAN_DIRS = (
    "src",
    "frontend/src",
    "tests",
    "scripts",
    "migrations",
    "examples",
    "docs",
    "requirements",
)
FORBIDDEN = {
    r"\bio\.kestra\b": "Kestra Java package name in implementation code",
    r"\bkestra-io/kestra\b": "upstream repository path in implementation code",
    r"\bKestraException\b": "upstream-specific class name",
    r"\bAbstractTask\b": "upstream-specific class pattern",
}
LEXICAL_SUFFIXES = {".py", ".sql", ".ts", ".tsx", ".yaml", ".yml", ".json", ".toml"}
SIMILARITY_SUFFIXES = {
    ".java",
    ".js",
    ".jsx",
    ".json",
    ".kt",
    ".kts",
    ".md",
    ".proto",
    ".py",
    ".rst",
    ".sql",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
}
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "build",
    "dist",
    "node_modules",
}
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
SHINGLE_SIZE = 24
MIN_SHARED_SHINGLES = 4


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_files(base: Path, suffixes: set[str]) -> Iterable[Path]:
    if not base.exists():
        return
    for path in base.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in suffixes
            and not IGNORED_PARTS.intersection(path.relative_to(base).parts)
        ):
            yield path


def lexical_findings(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    for directory in LEXICAL_SCAN_DIRS:
        base = root / directory
        for path in iter_files(base, LEXICAL_SUFFIXES):
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern, reason in FORBIDDEN.items():
                if re.search(pattern, text, re.IGNORECASE):
                    findings.append(f"{path.relative_to(root)}: {reason}: /{pattern}/")
    return findings


def governance_findings(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    baseline = load_json(root / "project-baseline.json")
    urs = load_json(root / "requirements" / "urs.json")
    provenance = load_json(root / "requirements" / "source-provenance.json")
    inventory = load_json(root / "requirements" / "compatibility-inventory.json")
    target = baseline["parity_target"]
    if urs["metadata"]["parity_target"] != target:
        findings.append("URS target differs from project-baseline.json")
    if provenance["target"] != target:
        findings.append("source-provenance target differs from project-baseline.json")
    if inventory["target"] != target:
        findings.append("compatibility-inventory target differs from project-baseline.json")

    source_ids = {item["id"] for item in provenance["sources"]}
    requirements = urs["functional_requirements"]
    items = inventory["items"]
    if [item["requirement_id"] for item in items] != [item["id"] for item in requirements]:
        findings.append("compatibility inventory does not cover each functional requirement once")
    for item in items:
        unknown_sources = set(item["source_ids"]) - source_ids
        if unknown_sources:
            findings.append(
                f"{item['requirement_id']}: unknown source IDs {sorted(unknown_sources)}"
            )

    roles = provenance.get("strict_mode", {}).get("required_roles", [])
    if roles != ["reference-researcher", "implementer", "reviewer", "verifier"]:
        findings.append("strict clean-room mode does not define four separated roles")
    if not provenance.get("strict_mode", {}).get("allowed_handoff_artifacts"):
        findings.append("strict clean-room mode lacks allowed handoff artifacts")
    if not provenance.get("strict_mode", {}).get("forbidden_handoff_artifacts"):
        findings.append("strict clean-room mode lacks forbidden handoff artifacts")
    return findings


def token_shingles(path: Path, size: int = SHINGLE_SIZE) -> set[str]:
    tokens = [
        match.group(0).casefold()
        for match in TOKEN_PATTERN.finditer(path.read_text(encoding="utf-8", errors="replace"))
    ]
    if len(tokens) < size:
        return set()
    return {
        hashlib.sha256("\x1f".join(tokens[index : index + size]).encode()).hexdigest()
        for index in range(len(tokens) - size + 1)
    }


def reference_commit(reference_tree: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(reference_tree), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip().casefold()


def similarity_findings(
    reference_tree: Path,
    *,
    root: Path = ROOT,
    require_pinned_reference: bool = True,
    shingle_size: int = SHINGLE_SIZE,
    minimum_shared: int = MIN_SHARED_SHINGLES,
) -> list[str]:
    root = root.resolve()
    reference_tree = reference_tree.resolve()
    if reference_tree == root or reference_tree.is_relative_to(root):
        return ["reference tree must be outside the AMESH implementation repository"]
    if not reference_tree.is_dir():
        return [f"reference tree does not exist: {reference_tree}"]

    if require_pinned_reference:
        expected_commit = load_json(root / "project-baseline.json")["parity_target"]["commit"]
        actual_commit = reference_commit(reference_tree)
        if actual_commit != expected_commit.casefold():
            return [
                "reference tree is not the pinned target commit: "
                f"expected {expected_commit}, observed {actual_commit or 'no Git commit'}"
            ]

    implementation_hashes: dict[str, set[str]] = defaultdict(set)
    for directory in SIMILARITY_SCAN_DIRS:
        base = root / directory
        for path in iter_files(base, SIMILARITY_SUFFIXES):
            relative = path.relative_to(root).as_posix()
            for digest in token_shingles(path, shingle_size):
                implementation_hashes[digest].add(relative)

    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    for reference_path in iter_files(reference_tree, SIMILARITY_SUFFIXES):
        relative_reference = reference_path.relative_to(reference_tree).as_posix()
        for digest in token_shingles(reference_path, shingle_size):
            for implementation_path in implementation_hashes.get(digest, ()):
                pair_counts[(implementation_path, relative_reference)] += 1

    return [
        f"{implementation_path}: {count} shared {shingle_size}-token shingles with "
        f"pinned reference path {reference_path}"
        for (implementation_path, reference_path), count in sorted(pair_counts.items())
        if count >= minimum_shared
    ]


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument(
        "--reference-tree",
        type=Path,
        help="isolated checkout of the pinned public reference, outside this repository",
    )
    argument_parser.add_argument(
        "--allow-unpinned-reference",
        action="store_true",
        help="allow a non-Git synthetic reference tree for local scanner verification",
    )
    return argument_parser


def report(section: str, findings: Sequence[str]) -> bool:
    if not findings:
        print(f"{section} passed.")
        return True
    print(f"{section} failed:", file=sys.stderr)
    for finding in findings:
        print(f"- {finding}", file=sys.stderr)
    return False


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    passed = report("Clean-room lexical gate", lexical_findings())
    passed = report("Clean-room provenance gate", governance_findings()) and passed
    if args.reference_tree is None:
        print("Clean-room similarity comparison not requested for this local validation.")
    else:
        passed = (
            report(
                "Clean-room similarity gate",
                similarity_findings(
                    args.reference_tree,
                    require_pinned_reference=not args.allow_unpinned_reference,
                ),
            )
            and passed
        )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
