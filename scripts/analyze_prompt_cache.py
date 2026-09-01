"""Render a privacy-safe, historical prompt-cache audit.

The report deliberately treats ``agent_invocations`` as the model-call
denominator.  Session events are only used for the optional, non-sensitive
compaction dimension.  Task-result cache and replay data are not queried.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

TURN_PATTERN = re.compile(r":turn:(\d+)(?::|$)")
MAX_DIMENSION_LENGTH = 200
MAX_WINDOW = timedelta(days=366)


@dataclass(frozen=True)
class CacheObservation:
    """A sanitized model invocation observation; no identifiers or payloads."""

    started_at: datetime
    namespace: str | None
    provider: str | None
    model: str | None
    adapter: str | None
    harness_adapter: str | None
    route: str | None
    turn: int | None
    attempt: int | None
    retry_max_attempts: int | None
    continuation_present: bool
    envelope_digest: str | None
    compacted: bool | None
    invocation_state: str
    cache_state: str
    input_tokens: int | None
    read_tokens: int | None
    write_tokens: int | None
    output_tokens: int | None
    legacy_cost_usd: float | None
    normalized_cost_usd: float | None
    normalized_cost_state: str | None
    cache_effect_usd: float | None


@dataclass
class Aggregate:
    model_calls: int = 0
    success: int = 0
    failure: int = 0
    other: int = 0
    cache_unclassifiable: int = 0
    cache_reported: int = 0
    cache_unavailable: int = 0
    read_positive: int = 0
    reported_zero: int = 0
    write_positive: int = 0
    input_tokens: int = 0
    read_tokens: int = 0
    write_tokens: int = 0
    output_tokens: int = 0
    legacy_cost_usd: float = 0.0
    legacy_cost_evidence: int = 0
    normalized_billed_cost_usd: float = 0.0
    normalized_cost_billed_evidence: int = 0
    normalized_cost_states: dict[str, int] | None = None
    cache_effect_usd: float = 0.0
    cache_effect_evidence: int = 0
    write_only: int = 0
    read_only: int = 0
    read_write: int = 0
    both_zero: int = 0

    def add(self, observation: CacheObservation) -> None:
        self.model_calls += 1
        if observation.invocation_state == "success":
            self.success += 1
        elif observation.invocation_state == "failure":
            self.failure += 1
            self.cache_unclassifiable += 1
            return
        else:
            self.other += 1
            self.cache_unclassifiable += 1
            return

        if observation.output_tokens is not None:
            self.output_tokens += observation.output_tokens
        if observation.legacy_cost_usd is not None:
            self.legacy_cost_usd += observation.legacy_cost_usd
            self.legacy_cost_evidence += 1
        if observation.normalized_cost_state:
            if self.normalized_cost_states is None:
                self.normalized_cost_states = {}
            state = observation.normalized_cost_state
            self.normalized_cost_states[state] = self.normalized_cost_states.get(state, 0) + 1
            if state == "billed" and observation.normalized_cost_usd is not None:
                self.normalized_billed_cost_usd += observation.normalized_cost_usd
                self.normalized_cost_billed_evidence += 1
        if observation.cache_effect_usd is not None:
            self.cache_effect_usd += observation.cache_effect_usd
            self.cache_effect_evidence += 1

        if observation.cache_state != "reported":
            self.cache_unavailable += 1
            return

        self.cache_reported += 1
        read_tokens = observation.read_tokens or 0
        write_tokens = observation.write_tokens or 0
        has_read = read_tokens > 0
        has_write = write_tokens > 0
        if has_read:
            self.read_positive += 1
        else:
            self.reported_zero += 1
        if has_write:
            self.write_positive += 1
        if has_read and has_write:
            self.read_write += 1
        elif has_read:
            self.read_only += 1
        elif has_write:
            self.write_only += 1
        else:
            self.both_zero += 1
        if observation.input_tokens is not None and observation.input_tokens > 0:
            self.input_tokens += observation.input_tokens
        self.read_tokens += max(read_tokens, 0)
        self.write_tokens += max(write_tokens, 0)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for field in ("legacy_cost_usd", "normalized_billed_cost_usd"):
            result[field] = round(result[field], 12)
        result["request_hit_rate"] = (
            self.read_positive / self.cache_reported if self.cache_reported else None
        )
        result["request_hit_rate_denominator"] = "cache_reported"
        result["cache_coverage"] = self.cache_reported / self.success if self.success else None
        result["all_success_read_positive_rate"] = self.read_positive / self.success if self.success else None
        result["token_weighted_reuse"] = (
            self.read_tokens / self.input_tokens if self.input_tokens else None
        )
        cache_effect = round(self.cache_effect_usd, 12) if self.cache_effect_evidence else None
        result["cache_effect_usd"] = cache_effect
        result["cache_savings_usd"] = cache_effect
        if self.normalized_cost_states is None:
            result["normalized_cost_states"] = {}
        return result


@dataclass(frozen=True)
class _GroupKey:
    day: date
    namespace: str | None
    provider: str | None
    model: str | None
    adapter: str | None
    harness_adapter: str | None
    route: str | None
    turn: int | None
    attempt: int | None
    retry_max_attempts: int | None
    continuation_present: bool
    envelope_digest: str | None
    compacted: bool | None

    def label(self) -> str:
        compacted = "unknown" if self.compacted is None else str(self.compacted).lower()
        return " / ".join(
            (
                self.day.isoformat(),
                self.namespace or "(none)",
                self.provider or "(none)",
                self.model or "(none)",
                self.adapter or "(none)",
                self.harness_adapter or "(none)",
                self.route or "(none)",
                str(self.turn) if self.turn is not None else "(none)",
                str(self.attempt) if self.attempt is not None else "(none)",
                str(self.retry_max_attempts) if self.retry_max_attempts is not None else "(none)",
                str(self.continuation_present).lower(),
                self.envelope_digest or "(none)",
                compacted,
            )
        )


def _dimension(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    return value[:MAX_DIMENSION_LENGTH]


def _integer(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return float(parsed) if parsed.is_finite() else None


def _digest(value: Any) -> str | None:
    value = _dimension(value)
    return value if value and re.fullmatch(r"sha256:[0-9a-f]{64}", value) else None


def _boolean(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


def _turn(value: Any) -> int | None:
    match = TURN_PATTERN.search(str(value or ""))
    return int(match.group(1)) if match else None


def observation_from_row(row: Mapping[str, Any]) -> CacheObservation:
    """Convert a database row into bounded, renderable audit data."""

    started_at = row.get("started_at")
    if not isinstance(started_at, datetime):
        raise ValueError("started_at must be a datetime")
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    return CacheObservation(
        started_at=started_at.astimezone(UTC),
        namespace=_dimension(row.get("namespace")),
        provider=_dimension(row.get("provider")),
        model=_dimension(row.get("model")),
        adapter=_dimension(row.get("adapter")),
        harness_adapter=_dimension(row.get("harness_adapter")),
        route=_dimension(row.get("route")),
        turn=_turn(row.get("turn")),
        attempt=_integer(row.get("attempt")),
        retry_max_attempts=_integer(row.get("retry_max_attempts")),
        continuation_present=bool(row.get("continuation_present")),
        envelope_digest=_digest(row.get("envelope_digest")),
        compacted=_boolean(row.get("compacted")),
        invocation_state={
            "SUCCEEDED": "success",
            "FAILED": "failure",
        }.get(str(row.get("invocation_state") or "").upper(), "other"),
        cache_state=("reported" if str(row.get("cache_state") or "").lower() == "reported" else "unavailable"),
        input_tokens=_integer(row.get("input_tokens")),
        read_tokens=_integer(row.get("read_tokens")),
        write_tokens=_integer(row.get("write_tokens")),
        output_tokens=_integer(row.get("output_tokens")),
        legacy_cost_usd=_number(row.get("legacy_cost_usd")),
        normalized_cost_usd=_number(row.get("normalized_cost_usd")),
        normalized_cost_state=_dimension(row.get("normalized_cost_state")),
        cache_effect_usd=_number(row.get("cache_effect_usd")),
    )


def aggregate_observations(observations: Iterable[CacheObservation]) -> dict[str, Any]:
    """Aggregate observations into a stable summary and required dimensions."""

    summary = Aggregate()
    groups: dict[_GroupKey, Aggregate] = defaultdict(Aggregate)
    observations = list(observations)
    for observation in observations:
        summary.add(observation)
        key = _GroupKey(
            day=observation.started_at.astimezone(UTC).date(),
            namespace=observation.namespace,
            provider=observation.provider,
            model=observation.model,
            adapter=observation.adapter,
            harness_adapter=observation.harness_adapter,
            route=observation.route,
            turn=observation.turn,
            attempt=observation.attempt,
            retry_max_attempts=observation.retry_max_attempts,
            continuation_present=observation.continuation_present,
            envelope_digest=observation.envelope_digest,
            compacted=observation.compacted,
        )
        groups[key].add(observation)

    return {
        "summary": summary.to_dict(),
        "groups": [
            {
                "day": key.day.isoformat(),
                "namespace": key.namespace,
                "provider": key.provider,
                "model": key.model,
                "adapter": key.adapter,
                "harness_adapter": key.harness_adapter,
                "route": key.route,
                "turn": key.turn,
                "attempt": key.attempt,
                "retry_max_attempts": key.retry_max_attempts,
                "continuation_present": key.continuation_present,
                "envelope_digest": key.envelope_digest,
                "compacted": key.compacted,
                **aggregate.to_dict(),
            }
            for key, aggregate in sorted(groups.items(), key=lambda item: item[0].label())
        ],
    }


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render only aggregate values and bounded dimensions, never payloads."""

    summary = report["summary"]
    lines = ["# Prompt-cache audit", "", "## Summary", "", "| Metric | Value |", "| --- | --- |"]
    for name, value in summary.items():
        lines.append(f"| {_markdown_cell(name)} | {_markdown_cell(value)} |")
    lines.extend(
        (
            "",
            "## Groups",
            "",
            "| Day | Namespace | Provider | Model | Adapter | Harness | Route | Turn | Attempt | Retry max | Continuation | Envelope | Compacted | Calls | Reported | Unavailable | Read+write | Read-only | Write-only | Both-zero | Reuse |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        )
    )
    for group in report["groups"]:
        lines.append(
            "| "
            + " | ".join(
                _markdown_cell(group.get(field))
                for field in (
                    "day",
                    "namespace",
                    "provider",
                    "model",
                    "adapter",
                    "harness_adapter",
                    "route",
                    "turn",
                    "attempt",
                    "retry_max_attempts",
                    "continuation_present",
                    "envelope_digest",
                    "compacted",
                    "model_calls",
                    "cache_reported",
                    "cache_unavailable",
                    "read_write",
                    "read_only",
                    "write_only",
                    "both_zero",
                    "token_weighted_reuse",
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def parse_bound(value: str, *, name: str) -> datetime:
    """Parse an ISO-8601 timezone-aware bound."""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed.astimezone(UTC)


def validate_filters(
    start: datetime | None,
    end: datetime | None,
    tenant: str | None,
    namespace: str | None,
    provider: str | None = None,
    model: str | None = None,
    harness: str | None = None,
    route: str | None = None,
    turn: int | None = None,
) -> tuple[
    datetime | None,
    datetime | None,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    str | None,
    int | None,
]:
    if start and end and start >= end:
        raise ValueError("from must be earlier than to")
    if start and end and end - start > MAX_WINDOW:
        raise ValueError("time window must not exceed 366 days")
    tenant_value = None
    if tenant:
        try:
            tenant_value = str(UUID(tenant))
        except ValueError as exc:
            raise ValueError("tenant must be a UUID") from exc
    namespace_value = _dimension(namespace)
    if namespace and namespace_value is None:
        raise ValueError("namespace must not be empty")
    raw_dimensions = (provider, model, harness, route)
    dimensions = tuple(_dimension(value) for value in raw_dimensions)
    if any(raw is not None and value is None for raw, value in zip(raw_dimensions, dimensions, strict=True)):
        raise ValueError("provider, model, harness, and route must not be empty")
    if turn is not None and (isinstance(turn, bool) or turn < 0):
        raise ValueError("turn must be a non-negative integer")
    return (start, end, tenant_value, namespace_value, *dimensions, turn)


QUERY = """
SELECT
    i.started_at,
    i.namespace_name AS namespace,
    i.state AS invocation_state,
    i.request_metadata ->> 'providerId' AS provider,
    COALESCE(i.result ->> 'model', i.request_metadata ->> 'model') AS model,
    i.request_metadata ->> 'adapter' AS adapter,
    COALESCE(context_event.harness_adapter, s.harness_adapter) AS harness_adapter,
    COALESCE(context_event.route_id, substring(i.request_metadata ->> 'invocationKey' FROM ':route:([^:]+)$')) AS route,
    substring(i.request_metadata ->> 'invocationKey' FROM ':turn:([0-9]+)(?::|$)') AS turn,
    i.attempt,
    NULLIF(i.request_metadata -> 'retry' ->> 'maxAttempts', '')::integer AS retry_max_attempts,
    (i.request_metadata ? 'continuation') AS continuation_present,
    s.envelope_digest,
    CASE
        WHEN (i.result -> 'usageNormalized' -> 'contextReceipt' ->> 'compacted') IS NOT NULL
            THEN (i.result -> 'usageNormalized' -> 'contextReceipt' ->> 'compacted')::boolean
        ELSE context_event.compacted
    END AS compacted,
    CASE
        WHEN i.result -> 'usageNormalized' -> 'promptCache' ->> 'state' = 'reported'
            THEN 'reported'
        ELSE 'unavailable'
    END AS cache_state,
    NULLIF(i.result -> 'usageNormalized' ->> 'inputTokens', '')::bigint AS input_tokens,
    NULLIF(i.result -> 'usageNormalized' -> 'promptCache' ->> 'readTokens', '')::bigint AS read_tokens,
    NULLIF(i.result -> 'usageNormalized' -> 'promptCache' ->> 'writeTokens', '')::bigint AS write_tokens,
    NULLIF(i.result -> 'usageNormalized' ->> 'outputTokens', '')::bigint AS output_tokens,
    NULLIF(i.result ->> 'costUsd', '')::double precision AS legacy_cost_usd,
    NULLIF(i.result -> 'costNormalized' ->> 'amountUsd', '')::double precision AS normalized_cost_usd,
    i.result -> 'costNormalized' ->> 'state' AS normalized_cost_state,
    NULLIF(i.result -> 'usageNormalized' -> 'promptCache' ->> 'costEffectUsd', '')::double precision AS cache_effect_usd
FROM agent_invocations AS i
LEFT JOIN agent_sessions AS s
  ON s.tenant_id = i.tenant_id
 AND s.task_run_id = i.task_run_id
 AND s.attempt = i.attempt
LEFT JOIN LATERAL (
    SELECT
        (e.payload -> 'contextReceipt' ->> 'compacted')::boolean AS compacted,
        e.payload -> 'harness' ->> 'adapter' AS harness_adapter,
        e.payload -> 'harness' -> 'metadata' ->> 'routeId' AS route_id
    FROM agent_session_events AS e
    WHERE e.tenant_id = i.tenant_id
      AND e.session_id = s.session_id
      AND e.event_type = 'model.response'
      AND (
          substring(i.request_metadata ->> 'invocationKey' FROM ':turn:([0-9]+)(?::|$)') IS NULL
          OR e.payload ->> 'turn' = substring(i.request_metadata ->> 'invocationKey' FROM ':turn:([0-9]+)(?::|$)')
      )
    ORDER BY e.event_index
    LIMIT 1
) AS context_event ON TRUE
WHERE i.kind = 'MODEL'
  AND (CAST(:from_time AS timestamptz) IS NULL OR i.started_at >= CAST(:from_time AS timestamptz))
  AND (CAST(:to_time AS timestamptz) IS NULL OR i.started_at < CAST(:to_time AS timestamptz))
  AND (CAST(:tenant_id AS uuid) IS NULL OR i.tenant_id = CAST(:tenant_id AS uuid))
  AND (CAST(:namespace AS text) IS NULL OR i.namespace_name = CAST(:namespace AS text))
  AND (CAST(:provider AS text) IS NULL OR i.request_metadata ->> 'providerId' = CAST(:provider AS text))
  AND (CAST(:model AS text) IS NULL OR COALESCE(i.result ->> 'model', i.request_metadata ->> 'model') = CAST(:model AS text))
  AND (CAST(:harness AS text) IS NULL OR COALESCE(context_event.harness_adapter, s.harness_adapter) = CAST(:harness AS text))
  AND (CAST(:route AS text) IS NULL OR COALESCE(context_event.route_id, substring(i.request_metadata ->> 'invocationKey' FROM ':route:([^:]+)$')) = CAST(:route AS text))
  AND (CAST(:turn AS integer) IS NULL OR substring(i.request_metadata ->> 'invocationKey' FROM ':turn:([0-9]+)(?::|$)')::integer = CAST(:turn AS integer))
ORDER BY i.started_at
"""


async def fetch_observations(
    database_url: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    tenant: str | None = None,
    namespace: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    harness: str | None = None,
    route: str | None = None,
    turn: int | None = None,
) -> list[CacheObservation]:
    """Fetch sanitized observations in an explicit read-only transaction."""

    (
        start,
        end,
        tenant,
        namespace,
        provider,
        model,
        harness,
        route,
        turn,
    ) = validate_filters(start, end, tenant, namespace, provider, model, harness, route, turn)
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(text("SET TRANSACTION READ ONLY"))
            result = await connection.execute(
                text(QUERY),
                {
                    "from_time": start,
                    "to_time": end,
                        "tenant_id": tenant,
                        "namespace": namespace,
                        "provider": provider,
                        "model": model,
                        "harness": harness,
                        "route": route,
                        "turn": turn,
                },
            )
            return [observation_from_row(row) for row in result.mappings()]
    finally:
        await engine.dispose()


def _database_url(value: str | None) -> str:
    resolved = value or os.getenv("AMESH_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not resolved:
        raise ValueError("database URL is required via --database-url or AMESH_DATABASE_URL")
    if not resolved.startswith("postgresql+asyncpg://"):
        raise ValueError("database URL must use postgresql+asyncpg")
    return resolved


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="end")
    parser.add_argument("--tenant")
    parser.add_argument("--namespace")
    parser.add_argument("--provider")
    parser.add_argument("--model")
    parser.add_argument("--harness")
    parser.add_argument("--route")
    parser.add_argument("--turn", type=int)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    return parser


async def _run(args: argparse.Namespace) -> str:
    start = parse_bound(args.start, name="from") if args.start else None
    end = parse_bound(args.end, name="to") if args.end else None
    (
        start,
        end,
        tenant,
        namespace,
        provider,
        model,
        harness,
        route,
        turn,
    ) = validate_filters(
        start,
        end,
        args.tenant,
        args.namespace,
        args.provider,
        args.model,
        args.harness,
        args.route,
        args.turn,
    )
    observations = await fetch_observations(
        _database_url(args.database_url),
        start=start,
        end=end,
        tenant=tenant,
        namespace=namespace,
        provider=provider,
        model=model,
        harness=harness,
        route=route,
        turn=turn,
    )
    report = aggregate_observations(observations)
    if args.format == "json":
        return json.dumps(report, indent=2, sort_keys=True) + "\n"
    return render_markdown(report)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        output = asyncio.run(_run(args))
    except (ValueError, OSError) as exc:
        _parser().error(str(exc))
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
