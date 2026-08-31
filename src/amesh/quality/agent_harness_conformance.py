from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.domain import canonical_hash, canonical_json

HARNESS_PORT_VERSION: Final = "amesh.agent-session-harness/v1"
CONFORMANCE_MANIFEST_VERSION: Final = "amesh.agent-harness-conformance-manifest/v1"
CONFORMANCE_REPORT_VERSION: Final = "amesh.agent-harness-conformance-report/v1"
REQUIRED_CASE_IDS: Final = frozenset(
    {
        "session-structured-output",
        "session-multi-turn-tool",
        "session-approval-denial",
        "session-bounded-context-cache",
        "session-continuation",
        "session-restart-pending-tool",
        "session-budget",
        "session-cost-tool-budgets",
        "session-malformed-actions",
        "session-nested-call-mutation",
        "session-gateway-result-required",
        "session-gateway-single-call",
        "session-gateway-result-immutable",
        "pi-model-gateway",
        "pi-credential-isolation",
        "pi-cache-usage",
        "pi-large-response",
        "pi-handshake",
        "pi-authority-frames",
        "pi-timeout",
        "pi-control-frames",
        "pi-progress-chronology",
        "pi-governed-image-boundary",
        "registry-explicit-pi",
        "registry-unknown-fail-closed",
    }
)


class HarnessConformanceSurface(StrEnum):
    AMESH_SESSION = "amesh-session"
    PI_BRIDGE = "pi-bridge"


class HarnessCaseStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    MISSING = "missing"


class HarnessConformanceCase(BaseModel):
    """One stable pytest node in the portable harness contract."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    case_id: str = Field(alias="caseId", pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=128)
    surface: HarnessConformanceSurface
    pytest_node_id: str = Field(alias="pytestNodeId", min_length=1, max_length=512)


class HarnessConformanceManifest(BaseModel):
    """Versioned mapping from portable case IDs to executable test nodes."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-harness-conformance-manifest/v1"] = Field(
        default="amesh.agent-harness-conformance-manifest/v1",
        alias="schemaVersion",
    )
    kit_version: str = Field(alias="kitVersion", pattern=r"^\d+\.\d+\.\d+$", max_length=32)
    port_version: Literal["amesh.agent-session-harness/v1"] = Field(
        default="amesh.agent-session-harness/v1",
        alias="portVersion",
    )
    cases: tuple[HarnessConformanceCase, ...] = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def validate_case_ids(self) -> HarnessConformanceManifest:
        ids = tuple(case.case_id for case in self.cases)
        if len(set(ids)) != len(ids):
            raise ValueError("harness conformance case IDs must be unique")
        if set(ids) != REQUIRED_CASE_IDS:
            raise ValueError("harness conformance manifest does not contain the complete case set")
        nodes = tuple(case.pytest_node_id for case in self.cases)
        if len(set(nodes)) != len(nodes):
            raise ValueError("harness conformance pytest node IDs must be unique")
        return self


class HarnessRuntimeVersions(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    python: str = Field(min_length=1, max_length=64)
    node: str = Field(min_length=1, max_length=64)


class HarnessDependencyProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    package: str = Field(min_length=1, max_length=512)
    version: str = Field(min_length=1, max_length=128)
    license: str = Field(min_length=1, max_length=256)
    integrity: str | None = Field(default=None, max_length=256)
    resolved: str | None = Field(default=None, max_length=2048)


class HarnessPackageProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    lock_file: str = Field(alias="lockFile", min_length=1, max_length=512)
    lock_sha256: str = Field(alias="lockSha256", pattern=r"^[0-9a-f]{64}$")
    dependencies: tuple[HarnessDependencyProvenance, ...] = Field(max_length=4096)


class HarnessConformanceCaseResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    case_id: str = Field(alias="caseId", min_length=1, max_length=128)
    surface: HarnessConformanceSurface
    pytest_node_id: str = Field(alias="pytestNodeId", min_length=1, max_length=512)
    status: HarnessCaseStatus


class HarnessConformanceReport(BaseModel):
    """Deterministic machine-readable result for one conformance invocation."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-harness-conformance-report/v1"] = Field(
        default="amesh.agent-harness-conformance-report/v1",
        alias="schemaVersion",
    )
    kit_version: str = Field(alias="kitVersion", pattern=r"^\d+\.\d+\.\d+$", max_length=32)
    port_version: Literal["amesh.agent-session-harness/v1"] = Field(
        default="amesh.agent-session-harness/v1",
        alias="portVersion",
    )
    manifest_digest: str = Field(alias="manifestDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    adapter: str = Field(min_length=1, max_length=128)
    adapter_version: str = Field(alias="adapterVersion", min_length=1, max_length=128)
    worker_protocol: str = Field(alias="workerProtocol", min_length=1, max_length=128)
    worker_file: str = Field(alias="workerFile", min_length=1, max_length=512)
    worker_sha256: str = Field(alias="workerSha256", pattern=r"^[0-9a-f]{64}$")
    amesh_version: str = Field(alias="ameshVersion", min_length=1, max_length=128)
    runtime: HarnessRuntimeVersions
    package_provenance: HarnessPackageProvenance = Field(alias="packageProvenance")
    cases: tuple[HarnessConformanceCaseResult, ...] = Field(min_length=1, max_length=256)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    overall: Literal["passed", "failed"]
    report_digest: str | None = Field(
        default=None,
        alias="reportDigest",
        pattern=r"^sha256:[0-9a-f]{64}$",
    )

    @model_validator(mode="after")
    def validate_counts(self) -> HarnessConformanceReport:
        expected = {
            HarnessCaseStatus.PASSED: self.passed,
            HarnessCaseStatus.SKIPPED: self.skipped,
        }
        for status, count in expected.items():
            actual = sum(case.status is status for case in self.cases)
            if count != actual:
                raise ValueError(f"report count for {status.value} does not match cases")
        actual_failed = sum(
            case.status
            in {
                HarnessCaseStatus.FAILED,
                HarnessCaseStatus.ERROR,
                HarnessCaseStatus.MISSING,
            }
            for case in self.cases
        )
        if self.failed != actual_failed:
            raise ValueError("report failed count does not match non-passing cases")
        if self.overall == "passed" and any(
            case.status is not HarnessCaseStatus.PASSED for case in self.cases
        ):
            raise ValueError("a passed report requires every case to pass")
        if self.overall == "failed" and all(
            case.status is HarnessCaseStatus.PASSED for case in self.cases
        ):
            raise ValueError("a failed report requires at least one non-passing case")
        return self

    def digest_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        payload.pop("reportDigest", None)
        return payload

    def with_digest(self) -> HarnessConformanceReport:
        return self.model_copy(
            update={"report_digest": "sha256:" + canonical_hash(self.digest_payload())}
        )

    def canonical_bytes(self) -> bytes:
        report = self.with_digest()
        return canonical_json(report.model_dump(mode="json", by_alias=True, exclude_none=True))


def manifest_digest(manifest: HarnessConformanceManifest) -> str:
    return "sha256:" + canonical_hash(manifest)


def canonical_report_json(report: HarnessConformanceReport) -> bytes:
    """Return canonical JSON including the self-consistent report digest."""

    return report.canonical_bytes()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dependency_license(value: object) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return "UNKNOWN"
