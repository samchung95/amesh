"""Small async SDK surface for the versioned differential REST contract."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from .differential import ComparisonReport, DifferentialSpec


class DifferentialClient:
    """Tenant-bound client; every write carries the spec idempotency key."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        tenant_id: str,
    ) -> None:
        self._client = client
        self._tenant_id = tenant_id

    async def run(self, spec: DifferentialSpec) -> ComparisonReport:
        if spec.tenant_id != self._tenant_id:
            raise ValueError("differential spec tenant does not match client tenant")
        response = await self._client.post(
            f"/api/v1/namespaces/{quote(spec.namespace, safe='')}/differentials",
            headers={
                "X-Amesh-Tenant": self._tenant_id,
                "Idempotency-Key": spec.idempotency_key,
            },
            json=spec.model_dump(mode="json", by_alias=True),
        )
        response.raise_for_status()
        return ComparisonReport.model_validate(response.json())

    async def get(self, namespace: str, idempotency_key: str) -> ComparisonReport:
        response = await self._client.get(
            f"/api/v1/namespaces/{quote(namespace, safe='')}/differentials/"
            f"{quote(idempotency_key, safe='')}",
            headers={"X-Amesh-Tenant": self._tenant_id},
        )
        response.raise_for_status()
        return ComparisonReport.model_validate(response.json())


def client_error_payload(response: httpx.Response) -> Any:
    """Return a JSON error payload without hiding transport errors."""

    try:
        return response.json()
    except ValueError:
        return response.text
