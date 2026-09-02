from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any
from uuid import uuid4

import pytest

from amesh.executor.service import _abandon_cache_population
from amesh.ports import TaskCacheDecision, TaskCacheKey, TaskCacheLookup


def _cache_key() -> TaskCacheKey:
    return TaskCacheKey(
        key_hash="a" * 64,
        key_prefix="tests/cache/result",
        cache_namespace="tests",
        scope="TASK",
        namespace="tests",
        flow_id="flow",
        flow_revision=1,
        task_id="result",
        task_type="test.cached",
        security_context_hash="b" * 64,
        invalidation_policy="TTL",
        ttl=timedelta(hours=1),
    )


def test_cache_abandonment_failure_is_logged_and_raised(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class FailingCache:
        async def abandon(self, *_args: Any, **_kwargs: Any) -> bool:
            raise RuntimeError("cache store unavailable")

    lookup = TaskCacheLookup(
        decision=TaskCacheDecision.MISS,
        reason="reserved",
        key_hash="a" * 64,
        owner_token=uuid4(),
    )
    with caplog.at_level("ERROR"), pytest.raises(RuntimeError, match="cache store unavailable"):
        asyncio.run(
            _abandon_cache_population(
                FailingCache(),
                _cache_key(),
                lookup,
                tenant_id="default",
                execution_id=uuid4(),
                task_run_id=uuid4(),
                attempt=1,
                reason="task failed",
            )
        )

    assert "task result cache abandonment failed" in caplog.text
