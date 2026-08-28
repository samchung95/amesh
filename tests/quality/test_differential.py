from __future__ import annotations

import json
from decimal import Decimal
from hashlib import sha256
from uuid import uuid4

import pytest

from amesh.quality import (
    ComparisonCategory,
    ComparisonDifference,
    ComparisonPolicy,
    ConfigurationPin,
    DifferentialService,
    DifferentialSpec,
    FixtureSource,
    RunObservation,
    ShadowExecutionError,
    ShadowFixture,
    ShadowRunContext,
    Tolerance,
)


def _fixture(key: str, source: FixtureSource = FixtureSource.SAFE_FIXTURE) -> ShadowFixture:
    value = {"status": "ok"}
    payload = json.dumps(
        {"key": key, "source": source.value, "value": value},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    return ShadowFixture(
        key=key, source=source, value=value, certificate="sha256:" + sha256(payload).hexdigest()
    )


def _spec(**updates: object) -> DifferentialSpec:
    values: dict[str, object] = {
        "tenantId": "tenant-a",
        "namespace": "quality",
        "left": {"key": "workflow", "revision": 1, "digest": "sha256:" + "1" * 64},
        "right": {"key": "workflow", "revision": 2, "digest": "sha256:" + "2" * 64},
        "inputs": {"prompt": "hello"},
        "idempotencyKey": "diff-1",
    }
    values.update(updates)
    return DifferentialSpec(**values)


def test_spec_pins_frozen_inputs_and_requires_certified_fixture() -> None:
    spec = _spec(fixtures=(_fixture("weather"),))
    assert spec.input_digest.startswith("sha256:")
    assert spec.fixture("weather") is not None
    spec.inputs["prompt"] = "mutated"
    with pytest.raises(ValueError, match="frozen inputs changed"):
        DifferentialService().run(spec, lambda configuration, inputs, context: RunObservation())
    with pytest.raises(ValueError, match="inputDigest"):
        _spec(inputDigest="sha256:" + "0" * 64)


def test_shadow_context_denies_uncontrolled_effects() -> None:
    context = ShadowRunContext(_spec())
    with pytest.raises(ShadowExecutionError, match="no certified fixture"):
        context.effect("send-email")

    context = ShadowRunContext(_spec(fixtures=(_fixture("recorded"),)))
    assert context.effect("send-email", fixture_key="recorded") == {"status": "ok"}


def test_structural_comparator_separates_contract_nondeterminism_and_tolerance() -> None:
    spec = _spec(
        policy=ComparisonPolicy(
            nondeterministicPaths=("output.requestId",),
            usageTolerance=Tolerance(absolute=Decimal("2")),
            latencyTolerance=Tolerance(absolute=Decimal("10")),
        )
    )
    service = DifferentialService()

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del inputs, context
        return RunObservation(
            schema={"type": "object"},
            output={"value": 1, "requestId": configuration.revision},
            deterministicAssertions=({"name": "valid", "passed": True},),
            taskChronology=({"task": "one", "state": "SUCCESS"},),
            toolChronology=(),
            evidence=({"kind": "trace"},),
            usage={"tokens": Decimal("10") + configuration.revision},
            latency=Decimal("100") + configuration.revision,
        )

    report = service.run(spec, execute)
    assert report.passed
    assert report.deterministic_failures == ()
    assert {item.category for item in report.nondeterministic_observations} == {
        ComparisonCategory.NONDETERMINISTIC_OBSERVATION
    }
    assert {item.category for item in report.tolerated_differences} == {
        ComparisonCategory.TOLERATED_DIFFERENCE
    }


def test_comparator_classifies_contract_and_evidence_regressions() -> None:
    spec = _spec()
    service = DifferentialService()

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del inputs, context
        return RunObservation(
            schema={"type": "object", "required": ["value"]}
            if configuration.revision == 1
            else {"type": "object", "required": ["other"]},
            taskChronology=({"task": "one", "state": "SUCCESS"},),
            evidence=({"event": "accepted", "revision": configuration.revision},),
        )

    report = service.run(spec, execute)
    assert not report.passed
    assert {item.code for item in report.deterministic_failures} >= {
        "SCHEMA_MISMATCH",
        "EVIDENCE_MISMATCH",
    }


def test_nondeterminism_policy_cannot_mask_schema_regressions() -> None:
    spec = _spec(policy=ComparisonPolicy(nondeterministicPaths=("schema.version",)))
    service = DifferentialService()

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del inputs, context
        return RunObservation(schema={"version": configuration.revision})

    report = service.run(spec, execute)
    assert any(item.code == "SCHEMA_MISMATCH" for item in report.deterministic_failures)
    assert report.nondeterministic_observations == ()


def test_service_idempotency_is_tenant_isolated() -> None:
    service = DifferentialService()
    calls = 0

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        nonlocal calls
        del configuration, inputs, context
        calls += 1
        return RunObservation(output={"value": 1})

    spec = _spec()
    first = service.run(spec, execute)
    second = service.run(spec, execute)
    assert first == second
    assert calls == 2
    assert service.get("tenant-a", "quality", "diff-1") == first

    other_tenant = _spec(tenantId="tenant-b")
    service.run(other_tenant, execute)
    assert calls == 4

    with pytest.raises(ValueError, match="different differential request"):
        service.run(_spec(inputs={"prompt": "different"}), execute)


def test_provider_neutral_comparator_extensions_are_additive() -> None:
    class Extension:
        def compare(
            self, left: object, right: object, policy: ComparisonPolicy
        ) -> tuple[ComparisonDifference, ...]:
            del left, right, policy
            return (
                ComparisonDifference(
                    category=ComparisonCategory.TOLERATED_DIFFERENCE,
                    code="EXTENSION_NOTE",
                    path="extension",
                    detail="extension evidence",
                ),
            )

    service = DifferentialService(comparators=(Extension(),))

    def execute(
        configuration: ConfigurationPin, inputs: object, context: ShadowRunContext
    ) -> RunObservation:
        del configuration, inputs, context
        return RunObservation()

    report = service.run(_spec(), execute)
    assert [item.code for item in report.tolerated_differences] == ["EXTENSION_NOTE"]


def test_spec_ids_are_independent_from_run_lineage() -> None:
    first = _spec()
    second = _spec()
    assert first.spec_id != second.spec_id
    assert uuid4() != first.spec_id
