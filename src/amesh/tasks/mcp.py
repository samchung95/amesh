from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, cast
from uuid import uuid5

import httpx2
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from pydantic import SecretStr

from amesh.domain import (
    AgentInvocationKind,
    AgentInvocationRecord,
    AgentInvocationStart,
    AgentInvocationState,
    FailureCategory,
    McpDiscoveryResult,
    McpToolImpact,
    McpToolPin,
    ModelDataEgress,
    canonical_hash,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import (
    TaskCompletion,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskHandler,
)
from amesh.ports import AgentPrimitiveRepository
from amesh.tasks.http import HttpTaskPolicy, validate_http_destination

McpTargetResolver = Callable[[str], Any]


async def discover_mcp_server(
    endpoint: str,
    credential: str,
    *,
    timeout_seconds: float = 30,
    target_resolver: McpTargetResolver | None = None,
    http_policy: HttpTaskPolicy | None = None,
) -> McpDiscoveryResult:
    tools: list[McpToolPin] = []
    server_name = "unknown"
    server_version = ""
    async with _client(
        endpoint,
        credential,
        timeout_seconds=timeout_seconds,
        target_resolver=target_resolver,
        http_policy=http_policy,
    ) as mcp_client:
        cursor: str | None = None
        while True:
            result = await mcp_client.list_tools(cursor=cursor)
            for tool in result.tools:
                annotations = tool.annotations
                impact = (
                    McpToolImpact.READ_ONLY
                    if annotations is not None and annotations.read_only_hint is True
                    else (
                        McpToolImpact.IDEMPOTENT_WRITE
                        if annotations is not None and annotations.idempotent_hint is True
                        else McpToolImpact.HIGH_IMPACT
                    )
                )
                tools.append(
                    McpToolPin(
                        name=tool.name,
                        description=tool.description or "",
                        inputSchema=tool.input_schema,
                        outputSchema=tool.output_schema,
                        impact=impact,
                    )
                )
            cursor = result.next_cursor
            if cursor is None:
                break
            if len(tools) >= 1000:
                raise RuntimeError("MCP discovery exceeded 1,000 tools")
        if mcp_client.server_info is not None:
            server_name = mcp_client.server_info.name
            server_version = mcp_client.server_info.version
    ordered = tuple(sorted(tools, key=lambda tool: tool.name))
    digest = "sha256:" + canonical_hash(
        {
            "serverName": server_name,
            "serverVersion": server_version,
            "tools": [
                {
                    "name": tool.name,
                    "inputSchema": tool.input_schema,
                    "outputSchema": tool.output_schema,
                }
                for tool in ordered
            ],
        }
    )
    return McpDiscoveryResult(
        serverName=server_name,
        serverVersion=server_version,
        tools=ordered,
        digest=digest,
    )


def agent_mcp_handler(
    target_resolver: McpTargetResolver | None = None,
    *,
    repository: AgentPrimitiveRepository | None = None,
    http_policy: HttpTaskPolicy | None = None,
) -> TaskHandler:
    async def run(
        task: TaskDefinition, context: TaskExecutionContext
    ) -> dict[str, Any] | TaskCompletion:
        extra = dict(task.model_extra or {})
        connection_key = extra.get("connection")
        if connection_key is None:
            return await _legacy_call(task, extra, target_resolver)
        if repository is None:
            raise ValueError("governed agent.mcp tasks require an agent primitive repository")
        if not isinstance(connection_key, str) or not connection_key:
            raise ValueError(f"task {task.id!r} connection must be a non-empty string")
        revision = extra.get("revision")
        if revision is not None and (
            not isinstance(revision, int) or isinstance(revision, bool) or revision < 1
        ):
            raise ValueError(f"task {task.id!r} revision must be a positive integer")
        connection = await repository.get_mcp_connection(
            context.tenant_id,
            context.namespace,
            connection_key,
            revision=revision,
        )
        spec = connection.spec
        if spec.credential_ref not in task.contract.secret_scopes:
            raise ValueError(
                f"task {task.id!r} connection credentialRef must be declared in "
                "contract.secretScopes"
            )
        credential = context.secrets.get(spec.credential_ref, "")
        if not credential:
            raise ValueError(f"task {task.id!r} credential {spec.credential_ref!r} is unavailable")
        tool_name = _required_string(extra, "tool", task.id)
        tool_pin = spec.pinned_tool(tool_name)
        arguments = extra.get("arguments", {})
        if not isinstance(arguments, dict):
            raise ValueError(f"task {task.id!r} arguments must be an object")
        data_policy = ModelDataEgress(extra.get("dataHandling", ModelDataEgress.DENY_SECRETS))
        outbound_arguments = _apply_data_policy(
            arguments,
            data_policy,
            tuple(context.secrets.values()),
        )
        _require_tool_authority(task, context, tool_pin, extra)
        return await _governed_mcp_call(
            task,
            context,
            extra,
            connection=connection,
            credential=credential,
            tool_name=tool_name,
            outbound_arguments=outbound_arguments,
            data_policy=data_policy,
            target_resolver=target_resolver,
            http_policy=http_policy,
            repository=repository,
        )
        try:
            Draft202012Validator(tool_pin.input_schema).validate(outbound_arguments)
        except JsonSchemaValidationError as exc:
            raise ValueError(
                f"MCP tool {tool_name!r} arguments failed schema: {exc.message}"
            ) from exc
        request_hash = canonical_hash(
            {
                "connectionDigest": connection.digest,
                "toolSchemaDigest": tool_pin.schema_digest,
                "tool": tool_name,
                "arguments": outbound_arguments,
            }
        )
        request_metadata = {
            "connectionId": str(connection.connection_id),
            "connectionKey": spec.key,
            "connectionRevision": connection.revision,
            "connectionDigest": connection.digest,
            "endpoint": spec.endpoint,
            "tool": tool_name,
            "toolSchemaDigest": tool_pin.schema_digest,
            "impact": tool_pin.impact.value,
            "dataHandling": data_policy.value,
            "arguments": _redact_values(outbound_arguments, tuple(context.secrets.values())),
            "requestHash": request_hash,
        }
        journal_operation = _journal_operation(
            f"{spec.key}.{tool_name}",
            extra,
            request_metadata,
        )
        claim = await repository.begin_invocation(
            AgentInvocationStart(
                invocationId=uuid5(context.attempt_id, f"mcp:{journal_operation}"),
                tenantId=context.tenant_id,
                namespace=context.namespace,
                executionId=context.execution_id,
                taskRunId=context.task_run_id,
                attempt=context.attempt,
                kind=AgentInvocationKind.MCP,
                operation=journal_operation,
                requestHash=request_hash,
                requestMetadata=request_metadata,
            )
        )
        if not claim.created:
            return _reused_completion(claim.record)
        invocation_id = claim.record.invocation_id
        try:
            discovery = await discover_mcp_server(
                spec.endpoint,
                credential,
                timeout_seconds=task.timeout_seconds or 30,
                target_resolver=target_resolver,
                http_policy=http_policy,
            )
            live_tool = next((tool for tool in discovery.tools if tool.name == tool_name), None)
            if live_tool is None:
                raise RuntimeError(f"MCP server no longer exposes pinned tool {tool_name!r}")
            if live_tool.schema_digest != tool_pin.schema_digest:
                raise RuntimeError(
                    f"MCP tool {tool_name!r} schema drifted from {tool_pin.schema_digest} "
                    f"to {live_tool.schema_digest}"
                )
            payload = await _call_tool(
                spec.endpoint,
                credential,
                tool_name,
                outbound_arguments,
                timeout_seconds=task.timeout_seconds or 30,
                target_resolver=target_resolver,
                http_policy=http_policy,
            )
            structured = payload.get("structuredContent")
            if tool_pin.output_schema is not None:
                try:
                    Draft202012Validator(tool_pin.output_schema).validate(structured)
                except JsonSchemaValidationError as exc:
                    raise ValueError(
                        f"MCP tool {tool_name!r} output failed schema: {exc.message}"
                    ) from exc
            output = {
                **payload,
                "connection": {
                    "key": spec.key,
                    "revision": connection.revision,
                    "digest": connection.digest,
                },
                "toolSchemaDigest": tool_pin.schema_digest,
                "requestHash": request_hash,
            }
            safe_output = cast(
                dict[str, Any],
                _redact_values(output, tuple(context.secrets.values())),
            )
            await repository.complete_invocation(
                invocation_id,
                tenant_id=context.tenant_id,
                state=AgentInvocationState.SUCCEEDED,
                result=safe_output,
            )
            return TaskCompletion(output=safe_output)
        except Exception as exc:
            secret_values = tuple(context.secrets.values())
            await repository.complete_invocation(
                invocation_id,
                tenant_id=context.tenant_id,
                state=AgentInvocationState.FAILED,
                error=str(_redact_values(_safe_error(exc), secret_values)),
            )
            raise _mcp_failure(
                exc,
                invocation_id,
                request_hash,
                secrets=secret_values,
            ) from exc

    return run


async def _governed_mcp_call(
    task: TaskDefinition,
    context: TaskExecutionContext,
    extra: dict[str, Any],
    *,
    connection: Any,
    credential: str,
    tool_name: str,
    outbound_arguments: dict[str, Any],
    data_policy: ModelDataEgress,
    target_resolver: McpTargetResolver | None,
    http_policy: HttpTaskPolicy | None,
    repository: AgentPrimitiveRepository,
) -> TaskCompletion:
    # Import lazily because the neutral adapter reuses this module's MCP client.
    from amesh.domain import (
        ToolInvocationRequest,
        ToolPolicy,
        ToolProviderKind,
        ToolProviderRef,
    )
    from amesh.tasks.tool_provider import (
        AgentPrimitiveInvocationJournal,
        GovernedToolInvoker,
        McpToolProvider,
    )

    spec = connection.spec
    legacy_hash = canonical_hash(
        {
            "connectionDigest": connection.digest,
            "toolSchemaDigest": spec.pinned_tool(tool_name).schema_digest,
            "tool": tool_name,
            "arguments": outbound_arguments,
        }
    )
    request_metadata: dict[str, object] = {
        "connectionId": str(connection.connection_id),
        "connectionKey": spec.key,
        "connectionRevision": connection.revision,
        "connectionDigest": connection.digest,
        "endpoint": spec.endpoint,
        "tool": tool_name,
        "toolSchemaDigest": spec.pinned_tool(tool_name).schema_digest,
        "schemaDigest": spec.pinned_tool(tool_name).schema_digest,
        "impact": spec.pinned_tool(tool_name).impact.value,
        "dataHandling": data_policy.value,
        "arguments": _redact_values(outbound_arguments, tuple(context.secrets.values())),
        "requestHash": legacy_hash,
        "policyDigest": canonical_hash(
            {
                "allowlist": spec.tool_allowlist,
                "secretScopes": task.contract.secret_scopes,
            }
        ),
    }
    journal_operation = _journal_operation(
        f"{spec.key}.{tool_name}",
        extra,
        request_metadata,
    )
    invocation_id = uuid5(context.attempt_id, f"mcp:{journal_operation}")
    approval_task = extra.get("approvalTask")
    request = ToolInvocationRequest(
        provider=ToolProviderRef(
            kind=ToolProviderKind.MCP,
            key=spec.key,
            revision=connection.revision,
        ),
        toolName=tool_name,
        arguments=outbound_arguments,
        tenantId=context.tenant_id,
        namespace=context.namespace,
        executionId=context.execution_id,
        taskRunId=context.task_run_id,
        attempt=context.attempt,
        invocationId=invocation_id,
        invocationKey=(
            extra.get("invocationKey") if isinstance(extra.get("invocationKey"), str) else None
        ),
        timeoutSeconds=task.timeout_seconds or 30,
        allowWrite=extra.get("allowWrite") is True,
        approvalGranted=(
            isinstance(approval_task, str)
            and isinstance(context.outputs.get(approval_task), dict)
            and context.outputs[approval_task].get("decision") == "APPROVED"
        ),
        secretValues=tuple(SecretStr(value) for value in context.secrets.values()),
        requestHashOverride=legacy_hash,
    )
    policy = ToolPolicy(
        allowedTools=spec.tool_allowlist,
        secretScopes=task.contract.secret_scopes,
        allowHighImpact=True,
    )
    provider = McpToolProvider(
        request.provider,
        spec.endpoint,
        credential,
        target_resolver=target_resolver,
        http_policy=http_policy,
        pinned_tools=spec.tools,
    )
    try:
        result = await GovernedToolInvoker(
            provider,
            AgentPrimitiveInvocationJournal(repository),
        ).invoke(request, policy)
    except Exception as exc:
        raise _mcp_failure(
            exc,
            invocation_id,
            legacy_hash,
            secrets=tuple(context.secrets.values()),
        ) from exc
    output = {
        **result.output,
        "connection": {
            "key": spec.key,
            "revision": connection.revision,
            "digest": connection.digest,
        },
        "toolSchemaDigest": spec.pinned_tool(tool_name).schema_digest,
        "requestHash": legacy_hash,
    }
    return TaskCompletion(
        output=cast(
            dict[str, Any],
            _redact_values(output, tuple(context.secrets.values())),
        )
    )


def _journal_operation(
    operation: str,
    extra: dict[str, Any],
    metadata: dict[str, Any],
) -> str:
    invocation_key = extra.get("invocationKey")
    if invocation_key is None:
        return operation
    if not isinstance(invocation_key, str) or not invocation_key or len(invocation_key) > 255:
        raise ValueError("invocationKey must be a non-empty string of at most 255 characters")
    metadata["invocationKey"] = invocation_key
    return f"{operation[:80]}#{canonical_hash(invocation_key)[:32]}"


async def _legacy_call(
    task: TaskDefinition,
    extra: dict[str, Any],
    target_resolver: McpTargetResolver | None,
) -> dict[str, Any]:
    endpoint = _required_string(extra, "endpoint", task.id)
    tool = _required_string(extra, "tool", task.id)
    arguments = extra.get("arguments", {})
    if not isinstance(arguments, dict):
        raise ValueError(f"task {task.id!r} arguments must be an object")
    target = target_resolver(endpoint) if target_resolver is not None else endpoint
    async with Client(
        target,
        raise_exceptions=True,
        read_timeout_seconds=task.timeout_seconds,
    ) as mcp_client:
        result = await mcp_client.call_tool(tool, arguments)
    return _tool_result(tool, result)


async def _call_tool(
    endpoint: str,
    credential: str,
    tool: str,
    arguments: dict[str, Any],
    *,
    timeout_seconds: float,
    target_resolver: McpTargetResolver | None,
    http_policy: HttpTaskPolicy | None,
) -> dict[str, Any]:
    async with _client(
        endpoint,
        credential,
        timeout_seconds=timeout_seconds,
        target_resolver=target_resolver,
        http_policy=http_policy,
    ) as mcp_client:
        result = await mcp_client.call_tool(tool, arguments)
    return _tool_result(tool, result)


def _tool_result(tool: str, result: Any) -> dict[str, Any]:
    if result.is_error:
        raise RuntimeError(f"MCP tool {tool!r} returned an error")
    payload = result.model_dump(mode="json", by_alias=True)
    return {
        "content": payload.get("content", []),
        "structuredContent": payload.get("structuredContent"),
    }


@asynccontextmanager
async def _client(
    endpoint: str,
    credential: str,
    *,
    timeout_seconds: float,
    target_resolver: McpTargetResolver | None,
    http_policy: HttpTaskPolicy | None,
) -> AsyncIterator[Client]:
    if target_resolver is not None:
        async with Client(
            target_resolver(endpoint),
            raise_exceptions=True,
            read_timeout_seconds=timeout_seconds,
        ) as mcp_client:
            yield mcp_client
        return
    validate_http_destination(endpoint, http_policy or HttpTaskPolicy(), resolve_dns=True)
    timeout = httpx2.Timeout(timeout_seconds, read=timeout_seconds)
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {credential}"},
        timeout=timeout,
        follow_redirects=False,
    ) as http_client:
        transport = streamable_http_client(endpoint, http_client=http_client)
        async with Client(
            transport,
            raise_exceptions=True,
            read_timeout_seconds=timeout_seconds,
        ) as mcp_client:
            yield mcp_client


