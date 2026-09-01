from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.image_inputs import InputModality, contains_image_reference

from .contracts import PluginOperation, PluginRequest, PluginResponse, PluginSession
from .errors import PluginContractError, PluginErrorDetail, PluginErrorPhase
from .manifest import (
    PLUGIN_PROTOCOL_VERSION,
    ExtensionType,
    PluginEntryPoint,
    PluginFilesystemAccess,
    PluginManifest,
    PluginNetworkAccess,
)
from .schema import validate_configuration

PluginHandler = Callable[[PluginRequest], Awaitable[PluginResponse]]


def validate_task_input_modalities(
    entry_point: PluginEntryPoint,
    request: PluginRequest,
) -> tuple[PluginErrorDetail, ...]:
    """Reject governed image inputs before a task plugin handler can run."""

    if entry_point.type is not ExtensionType.TASK or request.operation is not PluginOperation.EXECUTE:
        return ()
    routed_values = (request.configuration, request.input, request.context)
    if not any(contains_image_reference(value) for value in routed_values):
        return ()
    if InputModality.IMAGE in entry_point.input_modalities:
        return ()
    return (
        PluginErrorDetail(
            code="plugin.capability.input_modality_denied",
            message=(
                f"task entry point {entry_point.resolved_resource_type!r} does not support image input"
            ),
            phase=PluginErrorPhase.CAPABILITY,
            hint="Declare image in the entry point inputModalities before routing image content.",
            details={
                "required": InputModality.IMAGE.value,
                "supported": sorted(item.value for item in entry_point.input_modalities),
            },
        ),
    )


