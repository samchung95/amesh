from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from amesh.config import Settings
from amesh.deployment_profile import (
    HardenedProfileError,
    load_hardened_compose,
    validate_hardened_compose,
    validate_hardened_environment,
    validate_hardened_settings,
)

ROOT = Path(__file__).parents[1]


def test_checked_in_profile_is_loopback_private_and_gated() -> None:
    document = load_hardened_compose(ROOT / "compose.hardened.yaml")
    services = document["services"]

    assert services["api"]["ports"] == ["127.0.0.1:${AMESH_HARDENED_PORT:-8000}:8000"]
    assert "ports" not in services["postgres"]
    assert document["networks"]["private"]["internal"] is True
    assert "loopback" in services["api"]["networks"]
    assert document["networks"]["loopback"].get("internal") is not True
    assert json.loads(services["api"]["environment"]["SERVICE_ENABLED_ROLES"]) == [
        "webserver",
        "executor",
        "scheduler",
    ]
    assert services["api"]["environment"]["MODEL_CONTINUATION_ENCRYPTION_KEY"] == (
        "secret://model-continuation-key"
    )
    assert "model-continuation-key" in document["secrets"]
    assert services["api"]["environment"]["PGPASSFILE"] == "/run/secrets/postgres-pgpass"
    assert "postgres-pgpass" in document["secrets"]
    assert "password-free" in services["api"]["environment"]["DATABASE_URL"]
    assert "secret://" in yaml.safe_dump(document)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("ports", "non-loopback published port"),
        ("auth", "development authentication"),
        ("socket", "container-runtime authority"),
        ("roles", "enabled roles"),
    ],
)
def test_hardened_profile_rejects_unsafe_fixtures(path: str, expected: str) -> None:
    document = load_hardened_compose(ROOT / "compose.hardened.yaml")
    fixture = copy.deepcopy(document)
    if path == "ports":
        fixture["services"]["api"]["ports"] = ["8000:8000"]
    elif path == "auth":
        fixture["services"]["api"]["environment"]["AUTH_MODE"] = "development"
    elif path == "socket":
        fixture["services"]["api"]["volumes"] = ["/var/run/docker.sock:/var/run/docker.sock"]
    else:
        fixture["services"]["api"]["environment"]["SERVICE_ENABLED_ROLES"] = '["webserver"]'

    with pytest.raises(HardenedProfileError, match=expected):
        validate_hardened_compose(fixture)


def test_hardened_environment_requires_references_and_rejects_domain_credentials() -> None:
    environment = {
        "DATABASE_URL": "postgresql+asyncpg://amesh@postgres:5432/amesh",
        "PGPASSFILE": "/run/secrets/postgres-pgpass",
        "AMESH_ADMIN_TOKEN": "secret://admin-token",
        "AMESH_TOKEN_PEPPER": "secret://token-pepper",
        "MODEL_CONTINUATION_ENCRYPTION_KEY": "secret://model-continuation-key",
        "WEBHOOK_SIGNING_KEY": "secret://webhook-signing-key",
        "PLUGIN_REGISTRY_SIGNING_KEY": "secret://registry-signing-key",
    }
    validate_hardened_environment(environment)

    with pytest.raises(HardenedProfileError, match="OPENROUTER_API_KEY"):
        validate_hardened_environment({**environment, "OPENROUTER_API_KEY": "client-secret"})

    with pytest.raises(HardenedProfileError, match="secret:// reference"):
        validate_hardened_environment({**environment, "AMESH_ADMIN_TOKEN": "plain-token"})

    with pytest.raises(HardenedProfileError, match="must not embed"):
        validate_hardened_environment(
            {
                **environment,
                "DATABASE_URL": "postgresql+asyncpg://amesh:embedded@postgres:5432/amesh",
            }
        )

    with pytest.raises(HardenedProfileError, match="PGPASSFILE"):
        validate_hardened_environment({**environment, "PGPASSFILE": "/tmp/pgpass"})


def test_hardened_compose_rejects_password_urls_and_missing_pgpass_reference() -> None:
    document = load_hardened_compose(ROOT / "compose.hardened.yaml")
    password_url = copy.deepcopy(document)
    password_url["services"]["api"]["environment"]["DATABASE_URL"] = (
        "postgresql+asyncpg://amesh:embedded@postgres:5432/amesh"
    )
    with pytest.raises(HardenedProfileError, match="must not embed"):
        validate_hardened_compose(password_url)

    missing_reference = copy.deepcopy(document)
    missing_reference["services"]["api"]["environment"].pop("PGPASSFILE")
    with pytest.raises(HardenedProfileError, match="postgres-pgpass"):
        validate_hardened_compose(missing_reference)

    missing_secret = copy.deepcopy(document)
    missing_secret["secrets"].pop("postgres-pgpass")
    with pytest.raises(HardenedProfileError, match="undeclared secret"):
        validate_hardened_compose(missing_secret)


def test_hardened_settings_reject_development_and_private_host_access() -> None:
    settings = Settings(
        _env_file=None,
        app_env="production",
        auth_mode="credentials",
        object_storage_backend="local",
        execution_runner_mode="local",
        local_process_runner_enabled=True,
        amesh_admin_token="test-admin-token",
        amesh_token_pepper="test-token-pepper",
        webhook_signing_key="test-webhook-signing-key-that-is-long-enough",
        network_egress_allowed_hosts=("localhost",),
        service_enabled_roles=("webserver", "executor", "scheduler"),
    )
    validate_hardened_settings(settings)

    with pytest.raises(HardenedProfileError, match="private-host"):
        validate_hardened_settings(
            settings.model_copy(update={"core_http_allowed_private_hosts": ("localhost",)})
        )

    with pytest.raises(HardenedProfileError, match="development"):
        validate_hardened_settings(settings.model_copy(update={"app_env": "development"}))
