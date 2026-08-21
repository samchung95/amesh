from __future__ import annotations

from urllib.parse import urlsplit


def tenant_object_key(tenant_id: str, key: str) -> str:
    normalized = key.strip("/")
    if not tenant_id or "/" in tenant_id or tenant_id in {".", ".."}:
        raise ValueError("tenant ID must be a non-empty path segment")
    if not normalized or any(segment in {"", ".", ".."} for segment in normalized.split("/")):
        raise ValueError("object key must be a non-empty normalized relative path")
    return f"tenants/{tenant_id}/{normalized}"


def parse_tenant_uri(
    tenant_id: str,
    uri: str,
    *,
    scheme: str,
    container: str,
) -> str:
    parsed = urlsplit(uri)
    key = parsed.path.lstrip("/")
    prefix = f"tenants/{tenant_id}/"
    if (
        parsed.scheme != scheme
        or parsed.netloc != container
        or not key.startswith(prefix)
        or any(segment in {"", ".", ".."} for segment in key.split("/"))
    ):
        raise ValueError("object URI is outside the tenant storage prefix")
    return key


def relative_tenant_key(tenant_id: str, object_key: str) -> str:
    prefix = f"tenants/{tenant_id}/"
    if not object_key.startswith(prefix):
        raise ValueError("object key is outside the tenant storage prefix")
    return object_key.removeprefix(prefix)
