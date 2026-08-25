from __future__ import annotations

import httpx
from pydantic import SecretStr

from amesh.networking import outbound_http_client
from amesh.ports.agent_primitives import (
    ModelProviderRequest,
    ModelProviderResponse,
)
from amesh.tasks.http import HttpTaskPolicy, validate_http_destination


class OpenAICompatibleModelProvider:
    """OpenAI-compatible HTTP edge behind the provider-neutral model port."""

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        *,
        http_policy: HttpTaskPolicy | None = None,
    ) -> None:
        self._client = client
        self._http_policy = http_policy or HttpTaskPolicy()

    async def invoke(
        self,
        request: ModelProviderRequest,
        credential: SecretStr,
    ) -> ModelProviderResponse:
        validate_http_destination(
            request.endpoint,
            self._http_policy,
            resolve_dns=self._client is None,
        )

        async def post(active_client: httpx.AsyncClient) -> ModelProviderResponse:
            response = await active_client.post(
                request.endpoint,
                headers={
                    "Authorization": f"Bearer {credential.get_secret_value()}",
                    "Content-Type": "application/json",
                },
                json=request.payload,
                timeout=request.timeout_seconds,
            )
            response.raise_for_status()
            if len(response.content) > self._http_policy.maximum_response_bytes:
                raise ValueError("model response exceeds the configured payload limit")
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError("model provider response must be a JSON object")
            return ModelProviderResponse(payload=payload)

        if self._client is not None:
            return await post(self._client)
        async with outbound_http_client(
            request.endpoint,
            http_proxy_url=self._http_policy.http_proxy_url,
            https_proxy_url=self._http_policy.https_proxy_url,
            no_proxy=self._http_policy.no_proxy,
            ca_file=self._http_policy.ca_file,
            client_certificate_file=self._http_policy.client_certificate_file,
            client_key_file=self._http_policy.client_key_file,
        ) as active_client:
            return await post(active_client)
