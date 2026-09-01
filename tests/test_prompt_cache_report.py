from datetime import UTC, datetime

import pytest
from scripts.analyze_prompt_cache import (
    QUERY,
    CacheObservation,
    aggregate_observations,
    observation_from_row,
    parse_bound,
    render_markdown,
    validate_filters,
)


def _observation(**overrides: object) -> CacheObservation:
    values: dict[str, object] = {
        "started_at": datetime(2026, 8, 30, 12, tzinfo=UTC),
        "namespace": "research",
        "provider": "openrouter",
        "model": "openai/gpt-5.6-luna",
        "adapter": "openai-compatible",
        "harness_adapter": "pi-agent-core",
        "route": "primary",
        "turn": 1,
        "attempt": 1,
        "retry_max_attempts": 2,
        "continuation_present": False,
        "envelope_digest": "sha256:" + "a" * 64,
        "compacted": False,
        "invocation_state": "success",
        "cache_state": "reported",
        "input_tokens": 100,
        "read_tokens": 40,
        "write_tokens": 20,
        "output_tokens": 30,
        "legacy_cost_usd": 0.1,
        "normalized_cost_usd": 0.2,
        "normalized_cost_state": "billed",
        "cache_effect_usd": None,
    }
    values.update(overrides)
    return CacheObservation(**values)  # type: ignore[arg-type]


def test_aggregate_uses_reported_cache_as_hit_rate_denominator() -> None:
    report = aggregate_observations(
        (
            _observation(),
            _observation(read_tokens=0, write_tokens=20),
            _observation(read_tokens=0, write_tokens=0),
            _observation(invocation_state="failure", cache_state="unavailable"),
        )
    )

    summary = report["summary"]
    assert summary["model_calls"] == 4
    assert summary["success"] == 3
    assert summary["failure"] == 1
    assert summary["cache_reported"] == 3
    assert summary["cache_unavailable"] == 0
    assert summary["read_positive"] == 1
    assert summary["reported_zero"] == 2
    assert summary["write_positive"] == 2
    assert summary["read_write"] == 1
    assert summary["read_only"] == 0
    assert summary["write_only"] == 1
    assert summary["both_zero"] == 1
    assert summary["cache_unclassifiable"] == 1
    assert summary["cache_coverage"] == pytest.approx(1.0)
    assert summary["all_success_read_positive_rate"] == pytest.approx(1 / 3)
    assert summary["request_hit_rate"] == pytest.approx(1 / 3)
    assert summary["token_weighted_reuse"] == pytest.approx(40 / 300)
    assert summary["output_tokens"] == 90
    assert summary["legacy_cost_evidence"] == 3
    assert summary["normalized_cost_billed_evidence"] == 3
    assert summary["normalized_billed_cost_usd"] == pytest.approx(0.6)
    assert summary["cache_effect_evidence"] == 0
    assert summary["cache_effect_usd"] is None
    assert summary["cache_savings_usd"] is None


def test_cost_effect_is_summed_only_when_evidence_is_present() -> None:
    report = aggregate_observations(
        (
            _observation(cache_effect_usd=0.012345678901234),
            _observation(cache_effect_usd=None, normalized_cost_state="unavailable"),
        )
    )
    summary = report["summary"]
    assert summary["cache_effect_evidence"] == 1
    assert summary["cache_effect_usd"] == pytest.approx(0.012345678901)
    assert summary["cache_savings_usd"] == pytest.approx(0.012345678901)
    assert summary["normalized_cost_billed_evidence"] == 1
    assert summary["normalized_cost_states"] == {"billed": 1, "unavailable": 1}


def test_empty_evidence_is_explicitly_unavailable() -> None:
    summary = aggregate_observations(())["summary"]
    assert summary["model_calls"] == 0
    assert summary["cache_reported"] == 0
    assert summary["cache_unavailable"] == 0
    assert summary["cache_unclassifiable"] == 0
    assert summary["cache_coverage"] is None
    assert summary["request_hit_rate"] is None
    assert summary["token_weighted_reuse"] is None
    assert summary["cache_savings_usd"] is None


def test_observation_sanitizes_turn_and_dimensions() -> None:
    observation = observation_from_row(
        {
            "started_at": datetime(2026, 8, 30, 12),
            "namespace": "  research\nsecret-payload  ",
            "provider": "provider",
            "model": "model",
            "turn": "session:private-id:turn:12:route:primary",
            "adapter": "openai-compatible",
            "harness_adapter": "pi-agent-core",
            "route": "primary",
            "attempt": "2",
            "retry_max_attempts": "3",
            "continuation_present": True,
            "envelope_digest": "sha256:" + "b" * 64,
            "compacted": "true",
            "invocation_state": "SUCCEEDED",
            "cache_state": "reported",
            "input_tokens": "100",
            "read_tokens": "0",
            "write_tokens": "10",
        }
    )
    assert observation.turn == 12
    assert observation.namespace == "research\nsecret-payload"
    assert observation.invocation_state == "success"
    assert observation.compacted is True
    assert observation.envelope_digest == "sha256:" + "b" * 64
    assert observation.retry_max_attempts == 3


def test_report_groups_by_required_dimensions_and_renders_no_payloads() -> None:
    report = aggregate_observations((_observation(), _observation(compacted=True, turn=2)))
    assert len(report["groups"]) == 2
    assert report["groups"][0]["adapter"] == "openai-compatible"
    assert report["groups"][0]["harness_adapter"] == "pi-agent-core"
    assert report["groups"][0]["route"] == "primary"
    assert report["groups"][0]["attempt"] == 1
    assert report["groups"][0]["retry_max_attempts"] == 2
    assert report["groups"][0]["continuation_present"] is False
    markdown = render_markdown(report)
    assert "research" in markdown
    assert "openai/gpt-5.6-luna" in markdown
    assert "private-id" not in markdown
    assert "secret-payload" not in markdown
    assert "request_metadata" not in markdown
    assert "sha256:" + "a" * 64 in markdown


def test_bounds_require_timezone_and_valid_tenant() -> None:
    start = parse_bound("2026-08-01T00:00:00Z", name="from")
    end = parse_bound("2026-08-02T00:00:00+00:00", name="to")
    assert validate_filters(start, end, "00000000-0000-0000-0000-000000000001", "research")[2:4] == (
        "00000000-0000-0000-0000-000000000001",
        "research",
    )
    with pytest.raises(ValueError, match="timezone"):
        parse_bound("2026-08-01T00:00:00", name="from")
    with pytest.raises(ValueError, match="earlier"):
        validate_filters(end, start, None, None)
    with pytest.raises(ValueError, match="UUID"):
        validate_filters(start, end, "tenant-name", None)
    assert validate_filters(start, end, None, None, "provider", "model", "harness", "primary", 2)[4:] == (
        "provider",
        "model",
        "harness",
        "primary",
        2,
    )


def test_query_is_model_invocation_only_and_does_not_select_payloads() -> None:
    assert "FROM agent_invocations AS i" in QUERY
    assert "i.kind = 'MODEL'" in QUERY
    assert "task_cache" not in QUERY
    assert "replay" not in QUERY.lower()
    assert "i.request_metadata" in QUERY
    assert "i.result," not in QUERY
    assert "cache_effect_usd" in QUERY
    assert "envelope_digest" in QUERY
