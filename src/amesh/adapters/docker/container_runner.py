from __future__ import annotations

import asyncio
import hashlib
import io
import math
import shutil
import tarfile
from collections.abc import Awaitable, Callable, Iterable, Iterator, Mapping
from contextlib import suppress
from dataclasses import dataclass
from itertools import count
from pathlib import Path, PurePosixPath
from time import perf_counter
from typing import Any, cast

import docker
from docker.client import DockerClient
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from docker.models.volumes import Volume
from docker.types import Ulimit
from pydantic import ValidationError

from amesh.ports import (
    DockerContainerResourceLimits,
    DockerContainerRunnerExtension,
    DockerImagePolicy,
    RunnerCapabilities,
    RunnerDiagnostics,
    RunnerId,
    RunnerLog,
    RunnerLogStream,
    RunnerMetrics,
    RunnerNetworkAccess,
    RunnerOutputRedactor,
    RunnerReconciliationResult,
    RunnerRequest,
    RunnerResult,
    RunnerStatus,
    StaleRunnerAttemptError,
    TaskRunner,
    UnsupportedRunnerRequest,
    redact_runner_text,
    validate_runner_request,
)

from .image_policy import (
    CommandImagePolicyVerifier,
    ImagePolicyVerifier,
    resolve_and_verify_image,
)

_WORKSPACE = "/workspace"
_OWNER_LABEL = "amesh.runner"
_ATTEMPT_LABEL = "amesh.attempt-id"
_FENCE_LABEL = "amesh.fencing-token"
_VOLUME_LABEL = "amesh.workspace-volume"

_CAPABILITIES = RunnerCapabilities(
    runner=RunnerId.DOCKER,
    acceptsCommand=True,
    requiresCommand=True,
    acceptsImage=True,
    requiresImage=True,
    supportsFiles=True,
    supportsWorkingDirectory=True,
    supportsStandardInput=False,
    supportsResources=True,
    networkAccess=(RunnerNetworkAccess.INHERIT, RunnerNetworkAccess.NONE),
    supportsSecurityPolicy=True,
    supportsScopedCredentials=True,
    supportsReconciliation=True,
    extensionType=RunnerId.DOCKER,
    cancellationEscalation=("stop", "wait-grace", "kill"),
    platforms=("docker-engine", "rootless-docker", "remote-docker"),
    features=(
        "immutable-image-resolution",
        "archive-workspace-transfer",
        "ordered-stdout-stderr",
        "resource-and-security-controls",
        "image-policy-verification",
        "owned-resource-cleanup",
    ),
)

DockerRunnerLogSink = Callable[[RunnerLog], Awaitable[None]]


@dataclass
class _ActiveContainer:
    container: Container
    volume: Volume
    fencing_token: int
    cancel_grace_seconds: float
    is_cancel_requested: bool = False
    output_limit_exceeded: bool = False


