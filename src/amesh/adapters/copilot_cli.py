"""Official GitHub Copilot CLI JSONL adapter.

Only the documented ``copilot -p ... --output-format=json`` process contract is used here.
The CLI owns its refresh credential inside the isolated ``COPILOT_HOME``; AMESH exposes
neither that credential nor the CLI's session files.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections.abc import AsyncIterator, Mapping
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from amesh.domain.agent_progress import (
    AgentProgressActivity,
    AgentProgressStatus,
    AgentStatusDetail,
)
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.domain.image_validation import build_image_artifact_ref, inspect_image_bytes
from amesh.ports.agent_primitives import (
    ImageArtifactResolver,
    ModelProviderAccess,
    ModelProviderProgressDelta,
    ModelProviderRequest,
    ModelProviderResponse,
    ModelProviderStreamEvent,
)
from amesh.ports.model_engines import EngineAccountStatus, EngineLoginStart, ModelEngineAccess

_DEFAULT_COMMAND = ("copilot",)
COPILOT_CLI_ADAPTER_ID = "github-copilot-cli"
COPILOT_CLI_ADAPTER_REVISION = "1.0.0"
_ENVIRONMENT_KEYS = ("PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR")
_MAX_DIAGNOSTIC_CHARS = 512
_DEFAULT_FRAME_LIMIT = 1_048_576
_MAX_LAUNCHER_BYTES = 131_072
_INSTALLING_LAUNCHER_MARKERS = (
    "install-copilotcli",
    "update-copilotcli",
    "would you like to reinstall github copilot cli",
    "winget install github.copilot",
)
_DEVICE_CODE_RE = re.compile(r"\b[A-Z0-9]{3,8}(?:[- ][A-Z0-9]{3,8})\b")
_URL_RE = re.compile(r"https://[^\s\"'<>]+")


class CopilotCliError(RuntimeError):
    """Base error for Copilot CLI process or protocol failures."""


class CopilotCliProtocolError(CopilotCliError):
    """The CLI returned malformed or unsupported JSONL."""


class CopilotCliTimeout(CopilotCliError, TimeoutError):
    """A bounded Copilot CLI operation did not finish in time."""


@dataclass(frozen=True)
class CopilotCliConfig:
    """Pinned Copilot command and process bounds."""

    command: tuple[str, ...] = _DEFAULT_COMMAND
    state_root: Path = Path(".amesh-copilot")
    frame_limit_bytes: int = _DEFAULT_FRAME_LIMIT
    timeout_seconds: float = 120.0
    cancel_grace_seconds: float = 2.0
    github_host: str = "https://github.com"

    def __post_init__(self) -> None:
        if not self.command or any(not isinstance(part, str) or not part for part in self.command):
            raise ValueError("Copilot CLI command must be a non-empty argv tuple")
        if self.frame_limit_bytes < 512:
            raise ValueError("frame_limit_bytes must be at least 512")
        if self.timeout_seconds <= 0 or self.cancel_grace_seconds <= 0:
            raise ValueError("Copilot CLI timeouts must be positive")
        _safe_auth_url(self.github_host)


def derive_copilot_home(
    state_root: str | Path,
    *,
    tenant_id: str,
    namespace: str,
    engine_ref: str,
) -> Path:
    """Derive a stable home beneath the server-owned root."""

    for name, value in (
        ("tenant_id", tenant_id),
        ("namespace", namespace),
        ("engine_ref", engine_ref),
    ):
        if not isinstance(value, str) or not value.strip() or len(value) > 512:
            raise ValueError(f"{name} must be a non-blank bounded string")
    identity = "\0".join((tenant_id, namespace, engine_ref)).encode("utf-8")
    digest = hashlib.sha256(identity).hexdigest()
    return Path(state_root).resolve() / "copilot" / digest


class _CopilotProcess:
    def __init__(
        self,
        config: CopilotCliConfig,
        *,
        home: Path,
        cwd: Path,
        args: tuple[str, ...],
        merge_stderr: bool = False,
        owns_cwd: bool = False,
    ) -> None:
        self.config = config
        self.home = home
        self.cwd = cwd
        self.args = args
        self.merge_stderr = merge_stderr
        self.process: asyncio.subprocess.Process | None = None
        self.owns_cwd = owns_cwd

    async def start(self) -> None:
        self.home.mkdir(parents=True, exist_ok=True)
        environment = {key: value for key in _ENVIRONMENT_KEYS if (value := os.environ.get(key))}
        environment["COPILOT_HOME"] = str(self.home)
        environment["COPILOT_AUTO_UPDATE"] = "false"
        executable = _resolve_copilot_executable(self.args[0], environment)
        try:
            self.process = await asyncio.create_subprocess_exec(
                executable,
                *self.args[1:],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
                if self.merge_stderr
                else asyncio.subprocess.DEVNULL,
                cwd=str(self.cwd),
                env=environment,
                close_fds=os.name != "nt",
            )
        except OSError as exc:
            raise CopilotCliError("could not start pinned Copilot CLI command") from exc

    async def readline(self, timeout: float) -> bytes:
        if self.process is None or self.process.stdout is None:
            raise CopilotCliError("Copilot CLI process is not running")
        try:
            raw = await asyncio.wait_for(self.process.stdout.readline(), timeout)
        except TimeoutError as exc:
            raise CopilotCliTimeout("timed out waiting for Copilot CLI JSONL") from exc
        except asyncio.LimitOverrunError as exc:
            raise CopilotCliProtocolError("Copilot CLI JSONL frame exceeds stream limit") from exc
        if not raw:
            code = await self.process.wait()
            raise CopilotCliError(f"Copilot CLI exited before a response (code {code})")
        if len(raw) > self.config.frame_limit_bytes:
            raise CopilotCliProtocolError("Copilot CLI JSONL frame exceeds configured limit")
        return raw

    async def wait(self, timeout: float) -> int:
        if self.process is None:
            raise CopilotCliError("Copilot CLI process is not running")
        try:
            return await asyncio.wait_for(self.process.wait(), timeout)
        except TimeoutError as exc:
            raise CopilotCliTimeout("timed out waiting for Copilot CLI") from exc

    async def write(self, value: str) -> None:
        if self.process is None or self.process.stdin is None:
            raise CopilotCliError("Copilot CLI process is not running")
        self.process.stdin.write(value.encode("utf-8"))
        await self.process.stdin.drain()

    async def close(self) -> None:
        process = self.process
        self.process = None
        if process is None:
            if self.owns_cwd:
                await _remove_owned_directory(self.cwd)
            return
        if process.stdin is not None:
            process.stdin.close()
            with suppress(BrokenPipeError, ConnectionError):
                await process.stdin.wait_closed()
        if process.returncode is None:
            process.terminate()
            with suppress(TimeoutError):
                await asyncio.wait_for(process.wait(), self.config.cancel_grace_seconds)
        if process.returncode is None:
            process.kill()
            with suppress(TimeoutError):
                await asyncio.wait_for(process.wait(), self.config.cancel_grace_seconds)
        if self.owns_cwd:
            await _remove_owned_directory(self.cwd)


def _resolve_copilot_executable(command: str, environment: Mapping[str, str]) -> str:
    rejected_installing_wrapper = False
    seen: set[str] = set()
    for candidate in _copilot_command_candidates(command, environment):
        identity = os.path.normcase(os.path.abspath(candidate))
        if identity in seen:
            continue
        seen.add(identity)
        path = Path(candidate)
        if _is_installing_copilot_wrapper(path):
            rejected_installing_wrapper = True
            continue
        return str(path)
    if rejected_installing_wrapper:
        raise CopilotCliError(
            "resolved Copilot command only to an interactive installer/update bootstrapper; "
            "configure the installed Copilot CLI executable or npm copilot.cmd"
        )
    raise CopilotCliError("could not resolve pinned Copilot CLI command")


def _copilot_command_candidates(
    command: str, environment: Mapping[str, str]
) -> tuple[str, ...]:
    if os.path.dirname(command):
        resolved = shutil.which(command, path=environment.get("PATH"))
        if resolved is not None:
            return (resolved,)
        explicit = Path(command)
        return (str(explicit.resolve()),) if explicit.is_file() else ()
    candidates: list[str] = []
    for directory in os.get_exec_path(environment):
        resolved = shutil.which(command, path=directory)
        if resolved is not None:
            candidates.append(resolved)
    return tuple(candidates)


def _is_installing_copilot_wrapper(executable: Path) -> bool:
    normalized = executable.as_posix().casefold()
    if "globalstorage/github.copilot-chat/copilotcli/" in normalized:
        return True
    if executable.suffix.casefold() == ".ps1":
        return True
    launchers = [executable]
    companion = executable.with_suffix(".ps1")
    if companion != executable and companion.is_file():
        launchers.append(companion)
    return any(_launcher_contains_install_logic(path) for path in launchers)


def _launcher_contains_install_logic(path: Path) -> bool:
    suffix = path.suffix.casefold()
    if suffix not in {"", ".bat", ".cmd", ".ps1"}:
        return False
    try:
        if path.stat().st_size > _MAX_LAUNCHER_BYTES:
            return True
        raw = path.read_bytes()
    except OSError:
        return True
    if b"\x00" in raw:
        return False
    text = raw.decode("utf-8", errors="replace").casefold()
    return any(marker in text for marker in _INSTALLING_LAUNCHER_MARKERS)


async def _remove_owned_directory(path: Path) -> None:
    """Remove a process-owned temporary directory after Windows releases its cwd handle."""

    for attempt in range(5):
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 4:
                return
            await asyncio.sleep(0.05 * (attempt + 1))


class CopilotCliModelProvider:
    """ModelProvider implementation over the official Copilot CLI JSONL output."""

    def __init__(
        self,
        config: CopilotCliConfig | None = None,
        *,
        image_resolver: ImageArtifactResolver | None = None,
    ) -> None:
        self._config = config or CopilotCliConfig()
        self._image_resolver = image_resolver

    async def invoke(
        self, request: ModelProviderRequest, access: ModelProviderAccess
    ) -> ModelProviderResponse:
        response: ModelProviderResponse | None = None
        async for event in self.stream(request, access):
            if event.kind == "response":
                response = event.response
        if response is None:
            raise CopilotCliProtocolError("Copilot CLI run ended without a model response")
        return response

    async def stream(
        self,
        request: ModelProviderRequest,
        access: ModelProviderAccess,
    ) -> AsyncIterator[ModelProviderStreamEvent]:
        tenant_id = request.tenant_id
        namespace = request.namespace
        engine_ref = _engine_ref(access)
        if not tenant_id:
            raise ValueError("Copilot CLI invocation requires tenantId")
        if not namespace:
            raise ValueError("Copilot CLI invocation requires namespace")
        if not engine_ref:
            raise ValueError("Copilot CLI invocation requires a delegated engineRef")
        if request.continuation is not None or request.continuation_bindings:
            raise ValueError("Copilot CLI does not support native model continuations")
        if request.payload.get("tools"):
            raise ValueError("Copilot CLI native tools are disabled")

        home = derive_copilot_home(
            self._config.state_root,
            tenant_id=tenant_id,
            namespace=namespace,
            engine_ref=engine_ref,
        )
        request_timeout = request.timeout_seconds
        if request_timeout is not None and request_timeout <= 0:
            raise ValueError("Copilot CLI invocation timeout must be positive")
        home.mkdir(parents=True, exist_ok=True)
        with (
            tempfile.TemporaryDirectory(
                prefix="amesh-copilot-cwd-", ignore_cleanup_errors=True
            ) as cwd_name,
            tempfile.TemporaryDirectory(prefix="invocation-", dir=str(home)) as input_name,
        ):
            prompt, attachments = await _build_prompt(
                request.payload,
                resolver=self._image_resolver,
                tenant_id=tenant_id,
                input_dir=Path(input_name),
            )
            args = _invocation_args(
                self._config,
                request.model,
                prompt,
                attachments,
                reasoning_effort=_reasoning_effort(request.payload),
            )
            process = _CopilotProcess(
                self._config,
                home=home,
                cwd=Path(cwd_name),
                args=args,
                owns_cwd=True,
            )
            source_sequence = 1
            response_text: str | None = None
            usage: dict[str, Any] = {}
            emitted_started = False
            emitted_completed = False
            loop = asyncio.get_running_loop()
            deadline = loop.time() + request_timeout if request_timeout is not None else None
            try:
                await process.start()
                while True:
                    if deadline is None:
                        remaining = self._config.timeout_seconds
                    else:
                        remaining = deadline - loop.time()
                        if remaining <= 0:
                            raise CopilotCliTimeout("Copilot CLI invocation timed out")
                        remaining = min(remaining, self._config.timeout_seconds)
                    raw = await process.readline(remaining)
                    message = _decode_jsonl(raw)
                    event_type = message.get("type")
                    data = message.get("data")
                    data_map = data if isinstance(data, dict) else message
                    if event_type in {
                        "progress",
                        "session.start",
                        "session.started",
                        "assistant.turn_start",
                    }:
                        if not emitted_started:
                            yield _progress(
                                "copilot.turn", AgentProgressStatus.STARTED, source_sequence
                            )
                            source_sequence += 1
                            emitted_started = True
                    elif event_type in {"assistant.message_delta", "assistant.message"}:
                        content = _message_content(data_map)
                        if content is not None:
                            response_text = (
                                content
                                if event_type == "assistant.message"
                                else (response_text or "") + content
                            )
                        if event_type == "assistant.message" and not emitted_completed:
                            yield _progress(
                                "copilot.turn", AgentProgressStatus.COMPLETED, source_sequence
                            )
                            source_sequence += 1
                            emitted_completed = True
                    elif event_type in {
                        "usage",
                        "session.shutdown",
                        "session.usage",
                        "assistant.usage",
                    }:
                        usage.update(_usage_from_event(data_map))
                    elif event_type in {
                        "final",
                        "result",
                        "session.task_complete",
                        "session.completed",
                    }:
                        usage.update(_usage_from_event(data_map))
                        result_content = _result_content(data_map)
                        if result_content is not None:
                            response_text = result_content
                        if response_text is None:
                            raise CopilotCliProtocolError(
                                "Copilot CLI result did not contain assistant content"
                            )
                        if not emitted_started:
                            yield _progress(
                                "copilot.turn", AgentProgressStatus.STARTED, source_sequence
                            )
                            source_sequence += 1
                        if not emitted_completed:
                            yield _progress(
                                "copilot.turn", AgentProgressStatus.COMPLETED, source_sequence
                            )
                            emitted_completed = True
                        response_payload = _openai_payload(request.model, response_text, usage)
                        yield ModelProviderStreamEvent.response_event(
                            ModelProviderResponse(payload=response_payload)
                        )
                        return
                    elif event_type in {
                        "tool.execution_start",
                        "tool.execution_complete",
                        "permission.requested",
                        "user_input.requested",
                    }:
                        raise CopilotCliProtocolError(
                            "Copilot CLI emitted a native tool or approval event"
                        )
                    elif event_type in {"error", "session.error", "assistant.error"} or _has_error(
                        data_map
                    ):
                        raise CopilotCliError(
                            _error_detail(data_map) or "Copilot CLI reported an error"
                        )
            except asyncio.CancelledError:
                raise
            finally:
                await process.close()


class CopilotAccountManager:
    """Account lifecycle adapter using the documented Copilot CLI auth commands."""

    def __init__(
        self,
        config: CopilotCliConfig | None = None,
        *,
        engine_ref: str,
        namespace: str = "default",
    ) -> None:
        self._config = config or CopilotCliConfig()
        self._engine_ref = engine_ref
        self._namespace = namespace
        self._pending: dict[str, tuple[str, _CopilotProcess]] = {}
        self._authenticated: set[str] = set()
        self._logged_out: set[str] = set()

    def _home(self, tenant_id: str) -> Path:
        return derive_copilot_home(
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
    ) -> EngineAccountStatus:
        del refresh_token, include_rate_limits, include_usage
        # Copilot has no documented non-interactive account-read API.  Authentication readiness
        # is intentionally limited to this process's login completion evidence; no token file or
        # keyring value is inspected or returned.  A fresh manager therefore reports unknown.
        pending = self._pending.get(tenant_id)
        child = pending[1].process if pending is not None else None
        if pending is not None and child is not None and child.returncode is not None:
            success = child.returncode == 0
            await self._release(tenant_id)
            if success:
                self._authenticated.add(tenant_id)
            else:
                self._authenticated.discard(tenant_id)
        if tenant_id in self._authenticated:
            return EngineAccountStatus(authenticated=True, authMode="github-oauth")
        if tenant_id in self._logged_out:
            return EngineAccountStatus(authenticated=False, authMode="github-oauth")
        return EngineAccountStatus(authenticated=None, authMode="github-oauth", actionRequired=True)

    async def login_start(self, tenant_id: str, *, mode: str = "browser") -> EngineLoginStart:
        option = {
            "browser": "--web-flow",
            "device": "--device-code",
            "device-code": "--device-code",
        }.get(mode)
        if option is None:
            raise ValueError("Copilot login mode must be browser or device")
        await self._release(tenant_id)
        cwd = Path(tempfile.mkdtemp(prefix="amesh-copilot-login-cwd-"))
        args = (*self._config.command, "login", option)
        process = _CopilotProcess(
            self._config,
            home=self._home(tenant_id),
            cwd=cwd,
            args=args,
            merge_stderr=True,
            owns_cwd=True,
        )
        try:
            await process.start()
            login_id = uuid4().hex
            challenge = await _read_login_challenge(
                process,
                self._config.timeout_seconds,
                self._config.github_host,
            )
        except BaseException:
            await process.close()
            raise
        self._pending[tenant_id] = (login_id, process)
        return EngineLoginStart(
            kind="github_device_code" if option == "--device-code" else "github_browser",
            loginId=login_id,
            authUrl=challenge.get("authUrl"),
            verificationUrl=challenge.get("verificationUrl"),
            userCode=challenge.get("userCode"),
            actionRequired=True,
        )

    async def wait_login(
        self, tenant_id: str, login_id: str, *, timeout_seconds: float | None = None
    ) -> bool:
        pending = self._pending.get(tenant_id)
        if pending is None or pending[0] != login_id:
            raise ValueError("no pending Copilot login exists for tenant")
        process = pending[1]
        try:
            code = await process.wait(timeout_seconds or self._config.timeout_seconds)
            success = code == 0
            if success:
                self._authenticated.add(tenant_id)
            return success
        finally:
            await self._release(tenant_id)

    async def logout(self, tenant_id: str) -> None:
        await self._release(tenant_id)
        cwd = Path(tempfile.mkdtemp(prefix="amesh-copilot-logout-cwd-"))
        process = _CopilotProcess(
            self._config,
            home=self._home(tenant_id),
            cwd=cwd,
            args=_interactive_args(self._config),
            merge_stderr=True,
            owns_cwd=True,
        )
        try:
            await process.start()
            await process.write("/logout\n/exit\n")
            code = await process.wait(self._config.timeout_seconds)
            if code != 0:
                raise CopilotCliError(f"Copilot logout failed (code {code})")
        finally:
            await process.close()
        self._authenticated.discard(tenant_id)
        self._logged_out.add(tenant_id)

    async def close(self) -> None:
        for tenant_id in tuple(self._pending):
            await self._release(tenant_id)

    async def _release(self, tenant_id: str) -> None:
        pending = self._pending.pop(tenant_id, None)
        if pending is not None:
            await pending[1].close()


def _invocation_args(
    config: CopilotCliConfig,
    model: str,
    prompt: str,
    attachments: tuple[Path, ...] = (),
    reasoning_effort: str | None = None,
) -> tuple[str, ...]:
    args = [
        *config.command,
        "-p",
        prompt,
        "--output-format=json",
        f"--model={model}",
        "--no-custom-instructions",
        "--no-remote",
        "--no-remote-export",
        "--no-auto-update",
        "--no-bash-env",
        "--no-ask-user",
        "--disable-builtin-mcps",
        "--available-tools=",
        "--excluded-tools=*",
        "--deny-tool=*",
        "--disallow-temp-dir",
        "--no-color",
        "--no-banner",
        "--no-experimental",
    ]
    for attachment in attachments:
        args.extend(("--attachment", str(attachment)))
    if reasoning_effort is not None:
        args.append(f"--reasoning-effort={reasoning_effort}")
    return tuple(args)


def _reasoning_effort(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("reasoning_effort", payload.get("reasoningEffort"))
    if value is None:
        return None
    if not isinstance(value, str) or value not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Copilot CLI reasoning effort must be low, medium, high, xhigh, or max")
    return value


def _interactive_args(config: CopilotCliConfig) -> tuple[str, ...]:
    """Build a least-privilege interactive command for the documented ``/logout`` command."""

    return (
        *config.command,
        "--no-custom-instructions",
        "--no-remote",
        "--no-remote-export",
        "--no-auto-update",
        "--no-bash-env",
        "--no-ask-user",
        "--disable-builtin-mcps",
        "--available-tools=",
        "--excluded-tools=*",
        "--deny-tool=*",
        "--disallow-temp-dir",
        "--no-color",
        "--no-banner",
        "--no-experimental",
    )


async def _build_prompt(
    payload: Mapping[str, Any],
    *,
    resolver: ImageArtifactResolver | None,
    tenant_id: str,
    input_dir: Path,
) -> tuple[str, tuple[Path, ...]]:
    attachments: list[Path] = []
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        raw_input = payload.get("input", payload.get("prompt"))
        if not isinstance(raw_input, str) or not raw_input.strip():
            raise ValueError("Copilot CLI request requires non-blank messages or input")
        prompt = raw_input
    else:
        chunks: list[str] = []
        for message in messages:
            if not isinstance(message, dict):
                raise ValueError("Copilot CLI messages must be objects")
            role = message.get("role", "user")
            if not isinstance(role, str) or not role:
                role = "user"
            content = await _prompt_content(
                message.get("content", ""),
                resolver=resolver,
                tenant_id=tenant_id,
                input_dir=input_dir,
                attachments=attachments,
            )
            if content:
                chunks.append(f"[{role}]\n{content}")
        if not chunks:
            raise ValueError("Copilot CLI request contains no usable input")
        prompt = "\n\n".join(chunks)
    response_format = payload.get("response_format", payload.get("responseFormat"))
    if isinstance(response_format, dict) and response_format.get("type") == "json_schema":
        schema = response_format.get("json_schema", response_format.get("jsonSchema"))
        if isinstance(schema, dict) and isinstance(schema.get("schema"), dict):
            prompt += (
                "\n\nReturn exactly one JSON object and no surrounding prose or Markdown. "
                "The object must validate against this JSON Schema: "
                + json.dumps(schema["schema"], ensure_ascii=False, separators=(",", ":"))
            )
    return prompt, tuple(attachments)


async def _prompt_content(
    content: Any,
    *,
    resolver: ImageArtifactResolver | None,
    tenant_id: str,
    input_dir: Path,
    attachments: list[Path],
) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return json.dumps(content, ensure_ascii=False, separators=(",", ":"))
    parts: list[str] = []
    for index, part in enumerate(content):
        if not isinstance(part, dict):
            raise ValueError("Copilot CLI content parts must be objects")
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            parts.append(part["text"])
            continue
        if part.get("type") not in {"image_ref", "image"}:
            raise ValueError("Copilot CLI content supports text and governed image references")
        raw_image = part.get("image")
        if raw_image is None and isinstance(part.get("image_ref"), dict):
            raw_image = part["image_ref"]
        if resolver is None or not isinstance(raw_image, dict):
            raise ValueError("Copilot CLI image input requires a tenant-scoped image resolver")
        image = ImageArtifactRef.model_validate(raw_image)
        image_bytes = await resolver.resolve_image(image, tenant_id=tenant_id)
        if not isinstance(image_bytes, bytes) or not image_bytes:
            raise ValueError("image resolver must return non-empty bytes")
        media_type = image.artifact.media_type
        if not isinstance(media_type, str):
            raise ValueError("image artifact must declare a media type")
        inspection = inspect_image_bytes(image_bytes, declared_media_type=media_type)
        build_image_artifact_ref(
            image.artifact,
            inspection,
            filename=image.display.filename,
            alt_text=image.display.alt_text,
        )
        suffix = inspection.media_type.rsplit("/", 1)[-1]
        target = input_dir / f"image-{index:04d}.{suffix}"
        target.write_bytes(image_bytes)
        parts.append(f"[Attached image: {target}]")
        attachments.append(target)
    return "\n".join(parts)


def _decode_jsonl(raw: bytes) -> dict[str, Any]:
    try:
        decoded = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CopilotCliProtocolError("Copilot CLI emitted invalid JSONL") from exc
    if not isinstance(decoded, dict):
        raise CopilotCliProtocolError("Copilot CLI JSONL message must be an object")
    return decoded


def _message_content(data: Mapping[str, Any]) -> str | None:
    value = data.get("content", data.get("text", data.get("deltaContent")))
    if isinstance(value, str):
        return value
    return None


def _result_content(data: Mapping[str, Any]) -> str | None:
    value = _message_content(data)
    if value is not None:
        return value
    result = data.get("result")
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    return None


def _usage_from_event(data: Mapping[str, Any]) -> dict[str, Any]:
    usage: dict[str, Any] = {}
    raw = data.get("usage")
    if isinstance(raw, dict):
        _copy_usage_fields(usage, raw)
    _copy_usage_fields(usage, data)
    metrics = data.get("modelMetrics")
    if isinstance(metrics, dict):
        for model_metrics in metrics.values():
            if isinstance(model_metrics, dict):
                nested = model_metrics.get("usage")
                if isinstance(nested, dict):
                    _copy_usage_fields(usage, nested)
    return usage


def _copy_usage_fields(target: dict[str, Any], source: Mapping[str, Any]) -> None:
    aliases = {
        "input_tokens": ("input_tokens", "inputTokens", "prompt_tokens", "promptTokens"),
        "output_tokens": ("output_tokens", "outputTokens", "completion_tokens", "completionTokens"),
        "total_tokens": ("total_tokens", "totalTokens"),
        "reasoning_tokens": ("reasoning_tokens", "reasoningTokens"),
        "cache_read_tokens": ("cache_read_tokens", "cacheReadTokens", "cacheReadInputTokens"),
        "cache_write_tokens": (
            "cache_write_tokens",
            "cacheWriteTokens",
            "cacheCreationInputTokens",
        ),
        "premium_requests": ("premium_requests", "premiumRequests"),
        "ai_credits": ("ai_credits", "aiCredits", "nanoAiu"),
    }
    for target_name, names in aliases.items():
        for name in names:
            value = source.get(name)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                target[target_name] = value
                break
            if isinstance(value, float) and value >= 0 and target_name == "ai_credits":
                target[target_name] = value
                break
    if "total_tokens" not in target and {"input_tokens", "output_tokens"} <= target.keys():
        target["total_tokens"] = target["input_tokens"] + target["output_tokens"]


def _openai_payload(model: str, content: str, usage: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": f"chatcmpl-copilot-{uuid4().hex}",
        "object": "chat.completion",
        "created": int(time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }
    payload["usage"] = dict(usage)
    return payload


def _progress(
    activity_id: str, status: AgentProgressStatus, source_sequence: int
) -> ModelProviderStreamEvent:
    return ModelProviderStreamEvent.progress_event(
        ModelProviderProgressDelta(
            activity=AgentProgressActivity.MODEL,
            status=status,
            activityId=activity_id,
            sourceSequence=source_sequence,
            detail=AgentStatusDetail(code="copilot.processing", label="Copilot is processing"),
        )
    )


async def _read_login_challenge(
    process: _CopilotProcess,
    timeout: float,
    github_host: str,
) -> dict[str, str | None]:
    started = time()
    while time() - started < timeout:
        raw = await process.readline(max(0.01, timeout - (time() - started)))
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            continue
        try:
            message = json.loads(text)
        except json.JSONDecodeError:
            message = None
        if isinstance(message, dict):
            data = message.get("data", message)
            if isinstance(data, dict):
                challenge = _challenge_from_mapping(data, github_host)
                if any(challenge.values()):
                    return challenge
        challenge = _challenge_from_text(text, github_host)
        if any(challenge.values()):
            return challenge
    raise CopilotCliTimeout("Copilot login did not return a browser or device challenge")


def _challenge_from_mapping(data: Mapping[str, Any], github_host: str) -> dict[str, str | None]:
    auth = data.get("authUrl", data.get("url"))
    verification = data.get("verificationUrl", data.get("deviceUrl"))
    code = data.get("userCode", data.get("deviceCode", data.get("code")))
    return {
        "authUrl": _safe_auth_url(auth, github_host) if isinstance(auth, str) else None,
        "verificationUrl": _safe_auth_url(verification, github_host)
        if isinstance(verification, str)
        else None,
        "userCode": code
        if isinstance(code, str) and _DEVICE_CODE_RE.fullmatch(code.strip())
        else None,
    }


def _challenge_from_text(text: str, github_host: str) -> dict[str, str | None]:
    allowed_host = (urlsplit(github_host).hostname or "").lower().rstrip(".")
    urls = []
    for match in _URL_RE.findall(text):
        candidate = match.rstrip(".,)")
        if (urlsplit(candidate).hostname or "").lower().rstrip(".") != allowed_host:
            continue
        urls.append(_safe_auth_url(candidate, github_host))
    device_url = next((url for url in urls if "/device" in url), None)
    auth_url = next((url for url in urls if url != device_url), None)
    code_match = _DEVICE_CODE_RE.search(text)
    return {
        "authUrl": auth_url,
        "verificationUrl": device_url,
        "userCode": code_match.group(0) if code_match else None,
    }


def _safe_auth_url(value: str, github_host: str = "https://github.com") -> str:
    if not isinstance(value, str) or len(value) > 4096:
        raise CopilotCliProtocolError("Copilot login returned an invalid browser URL")
    parsed = urlsplit(value)
    allowed = urlsplit(github_host)
    host = (parsed.hostname or "").lower().rstrip(".")
    allowed_host = (allowed.hostname or "").lower().rstrip(".")
    if parsed.scheme != "https" or not allowed_host or host != allowed_host:
        raise CopilotCliProtocolError("Copilot login returned an unsafe browser URL")
    return value


def _engine_ref(access: ModelProviderAccess) -> str | None:
    return access.engine_ref if isinstance(access, ModelEngineAccess) else None


def _has_error(data: Mapping[str, Any]) -> bool:
    return isinstance(data.get("error"), (str, dict))


def _error_detail(data: Mapping[str, Any]) -> str | None:
    value = data.get("error", data.get("message"))
    if isinstance(value, dict):
        value = value.get("message", value.get("detail"))
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return None
    return " ".join(str(value).split())[:_MAX_DIAGNOSTIC_CHARS] or None


__all__ = [
    "COPILOT_CLI_ADAPTER_ID",
    "COPILOT_CLI_ADAPTER_REVISION",
    "CopilotAccountManager",
    "CopilotCliConfig",
    "CopilotCliError",
    "CopilotCliModelProvider",
    "CopilotCliProtocolError",
    "CopilotCliTimeout",
    "derive_copilot_home",
]
