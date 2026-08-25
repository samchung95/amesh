from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest

from amesh.evidence_bundle import (
    CanonicalEvidenceBuilder,
    CostState,
    EvidenceAccessDenied,
    EvidenceBundle,
    EvidenceBundleError,
    EvidenceBundleStore,
    EvidenceConflictError,
    EvidenceCost,
    EvidenceIntegrityError,
    EvidenceNotFoundError,
    EvidencePin,
    EvidencePresence,
    EvidenceRecord,
    EvidenceUnavailableError,
    FilesystemEvidenceObjectStore,
    MemoryEvidenceObjectStore,
    ProtectedContinuation,
    TokenUsage,
)
from amesh.ports import ExecutionEvidenceEvent, ExecutionEvidenceKind


def _record(
    record_id: str,
    sequence: int,
    *,
    payload: dict[str, object] | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        recordId=record_id,
        kind="trace",
        sequence=sequence,
        correlationId="correlation-1",
        occurredAt=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=sequence),
        payload=payload or {"value": sequence},
    )


def _bundle(*records: EvidenceRecord) -> EvidenceBundle:
    return EvidenceBundle(
        executionId="execution-1",
        tenantId="tenant-a",
        correlationId="correlation-1",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
        trace=records,
        tokenUsage=(
            TokenUsage(
                usageId="usage-1",
                correlationId="correlation-1",
                inputTokens=3,
                outputTokens=2,
                totalTokens=5,
            ),
        ),
        costs=(
            EvidenceCost(
                costId="cost-1",
                correlationId="correlation-1",
                state=CostState.UNPRICED,
            ),
        ),
    )


def test_bundle_digest_is_stable_and_order_is_canonical() -> None:
    first = _bundle(_record("second", 2), _record("first", 1))
    recovered = _bundle(_record("first", 1), _record("second", 2))

    assert [item.record_id for item in first.trace] == ["first", "second"]
    assert first.digest == recovered.digest
    assert first.sealed().bundle_digest == first.digest
    first.sealed().verify()


def test_reference_agent_and_tool_execution_exports_and_verifies() -> None:
    pin_digest = "sha256:" + "a" * 64
    bundle = EvidenceBundle(
        executionId="reference-execution",
        tenantId="tenant-a",
        correlationId="correlation-reference",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
        pins=(
            EvidencePin(
                pinId="agent-pin",
                category="agent",
                subject="planner",
                revision="7",
                digest=pin_digest,
            ),
            EvidencePin(
                pinId="tool-pin",
                category="tool",
                subject="search",
                revision="3",
                digest=pin_digest,
            ),
        ),
        agentSessions=(_record("agent-session", 1),),
        externalInvocations=(_record("tool-invocation", 2),),
        controls=(_record("control", 3),),
    ).sealed()

    store = EvidenceBundleStore()
    exported = store.put(bundle)
    recovered = store.get(
        "reference-execution", tenant_id="tenant-a", principal_tenant_id="tenant-a"
    )
    recovered.verify()
    assert exported.digest == recovered.digest == bundle.bundle_digest
    assert {pin.category for pin in recovered.pins} == {"agent", "tool"}


def test_bundle_redacts_secrets_and_omits_hidden_reasoning() -> None:
    bundle = _bundle(
        _record(
            "safe-1",
            1,
            payload={
                "authorization": "secret-canary",
                "nested": {"apiKey": "another-secret"},
                "chainOfThought": "private model reasoning",
                "message": "safe",
            },
        )
    )
    payload = bundle.trace[0].payload

    assert payload["authorization"] == "[REDACTED]"
    assert payload["nested"]["apiKey"] == "[REDACTED]"
    assert payload["chainOfThought"] == "[OMITTED]"
    assert "secret-canary" not in bundle.model_dump_json()
    assert "private model reasoning" not in bundle.model_dump_json()


def test_protected_continuation_is_resumable_but_not_serialized() -> None:
    continuation = ProtectedContinuation.create("provider", "2026.01", "opaque-secret")

    assert continuation.token_for_provider("provider", "2026.01") == "opaque-secret"
    assert "opaque-secret" not in continuation.model_dump_json()
    assert "opaque-secret" not in repr(continuation)
    with pytest.raises(EvidenceAccessDenied):
        continuation.token_for_provider("other", "2026.01")
    unavailable = ProtectedContinuation.model_validate(continuation.model_dump())
    with pytest.raises(EvidenceUnavailableError):
        unavailable.token_for_provider("provider", "2026.01")


