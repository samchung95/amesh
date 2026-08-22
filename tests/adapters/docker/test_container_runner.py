from __future__ import annotations

import asyncio
import io
import os
import sys
import tarfile
from pathlib import Path
from typing import Any, cast

import docker
import pytest
from docker.client import DockerClient
from pydantic import SecretStr

from amesh.adapters.docker import DockerContainerRunner
from amesh.adapters.docker.container_runner import (
    _restore_workspace,
    _validate_docker_request,
)
from amesh.adapters.docker.image_policy import CommandImagePolicyVerifier, image_registry
from amesh.domain.runner import (
    DockerContainerRunnerExtension,
    DockerImagePolicy,
    RunnerId,
    RunnerNetworkAccess,
    RunnerNetworkPolicy,
    RunnerSecurityPolicy,
)
from amesh.dsl import validate_flow_document
from amesh.ports import (
    RunnerLogStream,
    RunnerRequest,
    RunnerStatus,
    ScopedRunnerCredential,
    UnsupportedRunnerRequest,
)


class FakeImage:
    def __init__(self) -> None:
        self.attrs = {"RepoDigests": ["docker.io/library/alpine@sha256:" + "a" * 64]}


class FakeImages:
    def __init__(self) -> None:
        self.pull_auth: dict[str, str] | None = None

    def get(self, reference: str) -> FakeImage:
        del reference
        return FakeImage()

    def pull(self, reference: str, **kwargs: object) -> FakeImage:
        del reference
        self.pull_auth = cast(dict[str, str] | None, kwargs.get("auth_config"))
        return FakeImage()


class FakeVolume:
    def __init__(self, name: str, labels: dict[str, str]) -> None:
        self.name = name
        self.attrs = {"Labels": labels}
        self.removed = False

    def remove(self, *, force: bool = False) -> None:
        del force
        self.removed = True


class FakeVolumes:
    def __init__(self) -> None:
        self.created: list[FakeVolume] = []
        self.list_filters: dict[str, object] = {}

    def create(self, *, name: str, labels: dict[str, str]) -> FakeVolume:
        volume = FakeVolume(name, labels)
        self.created.append(volume)
        return volume

    def list(self, **kwargs: object) -> list[FakeVolume]:
        self.list_filters = cast(dict[str, object], kwargs.get("filters", {}))
        return [item for item in self.created if not item.removed]


class FakeContainer:
    def __init__(self, labels: dict[str, str], output_archive: bytes) -> None:
        self.id = "container-epic221"
        self.labels = labels
        self.attrs: dict[str, Any] = {
            "State": {"OOMKilled": False, "Error": ""},
        }
        self.output_archive = output_archive
        self.removed = False
        self.stopped = False
        self.received_archive = b""

    def put_archive(self, path: str, data: bytes) -> bool:
        assert path == "/workspace"
        self.received_archive = data
        return True

    def start(self) -> None: ...

    def attach(self, **kwargs: object) -> Any:
        del kwargs
        return iter(((b"stdout\n", None), (None, b"stderr\n")))

    def wait(self) -> dict[str, int]:
        return {"StatusCode": 0}

    def reload(self) -> None: ...

    def stats(self, **kwargs: object) -> dict[str, object]:
        del kwargs
        return {
            "cpu_stats": {"cpu_usage": {"total_usage": 2_000_000_000}},
            "memory_stats": {"max_usage": 12_345_678},
        }

    def get_archive(self, path: str) -> tuple[list[bytes], dict[str, object]]:
        assert path == "/workspace"
        return [self.output_archive], {}

    def stop(self, *, timeout: int) -> None:
        del timeout
        self.stopped = True

    def kill(self) -> None:
        self.stopped = True

    def remove(self, **kwargs: object) -> None:
        del kwargs
        self.removed = True


class FakeContainers:
    def __init__(self, output_archive: bytes) -> None:
        self.output_archive = output_archive
        self.created: list[FakeContainer] = []
        self.create_kwargs: dict[str, object] = {}

    def create(self, image: str, command: list[str], **kwargs: object) -> FakeContainer:
        self.create_kwargs = {"image": image, "command": command, **kwargs}
        container = FakeContainer(cast(dict[str, str], kwargs["labels"]), self.output_archive)
        self.created.append(container)
        return container

    def list(self, **kwargs: object) -> list[FakeContainer]:
        del kwargs
        return [item for item in self.created if not item.removed]


