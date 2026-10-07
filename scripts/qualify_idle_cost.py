"""Record the idle cost of each AMESH role loop over a large history (#136).

Optionally seeds settled history into a disposable qualification database, then times each role's
idle cycle in-process. A role whose cycle (its own CPU plus the PostgreSQL time it waits on) stays
under ``--budget-ms`` per ``--cycle-seconds`` cannot exceed that duty cycle of one core when idle.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres import (
    PostgresDurableTransport,
    PostgresExecutionRepository,
    PostgresSchedulerRepository,
    PostgresSearchRepository,
    PostgresTenantRepository,
    PostgresTriggerRuntimeRepository,
    PostgresWorkerRepository,
)
from amesh.config import Settings
from amesh.database import create_database_engine
from amesh.dsl import FlowDefinition
from amesh.entrypoints.worker import (
    process_trigger_occurrences_once,
    recover_once,
    schedule_once,
)
from amesh.ports import WorkerLossPolicy

SEED_TAG = "idle-seed"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Record AMESH idle role-loop cost")
    result.add_argument("--seed", action="store_true", help="seed history first (disposable DB)")
    result.add_argument("--executions", type=int, default=100_000)
    # Each audit row passes the hash-chain trigger (~1ms), so audit history dominates seeding time.
    result.add_argument("--audit-events", type=int, default=200_000)
    result.add_argument("--settled-occurrences", type=int, default=500_000)
    result.add_argument("--flows", type=int, default=1_000)
    result.add_argument("--cycles", type=int, default=20)
    result.add_argument("--cycle-seconds", type=float, default=1.0)
    result.add_argument("--budget-ms", type=float, default=100.0)
    result.add_argument("--output", type=Path)
    return result


async def _clone(
    connection: AsyncConnection,
    table: str,
    *,
    template: str,
    source: str,
    overrides: dict[str, str | None],
    parameters: dict[str, object],
) -> None:
    """Copy one template row once per ``source`` row; ``None`` overrides use the column default."""

    columns = [
        column
        for column in (
            await connection.scalars(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = :table "
                    "AND is_generated = 'NEVER' ORDER BY ordinal_position"
                ),
                {"table": table},
            )
        ).all()
        if overrides.get(column, "") is not None
    ]
    values = ", ".join(overrides.get(column) or f"template.{column}" for column in columns)
    await connection.execute(
        text(
            f"INSERT INTO {table} ({', '.join(columns)}) "
            f"SELECT {values} FROM {table} AS template CROSS JOIN {source} "
            f"WHERE {template}"
        ),
        parameters,
    )


async def seed(
    engine: AsyncEngine, arguments: argparse.Namespace
) -> tuple[dict[str, object], FlowDefinition]:
    started = perf_counter()
    repository = PostgresExecutionRepository(engine)
    namespace = f"qualification.idle.{uuid4().hex[:8]}"
    cron = FlowDefinition.model_validate(
        {
            "id": "hourly",
            "namespace": namespace,
            "triggers": [{"id": "hourly", "type": "core.cron", "cron": "0 * * * *"}],
            "tasks": [{"id": "work", "type": "core.return", "value": "ok"}],
        }
    )
    await repository.apply_flow(cron, tenant_id="default")
    for index in range(arguments.flows - 1):
        await repository.apply_flow(
            cron.model_copy(update={"id": f"flow_{index}", "triggers": []}),
            tenant_id="default",
        )
    template = await repository.create_execution(cron, tenant_id="default", inputs={})
    scheduler = PostgresSchedulerRepository(engine)
    trigger_runtime = PostgresTriggerRuntimeRepository(engine)
    await schedule_once(
        repository,
        scheduler,
        tenant_ids=("default",),
        scheduler_id=uuid4(),
        now=datetime(2026, 1, 1, 12, 0, 5, tzinfo=UTC),
        trigger_runtime=trigger_runtime,
    )
    settled = "now() - interval '1 day'"
    async with engine.begin() as connection:
        await _clone(
            connection,
            "executions",
            template="template.id = :template",
            source="generate_series(1, :count) AS seed(n)",
            overrides={
                "id": "gen_random_uuid()",
                "idempotency_key": f"'{SEED_TAG}-' || seed.n",
                "state": "CASE WHEN seed.n % 2 = 0 THEN 'SUCCESS' ELSE 'FAILED' END",
                "created_at": settled,
                "updated_at": settled,
            },
            parameters={"template": template.execution_id, "count": arguments.executions},
        )
        await _clone(
            connection,
            "task_runs",
            template="template.execution_id = :template",
            source=(
                f"(SELECT id FROM executions WHERE idempotency_key LIKE '{SEED_TAG}-%') AS seed"
            ),
            overrides={
                "id": "gen_random_uuid()",
                "execution_id": "seed.id",
                "state": "'SUCCESS'",
                "created_at": settled,
                "updated_at": settled,
            },
            parameters={"template": template.execution_id},
        )
        await _clone(
            connection,
            "audit_events",
            template=(
                "template.id = (SELECT min(id) FROM audit_events WHERE tenant_id = "
                "(SELECT id FROM tenants WHERE slug = 'default'))"
            ),
            source="generate_series(1, :count) AS seed(n)",
            overrides={"id": None, "event_id": "gen_random_uuid()", "occurred_at": settled},
            parameters={"count": arguments.audit_events},
        )
        await _clone(
            connection,
            "trigger_occurrences",
            template="template.namespace_name = :namespace",
            source="generate_series(1, :count) AS seed(n)",
            overrides={
                "occurrence_id": "gen_random_uuid()",
                "occurrence_key": f"'{SEED_TAG}-' || seed.n",
                "state": "'SUCCEEDED'",
                "created_at": settled,
                "updated_at": settled,
            },
            parameters={"namespace": namespace, "count": arguments.settled_occurrences},
        )
        await connection.execute(text("ANALYZE"))
    # Fire the missed schedule and settle its occurrences so timed scheduler cycles find no work.
    await schedule_once(
        repository,
        scheduler,
        tenant_ids=("default",),
        scheduler_id=uuid4(),
        trigger_runtime=trigger_runtime,
    )
    await process_trigger_occurrences_once(
        repository, trigger_runtime, tenant_ids=("default",), worker_id=uuid4()
    )
    return {"seedSeconds": round(perf_counter() - started, 1)}, cron


async def _time(cycle: Callable[[], Awaitable[object]], cycles: int) -> list[float]:
    durations = []
    for _ in range(cycles):
        started = perf_counter()
        await cycle()
        durations.append((perf_counter() - started) * 1000)
    return durations


async def measure(settings: Settings, arguments: argparse.Namespace) -> dict[str, object]:
    engine = create_database_engine(settings)
    try:
        report: dict[str, object] = {}
        recent_flow = None
        if arguments.seed:
            report, recent_flow = await seed(engine, arguments)
        tenant_ids = await PostgresTenantRepository(engine).list_active_for_worker_group(
            settings.worker_group
        )
        executions = PostgresExecutionRepository(engine)
        scheduler = PostgresSchedulerRepository(engine)
        trigger_runtime = PostgresTriggerRuntimeRepository(engine)
        workers = PostgresWorkerRepository(engine)
        transport = PostgresDurableTransport(engine)
        search = PostgresSearchRepository(engine)
        scheduler_id = uuid4()

        async def executor_cycle() -> None:
            await recover_once(executions, settings, tenant_ids=tenant_ids)

        async def scheduler_cycle() -> None:
            await schedule_once(
                executions,
                scheduler,
                tenant_ids=tenant_ids,
                scheduler_id=scheduler_id,
                trigger_runtime=trigger_runtime,
            )
            await process_trigger_occurrences_once(
                executions, trigger_runtime, tenant_ids=tenant_ids, worker_id=scheduler_id
            )

        async def worker_cycle() -> None:
            for tenant_id in tenant_ids:
                await workers.recover_expired_claims(
                    tenant_id=tenant_id, policy=WorkerLossPolicy.REQUEUE
                )

        async def indexer_cycle() -> None:
            for tenant_id in tenant_ids:
                await transport.publish_outbox(tenant_id=tenant_id, limit=500)
                await search.project_once(tenant_id=tenant_id, limit=5_000)

        # Converge first so the timed indexer cycles measure the idle path, and record the
        # periodic full pass separately: it runs at most once per full-pass interval.
        converge_started = perf_counter()
        for tenant_id in tenant_ids:
            while await search.project_once(tenant_id=tenant_id, limit=5_000):
                pass
        converge_seconds = perf_counter() - converge_started
        if recent_flow is not None:
            # One fresh, projected run keeps the incremental window non-empty, as on a lightly used
            # deployment; a recent change must not make idle cycles join the whole history.
            await executions.create_execution(recent_flow, tenant_id="default", inputs={})
            while await search.project_once(tenant_id="default", limit=5_000):
                pass
        every_cycle = PostgresSearchRepository(engine, full_pass_interval=timedelta(0))

        async def full_pass_cycle() -> None:
            for tenant_id in tenant_ids:
                await every_cycle.project_once(tenant_id=tenant_id, limit=5_000)

        full_pass = await _time(full_pass_cycle, 1)
        cycle_budget_ms = arguments.cycle_seconds * 1000
        roles: dict[str, object] = {}
        passed = True
        for role, cycle in (
            ("executor", executor_cycle),
            ("scheduler", scheduler_cycle),
            ("worker", worker_cycle),
            ("indexer", indexer_cycle),
        ):
            durations = sorted(await _time(cycle, arguments.cycles))
            p95 = durations[max(0, round(len(durations) * 0.95) - 1)]
            within = p95 <= arguments.budget_ms
            passed &= within
            roles[role] = {
                "p50Ms": round(statistics.median(durations), 1),
                "p95Ms": round(p95, 1),
                "dutyPercentAtP95": round(p95 / cycle_budget_ms * 100, 1),
                "withinBudget": within,
            }
        async with engine.connect() as connection:
            sizes = {
                table: int(await connection.scalar(text(f"SELECT count(*) FROM {table}")) or 0)
                for table in ("executions", "task_runs", "audit_events", "trigger_occurrences")
            }
        return {
            **report,
            "measuredAt": datetime.now(UTC).isoformat(),
            "tenants": list(tenant_ids),
            "rows": sizes,
            "cycleSeconds": arguments.cycle_seconds,
            "budgetMs": arguments.budget_ms,
            "indexerConvergeSeconds": round(converge_seconds, 1),
            "indexerFullPassMs": round(full_pass[0], 1),
            "roles": roles,
            "passed": passed,
        }
    finally:
        await engine.dispose()


def main() -> int:
    arguments = parser().parse_args()
    report = asyncio.run(measure(Settings(), arguments))
    encoded = json.dumps(report, indent=2, default=str, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
