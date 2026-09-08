from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.adapters.postgres.transfer_repository import (
    PostgresTransferRepository,
    _credential_rebinding_diagnostics,
)
from amesh.domain.agent_primitives import (
    AgentInvocationAccounting,
    AgentInvocationKind,
    AgentInvocationRecord,
    AgentInvocationState,
)
from amesh.domain.agent_resources import (
    AgentCapabilityPin,
    AgentEvaluationPolicy,
    AgentHardLimits,
    AgentMemoryPolicy,
    AgentPermissions,
    EffectiveCapabilityEnvelope,
    InstructionFragment,
    ModelFallbackMode,
    ResolvedResourcePin,
)
from amesh.domain.agent_sessions import (
    AgentHarnessPin,
    AgentSessionCheckpoint,
    AgentSessionCounters,
    AgentSessionEvent,
    AgentSessionPhase,
    AgentSessionRecord,
    AgentSessionState,
)
from amesh.domain.execution import ExecutionState, TaskRunState
from amesh.ports.execution_repository import PersistedExecution, PersistedTaskRun
from amesh.ports.metadata_repository import (
    ExecutionArtifact,
    ExecutionEvidenceEvent,
    ExecutionEvidenceKind,
)
from amesh.ports.object_store import ObjectMetadata
from amesh.session_transfer import (
    SessionTransferBundle,
    SessionTransferImportResult,
    SessionTransferMode,
    SessionTransferService,
    _bundle_checksum,
    seal_bundle,
)


class FakeImportRepository:
    def __init__(self) -> None:
        self.results: dict[tuple[str, str], SessionTransferImportResult] = {}
        self.calls = 0

    async def get_import(
        self, target_tenant_id: str, import_id: str
    ) -> SessionTransferImportResult | None:
        return self.results.get((target_tenant_id, import_id))

    async def import_records(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        actor_id: str,
        import_id: str,
    ) -> SessionTransferImportResult:
        self.calls += 1
        result = SessionTransferImportResult(
            importId=import_id,
            bundleDigest=bundle.checksum_sha256,
            mode=bundle.mode,
            targetTenantId=target_tenant_id,
            sessionId=str(bundle.session.session_id),
        )
        self.results[(target_tenant_id, import_id)] = result
        return result


class FakeArtifactStore:
    def __init__(self, metadata: ObjectMetadata) -> None:
        self.metadata = metadata

    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        assert tenant_id == self.metadata.tenant_id
        assert uri == self.metadata.uri
        return self.metadata


