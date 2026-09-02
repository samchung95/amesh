from __future__ import annotations

import json

import pytest
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

from amesh.api.contracts import CollectionQuery, collection_response
from amesh.api.models import CreateExecutionRequest


class Item(BaseModel):
    id: str
    rank: int
    group: str


class LabeledItem(Item):
    labels: dict[str, str]


def response_json(response) -> object:
    return json.loads(response.body)


def test_collection_query_filters_sorts_selects_and_pages() -> None:
    items = [
        Item(id="first", rank=1, group="a"),
        Item(id="second", rank=3, group="a"),
        Item(id="third", rank=2, group="b"),
    ]
    first = collection_response(
        items,
        CollectionQuery(limit=1, filters=["group=a"], sort="-rank", fields="id,rank"),
    )

    assert response_json(first) == [{"id": "second", "rank": 3}]
    assert first.headers["x-total-count"] == "2"
    cursor = first.headers["x-next-cursor"]

    second = collection_response(
        items,
        CollectionQuery(
            cursor=cursor,
            limit=1,
            filters=["group=a"],
            sort="-rank",
            fields="id,rank",
        ),
    )
    assert response_json(second) == [{"id": "first", "rank": 1}]
    assert "x-next-cursor" not in second.headers


def test_collection_query_rejects_invalid_cursor() -> None:
    with pytest.raises(HTTPException, match="invalid collection cursor"):
        collection_response([Item(id="one", rank=1, group="a")], CollectionQuery(cursor="bad"))


def test_nested_label_filter_uses_exact_key_and_value() -> None:
    response = collection_response(
        [
            LabeledItem(id="one", rank=1, group="a", labels={"team": "platform"}),
            LabeledItem(id="two", rank=2, group="a", labels={"team": "data"}),
        ],
        CollectionQuery(filters=["labels.team=platform"]),
    )

    assert response_json(response) == [
        {"id": "one", "rank": 1, "group": "a", "labels": {"team": "platform"}}
    ]


def test_create_execution_request_accepts_optional_exact_flow_revision() -> None:
    latest = CreateExecutionRequest.model_validate({"namespace": "tests", "flowId": "flow"})
    pinned = CreateExecutionRequest.model_validate(
        {"namespace": "tests", "flowId": "flow", "flowRevision": 3}
    )

    assert latest.flow_revision is None
    assert pinned.flow_revision == 3
    with pytest.raises(ValidationError):
        CreateExecutionRequest.model_validate(
            {"namespace": "tests", "flowId": "flow", "flowRevision": 0}
        )
