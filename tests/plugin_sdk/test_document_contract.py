from __future__ import annotations

import asyncio

import pytest

from amesh.plugin_sdk import (
    DOCUMENT_EXTRACTOR_CONTRACT_VERSION,
    DocumentArtifactRef,
    DocumentChunk,
    DocumentExtractionLimits,
    DocumentExtractRequest,
    DocumentExtractResult,
    DocumentPage,
    DocumentProvenance,
    DocumentRetention,
    DocumentSourceLocator,
    ExtractorProvenance,
    PluginCapabilities,
    PluginCompatibility,
    PluginContractHarness,
    PluginDocumentation,
    PluginEntryPoint,
    PluginFixture,
    PluginManifest,
    PluginOperation,
    PluginResponse,
    PluginTransport,
    document_extractor_output_schema,
)


def _artifact() -> DocumentArtifactRef:
    checksum = "a" * 64
    return DocumentArtifactRef(
        reference=f"nsfile:///docs/report.pdf?version=1&sha256={checksum}",
        contentAddress=f"sha256:{checksum}",
        tenantId="fixture",
        namespace="docs",
        path="docs/report.pdf",
        version=1,
        mediaType="application/pdf",
        sizeBytes=42,
        checksumSha256=checksum,
        provenance=DocumentProvenance(
            source="namespace-file",
            originNamespace="docs",
            createdBy="fixture",
            createdAt="2026-08-26T00:00:00Z",
        ),
        retention=DocumentRetention(),
    )


def test_document_artifact_reference_must_match_public_path() -> None:
    artifact = _artifact().model_dump(mode="json", by_alias=True)
    artifact["path"] = "docs/another.pdf"

    with pytest.raises(ValueError, match="does not match its path"):
        DocumentArtifactRef.model_validate(artifact)


def test_document_extractor_contract_runs_through_ordinary_task_plugin_harness() -> None:
    artifact = _artifact()
    request = DocumentExtractRequest(
        artifact=artifact,
        source="document.pdf",
        limits=DocumentExtractionLimits(maxTokens=50),
    )
    locator = DocumentSourceLocator(pageNumber=1, startOffset=0, endOffset=5)
    result = DocumentExtractResult(
        source=artifact,
        extractor=ExtractorProvenance(
            plugin="fixture.document.extractor",
            pluginVersion="1.0.0",
            pluginContentDigest="sha256:" + "b" * 64,
            parser="fixture",
            parserVersion="1.0.0",
            parserContentDigest="sha256:" + "c" * 64,
        ),
        metadata={"title": "Fixture"},
        pages=(DocumentPage(pageNumber=1, text="hello", tokenCount=1, sourceLocator=locator),),
        chunks=(
            DocumentChunk(
                id="page-1-chunk-1",
                text="hello",
                tokenCount=1,
                sourceLocators=(locator,),
            ),
        ),
        text="hello",
        tokenCount=1,
    )
    manifest = PluginManifest(
        name="fixture.document.extractor",
        version="1.0.0",
        vendor="AMESH tests",
        license="MIT",
        compatibility=PluginCompatibility(platformVersion=">=0.2.0"),
        capabilities=PluginCapabilities(),
        entryPoints=(
            PluginEntryPoint(
                name="extract",
                resourceType="document.extract",
                type="task",
                transport=PluginTransport.STDIO,
                target="service:extract",
                configurationSchema={
                    "type": "object",
                    "required": ["artifact", "source", "limits", "inputFiles"],
                    "properties": {
                        "artifact": {"type": "object"},
                        "source": {"type": "string"},
                        "limits": {"type": "object"},
                        "inputFiles": {"type": "object"},
                    },
                    "additionalProperties": True,
                },
                outputSchema=document_extractor_output_schema(),
                documentation=PluginDocumentation(
                    title="Document extractor",
                    description="Contract fixture",
                    category="Documents",
                ),
            ),
        ),
    )

    async def execute(plugin_request):
        parsed = DocumentExtractRequest.model_validate(
            {
                key: value
                for key, value in plugin_request.configuration.items()
                if key != "inputFiles"
            }
        )
        assert parsed.contract_version == DOCUMENT_EXTRACTOR_CONTRACT_VERSION
        return PluginResponse(
            invocationId=plugin_request.session.invocation_id,
            output=result.model_dump(mode="json", by_alias=True),
        )

    harness = PluginContractHarness(
        manifest,
        {("extract", PluginOperation.EXECUTE): execute},
    )
    fixture = PluginFixture(
        name="document-contract",
        entryPoint="extract",
        operation=PluginOperation.EXECUTE,
        configuration={
            **request.model_dump(mode="json", by_alias=True),
            "inputFiles": {"document.pdf": request.artifact.reference},
        },
    )

    async def scenario() -> None:
        outcome = await harness.run_fixture(fixture)
        assert outcome.passed, outcome.diagnostic
        DocumentExtractResult.model_validate(outcome.response.output)

    asyncio.run(scenario())