def _bundle(
    mode: SessionTransferMode = SessionTransferMode.TERMINAL_HISTORY,
    *,
    invocation_state: AgentInvocationState | None = None,
    invocation_accounting: AgentInvocationAccounting | None = None,
    event_indices: tuple[int, ...] = (1, 2),
) -> SessionTransferBundle:
    tenant_id = "source"
    execution_id = uuid4()
    task_run_id = uuid4()
    session_id = uuid4()
    capability_pin_id = uuid4()
    now = datetime.now(UTC)
    resource = ResolvedResourcePin(
        resourceId=uuid4(), kind="PROMPT", key="prompt", revision=1, digest="sha256:" + "a" * 64
    )
    envelope = EffectiveCapabilityEnvelope(
        agent=resource,
        resources=(resource,),
        instructions=(
            InstructionFragment(sourceKind="AGENT", sourceKey="agent", order=0, content="Do"),
        ),
        promptVariables={},
        modelRoutes=(),
        fallbackMode=ModelFallbackMode.DISABLED,
        outputNondeterminismDisclosure="May vary.",
        tools=(),
        inputSchema={"type": "object"},
        outputSchema={"type": "object"},
        memoryPolicy=AgentMemoryPolicy(),
        permissions=AgentPermissions(),
        hardLimits=AgentHardLimits(
            maxTotalTokens=10,
            maxCostUsd=Decimal("1"),
            maxDurationSeconds=10,
            maxToolCalls=0,
            maxTurns=1,
            maxLoopIterations=0,
            maxRecursionDepth=0,
            maxConcurrency=1,
        ),
        evaluationPolicy=AgentEvaluationPolicy(),
    )
    pin = AgentCapabilityPin(
        pinId=capability_pin_id,
        tenantId=tenant_id,
        namespace="agents.demo",
        subjectRef="session",
        envelopeDigest=envelope.digest,
        envelope=envelope,
        createdBy="author",
        createdAt=now,
    )
    terminal = mode is SessionTransferMode.TERMINAL_HISTORY
    session = AgentSessionRecord(
        sessionId=session_id,
        tenantId=tenant_id,
        namespace="agents.demo",
        executionId=execution_id,
        taskRunId=task_run_id,
        attempt=1,
        capabilityPinId=capability_pin_id,
        envelopeDigest=envelope.digest,
        harness=AgentHarnessPin(adapter="pi", adapterVersion="1", protocol="v1"),
        state=AgentSessionState.SUCCEEDED if terminal else AgentSessionState.RUNNING,
        phase=AgentSessionPhase.COMPLETE if terminal else AgentSessionPhase.READY,
        version=len(event_indices),
        checkpoint=AgentSessionCheckpoint(),
        counters=AgentSessionCounters(),
        finalResult={"ok": True} if terminal else None,
        completedAt=now if terminal else None,
        createdAt=now,
        updatedAt=now,
    )
    execution = PersistedExecution(
        execution_id=execution_id,
        tenant_id=tenant_id,
        state=ExecutionState.SUCCESS if terminal else ExecutionState.PAUSED,
        epoch=1,
        version=2,
        namespace="agents.demo",
        flow_id="flow",
        flow_revision=1,
        created_at=now,
        updated_at=now,
    )
    task = PersistedTaskRun(
        task_run_id=task_run_id,
        execution_id=execution_id,
        task_id="agent",
        state=TaskRunState.SUCCESS,
        current_attempt=1,
        version=1,
    )
    events = tuple(
        AgentSessionEvent(
            sessionId=session_id,
            eventIndex=index,
            eventKey=f"event-{index}",
            eventType="STEP",
            occurredAt=now,
        )
        for index in event_indices
    )
    invocations = ()
    if invocation_state is not None:
        invocations = (
            AgentInvocationRecord(
                invocationId=uuid4(),
                tenantId=tenant_id,
                namespace="agents.demo",
                executionId=execution_id,
                taskRunId=task_run_id,
                attempt=1,
                kind=AgentInvocationKind.MODEL,
                operation="chat",
                requestHash="a" * 64,
                state=invocation_state,
                accounting=invocation_accounting,
                startedAt=now,
                completedAt=(now if invocation_state is not AgentInvocationState.STARTED else None),
            ),
        )
    evidence = (
        ExecutionEvidenceEvent(
            cursor=1,
            event_id=uuid4(),
            execution_id=execution_id,
            task_run_id=task_run_id,
            kind=ExecutionEvidenceKind.AGENT,
            event_type="agent",
            payload={},
            occurred_at=now,
            ingested_at=now,
        ),
    )
    unsigned = SessionTransferBundle(
        mode=mode,
        sourceTenantId=tenant_id,
        session=session,
        events=events,
        execution=execution,
        taskRuns=(task,),
        invocations=invocations,
        evidenceEvents=evidence,
        capabilityPin=pin,
        checksumSha256="0" * 64,
    )
    return seal_bundle(unsigned)


def test_terminal_and_clean_checkpoint_eligibility() -> None:
    terminal = _bundle()
    clean = _bundle(SessionTransferMode.CLEAN_CHECKPOINT)
    service = SessionTransferService(FakeImportRepository())
    terminal_result = service.eligibility(terminal)
    clean_result = service.eligibility(clean)
    assert terminal_result.eligible
    assert clean_result.eligible
    assert terminal_result.reasons == ()
    assert clean_result.reasons == ()


def test_credential_rebinding_requires_same_stable_reference() -> None:
    bundle = _bundle()
    with_reference = bundle.model_copy(
        update={
            "execution": bundle.execution.model_copy(
                update={"inputs": {"credentialRef": "model-key"}}
            )
        }
    )
    assert _credential_rebinding_diagnostics(with_reference, None)
    assert _credential_rebinding_diagnostics(with_reference, {"model-key": "target-key"})
    assert not _credential_rebinding_diagnostics(with_reference, {"model-key": "model-key"})


def test_artifact_destination_requires_exact_tenant_size_and_checksum() -> None:
    async def scenario() -> None:
        bundle = _bundle()
        artifact = ExecutionArtifact(
            artifact_id=uuid4(),
            execution_id=bundle.execution.execution_id,
            task_run_id=bundle.task_runs[0].task_run_id,
            attempt=1,
            uri="s3://source/result.json",
            size_bytes=12,
            checksum_sha256="a" * 64,
            occurred_at=bundle.session.updated_at,
            ingested_at=bundle.session.updated_at,
        )
        transferable = seal_bundle(
            bundle.model_copy(
                update={
                    "artifacts": (artifact,),
                    "artifact_destination_refs": {artifact.uri: "s3://target/result.json"},
                    "checksum_sha256": "0" * 64,
                }
            )
        )
        metadata = ObjectMetadata(
            uri="s3://target/result.json",
            tenant_id="target",
            size=12,
            checksum_sha256="a" * 64,
        )
        repository = PostgresTransferRepository(
            cast(AsyncEngine, object()), object_store=FakeArtifactStore(metadata)
        )
        await repository.verify_artifact_references(transferable, target_tenant_id="target")

        mismatched = PostgresTransferRepository(
            cast(AsyncEngine, object()),
            object_store=FakeArtifactStore(metadata.model_copy(update={"size": 11})),
        )
        with pytest.raises(ValueError, match="failed size/checksum verification"):
            await mismatched.verify_artifact_references(transferable, target_tenant_id="target")

    asyncio.run(scenario())