class DockerContainerRunner(TaskRunner):
    """Runs one fenced task attempt through a Docker-compatible Engine API."""

    CAPABILITIES = _CAPABILITIES

    def __init__(
        self,
        *,
        client: DockerClient | None = None,
        endpoint: str | None = None,
        image_policy: DockerImagePolicy | None = None,
        image_verifier: ImagePolicyVerifier | None = None,
        signature_command: tuple[str, ...] = (),
        vulnerability_command: tuple[str, ...] = (),
        log_sink: DockerRunnerLogSink | None = None,
    ) -> None:
        self._client = client or (
            DockerClient(base_url=endpoint, version="auto") if endpoint else docker.from_env()
        )
        self._image_policy = image_policy or DockerImagePolicy()
        self._image_verifier = image_verifier or CommandImagePolicyVerifier(
            signature_command=signature_command,
            vulnerability_command=vulnerability_command,
        )
        self._log_sink = log_sink
        self._active: dict[str, _ActiveContainer] = {}
        self._lock = asyncio.Lock()

    @property
    def capabilities(self) -> RunnerCapabilities:
        return self.CAPABILITIES

    def close(self) -> None:
        self._client.close()

    async def run(self, request: RunnerRequest) -> RunnerResult:
        validate_runner_request(self.capabilities, request)
        extension, limits, auth_config, environment = _validate_docker_request(request)
        assert request.image is not None
        started_at = perf_counter()
        decision = await resolve_and_verify_image(
            self._client,
            request.image,
            extension,
            self._image_policy,
            self._image_verifier,
            auth_config=auth_config,
        )
        name = _resource_name(request.attempt_id)
        labels = {
            _OWNER_LABEL: RunnerId.DOCKER.value,
            _ATTEMPT_LABEL: request.attempt_id,
            _FENCE_LABEL: str(request.fencing_token),
            "amesh.tenant-id": request.tenant_id,
            "amesh.execution-id": request.execution_id,
            "amesh.task-run-id": request.task_run_id,
        }
        volume: Volume | None = None
        container: Container | None = None
        logs: tuple[RunnerLog, ...] = ()
        stdout = ""
        stderr = ""
        status = RunnerStatus.FAILED
        exit_code: int | None = None
        is_timed_out = False
        diagnostics_reason: str | None = None
        diagnostics_message: str | None = None
        state: dict[str, Any] = {}
        stats: dict[str, Any] = {}
        active: _ActiveContainer | None = None
        try:
            created_volume = await asyncio.to_thread(
                self._client.volumes.create,
                name=f"{name}-workspace",
                labels={**labels, _VOLUME_LABEL: "true"},
            )
            volume = created_volume
            created_container = await asyncio.to_thread(
                self._client.containers.create,
                decision.resolved,
                request.command,
                name=name,
                detach=True,
                environment=environment,
                working_dir=_WORKSPACE,
                volumes={volume.name: {"bind": _WORKSPACE, "mode": "rw"}},
                labels=labels,
                network_disabled=request.network_policy.access is RunnerNetworkAccess.NONE,
                network_mode=(
                    "none" if request.network_policy.access is RunnerNetworkAccess.NONE else None
                ),
                privileged=request.security_policy.privileged,
                read_only=request.security_policy.read_only_root_filesystem,
                user=(
                    str(request.security_policy.run_as_user)
                    if request.security_policy.run_as_user is not None
                    else None
                ),
                cap_add=list(request.security_policy.capability_add) or None,
                cap_drop=list(request.security_policy.capability_drop) or None,
                security_opt=(
                    ["no-new-privileges:true"]
                    if request.security_policy.no_new_privileges
                    else None
                ),
                nano_cpus=int(limits.cpus * 1_000_000_000) if limits.cpus else None,
                mem_limit=limits.memory_bytes,
                pids_limit=limits.processes,
                ulimits=(
                    [Ulimit(name="nofile", soft=limits.open_files, hard=limits.open_files)]
                    if limits.open_files is not None
                    else None
                ),
                runtime=extension.runtime,
                platform=extension.platform,
            )
            container = created_container
            if request.working_directory is not None:
                archive = _workspace_archive(Path(request.working_directory))
                await asyncio.to_thread(created_container.put_archive, _WORKSPACE, archive)
            active = _ActiveContainer(
                container=created_container,
                volume=created_volume,
                fencing_token=request.fencing_token,
                cancel_grace_seconds=request.cancel_grace_seconds,
            )
            async with self._lock:
                if request.attempt_id in self._active:
                    raise RuntimeError(f"attempt {request.attempt_id!r} is already running")
                self._active[request.attempt_id] = active
            log_stream = await asyncio.to_thread(
                created_container.attach,
                stream=True,
                logs=True,
                stdout=True,
                stderr=True,
                demux=True,
            )
            await asyncio.to_thread(created_container.start)
            log_task = asyncio.create_task(
                _capture_logs(
                    cast(Iterator[tuple[bytes | None, bytes | None] | bytes], log_stream),
                    self._log_sink,
                    tuple(
                        credential.value.get_secret_value() for credential in request.credentials
                    ),
                    request.output_limit_bytes,
                    on_limit_exceeded=lambda: _mark_output_limit_exceeded(active),
                )
            )
            wait_task = asyncio.create_task(asyncio.to_thread(created_container.wait))
            if request.timeout_seconds is None:
                wait_result = await wait_task
            else:
                done, _ = await asyncio.wait({wait_task}, timeout=request.timeout_seconds)
                if wait_task not in done:
                    is_timed_out = True
                    await _stop_container(created_container, request.cancel_grace_seconds)
                wait_result = await wait_task
            stdout, stderr, logs = await log_task
            exit_code = int(wait_result.get("StatusCode", 1))
            await asyncio.to_thread(created_container.reload)
            state = cast(dict[str, Any], created_container.attrs.get("State", {}))
            with suppress(APIError):
                stats = cast(
                    dict[str, Any],
                    await asyncio.to_thread(created_container.stats, stream=False, one_shot=True),
                )
            if request.working_directory is not None:
                archive_stream, _ = await asyncio.to_thread(
                    created_container.get_archive, _WORKSPACE
                )
                await asyncio.to_thread(
                    _restore_workspace,
                    Path(request.working_directory),
                    cast(Iterable[bytes], archive_stream),
                )
            if active.is_cancel_requested:
                status = RunnerStatus.CANCELLED
            elif is_timed_out:
                status = RunnerStatus.TIMED_OUT
            elif active.output_limit_exceeded:
                status = RunnerStatus.FAILED
            elif exit_code == 0:
                status = RunnerStatus.SUCCESS
            else:
                status = RunnerStatus.FAILED
            if bool(state.get("OOMKilled")):
                diagnostics_reason = "OOM_KILLED"
        except APIError as exc:
            diagnostics_reason = type(exc).__name__
            diagnostics_message = str(exc)
        finally:
            if active is not None:
                async with self._lock:
                    current = self._active.get(request.attempt_id)
                    if current is active:
                        del self._active[request.attempt_id]
            await _remove_owned_resources(container, volume)

        signal_number = exit_code - 128 if exit_code is not None and 128 < exit_code < 193 else None
        return RunnerResult(
            runner=RunnerId.DOCKER,
            exit_code=exit_code,
            signal=signal_number,
            status=status,
            logs=logs,
            metrics=_runner_metrics(stats, perf_counter() - started_at),
            outputs={"stdout": stdout, "stderr": stderr},
            diagnostics=RunnerDiagnostics(
                runner=RunnerId.DOCKER,
                externalId=container.id if container is not None else None,
                reason=diagnostics_reason,
                message=diagnostics_message,
                details={
                    "imageRequested": decision.requested,
                    "imageResolved": decision.resolved,
                    "registry": decision.registry,
                    "signatureVerified": decision.signature_verified,
                    "vulnerabilityPolicyPassed": decision.vulnerability_policy_passed,
                    "oomKilled": bool(state.get("OOMKilled")),
                    "runtimeError": state.get("Error") or None,
                    "outputLimitExceeded": bool(
                        active is not None and active.output_limit_exceeded
                    ),
                    "outputLimitBytes": request.output_limit_bytes,
                },
            ),
        )

    async def cancel(self, attempt_id: str, fencing_token: int) -> None:
        async with self._lock:
            active = self._active.get(attempt_id)
            if active is None or active.fencing_token != fencing_token:
                raise StaleRunnerAttemptError(
                    f"attempt {attempt_id!r} is inactive or fenced by a newer token"
                )
            active.is_cancel_requested = True
        await _stop_container(active.container, active.cancel_grace_seconds)

    async def reconcile(
        self,
        active_attempts: Mapping[str, int],
    ) -> RunnerReconciliationResult:
        cleaned: set[str] = set()
        retained: set[str] = set()
        containers = await asyncio.to_thread(
            self._client.containers.list,
            all=True,
            filters={"label": f"{_OWNER_LABEL}={RunnerId.DOCKER.value}"},
        )
        for container in containers:
            labels = container.labels
            attempt_id = labels.get(_ATTEMPT_LABEL, "")
            fence = labels.get(_FENCE_LABEL, "")
            if attempt_id and str(active_attempts.get(attempt_id)) == fence:
                retained.add(attempt_id)
                continue
            if attempt_id:
                cleaned.add(attempt_id)
            with suppress(APIError, NotFound):
                await asyncio.to_thread(container.remove, force=True, v=True)
        volumes = await asyncio.to_thread(
            self._client.volumes.list,
            filters={
                "label": [
                    f"{_OWNER_LABEL}={RunnerId.DOCKER.value}",
                    f"{_VOLUME_LABEL}=true",
                ]
            },
        )
        for volume in volumes:
            attempt_id = volume.attrs.get("Labels", {}).get(_ATTEMPT_LABEL, "")
            fence = volume.attrs.get("Labels", {}).get(_FENCE_LABEL, "")
            if attempt_id and str(active_attempts.get(attempt_id)) == fence:
                retained.add(attempt_id)
                continue
            if attempt_id:
                cleaned.add(attempt_id)
            with suppress(APIError, NotFound):
                await asyncio.to_thread(volume.remove, force=True)
        return RunnerReconciliationResult(
            runner=RunnerId.DOCKER,
            cleanedAttempts=tuple(sorted(cleaned)),
            retainedAttempts=tuple(sorted(retained)),
        )


