from __future__ import annotations

from typing import Protocol

from amesh.domain.search import (
    SearchDocumentType,
    SearchProjectionStatus,
    SearchRequest,
    SearchResponse,
)


class SearchUnavailableError(RuntimeError):
    """Raised when the optional search projection cannot serve a query."""


class SearchCursorError(ValueError):
    """Raised when an opaque search cursor is invalid for the current request."""


class SearchRepository(Protocol):
    async def search(
        self,
        request: SearchRequest,
        *,
        tenant_id: str,
        authorized_types: tuple[SearchDocumentType, ...],
        denied_types: tuple[SearchDocumentType, ...] = (),
    ) -> SearchResponse: ...

    async def status(self, *, tenant_id: str) -> SearchProjectionStatus: ...

    async def request_rebuild(
        self,
        *,
        tenant_id: str,
        actor_id: str,
        reason: str,
    ) -> SearchProjectionStatus: ...


class SearchProjector(Protocol):
    async def project_once(self, *, tenant_id: str, limit: int = 500) -> int: ...

    async def record_failure(self, *, tenant_id: str, error: str) -> None: ...
