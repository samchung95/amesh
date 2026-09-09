from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.domain.agent_tool_plan import (
    ExpandedToolPlan,
    RequiredToolPlan,
    RequiredToolStep,
    ToolPlanExpansionError,
    ToolPlanLedger,
    ToolPlanLedgerError,
    ToolPlanMatchError,
    ToolPlanOrderError,
    tool_call_digest,
)


def _plan(*steps: RequiredToolStep, max_occurrences: int = 1_000) -> RequiredToolPlan:
    return RequiredToolPlan(steps=steps, maxOccurrences=max_occurrences)


def test_expansion_preserves_step_and_collection_order_and_binds_item_arguments() -> None:
    plan = _plan(
        RequiredToolStep(
            stepId="quote",
            toolName="market.quote",
            forEach="/symbols",
            itemArgumentBindings={"symbol": "/ticker"},
            arguments={"market": "US"},
        ),
        RequiredToolStep(
            stepId="filing",
            toolName="sec.filing",
            argumentBindings={"symbol": "/focus"},
            arguments={"form": "10-K"},
        ),
    )

    expanded = plan.expand(
        {
            "symbols": [{"ticker": "JPM"}, {"ticker": "MSFT"}],
            "focus": "AAPL",
        }
    )

    assert [
        (item.occurrence_id, item.tool_name, item.arguments) for item in expanded.occurrences
    ] == [
        ("quote:0", "market.quote", {"market": "US", "symbol": "JPM"}),
        ("quote:1", "market.quote", {"market": "US", "symbol": "MSFT"}),
        ("filing:0", "sec.filing", {"form": "10-K", "symbol": "AAPL"}),
    ]
    assert expanded.occurrences[0].sequence == 1
    assert expanded.occurrences[-1].sequence == 3
    assert expanded.plan_digest == plan.digest


def test_expansion_supports_rfc6901_escapes_and_root_item_binding() -> None:
    plan = _plan(
        RequiredToolStep(
            stepId="escaped",
            toolName="example.lookup",
            forEach="/items",
            itemArgumentBindings={"name": "/a~1b", "whole": ""},
        )
    )

    expanded = plan.expand({"items": [{"a/b": "value"}]})

    assert expanded.occurrences[0].arguments == {
        "name": "value",
        "whole": {"a/b": "value"},
    }


@pytest.mark.parametrize(
    ("step", "runtime_input", "message"),
    [
        (
            RequiredToolStep(stepId="missing", toolName="x", forEach="/candidates"),
            {},
            "does not resolve",
        ),
        (
            RequiredToolStep(stepId="scalar", toolName="x", forEach="/candidate"),
            {"candidate": "not-an-array"},
            "must select an array",
        ),
        (
            RequiredToolStep(
                stepId="item",
                toolName="x",
                forEach="/candidates",
                itemArgumentBindings={"id": "/id"},
            ),
            {"candidates": [{}]},
            "does not resolve",
        ),
    ],
)
def test_expansion_rejects_invalid_runtime_pointers(
    step: RequiredToolStep, runtime_input: object, message: str
) -> None:
    with pytest.raises(ToolPlanExpansionError, match=message):
        _plan(step).expand(runtime_input)


def test_expansion_is_bounded_per_step_and_across_plan() -> None:
    step = RequiredToolStep(stepId="quotes", toolName="quote", forEach="/symbols", maxOccurrences=2)
    with pytest.raises(ToolPlanExpansionError, match="limit is 2"):
        _plan(step).expand({"symbols": ["A", "B", "C"]})

    with pytest.raises(ToolPlanExpansionError, match="1-occurrence limit"):
        _plan(
            RequiredToolStep(stepId="one", toolName="one"),
            RequiredToolStep(stepId="two", toolName="two"),
            max_occurrences=1,
        ).expand({})


def test_expansion_can_bind_root_input_and_each_candidate_without_ambiguous_scope() -> None:
    expanded = _plan(
        RequiredToolStep(
            stepId="filings",
            toolName="filing.lookup",
            forEach="/sections",
            argumentBindings={"symbol": "/symbol"},
            itemArgumentBindings={"section": ""},
        )
    ).expand({"symbol": "JPM", "sections": ["risk", "guidance"]})

    assert [item.arguments for item in expanded.occurrences] == [
        {"symbol": "JPM", "section": "risk"},
        {"symbol": "JPM", "section": "guidance"},
    ]