def test_ambiguous_invocation_is_rejected() -> None:
    bundle = _bundle(invocation_state=AgentInvocationState.STARTED)
    result = SessionTransferService(FakeImportRepository()).eligibility(bundle)
    assert not result.eligible
    assert any("STARTED" in reason for reason in result.reasons)


def test_in_doubt_invocation_accounting_is_transferable_without_private_content() -> None:
    accounting = AgentInvocationAccounting(
        inputTokens=12,
        outputTokens=8,
        reasoningTokens=5,
        totalTokens=20,
        cacheReadTokens=4,
        cacheWriteTokens=1,
        costState="billed",
        costAmountUsd="0.0002",
    )
    bundle = _bundle(
        invocation_state=AgentInvocationState.IN_DOUBT,
        invocation_accounting=accounting,
    )

    restored = SessionTransferBundle.model_validate(bundle.model_dump(mode="json", by_alias=True))

    assert SessionTransferService(FakeImportRepository()).eligibility(restored).eligible
    assert restored.invocations[0].state is AgentInvocationState.IN_DOUBT
    assert restored.invocations[0].accounting == accounting
    assert "reasoningContent" not in restored.canonical_bytes().decode("utf-8")


def test_active_lease_or_claim_is_rejected() -> None:
    bundle = _bundle()
    blocked = seal_bundle(
        bundle.model_copy(
            update={
                "active_lease_count": 1,
                "active_admission_claim_count": 1,
                "checksum_sha256": "0" * 64,
            }
        )
    )
    result = SessionTransferService(FakeImportRepository()).eligibility(blocked)
    assert not result.eligible
    assert "active lease exists" in result.reasons
    assert "active admission claim exists" in result.reasons


def test_clean_checkpoint_rejects_pending_action() -> None:
    bundle = _bundle(SessionTransferMode.CLEAN_CHECKPOINT)
    checkpoint = bundle.session.checkpoint.model_copy(update={"pending_action": {"tool": "search"}})
    blocked = seal_bundle(
        bundle.model_copy(
            update={
                "session": bundle.session.model_copy(update={"checkpoint": checkpoint}),
                "checksum_sha256": "0" * 64,
            }
        )
    )
    result = SessionTransferService(FakeImportRepository()).eligibility(blocked)
    assert not result.eligible
    assert "checkpoint has a pending action" in result.reasons


def test_cursor_gap_and_tenant_mismatch_are_rejected() -> None:
    valid = _bundle()
    gap_events = (valid.events[0].model_copy(update={"event_index": 3}), valid.events[1])
    gap = valid.model_copy(update={"events": gap_events, "checksum_sha256": "0" * 64})
    gap = gap.model_copy(update={"checksum_sha256": _bundle_checksum(gap)})
    result = SessionTransferService(FakeImportRepository()).eligibility(gap)
    assert not result.eligible
    assert any("cursor" in reason for reason in result.reasons)

    valid = _bundle()
    foreign = valid.execution.model_copy(update={"tenant_id": "other"})
    with pytest.raises(ValueError, match="another tenant"):
        seal_bundle(valid.model_copy(update={"execution": foreign, "checksum_sha256": "0" * 64}))


def test_tampering_is_detected_and_secret_fields_are_rejected() -> None:
    bundle = _bundle()
    with pytest.raises(ValueError, match="checksum"):
        bundle.model_copy(update={"source_tenant_id": "tampered"}).verify()
    unsafe_event = bundle.events[0].model_copy(update={"payload": {"accessTokenValue": "plain"}})
    unsafe = bundle.model_copy(
        update={"events": (unsafe_event, *bundle.events[1:]), "checksum_sha256": "0" * 64}
    )
    with pytest.raises(ValueError, match="secret-bearing"):
        seal_bundle(unsafe)


def test_import_identity_is_idempotent() -> None:
    async def scenario() -> None:
        repository = FakeImportRepository()
        service = SessionTransferService(repository)
        bundle = _bundle()
        first = await service.import_bundle(bundle, target_tenant_id="target", actor_id="admin")
        second = await service.import_bundle(bundle, target_tenant_id="target", actor_id="admin")
        assert first.already_present is False
        assert second.already_present is True
        assert first.import_id == second.import_id == bundle.import_id
        assert repository.calls == 1
        changed = seal_bundle(
            bundle.model_copy(
                update={
                    "session": bundle.session.model_copy(update={"final_result": {"ok": False}}),
                    "checksum_sha256": "0" * 64,
                }
            )
        )
        with pytest.raises(ValueError, match="another bundle"):
            await service.import_bundle(changed, target_tenant_id="target", actor_id="admin")
        assert repository.calls == 1

    asyncio.run(scenario())