def test_cost_and_presence_states_are_explicit() -> None:
    with pytest.raises(ValueError, match="priced cost requires"):
        EvidenceCost(costId="cost", correlationId="c", state=CostState.PRICED)
    with pytest.raises(ValueError, match="present token usage"):
        TokenUsage(usageId="usage", correlationId="c")

    unavailable = EvidenceBundle(
        executionId="e",
        tenantId="t",
        correlationId="c",
        createdAt=datetime.now(UTC),
        sectionStatus={"logs": EvidencePresence.UNAVAILABLE},
    )
    assert unavailable.section_status["logs"] is EvidencePresence.UNAVAILABLE
    assert unavailable.section_status["trace"] is EvidencePresence.ABSENT


def test_large_fields_are_content_addressed_and_corruption_is_detected() -> None:
    store = MemoryEvidenceObjectStore()
    bundle = _bundle(_record("large", 1, payload={"output": "x" * 500}))

    externalized = bundle.externalize_large_fields(store, max_inline_bytes=32)
    reference = externalized.trace[0].payload["externalRef"]
    assert reference["digest"].startswith("sha256:")
    externalized.verify_externalized_fields(store)

    store.tamper(reference["digest"], b"tampered")
    with pytest.raises(EvidenceIntegrityError):
        externalized.verify_externalized_fields(store)


def test_filesystem_object_store_round_trips_and_rejects_corruption(tmp_path: Path) -> None:
    store = FilesystemEvidenceObjectStore(tmp_path / "objects")
    reference = store.put(b"content")
    assert store.get(reference) == b"content"
    (tmp_path / "objects" / reference.digest[7:]).write_bytes(b"corrupt")
    with pytest.raises(EvidenceIntegrityError):
        store.get(reference)


def test_store_is_tenant_scoped_bounded_and_conflict_detecting() -> None:
    store = EvidenceBundleStore()
    bundle = _bundle(*(_record(str(index), index) for index in range(3)))
    stored = store.put(bundle)
    assert store.put(bundle).digest == stored.digest

    page = store.page(
        "execution-1",
        tenant_id="tenant-a",
        principal_tenant_id="tenant-a",
        section="trace",
        limit=2,
    )
    assert [item.record_id for item in page.items] == ["0", "1"]
    assert page.next_cursor == "2"
    next_page = store.page(
        "execution-1",
        tenant_id="tenant-a",
        principal_tenant_id="tenant-a",
        section="trace",
        cursor=page.next_cursor,
        limit=2,
    )
    assert [item.record_id for item in next_page.items] == ["2"]

    with pytest.raises(EvidenceAccessDenied):
        store.get("execution-1", tenant_id="tenant-a", principal_tenant_id="tenant-b")
    with pytest.raises(EvidenceNotFoundError):
        store.get("missing", tenant_id="tenant-a", principal_tenant_id="tenant-a")

    conflicting = _bundle(_record("different", 1))
    with pytest.raises(EvidenceConflictError):
        store.put(conflicting)

    store.available = False
    assert (
        store.read_page(
            "execution-1", tenant_id="tenant-a", principal_tenant_id="tenant-a", section="trace"
        ).state
        is EvidencePresence.UNAVAILABLE
    )


def test_schema_and_bundle_digest_tampering_are_rejected() -> None:
    with pytest.raises(EvidenceBundleError, match="unsupported evidence schema"):
        EvidenceBundle(
            schemaVersion="2.0",
            executionId="e",
            tenantId="t",
            correlationId="c",
            createdAt=datetime.now(UTC),
        ).verify()

    sealed = _bundle(_record("one", 1)).sealed()
    tampered = sealed.model_copy(update={"bundle_digest": "sha256:" + "0" * 64})
    with pytest.raises(EvidenceIntegrityError):
        tampered.verify()


