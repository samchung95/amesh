from __future__ import annotations

import argparse
import asyncio
from datetime import datetime

from amesh.adapters.postgres import PostgresDurableTransport
from amesh.config import Settings
from amesh.database import create_database_engine


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Purge terminal AMESH transport records")
    result.add_argument("--tenant", required=True)
    result.add_argument("--before", type=datetime.fromisoformat, required=True)
    result.add_argument("--limit", type=int, default=1_000)
    return result


async def purge(arguments: argparse.Namespace) -> str:
    engine = create_database_engine(Settings())
    try:
        result = await PostgresDurableTransport(engine).purge_terminal(
            tenant_id=arguments.tenant,
            before=arguments.before,
            limit=arguments.limit,
        )
        return result.model_dump_json()
    finally:
        await engine.dispose()


def main() -> int:
    arguments = parser().parse_args()
    print(asyncio.run(purge(arguments)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
