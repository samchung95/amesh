from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urljoin

import httpx

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskHandler
from amesh.networking import HttpTaskPolicy as HttpTaskPolicy
from amesh.networking import outbound_http_client
from amesh.networking import validate_http_destination as validate_http_destination
from amesh.workflow.working_directory import WorkingDirectoryManager

_REDIRECT_CODES = frozenset({301, 302, 303, 307, 308})


def core_http_handler(
    client: httpx.AsyncClient | None = None,
    *,
    policy: HttpTaskPolicy | None = None,
) -> TaskHandler:
    active_policy = policy or HttpTaskPolicy()

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        extra = task.configuration.handler_view().mutable_copy()
        url = _required_string(extra, "url", task.id)
        method = str(extra.get("method", "GET")).upper()
        headers, query = _request_credentials(extra)
        body = extra.get("body")
        timeout = task.timeout_seconds or 30
        response_limit = _bounded_positive_integer(
            extra.get("maxResponseBytes"),
            default=min(1_048_576, active_policy.maximum_response_bytes),
            maximum=active_policy.maximum_response_bytes,
            field="maxResponseBytes",
        )
        pagination = extra.get("pagination")
        if pagination is not None and not isinstance(pagination, dict):
            raise ValueError(f"task {task.id!r} pagination must be an object")

        page_url: str | None = url
        pages: list[dict[str, Any]] = []
        items: list[Any] = []
        max_pages = _bounded_positive_integer(
            pagination.get("maxPages") if pagination else None,
            default=1 if pagination is None else min(10, active_policy.maximum_pages),
            maximum=active_policy.maximum_pages,
            field="pagination.maxPages",
        )
        while page_url is not None and len(pages) < max_pages:
            response = await _request(
                client,
                method=method,
                url=page_url,
                headers=headers,
                query=query,
                body=body,
                timeout=timeout,
                response_limit=response_limit,
                policy=active_policy,
                resolve_dns=client is None,
            )
            pages.append(response)
            if pagination is None:
                break
            payload = response.get("json")
            if not isinstance(payload, (dict, list)):
                raise ValueError("paginated HTTP responses must contain JSON")
            items_path = pagination.get("itemsPath")
            if items_path is not None:
                selected = _json_path(payload, str(items_path))
                if not isinstance(selected, list):
                    raise ValueError("pagination itemsPath must select a JSON array")
                items.extend(selected)
            next_path = pagination.get("nextUrlPath")
            if not isinstance(next_path, str) or not next_path:
                raise ValueError("pagination requires nextUrlPath")
            next_value = _json_path(payload, next_path)
            page_url = urljoin(page_url, next_value) if isinstance(next_value, str) else None
            method = "GET"
            body = None
            query = {}
        if page_url is not None and pagination is not None and len(pages) >= max_pages:
            raise ValueError("HTTP pagination exceeded its configured page limit")
        if pagination is None:
            return pages[0]
        return {"pages": pages, "items": items, "pageCount": len(pages)}

    return run


