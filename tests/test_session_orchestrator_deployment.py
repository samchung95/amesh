from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "docker/compose.session-orchestrator.yaml"
PROFILE = ROOT / "charts" / "amesh" / "profiles" / "session-orchestrator.yaml"


def _yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_session_orchestrator_compose_is_local_and_runnerless() -> None:
    document = _yaml(COMPOSE)
    services = document["services"]
    networks = document["networks"]
    assert isinstance(services, dict)
    assert set(services) == {"api", "executor", "scheduler", "migrate", "preflight"}
    assert networks["private"].get("internal") is not True

    for _name, service in services.items():
        assert "/var/run/docker.sock" not in yaml.safe_dump(service)
        assert "group_add" not in service
        for port in service.get("ports", []):
            assert str(port).startswith("127.0.0.1:")

    for name in ("api", "executor"):
        environment = services[name]["environment"]
        assert environment["DOCKER_RUNNER_ENABLED"] == "false"
        assert environment["EXECUTION_RUNNER_MODE"] == "local"
        assert environment["LOCAL_PROCESS_RUNNER_ENABLED"] == "true"
        assert json.loads(environment["SERVICE_ENABLED_ROLES"]) == [
            "webserver",
            "executor",
            "scheduler",
        ]


def test_session_orchestrator_compose_declares_external_runtime_references() -> None:
    services = _yaml(COMPOSE)["services"]
    environment = services["api"]["environment"]
    assert environment["DATABASE_URL"].startswith("${AMESH_SESSION_DATABASE_URL:")
    assert environment["OBJECT_STORAGE_ENDPOINT"].startswith(
        "${AMESH_SESSION_OBJECT_STORAGE_ENDPOINT:"
    )
    assert environment["READINESS_CHECK_STORAGE"] == "true"
    assert environment["MODEL_CONTINUATION_ENCRYPTION_KEY"] == ("secret://model-continuation-key")
    assert environment["WEBHOOK_SIGNING_KEY"] == "secret://webhook-signing-key"
    assert environment["PLUGIN_REGISTRY_SIGNING_KEY"] == "secret://registry-signing-key"
    assert environment["IDENTITY_PROVIDERS"] == "[]"
    assert environment["SCIM_PROVIDERS"] == "[]"
    rendered = yaml.safe_dump(_yaml(COMPOSE))
    assert not any(
        forbidden in rendered
        for forbidden in ("OPENROUTER_API_KEY", "BROKER_PASSWORD", "KAFKA_PASSWORD")
    )
    assert "minio-development-only" not in rendered

    for role in ("api", "executor", "scheduler"):
        assert services[role]["depends_on"]["preflight"]["condition"] == (
            "service_completed_successfully"
        )
    for role in ("executor", "scheduler"):
        assert services[role]["healthcheck"]["test"] == [
            "CMD",
            "sh",
            "-c",
            "PGPASSFILE=/tmp/postgres-pgpass python -m amesh.entrypoints.role --check readiness",
        ]
    assert services["preflight"]["command"] == [
        "python",
        "-m",
        "amesh.entrypoints.deployment_profile",
        "--check-settings",
    ]


def test_docker_compose_profile_renders_with_reference_only_inputs() -> None:
    if shutil.which("docker") is None:
        pytest.skip("Docker is not installed")
    environment = os.environ.copy()
    environment.update(
        {
            "AMESH_SESSION_DATABASE_URL": "postgresql+asyncpg://db.internal/amesh",
            "AMESH_SESSION_DATABASE_TLS_MODE": "verify-full",
            "AMESH_SESSION_OBJECT_STORAGE_ENDPOINT": "https://s3.internal",
            "AMESH_SESSION_OBJECT_STORAGE_REGION": "us-east-1",
            "AMESH_SESSION_OBJECT_STORAGE_BUCKET": "amesh",
            "AMESH_SESSION_EGRESS_ALLOWED_HOSTS": '["s3.internal"]',
            "AMESH_SESSION_SECRETS_DIR": str(ROOT / ".session-secrets"),
        }
    )
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_helm_session_orchestrator_profile_has_role_and_secret_boundaries() -> None:
    profile = _yaml(PROFILE)
    roles = profile["serviceRoles"]
    assert [role for role, config in roles.items() if config["enabled"]] == [
        "executor",
        "scheduler",
    ]
    assert profile["database"]["existingSecret"] == "amesh-session-orchestrator-database"
    assert profile["objectStorage"]["existingSecret"] == (
        "amesh-session-orchestrator-object-storage"
    )
    assert profile["encryption"]["existingSecret"] == "amesh-session-orchestrator-encryption"
    assert profile["identity"]["providerConfigExistingSecret"] == (
        "amesh-session-orchestrator-identity"
    )
    assert profile["openRouter"]["existingSecret"] == ""
    assert profile["webhookSigningKey"]["existingSecret"] == ("amesh-session-orchestrator-auth")
    assert profile["pluginRegistrySigningKey"]["existingSecret"] == (
        "amesh-session-orchestrator-auth"
    )

    profile_text = PROFILE.read_text(encoding="utf-8")
    assert "/var/run/docker.sock" not in profile_text
    assert "minio-development-only" not in profile_text
    assert "DOCKER_RUNNER_ENABLED" not in profile_text

    role_template = (ROOT / "charts" / "amesh" / "templates" / "deployment-roles.yaml").read_text(
        encoding="utf-8"
    )
    server_template = (
        ROOT / "charts" / "amesh" / "templates" / "deployment-server.yaml"
    ).read_text(encoding="utf-8")
    helpers = (ROOT / "charts" / "amesh" / "templates" / "_helpers.tpl").read_text(encoding="utf-8")
    assert "/var/run/docker.sock" not in role_template + server_template
    assert "MODEL_CONTINUATION_ENCRYPTION_KEY" in helpers


def test_helm_session_orchestrator_profile_renders_when_helm_is_available() -> None:
    if shutil.which("helm") is None:
        pytest.skip("Helm is not installed")
    result = subprocess.run(
        [
            "helm",
            "template",
            "session-orchestrator",
            str(ROOT / "charts" / "amesh"),
            "-f",
            str(PROFILE),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "/var/run/docker.sock" not in result.stdout
    assert "amesh-session-orchestrator-encryption" in result.stdout
    assert "WEBHOOK_SIGNING_KEY" in result.stdout
    assert "PLUGIN_REGISTRY_SIGNING_KEY" in result.stdout
