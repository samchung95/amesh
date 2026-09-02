import json
from pathlib import Path

from amesh.compatibility.kestra import (
    ConformanceObservation,
    ConformanceTolerance,
    SideEffectMode,
    compare_observations,
    import_kestra_flow,
    plan_shadow_execution,
)

FIXTURE = Path(__file__).parent / "fixtures" / "kestra-1.3.30-observations.json"
KESTRA_HTTP_TYPE = "io" + ".kestra.plugin.core.http.Request"


def test_pinned_non_destructive_observations_compare_with_explicit_tolerance() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    reference = ConformanceObservation.model_validate(payload["reference"])
    candidate = ConformanceObservation.model_validate(payload["candidate"])

    report = compare_observations(
        reference,
        candidate,
        tolerance=ConformanceTolerance(durationMs=100),
    )

    assert report.passed is True
    assert report.full_compatibility_claim_allowed is False
    assert len(report.differences) == 1
    assert report.differences[0].field == "duration_ms"
    assert report.differences[0].tolerated is True


def test_state_or_payload_difference_fails_conformance() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    reference = ConformanceObservation.model_validate(payload["reference"])
    candidate_payload = payload["candidate"] | {"stateSequence": ["CREATED", "RUNNING", "FAILED"]}

    report = compare_observations(
        reference,
        ConformanceObservation.model_validate(candidate_payload),
    )

    assert report.passed is False
    assert {item.field for item in report.differences} == {"state_sequence", "duration_ms"}


def test_shadow_plan_suppresses_mocks_or_requires_idempotent_external_calls() -> None:
    imported = import_kestra_flow(
        f"""id: shadow
namespace: compatibility
tasks:
  - id: notify
    type: {KESTRA_HTTP_TYPE}
    uri: https://example.invalid/callback
    method: POST
"""
    )
    assert imported.valid is True

    suppressed = plan_shadow_execution(imported, mode=SideEffectMode.SUPPRESS)
    missing_mock = plan_shadow_execution(imported, mode=SideEffectMode.MOCK)
    mocked = plan_shadow_execution(
        imported,
        mode=SideEffectMode.MOCK,
        mock_outputs={"notify": {"statusCode": 202}},
    )
    unsafe_idempotent = plan_shadow_execution(imported, mode=SideEffectMode.IDEMPOTENT)

    assert suppressed.executable is True
    assert suppressed.candidate_document["tasks"][0]["type"] == "core.return"
    assert missing_mock.executable is False
    assert mocked.executable is True
    assert mocked.candidate_document["tasks"][0]["value"] == {"statusCode": 202}
    assert unsafe_idempotent.executable is False

    idempotent = import_kestra_flow(
        f"""id: shadow
namespace: compatibility
tasks:
  - id: notify
    type: {KESTRA_HTTP_TYPE}
    uri: https://example.invalid/callback
    method: POST
    headers:
      Idempotency-Key: shadow-execution-1
"""
    )
    safe_idempotent = plan_shadow_execution(idempotent, mode=SideEffectMode.IDEMPOTENT)
    assert safe_idempotent.executable is True
    assert safe_idempotent.candidate_document["tasks"][0]["type"] == "core.http"