def test_plan_and_call_digests_are_canonical_and_duplicate_occurrences_are_distinct() -> None:
    left = _plan(RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"b": 2, "a": 1}))
    right = _plan(RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"a": 1, "b": 2}))
    assert left.digest == right.digest
    assert tool_call_digest("lookup", {"b": 2, "a": 1}) == tool_call_digest(
        "lookup", {"a": 1, "b": 2}
    )

    expanded = _plan(
        RequiredToolStep(stepId="first", toolName="lookup", arguments={"symbol": "JPM"}),
        RequiredToolStep(stepId="second", toolName="lookup", arguments={"symbol": "JPM"}),
    ).expand({})
    assert [item.occurrence_id for item in expanded.occurrences] == ["first:0", "second:0"]
    assert expanded.occurrences[0].call_digest == expanded.occurrences[1].call_digest


def test_ledger_matches_exact_next_occurrence_and_rejects_changed_or_reordered_calls() -> None:
    expanded = _plan(
        RequiredToolStep(stepId="first", toolName="first", arguments={"value": 1}),
        RequiredToolStep(stepId="second", toolName="second", arguments={"value": 2}),
    ).expand({})
    ledger = ToolPlanLedger.from_expanded(expanded)

    with pytest.raises(ToolPlanMatchError, match="first"):
        ledger.match("first", {"value": 9})
    with pytest.raises(ToolPlanOrderError, match="later required occurrence"):
        ledger.match("second", {"value": 2})

    first = ledger.match("first", {"value": 1})
    assert first is not None
    ledger = ledger.record_success(first, attempt_key="attempt-1")
    assert ledger.match("second", {"value": 2}) == expanded.occurrences[1]


def test_ledger_failure_is_retryable_and_success_is_restart_safe_and_monotonic() -> None:
    expanded = _plan(
        RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"symbol": "JPM"}),
        RequiredToolStep(stepId="filing", toolName="filing", arguments={"symbol": "JPM"}),
    ).expand({})
    ledger = ToolPlanLedger.from_expanded(expanded)
    occurrence = ledger.match("lookup", {"symbol": "JPM"})
    assert occurrence is not None
    failed = ledger.record_failure(occurrence, attempt_key="attempt-1", error_code="TIMEOUT")
    assert not failed.is_complete
    assert failed.entries[0].attempt_count == 1
    assert failed.match("lookup", {"symbol": "JPM"}) == occurrence

    reloaded = ToolPlanLedger.model_validate(failed.model_dump(mode="json", by_alias=True))
    result_digest = tool_call_digest("result", {"ok": True})
    succeeded = reloaded.record_success(
        occurrence,
        attempt_key="attempt-2",
        result_digest=result_digest,
    )
    assert succeeded.entries[0].attempt_count == 2
    assert not succeeded.is_complete

    # A duplicate replay of the already accepted occurrence is a no-op, not a second completion.
    assert (
        succeeded.record_success(
            occurrence,
            attempt_key="replayed-attempt",
            result_digest=result_digest,
        )
        == succeeded
    )
    second = succeeded.match("filing", {"symbol": "JPM"})
    assert second is not None
    complete = succeeded.record_success(second, attempt_key="attempt-3")
    assert complete.is_complete
    assert complete.missing_occurrences == ()

    with pytest.raises(ToolPlanLedgerError, match="cannot be failed"):
        complete.record_failure(second, attempt_key="attempt-4", error_code="LATE_FAILURE")


def test_ledger_rejects_forged_occurrence_even_when_occurrence_id_matches() -> None:
    expanded = _plan(
        RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"x": 1})
    ).expand({})
    ledger = ToolPlanLedger.from_expanded(expanded)
    forged = expanded.occurrences[0].model_copy(update={"arguments": {"x": 2}})
    with pytest.raises(ToolPlanLedgerError, match="exact expanded occurrence"):
        ledger.record_success(forged, attempt_key="attempt-1")