def core_download_handler(
    workspace_manager: WorkingDirectoryManager,
    client: httpx.AsyncClient | None = None,
    *,
    policy: HttpTaskPolicy | None = None,
) -> TaskHandler:
    active_policy = policy or HttpTaskPolicy()

    async def run(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        extra = task.configuration.handler_view().mutable_copy()
        url = _required_string(extra, "url", task.id)
        destination = _required_string(extra, "destination", task.id)
        headers, query = _request_credentials(extra)
        response_limit = _bounded_positive_integer(
            extra.get("maxResponseBytes"),
            default=active_policy.maximum_response_bytes,
            maximum=active_policy.maximum_response_bytes,
            field="maxResponseBytes",
        )
        quota = context.workspace_quota_bytes or task.workspace_quota_bytes
        workspace = await workspace_manager.prepare(
            tenant_id=context.tenant_id,
            execution_id=str(context.execution_id),
            task_run_id=str(context.task_run_id),
            attempt_id=str(context.attempt_id),
            scope_id=context.workspace_scope_id,
            input_files=context.files,
            file_references=context.file_references,
            quota_bytes=quota,
        )
        try:
            response = await _request(
                client,
                method="GET",
                url=url,
                headers=headers,
                query=query,
                body=None,
                timeout=task.timeout_seconds or 30,
                response_limit=response_limit,
                policy=active_policy,
                resolve_dns=client is None,
                encode_body=True,
            )
            target = _safe_target(workspace.path, destination)
            await asyncio.to_thread(target.parent.mkdir, parents=True, exist_ok=True)
            content = base64.b64decode(str(response.pop("bodyBase64")), validate=True)
            await asyncio.to_thread(target.write_bytes, content)
            collected = await workspace_manager.collect(
                workspace,
                tenant_id=context.tenant_id,
                execution_id=str(context.execution_id),
                task_run_id=str(context.task_run_id),
                attempt=context.attempt,
                patterns=task.output_files,
                manifest_path=task.output_manifest,
                quota_bytes=quota,
            )
            return TaskCompletion(
                output={
                    **response,
                    "path": destination,
                    "sizeBytes": len(content),
                    "outputFiles": dict(collected.output_files),
                },
                artifacts=collected.artifacts,
            )
        finally:
            if not workspace.shared:
                await asyncio.to_thread(workspace_manager.cleanup, workspace.path)

    return run


async def _request(
    client: httpx.AsyncClient | None,
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    query: dict[str, str],
    body: object,
    timeout: float,
    response_limit: int,
    policy: HttpTaskPolicy,
    resolve_dns: bool,
    encode_body: bool = False,
) -> dict[str, Any]:
    current = url
    current_method = method
    current_body = body
    for redirect_count in range(policy.maximum_redirects + 1):
        validate_http_destination(current, policy, resolve_dns=resolve_dns)
        active_client = client or outbound_http_client(
            current,
            http_proxy_url=policy.http_proxy_url,
            https_proxy_url=policy.https_proxy_url,
            no_proxy=policy.no_proxy,
            ca_file=policy.ca_file,
            client_certificate_file=policy.client_certificate_file,
            client_key_file=policy.client_key_file,
        )
        try:
            async with active_client.stream(
                current_method,
                current,
                headers=headers,
                params=query or None,
                json=current_body,
                timeout=timeout,
                follow_redirects=False,
            ) as response:
                if response.status_code in _REDIRECT_CODES and response.headers.get("location"):
                    if redirect_count >= policy.maximum_redirects:
                        raise ValueError("HTTP request exceeded its redirect limit")
                    current = urljoin(str(response.url), response.headers["location"])
                    if response.status_code == 303:
                        current_method = "GET"
                        current_body = None
                    continue
                response.raise_for_status()
                declared_length = response.headers.get("content-length")
                if declared_length is not None and int(declared_length) > response_limit:
                    raise ValueError("HTTP response exceeds the configured payload limit")
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > response_limit:
                        raise ValueError("HTTP response exceeds the configured payload limit")
                result: dict[str, Any] = {
                    "statusCode": response.status_code,
                    "headers": dict(response.headers),
                }
                if encode_body:
                    result["bodyBase64"] = base64.b64encode(content).decode("ascii")
                    return result
                text = bytes(content).decode(response.encoding or "utf-8", errors="replace")
                result["body"] = text
                if response.headers.get("content-type", "").split(";", 1)[0] == "application/json":
                    result["json"] = json.loads(text)
                return result
        finally:
            if client is None:
                await active_client.aclose()
    raise RuntimeError("unreachable redirect state")


def _request_credentials(extra: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    raw_headers = extra.get("headers", {})
    if not isinstance(raw_headers, dict):
        raise ValueError("HTTP headers must be an object")
    headers = {str(key): str(value) for key, value in raw_headers.items()}
    raw_query = extra.get("query", {})
    if not isinstance(raw_query, dict):
        raise ValueError("HTTP query must be an object")
    query = {str(key): str(value) for key, value in raw_query.items()}
    auth = extra.get("auth")
    if auth is None:
        return headers, query
    if not isinstance(auth, dict):
        raise ValueError("HTTP auth must be an object")
    auth_type = auth.get("type")
    if auth_type == "bearer":
        headers["Authorization"] = f"Bearer {_required_string(auth, 'token', 'auth')}"
    elif auth_type == "basic":
        username = _required_string(auth, "username", "auth")
        password = _required_string(auth, "password", "auth")
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    elif auth_type == "apiKey":
        name = _required_string(auth, "name", "auth")
        value = _required_string(auth, "value", "auth")
        location = auth.get("in", "header")
        if location == "header":
            headers[name] = value
        elif location == "query":
            query[name] = value
        else:
            raise ValueError("HTTP apiKey auth location must be header or query")
    else:
        raise ValueError("HTTP auth type must be bearer, basic or apiKey")
    return headers, query


def _json_path(value: object, path: str) -> object:
    selected = value
    for part in path.split(".") if path else ():
        if isinstance(selected, dict):
            selected = selected.get(part)
        else:
            return None
    return selected


def _required_string(value: dict[str, Any], field: str, owner: str) -> str:
    selected = value.get(field)
    if not isinstance(selected, str) or not selected:
        raise ValueError(f"{owner!r} requires {field}")
    return selected


def _bounded_positive_integer(
    value: object,
    *,
    default: int,
    maximum: int,
    field: str,
) -> int:
    selected = default if value is None else value
    if not isinstance(selected, int) or isinstance(selected, bool) or not 0 < selected <= maximum:
        raise ValueError(f"{field} must be between 1 and {maximum}")
    return selected


def _safe_target(root: Path, logical_path: str) -> Path:
    if not logical_path or "\\" in logical_path or logical_path.startswith("/"):
        raise ValueError("download destination must use relative POSIX syntax")
    relative = PurePosixPath(logical_path)
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("download destination cannot traverse its workspace")
    candidate = root.joinpath(*relative.parts)
    if not candidate.resolve(strict=False).is_relative_to(root.resolve()):
        raise ValueError("download destination escapes its workspace")
    return candidate
