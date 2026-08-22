from __future__ import annotations

import json

import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from amesh.api.contracts import CollectionQuery, collection_response


class Item(BaseModel):
    id: str
    rank: int
    group: str


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
