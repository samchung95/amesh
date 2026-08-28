from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PluginErrorPhase(StrEnum):
    CONFIGURATION = "CONFIGURATION"
    COMPATIBILITY = "COMPATIBILITY"
    CAPABILITY = "CAPABILITY"
    RUNTIME = "RUNTIME"


class PluginErrorDetail(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    code: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,127}$")
    message: str = Field(min_length=1, max_length=4096)
    phase: PluginErrorPhase
    path: tuple[str | int, ...] = ()
    hint: str | None = Field(default=None, max_length=4096)
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class PluginContractError(ValueError):
    def __init__(self, *errors: PluginErrorDetail) -> None:
        if not errors:
            raise ValueError("PluginContractError requires at least one structured error")
        self.errors = errors
        super().__init__("; ".join(item.message for item in errors))
