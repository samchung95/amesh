from __future__ import annotations

import asyncio

import pytest

import amesh.recovery as recovery_module
from amesh.config import Settings


def test_restored_database_cleanup_preserves_primary_and_attempts_both_teardowns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingEngine:
        async def dispose(self) -> None:
            raise RuntimeError("dispose failed")

    dropped: list[str] = []

    async def failing_drop(
        _database_url: str,
        database_name: str,
        **_kwargs: object,
    ) -> None:
        dropped.append(database_name)
        raise RuntimeError("drop failed")

    monkeypatch.setattr(recovery_module, "drop_ephemeral_database", failing_drop)
    gaps = ["RuntimeError: primary recovery failure"]
    settings = Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://amesh:amesh@localhost/amesh",
    )

    asyncio.run(
        recovery_module._cleanup_restored_database(
            settings,
            FailingEngine(),  # type: ignore[arg-type]
            "amesh_restore",
            gaps,
        )
    )

    assert dropped == ["amesh_restore"]
    assert gaps[0] == "RuntimeError: primary recovery failure"
    assert any("restored engine disposal failed" in gap for gap in gaps)
    assert any("restored database cleanup failed" in gap for gap in gaps)
