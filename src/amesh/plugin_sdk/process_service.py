from __future__ import annotations

import asyncio
import json
import secrets
import sys
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from .contracts import PluginOperation, PluginRequest, PluginResponse
from .errors import PluginErrorDetail, PluginErrorPhase
from .harness import PluginCapabilityGrant, PluginContractHarness, PluginHandler
from .manifest import PluginManifest
from .schema import validate_configuration
from .wire import (
    PLUGIN_METHOD_CANCEL,
    PLUGIN_METHOD_DISCOVER,
    PLUGIN_METHOD_HANDSHAKE,
    PLUGIN_METHOD_INVOKE,
    PLUGIN_METHOD_SHUTDOWN,
    PLUGIN_METHOD_VALIDATE,
    PLUGIN_NOTIFICATION_ARTIFACT,
    PLUGIN_NOTIFICATION_ASSET,
    PLUGIN_NOTIFICATION_HEARTBEAT,
    PLUGIN_NOTIFICATION_LOG,
    PLUGIN_NOTIFICATION_METRIC,
    PLUGIN_WIRE_VERSION,
    SUPPORTED_WIRE_FEATURES,
    JsonRpcError,
    JsonRpcNotification,
    JsonRpcRequest,
    JsonRpcResponse,
    PluginArtifact,
    PluginAsset,
    PluginAuthenticatedParams,
    PluginCapabilityEnvelope,
    PluginHandshakeParams,
    PluginInvocationParams,
    PluginMetric,
)


class ProcessPluginResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    response: PluginResponse
    metrics: tuple[PluginMetric, ...] = ()
    artifacts: tuple[PluginArtifact, ...] = ()
    assets: tuple[PluginAsset, ...] = ()


ProcessPluginHandler = Callable[
    [PluginRequest, PluginCapabilityEnvelope],
    Awaitable[PluginResponse | ProcessPluginResult],
]


class _Session:
    def __init__(self, params: PluginHandshakeParams) -> None:
        self.id = params.session_id
        self.token = params.workload_token.get_secret_value()
        self.expires_at = params.expires_at
        self.content_digest = params.content_digest


