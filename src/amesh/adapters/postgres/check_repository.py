from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.dsl import CheckDefinition, FlowDefinition, compile_flow_tasks
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports.checks import (
    CheckActionRecord,
    CheckActionState,
    CheckComplianceSummary,
    CheckEvaluation,
    CheckEvaluationPoint,
    CheckOutcome,
    CheckPolicySource,
    CheckRepository,
    NamespaceCheckPolicy,
)
from amesh.ports.durable_transport import DurableEnvelope

from .durable_transport import PostgresDurableTransport
from .tenant_context import tenant_transaction


async def store_flow_check_definitions(
    connection: AsyncConnection,
    tenant_id: UUID,
    flow_revision_id: UUID,
    flow: FlowDefinition,
) -> None:
    """Materialize explicit and reusable checks with an immutable flow revision."""

    policy_rows = (
        (
            await connection.execute(
                text(
                    """
                    SELECT policy_id, policy_key, source, task_type, definition
                    FROM namespace_check_policies
                    WHERE tenant_id = :tenant_id
                      AND namespace_name = :namespace
                      AND enabled
                    ORDER BY CASE source WHEN 'PLUGIN_DEFAULT' THEN 0 ELSE 1 END,
                             policy_key
                    """
                ),
                {"tenant_id": tenant_id, "namespace": flow.namespace},
            )
        )
        .mappings()
        .all()
    )
    requested = set(flow.check_policies)
    available = {
        str(row["policy_key"])
        for row in policy_rows
        if str(row["source"]) == CheckPolicySource.NAMESPACE.value
    }
    missing = requested - available
    if missing:
        raise ValueError("unknown namespace check policies: " + ", ".join(sorted(missing)))

    task_types = {node.task.type for node in compile_flow_tasks(flow)}
    merged: dict[str, tuple[CheckDefinition, str, UUID | None]] = {}
    for row in policy_rows:
        source = str(row["source"])
        selected = (
            source == CheckPolicySource.NAMESPACE.value and str(row["policy_key"]) in requested
        ) or (
            source == CheckPolicySource.PLUGIN_DEFAULT.value and str(row["task_type"]) in task_types
        )
        if selected:
            definition = CheckDefinition.model_validate(row["definition"])
            merged[definition.id] = (
                definition,
                source,
                UUID(str(row["policy_id"])),
            )
    for definition in flow.checks:
        merged[definition.id] = (definition, "EXPLICIT", None)

    for definition, source, policy_id in merged.values():
        await connection.execute(
            text(
                """
                INSERT INTO flow_check_definitions (
                    check_definition_id, tenant_id, flow_revision_id,
                    namespace_name, flow_key, flow_revision, check_key,
                    check_type, source, source_policy_id, definition
                ) VALUES (
                    :check_definition_id, :tenant_id, :flow_revision_id,
                    :namespace, :flow_key, :flow_revision, :check_key,
                    :check_type, :source, :source_policy_id, CAST(:definition AS jsonb)
                )
                ON CONFLICT (tenant_id, flow_revision_id, check_key) DO NOTHING
                """
            ),
            {
                "check_definition_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "flow_revision_id": flow_revision_id,
                "namespace": flow.namespace,
                "flow_key": flow.id,
                "flow_revision": flow.revision,
                "check_key": definition.id,
                "check_type": definition.type,
                "source": source,
                "source_policy_id": policy_id,
                "definition": definition.model_dump_json(by_alias=True, exclude_none=True),
            },
        )


