from __future__ import annotations

import asyncio
import os

import pytest

from amesh.evidence_bundle import EvidenceIntegrityError
from amesh.restart_qualification import (
    DEFAULT_MAX_INLINE_BYTES,
    LocalQualificationBlobStore,
    fault_matrix,
)


def test_fault_matrix_is_stable_and_covers_supported_roles() -> None:
    matrix = fault_matrix()

    assert len(matrix) == 40
    assert {(item["service"], item["boundary"]) for item in matrix} >= {
        ("api", "occurrence"),
        ("scheduler", "occurrence"),
        ("executor", "checkpoint"),
        ("worker", "final_output"),
        ("model", "model_call"),
        ("tool", "tool_call"),
        ("evidence", "final_output"),
    }
    assert {item["phase"] for item in matrix} == {"before", "after"}


def test_local_blob_store_is_content_addressed_and_detects_corruption(tmp_path) -> None:
    store = LocalQualificationBlobStore(tmp_path)
    content = b"qualification-content"
    reference = store.put(content)

    assert store.put(content) == reference
    assert store.get(reference) == content
    store.tamper(reference, b"corrupt")
    with pytest.raises(EvidenceIntegrityError):
        store.get(reference)


@pytest.mark.skipif(
    os.getenv("AMESH_TEST_DATABASE_URL") is None,
    reason="AMESH_TEST_DATABASE_URL is required for isolated qualification integration tests",
)
def test_live_restart_qualification_produces_passing_report() -> None:
    from amesh.restart_qualification import qualify_restart_idempotency

    report = asyncio.run(
        qualify_restart_idempotency(
            os.environ["AMESH_TEST_DATABASE_URL"],
            payload_bytes=DEFAULT_MAX_INLINE_BYTES + 1024,
            max_inline_bytes=DEFAULT_MAX_INLINE_BYTES,
        )
    )

    assert report["passed"] is True
    assert report["matrix"]["failedCount"] == 0
    assert report["assertions"]["zeroLostAcceptedRecords"] is True
    assert report["assertions"]["zeroDuplicateLogicalDecisions"] is True
    assert report["assertions"]["stableAcceptedResultReuse"] is True
    assert all(report["assertions"].values())
    assert report["largePayload"]["integrityVerified"] is True
