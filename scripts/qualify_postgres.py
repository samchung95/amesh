from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from amesh.config import Settings
from amesh.postgres_qualification import qualify_postgres


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Qualify an AMESH PostgreSQL backend")
    result.add_argument(
        "--profile",
        choices=("self-managed", "aws-rds", "azure-flex", "gcp-cloud-sql"),
        required=True,
    )
    result.add_argument("--output", type=Path)
    result.add_argument("--require-tls", action="store_true")
    result.add_argument("--max-p95-ms", type=float, default=50.0)
    return result


def main() -> int:
    arguments = parser().parse_args()
    report = asyncio.run(
        qualify_postgres(
            Settings(),
            profile=arguments.profile,
            require_tls=arguments.require_tls,
            max_p95_ms=arguments.max_p95_ms,
        )
    )
    encoded = json.dumps(report, indent=2, default=str, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
