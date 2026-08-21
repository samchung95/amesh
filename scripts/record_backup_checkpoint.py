from __future__ import annotations

import argparse
import asyncio

from amesh.adapters.postgres import PostgresOperationsRepository
from amesh.config import Settings
from amesh.database import create_database_engine


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Record a PostgreSQL LSN against a completed object manifest"
    )
    result.add_argument("--manifest-uri", required=True)
    result.add_argument("--manifest-sha256", required=True)
    result.add_argument("--actor", required=True)
    return result


async def record(arguments: argparse.Namespace) -> str:
    engine = create_database_engine(Settings())
    try:
        checkpoint = await PostgresOperationsRepository(engine).record_backup_checkpoint(
            arguments.manifest_uri,
            arguments.manifest_sha256,
            created_by=arguments.actor,
        )
        return checkpoint.model_dump_json()
    finally:
        await engine.dispose()


def main() -> int:
    arguments = parser().parse_args()
    print(asyncio.run(record(arguments)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
