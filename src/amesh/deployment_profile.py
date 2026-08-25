"""Validation for the client-driven hardened local deployment profile.

The validator is deliberately independent of the service runtime.  Compose can run it
as a one-shot gate before starting any client-facing or worker role, and tests can
validate the checked-in profile without a container runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

from amesh.config import Settings, get_settings

PROFILE_FILE = "compose.hardened.yaml"
REQUIRED_SERVICES = frozenset({"api", "executor", "scheduler", "postgres", "migrate", "preflight"})
REQUIRED_ROLES = ("webserver", "executor", "scheduler")
SECRET_REFERENCE = re.compile(r"^secret://([A-Za-z0-9][A-Za-z0-9_.-]{0,127})$")
SECRET_ENVIRONMENT = frozenset(
    {
        "AMESH_ADMIN_TOKEN",
        "AMESH_TOKEN_PEPPER",
        "MODEL_CONTINUATION_ENCRYPTION_KEY",
        "WEBHOOK_SIGNING_KEY",
        "PLUGIN_REGISTRY_SIGNING_KEY",
    }
)
FORBIDDEN_ENVIRONMENT_NAMES = frozenset(
    {
        "OPENROUTER_API_KEY",
        "BROKER_API_KEY",
        "BROKER_PASSWORD",
        "KAFKA_PASSWORD",
        "KAFKA_SASL_PASSWORD",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AZURE_CLIENT_SECRET",
        "GOOGLE_APPLICATION_CREDENTIALS",
    }
)


class HardenedProfileError(ValueError):
    """Raised when the hardened profile is not fail-closed."""


def _environment(service: Mapping[str, Any]) -> dict[str, str]:
    raw = service.get("environment", {})
    if isinstance(raw, Mapping):
        return {str(key): str(value) for key, value in raw.items() if value is not None}
    if isinstance(raw, list):
        result: dict[str, str] = {}
        for entry in raw:
            key, separator, value = str(entry).partition("=")
            if separator:
                result[key] = value
        return result
    return {}


def _port_host(port: Any) -> str | None:
    if isinstance(port, Mapping):
        host = port.get("host_ip", port.get("published_ip"))
        return str(host) if host is not None else None
    value = str(port)
    if value.startswith("127.0.0.1:"):
        return "127.0.0.1"
    if value.startswith("[::1]:") or value.startswith("::1:"):
        return "::1"
    return None


def _violation(message: str) -> HardenedProfileError:
    return HardenedProfileError(f"hardened deployment profile rejected: {message}")


def _json_environment_value(environment: Mapping[str, str], key: str) -> Any:
    try:
        return json.loads(environment[key])
    except KeyError as exc:
        raise _violation(f"{key} must be explicit JSON") from exc
    except json.JSONDecodeError as exc:
        raise _violation(f"{key} must be valid JSON") from exc


def _validate_password_free_database_url(value: str) -> None:
    """Require database authentication to come from the mounted asyncpg passfile."""

    if not value:
        raise _violation("DATABASE_URL must be supplied")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise _violation("DATABASE_URL must be a valid PostgreSQL URL") from exc
    if parsed.password is not None:
        raise _violation("DATABASE_URL must not embed a database password")


def validate_hardened_compose(document: Mapping[str, Any]) -> None:
    """Validate the checked-in Compose topology without contacting a runtime."""

    services = document.get("services")
    if not isinstance(services, Mapping):
        raise _violation("services must be a mapping")
    missing = REQUIRED_SERVICES - set(services)
    if missing:
        raise _violation(f"required services are missing: {', '.join(sorted(missing))}")

    networks = document.get("networks")
    private = networks.get("private") if isinstance(networks, Mapping) else None
    if not isinstance(private, Mapping) or private.get("internal") is not True:
        raise _violation("the private network must be marked internal")
    loopback = networks.get("loopback") if isinstance(networks, Mapping) else None
    if not isinstance(loopback, Mapping) or loopback.get("internal") is True:
        raise _violation("the loopback ingress network must permit loopback publication")

    secret_definitions = document.get("secrets")
    if not isinstance(secret_definitions, Mapping) or not secret_definitions:
        raise _violation("secret files must be declared at the Compose top level")
    declared_secrets = set(secret_definitions)
    rendered = json.dumps(document, sort_keys=True).lower()
    if (
        "/var/run/docker.sock" in rendered
        or "docker_runner" in rendered
        or "execution_runner_mode: docker" in rendered
    ):
        raise _violation("container-runtime authority is not allowed")
    if "openrouter_api_key" in rendered or "broker_password" in rendered:
        raise _violation("domain credentials are not allowed")

    for name, raw_service in services.items():
        if not isinstance(raw_service, Mapping):
            raise _violation(f"service {name!r} must be a mapping")
        service = raw_service
        service_networks = service.get("networks", ())
        if isinstance(service_networks, Mapping):
            service_networks = tuple(service_networks)
        if "private" not in service_networks:
            raise _violation(f"service {name!r} is not attached to the private network")
        environment = _environment(service)
        if name in {"migrate", "preflight", "api", "executor", "scheduler"}:
            attached_secrets: set[str] = set()
            for raw_secret in service.get("secrets", ()) or ():
                if isinstance(raw_secret, Mapping):
                    source = raw_secret.get("source", raw_secret.get("target"))
                    if source is not None:
                        attached_secrets.add(str(source))
                else:
                    attached_secrets.add(str(raw_secret))
            undeclared = attached_secrets - declared_secrets
            if undeclared:
                raise _violation(
                    f"service {name!r} references undeclared secret(s): {', '.join(sorted(undeclared))}"
                )
            if "postgres-pgpass" not in attached_secrets:
                raise _violation(f"service {name!r} must mount the postgres-pgpass secret")
            if environment.get("PGPASSFILE") != "/run/secrets/postgres-pgpass":
                raise _violation(f"service {name!r} must use the mounted postgres-pgpass secret")
            _validate_password_free_database_url(environment.get("DATABASE_URL", ""))
        for key in FORBIDDEN_ENVIRONMENT_NAMES:
            if key in environment:
                raise _violation(f"forbidden domain credential {key} is configured")
        for key, value in environment.items():
            if (
                key.endswith(("_API_KEY", "_PASSWORD", "_SECRET", "_TOKEN"))
                and key not in SECRET_ENVIRONMENT
            ):
                raise _violation(f"unexpected secret environment variable {key}")
            if key in SECRET_ENVIRONMENT and SECRET_REFERENCE.fullmatch(value) is None:
                raise _violation(f"{key} must use a secret:// reference")
            if value.startswith("secret://"):
                match = SECRET_REFERENCE.fullmatch(value)
                if match is None or match.group(1) not in declared_secrets:
                    raise _violation(f"{key} references an undeclared secret")
        for port in service.get("ports", ()) or ():
            host = _port_host(port)
            if host not in {"127.0.0.1", "::1"}:
                raise _violation(f"service {name!r} has a non-loopback published port")

    api_environment = _environment(services["api"])
    api_networks = services["api"].get("networks", ())
    if isinstance(api_networks, Mapping):
        api_networks = tuple(api_networks)
    if "loopback" not in api_networks:
        raise _violation("api must attach to the loopback ingress network")
    if api_environment.get("AUTH_MODE") == "development":
        raise _violation("development authentication is enabled")
    if api_environment.get("EXECUTION_RUNNER_MODE") == "docker":
        raise _violation("Docker execution is enabled")
    if api_environment.get("DOCKER_RUNNER_ENABLED", "false").lower() == "true":
        raise _violation("Docker execution is enabled")
    if api_environment.get("NETWORK_PUBLIC_EXPOSURE", "false").lower() == "true":
        raise _violation("public network exposure is enabled")
    enabled_roles = tuple(_json_environment_value(api_environment, "SERVICE_ENABLED_ROLES"))
    if enabled_roles != REQUIRED_ROLES:
        raise _violation(f"enabled roles must be exactly {REQUIRED_ROLES!r}")
    egress = _json_environment_value(api_environment, "NETWORK_EGRESS_ALLOWED_HOSTS")
    if not isinstance(egress, list) or not egress or "*" in egress:
        raise _violation("outbound egress must be a non-wildcard allowlist")
    if _json_environment_value(api_environment, "CORE_HTTP_ALLOWED_PRIVATE_HOSTS"):
        raise _violation("private-host access must remain denied")

    scheduler = services["scheduler"]
    scheduler_environment = _environment(scheduler)
    if scheduler_environment.get("SERVICE_ROLE") != "scheduler":
        raise _violation("scheduler service must declare SERVICE_ROLE=scheduler")
    healthcheck = scheduler.get("healthcheck") if isinstance(scheduler, Mapping) else None
    health_text = json.dumps(healthcheck, sort_keys=True) if healthcheck is not None else ""
    if "readiness" not in health_text:
        raise _violation("scheduler health must use the role readiness check")

    for role in ("api", "executor", "scheduler"):
        dependencies = services[role].get("depends_on", {})
        preflight = dependencies.get("preflight") if isinstance(dependencies, Mapping) else None
        if (
            not isinstance(preflight, Mapping)
            or preflight.get("condition") != "service_completed_successfully"
        ):
            raise _violation(f"{role} must wait for the preflight gate")


def load_hardened_compose(path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate a hardened Compose document."""

    source = Path(path or PROFILE_FILE)
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise _violation(f"cannot read Compose profile {source}") from exc
    if not isinstance(document, dict):
        raise _violation("Compose profile must contain a mapping")
    validate_hardened_compose(document)
    return document


