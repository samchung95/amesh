from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

from amesh.api.contracts import CollectionQuery
from amesh.api.routers.executions import _flow_equality_filter, list_executions
from amesh.domain import ActorContext, ExecutionState, PrincipalType
from amesh.dsl import FlowDefinition
from amesh.ports import PersistedExecution

_NOW = datetime(2026, 9, 27, 9, 0, tzinfo=UTC)


def _execution(namespace: str, flow_id: str, revision: int, minutes: int) -> PersistedExecution:
    return PersistedExecution(
        execution_id=uuid4(),
        tenant_id="default",
        state=ExecutionState.SUCCESS,
        epoch=1,
        version=1,
        namespace=namespace,
        flow_id=flow_id,
        flow_revision=revision,
        created_at=_NOW + timedelta(minutes=minutes),
        updated_at=_NOW + timedelta(minutes=minutes),
    )


class _Repository:
    def __init__(self, executions: list[PersistedExecution]) -> None:
        self.executions = executions
        self.list_calls: list[dict[str, Any]] = []
        self.flow_calls: list[tuple[str, str, int]] = []

    async def list_executions(self, **kwargs: Any) -> list[PersistedExecution]:
        self.list_calls.append(kwargs)
        return self.executions

    async def get_flow(
        self, namespace: str, flow_id: str, *, tenant_id: str, revision: int
    ) -> FlowDefinition:
        del tenant_id
        self.flow_calls.append((namespace, flow_id, revision))
        return FlowDefinition.model_validate(
            {"id": flow_id, "namespace": namespace, "tasks": [{"id": "t", "type": "core.return"}]}
        )


class _AllowAll:
    async def require(self, request: object) -> object:
        del request
        return object()


def _list(repository: _Repository, query: CollectionQuery) -> list[dict[str, Any]]:
    response = asyncio.run(
        list_executions(
            repository=cast(Any, repository),
            actor=ActorContext(
                principal_id=uuid4(), principal_type=PrincipalType.USER, display="u"
            ),
            authorization_service=cast(Any, _AllowAll()),
            tenant_id="default",
            query=query,
        )
    )
    return cast(list[dict[str, Any]], json.loads(bytes(response.body)))


def test_flow_equality_filter_needs_both_namespace_and_flow_id() -> None:
    assert _flow_equality_filter(["namespace=team.data", "flow_id=daily"]) == (
        "team.data",
        "daily",
    )
    assert _flow_equality_filter(["flow_id=daily", "namespace=a", "namespace=b"]) == ("a", "daily")
    assert _flow_equality_filter(["namespace=team.data"]) is None
    assert _flow_equality_filter(["state=SUCCESS", "flow_id=daily"]) is None
    assert _flow_equality_filter([]) is None


def test_flow_filters_are_pushed_to_the_repository_and_flows_are_loaded_once() -> None:
    repository = _Repository(
        [_execution("team.data", "daily", 7, minute) for minute in range(5)]
        + [_execution("team.data", "daily", 6, -1)]
    )

    page = _list(
        repository,
        CollectionQuery(
            filters=["namespace=team.data", "flow_id=daily"], limit=1, sort="-updated_at"
        ),
    )

    assert repository.list_calls == [
        {"tenant_id": "default", "limit": 1000, "namespace": "team.data", "flow_id": "daily"}
    ]
    assert sorted(repository.flow_calls) == [("team.data", "daily", 6), ("team.data", "daily", 7)]
    assert len(page) == 1
    assert page[0]["updated_at"].startswith("2026-09-27T09:04:00")


def test_unfiltered_listing_keeps_the_tenant_wide_query() -> None:
    repository = _Repository([_execution("team.data", "daily", 1, 0)])

    page = _list(repository, CollectionQuery(filters=["namespace=team.data"], limit=10))

    assert repository.list_calls == [
        {"tenant_id": "default", "limit": 1000, "namespace": None, "flow_id": None}
    ]
    assert [item["flow_id"] for item in page] == ["daily"]
