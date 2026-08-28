from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCRIPT_TASK_TYPES = frozenset(
    {
        "script.shell",
        "script.python",
        "script.node",
        "script.java",
        "script.r",
        "script.powershell",
    }
)

_IMMUTABLE_IMAGE = re.compile(r"^[^\s@]+@sha256:[0-9a-f]{64}$")
_DEFAULT_IMAGES = {
    "shell": (
        "docker.io/library/alpine"
        "@sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1"
    ),
    "python": (
        "docker.io/library/python"
        "@sha256:5f55cdf0c5d9dc1a415637a5ccc4a9e18663ad203673173b8cda8f8dcacef689"
    ),
    "node": (
        "docker.io/library/node"
        "@sha256:4a4884e8a44826194dff92ba316264f392056cbe243dcc9fd3551e71cea02b90"
    ),
    "java": (
        "docker.io/library/eclipse-temurin"
        "@sha256:7d1d666ddafac14da0ded6b4b076becf76cf88b31f9d7953a76555cc82f86511"
    ),
    "r": (
        "docker.io/library/r-base"
        "@sha256:fa1972f31def171b83e0911e947ab8b57db143f0fc8a67af4c0d5ac329041646"
    ),
    "powershell": (
        "mcr.microsoft.com/powershell"
        "@sha256:a3affe99603400235501b8da8be5f9e40152d4db6557f698a91da0280f9e1469"
    ),
}


class ScriptDependency(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=512)
    version: str = Field(min_length=1, max_length=512)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ScriptSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    type: Literal["inline", "namespace", "repository", "package"]
    content: str | None = Field(default=None, max_length=1_048_576)
    path: str | None = Field(default=None, max_length=4096)

    @model_validator(mode="after")
    def validate_variant(self) -> ScriptSource:
        if self.type == "inline":
            if self.content is None or self.path is not None:
                raise ValueError("inline script source requires content and prohibits path")
            return self
        if self.path is None or self.content is not None:
            raise ValueError(f"{self.type} script source requires path and prohibits content")
        _validate_workspace_path(self.path)
        return self


class ScriptTaskPolicy(BaseModel):
    """Operator-owned image and runtime dependency policy for first-party script tasks."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    default_images: dict[str, str] = Field(
        default_factory=lambda: dict(_DEFAULT_IMAGES),
        alias="defaultImages",
    )
    approved_images: dict[str, tuple[str, ...]] = Field(
        default_factory=dict,
        alias="approvedImages",
    )
    dependency_installation_enabled: bool = Field(
        default=False,
        alias="dependencyInstallationEnabled",
    )
    dependency_allowed_egress: tuple[str, ...] = Field(
        default=(),
        alias="dependencyAllowedEgress",
    )

    @model_validator(mode="after")
    def validate_images(self) -> ScriptTaskPolicy:
        missing = set(_DEFAULT_IMAGES).difference(self.default_images)
        unknown = set(self.default_images).union(self.approved_images).difference(_DEFAULT_IMAGES)
        if missing or unknown:
            details = []
            if missing:
                details.append("missing " + ", ".join(sorted(missing)))
            if unknown:
                details.append("unknown " + ", ".join(sorted(unknown)))
            raise ValueError("script image policy language mismatch: " + "; ".join(details))
        images = tuple(self.default_images.values()) + tuple(
            image for values in self.approved_images.values() for image in values
        )
        invalid = sorted(image for image in images if not _IMMUTABLE_IMAGE.fullmatch(image))
        if invalid:
            raise ValueError("script images must use immutable sha256 digests")
        return self


def script_catalog_schema() -> dict[str, Any]:
    return {
        "source": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "type": {"const": "inline"},
                        "content": {"type": "string", "maxLength": 1_048_576},
                    },
                    "required": ["type", "content"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "type": {"enum": ["namespace", "repository", "package"]},
                        "path": {"type": "string", "minLength": 1, "maxLength": 4096},
                    },
                    "required": ["type", "path"],
                    "additionalProperties": False,
                },
            ]
        },
        "args": {"type": "array", "items": {"type": "string"}},
        "interpreter": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
        "dependencies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "version": {"type": "string", "minLength": 1},
                    "digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
                },
                "required": ["name", "version", "digest"],
                "additionalProperties": False,
            },
        },
        "dependencyCommand": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
    }


def _validate_workspace_path(value: str) -> None:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("script source path must be a safe relative workspace path")
