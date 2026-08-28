from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.dsl.models import FlowDefinition


class FormField(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_.-]{0,127}$")
    type: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=256)
    help_text: str = Field(default="", alias="helpText", max_length=2048)
    required: bool = False
    sensitive: bool = False
    placeholder: str | None = Field(default=None, max_length=512)
    default: Any | None = None
    options: tuple[Any, ...] = ()
    validation: dict[str, Any] = Field(default_factory=dict)
    schema_: dict[str, Any] = Field(default_factory=dict, alias="schema")


class FormSection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    title: str = Field(min_length=1, max_length=256)
    help_text: str = Field(default="", alias="helpText", max_length=2048)
    columns: int = Field(default=1, ge=1, le=3)
    fields: tuple[str, ...] = Field(min_length=1)


class AppForm(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    fields: tuple[FormField, ...] = ()
    layout: tuple[FormSection, ...] = ()

    @model_validator(mode="after")
    def validate_layout(self) -> AppForm:
        field_ids = [field.id for field in self.fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("form field IDs must be unique")
        placed = [field_id for section in self.layout for field_id in section.fields]
        unknown = sorted(set(placed) - set(field_ids))
        if unknown:
            raise ValueError("form layout references unknown fields: " + ", ".join(unknown))
        if len(placed) != len(set(placed)):
            raise ValueError("form fields may appear only once in layout")
        return self


class WorkflowAppSpec(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2048)
    flow_id: str = Field(alias="flowId", pattern=r"^[A-Za-z_][A-Za-z0-9_.-]{0,127}$")
    flow_revision: int | None = Field(default=None, alias="flowRevision", ge=1)
    form: AppForm | None = None
    embed_enabled: bool = Field(default=True, alias="embedEnabled")
    launch_label: str = Field(default="Run", alias="launchLabel", min_length=1, max_length=80)


class WorkflowAppUpsertRequest(WorkflowAppSpec):
    expected_version: int | None = Field(default=None, alias="expectedVersion", ge=1)


class WorkflowApp(WorkflowAppSpec):
    namespace: str
    app_id: str = Field(alias="appId", pattern=r"^[a-z][a-z0-9_.-]{0,127}$")
    revision: int = Field(ge=1)
    resource_version: int = Field(alias="resourceVersion", ge=1)
    form: AppForm
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")


class WorkflowAppLaunchRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    inputs: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey", max_length=512)


class HumanTaskState(StrEnum):
    OPEN = "OPEN"
    ESCALATED = "ESCALATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


class HumanTaskActionKind(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    COMMENT = "COMMENT"
    ATTACH = "ATTACH"
    DELEGATE = "DELEGATE"
    ESCALATE = "ESCALATE"

    @property
    def terminal(self) -> bool:
        return self in {
            HumanTaskActionKind.APPROVE,
            HumanTaskActionKind.REJECT,
            HumanTaskActionKind.REQUEST_CHANGES,
        }


class HumanTaskCreate(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    namespace: str
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=4096)
    form: AppForm = Field(default_factory=AppForm)
    assignee_ids: tuple[UUID, ...] = Field(default=(), alias="assigneeIds")
    group_ids: tuple[UUID, ...] = Field(default=(), alias="groupIds")
    deadline_at: datetime | None = Field(default=None, alias="deadlineAt")
    escalation_assignee_ids: tuple[UUID, ...] = Field(
        default=(), alias="escalationAssigneeIds"
    )
    escalation_group_ids: tuple[UUID, ...] = Field(default=(), alias="escalationGroupIds")

    @model_validator(mode="after")
    def require_participant(self) -> HumanTaskCreate:
        if not self.assignee_ids and not self.group_ids:
            raise ValueError("human approval requires at least one assignee or group")
        if self.deadline_at is not None and (
            self.deadline_at.tzinfo is None or self.deadline_at.utcoffset() is None
        ):
            raise ValueError("human approval deadline must include a timezone")
        return self


class HumanTaskActionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    action: HumanTaskActionKind
    idempotency_key: str = Field(alias="idempotencyKey", min_length=8, max_length=256)
    reason: str = Field(default="", max_length=4096)
    form_values: dict[str, Any] = Field(default_factory=dict, alias="formValues")
    comment: str = Field(default="", max_length=16_384)
    artifact_uri: str | None = Field(default=None, alias="artifactUri", max_length=4096)
    assignee_ids: tuple[UUID, ...] = Field(default=(), alias="assigneeIds")
    group_ids: tuple[UUID, ...] = Field(default=(), alias="groupIds")

    @model_validator(mode="after")
    def validate_action_payload(self) -> HumanTaskActionRequest:
        if self.action is HumanTaskActionKind.COMMENT and not self.comment:
            raise ValueError("COMMENT requires comment text")
        if self.action is HumanTaskActionKind.ATTACH and self.artifact_uri is None:
            raise ValueError("ATTACH requires artifactUri")
        if (
            self.action is HumanTaskActionKind.DELEGATE
            and not self.assignee_ids
            and not self.group_ids
        ):
            raise ValueError("DELEGATE requires at least one assignee or group")
        return self


class HumanTaskAction(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    action_id: UUID = Field(alias="actionId")
    action: HumanTaskActionKind
    actor_id: UUID | None = Field(alias="actorId")
    reason: str
    form_values: dict[str, Any] = Field(alias="formValues")
    comment: str
    artifact_uri: str | None = Field(alias="artifactUri")
    occurred_at: datetime = Field(alias="occurredAt")


class HumanTask(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    human_task_id: UUID = Field(alias="humanTaskId")
    namespace: str
    execution_id: UUID = Field(alias="executionId")
    task_run_id: UUID = Field(alias="taskRunId")
    attempt: int
    title: str
    description: str
    form: AppForm
    assignee_ids: tuple[UUID, ...] = Field(alias="assigneeIds")
    group_ids: tuple[UUID, ...] = Field(alias="groupIds")
    deadline_at: datetime | None = Field(alias="deadlineAt")
    state: HumanTaskState
    version: int
    created_at: datetime = Field(alias="createdAt")
    decided_by: UUID | None = Field(alias="decidedBy")
    decided_at: datetime | None = Field(alias="decidedAt")
    reason: str
    form_values: dict[str, Any] = Field(alias="formValues")
    actions: tuple[HumanTaskAction, ...] = ()


class HumanTaskNotification(BaseModel):
    """Participant-safe notification; execution identifiers and form values are excluded."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    notification_id: UUID = Field(alias="notificationId")
    human_task_id: UUID = Field(alias="humanTaskId")
    kind: str
    title: str
    message: str
    deadline_at: datetime | None = Field(alias="deadlineAt")
    created_at: datetime = Field(alias="createdAt")
    read_at: datetime | None = Field(alias="readAt")


def form_from_flow(flow: FlowDefinition) -> AppForm:
    fields: list[FormField] = []
    for definition in flow.inputs:
        input_type = definition.type.lower()
        control = {
            "bool": "checkbox",
            "boolean": "checkbox",
            "int": "number",
            "integer": "number",
            "float": "number",
            "number": "number",
            "date": "date",
            "datetime": "datetime-local",
            "file": "file",
            "object": "json",
            "json": "json",
            "array": "json",
            "secret": "password",
        }.get(input_type, "select" if definition.values else "text")
        fields.append(
            FormField(
                id=definition.id,
                type=control,
                label=definition.display_name or definition.id.replace("_", " ").title(),
                helpText=definition.description or "",
                required=definition.required,
                sensitive=definition.sensitive or input_type == "secret",
                placeholder=definition.placeholder,
                default=(definition.default if definition.has_default else definition.prefill),
                options=definition.values,
                validation=definition.validation,
                schema=definition.value_schema,
            )
        )
    layout = (
        FormSection(title="Inputs", fields=tuple(field.id for field in fields))
        if fields
        else None
    )
    return AppForm(fields=tuple(fields), layout=(layout,) if layout is not None else ())


def terminal_state(action: HumanTaskActionKind) -> HumanTaskState:
    return {
        HumanTaskActionKind.APPROVE: HumanTaskState.APPROVED,
        HumanTaskActionKind.REJECT: HumanTaskState.REJECTED,
        HumanTaskActionKind.REQUEST_CHANGES: HumanTaskState.CHANGES_REQUESTED,
    }[action]


def utc_now() -> datetime:
    return datetime.now(UTC)