def _require_tool_authority(
    task: TaskDefinition,
    context: TaskExecutionContext,
    tool: McpToolPin,
    extra: dict[str, Any],
) -> None:
    if tool.impact is McpToolImpact.READ_ONLY:
        return
    if extra.get("allowWrite") is not True:
        raise PermissionError(
            f"MCP tool {tool.name!r} requires explicit allowWrite because it is {tool.impact.value}"
        )
    if tool.impact is not McpToolImpact.HIGH_IMPACT:
        return
    approval_task = extra.get("approvalTask")
    approval = context.outputs.get(approval_task) if isinstance(approval_task, str) else None
    if not isinstance(approval, dict) or approval.get("decision") != "APPROVED":
        raise PermissionError(f"MCP tool {tool.name!r} requires an APPROVED approvalTask output")
    if approval_task not in task.depends_on:
        raise PermissionError("approvalTask must be a direct task dependency")


def _apply_data_policy(
    arguments: dict[str, Any],
    policy: ModelDataEgress,
    secrets: tuple[str, ...],
) -> dict[str, Any]:
    has_secret = any(secret and _contains_value(arguments, secret) for secret in secrets)
    if has_secret and policy is ModelDataEgress.DENY_SECRETS:
        raise PermissionError("MCP arguments contain secret material denied by dataHandling")
    if policy is ModelDataEgress.REDACT_SECRETS:
        return cast(dict[str, Any], _redact_values(arguments, secrets))
    return arguments


