from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InputDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=256)
    required: bool = False
    default: Any | None = None
    description: str | None = None
    sensitive: bool = False


class TriggerDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=512)
    disabled: bool = False


class TaskDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=512)
    description: str | None = None
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    run_if: str | None = Field(default=None, alias="runIf")
    tasks: list["TaskDefinition"] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_self_dependency(self) -> "TaskDefinition":
        if self.id in self.depends_on:
            raise ValueError(f"task {self.id!r} cannot depend on itself")
        return self


class FlowDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str = Field(min_length=1, max_length=128)
    namespace: str = Field(min_length=1, max_length=255)
    description: str | None = None
    revision: int = Field(default=1, ge=1)
    disabled: bool = False
    labels: dict[str, str] = Field(default_factory=dict)
    inputs: list[InputDefinition] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    tasks: list[TaskDefinition] = Field(min_length=1)
    triggers: list[TriggerDefinition] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[TaskDefinition] = Field(default_factory=list)
    finally_tasks: list[TaskDefinition] = Field(default_factory=list, alias="finally")

    @model_validator(mode="after")
    def validate_identifiers(self) -> "FlowDefinition":
        if not self.namespace or self.namespace.startswith(".") or self.namespace.endswith("."):
            raise ValueError("namespace must be a non-empty dotted identifier")
        if ".." in self.namespace:
            raise ValueError("namespace cannot contain empty segments")
        return self


class ValidationIssue(BaseModel):
    code: str
    message: str
    path: str
    severity: str = "error"


class FlowValidationResult(BaseModel):
    valid: bool
    semantic_hash: str | None = None
    canonical: dict[str, Any] | None = None
    issues: list[ValidationIssue] = Field(default_factory=list)
