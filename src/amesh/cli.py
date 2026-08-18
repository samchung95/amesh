from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from amesh import __version__
from amesh.dsl import FlowDocumentError, validate_flow_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="amesh")
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    validate = subcommands.add_parser("validate", help="Validate a flow YAML or JSON file")
    validate.add_argument("path", type=Path)
    validate.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        path: Path = args.path
        try:
            result = validate_flow_document(path.read_bytes())
        except (OSError, FlowDocumentError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if args.as_json:
            print(result.model_dump_json(indent=2))
        elif result.valid:
            print(f"valid: {path} ({result.semantic_hash})")
        else:
            for issue in result.issues:
                print(f"{issue.severity}: {issue.path}: {issue.code}: {issue.message}")
        return 0 if result.valid else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
