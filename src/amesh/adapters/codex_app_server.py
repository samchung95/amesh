"""Official Codex App Server JSONL adapter.

The adapter deliberately owns only the process/protocol edge.  Account state remains in the
Codex-managed ``CODEX_HOME`` selected for one AMESH tenant binding; AMESH never receives or
persists the refresh token that Codex stores there.
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import shutil
import tempfile
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic, time
from typing import Any, TypeVar, cast
from urllib.parse import urlsplit
from uuid import uuid4

from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressStatus,
    AgentStatusDetail,
)
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.domain.image_validation import inspect_image_bytes
from amesh.ports.agent_primitives import (
    ImageArtifactResolver,
    ModelProviderAccess,
    ModelProviderProgressDelta,
    ModelProviderRequest,
    ModelProviderResponse,
    ModelProviderStreamEvent,
)
from amesh.ports.model_engines import (
    EngineAccountStatus,
    EngineLoginStart,
    ModelEngineAccess,
    ProviderProcessError,
    ProviderProtocolError,
    ProviderTimeoutError,
)

from ._managed_process import (
    ManagedProcess,
    ManagedProcessError,
    ManagedProcessProtocolError,
    ManagedProcessTimeout,
    managed_process_environment,
)

_DEFAULT_COMMAND = ("codex", "app-server", "--stdio")
CODEX_APP_SERVER_ADAPTER_ID = "openai-codex-app-server"
CODEX_APP_SERVER_REVISION = "1.0.0"
_SAFE_AUTH_HOSTS = ("chatgpt.com", "auth.openai.com")
_MAX_DIAGNOSTIC_CHARS = 512
_InvocationResultT = TypeVar("_InvocationResultT")
_DISABLED_FEATURES = (
    "apps",
    "browser_use",
    "browser_use_external",
    "browser_use_full_cdp_access",
    "code_mode",
    "code_mode_host",
    "collaboration_modes",
    "computer_use",
    "deferred_executor",
    "enable_mcp_apps",
    "hooks",
    "image_generation",
    "in_app_browser",
    "mcp_2026_07_28",
    "multi_agent",
    "multi_agent_v2",
    "plugins",
    "shell_snapshot",
    "shell_snapshot_v2",
    "shell_tool",
    "skill_search",
    "tool_call_mcp_elicitation",
    "unified_exec",
    "view_image",
    "web_search_cached",
    "web_search_request",
)


class CodexAppServerError(ProviderProcessError):
    """Base error for process or protocol failures."""


class CodexAppServerProtocolError(CodexAppServerError, ProviderProtocolError):
    """The process returned malformed or unexpected JSONL."""


class CodexAppServerRpcError(CodexAppServerError):
    """The app server returned a JSON-RPC error."""

    def __init__(self, method: str, error: Mapping[str, Any]) -> None:
        message = _bounded_text(error.get("message")) or "Codex App Server request failed"
        super().__init__(f"Codex App Server {method!r} failed: {message}")
        self.method = method
        self.code = error.get("code")


class CodexAppServerTimeout(CodexAppServerError, ProviderTimeoutError):
    """The bounded app-server operation did not finish in time."""


@dataclass(frozen=True)
class CodexAppServerConfig:
    """Pinned command and bounded process settings."""

    command: tuple[str, ...] = _DEFAULT_COMMAND
    state_root: Path = Path(".amesh-codex")
    client_name: str = "amesh"
    client_version: str = "0.2.0"
    frame_limit_bytes: int = 1_048_576
    timeout_seconds: float = 120.0
    cancel_grace_seconds: float = 2.0
    pending_login_timeout_seconds: float = 600.0
    environment: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.command or any(not isinstance(part, str) or not part for part in self.command):
            raise ValueError("Codex App Server command must be a non-empty argv tuple")
        if self.frame_limit_bytes < 512:
            raise ValueError("frame_limit_bytes must be at least 512")
        if (
            self.timeout_seconds <= 0
            or self.cancel_grace_seconds <= 0
            or self.pending_login_timeout_seconds <= 0
        ):
            raise ValueError("Codex App Server timeouts must be positive")
        if not self.client_name or not self.client_version:
            raise ValueError("Codex App Server client metadata is required")


def derive_codex_home(
    state_root: str | Path,
    *,
    tenant_id: str,
    namespace: str,
    engine_ref: str,
) -> Path:
    """Derive a stable, non-user-controlled home beneath the configured server root."""

    for name, value in (
        ("tenant_id", tenant_id),
        ("namespace", namespace),
        ("engine_ref", engine_ref),
    ):
        if not isinstance(value, str) or not value.strip() or len(value) > 512:
            raise ValueError(f"{name} must be a non-blank bounded string")
    identity = "\0".join((tenant_id, namespace, engine_ref)).encode("utf-8")
    digest = hashlib.sha256(identity).hexdigest()
    return Path(state_root).resolve() / "codex" / digest


CodexAccountStatus = EngineAccountStatus
CodexLoginStart = EngineLoginStart


@dataclass(frozen=True)
class _CodexLoginOutcome:
    success: bool | None
    error: str | None = None


class _JsonRpcProcess:
    def __init__(
        self, config: CodexAppServerConfig, home: Path, workdir: Path | None = None
    ) -> None:
        self._config = config
        self._home = home
        self._workdir = workdir
        self._process: asyncio.subprocess.Process | None = None
        self._managed_process: ManagedProcess | None = None
        self._next_id = 0
        self._initialized = False
        self._notifications: deque[dict[str, Any]] = deque()

    async def start(self) -> None:
        if self._process is not None:
            return
        self._home.mkdir(parents=True, exist_ok=True)
        if self._workdir is not None:
            self._workdir.mkdir(parents=True, exist_ok=True)
        environment = managed_process_environment(
            self._config.environment,
            overrides={"HOME": str(self._home), "CODEX_HOME": str(self._home)},
        )
        executable = shutil.which(self._config.command[0])
        if executable is None:
            raise CodexAppServerError("could not resolve pinned Codex App Server command")
        command = (
            executable,
            *self._config.command[1:],
            *(flag for feature in _DISABLED_FEATURES for flag in ("--disable", feature)),
        )
        managed = ManagedProcess(
            command,
            environment=environment,
            frame_limit_bytes=self._config.frame_limit_bytes,
            timeout_seconds=self._config.timeout_seconds,
            cancel_grace_seconds=self._config.cancel_grace_seconds,
            cwd=self._workdir,
        )
        self._managed_process = managed
        try:
            self._process = await managed.start()
        except ManagedProcessError as exc:
            raise CodexAppServerError("could not start pinned Codex App Server command") from exc

    async def initialize(self) -> dict[str, Any]:
        if self._initialized:
            return {}
        result = await self.request(
            "initialize",
            {
                "clientInfo": {
                    "name": self._config.client_name,
                    "title": "AMESH Codex App Server adapter",
                    "version": self._config.client_version,
                },
                "capabilities": {
                    "experimentalApi": False,
                    "extensions": {},
                },
            },
        )
        await self.notify("initialized", None)
        self._initialized = True
        return result

    async def request(self, method: str, params: Mapping[str, Any] | None) -> dict[str, Any]:
        self._next_id += 1
        request_id = self._next_id
        message: dict[str, Any] = {"method": method, "id": request_id}
        if params is not None:
            message["params"] = params
        await self._write(message)
        while True:
            message = await self._read()
            if message.get("id") == request_id:
                if isinstance(message.get("error"), dict):
                    raise CodexAppServerRpcError(method, message["error"])
                result = message.get("result")
                if not isinstance(result, dict):
                    raise CodexAppServerProtocolError(
                        f"Codex {method} response result is not an object"
                    )
                return result
            await self._handle_unsolicited(message)

    async def notify(self, method: str, params: Mapping[str, Any] | None) -> None:
        await self._write({"method": method, "params": params or {}})

    async def read_notification(self) -> dict[str, Any]:
        while True:
            if self._notifications:
                return self._notifications.popleft()
            message = await self._read()
            if "id" in message:
                await self._handle_unsolicited(message)
                continue
            return message

    async def _handle_unsolicited(self, message: Mapping[str, Any]) -> None:
        method = message.get("method")
        request_id = message.get("id")
        if request_id is None:
            if isinstance(method, str):
                self._notifications.append(dict(message))
            return
        if not isinstance(method, str):
            return
        # AMESH never delegates native shell, patch, MCP or approval authority to Codex.
        await self._write(
            {
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "AMESH has disabled native Codex tools",
                },
            }
        )

    async def _write(self, message: Mapping[str, Any]) -> None:
        managed = self._managed_process
        if managed is None:
            raise CodexAppServerError("Codex App Server process is not running")
        encoded = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        try:
            await managed.write(encoded + b"\n")
        except ManagedProcessProtocolError as exc:
            raise CodexAppServerProtocolError(
                "Codex JSON-RPC frame exceeds configured limit"
            ) from exc
        except ManagedProcessTimeout as exc:
            raise CodexAppServerTimeout("timed out writing to Codex App Server") from exc
        except ManagedProcessError as exc:
            raise CodexAppServerError("Codex App Server exited while receiving input") from exc

    async def _read(self) -> dict[str, Any]:
        managed = self._managed_process
        if managed is None:
            raise CodexAppServerError("Codex App Server process is not running")
        try:
            raw = await managed.readline()
        except ManagedProcessTimeout as exc:
            raise CodexAppServerTimeout("timed out waiting for Codex App Server JSONL") from exc
        except ManagedProcessProtocolError as exc:
            raise CodexAppServerProtocolError(
                "Codex JSON-RPC frame exceeds configured limit"
            ) from exc
        except ManagedProcessError as exc:
            raise CodexAppServerError(str(exc)) from exc
        try:
            decoded = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CodexAppServerProtocolError("Codex App Server emitted invalid JSONL") from exc
        if not isinstance(decoded, dict):
            raise CodexAppServerProtocolError("Codex App Server JSONL message must be an object")
        return decoded

    async def interrupt(self, thread_id: str, turn_id: str) -> None:
        with suppress(CodexAppServerError, BrokenPipeError):
            await self.request("turn/interrupt", {"threadId": thread_id, "turnId": turn_id})

    async def close(self) -> None:
        process = self._process
        self._process = None
        managed = self._managed_process
        self._managed_process = None
        if process is None or managed is None:
            return
        await managed.close()


class CodexAppServerProcessClient:
    """Small JSONL client used by both model invocation and account management."""

    def __init__(
        self, config: CodexAppServerConfig, home: Path, *, workdir: Path | None = None
    ) -> None:
        self._rpc = _JsonRpcProcess(config, home, workdir)

    async def __aenter__(self) -> CodexAppServerProcessClient:
        try:
            await self._rpc.start()
            await self._rpc.initialize()
        except BaseException:
            await self._rpc.close()
            raise
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self._rpc.close()

    async def request(self, method: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return await self._rpc.request(method, params)

    async def account_read(self, *, refresh_token: bool = False) -> dict[str, Any]:
        return await self.request("account/read", {"refreshToken": refresh_token})

    async def account_login_start(self, login_type: str) -> dict[str, Any]:
        if login_type not in {"chatgpt", "chatgptDeviceCode"}:
            raise ValueError("only documented ChatGPT browser or device login is supported")
        return await self.request("account/login/start", {"type": login_type})

    async def account_logout(self) -> dict[str, Any]:
        return await self.request("account/logout")

    async def close(self) -> None:
        await self._rpc.close()

    async def start_thread(self, model: str) -> str:
        result = await self.request(
            "thread/start",
            {
                "model": model,
                "ephemeral": True,
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "config": _deny_by_default_config(),
            },
        )
        thread = result.get("thread")
        thread_id = thread.get("id") if isinstance(thread, dict) else None
        if not isinstance(thread_id, str) or not thread_id:
            raise CodexAppServerProtocolError("thread/start did not return a thread id")
        return thread_id

    async def start_turn(self, params: Mapping[str, Any]) -> str:
        result = await self.request("turn/start", params)
        turn = result.get("turn")
        turn_id = turn.get("id") if isinstance(turn, dict) else None
        if not isinstance(turn_id, str) or not turn_id:
            raise CodexAppServerProtocolError("turn/start did not return a turn id")
        return turn_id

    async def next_notification(self) -> dict[str, Any]:
        return await self._rpc.read_notification()

    async def interrupt(self, thread_id: str, turn_id: str) -> None:
        await self._rpc.interrupt(thread_id, turn_id)


class CodexAppServerModelProvider:
    """ModelProvider implementation over the official Codex App Server process API."""

    def __init__(
        self,
        config: CodexAppServerConfig | None = None,
        *,
        image_resolver: ImageArtifactResolver | None = None,
    ) -> None:
        self._config = config or CodexAppServerConfig()
        self._image_resolver = image_resolver

    async def invoke(
        self, request: ModelProviderRequest, access: ModelProviderAccess
    ) -> ModelProviderResponse:
        response: ModelProviderResponse | None = None
        async for event in self.stream(request, access):
            if event.kind == "response":
                response = event.response
        if response is None:
            raise CodexAppServerProtocolError("Codex turn ended without a model response")
        return response

    async def stream(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> AsyncIterator[ModelProviderStreamEvent]:
        tenant_id = request.tenant_id
        if tenant_id is None:
            raise ValueError("Codex App Server invocation requires tenantId")
        payload = copy.deepcopy(request.payload)
        engine_ref = _engine_ref_from_access(access)
        if not engine_ref:
            raise ValueError("Codex App Server invocation requires a delegated engineRef")
        namespace = request.namespace
        if not namespace:
            raise ValueError("Codex App Server invocation requires namespace")
        home = derive_codex_home(
            self._config.state_root,
            tenant_id=tenant_id,
            namespace=namespace,
            engine_ref=engine_ref,
        )
        timeout = request.timeout_seconds
        if timeout is not None and timeout <= 0:
            raise ValueError("Codex invocation timeout must be positive")
        reasoning_effort = _reasoning_effort(payload)
        temp_dir = tempfile.TemporaryDirectory(prefix="amesh-codex-image-")
        work_dir = tempfile.TemporaryDirectory(
            prefix="amesh-codex-work-", ignore_cleanup_errors=True
        )
        async with _InvocationClient(self._config, home, timeout, Path(work_dir.name)) as client:
            try:
                input_items = await client.run(
                    _build_turn_input(
                        payload,
                        resolver=self._image_resolver,
                        tenant_id=tenant_id,
                        temp_dir=Path(temp_dir.name),
                    ),
                    "timed out building Codex turn input",
                )
                output_schema = _output_schema(payload)
                thread_id = await client.start_thread(request.model)
                turn_params: dict[str, Any] = {
                    "threadId": thread_id,
                    "input": input_items,
                    "model": request.model,
                    "approvalPolicy": "never",
                    "sandboxPolicy": {"type": "readOnly"},
                }
                if output_schema is not None:
                    turn_params["outputSchema"] = output_schema
                if reasoning_effort is not None:
                    turn_params["effort"] = reasoning_effort
                await client.start_turn(turn_params)
                source_sequence = 1
                thinking_segment = None
                yield _progress(
                    AgentProgressActivity.MODEL,
                    AgentProgressStatus.STARTED,
                    "codex.turn",
                    source_sequence,
                )
                source_sequence += 1
                text_parts: list[str] = []
                usage: dict[str, Any] | None = None
                finish_reason = "stop"
                while True:
                    notification = await client.next_notification()
                    method = notification.get("method")
                    params = notification.get("params")
                    if not isinstance(method, str) or not isinstance(params, dict):
                        continue
                    if method in {"item/reasoning/summaryTextDelta", "item/reasoning/textDelta"}:
                        if thinking_segment is None:
                            thinking_segment = uuid4()
                            yield _progress(
                                AgentProgressActivity.THINKING,
                                AgentProgressStatus.STARTED,
                                "codex.reasoning",
                                source_sequence,
                                thinking_segment,
                            )
                            source_sequence += 1
                        yield _progress(
                            AgentProgressActivity.THINKING,
                            AgentProgressStatus.DELTA,
                            "codex.reasoning",
                            source_sequence,
                            thinking_segment,
                        )
                        source_sequence += 1
                        continue
                    if method == "item/agentMessage/delta":
                        delta = params.get("delta")
                        if isinstance(delta, str):
                            text_parts.append(delta)
                        continue
                    if method == "thread/tokenUsage/updated":
                        candidate = params.get("tokenUsage", params.get("usage"))
                        if isinstance(candidate, dict):
                            usage = _normalize_usage(candidate)
                        continue
                    if method != "turn/completed":
                        continue
                    turn = params.get("turn")
                    if not isinstance(turn, dict):
                        raise CodexAppServerProtocolError("turn/completed did not contain turn")
                    status = turn.get("status")
                    if status == "interrupted":
                        finish_reason = "cancelled"
                    elif status != "completed":
                        error = turn.get("error")
                        detail = (
                            _bounded_text(error.get("message")) if isinstance(error, dict) else None
                        )
                        raise CodexAppServerError(detail or "Codex turn failed")
                    usage = usage or _usage_from_turn(turn)
                    final_text = _final_text_from_turn(turn) or "".join(text_parts)
                    if thinking_segment is not None:
                        yield _progress(
                            AgentProgressActivity.THINKING,
                            AgentProgressStatus.COMPLETED,
                            "codex.reasoning",
                            source_sequence,
                            thinking_segment,
                        )
                        source_sequence += 1
                    yield _progress(
                        AgentProgressActivity.MODEL,
                        AgentProgressStatus.CANCELLED
                        if finish_reason == "cancelled"
                        else AgentProgressStatus.COMPLETED,
                        "codex.turn",
                        source_sequence,
                    )
                    response_payload = _openai_payload(
                        request.model,
                        final_text,
                        usage,
                        finish_reason,
                    )
                    yield ModelProviderStreamEvent.response_event(
                        ModelProviderResponse(payload=response_payload)
                    )
                    return
            except asyncio.CancelledError:
                await client.interrupt_if_active()
                raise
            finally:
                temp_dir.cleanup()
                work_dir.cleanup()


class _InvocationClient:
    def __init__(
        self, config: CodexAppServerConfig, home: Path, timeout: float | None, workdir: Path
    ) -> None:
        self.client = CodexAppServerProcessClient(config, home, workdir=workdir)
        self.timeout = timeout
        self._deadline = monotonic() + timeout if timeout is not None else None
        self.cancel_timeout = (
            min(timeout, config.cancel_grace_seconds)
            if timeout is not None
            else config.cancel_grace_seconds
        )
        self.thread_id: str | None = None
        self.turn_id: str | None = None

    async def run(
        self, operation: Awaitable[_InvocationResultT], detail: str
    ) -> _InvocationResultT:
        if self._deadline is None:
            return await operation
        remaining = self._deadline - monotonic()
        if remaining <= 0:
            raise CodexAppServerTimeout(detail)
        try:
            return await asyncio.wait_for(operation, remaining)
        except CodexAppServerTimeout:
            raise
        except TimeoutError as exc:
            raise CodexAppServerTimeout(detail) from exc

    async def __aenter__(self) -> _InvocationClient:
        await self.run(self.client.__aenter__(), "timed out starting Codex App Server")
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is asyncio.CancelledError or (
            isinstance(exc_type, type)
            and issubclass(exc_type, (CodexAppServerTimeout, TimeoutError))
        ):
            await self.interrupt_if_active()
        await self.client.__aexit__(exc_type, exc, traceback)

    async def start_thread(self, model: str) -> str:
        self.thread_id = await self.run(
            self.client.start_thread(model), "timed out starting Codex thread"
        )
        return self.thread_id

    async def start_turn(self, params: Mapping[str, Any]) -> str:
        self.turn_id = await self.run(
            self.client.start_turn(params), "timed out starting Codex turn"
        )
        return self.turn_id

    async def next_notification(self) -> dict[str, Any]:
        return await self.run(self.client.next_notification(), "timed out waiting for Codex turn")

    async def interrupt_if_active(self) -> None:
        if self.thread_id is not None and self.turn_id is not None:
            with suppress(CodexAppServerError, TimeoutError):
                await asyncio.wait_for(
                    self.client.interrupt(self.thread_id, self.turn_id),
                    self.cancel_timeout,
                )


class CodexAccountManager:
    """Provider-neutral account manager for isolated Codex homes."""

    def __init__(
        self, config: CodexAppServerConfig | None = None, *, engine_ref: str, namespace: str
    ) -> None:
        self._config = config or CodexAppServerConfig()
        self._engine_ref = engine_ref
        self._namespace = namespace
        self._pending: dict[str, CodexAppServerProcessClient] = {}
        self._login_tasks: dict[str, tuple[str, asyncio.Task[_CodexLoginOutcome]]] = {}

    def _home(self, tenant_id: str) -> Path:
        return derive_codex_home(
            self._config.state_root,
            tenant_id=tenant_id,
            namespace=self._namespace,
            engine_ref=self._engine_ref,
        )

    async def status(
        self,
        tenant_id: str,
        *,
        refresh_token: bool = False,
        include_rate_limits: bool = False,
        include_usage: bool = False,
    ) -> CodexAccountStatus:
        tracked = self._login_tasks.get(tenant_id)
        if tracked is not None and not tracked[1].done():
            return CodexAccountStatus(authenticated=None, actionRequired=True)
        outcome = tracked[1].result() if tracked is not None else None
        async with CodexAppServerProcessClient(self._config, self._home(tenant_id)) as client:
            result = await client.account_read(refresh_token=refresh_token)
            account = result.get("account")
            account_map = account if isinstance(account, dict) else {}
            rate_limits = None
            if account_map and include_rate_limits:
                rate_result = await client.request("account/rateLimits/read", {})
                rate_limits = rate_result if rate_result else None
            usage = None
            if account_map and include_usage:
                usage_result = await client.request("account/usage/read")
                usage = usage_result if usage_result else None
            auth_mode = _string_value(account_map.get("type"))
            authenticated: bool | None = bool(account)
            if not account_map and outcome is not None and outcome.success is not False:
                authenticated = None
            return CodexAccountStatus(
                authenticated=authenticated,
                authMode=auth_mode,
                planType=_string_value(account_map.get("planType")),
                requiresOpenaiAuth=(
                    result.get("requiresOpenaiAuth")
                    if isinstance(result.get("requiresOpenaiAuth"), bool)
                    else None
                ),
                rateLimits=rate_limits,
                usage=usage,
                actionRequired=authenticated is not True,
            )

    async def login_start(self, tenant_id: str, *, mode: str = "browser") -> CodexLoginStart:
        mode = {"browser": "chatgpt", "device": "chatgptDeviceCode"}.get(mode, mode)
        await self._release(tenant_id)
        client = CodexAppServerProcessClient(self._config, self._home(tenant_id))
        await client.__aenter__()
        try:
            result = await client.account_login_start(mode)
            kind = _string_value(result.get("type"))
            if kind not in {"chatgpt", "chatgptDeviceCode"}:
                raise CodexAppServerProtocolError("Codex login returned an unsupported flow")
            auth_url = _safe_auth_url(result.get("authUrl")) if kind == "chatgpt" else None
            verification_url = (
                _safe_auth_url(result.get("verificationUrl"))
                if kind == "chatgptDeviceCode"
                else None
            )
            login_id = _string_value(result.get("loginId"))
            if not login_id:
                raise CodexAppServerProtocolError("Codex login response did not contain loginId")
            expires = result.get("expiresAt")
            response = CodexLoginStart(
                kind=kind,
                loginId=login_id,
                authUrl=auth_url,
                verificationUrl=verification_url,
                userCode=_string_value(result.get("userCode")),
                expiresAt=expires
                if isinstance(expires, int) and not isinstance(expires, bool)
                else None,
            )
        except BaseException:
            await client.close()
            raise
        lifetime = (
            max(0.0, response.expires_at - time())
            if response.expires_at is not None
            else self._config.pending_login_timeout_seconds
        )
        self._pending[tenant_id] = client
        task = asyncio.create_task(
            self._monitor_login(tenant_id, response.login_id, client, lifetime)
        )
        self._login_tasks[tenant_id] = (response.login_id, task)
        return response

    async def logout(self, tenant_id: str) -> None:
        await self._release(tenant_id)
        async with CodexAppServerProcessClient(self._config, self._home(tenant_id)) as client:
            await client.account_logout()

    async def wait_login(
        self,
        tenant_id: str,
        login_id: str,
        *,
        timeout_seconds: float | None = None,
    ) -> bool:
        """Wait for the documented login completion notification without exposing credentials."""

        tracked = self._login_tasks.get(tenant_id)
        if tracked is None or tracked[0] != login_id:
            raise ValueError("no pending Codex login exists for tenant")
        wait_for = timeout_seconds if timeout_seconds is not None else self._config.timeout_seconds
        outcome = await asyncio.wait_for(asyncio.shield(tracked[1]), wait_for)
        if outcome.success is None:
            raise CodexAppServerError(outcome.error or "Codex login completion is unknown")
        return outcome.success

    async def close(self) -> None:
        tenant_ids = set(self._pending) | set(self._login_tasks)
        for tenant_id in tenant_ids:
            await self._release(tenant_id)

    async def _monitor_login(
        self,
        tenant_id: str,
        login_id: str,
        client: CodexAppServerProcessClient,
        lifetime: float,
    ) -> _CodexLoginOutcome:
        deadline = monotonic() + lifetime
        try:
            while True:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return _CodexLoginOutcome(False, "Codex login expired before completion")
                try:
                    message = await asyncio.wait_for(client.next_notification(), remaining)
                except CodexAppServerTimeout:
                    continue
                except TimeoutError:
                    return _CodexLoginOutcome(False, "Codex login expired before completion")
                if message.get("method") != "account/login/completed":
                    continue
                params = message.get("params")
                if not isinstance(params, dict) or params.get("loginId") not in {login_id, None}:
                    continue
                success = params.get("success")
                if not isinstance(success, bool):
                    raise CodexAppServerProtocolError("Codex login completion lacked success")
                error = params.get("error")
                if error is not None and not isinstance(error, str):
                    raise CodexAppServerProtocolError(
                        "Codex login completion contained invalid error"
                    )
                return _CodexLoginOutcome(success, _bounded_text(error))
        except CodexAppServerError as exc:
            return _CodexLoginOutcome(None, _bounded_text(str(exc)))
        finally:
            if self._pending.get(tenant_id) is client:
                self._pending.pop(tenant_id, None)
                await client.close()

    async def _release(self, tenant_id: str) -> None:
        client = self._pending.pop(tenant_id, None)
        tracked = self._login_tasks.pop(tenant_id, None)
        task = tracked[1] if tracked is not None else None
        try:
            if task is not None and task is not asyncio.current_task():
                if not task.done():
                    task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        finally:
            if client is not None:
                await client.close()


def _progress(
    activity: AgentProgressActivity,
    status: AgentProgressStatus,
    activity_id: str,
    source_sequence: int,
    segment_id: Any = None,
) -> ModelProviderStreamEvent:
    return ModelProviderStreamEvent.progress_event(
        ModelProviderProgressDelta(
            activity=activity,
            status=status,
            activityId=activity_id,
            segmentId=segment_id,
            sourceSequence=source_sequence,
            detail=AgentStatusDetail(code="codex.processing", label="Codex is processing"),
        )
    )


async def _build_turn_input(
    payload: dict[str, Any],
    *,
    resolver: ImageArtifactResolver | None,
    tenant_id: str,
    temp_dir: Path,
) -> list[dict[str, Any]]:
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        input_value = payload.get("input", payload.get("prompt", ""))
        if not isinstance(input_value, str) or not input_value.strip():
            raise ValueError("Codex request requires non-blank messages or input")
        return [{"type": "text", "text": input_value}]
    result: list[dict[str, Any]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Codex messages must be objects")
        role = _string_value(message.get("role")) or "user"
        content = message.get("content", "")
        text, images = await _message_content(
            content,
            resolver=resolver,
            tenant_id=tenant_id,
            temp_dir=temp_dir,
        )
        if text:
            prefix = "" if len(messages) == 1 and role == "user" else f"[{role}]\n"
            result.append({"type": "text", "text": prefix + text})
        result.extend(images)
    if not result:
        raise ValueError("Codex request contains no usable input")
    return result


async def _message_content(
    content: Any,
    *,
    resolver: ImageArtifactResolver | None,
    tenant_id: str,
    temp_dir: Path,
) -> tuple[str, list[dict[str, Any]]]:
    if isinstance(content, str):
        return content, []
    if not isinstance(content, list):
        return json.dumps(content, ensure_ascii=False, separators=(",", ":")), []
    text_parts: list[str] = []
    images: list[dict[str, Any]] = []
    for index, part in enumerate(content):
        if not isinstance(part, dict):
            raise ValueError("Codex content parts must be objects")
        if part.get("type") == "text":
            if isinstance(part.get("text"), str):
                text_parts.append(part["text"])
            continue
        if part.get("type") not in {"image_ref", "image"}:
            raise ValueError("Codex content supports text and governed image references")
        raw_image = part.get("image")
        if raw_image is None and isinstance(part.get("image_ref"), dict):
            raw_image = part["image_ref"]
        if resolver is None or not isinstance(raw_image, dict):
            raise ValueError("Codex image input requires a tenant-scoped image resolver")
        image = ImageArtifactRef.model_validate(raw_image)
        image_bytes = await resolver.resolve_image(image, tenant_id=tenant_id)
        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError("image resolver must return non-empty bytes")
        media_type = image.artifact.media_type
        if not isinstance(media_type, str):
            raise ValueError("image artifact must declare a media type")
        inspection = inspect_image_bytes(image_bytes, declared_media_type=media_type)
        target = temp_dir / f"image-{index:04d}.{inspection.media_type.rsplit('/', 1)[-1]}"
        target.write_bytes(image_bytes)
        images.append({"type": "localImage", "path": str(target)})
    return "".join(text_parts), images


def _output_schema(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    raw = payload.get("responseFormat", payload.get("response_format"))
    if not isinstance(raw, dict):
        return None
    if raw.get("type") != "json_schema":
        return None
    schema = raw.get("json_schema", raw.get("jsonSchema"))
    if not isinstance(schema, dict) or not isinstance(schema.get("schema"), dict):
        return None
    return cast(dict[str, Any], copy.deepcopy(schema["schema"]))


def _reasoning_effort(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("reasoning_effort", payload.get("reasoningEffort"))
    if value is None:
        return None
    if not isinstance(value, str) or value not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError(
            "Codex App Server reasoning effort must be low, medium, high, xhigh, or max"
        )
    return value


def _final_text_from_turn(turn: Mapping[str, Any]) -> str:
    items = turn.get("items")
    if not isinstance(items, list):
        return ""
    for item in reversed(items):
        if (
            isinstance(item, dict)
            and item.get("type") == "agentMessage"
            and isinstance(item.get("text"), str)
        ):
            return cast(str, item["text"])
    return ""


def _usage_from_turn(turn: Mapping[str, Any]) -> dict[str, Any] | None:
    usage = turn.get("usage")
    return _normalize_usage(usage) if isinstance(usage, dict) else None


def _normalize_usage(usage: Mapping[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    aliases = {
        "prompt_tokens": ("prompt_tokens", "inputTokens", "input_tokens"),
        "completion_tokens": ("completion_tokens", "outputTokens", "output_tokens"),
        "total_tokens": ("total_tokens", "totalTokens"),
    }
    for target, keys in aliases.items():
        value = next((usage.get(key) for key in keys if isinstance(usage.get(key), int)), None)
        if value is not None and value >= 0:
            values[target] = value
    if "total_tokens" not in values and {"prompt_tokens", "completion_tokens"} <= values.keys():
        values["total_tokens"] = values["prompt_tokens"] + values["completion_tokens"]
    return values


def _openai_payload(
    model: str,
    content: str,
    usage: dict[str, Any] | None,
    finish_reason: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": f"chatcmpl-codex-{uuid4().hex}",
        "object": "chat.completion",
        "created": int(time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": finish_reason,
            }
        ],
    }
    payload["usage"] = usage or {}
    return payload


def _safe_auth_url(value: Any) -> str:
    if not isinstance(value, str) or len(value) > 4096:
        raise CodexAppServerProtocolError("Codex login returned an invalid browser URL")
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower().rstrip(".")
    allowed = any(host == suffix or host.endswith("." + suffix) for suffix in _SAFE_AUTH_HOSTS)
    if parsed.scheme != "https" or not allowed:
        raise CodexAppServerProtocolError("Codex login returned an unsafe browser URL")
    return value


def _deny_by_default_config() -> dict[str, Any]:
    """Return an invocation-owned config overlay with no native tools or integrations."""

    return {
        "approval_policy": "never",
        "sandbox_mode": "read-only",
        "web_search": "disabled",
        "apps": {
            "_default": {
                "enabled": False,
                "default_tools_enabled": False,
                "open_world_enabled": False,
                "destructive_enabled": False,
            }
        },
        "browser_use": {
            "allow_history_access": False,
            "default_origin_policy": {
                "access": "deny",
                "downloads": "deny",
                "full_cdp_access": "deny",
                "uploads": "deny",
            },
        },
        "computer_use": {"default_app_access": "deny"},
        "mcp_servers": {},
        "plugins": {},
        "skills": {},
        "hooks": {},
        "features": {feature: False for feature in _DISABLED_FEATURES},
    }


def _engine_ref_from_access(access: ModelProviderAccess) -> str | None:
    if isinstance(access, ModelEngineAccess):
        return access.engine_ref
    return None


def _string_value(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _bounded_text(value: Any) -> str | None:
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return None
    return " ".join(str(value).split())[:_MAX_DIAGNOSTIC_CHARS] or None


__all__ = [
    "CODEX_APP_SERVER_ADAPTER_ID",
    "CODEX_APP_SERVER_REVISION",
    "CodexAccountManager",
    "CodexAccountStatus",
    "CodexAppServerConfig",
    "CodexAppServerError",
    "CodexAppServerModelProvider",
    "CodexAppServerProcessClient",
    "CodexAppServerProtocolError",
    "CodexAppServerRpcError",
    "CodexAppServerTimeout",
    "CodexLoginStart",
    "derive_codex_home",
]
