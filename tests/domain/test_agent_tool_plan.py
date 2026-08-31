from __future__ import annotations

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
    ledger = ledger.record_success(first, attempt_key="attempt-1")
    assert ledger.match("second", {"value": 2}) == expanded.occurrences[1]


def test_ledger_failure_is_retryable_and_success_is_restart_safe_and_monotonic() -> None:
    expanded = _plan(
        RequiredToolStep(stepId="lookup", toolName="lookup", arguments={"symbol": "JPM"}),
        RequiredToolStep(stepId="filing", toolName="filing", arguments={"symbol": "JPM"}),
    ).expand({})
    ledger = ToolPlanLedger.from_expanded(expanded)
    occurrence = ledger.match("lookup", {"symbol": "JPM"})
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
