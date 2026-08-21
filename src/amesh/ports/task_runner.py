from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class RunnerRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: str
    execution_id: str
    task_run_id: str
    attempt_id: str
    fencing_token: int = Field(ge=1)
    command: list[str]
    image: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    input_files: dict[str, str] = Field(default_factory=dict)
    resource_limits: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float | None = Field(default=None, gt=0)
    cancel_grace_seconds: float = Field(default=1, ge=0)


class RunnerStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class StaleRunnerAttemptError(RuntimeError):
    """Raised when cancellation targets an inactive or superseded runner attempt."""


class RunnerResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    exit_code: int | None
    status: RunnerStatus
    outputs: dict[str, Any] = Field(default_factory=dict)
    artifact_uris: list[str] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class TaskRunner(Protocol):
    async def run(self, request: RunnerRequest) -> RunnerResult: ...

    async def cancel(self, attempt_id: str, fencing_token: int) -> None: ...
