from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Protocol, runtime_checkable
from urllib.parse import parse_qs, unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DOCUMENT_EXTRACTOR_CONTRACT_VERSION: Literal["amesh.document-extractor/v1"] = (
    "amesh.document-extractor/v1"
)
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"


class DocumentProvenance(BaseModel):
    """Immutable, non-secret origin metadata for a document artifact."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    source: str = Field(min_length=1, max_length=255)
    origin_namespace: str = Field(alias="originNamespace", min_length=1, max_length=255)
    created_by: str = Field(alias="createdBy", min_length=1, max_length=255)
    created_at: datetime = Field(alias="createdAt")
    lineage: tuple[str, ...] = ()


class DocumentRetention(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    retention_until: datetime | None = Field(default=None, alias="retentionUntil")
    legal_hold: bool = Field(default=False, alias="legalHold")


class DocumentArtifactRef(BaseModel):
    """A tenant-safe content-addressed reference; storage URIs are never exposed."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.artifact-ref/v1"] = Field(
        default="amesh.artifact-ref/v1", alias="schemaVersion"
    )
    reference: str = Field(min_length=1, max_length=4096)
    content_address: str = Field(alias="contentAddress", pattern=r"^sha256:[0-9a-f]{64}$")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: str = Field(min_length=1, max_length=255)
    path: str = Field(min_length=1, max_length=1024)
    version: int = Field(ge=1)
    media_type: str | None = Field(default=None, alias="mediaType", max_length=255)
    size_bytes: int = Field(alias="sizeBytes", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=_DIGEST_PATTERN)
    provenance: DocumentProvenance
    retention: DocumentRetention

    @field_validator("reference")
    @classmethod
    def require_opaque_reference(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "nsfile"
            or parsed.netloc
            or parsed.fragment
            or not parsed.path.startswith("/")
        ):
            raise ValueError("document artifact reference must be an opaque nsfile reference")
        values = parse_qs(parsed.query, keep_blank_values=True)
        if set(values) != {"version", "sha256"} or any(
            len(items) != 1 for items in values.values()
        ):
            raise ValueError("document artifact reference must contain version and sha256")
        return value

    @model_validator(mode="after")
    def validate_content_identity(self) -> DocumentArtifactRef:
        reference = urlsplit(self.reference)
        parsed = parse_qs(reference.query, keep_blank_values=True)
        if unquote(reference.path.removeprefix("/")) != self.path:
            raise ValueError("document artifact reference does not match its path")
        if self.version != int(parsed["version"][0]) or self.checksum_sha256 != parsed["sha256"][0]:
            raise ValueError("document artifact reference does not match its content identity")
        if self.content_address != f"sha256:{self.checksum_sha256}":
            raise ValueError("contentAddress must match checksumSha256")
        return self


class DocumentExtractionLimits(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    max_bytes: int = Field(default=104_857_600, alias="maxBytes", ge=1, le=1_073_741_824)
    max_pages: int = Field(default=1000, alias="maxPages", ge=1, le=100_000)
    max_tokens: int = Field(default=1_000_000, alias="maxTokens", ge=1, le=10_000_000)
    chunk_tokens: int = Field(default=512, alias="chunkTokens", ge=1, le=16_384)
    chunk_overlap_tokens: int = Field(default=0, alias="chunkOverlapTokens", ge=0, le=4096)
    wall_time_seconds: float = Field(default=30, alias="wallTimeSeconds", gt=0, le=3600)


class DocumentExtractRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: Literal["amesh.document-extractor/v1"] = Field(
        default=DOCUMENT_EXTRACTOR_CONTRACT_VERSION,
        alias="contractVersion",
    )
    artifact: DocumentArtifactRef
    source: str = Field(min_length=1, max_length=4096)
    limits: DocumentExtractionLimits = Field(default_factory=DocumentExtractionLimits)


class DocumentSourceLocator(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    page_number: int = Field(alias="pageNumber", ge=1)
    start_offset: int = Field(alias="startOffset", ge=0)
    end_offset: int = Field(alias="endOffset", ge=0)

    @property
    def valid(self) -> bool:
        return self.end_offset >= self.start_offset


class DocumentPage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    page_number: int = Field(alias="pageNumber", ge=1)
    text: str
    token_count: int = Field(alias="tokenCount", ge=0)
    source_locator: DocumentSourceLocator = Field(alias="sourceLocator")


class DocumentChunk(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    id: str = Field(min_length=1, max_length=255)
    text: str
    token_count: int = Field(alias="tokenCount", ge=0)
    source_locators: tuple[DocumentSourceLocator, ...] = Field(alias="sourceLocators")


class ExtractorProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: Literal["amesh.document-extractor/v1"] = Field(
        default=DOCUMENT_EXTRACTOR_CONTRACT_VERSION,
        alias="contractVersion",
    )
    plugin: str = Field(min_length=1, max_length=255)
    plugin_version: str = Field(alias="pluginVersion", min_length=1, max_length=128)
    plugin_content_digest: str = Field(
        alias="pluginContentDigest", pattern=r"^sha256:[0-9a-f]{64}$"
    )
    parser: str = Field(min_length=1, max_length=255)
    parser_version: str = Field(alias="parserVersion", min_length=1, max_length=128)
    parser_content_digest: str = Field(
        alias="parserContentDigest", pattern=r"^sha256:[0-9a-f]{64}$"
    )


class DocumentExtractResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    contract_version: Literal["amesh.document-extractor/v1"] = Field(
        default=DOCUMENT_EXTRACTOR_CONTRACT_VERSION,
        alias="contractVersion",
    )
    source: DocumentArtifactRef
    extractor: ExtractorProvenance
    metadata: dict[str, Any] = Field(default_factory=dict)
    pages: tuple[DocumentPage, ...] = ()
    chunks: tuple[DocumentChunk, ...] = ()
    text: str
    token_count: int = Field(alias="tokenCount", ge=0)


@runtime_checkable
class DocumentExtractorPlugin(Protocol):
    async def extract(self, request: DocumentExtractRequest) -> DocumentExtractResult: ...


def document_extractor_output_schema() -> dict[str, Any]:
    """Return the normative JSON Schema advertised by extractor plugins."""

    return DocumentExtractResult.model_json_schema(by_alias=True)
