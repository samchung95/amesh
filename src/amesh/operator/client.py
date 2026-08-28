from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
import yaml

from amesh.operator.model import OperatorTarget, ResourceDescriptor


class AmeshApiError(RuntimeError):
    def __init__(self, method: str, path: str, status_code: int | None) -> None:
        self.method = method
        self.path = path
        self.status_code = status_code
        status = "transport failure" if status_code is None else f"HTTP {status_code}"
        super().__init__(f"AMESH {method} {path} failed: {status}")

    @property
    def transient(self) -> bool:
        return self.status_code is None or self.status_code == 429 or self.status_code >= 500


@dataclass(frozen=True, slots=True)
class ResourceIdentity:
    tenant: str
    namespace: str
    key: str
    server_id: str = ""
    revision: str = ""


@dataclass(frozen=True, slots=True)
class RemoteResource:
    document: object
    server_id: str = ""
    revision: str = ""


class AmeshApiClient:
    def __init__(
        self,
        *,
        timeout_seconds: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout_seconds,
            follow_redirects=False,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def read(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> RemoteResource | None:
        if descriptor.server_id_field and not identity.server_id:
            return None
        response = await self._request(
            descriptor=descriptor,
            target=target,
            token=token,
            method="GET",
            path=_render(descriptor.read_path, descriptor, identity),
        )
        if response.status_code == 404:
            return None
        self._raise_for_status(response)
        document: object
        body: object
        if descriptor.read_mode == "raw":
            document = response.text
            body = {}
        else:
            body = _json_body(response)
            if descriptor.read_mode == "collection":
                selected = _collection_item(descriptor, identity, body)
                if selected is None:
                    return None
                body = selected
            if descriptor.read_document_field:
                document = _mapping(body).get(descriptor.read_document_field)
            else:
                document = body
        mapped = _mapping(body) if isinstance(body, Mapping) else {}
        server_id = _string_field(mapped, descriptor.server_id_field) or identity.server_id
        revision = _string_field(mapped, descriptor.revision_field) or identity.revision
        if descriptor.revision_header:
            revision = response.headers.get(descriptor.revision_header, revision)
        return RemoteResource(
            document=without_server_defaults(document, descriptor.server_managed_defaults),
            server_id=server_id,
            revision=revision,
        )

    async def apply(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        desired: object,
        target: OperatorTarget,
        token: str,
        *,
        exists: bool,
        content_type: str | None = None,
    ) -> RemoteResource:
        method = descriptor.update_method if exists else descriptor.create_method
        path = descriptor.update_path if exists else descriptor.create_path
        response = await self._request(
            descriptor=descriptor,
            target=target,
            token=token,
            method=method,
            path=_render(path, descriptor, identity),
            desired=desired,
            content_type=content_type,
        )
        self._raise_for_status(response)
        body = _json_body(response) if response.content else {}
        mapped = _mapping(body) if isinstance(body, Mapping) else {}
        server_id = _string_field(mapped, descriptor.server_id_field) or identity.server_id
        revision = _string_field(mapped, descriptor.revision_field) or identity.revision
        return RemoteResource(document=desired, server_id=server_id, revision=revision)

    async def delete(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> None:
        if not descriptor.supports_delete:
            raise ValueError(f"{descriptor.kind} does not support deletion through the AMESH API")
        if "{server_id}" in descriptor.delete_path and not identity.server_id:
            raise ValueError(f"{descriptor.kind} deletion requires status.remoteId")
        if "{revision}" in descriptor.delete_path and not identity.revision:
            raise ValueError(f"{descriptor.kind} deletion requires status.remoteRevision")
        response = await self._request(
            descriptor=descriptor,
            target=target,
            token=token,
            method=descriptor.delete_method,
            path=_render(descriptor.delete_path, descriptor, identity),
        )
        if response.status_code == 404:
            return
        self._raise_for_status(response)

    async def _request(
        self,
        *,
        descriptor: ResourceDescriptor,
        target: OperatorTarget,
        token: str,
        method: str,
        path: str,
        desired: object | None = None,
        content_type: str | None = None,
    ) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Amesh-Tenant": target.tenant,
            "Accept": "application/json",
            "User-Agent": "amesh-kubernetes-operator/0.2.0",
        }
        request: dict[str, Any] = {"headers": headers}
        if desired is not None:
            if descriptor.payload_mode == "flow":
                request["content"] = yaml.safe_dump(desired, allow_unicode=True, sort_keys=False)
                headers["Content-Type"] = "application/yaml"
            elif descriptor.payload_mode == "file":
                if not isinstance(desired, str):
                    raise ValueError("AmeshFile spec.content must be a string")
                request["content"] = desired.encode()
                headers["Content-Type"] = content_type or "application/octet-stream"
            else:
                request["json"] = desired
                headers["Content-Type"] = "application/json"
        try:
            return await self._client.request(method, f"{target.endpoint}{path}", **request)
        except httpx.HTTPError as exc:
            raise AmeshApiError(method, path, None) from exc

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.is_success:
            return
        raise AmeshApiError(
            response.request.method, response.request.url.path, response.status_code
        )


def canonical_digest(value: object) -> str:
    normalized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(normalized.encode()).hexdigest()


def without_server_defaults(value: object, fields: tuple[str, ...]) -> object:
    selected = deepcopy(value)
    if isinstance(selected, dict):
        for field in fields:
            selected.pop(field, None)
    return selected


def _render(template: str, descriptor: ResourceDescriptor, identity: ResourceIdentity) -> str:
    key_safe = "/" if descriptor.payload_mode == "file" else ""
    return template.format(
        tenant=quote(identity.tenant, safe=""),
        namespace=quote(identity.namespace, safe=""),
        key=quote(identity.key, safe=key_safe),
        server_id=quote(identity.server_id, safe=""),
        revision=quote(identity.revision, safe=""),
    )


def _json_body(response: httpx.Response) -> object:
    try:
        return response.json()
    except ValueError as exc:
        raise AmeshApiError(response.request.method, response.request.url.path, 502) from exc


def _collection_item(
    descriptor: ResourceDescriptor,
    identity: ResourceIdentity,
    value: object,
) -> dict[str, object] | None:
    items: object = value
    if isinstance(value, dict):
        items = value.get(descriptor.read_collection_field or "items", value)
    if not isinstance(items, list):
        raise ValueError(f"{descriptor.kind} collection response is not a list")
    expected = identity.server_id if descriptor.read_match_field == "id" else identity.key
    for item in items:
        if isinstance(item, dict) and str(item.get(descriptor.read_match_field, "")) == expected:
            return dict(item)
    return None


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("AMESH API response must be an object")
    return {str(key): item for key, item in value.items()}


def _string_field(value: Mapping[str, object], field: str) -> str:
    if not field:
        return ""
    selected = value.get(field)
    return "" if selected is None else str(selected)
