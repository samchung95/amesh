#!/usr/bin/env python3
"""Validate that .env.example exactly documents the Settings environment surface."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from amesh.config import Settings

ROOT = Path(__file__).resolve().parents[1]
LOADER_CONTROL_NAMES = frozenset({"AMESH_CONFIG_FILES", "AMESH_SECRETS_DIR"})
_DECLARATION = re.compile(r"^\s*(?:#\s*)?([^=\s]+)=(.*)$")


class EnvironmentExampleError(ValueError):
    """Raised when the environment example drifts from Settings."""


def _declarations(path: Path) -> tuple[tuple[str, str], ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EnvironmentExampleError(f"cannot read environment example: {path}") from exc
    return tuple(
        (match.group(1), match.group(2))
        for line in lines
        if (match := _DECLARATION.fullmatch(line)) is not None
    )


def validate_environment_example(path: Path) -> None:
    declarations = _declarations(path)
    counts = Counter(name for name, _value in declarations)
    duplicates = sorted(name for name, count in counts.items() if count != 1)
    if duplicates:
        raise EnvironmentExampleError(
            "duplicate environment example setting(s): " + ", ".join(duplicates)
        )

    setting_names = {name.upper() for name in Settings.model_fields}
    expected_names = setting_names | LOADER_CONTROL_NAMES
    actual_names = set(counts)
    unknown = sorted(actual_names - expected_names)
    missing = sorted(expected_names - actual_names)
    errors: list[str] = []
    if unknown:
        errors.append("unknown setting(s): " + ", ".join(unknown))
    if missing:
        errors.append("missing setting(s): " + ", ".join(missing))
    if errors:
        raise EnvironmentExampleError("; ".join(errors))

    samples = {name: value for name, value in declarations if name in setting_names}
    try:
        with patch.dict(os.environ, samples, clear=True):
            Settings(_env_file=None)  # type: ignore[call-arg]  # Pydantic Settings control.
    except ValidationError as exc:
        fields = sorted(
            {
                str(error["loc"][0]) if error["loc"] else "configuration"
                for error in exc.errors(include_input=False)
            }
        )
        raise EnvironmentExampleError(
            "invalid environment example value(s) for: " + ", ".join(fields)
        ) from None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / ".env.example")
    arguments = parser.parse_args(argv)
    try:
        validate_environment_example(arguments.path)
    except EnvironmentExampleError as exc:
        print(f"environment example validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
