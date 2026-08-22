from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, TypeVar

T = TypeVar("T")
PageLoader = Callable[[str | None], dict[str, Any]]


def iterate_pages(load: PageLoader) -> Iterator[Any]:
    cursor: str | None = None
    while True:
        page = load(cursor)
        yield from page.get("items", [])
        cursor = page.get("nextCursor")
        if not cursor:
            return
