from __future__ import annotations

import base64
import io
import shutil
import tarfile
from collections.abc import Callable
from pathlib import Path, PurePosixPath

from kubernetes import client as sync_client  # type: ignore[import-untyped]
from kubernetes.stream import stream  # type: ignore[import-untyped]

from amesh.ports import RunnerId, UnsupportedRunnerRequest


def upload_workspace(
    core: sync_client.CoreV1Api,
    *,
    namespace: str,
    pod_name: str,
    root: Path,
) -> None:
    payload = base64.b64encode(workspace_archive(root)).decode("ascii")
    command = [
        "sh",
        "-c",
        "base64 -d > /control/input.tar && touch /control/input-ready",
    ]
    _exec(core, namespace, pod_name, "workspace-init", command, stdin=payload)


def download_workspace(
    core: sync_client.CoreV1Api,
    *,
    namespace: str,
    pod_name: str,
    root: Path,
) -> None:
    encoded = _exec(
        core,
        namespace,
        pod_name,
        "workspace-transfer",
        ["sh", "-c", "tar -cf - -C /workspace . | base64"],
    )
    restore_workspace(root, base64.b64decode(encoded))


def release_transfer_sidecar(
    core: sync_client.CoreV1Api,
    *,
    namespace: str,
    pod_name: str,
) -> None:
    _exec(
        core,
        namespace,
        pod_name,
        "workspace-transfer",
        ["sh", "-c", "touch /control/release"],
    )


def workspace_archive(root: Path) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    raise UnsupportedRunnerRequest(
                        RunnerId.KUBERNETES,
                        (f"workspace contains symlink {path.relative_to(root).as_posix()!r}",),
                    )
                archive.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)
    return buffer.getvalue()


def restore_workspace(root: Path, payload: bytes) -> None:
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as archive:
        members = archive.getmembers()
        validated = [(_archive_relative_path(member), member) for member in members]
        root.mkdir(parents=True, exist_ok=True)
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
                raise ValueError(f"workspace archive member {member.name!r} has no content")
            with target.open("wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)


def _archive_relative_path(member: tarfile.TarInfo) -> PurePosixPath | None:
    path = PurePosixPath(member.name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"workspace archive path escapes workspace: {member.name!r}")
    if member.issym() or member.islnk() or member.isdev():
        raise ValueError(f"workspace archive member type is prohibited: {member.name!r}")
    parts = path.parts[1:] if path.parts and path.parts[0] in {".", "workspace"} else path.parts
    if not parts:
        return None
    return PurePosixPath(*parts)


def _exec(
    core: sync_client.CoreV1Api,
    namespace: str,
    pod_name: str,
    container: str,
    command: list[str],
    *,
    stdin: str | None = None,
    stream_factory: Callable[..., object] = stream,
) -> str:
    response = stream_factory(
        core.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        container=container,
        command=command,
        stderr=True,
        stdin=stdin is not None,
        stdout=True,
        tty=False,
        _preload_content=False,
    )
    if stdin is not None:
        response.write_stdin(stdin)  # type: ignore[attr-defined]
        response.close_channel(0)  # type: ignore[attr-defined]
    stdout: list[str] = []
    stderr: list[str] = []
    while response.is_open():  # type: ignore[attr-defined]
        response.update(timeout=1)  # type: ignore[attr-defined]
        if response.peek_stdout():  # type: ignore[attr-defined]
            stdout.append(response.read_stdout())  # type: ignore[attr-defined]
        if response.peek_stderr():  # type: ignore[attr-defined]
            stderr.append(response.read_stderr())  # type: ignore[attr-defined]
    response.close()  # type: ignore[attr-defined]
    if stderr:
        raise RuntimeError("Kubernetes workspace transfer failed: " + "".join(stderr).strip())
    return "".join(stdout)