def _validate_docker_request(
    request: RunnerRequest,
) -> tuple[
    DockerContainerRunnerExtension,
    DockerContainerResourceLimits,
    dict[str, str] | None,
    dict[str, str],
]:
    extension = (
        request.extension
        if isinstance(request.extension, DockerContainerRunnerExtension)
        else DockerContainerRunnerExtension(type=RunnerId.DOCKER)
    )
    try:
        limits = DockerContainerResourceLimits.model_validate(request.resource_limits)
    except ValidationError as exc:
        fields = sorted({".".join(str(item) for item in error["loc"]) for error in exc.errors()})
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            ("resource limits " + ", ".join(fields),),
        ) from exc
    values = {
        item.environment_variable: item.value.get_secret_value() for item in request.credentials
    }
    registry_names = {
        item
        for item in (
            extension.registry_username_variable,
            extension.registry_password_variable,
        )
        if item is not None
    }
    missing = registry_names.difference(values)
    if missing:
        raise UnsupportedRunnerRequest(
            RunnerId.DOCKER,
            ("registry credential variables are unavailable: " + ", ".join(sorted(missing)),),
        )
    auth_config = (
        {
            "username": values[cast(str, extension.registry_username_variable)],
            "password": values[cast(str, extension.registry_password_variable)],
        }
        if registry_names
        else None
    )
    environment = dict(request.environment)
    environment.update(
        {name: value for name, value in values.items() if name not in registry_names}
    )
    return extension, limits, auth_config, environment


