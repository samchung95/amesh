from __future__ import annotations

import asyncio
from typing import Any

import pytest
from pydantic import ValidationError

from amesh.domain.image_inputs import InputModality
from amesh.plugin_sdk import (
    PLUGIN_PROTOCOL_VERSION,
    ExtensionType,
    PluginCapabilities,
    PluginCapabilityGrant,
    PluginCompatibility,
    PluginContractError,
    PluginContractHarness,
    PluginDocumentation,
    PluginEntryPoint,
    PluginErrorDetail,
    PluginErrorPhase,
    PluginFilesystemAccess,
    PluginFixture,
    PluginManifest,
    PluginNetworkAccess,
    PluginOperation,
    PluginRequest,
    PluginResponse,
    PluginSession,
    PluginTransport,
    TaskExtension,
    TaskResult,
    extension_operation,
    plugin_catalog,
)


def entry_point(extension_type: ExtensionType) -> PluginEntryPoint:
    return PluginEntryPoint(
        name=f"{extension_type.value}.main",
        type=extension_type,
        transport=PluginTransport.STDIO,
        target="bin/example-plugin",
        configurationSchema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "title": "Value",
                    "description": "Fixture value.",
                },
                "mode": {"type": "string", "enum": ["safe", "fast"]},
                "token": {"type": "string", "writeOnly": True},
            },
            "required": ["value"],
            "additionalProperties": False,
        },
        outputSchema={"type": "object"},
        documentation=PluginDocumentation(
            title=f"Example {extension_type.value}",
            description="Contract fixture.",
            category="Tests",
            propertyOrder=("mode", "value", "token"),
            examples=({"value": "fixture"},),
        ),
    )


def manifest(*, capabilities: PluginCapabilities | None = None) -> PluginManifest:
    return PluginManifest(
        name="example.contract",
        version="1.2.3-beta.1+build.7",
        vendor="Example Corp",
        license="Apache-2.0",
        compatibility=PluginCompatibility(
            platformVersion=">=0.2.0,<1.0.0",
            protocolVersions=(PLUGIN_PROTOCOL_VERSION,),
        ),
        entryPoints=tuple(entry_point(value) for value in ExtensionType),
        capabilities=capabilities or PluginCapabilities(),
    )


def test_versioned_manifest_round_trips_as_language_neutral_json() -> None:
    source = manifest()
    encoded = source.model_dump_json(by_alias=True)
    restored = PluginManifest.model_validate_json(encoded)

    assert restored == source
    assert restored.schema_version == "amesh.plugin/v1"
    assert {item.type for item in restored.entry_points} == set(ExtensionType)
    assert all(item.api_version == "amesh.extension/v1" for item in restored.entry_points)


def test_manifest_rejects_invalid_versions_schemas_and_duplicate_entry_points() -> None:
    values = manifest().model_dump(mode="json", by_alias=True)
    values["version"] = "latest"
    with pytest.raises(ValidationError, match="version"):
        PluginManifest.model_validate(values)

    bad_entry = entry_point(ExtensionType.TASK).model_copy(
        update={"configuration_schema": {"type": "not-a-json-schema-type"}}
    )
    values = manifest().model_dump(mode="json", by_alias=True)
    values["entryPoints"] = [bad_entry.model_dump(mode="json", by_alias=True)]
    with pytest.raises(ValidationError, match="invalid Draft 2020-12"):
        PluginManifest.model_validate(values)

    duplicate = entry_point(ExtensionType.TASK).model_dump(mode="json", by_alias=True)
    values = manifest().model_dump(mode="json", by_alias=True)
    values["entryPoints"] = [duplicate, duplicate]
    with pytest.raises(ValidationError, match="must be unique"):
        PluginManifest.model_validate(values)


def test_catalog_generates_schema_documentation_and_ui_controls() -> None:
    catalog = plugin_catalog(manifest())
    task = next(item for item in catalog["entryPoints"] if item["type"] == "task")

    assert task["configurationSchema"]["required"] == ["value"]
    assert task["documentation"]["title"] == "Example task"
    assert [item["property"] for item in task["uiControls"]] == [
        "mode",
        "value",
        "token",
    ]
    assert task["uiControls"][0]["control"] == "select"
    assert task["uiControls"][1]["required"] is True
    assert task["uiControls"][2]["control"] == "password"
    assert task["uiControls"][2]["secret"] is True