async def synchronize_active_flow_checks(
    connection: AsyncConnection,
    tenant_id: UUID,
    flow_id: UUID,
    *,
    active_revision: int,
    flow_disabled: bool,
) -> None:
    """Activate only the selected revision and start its initial freshness windows."""

    rows = (
        (
            await connection.execute(
                text(
                    """
                    UPDATE flow_check_definitions AS definitions
                    SET active = (
                        NOT :flow_disabled
                        AND revisions.revision = :active_revision
                    )
                    FROM flow_revisions AS revisions
                    WHERE definitions.tenant_id = :tenant_id
                      AND definitions.flow_revision_id = revisions.id
                      AND revisions.flow_id = :flow_id
                    RETURNING definitions.check_definition_id,
                              definitions.definition,
                              definitions.active
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "flow_id": flow_id,
                    "active_revision": active_revision,
                    "flow_disabled": flow_disabled,
                },
            )
        )
        .mappings()
        .all()
    )
    now = await _database_time(connection)
    for row in rows:
        definition = CheckDefinition.model_validate(row["definition"])
        if row["active"] and definition.type == "FRESHNESS":
            await _schedule_deadline(
                connection,
                tenant_id,
                UUID(str(row["check_definition_id"])),
                execution_id=None,
                deadline_type="FRESHNESS",
                due_at=now + _threshold(definition),
                subject_key=f"freshness:{active_revision}:{now.isoformat()}",
            )


async def record_execution_check_start(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    flow_revision_id: UUID,
    execution_id: UUID,
    execution_state: str,
    namespace: str,
    flow_id: str,
    flow_revision: int,
    created_at: datetime,
    started_at: datetime | None = None,
    trigger: dict[str, Any],
    labels: dict[str, str],
) -> None:
    rows = await _active_definitions(connection, tenant_id, flow_revision_id)
    policy_depth = _policy_depth(trigger)
    scheduled_for = _parse_datetime(trigger.get("scheduledFor")) or created_at
    start_time = started_at or created_at
    for row in rows:
        definition = CheckDefinition.model_validate(row["definition"])
        definition_id = UUID(str(row["check_definition_id"]))
        subject_key = f"execution:{execution_id}"
        if definition.type == "START_DELAY":
            if execution_state in {"RUNNING", "SUCCESS", "FAILED", "WARNING", "CANCELLED"}:
                delay = max((start_time - scheduled_for).total_seconds(), 0.0)
                passed = delay <= _threshold(definition).total_seconds()
                await _insert_evaluation(
                    connection,
                    tenant_id,
                    row,
                    execution_id=execution_id,
                    evaluation_point=CheckEvaluationPoint.STARTED,
                    subject_key=subject_key,
                    outcome=_outcome(definition, passed),
                    reason=(
                        "execution started within the configured delay"
                        if passed
                        else "execution start delay exceeded the configured threshold"
                    ),
                    evidence={
                        "delaySeconds": delay,
                        "thresholdSeconds": _threshold(definition).total_seconds(),
                        "scheduledFor": scheduled_for.isoformat(),
                        "startedAt": start_time.isoformat(),
                    },
                    labels=labels,
                    policy_depth=policy_depth,
                )
                await connection.execute(
                    text(
                        """
                        UPDATE check_deadlines
                        SET state = 'PROCESSED', processed_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id
                          AND check_definition_id = :check_definition_id
                          AND subject_key = :subject_key
                          AND state = 'PENDING'
                        """
                    ),
                    {
                        "tenant_id": tenant_id,
                        "check_definition_id": definition_id,
                        "subject_key": subject_key,
                    },
                )
            else:
                await _schedule_deadline(
                    connection,
                    tenant_id,
                    definition_id,
                    execution_id=execution_id,
                    deadline_type="START_DELAY",
                    due_at=scheduled_for + _threshold(definition),
                    subject_key=subject_key,
                )
        elif definition.type in {"DURATION", "COMPLETION_WINDOW"}:
            anchor = start_time if definition.type == "DURATION" else scheduled_for
            await _schedule_deadline(
                connection,
                tenant_id,
                definition_id,
                execution_id=execution_id,
                deadline_type=definition.type,
                due_at=anchor + _threshold(definition),
                subject_key=subject_key,
            )


async def evaluate_execution_terminal_checks(
    connection: AsyncConnection,
    tenant_id: UUID,
    *,
    flow_revision_id: UUID,
    execution_id: UUID,
    execution_state: str,
    namespace: str,
    flow_id: str,
    flow_revision: int,
    created_at: datetime,
    terminal_at: datetime,
    inputs: dict[str, Any],
    trigger: dict[str, Any],
    labels: dict[str, str],
) -> None:
    del namespace, flow_id, flow_revision
    rows = await _active_definitions(connection, tenant_id, flow_revision_id)
    outputs = await _execution_outputs(connection, tenant_id, execution_id)
    policy_depth = _policy_depth(trigger)
    scheduled_for = _parse_datetime(trigger.get("scheduledFor")) or created_at
    context = ExpressionContext(
        flow={
            "id": rows[0]["flow_key"] if rows else "",
            "namespace": rows[0]["namespace_name"] if rows else "",
            "revision": int(rows[0]["flow_revision"]) if rows else 0,
        },
        execution={
            "id": str(execution_id),
            "state": execution_state,
            "createdAt": created_at.isoformat(),
            "terminalAt": terminal_at.isoformat(),
        },
        trigger=trigger,
        inputs=inputs,
        outputs=outputs,
        labels=labels,
        namespace={"id": rows[0]["namespace_name"] if rows else ""},
    )
    elapsed = max((terminal_at - created_at).total_seconds(), 0.0)
    for row in rows:
        definition = CheckDefinition.model_validate(row["definition"])
        subject_key = f"execution:{execution_id}"
        if definition.type == "START_DELAY":
            continue
        outcome = CheckOutcome.PASS
        reason = "check passed"
        evidence: dict[str, Any] = {"executionState": execution_state}
        if definition.type == "DURATION":
            threshold = _threshold(definition).total_seconds()
            passed = elapsed <= threshold
            outcome = _outcome(definition, passed)
            reason = (
                "execution duration is within threshold"
                if passed
                else "execution duration exceeded threshold"
            )
            evidence.update(elapsedSeconds=elapsed, thresholdSeconds=threshold)
        elif definition.type == "COMPLETION_WINDOW":
            due_at = scheduled_for + _threshold(definition)
            passed = terminal_at <= due_at
            outcome = _outcome(definition, passed)
            reason = (
                "execution completed within its window"
                if passed
                else "execution missed its completion window"
            )
            evidence.update(dueAt=due_at.isoformat(), terminalAt=terminal_at.isoformat())
        elif definition.type in {"OUTPUT", "EXPRESSION"}:
            try:
                passed = NativeExpressionEngine().evaluate_condition(
                    str(definition.expression), context
                )
                outcome = _outcome(definition, passed)
                reason = "expression evaluated true" if passed else "expression evaluated false"
                evidence.update(expression=definition.expression, result=passed)
            except Exception as exc:
                outcome = CheckOutcome.ERROR
                reason = "expression evaluation failed"
                evidence.update(expression=definition.expression, error=str(exc))
        elif definition.type == "FRESHNESS":
            reason = "flow completed and refreshed its freshness window"
            evidence.update(terminalAt=terminal_at.isoformat())
            await connection.execute(
                text(
                    """
                    UPDATE check_deadlines
                    SET state = 'PROCESSED', processed_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND check_definition_id = :check_definition_id
                      AND state = 'PENDING'
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "check_definition_id": row["check_definition_id"],
                },
            )
            await _schedule_deadline(
                connection,
                tenant_id,
                UUID(str(row["check_definition_id"])),
                execution_id=None,
                deadline_type="FRESHNESS",
                due_at=terminal_at + _threshold(definition),
                subject_key=f"freshness:{terminal_at.isoformat()}",
            )
        await _insert_evaluation(
            connection,
            tenant_id,
            row,
            execution_id=execution_id,
            evaluation_point=(
                CheckEvaluationPoint.FRESHNESS
                if definition.type == "FRESHNESS"
                else CheckEvaluationPoint.TERMINAL
            ),
            subject_key=subject_key,
            outcome=outcome,
            reason=reason,
            evidence=evidence,
            labels=labels,
            policy_depth=policy_depth,
        )
        if definition.type in {"DURATION", "COMPLETION_WINDOW"}:
            await connection.execute(
                text(
                    """
                    UPDATE check_deadlines
                    SET state = 'PROCESSED', processed_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND check_definition_id = :check_definition_id
                      AND subject_key = :subject_key
                      AND state = 'PENDING'
                    """
                ),
                {
                    "tenant_id": tenant_id,
                    "check_definition_id": row["check_definition_id"],
                    "subject_key": subject_key,
                },
            )


class PostgresCheckRepository(CheckRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._transport = PostgresDurableTransport(engine)

    async def upsert_policy(
        self,
        *,
        tenant_id: str,
        namespace: str,
        policy_key: str,
        source: CheckPolicySource,
        definition: CheckDefinition,
        actor_id: str,
        task_type: str | None = None,
        enabled: bool = True,
    ) -> NamespaceCheckPolicy:
        if source is CheckPolicySource.PLUGIN_DEFAULT and not task_type:
            raise ValueError("plugin-default check policies require task_type")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO namespace_check_policies (
                                policy_id, tenant_id, namespace_name, policy_key,
                                source, task_type, definition, enabled,
                                created_by, updated_by
                            ) VALUES (
                                :policy_id, :tenant_id, :namespace, :policy_key,
                                :source, :task_type, CAST(:definition AS jsonb), :enabled,
                                :actor_id, :actor_id
                            )
                            ON CONFLICT (tenant_id, namespace_name, policy_key)
                            DO UPDATE SET
                                source = EXCLUDED.source,
                                task_type = EXCLUDED.task_type,
                                definition = EXCLUDED.definition,
                                enabled = EXCLUDED.enabled,
                                updated_by = EXCLUDED.updated_by,
                                updated_at = clock_timestamp()
                            RETURNING *
                            """
                        ),
                        {
                            "policy_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "policy_key": policy_key,
                            "source": source.value,
                            "task_type": task_type,
                            "definition": definition.model_dump_json(
                                by_alias=True, exclude_none=True
                            ),
                            "enabled": enabled,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await connection.execute(
                text(
                    """
                    INSERT INTO audit_events (
                        event_id, tenant_id, actor_id, action, resource_type,
                        resource_id, outcome, reason, source, evidence, occurred_at
                    ) VALUES (
                        :event_id, :tenant_id, :actor_id, 'check_policy.upsert',
                        'check_policy', :resource_id, 'SUCCESS',
                        'check policy stored', '{"component":"check-api"}'::jsonb,
                        CAST(:evidence AS jsonb), clock_timestamp()
                    )
                    """
                ),
                {
                    "event_id": new_runtime_id(),
                    "tenant_id": tenant_uuid,
                    "actor_id": actor_id,
                    "resource_id": f"{namespace}/{policy_key}",
                    "evidence": json.dumps(
                        {
                            "source": source.value,
                            "taskType": task_type,
                            "checkId": definition.id,
                            "checkType": definition.type,
                            "enabled": enabled,
                        }
                    ),
                },
            )
        return _to_policy(row, tenant_id)

    async def list_policies(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        limit: int = 100,
    ) -> list[NamespaceCheckPolicy]:
        _validate_limit(limit)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM namespace_check_policies
                            WHERE tenant_id = :tenant_id
                              AND (CAST(:namespace AS text) IS NULL OR namespace_name = :namespace)
                            ORDER BY namespace_name, policy_key
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": namespace, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return [_to_policy(row, tenant_id) for row in rows]

    async def list_evaluations(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        execution_id: UUID | None = None,
        outcome: CheckOutcome | None = None,
        limit: int = 100,
    ) -> list[CheckEvaluation]:
        _validate_limit(limit)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT * FROM check_evaluations
                            WHERE tenant_id = :tenant_id
                              AND (CAST(:namespace AS text) IS NULL OR namespace_name = :namespace)
                              AND (CAST(:flow_id AS text) IS NULL OR flow_key = :flow_id)
                              AND (CAST(:execution_id AS uuid) IS NULL OR execution_id = :execution_id)
                              AND (CAST(:outcome AS text) IS NULL OR outcome = :outcome)
                            ORDER BY evaluated_at DESC, evaluation_id DESC
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "execution_id": execution_id,
                            "outcome": outcome.value if outcome else None,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [_to_evaluation(row, tenant_id) for row in rows]

    async def summarize(
        self,
        *,
        tenant_id: str,
        group_by: str,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        limit: int = 100,
    ) -> list[CheckComplianceSummary]:
        _validate_limit(limit)
        label_key: str | None = None
        expressions = {
            "tenant": "'tenant'",
            "namespace": "namespace_name",
            "flow": "namespace_name || '.' || flow_key",
            "day": "to_char(date_trunc('day', evaluated_at), 'YYYY-MM-DD')",
            "week": "to_char(date_trunc('week', evaluated_at), 'IYYY-\"W\"IW')",
            "month": "to_char(date_trunc('month', evaluated_at), 'YYYY-MM')",
        }
        if group_by.startswith("label:"):
            label_key = group_by.partition(":")[2]
            if not label_key:
                raise ValueError("label grouping requires label:<key>")
            group_expression = "COALESCE(labels ->> :label_key, '(unset)')"
        else:
            try:
                group_expression = expressions[group_by]
            except KeyError as exc:
                raise ValueError("unsupported compliance grouping") from exc
        query = text(
            f"""
            SELECT {group_expression} AS group_key,
                   count(*) AS total,
                   count(*) FILTER (WHERE outcome = 'PASS') AS passed,
                   count(*) FILTER (WHERE outcome = 'WARN') AS warned,
                   count(*) FILTER (WHERE outcome = 'FAIL') AS failed,
                   count(*) FILTER (WHERE outcome = 'ERROR') AS errors
            FROM check_evaluations
            WHERE tenant_id = :tenant_id
              AND (CAST(:from_time AS timestamptz) IS NULL OR evaluated_at >= :from_time)
              AND (CAST(:to_time AS timestamptz) IS NULL OR evaluated_at < :to_time)
              AND (CAST(:namespace AS text) IS NULL OR namespace_name = :namespace)
              AND (CAST(:flow_id AS text) IS NULL OR flow_key = :flow_id)
            GROUP BY {group_expression}
            ORDER BY group_key
            LIMIT :limit
            """
        )
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        query,
                        {
                            "tenant_id": tenant_uuid,
                            "from_time": from_time,
                            "to_time": to_time,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "label_key": label_key,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [
            CheckComplianceSummary(
                group_key=str(row["group_key"]),
                total=int(row["total"]),
                passed=int(row["passed"]),
                warned=int(row["warned"]),
                failed=int(row["failed"]),
                errors=int(row["errors"]),
                compliance_rate=(int(row["passed"]) / int(row["total"])),
            )
            for row in rows
        ]

    async def process_due_checks(self, *, tenant_id: str, limit: int = 100) -> int:
        _validate_limit(limit)
        processed = 0
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT deadlines.*, definitions.namespace_name,
                                   definitions.flow_key, definitions.flow_revision,
                                   definitions.check_key, definitions.check_type,
                                   definitions.source, definitions.definition,
                                   executions.state AS execution_state,
                                   executions.labels, executions.trigger_context
                            FROM check_deadlines AS deadlines
                            JOIN flow_check_definitions AS definitions
                              ON definitions.tenant_id = deadlines.tenant_id
                             AND definitions.check_definition_id = deadlines.check_definition_id
                            LEFT JOIN executions
                              ON executions.tenant_id = deadlines.tenant_id
                             AND executions.id = deadlines.execution_id
                            WHERE deadlines.tenant_id = :tenant_id
                              AND deadlines.state = 'PENDING'
                              AND deadlines.due_at <= clock_timestamp()
                              AND definitions.active
                            ORDER BY deadlines.due_at, deadlines.deadline_id
                            FOR UPDATE OF deadlines SKIP LOCKED
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
            now = await _database_time(connection)
            for row in rows:
                await _evaluate_due_deadline(connection, tenant_uuid, row, now)
                await connection.execute(
                    text(
                        """
                        UPDATE check_deadlines
                        SET state = 'PROCESSED', processed_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND deadline_id = :deadline_id
                        """
                    ),
                    {"tenant_id": tenant_uuid, "deadline_id": row["deadline_id"]},
                )
                processed += 1
        return processed

    async def claim_actions(
        self,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
        limit: int = 100,
    ) -> list[CheckActionRecord]:
        _validate_limit(limit)
        lease_seconds = lease_duration.total_seconds()
        if lease_seconds <= 0:
            raise ValueError("check action lease must be positive")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            await connection.execute(
                text(
                    """
                    UPDATE check_action_queue
                    SET state = CASE WHEN attempt >= max_attempts
                                     THEN 'DEAD_LETTERED' ELSE 'RETRY_WAIT' END,
                        owner_id = NULL, lease_expires_at = NULL,
                        available_at = clock_timestamp(),
                        completed_at = CASE WHEN attempt >= max_attempts
                                            THEN clock_timestamp() ELSE NULL END,
                        last_error = 'processing lease expired',
                        updated_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id
                      AND state = 'PROCESSING'
                      AND lease_expires_at <= clock_timestamp()
                    """
                ),
                {"tenant_id": tenant_uuid},
            )
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            WITH candidates AS (
                                SELECT action_id
                                FROM check_action_queue
                                WHERE tenant_id = :tenant_id
                                  AND state IN ('PENDING', 'RETRY_WAIT')
                                  AND available_at <= clock_timestamp()
                                ORDER BY available_at, created_at, action_id
                                FOR UPDATE SKIP LOCKED
                                LIMIT :limit
                            )
                            UPDATE check_action_queue AS actions
                            SET state = 'PROCESSING', owner_id = :owner_id,
                                fencing_token = fencing_token + 1,
                                lease_expires_at = clock_timestamp()
                                    + (:lease_seconds * interval '1 second'),
                                attempt = attempt + 1,
                                updated_at = clock_timestamp()
                            FROM candidates
                            WHERE actions.tenant_id = :tenant_id
                              AND actions.action_id = candidates.action_id
                            RETURNING actions.*
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "owner_id": owner_id,
                            "lease_seconds": lease_seconds,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return [_to_action(row, tenant_id) for row in rows]

    async def publish_notification(self, action: CheckActionRecord, *, tenant_id: str) -> None:
        envelope = DurableEnvelope(
            message_id=action.action_id,
            message_type="amesh.check.notification.v1",
            schema_version=1,
            tenant_id=tenant_id,
            partition_key=f"check:{action.evaluation_id}",
            correlation_id=action.evaluation_id,
            produced_at=action.created_at.astimezone(UTC),
            payload={
                "evaluationId": str(action.evaluation_id),
                "executionId": str(action.execution_id) if action.execution_id else None,
                "channel": action.channel,
                **action.payload,
            },
        )
        await self._transport.enqueue_outbox(
            f"amesh.check.notification.{action.channel}",
            envelope,
            max_attempts=action.max_attempts,
        )

    async def complete_action(
        self,
        action_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        evidence: dict[str, Any],
    ) -> CheckActionRecord:
        return await self._finish_action(
            action_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            fencing_token=fencing_token,
            succeeded=True,
            evidence=evidence,
        )

    async def fail_action(
        self,
        action_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        error: str,
        retry_delay: timedelta,
    ) -> CheckActionRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE check_action_queue
                            SET state = CASE WHEN attempt >= max_attempts
                                             THEN 'DEAD_LETTERED' ELSE 'RETRY_WAIT' END,
                                owner_id = NULL, lease_expires_at = NULL,
                                available_at = clock_timestamp()
                                    + (:retry_seconds * interval '1 second'),
                                completed_at = CASE WHEN attempt >= max_attempts
                                                    THEN clock_timestamp() ELSE NULL END,
                                last_error = :error,
                                updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND action_id = :action_id
                              AND state = 'PROCESSING' AND owner_id = :owner_id
                              AND fencing_token = :fencing_token
                              AND lease_expires_at > clock_timestamp()
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "action_id": action_id,
                            "owner_id": owner_id,
                            "fencing_token": fencing_token,
                            "retry_seconds": max(retry_delay.total_seconds(), 0),
                            "error": error[:4000],
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise RuntimeError("check action claim is stale")
        return _to_action(row, tenant_id)

    async def _finish_action(
        self,
        action_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        succeeded: bool,
        evidence: dict[str, Any],
    ) -> CheckActionRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE check_action_queue
                            SET state = :state, owner_id = NULL, lease_expires_at = NULL,
                                evidence = evidence || CAST(:evidence AS jsonb),
                                completed_at = clock_timestamp(), updated_at = clock_timestamp()
                            WHERE tenant_id = :tenant_id AND action_id = :action_id
                              AND state = 'PROCESSING' AND owner_id = :owner_id
                              AND fencing_token = :fencing_token
                              AND lease_expires_at > clock_timestamp()
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "action_id": action_id,
                            "owner_id": owner_id,
                            "fencing_token": fencing_token,
                            "state": "SUCCEEDED" if succeeded else "DEAD_LETTERED",
                            "evidence": json.dumps(evidence),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise RuntimeError("check action claim is stale")
        return _to_action(row, tenant_id)


async def _active_definitions(
    connection: AsyncConnection, tenant_id: UUID, flow_revision_id: UUID
) -> list[RowMapping]:
    return list(
        (
            await connection.execute(
                text(
                    """
                    SELECT * FROM flow_check_definitions
                    WHERE tenant_id = :tenant_id
                      AND flow_revision_id = :flow_revision_id
                      AND active
                    ORDER BY check_key
                    """
                ),
                {"tenant_id": tenant_id, "flow_revision_id": flow_revision_id},
            )
        )
        .mappings()
        .all()
    )


async def _schedule_deadline(
    connection: AsyncConnection,
    tenant_id: UUID,
    check_definition_id: UUID,
    *,
    execution_id: UUID | None,
    deadline_type: str,
    due_at: datetime,
    subject_key: str,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO check_deadlines (
                deadline_id, tenant_id, check_definition_id, execution_id,
                subject_key, deadline_type, due_at
            ) VALUES (
                :deadline_id, :tenant_id, :check_definition_id, :execution_id,
                :subject_key, :deadline_type, :due_at
            )
            ON CONFLICT (tenant_id, check_definition_id, subject_key) DO NOTHING
            """
        ),
        {
            "deadline_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "check_definition_id": check_definition_id,
            "execution_id": execution_id,
            "subject_key": subject_key,
            "deadline_type": deadline_type,
            "due_at": due_at,
        },
    )


async def _insert_evaluation(
    connection: AsyncConnection,
    tenant_id: UUID,
    definition_row: RowMapping,
    *,
    execution_id: UUID | None,
    evaluation_point: CheckEvaluationPoint,
    subject_key: str,
    outcome: CheckOutcome,
    reason: str,
    evidence: dict[str, Any],
    labels: dict[str, str],
    policy_depth: int,
) -> UUID | None:
    definition = CheckDefinition.model_validate(definition_row["definition"])
    evaluation_id = new_runtime_id()
    inserted = await connection.scalar(
        text(
            """
            INSERT INTO check_evaluations (
                evaluation_id, tenant_id, check_definition_id, execution_id,
                namespace_name, flow_key, flow_revision, check_key, check_type,
                source, evaluation_point, subject_key, outcome, severity,
                reason, evidence, labels
            ) VALUES (
                :evaluation_id, :tenant_id, :check_definition_id, :execution_id,
                :namespace, :flow_key, :flow_revision, :check_key, :check_type,
                :source, :evaluation_point, :subject_key, :outcome, :severity,
                :reason, CAST(:evidence AS jsonb), CAST(:labels AS jsonb)
            )
            ON CONFLICT (tenant_id, check_definition_id, subject_key, evaluation_point)
            DO NOTHING
            RETURNING evaluation_id
            """
        ),
        {
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "check_definition_id": definition_row["check_definition_id"],
            "execution_id": execution_id,
            "namespace": definition_row["namespace_name"],
            "flow_key": definition_row["flow_key"],
            "flow_revision": definition_row["flow_revision"],
            "check_key": definition_row["check_key"],
            "check_type": definition_row["check_type"],
            "source": definition_row["source"],
            "evaluation_point": evaluation_point.value,
            "subject_key": subject_key,
            "outcome": outcome.value,
            "severity": definition.severity,
            "reason": reason,
            "evidence": json.dumps(evidence),
            "labels": json.dumps(labels),
        },
    )
    if inserted is None or outcome is CheckOutcome.PASS:
        return UUID(str(inserted)) if inserted is not None else None
    for index, action in enumerate(definition.actions):
        skipped = policy_depth >= action.max_depth
        payload = {
            "checkId": definition.id,
            "checkType": definition.type,
            "outcome": outcome.value,
            "reason": reason,
            "sourceExecutionId": str(execution_id) if execution_id else None,
            **action.payload,
        }
        await connection.execute(
            text(
                """
                INSERT INTO check_action_queue (
                    action_id, tenant_id, evaluation_id, execution_id,
                    action_index, action_type, state, target_namespace,
                    target_flow_key, channel, payload, policy_depth,
                    max_depth, max_attempts, evidence
                ) VALUES (
                    :action_id, :tenant_id, :evaluation_id, :execution_id,
                    :action_index, :action_type, :state, :target_namespace,
                    :target_flow_key, :channel, CAST(:payload AS jsonb), :policy_depth,
                    :max_depth, :max_attempts, CAST(:action_evidence AS jsonb)
                )
                ON CONFLICT (tenant_id, evaluation_id, action_index) DO NOTHING
                """
            ),
            {
                "action_id": new_runtime_id(),
                "tenant_id": tenant_id,
                "evaluation_id": inserted,
                "execution_id": execution_id,
                "action_index": index,
                "action_type": action.type,
                "state": "SKIPPED" if skipped else "PENDING",
                "target_namespace": action.namespace or definition_row["namespace_name"],
                "target_flow_key": action.flow_id,
                "channel": action.channel,
                "payload": json.dumps(payload),
                "policy_depth": policy_depth,
                "max_depth": action.max_depth,
                "max_attempts": action.max_attempts,
                "action_evidence": json.dumps(
                    {
                        "decision": "skipped",
                        "reason": "maximum check policy depth reached",
                    }
                    if skipped
                    else {}
                ),
            },
        )
    return UUID(str(inserted))


async def _evaluate_due_deadline(
    connection: AsyncConnection,
    tenant_id: UUID,
    row: RowMapping,
    now: datetime,
) -> None:
    definition = CheckDefinition.model_validate(row["definition"])
    execution_state = str(row["execution_state"]) if row["execution_state"] else None
    terminal = execution_state in {"SUCCESS", "FAILED", "WARNING", "CANCELLED"}
    passed = terminal if definition.type in {"DURATION", "COMPLETION_WINDOW"} else False
    if definition.type == "START_DELAY":
        passed = execution_state == "RUNNING" or terminal
    outcome = _outcome(definition, passed)
    reason = (
        "deadline was satisfied before periodic evaluation"
        if passed
        else f"{definition.type.lower().replace('_', ' ')} deadline was exceeded"
    )
    await _insert_evaluation(
        connection,
        tenant_id,
        row,
        execution_id=(UUID(str(row["execution_id"])) if row["execution_id"] else None),
        evaluation_point=(
            CheckEvaluationPoint.FRESHNESS
            if definition.type == "FRESHNESS"
            else CheckEvaluationPoint.DEADLINE
        ),
        subject_key=str(row["subject_key"]),
        outcome=outcome,
        reason=reason,
        evidence={
            "dueAt": row["due_at"].isoformat(),
            "evaluatedAt": now.isoformat(),
            "executionState": execution_state,
        },
        labels=dict(row["labels"] or {}),
        policy_depth=_policy_depth(dict(row["trigger_context"] or {})),
    )
    if definition.type == "FRESHNESS":
        next_due = now + _threshold(definition)
        await _schedule_deadline(
            connection,
            tenant_id,
            UUID(str(row["check_definition_id"])),
            execution_id=None,
            deadline_type="FRESHNESS",
            due_at=next_due,
            subject_key=f"freshness:{next_due.isoformat()}",
        )


async def _execution_outputs(
    connection: AsyncConnection, tenant_id: UUID, execution_id: UUID
) -> dict[str, Any]:
    rows = (
        (
            await connection.execute(
                text(
                    """
                    SELECT task_runs.task_path, outputs.value
                    FROM execution_outputs AS outputs
                    JOIN task_runs
                      ON task_runs.tenant_id = outputs.tenant_id
                     AND task_runs.execution_id = outputs.execution_id
                     AND task_runs.id = outputs.task_run_id
                    WHERE outputs.tenant_id = :tenant_id
                      AND outputs.execution_id = :execution_id
                    ORDER BY outputs.occurred_at, outputs.id
                    """
                ),
                {"tenant_id": tenant_id, "execution_id": execution_id},
            )
        )
        .mappings()
        .all()
    )
    return {str(row["task_path"]): dict(row["value"]) for row in rows}


async def _database_time(connection: AsyncConnection) -> datetime:
    value = await connection.scalar(text("SELECT clock_timestamp()"))
    if not isinstance(value, datetime):
        raise TypeError("PostgreSQL returned an invalid database timestamp")
    return value


def _threshold(definition: CheckDefinition) -> timedelta:
    if definition.threshold is None:
        raise ValueError(f"check {definition.id!r} has no threshold")
    return definition.threshold


def _outcome(definition: CheckDefinition, passed: bool) -> CheckOutcome:
    if passed:
        return CheckOutcome.PASS
    return CheckOutcome.WARN if definition.severity == "WARN" else CheckOutcome.FAIL


def _policy_depth(trigger: dict[str, Any]) -> int:
    value = trigger.get("checkPolicyDepth", 0)
    return max(int(value), 0) if isinstance(value, int | str) else 0


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _validate_limit(limit: int) -> None:
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")


def _to_policy(row: RowMapping, tenant_id: str) -> NamespaceCheckPolicy:
    return NamespaceCheckPolicy(
        policy_id=row["policy_id"],
        tenant_id=tenant_id,
        namespace=row["namespace_name"],
        policy_key=row["policy_key"],
        source=row["source"],
        task_type=row["task_type"],
        definition=CheckDefinition.model_validate(row["definition"]),
        enabled=row["enabled"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _to_evaluation(row: RowMapping, tenant_id: str) -> CheckEvaluation:
    return CheckEvaluation(
        evaluation_id=row["evaluation_id"],
        tenant_id=tenant_id,
        check_definition_id=row["check_definition_id"],
        execution_id=row["execution_id"],
        namespace=row["namespace_name"],
        flow_id=row["flow_key"],
        flow_revision=row["flow_revision"],
        check_id=row["check_key"],
        check_type=row["check_type"],
        source=row["source"],
        evaluation_point=row["evaluation_point"],
        subject_key=row["subject_key"],
        outcome=row["outcome"],
        severity=row["severity"],
        reason=row["reason"],
        evidence=row["evidence"],
        labels=row["labels"],
        evaluated_at=row["evaluated_at"],
    )


def _to_action(row: RowMapping, tenant_id: str) -> CheckActionRecord:
    return CheckActionRecord(
        action_id=row["action_id"],
        tenant_id=tenant_id,
        evaluation_id=row["evaluation_id"],
        execution_id=row["execution_id"],
        action_index=row["action_index"],
        action_type=row["action_type"],
        state=CheckActionState(row["state"]),
        target_namespace=row["target_namespace"],
        target_flow_id=row["target_flow_key"],
        channel=row["channel"],
        payload=row["payload"],
        policy_depth=row["policy_depth"],
        max_depth=row["max_depth"],
        attempt=row["attempt"],
        max_attempts=row["max_attempts"],
        owner_id=row["owner_id"],
        fencing_token=row["fencing_token"],
        available_at=row["available_at"],
        last_error=row["last_error"],
        evidence=row["evidence"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