class FakeClient:
    def __init__(self, output_archive: bytes) -> None:
        self.images = FakeImages()
        self.volumes = FakeVolumes()
        self.containers = FakeContainers(output_archive)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def request(*command: str, **updates: object) -> RunnerRequest:
    values: dict[str, object] = {
        "tenant_id": "default",
        "namespace": "tests.docker",
        "execution_id": "execution-221",
        "task_run_id": "task-221",
        "attempt_id": "attempt-221",
        "fencing_token": 1,
        "command": list(command),
        "image": "alpine:3.21",
        "extension": DockerContainerRunnerExtension(type=RunnerId.DOCKER),
        "cancel_grace_seconds": 0.1,
    }
    values.update(updates)
    return RunnerRequest.model_validate(values)


def workspace_archive(files: dict[str, bytes]) -> bytes:
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w") as archive:
        directory = tarfile.TarInfo("workspace")
        directory.type = tarfile.DIRTYPE
        archive.addfile(directory)
        for name, content in files.items():
            member = tarfile.TarInfo(f"workspace/{name}")
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    return payload.getvalue()


def test_epic221_docker_runner_yaml_contract() -> None:
    result = validate_flow_document(
        """
id: docker_runner
namespace: tests.docker
tasks:
  - id: transform
    type: core.shell
    image: alpine:3.21
    command: [sh, -c, "tr a-z A-Z < input.txt > output.txt"]
    inputFiles: {input.txt: "hello"}
    outputFiles: [output.txt]
    taskRunner:
      type: docker
      pullPolicy: IF_NOT_PRESENT
      platform: linux/amd64
    networkPolicy: {access: none}
    securityPolicy:
      readOnlyRootFilesystem: true
      capabilityDrop: [ALL]
      noNewPrivileges: true
    resources:
      cpus: 0.5
      memoryBytes: 33554432
      processes: 16
      openFiles: 64
"""
    )

    assert result.valid, result.issues


def test_urs_f_0265_0270_image_policy_and_immutable_resolution_fail_closed(
    tmp_path: Path,
) -> None:
    fake = FakeClient(workspace_archive({"output.txt": b"done"}))
    runner = DockerContainerRunner(
        client=cast(DockerClient, fake),
        image_policy=DockerImagePolicy(allowedRegistries=("docker.io",), allowTags=False),
    )
    with pytest.raises(UnsupportedRunnerRequest, match="allowTags"):
        asyncio.run(runner.run(request("true", working_directory=str(tmp_path))))
    assert not fake.containers.created

    with pytest.raises(UnsupportedRunnerRequest, match="not allowed"):
        asyncio.run(
            runner.run(
                request(
                    "true",
                    image="evil.example/image@sha256:" + "b" * 64,
                    working_directory=str(tmp_path),
                )
            )
        )
    assert image_registry("alpine:3.21") == "docker.io"
    assert image_registry("registry.example:5000/team/image:1") == "registry.example:5000"