def validate_hardened_settings(settings: Settings) -> None:
    """Validate the runtime settings that are not expressible in Compose topology."""

    failures: list[str] = []
    if settings.app_env == "development":
        failures.append("APP_ENV cannot be development")
    if settings.auth_mode == "development":
        failures.append("AUTH_MODE cannot be development")
    if settings.amesh_admin_token.get_secret_value() == "development-token":
        failures.append("AMESH_ADMIN_TOKEN cannot use the development default")
    if settings.execution_runner_mode == "docker" or settings.docker_runner_enabled:
        failures.append("Docker execution is disabled")
    if settings.network_public_exposure:
        failures.append("public exposure is disabled")
    if "*" in settings.network_egress_allowed_hosts:
        failures.append("NETWORK_EGRESS_ALLOWED_HOSTS cannot contain *")
    if settings.core_http_allowed_private_hosts:
        failures.append("private-host access requires an explicit hardened-profile exception")
    if tuple(settings.service_enabled_roles) != REQUIRED_ROLES:
        failures.append(f"SERVICE_ENABLED_ROLES must be exactly {REQUIRED_ROLES!r}")
    if failures:
        raise _violation("; ".join(failures))


def validate_hardened_environment(environment: Mapping[str, str] | None = None) -> None:
    """Reject missing secret references and unrelated credentials before startup."""

    values = dict(environment or os.environ)
    _validate_password_free_database_url(values.get("DATABASE_URL", ""))
    if values.get("PGPASSFILE") not in {
        "/run/secrets/postgres-pgpass",
        "/tmp/postgres-pgpass",
    }:
        raise _violation(
            "PGPASSFILE must reference the postgres-pgpass secret or its private tmpfs copy"
        )
    for key in SECRET_ENVIRONMENT:
        if SECRET_REFERENCE.fullmatch(values.get(key, "")) is None:
            raise _violation(f"{key} must be supplied as a secret:// reference")
    forbidden = sorted(key for key in FORBIDDEN_ENVIRONMENT_NAMES if key in values)
    if forbidden:
        raise _violation(f"forbidden environment credentials: {', '.join(forbidden)}")
    unexpected = sorted(
        key
        for key in values
        if key.endswith(("_API_KEY", "_PASSWORD", "_SECRET", "_TOKEN"))
        and key not in SECRET_ENVIRONMENT
        and not key.endswith("_FILE")
    )
    if unexpected:
        raise _violation(f"unexpected environment credentials: {', '.join(unexpected)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the hardened local deployment profile")
    parser.add_argument("--compose", default=PROFILE_FILE, help="Compose profile to validate")
    parser.add_argument("--check-settings", action="store_true")
    args = parser.parse_args()
    if args.check_settings:
        validate_hardened_environment()
        validate_hardened_settings(get_settings())
        # The runtime image contains the application and migrations, not the host's
        # Compose file. Static topology validation runs on the host before Compose.
        if Path(args.compose).exists():
            load_hardened_compose(args.compose)
    else:
        load_hardened_compose(args.compose)
    print("hardened deployment profile: ready")


if __name__ == "__main__":
    main()
