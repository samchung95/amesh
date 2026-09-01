from __future__ import annotations

import hashlib
import re
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain.agent_primitives import AgentInvocationRecord, AgentInvocationState
from amesh.domain.agent_resources import AgentCapabilityPin
from amesh.domain.agent_sessions import (
    AgentSessionEvent,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionState,
)
from amesh.domain.execution import (
    ExecutionEvent,
    ExecutionState,
    TaskRunEvent,
    TaskRunState,
)
from amesh.domain.resources import canonical_json
from amesh.ports.execution_repository import PersistedExecution, PersistedTaskRun
from amesh.ports.metadata_repository import ExecutionArtifact, ExecutionEvidenceEvent

_SCHEMA_VERSION = "amesh.session-transfer/v1"
_EMPTY_DIGEST = "0" * 64
_SECRET_KEYS = frozenset(
    {
        "password",
        "token",
        "secret",
        "secret_value",
        "api_key",
        "apikey",
        "private_key",
        "privatekey",
        "access_token",
        "refresh_token",
        "credential",
        "credentials",
        "credential_value",
    }
)
_REFERENCE_KEYS = frozenset(
    {
        "credentialref",
        "credential_ref",
        "secretscopes",
        "secret_scopes",
        "tokendigest",
        "token_digest",
    }
)
_SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:^|_)(?:client|access|refresh|bearer|auth)_(?:token|secret)(?:_|$)|"
    r"(?:^|_)(?:api|private)_key(?:_|$)|"
    r"(?:^|_)(?:token|secret|password|credential)(?:_|$)"
)
_TERMINAL_EXECUTION_STATES = frozenset(
    {
        ExecutionState.CANCELLED,
        ExecutionState.SUCCESS,
        ExecutionState.FAILED,
        ExecutionState.WARNING,
    }
)
_TERMINAL_TASK_STATES = frozenset(
    {TaskRunState.SUCCESS, TaskRunState.FAILED, TaskRunState.CANCELLED}
)


class SessionTransferMode(StrEnum):
    TERMINAL_HISTORY = "TERMINAL_HISTORY"
    CLEAN_CHECKPOINT = "CLEAN_CHECKPOINT"


class SessionTaskRunEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    task_run_id: UUID = Field(alias="taskRunId")
    sequence: int = Field(ge=1)
    event: TaskRunEvent