def _reused_completion(record: AgentInvocationRecord) -> TaskCompletion:
    if record.state is AgentInvocationState.SUCCEEDED and record.result is not None:
        return TaskCompletion(output=record.result)
    evidence: dict[str, object] = {
        "agentInvocation": {
            "invocationId": str(record.invocation_id),
            "state": record.state.value,
            "requestHash": record.request_hash,
            "ambiguousExternalOutcome": record.state is AgentInvocationState.STARTED,
        }
    }
    if record.state is AgentInvocationState.STARTED:
        raise TaskExecutionFailure(
            "MCP invocation has an ambiguous external outcome and was not repeated",
            FailureCategory.INFRASTRUCTURE,
            evidence=evidence,
        )
    raise TaskExecutionFailure(
        record.error or "MCP invocation previously failed",
        FailureCategory.NON_RETRYABLE,
        evidence=evidence,
    )


def _mcp_failure(
    exc: Exception,
    invocation_id: object,
    request_hash: str,
    *,
    secrets: tuple[str, ...] = (),
) -> TaskExecutionFailure:
    category = (
        exc.category
        if isinstance(exc, TaskExecutionFailure)
        else (
            FailureCategory.NON_RETRYABLE
            if isinstance(exc, (TypeError, ValueError, PermissionError))
            else FailureCategory.INFRASTRUCTURE
        )
    )
    return TaskExecutionFailure(
        str(_redact_values(_safe_error(exc), secrets)),
        category,
        evidence={
            "agentInvocation": {
                "invocationId": str(invocation_id),
                "state": AgentInvocationState.FAILED.value,
                "requestHash": request_hash,
            }
        },
    )


def _required_string(value: dict[str, Any], field: str, owner: str) -> str:
    selected = value.get(field)
    if not isinstance(selected, str) or not selected:
        raise ValueError(f"{owner!r} requires {field}")
    return selected


def _safe_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {str(exc)[:2000]}"


def _contains_value(value: object, secret: str) -> bool:
    if isinstance(value, str):
        return secret in value
    if isinstance(value, dict):
        return any(_contains_value(item, secret) for item in value.values())
    if isinstance(value, list | tuple):
        return any(_contains_value(item, secret) for item in value)
    return False


def _redact_values(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED]")
        return redacted
    if isinstance(value, dict):
        return {str(key): _redact_values(item, secrets) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_redact_values(item, secrets) for item in value]
    return value