def test_urs_f_0266_0267_0268_0271_0272_container_contract_and_cleanup(
    tmp_path: Path,
) -> None:
    (tmp_path / "input.txt").write_text("input", encoding="utf-8")
    fake = FakeClient(workspace_archive({"output.txt": b"transformed"}))
    runner = DockerContainerRunner(
        client=cast(DockerClient, fake),
        image_policy=DockerImagePolicy(allowedRegistries=("docker.io",), allowTags=True),
    )
    result = asyncio.run(
        runner.run(
            request(
                "sh",
                "-c",
                "cat input.txt > output.txt",
                working_directory=str(tmp_path),
                resource_limits={
                    "cpus": 0.5,
                    "memoryBytes": 32 * 1024 * 1024,
                    "processes": 16,
                    "openFiles": 64,
                },
                network_policy=RunnerNetworkPolicy(access=RunnerNetworkAccess.NONE),
                security_policy=RunnerSecurityPolicy(
                    readOnlyRootFilesystem=True,
                    runAsUser=1000,
                    capabilityAdd=("CHOWN",),
                    capabilityDrop=("ALL",),
                ),
            )
        )
    )

    created = fake.containers.create_kwargs
    assert created["image"] == "docker.io/library/alpine@sha256:" + "a" * 64
    assert created["network_disabled"] is True
    assert created["network_mode"] == "none"
    assert created["read_only"] is True
    assert created["user"] == "1000"
    assert created["cap_add"] == ["CHOWN"]
    assert created["cap_drop"] == ["ALL"]
    assert created["security_opt"] == ["no-new-privileges:true"]
    assert created["volumes"] == {
        fake.volumes.created[0].name: {"bind": "/workspace", "mode": "rw"}
    }
    assert "/var/run/docker.sock" not in repr(created["volumes"])
    assert result.status is RunnerStatus.SUCCESS
    assert result.logs[0].stream is RunnerLogStream.STDOUT
    assert result.logs[1].stream is RunnerLogStream.STDERR
    assert result.metrics.cpu_seconds == 2
    assert result.metrics.peak_memory_bytes == 12_345_678
    assert result.diagnostics.details["imageResolved"].endswith("a" * 64)
    assert (tmp_path / "output.txt").read_text(encoding="utf-8") == "transformed"
    assert fake.containers.created[0].removed
    assert fake.volumes.created[0].removed

    reconciled = asyncio.run(runner.reconcile({}))
    assert reconciled.cleaned_attempts == ()
    assert fake.volumes.list_filters == {
        "label": ["amesh.runner=docker", "amesh.workspace-volume=true"]
    }


def test_urs_f_0269_remote_rootless_capability_and_registry_credentials_are_scoped() -> None:
    credential_request = request(
        "true",
        credentials=(
            ScopedRunnerCredential(
                scope="username",
                environmentVariable="REGISTRY_USER",
                value=SecretStr("robot"),
            ),
            ScopedRunnerCredential(
                scope="password",
                environmentVariable="REGISTRY_PASSWORD",
                value=SecretStr("temporary"),
            ),
            ScopedRunnerCredential(
                scope="task",
                environmentVariable="TASK_TOKEN",
                value=SecretStr("inside"),
            ),
        ),
        extension=DockerContainerRunnerExtension(
            type=RunnerId.DOCKER,
            registryUsernameVariable="REGISTRY_USER",
            registryPasswordVariable="REGISTRY_PASSWORD",
        ),
    )
    _, _, auth_config, environment = _validate_docker_request(credential_request)

    assert DockerContainerRunner.CAPABILITIES.platforms == (
        "docker-engine",
        "rootless-docker",
        "remote-docker",
    )
    assert auth_config == {"username": "robot", "password": "temporary"}
    assert environment == {"TASK_TOKEN": "inside"}
    assert "temporary" not in repr(credential_request)


def test_urs_f_0270_command_verifier_is_argv_only_and_fails_closed() -> None:
    verifier = CommandImagePolicyVerifier(
        signature_command=(sys.executable, "-c", "import sys; raise SystemExit(0)", "{image}"),
        vulnerability_command=(
            sys.executable,
            "-c",
            "import sys; print('denied', file=sys.stderr); raise SystemExit(3)",
            "{image}",
        ),
    )
    asyncio.run(verifier.verify_signature("image@sha256:" + "a" * 64))
    with pytest.raises(UnsupportedRunnerRequest, match="vulnerability verification rejected"):
        asyncio.run(verifier.verify_vulnerabilities("image@sha256:" + "a" * 64))
    missing_image = CommandImagePolicyVerifier(
        signature_command=(sys.executable, "-c", "raise SystemExit(0)"),
    )
    with pytest.raises(UnsupportedRunnerRequest, match=r"must contain the \{image\} placeholder"):
        asyncio.run(missing_image.verify_signature("image@sha256:" + "a" * 64))


def test_urs_f_0267_output_archive_rejects_links_before_replacing_workspace(
    tmp_path: Path,
) -> None:
    existing = tmp_path / "existing.txt"
    existing.write_text("preserved", encoding="utf-8")
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w") as archive:
        link = tarfile.TarInfo("workspace/escape")
        link.type = tarfile.SYMTYPE
        link.linkname = "../../outside"
        archive.addfile(link)

    with pytest.raises(ValueError, match="prohibited"):
        _restore_workspace(tmp_path, [payload.getvalue()])
    assert existing.read_text(encoding="utf-8") == "preserved"


