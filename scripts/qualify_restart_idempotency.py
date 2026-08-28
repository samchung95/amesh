from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from amesh.restart_qualification import (
    DEFAULT_MAX_INLINE_BYTES,
    DEFAULT_PAYLOAD_BYTES,
    qualify_restart_idempotency,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Run the isolated PostgreSQL/local-blob restart qualification"
    )
    result.add_argument(
        "--database-url",
        default=os.getenv("AMESH_TEST_DATABASE_URL"),
        help=(
            "admin PostgreSQL URL used only to create an amesh_test_* database "
            "(default: AMESH_TEST_DATABASE_URL)"
        ),
    )
    result.add_argument("--output", type=Path, help="write the JSON report to this path")
    result.add_argument("--payload-bytes", type=int, default=DEFAULT_PAYLOAD_BYTES)
    result.add_argument("--max-inline-bytes", type=int, default=DEFAULT_MAX_INLINE_BYTES)
    result.add_argument(
        "--object-store-root",
        type=Path,
        help="retain local blobs at this path; otherwise use a cleaned temporary directory",
    )
    return result


def main() -> int:
    arguments = parser().parse_args()
    if not arguments.database_url:
        raise SystemExit(
            "--database-url or AMESH_TEST_DATABASE_URL is required; "
            "the URL must point to a PostgreSQL server, not a shared application database"
        )
    report = asyncio.run(
        qualify_restart_idempotency(
            arguments.database_url,
            payload_bytes=arguments.payload_bytes,
            max_inline_bytes=arguments.max_inline_bytes,
            object_store_root=arguments.object_store_root,
        )
    )
    encoded = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