def test_canonical_builder_projects_events_and_preserves_absent_sections() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    bundle = CanonicalEvidenceBuilder.from_events(
        "execution-2",
        "tenant-a",
        [
            {
                "event_id": "event-2",
                "event_type": "state.changed",
                "kind": "STATE",
                "cursor": 2,
                "occurred_at": now,
                "payload": {"state": "SUCCESS"},
            },
            {
                "event_id": "event-1",
                "event_type": "log.info",
                "kind": "LOG",
                "cursor": 1,
                "task_run_id": "task-1",
                "occurred_at": now,
                "payload": {"message": "done", "apiKey": "secret"},
            },
        ],
        created_at=now,
        inputs={"request": "safe"},
    )

    assert [record.record_id for record in bundle.trace] == ["event-1", "event-2"]
    assert bundle.state_transitions[0].record_id == "event-2"
    assert bundle.task_attempts[0].record_id == "event-1"
    assert bundle.inputs[0].payload["request"] == "safe"
    assert bundle.outputs == ()
    assert bundle.section_status["outputs"] is EvidencePresence.ABSENT


def test_canonical_builder_projects_agent_external_and_control_evidence() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    execution_id = UUID("00000000-0000-0000-0000-000000000812")
    task_run_id = UUID("00000000-0000-0000-0000-000000000813")
    events = [
        ExecutionEvidenceEvent(
            cursor=8,
            event_id=UUID("00000000-0000-0000-0000-000000000821"),
            execution_id=execution_id,
            kind=ExecutionEvidenceKind.DECISION,
            event_type="decision.accepted",
            payload={"decision": "approve"},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=7,
            event_id=UUID("00000000-0000-0000-0000-000000000822"),
            execution_id=execution_id,
            kind=ExecutionEvidenceKind.INTERVENTION,
            event_type="intervention.requested",
            payload={"reason": "review"},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=6,
            event_id=UUID("00000000-0000-0000-0000-000000000823"),
            execution_id=execution_id,
            kind=ExecutionEvidenceKind.APPROVAL,
            event_type="approval.granted",
            payload={"actor": "operator"},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=5,
            event_id=UUID("00000000-0000-0000-0000-000000000824"),
            execution_id=execution_id,
            kind=ExecutionEvidenceKind.CONTROL,
            event_type="control.evaluated",
            payload={"allowed": True},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=4,
            event_id=UUID("00000000-0000-0000-0000-000000000825"),
            execution_id=execution_id,
            task_run_id=task_run_id,
            kind=ExecutionEvidenceKind.ERROR,
            event_type="error.external",
            payload={"message": "provider unavailable", "token": "private"},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=3,
            event_id=UUID("00000000-0000-0000-0000-000000000826"),
            execution_id=execution_id,
            task_run_id=task_run_id,
            kind=ExecutionEvidenceKind.TOOL,
            event_type="tool.result",
            payload={"usage": {"total_tokens": 2}},
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=2,
            event_id=UUID("00000000-0000-0000-0000-000000000827"),
            execution_id=execution_id,
            task_run_id=task_run_id,
            kind=ExecutionEvidenceKind.MODEL,
            event_type="model.response",
            payload={
                "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7},
                "costUsd": "0.0007",
                "reasoning": "private chain of thought",
            },
            occurred_at=now,
            ingested_at=now,
        ),
        ExecutionEvidenceEvent(
            cursor=1,
            event_id=UUID("00000000-0000-0000-0000-000000000828"),
            execution_id=execution_id,
            task_run_id=task_run_id,
            kind=ExecutionEvidenceKind.STATE,
            event_type="agent.session.started",
            payload={"sessionId": "session-reference"},
            occurred_at=now,
            ingested_at=now,
        ),
    ]

    first = CanonicalEvidenceBuilder.from_events(
        execution_id,
        "tenant-a",
        events,
        created_at=now,
    ).sealed()
    recovered = CanonicalEvidenceBuilder.from_events(
        execution_id,
        "tenant-a",
        list(reversed(events)),
        created_at=now,
    ).sealed()

    assert first.digest == recovered.digest == first.bundle_digest
    assert len(first.agent_sessions) == 1
    assert {record.kind for record in first.external_invocations} == {
        "model.response",
        "tool.result",
    }
    assert len(first.errors) == len(first.approvals) == len(first.interventions) == 1
    assert len(first.controls) == len(first.decisions) == 1
    assert {item.total_tokens for item in first.token_usage} == {2, 7}
    priced = next(item for item in first.costs if item.state is CostState.PRICED)
    assert priced.amount == "0.0007"
    assert first.external_invocations[0].payload["reasoning"] == "[OMITTED]"
    assert first.errors[0].payload["token"] == "[REDACTED]"
