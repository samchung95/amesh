from __future__ import annotations

import asyncio
import os
import sys
from datetime import timedelta

from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresDurableTransport


async def claim_record_and_exit(database_url: str, lane: str) -> int:
    engine = create_async_engine(database_url)
    transport = PostgresDurableTransport(engine)
    claims = await transport.claim(
        lane,
        "crashing-worker",
        limit=1,
        lease_duration=timedelta(milliseconds=100),
    )
    if len(claims) != 1:
        return 2
    was_first_delivery = await transport.record_consumed("executor", claims[0].envelope)
    if not was_first_delivery:
        return 3
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(claim_record_and_exit(sys.argv[1], sys.argv[2]))
    os._exit(exit_code)
