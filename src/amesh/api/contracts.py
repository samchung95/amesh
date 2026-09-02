from __future__ import annotations

import base64
import json
from collections.abc import Mapping, Sequence
from typing import Annotated, Any

from fastapi import HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse


class CollectionQuery:
    def __init__(
        self,
        cursor: Annotated[
            str | None, Query(description="Opaque cursor from the prior page")
        ] = None,
        limit: Annotated[int | None, Query(ge=1, le=1000)] = None,
        filters: Annotated[
            list[str] | None,
            Query(
                alias="filter",
                description="Repeatable top-level equality filter in field=value form",
            ),
        ] = None,
        sort: Annotated[
            str | None,
            Query(description="Comma-separated top-level fields; prefix descending fields with -"),
        ] = None,
        fields: Annotated[
            str | None,
            Query(description="Comma-separated top-level response fields"),
        ] = None,
    ) -> None:
        self.cursor = cursor
        self.limit = limit
        self.filters = filters or []
        self.sort = sort
        self.fields = fields


def default_limited_collection_query(
    cursor: Annotated[str | None, Query(description="Opaque cursor from the prior page")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    filters: Annotated[
        list[str] | None,
        Query(
            alias="filter",
            description="Repeatable top-level equality filter in field=value form",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Query(description="Comma-separated top-level fields; prefix descending fields with -"),
    ] = None,
    fields: Annotated[
        str | None,
        Query(description="Comma-separated top-level response fields"),
    ] = None,
) -> CollectionQuery:
    return CollectionQuery(
        cursor=cursor,
        limit=limit,
        filters=filters,
        sort=sort,
        fields=fields,
    )


def collection_response(
    items: Sequence[BaseModel],
    query: CollectionQuery,
    *,
    default_limit: int | None = None,
) -> JSONResponse:
    encoded = jsonable_encoder(items)
    if not isinstance(encoded, list) or any(not isinstance(item, dict) for item in encoded):
        raise TypeError("collection items must encode as JSON objects")
    values: list[dict[str, Any]] = encoded
    values = _filter_values(values, query.filters)
    values = _sort_values(values, query.sort)

    offset = _decode_cursor(query.cursor)
    if offset > len(values):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cursor is outside the current result set",
        )
    limit = query.limit if query.limit is not None else default_limit
    page = values[offset:] if limit is None else values[offset : offset + limit]
    next_offset = offset + len(page)

    selected_fields = _parse_csv(query.fields)
    if selected_fields:
        available = set().union(*(item.keys() for item in values)) if values else set()
        unknown = selected_fields - available
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"unknown fields: {', '.join(sorted(unknown))}",
            )
        page = [
            {key: value for key, value in item.items() if key in selected_fields} for item in page
        ]

    headers = {"X-Total-Count": str(len(values))}
    if next_offset < len(values):
        headers["X-Next-Cursor"] = _encode_cursor(next_offset)
    return JSONResponse(content=page, headers=headers)


def _filter_values(
    values: list[dict[str, Any]],
    filters: Sequence[str],
) -> list[dict[str, Any]]:
    result = values
    for expression in filters:
        field, separator, expected = expression.partition("=")
        if not separator or not field:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="filters must use field=value syntax",
            )
        if result and _nested_value(result[0], field) is _MISSING:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"unknown filter field: {field}",
            )
        result = [item for item in result if _filter_text(_nested_value(item, field)) == expected]
    return result


_MISSING = object()


def _nested_value(item: Mapping[str, Any], field: str) -> Any:
    value: Any = item
    for part in field.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return _MISSING
        value = value[part]
    return value


def _sort_values(values: list[dict[str, Any]], sort: str | None) -> list[dict[str, Any]]:
    fields = [item for item in (sort or "").split(",") if item]
    result = list(values)
    for expression in reversed(fields):
        descending = expression.startswith("-")
        field = expression[1:] if descending else expression
        if not field or (result and field not in result[0]):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"unknown sort field: {field}",
            )
        result.sort(
            key=lambda item: (item.get(field) is None, _filter_text(item.get(field))),
            reverse=descending,
        )
    return result


def _parse_csv(value: str | None) -> set[str]:
    return {item.strip() for item in (value or "").split(",") if item.strip()}


def _filter_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _encode_cursor(offset: int) -> str:
    payload = json.dumps({"offset": offset, "version": 1}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_cursor(cursor: str | None) -> int:
    if cursor is None:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        if payload.get("version") != 1 or not isinstance(payload.get("offset"), int):
            raise ValueError
        offset = int(payload["offset"])
        if offset < 0:
            raise ValueError
        return offset
    except (UnicodeDecodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid collection cursor",
        ) from exc
