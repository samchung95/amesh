from __future__ import annotations

import ssl
from typing import Any

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from amesh.config import Settings


def create_database_engine(
    settings: Settings,
    *,
    read_replica: bool = False,
) -> AsyncEngine:
    """Create one bounded async PostgreSQL engine for a process role."""

    database_url = (
        settings.database_read_replica_url
        if read_replica and settings.database_read_replica_url is not None
        else settings.database_url
    )
    url = _with_statement_cache(database_url, settings.database_prepared_statement_cache_size)
    connect_args: dict[str, Any] = {}
    connect_args["ssl"] = database_ssl_argument(settings)
    return create_async_engine(
        url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout_seconds,
        pool_recycle=settings.database_pool_recycle_seconds,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def _with_statement_cache(database_url: str, cache_size: int) -> URL:
    url = make_url(database_url)
    return url.update_query_dict({"prepared_statement_cache_size": str(cache_size)})


def database_ssl_argument(settings: Settings) -> ssl.SSLContext | bool:
    if settings.database_tls_mode == "disable":
        return False
    if settings.database_tls_mode == "require":
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    return ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile=settings.database_tls_ca_file,
    )
