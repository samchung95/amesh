from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _yaml(name: str) -> dict[str, object]:
    value = yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _assert_shared_values(
    services: Mapping[str, dict[str, object]],
    names: Sequence[str],
    template: Mapping[str, object],
    keys: Sequence[str],
) -> None:
    for name in names:
        for key in keys:
            assert services[name][key] is template[key]


def test_distributed_compose_uses_local_shared_service_sources() -> None:
    document = _yaml("compose.yaml")
    services = document["services"]
    assert isinstance(services, dict)
    application = document["x-application-service"]
    role = document["x-role-service"]
    dependencies = document["x-database-role-dependencies"]
    assert isinstance(application, dict)
    assert isinstance(role, dict)
    assert isinstance(dependencies, dict)

    _assert_shared_values(
        services,
        ("api", "executor", "scheduler", "indexer", "worker", "maintenance"),
        application,
        ("build", "tmpfs", "security_opt"),
    )
    _assert_shared_values(
        services,
        ("executor", "scheduler", "indexer", "worker", "maintenance"),
        role,
        ("command", "healthcheck"),
    )
    for name in ("scheduler", "indexer", "worker", "maintenance"):
        assert services[name]["depends_on"] is dependencies

    source = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert source.count("<<: *role-environment") == 5


@pytest.mark.parametrize(
    ("name", "runtime_names", "role_names"),
    [
        (
            "docker/compose.hardened.yaml",
            ("api", "executor", "scheduler"),
            ("executor", "scheduler"),
        ),
        (
            "docker/compose.session-orchestrator.yaml",
            ("api", "executor", "scheduler"),
            ("executor", "scheduler"),
        ),
    ],
)
def test_production_compose_uses_local_shared_service_sources(
    name: str,
    runtime_names: tuple[str, ...],
    role_names: tuple[str, ...],
) -> None:
    document = _yaml(name)
    services = document["services"]
    application = document["x-application-service"]
    runtime = document["x-runtime-service"]
    role = document["x-role-service"]
    assert isinstance(services, dict)
    assert isinstance(application, dict)
    assert isinstance(runtime, dict)
    assert isinstance(role, dict)

    _assert_shared_values(
        services,
        ("migrate", "preflight", *runtime_names),
        application,
        ("build", "entrypoint", "secrets", "tmpfs", "security_opt"),
    )
    _assert_shared_values(services, runtime_names, runtime, ("depends_on", "cap_drop"))
    _assert_shared_values(services, role_names, role, ("command", "healthcheck"))


def test_verification_compose_uses_one_image_and_build_source() -> None:
    document = _yaml("docker/compose.verify.yaml")
    services = document["services"]
    build = document["x-verification-build"]
    image = document["x-verification-image"]
    assert isinstance(services, dict)

    for name in ("migrate", "verify", "package", "live-openrouter"):
        assert services[name]["build"] is build
        assert services[name]["image"] == image


@pytest.mark.parametrize(
    ("name", "environment"),
    [
        ("compose.yaml", {}),
        (
            "docker/compose.hardened.yaml",
            {
                "AMESH_DATABASE_URL": "postgresql+asyncpg://amesh@postgres:5432/amesh",
                "AMESH_DATABASE_TLS_MODE": "disable",
                "AMESH_HARDENED_SECRETS_DIR": ".hardened-secrets",
                "AMESH_POSTGRES_DB": "amesh",
                "AMESH_POSTGRES_USER": "amesh",
            },
        ),
        (
            "docker/compose.session-orchestrator.yaml",
            {
                "AMESH_SESSION_DATABASE_URL": "postgresql+asyncpg://db.internal/amesh",
                "AMESH_SESSION_DATABASE_TLS_MODE": "verify-full",
                "AMESH_SESSION_EGRESS_ALLOWED_HOSTS": '["s3.internal"]',
                "AMESH_SESSION_OBJECT_STORAGE_BUCKET": "amesh",
                "AMESH_SESSION_OBJECT_STORAGE_ENDPOINT": "https://s3.internal",
                "AMESH_SESSION_OBJECT_STORAGE_REGION": "us-east-1",
                "AMESH_SESSION_SECRETS_DIR": ".session-secrets",
            },
        ),
        ("docker/compose.verify.yaml", {}),
    ],
)
def test_compose_manifests_render_after_shared_merges(
    name: str,
    environment: Mapping[str, str],
) -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker is not installed")
    process_environment = os.environ.copy()
    process_environment.update(environment)

    result = subprocess.run(
        ["docker", "compose", "-f", name, "config", "--quiet"],
        cwd=ROOT,
        env=process_environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