def test_task_image_input_requires_explicit_entry_point_modality_and_never_runs_handler() -> None:
    async def scenario() -> None:
        item = entry_point(ExtensionType.TASK)
        called = False

        async def handler(request: PluginRequest) -> PluginResponse:
            nonlocal called
            called = True
            return PluginResponse(invocationId=request.session.invocation_id)

        harness = PluginContractHarness(
            PluginManifest(
                name="example.contract",
                version="1.0.0",
                vendor="Example",
                license="MIT",
                compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
                entryPoints=(item,),
            ),
            {(item.name, PluginOperation.EXECUTE): handler},
        )
        image_ref = {"schemaVersion": "amesh.image-ref/v1", "artifact": {"tenantId": "tenant-a"}}
        response = await harness.invoke(
            request_for(item, configuration={"value": "ok"}).model_copy(
                update={"input": {"picture": image_ref}}
            )
        )

        assert response.errors[0].code == "plugin.capability.input_modality_denied"
        assert called is False
        assert item.input_modalities == frozenset({InputModality.TEXT})
        assert "inputModalities" in item.model_dump(mode="json", by_alias=True)

        image_item = item.model_copy(
            update={"input_modalities": frozenset({InputModality.TEXT, InputModality.IMAGE})}
        )
        image_manifest = PluginManifest(
            name="example.image",
            version="1.0.0",
            vendor="Example",
            license="MIT",
            compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
            entryPoints=(image_item,),
        )
        image_harness = PluginContractHarness(
            image_manifest,
            {(image_item.name, PluginOperation.EXECUTE): handler},
        )
        allowed = await image_harness.invoke(
            request_for(image_item, configuration={"value": "ok"})
            .model_copy(update={"plugin": "example.image"})
            .model_copy(update={"input": {"picture": image_ref}})
        )
        assert allowed.errors == ()
        assert called is True

    asyncio.run(scenario())


def test_local_harness_runs_fixture_for_every_extension_type() -> None:
    async def scenario() -> None:
        async def handler(request: PluginRequest) -> PluginResponse:
            return PluginResponse(
                invocationId=request.session.invocation_id,
                output={"entryPoint": request.entry_point, "value": request.configuration["value"]},
            )

        handlers = {
            (item.name, extension_operation(item.type)): handler for item in manifest().entry_points
        }
        harness = PluginContractHarness(manifest(), handlers)
        for item in manifest().entry_points:
            fixture = PluginFixture(
                name=item.type.value,
                entryPoint=item.name,
                operation=extension_operation(item.type),
                configuration={"value": "verified"},
                expectedOutput={"entryPoint": item.name, "value": "verified"},
            )
            result = await harness.run_fixture(fixture)
            assert result.passed, result.diagnostic

    asyncio.run(scenario())


def test_capability_contract_denies_network_filesystem_and_secret_scope_gaps() -> None:
    declared = PluginCapabilities(
        required=("artifact.publish",),
        networkAccess=PluginNetworkAccess.RESTRICTED,
        allowedEgress=("api.example.com:443",),
        filesystemAccess=PluginFilesystemAccess.WORKSPACE_WRITE,
        secretScopes=("provider.token",),
    )
    harness = PluginContractHarness(
        manifest(capabilities=declared),
        {},
        grant=PluginCapabilityGrant(
            capabilities=(),
            networkAccess=PluginNetworkAccess.NONE,
            filesystemAccess=PluginFilesystemAccess.WORKSPACE_READ,
        ),
    )

    assert {item.code for item in harness.validate_capabilities()} == {
        "plugin.capability.missing",
        "plugin.capability.network_denied",
        "plugin.capability.egress_denied",
        "plugin.capability.filesystem_denied",
        "plugin.capability.secret_scope_denied",
    }


def test_configuration_and_runtime_errors_are_structured_and_secret_free() -> None:
    async def scenario() -> None:
        async def fails(request: PluginRequest) -> PluginResponse:
            del request
            raise PluginContractError(
                PluginErrorDetail(
                    code="plugin.runtime.provider_denied",
                    message="provider rejected the request",
                    phase=PluginErrorPhase.RUNTIME,
                    retryable=False,
                )
            )

        item = entry_point(ExtensionType.TASK)
        harness = PluginContractHarness(
            PluginManifest(
                name="example.contract",
                version="1.0.0",
                vendor="Example",
                license="MIT",
                compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
                entryPoints=(item,),
            ),
            {(item.name, PluginOperation.EXECUTE): fails},
        )
        invalid = await harness.invoke(request_for(item, configuration={"token": "must-not-leak"}))
        failed = await harness.invoke(
            request_for(item, configuration={"value": "ok", "token": "must-not-leak"})
        )

        assert invalid.errors[0].code == "plugin.configuration.invalid"
        assert invalid.errors[0].path == ()
        assert invalid.errors[0].hint
        assert failed.errors[0].code == "plugin.runtime.provider_denied"
        assert "must-not-leak" not in invalid.model_dump_json()
        assert "must-not-leak" not in failed.model_dump_json()

    asyncio.run(scenario())


def test_python_task_protocol_is_runtime_checkable() -> None:
    class ExampleTask:
        async def validate(
            self,
            configuration: dict[str, Any],
        ) -> tuple[PluginErrorDetail, ...]:
            del configuration
            return ()

        async def execute(self, request: PluginRequest) -> TaskResult:
            del request
            return TaskResult(output={"ok": True})

    assert isinstance(ExampleTask(), TaskExtension)


def request_for(
    item: PluginEntryPoint,
    *,
    configuration: dict[str, Any],
) -> PluginRequest:
    return PluginRequest(
        plugin="example.contract",
        entryPoint=item.name,
        operation=PluginOperation.EXECUTE,
        session=PluginSession(tenantId="default", invocationId="invocation-1"),
        configuration=configuration,
    )
