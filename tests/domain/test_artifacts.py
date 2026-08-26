from __future__ import annotations

from datetime import UTC, datetime

import pytest

from amesh.domain import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
    parse_artifact_reference,
)

CHECKSUM = "a" * 64


def _artifact(reference: str | None = None) -> ArtifactRef:
    return ArtifactRef(
        reference=reference or build_artifact_reference("reports/quarter 1.pdf", 2, CHECKSUM),
        contentAddress=f"sha256:{CHECKSUM}",
        tenantId="tenant-a",
        namespace="reports",
        path="reports/quarter 1.pdf",
        version=2,
        mediaType="application/pdf",
        sizeBytes=12,
        checksumSha256=CHECKSUM,
        provenance=ArtifactProvenance(
            source="namespace-file",
            originNamespace="reports",
            createdBy="operator",
            createdAt=datetime(2026, 8, 26, tzinfo=UTC),
            lineage=("namespace-file", "reports", "reports/quarter 1.pdf"),
        ),
        retention=ArtifactRetention(),
    )


def test_artifact_reference_round_trips_encoded_path() -> None:
    reference = build_artifact_reference("reports/quarter 1.pdf", 2, CHECKSUM)
    assert reference == f"nsfile:///reports/quarter%201.pdf?version=2&sha256={CHECKSUM}"
    assert parse_artifact_reference(reference) == ("reports/quarter 1.pdf", 2, CHECKSUM)
    assert _artifact().model_dump(by_alias=True)["schemaVersion"] == "amesh.artifact-ref/v1"


@pytest.mark.parametrize(
    "reference",
    (
        "s3://bucket/tenants/tenant-a/report.pdf?version=2&sha256=" + CHECKSUM,
        "nsfile://other/reports/report.pdf?version=2&sha256=" + CHECKSUM,
        "nsfile:///../report.pdf?version=2&sha256=" + CHECKSUM,
        "nsfile:///reports/report.pdf?version=0&sha256=" + CHECKSUM,
        "nsfile:///reports/report.pdf?version=2&sha256=" + "A" * 64,
        "nsfile:///reports/report.pdf?version=2&sha256=" + CHECKSUM + "&extra=x",
    ),
)
def test_artifact_reference_rejects_unsafe_or_non_exact_syntax(reference: str) -> None:
    with pytest.raises(ValueError):
        parse_artifact_reference(reference)


def test_artifact_ref_rejects_digest_or_reference_mismatch() -> None:
    with pytest.raises(ValueError):
        _artifact(build_artifact_reference("other.pdf", 2, CHECKSUM))
