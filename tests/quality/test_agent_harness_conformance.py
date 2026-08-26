from __future__ import annotations

import json
from pathlib import Path

from amesh.quality.agent_harness_conformance import (
    HARNESS_PORT_VERSION,
    HarnessCaseStatus,
    HarnessConformanceCaseResult,
    HarnessConformanceManifest,
    HarnessConformanceReport,
    HarnessPackageProvenance,
    HarnessRuntimeVersions,
    canonical_report_json,
    manifest_digest,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "schemas" / "agent-harness-conformance-manifest-v1.json"


def _manifest() -> HarnessConformanceManifest:
    return HarnessConformanceManifest.model_validate_json(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_checked_in_manifest_is_versioned_and_maps_unique_executable_nodes() -> None:
    manifest = _manifest()

    assert manifest.port_version == HARNESS_PORT_VERSION
    assert len({case.case_id for case in manifest.cases}) == len(manifest.cases)
    assert len({case.pytest_node_id for case in manifest.cases}) == len(manifest.cases)
    for case in manifest.cases:
        file_name = case.pytest_node_id.split("::", 1)[0]
        assert (ROOT / file_name).is_file()


def test_manifest_digest_is_stable_for_canonical_content() -> None:
    first = _manifest()
    reordered = HarnessConformanceManifest.model_validate(
        json.loads(json.dumps(first.model_dump(mode="json", by_alias=True), sort_keys=False))
    )

    assert manifest_digest(first) == manifest_digest(reordered)


def test_report_digest_and_canonical_bytes_are_stable() -> None:
    manifest = _manifest()
    cases = tuple(
        HarnessConformanceCaseResult(
            caseId=case.case_id,
            surface=case.surface,
            pytestNodeId=case.pytest_node_id,
            status=HarnessCaseStatus.PASSED,
        )
        for case in manifest.cases
    )
    kwargs = {
        "kitVersion": manifest.kit_version,
        "portVersion": manifest.port_version,
        "manifestDigest": manifest_digest(manifest),
        "adapter": "fixture",
        "adapterVersion": "1.0.0",
        "workerProtocol": "fixture/v1",
        "workerFile": "harnesses/fixture/worker.mjs",
        "workerSha256": "1" * 64,
        "ameshVersion": "0.2.0",
        "runtime": HarnessRuntimeVersions(python="3.12.0", node="v22.19.0"),
        "packageProvenance": HarnessPackageProvenance(
            lockFile="harnesses/fixture/package-lock.json",
            lockSha256="0" * 64,
            dependencies=(),
        ),
        "cases": cases,
        "passed": len(cases),
        "failed": 0,
        "skipped": 0,
        "overall": "passed",
    }
    first = HarnessConformanceReport(**kwargs).with_digest()
    second = HarnessConformanceReport(**kwargs).with_digest()

    assert first.report_digest is not None
    assert first.report_digest == second.report_digest
    assert canonical_report_json(first) == canonical_report_json(second)
    assert json.loads(canonical_report_json(first))["reportDigest"] == first.report_digest