class PluginCapabilityGrant(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    capabilities: tuple[str, ...] = ()
    network_access: PluginNetworkAccess = Field(
        default=PluginNetworkAccess.NONE,
        alias="networkAccess",
    )
    allowed_egress: tuple[str, ...] = Field(default=(), alias="allowedEgress")
    filesystem_access: PluginFilesystemAccess = Field(
        default=PluginFilesystemAccess.NONE,
        alias="filesystemAccess",
    )
    secret_scopes: tuple[str, ...] = Field(default=(), alias="secretScopes")


class PluginFixture(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    entry_point: str = Field(alias="entryPoint", min_length=1, max_length=255)
    operation: PluginOperation
    configuration: dict[str, Any] = Field(default_factory=dict)
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    expected_output: dict[str, Any] | None = Field(default=None, alias="expectedOutput")
    expected_error_codes: tuple[str, ...] = Field(default=(), alias="expectedErrorCodes")


class PluginFixtureResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    fixture: str
    passed: bool
    response: PluginResponse
    diagnostic: str | None = None


class PluginContractHarness:
    """Transport-neutral local harness for one validated plugin manifest."""

    def __init__(
        self,
        manifest: PluginManifest,
        handlers: Mapping[tuple[str, PluginOperation], PluginHandler],
        *,
        grant: PluginCapabilityGrant | None = None,
    ) -> None:
        self._manifest = manifest
        self._entry_points = {item.name: item for item in manifest.entry_points}
        self._handlers = dict(handlers)
        self._grant = grant or PluginCapabilityGrant()

    def validate_capabilities(self) -> tuple[PluginErrorDetail, ...]:
        declared = self._manifest.capabilities
        errors: list[PluginErrorDetail] = []
        missing = sorted(set(declared.required).difference(self._grant.capabilities))
        if missing:
            errors.append(
                PluginErrorDetail(
                    code="plugin.capability.missing",
                    message="plugin requires unavailable capabilities: " + ", ".join(missing),
                    phase=PluginErrorPhase.CAPABILITY,
                    hint="Grant the declared capabilities or reject this plugin version.",
                    details={"missing": missing},
                )
            )
        if (
            declared.network_access is PluginNetworkAccess.RESTRICTED
            and self._grant.network_access is PluginNetworkAccess.NONE
        ):
            errors.append(
                PluginErrorDetail(
                    code="plugin.capability.network_denied",
                    message="plugin requires restricted network access but the grant denies network",
                    phase=PluginErrorPhase.CAPABILITY,
                    hint="Grant only the declared egress destinations or reject the plugin.",
                )
            )
        disallowed_egress = sorted(
            set(declared.allowed_egress).difference(self._grant.allowed_egress)
        )
        if disallowed_egress:
            errors.append(
                PluginErrorDetail(
                    code="plugin.capability.egress_denied",
                    message="plugin requires unavailable egress destinations: "
                    + ", ".join(disallowed_egress),
                    phase=PluginErrorPhase.CAPABILITY,
                    details={"denied": disallowed_egress},
                )
            )
        if _filesystem_rank(declared.filesystem_access) > _filesystem_rank(
            self._grant.filesystem_access
        ):
            errors.append(
                PluginErrorDetail(
                    code="plugin.capability.filesystem_denied",
                    message=(
                        f"plugin requires {declared.filesystem_access.value} filesystem access"
                    ),
                    phase=PluginErrorPhase.CAPABILITY,
                )
            )
        missing_scopes = sorted(set(declared.secret_scopes).difference(self._grant.secret_scopes))
        if missing_scopes:
            errors.append(
                PluginErrorDetail(
                    code="plugin.capability.secret_scope_denied",
                    message="plugin requires unavailable secret scopes: "
                    + ", ".join(missing_scopes),
                    phase=PluginErrorPhase.CAPABILITY,
                    details={"missingScopes": missing_scopes},
                )
            )
        return tuple(errors)

    async def invoke(self, request: PluginRequest) -> PluginResponse:
        entry_point = self._entry_points.get(request.entry_point)
        errors: tuple[PluginErrorDetail, ...]
        if request.protocol_version not in self._manifest.compatibility.protocol_versions:
            errors = (
                PluginErrorDetail(
                    code="plugin.compatibility.protocol",
                    message=f"protocol {request.protocol_version!r} is not supported by the plugin",
                    phase=PluginErrorPhase.COMPATIBILITY,
                    hint="Use a protocol version declared by the plugin manifest.",
                ),
            )
        elif request.plugin != self._manifest.name:
            errors = (
                PluginErrorDetail(
                    code="plugin.compatibility.identity",
                    message=f"request targets plugin {request.plugin!r}, not this manifest",
                    phase=PluginErrorPhase.COMPATIBILITY,
                ),
            )
        elif entry_point is None:
            errors = (
                PluginErrorDetail(
                    code="plugin.configuration.entry_point_unknown",
                    message=f"plugin entry point {request.entry_point!r} is not declared",
                    phase=PluginErrorPhase.CONFIGURATION,
                    path=("entryPoint",),
                ),
            )
        else:
            errors = (
                self.validate_capabilities()
                + validate_configuration(entry_point, request.configuration)
                + validate_task_input_modalities(entry_point, request)
            )
        if errors:
            return PluginResponse(invocationId=request.session.invocation_id, errors=errors)

        handler = self._handlers.get((request.entry_point, request.operation))
        if handler is None:
            return PluginResponse(
                invocationId=request.session.invocation_id,
                errors=(
                    PluginErrorDetail(
                        code="plugin.runtime.operation_unsupported",
                        message=(
                            f"entry point {request.entry_point!r} does not implement "
                            f"operation {request.operation.value!r}"
                        ),
                        phase=PluginErrorPhase.RUNTIME,
                    ),
                ),
            )
        try:
            response = await handler(request)
        except PluginContractError as exc:
            return PluginResponse(
                invocationId=request.session.invocation_id,
                errors=exc.errors,
            )
        except Exception as exc:
            return PluginResponse(
                invocationId=request.session.invocation_id,
                errors=(
                    PluginErrorDetail(
                        code="plugin.runtime.unhandled",
                        message="plugin runtime failed",
                        phase=PluginErrorPhase.RUNTIME,
                        hint="Inspect isolated plugin logs using the invocation identifier.",
                        details={"exceptionType": type(exc).__name__},
                    ),
                ),
            )
        if response.invocation_id != request.session.invocation_id:
            return PluginResponse(
                invocationId=request.session.invocation_id,
                errors=(
                    PluginErrorDetail(
                        code="plugin.runtime.invocation_mismatch",
                        message="plugin response invocation identifier does not match the request",
                        phase=PluginErrorPhase.RUNTIME,
                    ),
                ),
            )
        return response

    async def run_fixture(self, fixture: PluginFixture) -> PluginFixtureResult:
        request = PluginRequest(
            protocolVersion=PLUGIN_PROTOCOL_VERSION,
            plugin=self._manifest.name,
            entryPoint=fixture.entry_point,
            operation=fixture.operation,
            session=PluginSession(tenantId="fixture", invocationId=f"fixture:{fixture.name}"),
            configuration=fixture.configuration,
            input=fixture.input,
            context=fixture.context,
        )
        response = await self.invoke(request)
        actual_codes = tuple(item.code for item in response.errors)
        if fixture.expected_error_codes:
            passed = actual_codes == fixture.expected_error_codes
            diagnostic = (
                None
                if passed
                else f"expected error codes {fixture.expected_error_codes}, got {actual_codes}"
            )
        else:
            passed = not actual_codes and (
                fixture.expected_output is None or response.output == fixture.expected_output
            )
            diagnostic = None if passed else "plugin fixture output did not match"
        return PluginFixtureResult(
            fixture=fixture.name,
            passed=passed,
            response=response,
            diagnostic=diagnostic,
        )


def extension_operation(extension_type: ExtensionType) -> PluginOperation:
    return {
        ExtensionType.TASK: PluginOperation.EXECUTE,
        ExtensionType.TRIGGER: PluginOperation.POLL,
        ExtensionType.CONDITION: PluginOperation.EVALUATE,
        ExtensionType.RUNNER: PluginOperation.RUN,
        ExtensionType.STORAGE: PluginOperation.GET,
        ExtensionType.SECRET: PluginOperation.RESOLVE,
        ExtensionType.EXPRESSION: PluginOperation.EVALUATE,
        ExtensionType.NOTIFICATION: PluginOperation.SEND,
    }[extension_type]


def _filesystem_rank(value: PluginFilesystemAccess) -> int:
    return {
        PluginFilesystemAccess.NONE: 0,
        PluginFilesystemAccess.WORKSPACE_READ: 1,
        PluginFilesystemAccess.WORKSPACE_WRITE: 2,
    }[value]