def test_contract_rejects_duplicate_step_ids_and_invalid_pointer_escapes() -> None:
    with pytest.raises(ValidationError, match="stepId values must be unique"):
        _plan(
            RequiredToolStep(stepId="same", toolName="one"),
            RequiredToolStep(stepId="same", toolName="two"),
        )
    with pytest.raises(ValidationError, match="invalid JSON Pointer escape"):
        RequiredToolStep(stepId="bad", toolName="x", argumentBindings={"value": "/a~2b"})


def test_expanded_plan_round_trip_preserves_digest_and_order() -> None:
    expanded = _plan(
        RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"x": 1})
    ).expand({})
    restored = ExpandedToolPlan.model_validate(expanded.model_dump(mode="json", by_alias=True))
    assert restored == expanded
    assert restored.digest == expanded.digest


ACCEPTED_SCHEMA = {
    "type": "object",
    "required": ["accepted"],
    "properties": {"accepted": {"const": True}},
}


def _unordered_ledger() -> ToolPlanLedger:
    plan = RequiredToolPlan(
        mode="UNORDERED",
        steps=(
            RequiredToolStep(
                stepId="submit",
                toolName="submit",
                successSchema=ACCEPTED_SCHEMA,
                argumentBindings={"owner": "/owner"},
            ),
            RequiredToolStep(stepId="check", toolName="check", successSchema=ACCEPTED_SCHEMA),
        ),
    )
    return ToolPlanLedger.from_expanded(plan.expand({"owner": "trusted"})).model_copy(
        update={"session_id": uuid4()}
    )


def test_unordered_results_allow_reverse_order_generated_arguments_and_correction() -> None:
    ledger = _unordered_ledger()
    session_id = ledger.session_id
    assert session_id is not None
    assert ledger.session_id is not None
    assert ledger.match("other", {}) is None
    assert ledger.match("submit", {"owner": "forged", "report": "anything"}) is None
    second = ledger.match("check", {"generated": "value"})
    assert second is not None
    ledger = ledger.record_result(
        second,
        session_id=session_id,
        attempt_key=f"session:{ledger.session_id}:turn:1:tool:check",
        result={"structuredContent": {"accepted": True}},
    )
    first = ledger.match("submit", {"owner": "trusted", "report": "invalid"})
    assert first is not None
    ledger = ledger.record_result(
        first,
        session_id=session_id,
        attempt_key=f"session:{ledger.session_id}:turn:2:tool:submit",
        result={"structuredContent": {"accepted": False, "errors": ["correct report"]}},
    )
    assert not ledger.is_complete
    assert ledger.entries[0].error_code == "RESULT_NOT_ACCEPTED"
    assert ledger.match("submit", {"owner": "trusted", "report": "corrected"}) == first
    result = {"structuredContent": {"accepted": True, "receipt": "actual"}}
    ledger = ledger.record_result(
        first,
        session_id=session_id,
        attempt_key=f"session:{ledger.session_id}:turn:3:tool:submit",
        result=result,
    )
    assert ledger.is_complete
    assert ledger.entries[0].attempt_count == 2
    assert ledger.entries[0].result_digest is not None
    restored = ToolPlanLedger.model_validate_json(ledger.model_dump_json(by_alias=True))
    assert restored == ledger
    assert (
        restored.record_result(
            first,
            session_id=session_id,
            attempt_key=f"session:{ledger.session_id}:turn:3:tool:submit",
            result=result,
        )
        == ledger
    )
    assert ledger.match("submit", {"owner": "trusted", "report": "extra"}) is None


@pytest.mark.parametrize(
    "result",
    [
        {},
        {"accepted": True},
        {"structuredContent": {}},
        {"structuredContent": {"accepted": False}},
        {"structuredContent": {"accepted": "true"}},
        {"structuredContent": {"accepted": 1}},
        {"structuredContent": None},
        {"structuredContent": '{"accepted":true}'},
        {"isError": True, "structuredContent": {"accepted": True}},
    ],
)
def test_unordered_gate_never_accepts_missing_malformed_or_error_results(
    result: dict[str, Any],
) -> None:
    ledger = _unordered_ledger()
    session_id = ledger.session_id
    assert session_id is not None
    first = ledger.occurrences[0]
    rejected = ledger.record_result(
        first,
        session_id=session_id,
        attempt_key=f"session:{ledger.session_id}:turn:1:tool:submit",
        result=result,
    )
    assert not rejected.is_complete
    assert rejected.entries[0].state.value == "FAILED"


