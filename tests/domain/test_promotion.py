from datetime import UTC, datetime, timedelta

import pytest

from amesh.domain.promotion import (
    EvidenceArtifact,
    EvidenceRequirement,
    PromotionEvidenceKind,
    PromotionPolicy,
    PromotionTargetKind,
    evaluate_promotion_gate,
)


def _digest(char: str) -> str:
    return "sha256:" + char * 64


def _policy(*, evidence_digest: str) -> PromotionPolicy:
    return PromotionPolicy(
        tenantId="tenant-a",
        targetKind=PromotionTargetKind.WORKFLOW,
        targetKey="checkout",
        targetRevision=2,
        configurationDigest=_digest("a"),
        requiredEvidence=(
            EvidenceRequirement(
                kind=PromotionEvidenceKind.TEST,
                key="unit",
                digest=evidence_digest,
            ),
        ),
        createdBy="release-manager",
    )


def _evidence(digest: str, *, captured_at: datetime) -> EvidenceArtifact:
    return EvidenceArtifact(
        tenantId="tenant-a",
        kind=PromotionEvidenceKind.TEST,
        key="unit",
        digest=digest,
        configurationDigest=_digest("a"),
        passed=True,
        capturedAt=captured_at,
    )


def test_gate_requires_exact_fresh_digest_and_configuration() -> None:
    now = datetime.now(UTC)
    digest = _digest("b")
    policy = _policy(evidence_digest=digest)
    passed = evaluate_promotion_gate(policy, [_evidence(digest, captured_at=now)], now=now)
    assert passed.passed

    stale = evaluate_promotion_gate(
        policy,
        [_evidence(digest, captured_at=now - timedelta(days=2))],
        now=now,
    )
    assert not stale.passed
    assert "stale evidence" in " ".join(stale.failures)


def test_gate_rejects_mismatched_evidence_digest() -> None:
    now = datetime.now(UTC)
    gate = evaluate_promotion_gate(
        _policy(evidence_digest=_digest("b")),
        [_evidence(_digest("c"), captured_at=now)],
        now=now,
    )
    assert not gate.passed
    assert any("digest mismatch" in failure for failure in gate.failures)


def test_policy_is_immutable_and_requirement_keys_are_unique() -> None:
    with pytest.raises(ValueError, match="unique"):
        PromotionPolicy(
            tenantId="tenant-a",
            targetKind="WORKFLOW",
            targetKey="checkout",
            targetRevision=1,
            configurationDigest=_digest("a"),
            requiredEvidence=(
                EvidenceRequirement(kind="TEST", key="unit", digest=_digest("b")),
                EvidenceRequirement(kind="TEST", key="unit", digest=_digest("c")),
            ),
            createdBy="release-manager",
        )
