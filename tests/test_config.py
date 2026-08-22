import asyncio
import json
import logging
import socket
from pathlib import Path

import pytest
from fastapi import HTTPException

from amesh.app import authenticate_bearer_actor
from amesh.config import (
    ConfigurationLoadError,
    ConfigurationManager,
    NonReloadableConfigurationChanged,
    Settings,
    load_configuration,
    redact_runtime_text,
    security_baseline_findings,
)
from amesh.observability import JsonFormatter
from amesh.ports import StorageBackend
from amesh.storage.factory import build_object_store


def test_reference_configuration_is_postgresql_only() -> None:
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert not hasattr(settings, "nats_url")
    assert settings.object_storage_bucket == "amesh"
    assert settings.object_storage_backend == "s3"
    assert settings.object_storage_gc_safety_window_seconds == 86_400
    assert settings.database_pool_size == 10
    assert settings.database_prepared_statement_cache_size == 100
    assert settings.core_http_allowed_private_hosts == ()
    assert settings.core_http_max_response_bytes == 10 * 1024 * 1024


def test_database_urls_require_the_async_postgresql_driver() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(_env_file=None, database_url="sqlite+aiosqlite:///amesh.db")
    with pytest.raises(ValueError, match="DATABASE_READ_REPLICA_URL"):
        Settings(
            _env_file=None,
            database_read_replica_url="mysql+asyncmy://amesh@replica/amesh",
        )


def test_development_bootstrap_token_fails_closed_outside_development() -> None:
    with pytest.raises(ValueError, match="development authentication"):
        Settings(
            _env_file=None,
            app_env="production",
            auth_mode="development",
            amesh_admin_token="test-token",
            amesh_token_pepper="test-production-pepper",
        )

    settings = Settings(
        _env_file=None,
        app_env="production",
        auth_mode="credentials",
        amesh_admin_token="test-token",
        amesh_token_pepper="test-production-pepper",
        object_storage_workload_identity=True,
        webhook_signing_key="external-webhook-signing-key-at-least-32-bytes",
    )
    with pytest.raises(HTTPException) as caught:
        asyncio.run(authenticate_bearer_actor(settings, None, "Bearer test-token"))
    assert caught.value.status_code == 401


def test_object_storage_backend_configuration_and_workload_identity() -> None:
    azure = Settings(
        _env_file=None,
        object_storage_backend="azure",
        object_storage_azure_account_url="https://account.blob.core.windows.net",
        object_storage_workload_identity=True,
        object_storage_encryption_key_id="scope-a",
        object_storage_proxy_url="http://proxy.internal:8080",
        object_storage_ca_file="/etc/amesh/storage-ca.pem",
    )
    gcs = Settings(
        _env_file=None,
        object_storage_backend="gcs",
        object_storage_workload_identity=True,
        object_storage_gcs_project="project-a",
        object_storage_gcs_endpoint="https://storage.private.example",
    )

    assert build_object_store(azure).backend is StorageBackend.AZURE
    assert build_object_store(gcs).backend is StorageBackend.GCS
    with pytest.raises(ValueError, match="AZURE_ACCOUNT_URL"):
        Settings(_env_file=None, object_storage_backend="azure")
    with pytest.raises(ValueError, match="GCS requires workload identity"):
        Settings(_env_file=None, object_storage_backend="gcs")


def test_layered_configuration_precedence_secret_references_and_redaction(
    tmp_path: Path,
) -> None:
    secret_directory = tmp_path / "secrets"
    secret_directory.mkdir()
    (secret_directory / "pepper").write_text("canary-pepper-value\n", encoding="utf-8")
    first = tmp_path / "first.yaml"
    first.write_text(
        "app_port: 7000\namesh_token_pepper: secret://pepper\nlog_level: WARNING\n",
        encoding="utf-8",
    )
    second = tmp_path / "second.json"
    second.write_text('{"app_port": 7001, "log_level": "ERROR"}', encoding="utf-8")

    loaded = load_configuration(
        config_files=(first, second),
        environment={"APP_PORT": "7002", "AMESH_SECRETS_DIR": str(secret_directory)},
        argv=("--set", "APP_PORT=7003", "--set=LOG_LEVEL=DEBUG"),
    )

    assert loaded.settings.app_port == 7003
    assert loaded.settings.log_level == "DEBUG"
    assert loaded.settings.amesh_token_pepper.get_secret_value() == "canary-pepper-value"
    snapshot = loaded.snapshot(1)
    entries = {entry.name: entry for entry in snapshot.entries}
    assert entries["app_port"].source == "command-line"
    assert entries["amesh_token_pepper"].value == "[REDACTED]"
    assert "canary-pepper-value" not in snapshot.model_dump_json()
    assert redact_runtime_text("failed canary-pepper-value") == "failed [REDACTED]"
    record = logging.LogRecord(
        "amesh.test",
        logging.ERROR,
        __file__,
        1,
        "failed canary-pepper-value",
        (),
        None,
    )
    rendered_log = JsonFormatter().format(record)
    assert "canary-pepper-value" not in rendered_log
    assert "[REDACTED]" in rendered_log


def test_configuration_rejects_unknown_missing_secret_and_unsafe_combinations(
    tmp_path: Path,
) -> None:
    unknown = tmp_path / "unknown.yaml"
    unknown.write_text("not_a_setting: true\n", encoding="utf-8")
    with pytest.raises(ConfigurationLoadError, match="unknown configuration"):
        load_configuration(config_files=(unknown,), environment={})
    with pytest.raises(ConfigurationLoadError, match="AMESH_SECRETS_DIR"):
        load_configuration(
            environment={"AMESH_TOKEN_PEPPER": "secret://missing"},
        )
    with pytest.raises(ConfigurationLoadError, match="configuration validation failed") as caught:
        load_configuration(
            environment={
                "APP_ENV": "production",
                "AUTH_MODE": "development",
                "AMESH_TOKEN_PEPPER": "canary-production-pepper",
            }
        )
    assert "canary-production-pepper" not in str(caught.value)