def test_unordered_ledger_rejects_cross_session_and_claim_only_success() -> None:
    ledger = _unordered_ledger()
    session_id = ledger.session_id
    assert session_id is not None
    first = ledger.occurrences[0]
    result = {"structuredContent": {"accepted": True}}
    with pytest.raises(ToolPlanLedgerError, match="actual record_result"):
        ledger.record_success(first, attempt_key="model-claimed-receipt")
    with pytest.raises(ToolPlanLedgerError, match="this session"):
        ledger.record_result(first, session_id=uuid4(), attempt_key="external", result=result)
    with pytest.raises(ToolPlanLedgerError, match="tool loop"):
        ledger.record_result(
            first,
            session_id=session_id,
            attempt_key="workflow:mcp",
            result=result,
        )
    accepted = ledger.record_result(
        first,
        session_id=session_id,
        attempt_key=f"session:{ledger.session_id}:turn:1:tool:submit",
        result=result,
    )
    copied = accepted.model_dump(mode="json", by_alias=True)
    copied["sessionId"] = str(uuid4())
    with pytest.raises(ValidationError, match="tool loop"):
        ToolPlanLedger.model_validate(copied)
    assert not _unordered_ledger().is_complete


@pytest.mark.parametrize(
    "schema",
    [
        {},
        {"type": "invalid"},
        {"properties": {"accepted": {"const": True}}},
        {"$ref": "https://example.invalid/condition"},
        {"allOf": [{"$dynamicRef": "#external"}]},
    ],
)
def test_success_conditions_reject_invalid_permissive_and_reference_schemas(
    schema: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError, match="successSchema"):
        RequiredToolStep(stepId="x", toolName="x", successSchema=schema)


def test_unordered_configuration_is_explicit_and_unambiguous() -> None:
    step = RequiredToolStep(stepId="one", toolName="x", successSchema=ACCEPTED_SCHEMA)
    with pytest.raises(ValidationError, match="UNORDERED"):
        RequiredToolPlan(steps=(step,))
    with pytest.raises(ValidationError, match="successSchema"):
        RequiredToolPlan(mode="UNORDERED", steps=(RequiredToolStep(stepId="x", toolName="x"),))
    with pytest.raises(ValidationError, match="unique toolName"):
        RequiredToolPlan(mode="UNORDERED", steps=(step, step.model_copy(update={"step_id": "two"})))
    with pytest.raises(ValidationError, match="forEach"):
        RequiredToolPlan(mode="UNORDERED", steps=(step.model_copy(update={"for_each": "/items"}),))


def test_ordered_digest_remains_compatible_with_pre_extension_checkpoints() -> None:
    from amesh.domain.resources import canonical_hash

    document = {
        "schemaVersion": "amesh.agent-tool-plan/v1",
        "maxOccurrences": 1000,
        "steps": [
            {
                "stepId": "x",
                "toolName": "x",
                "arguments": {},
                "argumentBindings": {},
                "itemArgumentBindings": {},
                "maxOccurrences": 1000,
            }
        ],
    }
    plan = RequiredToolPlan.model_validate(document)
    assert plan.digest == "sha256:" + canonical_hash(document)
    expanded = plan.expand({})
    old_expanded = expanded.model_dump(mode="json", by_alias=True, exclude_none=True)
    old_expanded.pop("mode")
    assert expanded.digest == "sha256:" + canonical_hash(old_expanded)
    ledger = ToolPlanLedger.from_expanded(expanded)
    old_ledger = ledger.model_dump(mode="json", by_alias=True, exclude_none=True)
    old_ledger.pop("mode")
    assert ledger.digest == "sha256:" + canonical_hash(old_ledger)
    assert ToolPlanLedger.model_validate(old_ledger) == ledger
