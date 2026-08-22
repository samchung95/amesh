from __future__ import annotations

import json
import os
import re
from contextlib import suppress
from pathlib import Path
from typing import Protocol, cast

import keyring
from keyring.errors import KeyringError
from pydantic import BaseModel, ConfigDict, Field

_SERVICE_NAME = "amesh-cli"
_PROFILE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class CliProfile(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    api_url: str = Field(default="http://127.0.0.1:8000", alias="apiUrl")
    tenant: str = "default"


class CliConfiguration(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_version: int = Field(default=1, alias="schemaVersion")
    active_profile: str = Field(default="default", alias="activeProfile")
    profiles: dict[str, CliProfile] = Field(default_factory=dict)

    def profile(self, name: str | None = None) -> tuple[str, CliProfile]:
        selected = name or self.active_profile
        validate_profile_name(selected)
        return selected, self.profiles.get(selected, CliProfile())


class CredentialStore(Protocol):
    def get(self, profile: str) -> str | None: ...

    def set(self, profile: str, token: str) -> None: ...

    def delete(self, profile: str) -> None: ...


class KeyringCredentialStore:
    def get(self, profile: str) -> str | None:
        validate_profile_name(profile)
        try:
            return keyring.get_password(_SERVICE_NAME, profile)
        except KeyringError as exc:
            raise RuntimeError(
                f"operating-system credential storage is unavailable: {exc}"
            ) from exc

    def set(self, profile: str, token: str) -> None:
        validate_profile_name(profile)
        if not token:
            raise ValueError("credential token must not be empty")
        try:
            keyring.set_password(_SERVICE_NAME, profile, token)
        except KeyringError as exc:
            raise RuntimeError(
                f"operating-system credential storage is unavailable: {exc}"
            ) from exc

    def delete(self, profile: str) -> None:
        validate_profile_name(profile)
        try:
            if keyring.get_password(_SERVICE_NAME, profile) is not None:
                keyring.delete_password(_SERVICE_NAME, profile)
        except KeyringError as exc:
            raise RuntimeError(
                f"operating-system credential storage is unavailable: {exc}"
            ) from exc


def default_cli_config_path() -> Path:
    overridden = os.getenv("AMESH_CONFIG_PATH")
    if overridden:
        return Path(overridden).expanduser()
    if os.name == "nt":
        root = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "amesh" / "config.json"


def load_cli_configuration(path: Path) -> CliConfiguration:
    if not path.exists():
        return CliConfiguration()
    try:
        return CliConfiguration.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"invalid CLI configuration {path}: {exc}") from exc


def save_cli_configuration(path: Path, configuration: CliConfiguration) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(
        configuration.model_dump_json(indent=2, by_alias=True) + "\n",
        encoding="utf-8",
    )
    with suppress(OSError):
        temporary.chmod(0o600)
    temporary.replace(path)


def validate_profile_name(value: str) -> str:
    if not _PROFILE_PATTERN.fullmatch(value):
        raise ValueError(
            "profile name must contain 1-64 letters, digits, dots, underscores or hyphens"
        )
    return value


def public_configuration(configuration: CliConfiguration) -> dict[str, object]:
    return cast(dict[str, object], json.loads(configuration.model_dump_json(by_alias=True)))
