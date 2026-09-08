"""Runtime input models for built-in task handlers and their authoring schemas.

Typed dictionaries retain absent optional fields so each handler's existing
defaults remain authoritative. The executor validates these models after rendering.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal, Required, TypedDict
from uuid import UUID

from pydantic import ConfigDict, Field, with_config

from amesh.domain.human_tasks import AppForm
from amesh.domain.runner import RunnerExtension, RunnerNetworkPolicy, RunnerSecurityPolicy
from amesh.domain.scripts import ScriptDependency, ScriptSource
from amesh.plugin_sdk import DocumentArtifactRef, DocumentExtractionLimits

NonEmptyText = Annotated[str, Field(min_length=1)]
WorkspacePath = Annotated[str, Field(min_length=1, max_length=4096)]
PositiveNumber = Annotated[float, Field(gt=0)]
PositiveInteger = Annotated[int, Field(ge=1)]
UniquePaths = Annotated[list[WorkspacePath], Field(json_schema_extra={"uniqueItems": True})]
UniqueIds = Annotated[list[UUID], Field(json_schema_extra={"uniqueItems": True})]
_DISABLED_TIMEOUT_CONSTRAINT: dict[str, Any] = {
    "if": {"properties": {"timeoutMode": {"const": "DISABLED"}}, "required": ["timeoutMode"]},
    "then": {"not": {"required": ["timeoutSeconds"]}},
}


@with_config(extra="forbid")
class HandlerConfiguration(TypedDict, total=False):
    pass


class TimedConfiguration(HandlerConfiguration, total=False):
    timeoutSeconds: PositiveNumber


class WorkspaceConfiguration(HandlerConfiguration, total=False):
    inputFiles: dict[str, str]
    outputFiles: UniquePaths
    outputManifest: WorkspacePath
    workspaceQuotaBytes: PositiveInteger
    retainDiagnosticsOnFailure: bool


class RunnerConfiguration(WorkspaceConfiguration, TimedConfiguration, total=False):
    image: NonEmptyText
    environment: dict[str, str]
    resources: dict[str, Any]
    taskRunner: RunnerExtension
    runnerCredentials: dict[str, str]
    networkPolicy: RunnerNetworkPolicy
    securityPolicy: RunnerSecurityPolicy


class ShellConfiguration(RunnerConfiguration, total=False):
    command: Required[Annotated[list[str], Field(min_length=1)]]
    stdin: str


class ScriptConfiguration(RunnerConfiguration, total=False):
    source: Required[ScriptSource]
    args: list[str]
    interpreter: Annotated[list[NonEmptyText], Field(min_length=1)]
    dependencies: list[ScriptDependency]
    dependencyCommand: Annotated[list[NonEmptyText], Field(min_length=1)]


class SleepConfiguration(HandlerConfiguration):
    seconds: Annotated[float, Field(ge=0, le=86_400)]


class FailConfiguration(HandlerConfiguration, total=False):
    message: NonEmptyText


class AssertConfiguration(FailConfiguration, total=False):
    # Expressions are rendered before _run_assert enforces the boolean result.
    value: Required[Any]


class DebugConfiguration(HandlerConfiguration, total=False):
    include: Annotated[
        list[Literal["inputs", "outputs", "variables", "labels", "trigger", "iteration", "files"]],
        Field(json_schema_extra={"uniqueItems": True}),
    ]


@with_config(
    extra="forbid",
    json_schema_extra={"anyOf": [{"required": ["input"]}, {"required": ["value"]}]},
)
class DataConfiguration(TimedConfiguration, total=False):
    input: Any
    value: Any
    maxPayloadBytes: Annotated[int, Field(ge=1, le=10_485_760)]
    delimiter: Annotated[str, Field(min_length=1, max_length=1)]
    search: str
    replacement: str
    separator: str


class SerializedDataConfiguration(DataConfiguration, total=False):
    operation: Literal["parse", "serialize"]


class TextDataConfiguration(DataConfiguration, total=False):
    operation: Literal["trim", "upper", "lower", "replace", "split", "join"]


class HttpAuthentication(HandlerConfiguration, total=False):
    type: Required[Literal["bearer", "basic", "apiKey"]]
    token: NonEmptyText
    username: NonEmptyText
    password: NonEmptyText
    name: NonEmptyText
    value: NonEmptyText
    in_: Annotated[Literal["header", "query"], Field(alias="in")]


class HttpPagination(HandlerConfiguration, total=False):
    nextUrlPath: Required[NonEmptyText]
    itemsPath: NonEmptyText
    maxPages: PositiveInteger


class HttpConfiguration(TimedConfiguration, total=False):
    url: Required[NonEmptyText]
    method: NonEmptyText
    headers: dict[str, str]
    query: dict[str, str]
    auth: HttpAuthentication
    body: Any
    pagination: HttpPagination
    maxResponseBytes: PositiveInteger


class DownloadConfiguration(HttpConfiguration, WorkspaceConfiguration, total=False):
    destination: Required[WorkspacePath]


class FileSourceConfiguration(WorkspaceConfiguration, TimedConfiguration, total=False):
    source: Required[WorkspacePath]


class FileCopyConfiguration(FileSourceConfiguration, total=False):
    destination: Required[WorkspacePath]


class FileChecksumConfiguration(FileSourceConfiguration, total=False):
    algorithm: Literal["sha256", "sha512"]


class CompressConfiguration(WorkspaceConfiguration, TimedConfiguration, total=False):
    sources: Required[Annotated[UniquePaths, Field(min_length=1)]]
    destination: Required[WorkspacePath]


class ExtractConfiguration(FileCopyConfiguration, total=False):
    maxEntries: Annotated[int, Field(ge=1, le=10_000)]
    maxUncompressedBytes: Annotated[int, Field(ge=1, le=104_857_600)]


class DocumentExtractConfiguration(HandlerConfiguration, total=False):
    source: Required[WorkspacePath]
    artifact: Required[DocumentArtifactRef]
    limits: Required[DocumentExtractionLimits]
    inputFiles: Required[dict[str, str]]
    outputFiles: UniquePaths
    workspaceQuotaBytes: PositiveInteger


class EmailAuthentication(HandlerConfiguration):
    username: NonEmptyText
    password: NonEmptyText


class EmailConfiguration(TimedConfiguration, total=False):
    smtpHost: Required[NonEmptyText]
    smtpPort: Annotated[int, Field(ge=1, le=65_535)]
    sender: Required[Annotated[str, Field(min_length=3)]]
    recipients: Required[Annotated[list[Annotated[str, Field(min_length=3)]], Field(min_length=1)]]
    subject: Required[NonEmptyText]
    text: Required[Annotated[str, Field(min_length=1, max_length=1_048_576)]]
    startTls: bool
    auth: EmailAuthentication


@with_config(
    extra="forbid",
    json_schema_extra={
        "anyOf": [{"required": ["assigneeIds"]}, {"required": ["groupIds"]}],
        "not": {"required": ["deadlineAt", "deadlineSeconds"]},
    },
)
class ApprovalConfiguration(HandlerConfiguration, total=False):
    title: Annotated[str, Field(min_length=1, max_length=256)]
    description: Annotated[str, Field(max_length=4096)]
    form: AppForm
    assigneeIds: UniqueIds
    groupIds: UniqueIds
    deadlineAt: datetime
    deadlineSeconds: Annotated[float, Field(gt=0, le=31_536_000)]
    escalationAssigneeIds: UniqueIds
    escalationGroupIds: UniqueIds


@with_config(
    extra="forbid",
    json_schema_extra={
        "anyOf": [{"required": ["endpoint"]}, {"required": ["connection"]}],
        "allOf": [_DISABLED_TIMEOUT_CONSTRAINT],
    },
)
class McpConfiguration(TimedConfiguration, total=False):
    endpoint: NonEmptyText
    connection: NonEmptyText
    revision: PositiveInteger
    tool: Required[NonEmptyText]
    arguments: dict[str, Any]
    allowWrite: bool
    approvalTask: NonEmptyText
    dataHandling: Literal["DENY_SECRETS", "REDACT_SECRETS", "ALLOW"]
    timeoutMode: Literal["BOUNDED", "DISABLED"]


def handler_configuration_models() -> dict[str, Any]:
    """Return actual handler input types; flowables keep their executor-owned contracts."""
    from amesh.domain import AgentHandoffRequest, AgentRouteRequest
    from amesh.dsl.models import TaskTimeoutMode

    from .session import _AgentSessionTaskSpec

    # These handlers consume their existing domain models after task controls have
    # been separated by TaskConfiguration.handler_view().
    class RouteConfiguration(AgentRouteRequest):
        timeout_seconds: float | None = Field(default=None, alias="timeoutSeconds", gt=0)

    class HandoffConfiguration(AgentHandoffRequest):
        timeout_seconds: float | None = Field(default=None, alias="timeoutSeconds", gt=0)

    class SessionConfiguration(_AgentSessionTaskSpec):
        model_config = ConfigDict(
            json_schema_extra={
                "allOf": [_DISABLED_TIMEOUT_CONSTRAINT],
                "dependentRequired": {
                    field: ["meshId", "memberId", "meshBudget"]
                    for field in ("meshId", "memberId", "meshBudget")
                },
            }
        )
        timeout_seconds: float | None = Field(default=None, alias="timeoutSeconds", gt=0)
        timeout_mode: TaskTimeoutMode = Field(default=TaskTimeoutMode.BOUNDED, alias="timeoutMode")

    return {
        "core.shell": ShellConfiguration,
        **{
            f"script.{language}": ScriptConfiguration
            for language in ("python", "node", "shell", "powershell", "r", "java")
        },
        "core.sleep": SleepConfiguration,
        "core.fail": FailConfiguration,
        "core.assert": AssertConfiguration,
        "core.debug": DebugConfiguration,
        **{
            f"core.data.{format_name}": SerializedDataConfiguration
            for format_name in ("json", "yaml", "csv", "xml")
        },
        "core.data.text": TextDataConfiguration,
        "core.http": HttpConfiguration,
        "core.download": DownloadConfiguration,
        "core.notify.webhook": HttpConfiguration,
        "core.notify.email": EmailConfiguration,
        "core.files.copy": FileCopyConfiguration,
        "core.files.move": FileCopyConfiguration,
        "core.files.delete": FileSourceConfiguration,
        "core.files.checksum": FileChecksumConfiguration,
        "core.files.compress": CompressConfiguration,
        "core.files.extract": ExtractConfiguration,
        "core.document.extract": DocumentExtractConfiguration,
        "core.approval": ApprovalConfiguration,
        "agent.mcp": McpConfiguration,
        "agent.route": RouteConfiguration,
        "agent.handoff": HandoffConfiguration,
        "agent.session": SessionConfiguration,
    }