class SessionTransferEligibility(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    eligible: bool
    mode: SessionTransferMode
    reasons: tuple[str, ...] = ()


class SessionTransferCompatibilityReport(BaseModel):
    """Mutation-free target compatibility result for a session transfer."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    schema_version: str = Field(default="amesh.session-transfer-plan/v1", alias="schemaVersion")
    eligible: bool
    mode: SessionTransferMode
    source_tenant_id: str = Field(alias="sourceTenantId")
    target_tenant_id: str = Field(alias="targetTenantId")
    bundle_digest: str = Field(alias="bundleDigest", pattern=r"^[0-9a-f]{64}$")
    flow_compatible: bool = Field(alias="flowCompatible")
    capability_pin_compatible: bool = Field(alias="capabilityPinCompatible")
    harness_compatible: bool = Field(alias="harnessCompatible")
    credential_rebinding_diagnostics: tuple[str, ...] = Field(
        default=(), alias="credentialRebindingDiagnostics"
    )
    artifact_diagnostics: tuple[str, ...] = Field(default=(), alias="artifactDiagnostics")
    issues: tuple[str, ...] = ()


class SessionTransferBundle(BaseModel):
    """A sealed snapshot of canonical records; no live worker state is included."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    schema_version: str = Field(default=_SCHEMA_VERSION, alias="schemaVersion")
    mode: SessionTransferMode
    source_tenant_id: str = Field(alias="sourceTenantId", min_length=1, max_length=255)
    session: AgentSessionRecord
    events: tuple[AgentSessionEvent, ...] = ()
    execution: PersistedExecution
    task_runs: tuple[PersistedTaskRun, ...] = Field(default=(), alias="taskRuns")
    execution_events: tuple[ExecutionEvent, ...] = Field(default=(), alias="executionEvents")
    task_run_events: tuple[TaskRunEvent, ...] = Field(default=(), alias="taskRunEvents")
    task_run_event_records: tuple[SessionTaskRunEvent, ...] = Field(
        default=(), alias="taskRunEventRecords"
    )
    invocations: tuple[AgentInvocationRecord, ...] = ()
    evidence_events: tuple[ExecutionEvidenceEvent, ...] = Field(default=(), alias="evidenceEvents")
    artifacts: tuple[ExecutionArtifact, ...] = ()
    artifact_destination_refs: dict[str, str] = Field(
        default_factory=dict,
        alias="artifactDestinationRefs",
    )
    capability_pin: AgentCapabilityPin | None = Field(default=None, alias="capabilityPin")
    active_lease_count: int = Field(default=0, alias="activeLeaseCount", ge=0)
    active_admission_claim_count: int = Field(default=0, alias="activeAdmissionClaimCount", ge=0)
    unresolved_approval_count: int = Field(default=0, alias="unresolvedApprovalCount", ge=0)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")

    @property
    def import_id(self) -> str:
        return f"{self.source_tenant_id}:{self.session.session_id}:{self.mode.value}"

    def canonical_bytes(self) -> bytes:
        return canonical_json(self.model_dump(mode="json", by_alias=True))

    def verify(self) -> None:
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(f"unsupported session transfer schema {self.schema_version!r}")
        if self.checksum_sha256 != _bundle_checksum(self):
            raise ValueError("session transfer bundle checksum is invalid")


class SessionTransferImportResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    import_id: str = Field(alias="importId", min_length=1)
    bundle_digest: str = Field(alias="bundleDigest", pattern=r"^[0-9a-f]{64}$")
    mode: SessionTransferMode
    target_tenant_id: str = Field(alias="targetTenantId", min_length=1, max_length=255)
    session_id: str = Field(alias="sessionId", min_length=1)
    already_present: bool = Field(default=False, alias="alreadyPresent")
    id_mapping: dict[str, str] = Field(default_factory=dict, alias="idMapping")
    credential_rebinding_diagnostics: tuple[str, ...] = Field(
        default=(), alias="credentialRebindingDiagnostics"
    )


class SessionTransferImportRepository(Protocol):
    """Persistence boundary for a future implementation of canonical record import."""

    async def get_import(
        self, target_tenant_id: str, import_id: str
    ) -> SessionTransferImportResult | None: ...

    async def import_records(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        actor_id: str,
        import_id: str,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferImportResult: ...

    async def plan_import(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferCompatibilityReport: ...


class SessionTransferService:
    def __init__(self, imports: SessionTransferImportRepository) -> None:
        self._imports = imports

    def eligibility(
        self,
        bundle: SessionTransferBundle,
        *,
        mode: SessionTransferMode | None = None,
    ) -> SessionTransferEligibility:
        selected_mode = mode or bundle.mode
        reasons: list[str] = []
        try:
            bundle.verify()
            _validate_bundle(bundle)
        except ValueError as exc:
            reasons.append(str(exc))
            return SessionTransferEligibility(
                eligible=False, mode=selected_mode, reasons=tuple(reasons)
            )
        if selected_mode is not bundle.mode:
            reasons.append("requested transfer mode does not match bundle mode")
        if bundle.active_lease_count:
            reasons.append("active lease exists")
        if bundle.active_admission_claim_count:
            reasons.append("active admission claim exists")
        if bundle.unresolved_approval_count:
            reasons.append("unresolved approval exists")

        session = bundle.session
        if session.harness is None:
            reasons.append("exact harness pin is missing")
        if bundle.capability_pin is None:
            reasons.append("exact capability pin is missing")
        if session.checkpoint.pending_action is not None:
            reasons.append("checkpoint has a pending action")
        if session.checkpoint.pending_turn is not None:
            reasons.append("checkpoint has a pending turn")
        if session.checkpoint.memory_write is not None:
            reasons.append("checkpoint has a pending memory write")
        if session.checkpoint.model_continuation is not None:
            reasons.append("checkpoint has a provider continuation")
        if session.checkpoint.model_continuations:
            reasons.append("checkpoint has provider continuation bindings")
        if any(item.state is AgentInvocationState.STARTED for item in bundle.invocations):
            reasons.append("an external model or tool invocation is still STARTED")

        if selected_mode is SessionTransferMode.TERMINAL_HISTORY:
            if session.state not in {AgentSessionState.SUCCEEDED, AgentSessionState.FAILED}:
                reasons.append("terminal history requires a terminal session")
            if session.phase is not AgentSessionPhase.COMPLETE:
                reasons.append("terminal history requires COMPLETE phase")
            if session.completed_at is None:
                reasons.append("terminal history requires completion timestamp")
            if bundle.execution.state not in _TERMINAL_EXECUTION_STATES:
                reasons.append("terminal history requires a terminal execution")
            if any(task.state not in _TERMINAL_TASK_STATES for task in bundle.task_runs):
                reasons.append("terminal history contains a non-terminal task run")
        else:
            if session.state is not AgentSessionState.RUNNING:
                reasons.append("clean checkpoint requires a RUNNING session")
            if session.phase is not AgentSessionPhase.READY:
                reasons.append("clean checkpoint requires READY phase")
            if bundle.execution.state is not ExecutionState.PAUSED:
                reasons.append("clean checkpoint requires a PAUSED execution")

        return SessionTransferEligibility(
            eligible=not reasons,
            mode=selected_mode,
            reasons=tuple(reasons),
        )

    async def import_bundle(
        self,
        bundle: SessionTransferBundle,
        *,
        target_tenant_id: str,
        actor_id: str,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferImportResult:
        eligibility = self.eligibility(bundle)
        if not eligibility.eligible:
            raise ValueError("session transfer is ineligible: " + "; ".join(eligibility.reasons))
        import_id = bundle.import_id
        existing = await self._imports.get_import(target_tenant_id, import_id)
        if existing is not None:
            if (
                existing.bundle_digest != bundle.checksum_sha256
                or existing.import_id != import_id
                or existing.mode != bundle.mode
            ):
                raise ValueError("session transfer import identity was reused with another bundle")
            return existing.model_copy(update={"already_present": True})
        if credential_rebindings is None:
            result = await self._imports.import_records(
                target_tenant_id,
                bundle,
                actor_id=actor_id,
                import_id=import_id,
            )
        else:
            result = await self._imports.import_records(
                target_tenant_id,
                bundle,
                actor_id=actor_id,
                import_id=import_id,
                credential_rebindings=credential_rebindings,
            )
        if result.import_id != import_id or result.bundle_digest != bundle.checksum_sha256:
            raise ValueError("session transfer repository returned an invalid import identity")
        return result

    async def plan_import(
        self,
        bundle: SessionTransferBundle,
        *,
        target_tenant_id: str,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferCompatibilityReport:
        """Return target diagnostics without writing canonical or ledger records."""

        try:
            bundle.verify()
            _validate_bundle(bundle)
        except ValueError as exc:
            return SessionTransferCompatibilityReport(
                eligible=False,
                mode=bundle.mode,
                sourceTenantId=bundle.source_tenant_id,
                targetTenantId=target_tenant_id,
                bundleDigest=bundle.checksum_sha256,
                flowCompatible=False,
                capabilityPinCompatible=False,
                harnessCompatible=False,
                issues=(str(exc),),
            )
        eligibility = self.eligibility(bundle)
        report = await self._imports.plan_import(
            target_tenant_id,
            bundle,
            credential_rebindings=credential_rebindings,
        )
        issues = tuple(dict.fromkeys((*eligibility.reasons, *report.issues)))
        return report.model_copy(update={"eligible": not issues, "issues": issues})


def seal_bundle(bundle: SessionTransferBundle) -> SessionTransferBundle:
    """Seal an unsigned bundle after validating its canonical records."""
    _validate_bundle(bundle.model_copy(update={"checksum_sha256": _EMPTY_DIGEST}))
    return bundle.model_copy(update={"checksum_sha256": _bundle_checksum(bundle)})


def _validate_bundle(bundle: SessionTransferBundle) -> None:
    session = bundle.session
    if session.tenant_id != bundle.source_tenant_id:
        raise ValueError("session belongs to another tenant")
    if bundle.execution.tenant_id != bundle.source_tenant_id:
        raise ValueError("execution belongs to another tenant")
    if session.execution_id != bundle.execution.execution_id:
        raise ValueError("session execution identity does not match execution record")
    task_ids = {item.task_run_id for item in bundle.task_runs}
    for task in bundle.task_runs:
        if task.execution_id != bundle.execution.execution_id:
            raise ValueError("task run belongs to another execution")
    if bundle.capability_pin is not None:
        if bundle.capability_pin.tenant_id != bundle.source_tenant_id:
            raise ValueError("capability pin belongs to another tenant")
        if bundle.capability_pin.pin_id != session.capability_pin_id:
            raise ValueError("capability pin identity does not match session")
        if bundle.capability_pin.envelope_digest != session.envelope_digest:
            raise ValueError("capability pin digest does not match session")
    _check_no_secrets(bundle)

    event_indices = [item.event_index for item in bundle.events]
    if event_indices != list(range(1, session.version + 1)):
        raise ValueError("session event cursor has a gap or does not match session version")
    if any(item.session_id != session.session_id for item in bundle.events):
        raise ValueError("session event belongs to another session")
    if len({item.event_id for item in bundle.events}) != len(bundle.events):
        raise ValueError("session event IDs must be unique")

    for invocation in bundle.invocations:
        if invocation.tenant_id != bundle.source_tenant_id:
            raise ValueError("invocation belongs to another tenant")
        if invocation.execution_id != bundle.execution.execution_id:
            raise ValueError("invocation belongs to another execution")
        if invocation.task_run_id not in task_ids:
            raise ValueError("invocation references an unexported task run")
    for task_record in bundle.task_run_event_records:
        if task_record.task_run_id not in task_ids:
            raise ValueError("task-run event references an unexported task run")
    task_record_event_ids = [item.event.event_id for item in bundle.task_run_event_records]
    if len(set(task_record_event_ids)) != len(task_record_event_ids):
        raise ValueError("task-run event IDs must be unique")
    for task_run_id in task_ids:
        sequences = sorted(
            item.sequence
            for item in bundle.task_run_event_records
            if item.task_run_id == task_run_id
        )
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("task-run event cursor has a gap")

    legacy_task_event_ids = {item.event_id for item in bundle.task_run_events}
    for event in bundle.execution_events:
        if event.event_id in legacy_task_event_ids or event.event_id in task_record_event_ids:
            raise ValueError("execution and task event IDs must not overlap")
        if event.payload is None:
            raise ValueError("execution event payload is missing")
    for legacy_task_event in bundle.task_run_events:
        if legacy_task_event.payload is None:
            raise ValueError("task-run event payload is missing")
    for task_record in bundle.task_run_event_records:
        if task_record.event.payload is None:
            raise ValueError("task-run event payload is missing")
    evidence_cursors = [item.cursor for item in bundle.evidence_events]
    if evidence_cursors and evidence_cursors != list(
        range(evidence_cursors[0], evidence_cursors[0] + len(evidence_cursors))
    ):
        raise ValueError("evidence cursor has a gap")
    if any(item.execution_id != bundle.execution.execution_id for item in bundle.evidence_events):
        raise ValueError("evidence event belongs to another execution")
    for artifact in bundle.artifacts:
        if artifact.execution_id != bundle.execution.execution_id:
            raise ValueError("artifact belongs to another execution")
        if artifact.task_run_id not in task_ids:
            raise ValueError("artifact references an unexported task run")
        if artifact.checksum_sha256 is None:
            raise ValueError("artifact is missing its integrity checksum")
        destination = bundle.artifact_destination_refs.get(artifact.uri)
        if destination is None or not destination.strip():
            raise ValueError(f"artifact {artifact.uri} has no declared destination reference")


def _check_no_secrets(bundle: SessionTransferBundle) -> None:
    _walk_for_secrets(bundle.model_dump(mode="json", by_alias=True))


def _walk_for_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key)).replace("-", "_").lower()
            if normalized not in _REFERENCE_KEYS and (
                normalized in _SECRET_KEYS or _SENSITIVE_KEY_PATTERN.search(normalized)
            ):
                raise ValueError(f"session transfer contains secret-bearing field {key!r}")
            _walk_for_secrets(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _walk_for_secrets(item)


def _bundle_checksum(bundle: SessionTransferBundle) -> str:
    payload = bundle.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
    return hashlib.sha256(canonical_json(payload)).hexdigest()


__all__ = [
    "SessionTaskRunEvent",
    "SessionTransferBundle",
    "SessionTransferCompatibilityReport",
    "SessionTransferEligibility",
    "SessionTransferImportRepository",
    "SessionTransferImportResult",
    "SessionTransferMode",
    "SessionTransferService",
    "seal_bundle",
]