async def _capture_logs(
    iterator: Iterator[tuple[bytes | None, bytes | None] | bytes],
    sink: DockerRunnerLogSink | None,
    secret_values: tuple[str, ...],
    output_limit_bytes: int | None = None,
    on_limit_exceeded: Callable[[], Awaitable[None]] | None = None,
) -> tuple[str, str, tuple[RunnerLog, ...]]:
    sequence = count()
    logs: list[RunnerLog] = []
    stdout = bytearray()
    stderr = bytearray()
    redactors = {
        stream: RunnerOutputRedactor(secret_values)
        for stream in (RunnerLogStream.STDOUT, RunnerLogStream.STDERR)
    }
    captured_bytes = 0
    limit_triggered = False
    limit_task: asyncio.Future[None] | None = None
    while True:
        chunk = await asyncio.to_thread(_next_log_chunk, iterator)
        if chunk is None:
            break
        pairs = (
            ((RunnerLogStream.STDOUT, chunk),)
            if isinstance(chunk, bytes)
            else (
                (RunnerLogStream.STDOUT, chunk[0]),
                (RunnerLogStream.STDERR, chunk[1]),
            )
        )
        for log_stream, value in pairs:
            if not value:
                continue
            if output_limit_bytes is None:
                retained = value
            else:
                remaining = max(output_limit_bytes - captured_bytes, 0)
                retained = value[:remaining]
                captured_bytes += len(value)
                if len(value) > remaining and not limit_triggered:
                    limit_triggered = True
                    if on_limit_exceeded is not None:
                        # Keep draining the attach stream while Docker stops the container. Pausing
                        # the stream here can back-pressure the daemon and deadlock its stop request.
                        limit_task = asyncio.ensure_future(on_limit_exceeded())
            target = stdout if log_stream is RunnerLogStream.STDOUT else stderr
            target.extend(retained)
            message = redactors[log_stream].feed(retained.decode(errors="replace"))
            if message:
                entry = RunnerLog(
                    sequence=next(sequence),
                    stream=log_stream,
                    level="INFO" if log_stream is RunnerLogStream.STDOUT else "ERROR",
                    message=message,
                )
                logs.append(entry)
                if sink is not None:
                    await sink(entry)
    if limit_task is not None:
        await limit_task
    for log_stream, redactor in redactors.items():
        message = redactor.flush()
        if message:
            entry = RunnerLog(
                sequence=next(sequence),
                stream=log_stream,
                level="INFO" if log_stream is RunnerLogStream.STDOUT else "ERROR",
                message=message,
            )
            logs.append(entry)
            if sink is not None:
                await sink(entry)
    return (
        redact_runner_text(stdout.decode(errors="replace"), secret_values),
        redact_runner_text(stderr.decode(errors="replace"), secret_values),
        tuple(logs),
    )


