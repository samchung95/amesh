from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
LONG_RUNNING = (
    "api",
    "executor",
    "scheduler",
    "indexer",
    "worker",
    "maintenance",
    "postgres",
    "minio",
)
ONE_SHOT = ("migrate", "minio-init")
DOCKER_SOCKET = "/var/run/docker.sock"
LOOPBACK_BIND = "${AMESH_BIND_ADDRESS:-127.0.0.1}:"


def _services(name: str) -> dict[str, dict[str, object]]:
    document = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    services = document["services"]
    assert isinstance(services, dict)
    return services


def _published_ports(services: dict[str, dict[str, object]]) -> list[str]:
    ports: list[str] = []
    for service in services.values():
        values = service.get("ports", [])
        assert isinstance(values, list)
        ports.extend(str(value) for value in values)
    return ports


@pytest.mark.parametrize("name", ["compose.yaml", "docker/compose.compact.yaml"])
def test_development_profiles_publish_ports_on_loopback_only(name: str) -> None:
    ports = _published_ports(_services(name))

    assert ports
    for port in ports:
        assert port.startswith(LOOPBACK_BIND), port


def test_default_compose_restarts_long_running_services_only() -> None:
    services = _services("compose.yaml")

    for name in LONG_RUNNING:
        assert services[name].get("restart") == "unless-stopped", name
    for name in ONE_SHOT:
        assert services[name].get("restart", "no") == "no", name
    assert set(services) == {*LONG_RUNNING, *ONE_SHOT}


def test_compact_compose_restarts_runtime_and_database() -> None:
    services = _services("docker/compose.compact.yaml")

    assert services["compact"]["restart"] == "unless-stopped"
    assert services["postgres"]["restart"] == "unless-stopped"
    assert services["compact-volume-init"].get("restart", "no") == "no"


@pytest.mark.parametrize("name", ["compose.yaml", "docker/compose.compact.yaml"])
def test_development_profiles_do_not_grant_container_runtime_authority(name: str) -> None:
    services = _services(name)

    assert DOCKER_SOCKET not in yaml.safe_dump(services)
    for service in services.values():
        assert "group_add" not in service
        environment = service.get("environment", {})
        assert isinstance(environment, dict)
        assert str(environment.get("DOCKER_RUNNER_ENABLED", "false")).lower() == "false"


def test_docker_runner_overlay_is_limited_to_trusted_runtime_processes() -> None:
    services = _services("docker/compose.docker-runner.yaml")

    assert set(services) == {"api", "executor"}
    for service in services.values():
        environment = service["environment"]
        assert isinstance(environment, dict)
        assert environment["DOCKER_RUNNER_ENABLED"] == "true"
        assert "DOCKER_IMAGE_POLICY" in environment
        assert service["volumes"] == [f"{DOCKER_SOCKET}:{DOCKER_SOCKET}"]
        assert "ports" not in service


def test_docker_runner_overlay_merges_socket_into_rendered_stack() -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker is not installed")

    def render(*overlays: str) -> dict[str, dict[str, object]]:
        arguments = ["docker", "compose", "-f", "compose.yaml"]
        for overlay in overlays:
            arguments += ["-f", overlay]
        environment = os.environ.copy()
        environment.pop("AMESH_BIND_ADDRESS", None)
        result = subprocess.run(
            [*arguments, "config", "--format", "json"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        rendered = yaml.safe_load(result.stdout)
        assert isinstance(rendered, dict)
        services = rendered["services"]
        assert isinstance(services, dict)
        return services

    default = render()
    enabled = render("docker/compose.docker-runner.yaml")

    assert DOCKER_SOCKET not in yaml.safe_dump(default)
    for name in ("api", "executor"):
        environment = enabled[name]["environment"]
        assert isinstance(environment, dict)
        assert environment["DOCKER_RUNNER_ENABLED"] == "true"
        mounts = enabled[name]["volumes"]
        assert isinstance(mounts, list)
        targets = {mount["target"] for mount in mounts}
        assert {DOCKER_SOCKET, "/var/lib/amesh/plugins"} <= targets
    for name in ("scheduler", "indexer", "worker", "maintenance"):
        assert DOCKER_SOCKET not in yaml.safe_dump(enabled[name])
    for name in ("api", "postgres", "minio"):
        ports = default[name]["ports"]
        assert isinstance(ports, list)
        for port in ports:
            assert isinstance(port, dict)
            assert port["host_ip"] == "127.0.0.1"
