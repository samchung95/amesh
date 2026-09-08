from __future__ import annotations

import ssl
from typing import Any

from amesh import database
from amesh.config import Settings


def test_database_engine_applies_pool_cache_and_replica_settings(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}
    expected = object()

    def capture(url: object, **kwargs: object) -> object:
        captured["url"] = url
        captured.update(kwargs)
        return expected

    monkeypatch.setattr(database, "create_async_engine", capture)
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://primary/amesh",
        database_read_replica_url="postgresql+asyncpg://replica/amesh",
        database_pool_size=7,
        database_max_overflow=3,
        database_pool_timeout_seconds=4,
        database_pool_recycle_seconds=300,
        database_prepared_statement_cache_size=250,
        database_tls_mode="verify-full",
    )

    result = database.create_database_engine(settings, read_replica=True)

    assert result is expected
    assert str(captured["url"]) == (
        "postgresql+asyncpg://replica/amesh?prepared_statement_cache_size=250"
    )
    assert captured["pool_size"] == 7
    assert captured["max_overflow"] == 3
    assert captured["pool_timeout"] == 4
    assert captured["pool_recycle"] == 300
    assert captured["pool_pre_ping"] is True
    context = captured["connect_args"]["ssl"]
    assert isinstance(context, ssl.SSLContext)
    assert context.check_hostname
    assert context.verify_mode is ssl.CERT_REQUIRED


def test_database_tls_require_encrypts_without_certificate_verification(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def capture(url: object, **kwargs: object) -> object:
        del url
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(database, "create_async_engine", capture)
    settings = Settings(_env_file=None, database_tls_mode="require")

    database.create_database_engine(settings)

    context = captured["connect_args"]["ssl"]
    assert isinstance(context, ssl.SSLContext)
    assert not context.check_hostname
    assert context.verify_mode is ssl.CERT_NONE


def test_database_tls_disable_is_explicit(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def capture(url: object, **kwargs: object) -> object:
        del url
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(database, "create_async_engine", capture)

    database.create_database_engine(Settings(_env_file=None))

    assert captured["connect_args"] == {"ssl": False}