async def serve_stdio_plugin(
    manifest: PluginManifest,
    handlers: Mapping[tuple[str, PluginOperation], ProcessPluginHandler],
    *,
    heartbeat_seconds: float = 0.25,
) -> None:
    """Serve one language-neutral plugin session over JSON-RPC 2.0 newline frames."""

    writer_lock = asyncio.Lock()
    captured: ContextVar[ProcessPluginResult | None] = ContextVar(
        "amesh_process_plugin_result",
        default=None,
    )
    active_capabilities: ContextVar[PluginCapabilityEnvelope | None] = ContextVar(
        "amesh_process_plugin_capabilities",
        default=None,
    )
    wrapped: dict[tuple[str, PluginOperation], PluginHandler] = {}
    for key, handler in handlers.items():

        async def invoke_handler(
            request: PluginRequest,
            *,
            selected: ProcessPluginHandler = handler,
        ) -> PluginResponse:
            capability_envelope = active_capabilities.get()
            if capability_envelope is None:
                raise RuntimeError("plugin invocation capability envelope is unavailable")
            result = await selected(request, capability_envelope)
            if isinstance(result, ProcessPluginResult):
                captured.set(result)
                return result.response
            if not isinstance(result, PluginResponse):
                raise TypeError("plugin handler must return PluginResponse or ProcessPluginResult")
            return result

        wrapped[key] = invoke_handler
    capabilities = manifest.capabilities
    harness = PluginContractHarness(
        manifest,
        wrapped,
        grant=PluginCapabilityGrant(
            capabilities=capabilities.required,
            networkAccess=capabilities.network_access,
            allowedEgress=capabilities.allowed_egress,
            filesystemAccess=capabilities.filesystem_access,
            secretScopes=capabilities.secret_scopes,
        ),
    )
    entry_points = {entry.name: entry for entry in manifest.entry_points}
    session: _Session | None = None
    invocation: asyncio.Task[None] | None = None
    invocation_id: str | None = None

    async def write(value: BaseModel) -> None:
        encoded = (
            json.dumps(
                value.model_dump(mode="json", by_alias=True, exclude_none=True),
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        async with writer_lock:
            sys.stdout.buffer.write(encoded)
            sys.stdout.buffer.flush()

    async def write_response(
        request_id: str,
        *,
        result: dict[str, Any] | None = None,
        error: JsonRpcError | None = None,
    ) -> None:
        await write(JsonRpcResponse(id=request_id, result=result, error=error))

    def authenticate(params: Mapping[str, Any]) -> _Session:
        if session is None:
            raise PermissionError("plugin session has not completed the handshake")
        authenticated = PluginAuthenticatedParams.model_validate(
            {
                "sessionId": params.get("sessionId"),
                "workloadToken": params.get("workloadToken"),
                "invocationId": params.get("invocationId"),
            }
        )
        if datetime.now(UTC) >= session.expires_at:
            raise PermissionError("plugin workload identity expired")
        if authenticated.session_id != session.id or not secrets.compare_digest(
            authenticated.workload_token.get_secret_value(),
            session.token,
        ):
            raise PermissionError("plugin workload identity mismatch")
        return session

    def authenticated_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
        if session is None:
            raise RuntimeError("plugin session is unavailable")
        return {
            "sessionId": session.id,
            "workloadToken": session.token,
            **payload,
        }

    async def notify(method: str, payload: Mapping[str, Any]) -> None:
        await write(JsonRpcNotification(method=method, params=authenticated_payload(payload)))

    async def heartbeat(active_invocation_id: str) -> None:
        while True:
            await notify(
                PLUGIN_NOTIFICATION_HEARTBEAT,
                {
                    "invocationId": active_invocation_id,
                    "observedAt": datetime.now(UTC).isoformat(),
                },
            )
            await asyncio.sleep(heartbeat_seconds)

    async def execute(request_id: str, params: PluginInvocationParams) -> None:
        heartbeat_task = asyncio.create_task(heartbeat(params.request.session.invocation_id))
        token = captured.set(None)
        capability_token = active_capabilities.set(params.capabilities)
        try:
            response = await harness.invoke(params.request)
            result = captured.get() or ProcessPluginResult(response=response)
            for log in result.response.logs:
                await notify(
                    PLUGIN_NOTIFICATION_LOG,
                    {
                        "invocationId": params.request.session.invocation_id,
                        "log": log.model_dump(mode="json", by_alias=True, exclude_none=True),
                    },
                )
            for metric in result.metrics:
                await notify(
                    PLUGIN_NOTIFICATION_METRIC,
                    {
                        "invocationId": params.request.session.invocation_id,
                        "metric": metric.model_dump(mode="json", by_alias=True, exclude_none=True),
                    },
                )
            for artifact in result.artifacts:
                await notify(
                    PLUGIN_NOTIFICATION_ARTIFACT,
                    {
                        "invocationId": params.request.session.invocation_id,
                        "artifact": artifact.model_dump(
                            mode="json", by_alias=True, exclude_none=True
                        ),
                    },
                )
            for asset in result.assets:
                await notify(
                    PLUGIN_NOTIFICATION_ASSET,
                    {
                        "invocationId": params.request.session.invocation_id,
                        "asset": asset.model_dump(
                            mode="json", by_alias=True, exclude_none=True
                        ),
                    },
                )
            response_payload = result.response.model_copy(update={"logs": ()}).model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
            )
            await write_response(
                request_id,
                result=authenticated_payload({"response": response_payload}),
            )
        except asyncio.CancelledError:
            await write_response(
                request_id,
                error=JsonRpcError(
                    code=-32010,
                    message="plugin invocation cancelled",
                    data=authenticated_payload(
                        {"invocationId": params.request.session.invocation_id}
                    ),
                ),
            )
        finally:
            captured.reset(token)
            active_capabilities.reset(capability_token)
            heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await heartbeat_task

    while True:
        line = await asyncio.to_thread(sys.stdin.buffer.readline)
        if not line:
            break
        payload: object = {}
        try:
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError("JSON-RPC frame must be an object")
            if "id" not in payload:
                notification = JsonRpcNotification.model_validate(payload)
                if notification.method == PLUGIN_METHOD_CANCEL:
                    authenticate(notification.params)
                    requested = notification.params.get("invocationId")
                    if invocation is not None and requested == invocation_id:
                        invocation.cancel()
                elif notification.method == PLUGIN_METHOD_SHUTDOWN:
                    authenticate(notification.params)
                    if invocation is not None:
                        invocation.cancel()
                        with suppress(asyncio.CancelledError):
                            await invocation
                    break
                continue
            request = JsonRpcRequest.model_validate(payload)
            if request.method == PLUGIN_METHOD_HANDSHAKE:
                handshake_params = PluginHandshakeParams.model_validate(request.params)
                if session is not None:
                    raise ValueError("plugin session handshake is already complete")
                if PLUGIN_WIRE_VERSION not in handshake_params.protocol_versions:
                    raise ValueError("no compatible plugin wire protocol")
                if not set(handshake_params.required_features).issubset(SUPPORTED_WIRE_FEATURES):
                    raise ValueError("plugin requires unsupported wire features")
                if (
                    handshake_params.plugin != manifest.name
                    or handshake_params.version != manifest.version
                ):
                    raise ValueError("plugin handshake identity mismatch")
                session = _Session(handshake_params)
                await write_response(
                    request.id,
                    result={
                        "protocolVersion": PLUGIN_WIRE_VERSION,
                        "features": [feature.value for feature in SUPPORTED_WIRE_FEATURES],
                        "plugin": manifest.name,
                        "version": manifest.version,
                        "contentDigest": session.content_digest,
                        "sessionId": session.id,
                        "workloadToken": session.token,
                    },
                )
            elif request.method == PLUGIN_METHOD_DISCOVER:
                authenticate(request.params)
                await write_response(
                    request.id,
                    result=authenticated_payload(
                        {
                            "entryPoints": [
                                {
                                    "name": entry.name,
                                    "type": entry.type.value,
                                    "resourceType": entry.resolved_resource_type,
                                    "configurationSchema": entry.configuration_schema,
                                    "outputSchema": entry.output_schema,
                                }
                                for entry in manifest.entry_points
                            ]
                        }
                    ),
                )
            elif request.method == PLUGIN_METHOD_VALIDATE:
                authenticate(request.params)
                validation_params = PluginInvocationParams.model_validate(request.params)
                entry = entry_points.get(validation_params.request.entry_point)
                errors = (
                    validate_configuration(entry, validation_params.request.configuration)
                    if entry is not None
                    else (
                        PluginErrorDetail(
                            code="plugin.configuration.entry_point_unknown",
                            message="plugin entry point is not declared",
                            phase=PluginErrorPhase.CONFIGURATION,
                        ),
                    )
                )
                await write_response(
                    request.id,
                    result=authenticated_payload(
                        {
                            "response": PluginResponse(
                                invocationId=validation_params.request.session.invocation_id,
                                errors=errors,
                            ).model_dump(mode="json", by_alias=True, exclude_none=True)
                        }
                    ),
                )
            elif request.method == PLUGIN_METHOD_INVOKE:
                authenticate(request.params)
                if invocation is not None and not invocation.done():
                    raise RuntimeError("plugin process supports one active invocation")
                invocation_params = PluginInvocationParams.model_validate(request.params)
                invocation_id = invocation_params.request.session.invocation_id
                invocation = asyncio.create_task(execute(request.id, invocation_params))
            else:
                await write_response(
                    request.id,
                    error=JsonRpcError(code=-32601, message="method not found"),
                )
        except Exception as exc:
            request_id = (
                str(payload.get("id", "invalid")) if isinstance(payload, dict) else "invalid"
            )
            await write_response(
                request_id,
                error=JsonRpcError(
                    code=-32602,
                    message="invalid plugin RPC request",
                    data={"exceptionType": type(exc).__name__},
                ),
            )

    if invocation is not None and not invocation.done():
        invocation.cancel()
        with suppress(asyncio.CancelledError):
            await invocation