def test_reload_is_atomic_and_limited_to_explicit_reloadable_settings() -> None:
    candidates = [
        load_configuration(environment={"LOG_LEVEL": "INFO"}),
        load_configuration(environment={"LOG_LEVEL": "DEBUG"}),
        load_configuration(environment={"APP_PORT": "9000", "LOG_LEVEL": "WARNING"}),
    ]
    manager = ConfigurationManager(lambda: candidates.pop(0))

    reloaded = manager.reload()
    assert reloaded.version == 2
    assert manager.settings.log_level == "DEBUG"
    with pytest.raises(NonReloadableConfigurationChanged) as caught:
        manager.reload()
    assert caught.value.fields == ("app_port",)
    assert manager.settings.log_level == "DEBUG"
    assert manager.settings.app_port == 8000


def test_docker_runner_complex_environment_settings_are_json() -> None:
    loaded = load_configuration(
        environment={
            "DOCKER_IMAGE_POLICY": (
                '{"allowedRegistries":["registry.example"],"allowTags":true,'
                '"requireSignature":true}'
            ),
            "DOCKER_SIGNATURE_VERIFICATION_COMMAND": '["cosign","verify","{image}"]',
        }
    )

    assert loaded.settings.docker_image_policy.allowed_registries == ("registry.example",)
    assert loaded.settings.docker_image_policy.allow_tags
    assert loaded.settings.docker_image_policy.require_signature
    assert loaded.settings.docker_signature_verification_command == (
        "cosign",
        "verify",
        "{image}",
    )


def test_plugin_discovery_sources_are_typed_json_configuration(tmp_path: Path) -> None:
    loaded = load_configuration(
        environment={
            "PLUGIN_DIRECTORIES": json.dumps([str(tmp_path / "plugins")]),
            "PLUGIN_REGISTRIES": json.dumps([str(tmp_path / "registry.json")]),
            "PLUGIN_INSTALL_ROOT": str(tmp_path / "installed"),
            "PLUGIN_REGISTRY_ROOT": str(tmp_path / "self-hosted"),
            "PLUGIN_REGISTRY_TIMEOUT_SECONDS": "15",
            "PLUGIN_REGISTRY_SIGNING_KEY_ID": "test-key",
            "PLUGIN_REGISTRY_SIGNING_KEY": "test-registry-signing-key-at-least-32-bytes",
            "PLUGIN_REGISTRY_ALLOWED_ORIGINS": '["https://registry.example"]',
            "PLUGIN_REGISTRY_MIRRORS": (
                '{"https://registry.example":"https://mirror.internal"}'
            ),
            "PLUGIN_REGISTRY_PROXY_URL": "http://proxy.internal:8080",
        }
    )

    assert loaded.settings.plugin_directories == (str(tmp_path / "plugins"),)
    assert loaded.settings.plugin_registries == (str(tmp_path / "registry.json"),)
    assert loaded.settings.plugin_install_root == str(tmp_path / "installed")
    assert loaded.settings.plugin_registry_root == str(tmp_path / "self-hosted")
    assert loaded.settings.plugin_registry_timeout_seconds == 15
    assert loaded.settings.plugin_registry_signing_key_id == "test-key"
    assert loaded.settings.plugin_registry_allowed_origins == ("https://registry.example",)
    assert loaded.settings.plugin_registry_mirrors == {
        "https://registry.example": "https://mirror.internal"
    }
    assert loaded.settings.plugin_registry_proxy_url == "http://proxy.internal:8080"


def test_core_http_policy_is_typed_and_operator_bounded() -> None:
    loaded = load_configuration(
        environment={
            "CORE_HTTP_ALLOWED_PRIVATE_HOSTS": '["hooks.internal","127.0.0.1"]',
            "CORE_HTTP_MAX_RESPONSE_BYTES": "2097152",
            "CORE_HTTP_MAX_PAGES": "20",
            "CORE_HTTP_MAX_REDIRECTS": "2",
        }
    )

    assert loaded.settings.core_http_allowed_private_hosts == (
        "hooks.internal",
        "127.0.0.1",
    )
    assert loaded.settings.core_http_max_response_bytes == 2_097_152
    assert loaded.settings.core_http_max_pages == 20
    assert loaded.settings.core_http_max_redirects == 2


def test_renamed_settings_are_migrated_with_a_safe_warning(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.yaml"
    legacy.write_text("telemetry_enabled: true\n", encoding="utf-8")

    with pytest.warns(DeprecationWarning, match="TELEMETRY_ENABLED"):
        loaded = load_configuration(config_files=(legacy,), environment={})

    assert loaded.settings.product_telemetry_enabled
    assert loaded.warnings == (
        "TELEMETRY_ENABLED is deprecated; migrated to PRODUCT_TELEMETRY_ENABLED",
    )


def test_production_security_baseline_and_offline_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    secure = Settings(
        _env_file=None,
        app_env="production",
        auth_mode="credentials",
        amesh_token_pepper="external-production-pepper",
        object_storage_workload_identity=True,
        plugin_trust_mode="signed-only",
        plugin_registry_signing_key="external-registry-signing-key-at-least-32-bytes",
        webhook_signing_key="external-webhook-signing-key-at-least-32-bytes",
    )
    assert security_baseline_findings(secure) == ()

    def reject_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("configuration loading attempted an outbound connection")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    offline = load_configuration(environment={}).settings
    assert not offline.product_telemetry_enabled
    assert not offline.product_update_checks_enabled