async def _mark_output_limit_exceeded(active: _ActiveContainer) -> None:
    if active.output_limit_exceeded:
        return
    active.output_limit_exceeded = True
    await _stop_container(active.container, active.cancel_grace_seconds)


def _next_log_chunk(
    iterator: Iterator[tuple[bytes | None, bytes | None] | bytes],
) -> tuple[bytes | None, bytes | None] | bytes | None:
    try:
        return next(iterator)
    except StopIteration:
        return None


async def _stop_container(container: Container, grace_seconds: float) -> None:
    try:
        await asyncio.to_thread(container.stop, timeout=max(0, math.ceil(grace_seconds)))
    except NotFound:
        return
    except APIError:
        with suppress(APIError, NotFound):
            await asyncio.to_thread(container.kill)


async def _remove_owned_resources(
    container: Container | None,
    volume: Volume | None,
) -> None:
    if container is not None:
        with suppress(APIError, NotFound):
            await asyncio.to_thread(container.remove, force=True, v=True)
    if volume is not None:
        with suppress(APIError, NotFound):
            await asyncio.to_thread(volume.remove, force=True)


def _resource_name(attempt_id: str) -> str:
    digest = hashlib.sha256(attempt_id.encode()).hexdigest()[:20]
    return f"amesh-task-{digest}"


def _workspace_archive(root: Path) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    raise UnsupportedRunnerRequest(
                        RunnerId.DOCKER,
                        (f"workspace contains symlink {path.relative_to(root).as_posix()!r}",),
                    )
                archive.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)
    return buffer.getvalue()


def _restore_workspace(root: Path, chunks: Iterable[bytes]) -> None:
    payload = io.BytesIO(b"".join(chunks))
    with tarfile.open(fileobj=payload, mode="r:*") as archive:
        members = archive.getmembers()
        validated = [(_archive_relative_path(member), member) for member in members]
        for path in root.iterdir():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
        for relative, member in validated:
            if relative is None:
                continue
            target = root.joinpath(*relative.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"container archive member {member.name!r} has no content")
            with target.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)


def _archive_relative_path(member: tarfile.TarInfo) -> PurePosixPath | None:
    path = PurePosixPath(member.name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"container archive path escapes workspace: {member.name!r}")
    if member.issym() or member.islnk() or member.isdev():
        raise ValueError(f"container archive member type is prohibited: {member.name!r}")
    parts = path.parts[1:] if path.parts and path.parts[0] == "workspace" else path.parts
    if not parts:
        return None
    return PurePosixPath(*parts)


def _runner_metrics(stats: dict[str, Any], duration_seconds: float) -> RunnerMetrics:
    cpu_stats = stats.get("cpu_stats", {})
    cpu_usage = cpu_stats.get("cpu_usage", {}) if isinstance(cpu_stats, dict) else {}
    memory_stats = stats.get("memory_stats", {})
    cpu_total = cpu_usage.get("total_usage") if isinstance(cpu_usage, dict) else None
    peak_memory = None
    if isinstance(memory_stats, dict):
        peak_memory = memory_stats.get("max_usage") or memory_stats.get("usage")
    return RunnerMetrics(
        duration_seconds=duration_seconds,
        cpu_seconds=float(cpu_total) / 1_000_000_000
        if isinstance(cpu_total, int | float)
        else None,
        peak_memory_bytes=int(peak_memory) if isinstance(peak_memory, int) else None,
    )
