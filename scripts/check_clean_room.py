#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("src", "tests", "migrations", "examples")
FORBIDDEN = {
    r"\bio\.kestra\b": "Kestra Java package name in implementation code",
    r"\bkestra-io/kestra\b": "upstream repository path in implementation code",
    r"\bKestraException\b": "upstream-specific class name",
    r"\bAbstractTask\b": "upstream-specific class pattern",
}
ALLOWED_SUFFIXES = {".py", ".sql", ".yaml", ".yml", ".json", ".toml"}


def main() -> int:
    findings: list[str] = []
    for directory in SCAN_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in ALLOWED_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern, reason in FORBIDDEN.items():
                if re.search(pattern, text, re.IGNORECASE):
                    findings.append(f"{path.relative_to(ROOT)}: {reason}: /{pattern}/")

    if findings:
        print("Clean-room lexical gate failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("Clean-room lexical gate passed for implementation directories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
