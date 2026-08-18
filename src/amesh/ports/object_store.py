from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class ObjectMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    uri: str
    tenant_id: str
    size: int = Field(ge=0)
    checksum_sha256: str
    content_type: str | None = None


class ObjectStore(Protocol):
    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata: ...

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]: ...

    async def delete(self, tenant_id: str, uri: str) -> None: ...