@pytest.mark.skipif(
    os.getenv("AMESH_TEST_DOCKER") != "1",
    reason="set AMESH_TEST_DOCKER=1 for the disposable Docker Engine profile",
)
def test_epic221_real_engine_archive_security_logs_cancellation_and_reconciliation(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        client = docker.from_env()
        await asyncio.to_thread(client.ping)
        policy = DockerImagePolicy(allowedRegistries=("docker.io",), allowTags=True)
        runner = DockerContainerRunner(client=client, image_policy=policy)
        (tmp_path / "input.txt").write_text("hello docker", encoding="utf-8")
        running = asyncio.create_task(
            runner.run(
                request(
                    "sh",
                    "-c",
                    "cat input.txt; echo stderr-ok >&2; tr a-z A-Z < input.txt > output.txt; sleep 0.4",
                    working_directory=str(tmp_path),
                    resource_limits={
                        "cpus": 0.5,
                        "memoryBytes": 32 * 1024 * 1024,
                        "processes": 32,
                        "openFiles": 64,
                    },
                    network_policy=RunnerNetworkPolicy(access=RunnerNetworkAccess.NONE),
                    security_policy=RunnerSecurityPolicy(
                        readOnlyRootFilesystem=True,
                        runAsUser=0,
                    ),
                )
            )
        )
        owned: list[Any] = []
        for _ in range(100):
            owned = await asyncio.to_thread(
                client.containers.list,
                all=True,
                filters={"label": "amesh.runner=docker"},
            )
            if owned:
                break
            await asyncio.sleep(0.02)
        assert owned
        inspected = owned[0].attrs
        host = inspected["HostConfig"]
        assert host["ReadonlyRootfs"] is True
        assert host["NetworkMode"] == "none"
        assert host["CapDrop"] == ["ALL"]
        assert host["Memory"] == 32 * 1024 * 1024
        assert all(mount["Destination"] != "/var/run/docker.sock" for mount in inspected["Mounts"])
        result = await running

        assert result.status is RunnerStatus.SUCCESS
        assert result.exit_code == 0
        assert "@sha256:" in result.diagnostics.details["imageResolved"]
        assert "hello docker" in result.outputs["stdout"]
        assert "stderr-ok" in result.outputs["stderr"]
        assert (tmp_path / "output.txt").read_text(encoding="utf-8") == "HELLO DOCKER"
        assert not await asyncio.to_thread(
            client.containers.list,
            all=True,
            filters={"label": "amesh.attempt-id=attempt-221"},
        )

        cancelled = asyncio.create_task(
            runner.run(
                request(
                    "sleep",
                    "30",
                    attempt_id="attempt-cancel-221",
                )
            )
        )
        for _ in range(100):
            if "attempt-cancel-221" in runner._active:
                break
            await asyncio.sleep(0.02)
        await runner.cancel("attempt-cancel-221", 1)
        assert (await cancelled).status is RunnerStatus.CANCELLED

        image = await asyncio.to_thread(client.images.get, "alpine:3.21")
        orphan_volume = await asyncio.to_thread(
            client.volumes.create,
            name="amesh-test-orphan-221",
            labels={
                "amesh.runner": "docker",
                "amesh.workspace-volume": "true",
                "amesh.attempt-id": "attempt-orphan-221",
                "amesh.fencing-token": "1",
            },
        )
        await asyncio.to_thread(
            client.containers.create,
            image.id,
            ["true"],
            name="amesh-test-orphan-221",
            labels={
                "amesh.runner": "docker",
                "amesh.attempt-id": "attempt-orphan-221",
                "amesh.fencing-token": "1",
            },
            volumes={orphan_volume.name: {"bind": "/workspace", "mode": "rw"}},
        )
        first = await runner.reconcile({})
        second = await runner.reconcile({})
        assert first.cleaned_attempts == ("attempt-orphan-221",)
        assert second.cleaned_attempts == ()
        client.close()

    asyncio.run(scenario())
