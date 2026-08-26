from __future__ import annotations

import json
from pathlib import Path

from amesh.app import app
from amesh.domain.artifacts import ArtifactRef
from amesh.domain.execution import (
    ExecutionCommand,
    ExecutionEvent,
    ExecutionSnapshot,
    ExecutionTransition,
    TaskRunCommand,
    TaskRunEvent,
    TaskRunSnapshot,
    TaskRunTransition,
)
from amesh.dsl.models import FlowDefinition
from amesh.dsl.registry import default_resource_registry
from amesh.plugin_sdk import (
    CertificationReport,
    DocumentExtractRequest,
    DocumentExtractResult,
    PluginCatalogSnapshot,
    PluginExtensionContract,
    PluginManifest,
    PluginRegistryIndex,
    PluginRequest,
    PluginResolution,
    PluginResponse,
    PluginWireContract,
)
from amesh.ports import DurableEnvelope
from amesh.quality.agent_harness_conformance import (
    HarnessConformanceManifest,
    HarnessConformanceReport,
)


def load(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_checked_in_contracts_are_current() -> None:
    assert load("schemas/flow.schema.json") == FlowDefinition.model_json_schema()
    assert load("schemas/message-envelope.schema.json") == DurableEnvelope.model_json_schema()
    assert load("schemas/resource-catalog.json") == default_resource_registry().catalog()
    assert load("schemas/artifact-ref.schema.json") == ArtifactRef.model_json_schema()
    assert (
        load("schemas/document-extract-request.schema.json")
        == DocumentExtractRequest.model_json_schema()
    )
    assert (
        load("schemas/document-extract-result.schema.json")
        == DocumentExtractResult.model_json_schema()
    )
    assert (
        load("schemas/agent-harness-conformance-manifest.schema.json")
        == HarnessConformanceManifest.model_json_schema()
    )
    assert (
        load("schemas/agent-harness-conformance-report.schema.json")
        == HarnessConformanceReport.model_json_schema()
    )
    assert load("schemas/plugin-manifest.schema.json") == PluginManifest.model_json_schema()
    assert load("schemas/plugin-request.schema.json") == PluginRequest.model_json_schema()
    assert load("schemas/plugin-response.schema.json") == PluginResponse.model_json_schema()
    assert load("schemas/plugin-wire.schema.json") == PluginWireContract.model_json_schema()
    assert (
        load("schemas/plugin-extensions.schema.json") == PluginExtensionContract.model_json_schema()
    )
    assert load("schemas/plugin-catalog.schema.json") == PluginCatalogSnapshot.model_json_schema()
    assert load("schemas/plugin-registry.schema.json") == PluginRegistryIndex.model_json_schema()
    assert load("schemas/plugin-resolution.schema.json") == PluginResolution.model_json_schema()
    assert (
        load("schemas/plugin-certification.schema.json") == CertificationReport.model_json_schema()
    )
    assert load("schemas/execution-command.schema.json") == ExecutionCommand.model_json_schema()
    assert load("schemas/execution-event.schema.json") == ExecutionEvent.model_json_schema()
    assert load("schemas/execution-snapshot.schema.json") == ExecutionSnapshot.model_json_schema()
    assert (
        load("schemas/execution-transition.schema.json") == ExecutionTransition.model_json_schema()
    )
    assert load("schemas/task-run-command.schema.json") == TaskRunCommand.model_json_schema()
    assert load("schemas/task-run-event.schema.json") == TaskRunEvent.model_json_schema()
    assert load("schemas/task-run-snapshot.schema.json") == TaskRunSnapshot.model_json_schema()
    assert load("schemas/task-run-transition.schema.json") == TaskRunTransition.model_json_schema()
    assert load("docs/api/openapi.json") == app.openapi()
