"""Durable PostgreSQL command/event/outbox storage for differential shadow runs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, cast
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import new_runtime_id
from amesh.ports.differential import DifferentialShadowRepository

from .differential import (
    ComparisonReport,
    DifferentialSpec,
    Lineage,
    RunObservation,
    ShadowRun,
)


class DifferentialState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class DifferentialConflictError(ValueError):
    """Raised when an immutable request or evidence identity is reused with different data."""


class DifferentialRunBusyError(RuntimeError):
    """Raised when an in-flight side cannot be safely started a second time."""


class DifferentialRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    spec: DifferentialSpec
    state: DifferentialState
    version: int = Field(ge=0)
    left_run_id: UUID | None = Field(default=None, alias="leftRunId")
    right_run_id: UUID | None = Field(default=None, alias="rightRunId")
    report: ComparisonReport | None = None
    error: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")


class DifferentialRunRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    run_id: UUID = Field(alias="runId")
    tenant_id: str = Field(alias="tenantId")
    spec_id: UUID = Field(alias="specId")
    side: str = Field(pattern=r"^(left|right)$")
    configuration_digest: str = Field(alias="configurationDigest")
    input_digest: str = Field(alias="inputDigest")
    state: DifferentialState
    attempt: int = Field(ge=0)
    observation: RunObservation | None = None
    error: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")

    def shadow_run(self) -> ShadowRun:
        if self.observation is None:
            raise ValueError("differential run has no accepted observation")
        return ShadowRun(
            lineage=Lineage(
                runId=self.run_id,
                specId=self.spec_id,
                side=self.side,
                configurationDigest=self.configuration_digest,
                inputDigest=self.input_digest,
            ),
            observation=self.observation,
        )


class DifferentialEventRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    event_id: UUID = Field(alias="eventId")
    tenant_id: str = Field(alias="tenantId")
    spec_id: UUID = Field(alias="specId")
    run_id: UUID | None = Field(default=None, alias="runId")
    sequence: int = Field(ge=1)
    event_key: str = Field(alias="eventKey")
    event_type: str = Field(alias="eventType")
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(alias="occurredAt")


class PostgresDifferentialShadowRepository(DifferentialShadowRepository):
    """Tenant-isolated durable differential state with restart-safe side claims."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_or_get(
        self,
        spec: DifferentialSpec,
        *,
        actor_id: str,
    ) -> DifferentialRecord:
        if not actor_id:
            raise ValueError("actor_id is required")
        if _digest(spec.inputs) != spec.input_digest:
            raise ValueError("frozen inputs changed after differential specification creation")
        request_hash = _request_hash(spec)
        payload = spec.model_dump(mode="json", by_alias=True)
        async with tenant_transaction(self._engine, spec.tenant_id) as (connection, tenant_uuid):
            command = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO commands_inbox (
                            tenant_id, command_id, idempotency_key, command_type, request_hash
                        ) VALUES (
                            :tenant_id, :command_id, :idempotency_key,
                            'DifferentialSpecCreate', :request_hash
                        )
                        ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
                        RETURNING request_hash
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "command_id": spec.spec_id,
                            "idempotency_key": spec.idempotency_key,
                            "request_hash": request_hash,
                        },
                    )
                )
                .mappings()
                .first()
            )
            if command is None:
                command = (
                    (
                        await connection.execute(
                            text(
                                """
                            SELECT request_hash FROM commands_inbox
                            WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key
                            """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "idempotency_key": spec.idempotency_key,
                            },
                        )
                    )
                    .mappings()
                    .first()
                )
                if command is None:
                    raise LookupError("differential command journal entry is unavailable")
                if command["request_hash"] != request_hash:
                    raise DifferentialConflictError(
                        "idempotency key was used for a different differential request"
                    )
            inserted = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO differential_specs (
                            spec_id, tenant_id, namespace_name, idempotency_key,
                            left_configuration, right_configuration, inputs, input_digest,
                            fixtures, policy, actor_id
                        ) VALUES (
                            :spec_id, :tenant_id, :namespace_name, :idempotency_key,
                            CAST(:left_configuration AS jsonb),
                            CAST(:right_configuration AS jsonb), CAST(:inputs AS jsonb),
                            :input_digest, CAST(:fixtures AS jsonb), CAST(:policy AS jsonb), :actor_id
                        )
                        ON CONFLICT (tenant_id, namespace_name, idempotency_key) DO NOTHING
                        RETURNING *
                        """
                        ),
                        {
                            "spec_id": spec.spec_id,
                            "tenant_id": tenant_uuid,
                            "namespace_name": spec.namespace,
                            "idempotency_key": spec.idempotency_key,
                            "left_configuration": json.dumps(
                                payload["left"], separators=(",", ":")
                            ),
                            "right_configuration": json.dumps(
                                payload["right"], separators=(",", ":")
                            ),
                            "inputs": json.dumps(payload["inputs"], separators=(",", ":")),
                            "input_digest": spec.input_digest,
                            "fixtures": json.dumps(payload["fixtures"], separators=(",", ":")),
                            "policy": json.dumps(payload["policy"], separators=(",", ":")),
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .first()
            )
            row = inserted or await self._select_spec(connection, tenant_uuid, spec.spec_id)
            if row is None:
                row = await self._select_spec_by_key(
                    connection,
                    tenant_uuid,
                    spec.namespace,
                    spec.idempotency_key,
                )
            if row is None:
                raise LookupError("differential specification was not stored")
            stored = _record(row, spec.tenant_id)
            if _request_hash(stored.spec) != request_hash:
                raise DifferentialConflictError("stored differential specification conflicts")
            if inserted is not None:
                await self._append_event(
                    connection,
                    tenant_uuid,
                    spec.spec_id,
                    event_key=f"spec:{spec.spec_id}:created",
                    event_type="DifferentialSpecCreated",
                    payload={"inputDigest": spec.input_digest},
                )
                await connection.execute(
                    text(
                        """
                        UPDATE commands_inbox
                        SET response_status = 201,
                            response_body = CAST(:response_body AS jsonb),
                            committed_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "idempotency_key": spec.idempotency_key,
                        "response_body": json.dumps(payload, separators=(",", ":")),
                    },
                )
            return stored

    async def get(
        self,
        tenant_id: str,
        namespace: str,
        idempotency_key: str,
    ) -> DifferentialRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._select_spec_by_key(
                connection, tenant_uuid, namespace, idempotency_key
            )
            if row is None:
                raise LookupError("differential specification does not exist")
            return _record(row, tenant_id)

    async def get_by_id(self, tenant_id: str, spec_id: UUID) -> DifferentialRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._select_spec(connection, tenant_uuid, spec_id)
            if row is None:
                raise LookupError("differential specification does not exist")
            return _record(row, tenant_id)

    async def claim_side(
        self,
        tenant_id: str,
        spec_id: UUID,
        side: str,
    ) -> DifferentialRunRecord:
        normalized_side = side.lower()
        if normalized_side not in {"left", "right"}:
            raise ValueError("differential side must be left or right")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            spec_row = await self._select_spec(connection, tenant_uuid, spec_id, lock=True)
            if spec_row is None:
                raise LookupError("differential specification does not exist")
            spec = _spec_from_row(spec_row, tenant_id)
            configuration = spec.left if normalized_side == "left" else spec.right
            run_row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM differential_runs
                        WHERE tenant_id = :tenant_id AND spec_id = :spec_id AND side = :side
                        FOR UPDATE
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "spec_id": spec_id,
                            "side": normalized_side.upper(),
                        },
                    )
                )
                .mappings()
                .first()
            )
            if spec_row["state"] == DifferentialState.SUCCEEDED.value and run_row is None:
                raise DifferentialConflictError(
                    "completed differential is missing its side lineage"
                )
            if run_row is not None and (
                run_row["configuration_digest"] != configuration.digest
                or run_row["input_digest"] != spec.input_digest
            ):
                raise DifferentialConflictError("differential run pin conflicts with its spec")
            if run_row is not None and run_row["state"] == DifferentialState.RUNNING.value:
                raise DifferentialRunBusyError("differential side is already running")
            if run_row is not None and run_row["state"] == DifferentialState.SUCCEEDED.value:
                return _run_record(run_row, tenant_id)
            attempt = (int(run_row["attempt"]) if run_row is not None else 0) + 1
            if run_row is None:
                run_id = new_runtime_id()
                run_row = (
                    (
                        await connection.execute(
                            text(
                                """
                            INSERT INTO differential_runs (
                                run_id, tenant_id, spec_id, side, configuration_digest,
                                input_digest, state, attempt
                            ) VALUES (
                                :run_id, :tenant_id, :spec_id, :side, :configuration_digest,
                                :input_digest, 'RUNNING', :attempt
                            ) RETURNING *
                            """
                            ),
                            {
                                "run_id": run_id,
                                "tenant_id": tenant_uuid,
                                "spec_id": spec_id,
                                "side": normalized_side.upper(),
                                "configuration_digest": configuration.digest,
                                "input_digest": spec.input_digest,
                                "attempt": attempt,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
            else:
                run_row = (
                    (
                        await connection.execute(
                            text(
                                """
                            UPDATE differential_runs
                            SET state = 'RUNNING', attempt = :attempt,
                                error = NULL, updated_at = clock_timestamp(), completed_at = NULL
                            WHERE tenant_id = :tenant_id AND run_id = :run_id
                            RETURNING *
                            """
                            ),
                            {
                                "tenant_id": tenant_uuid,
                                "run_id": run_row["run_id"],
                                "attempt": attempt,
                            },
                        )
                    )
                    .mappings()
                    .one()
                )
            await self._append_event(
                connection,
                tenant_uuid,
                spec_id,
                run_id=run_row["run_id"],
                event_key=f"run:{run_row['run_id']}:attempt:{attempt}:claimed",
                event_type="DifferentialSideClaimed",
                payload={"side": normalized_side, "attempt": attempt},
            )
            await connection.execute(
                text(
                    """
                    UPDATE differential_specs
                    SET state = 'RUNNING', version = version + 1, updated_at = clock_timestamp(),
                        error = NULL, completed_at = NULL,
                        left_run_id = CASE WHEN :side = 'LEFT' THEN :run_id ELSE left_run_id END,
                        right_run_id = CASE WHEN :side = 'RIGHT' THEN :run_id ELSE right_run_id END
                    WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "spec_id": spec_id,
                    "side": normalized_side.upper(),
                    "run_id": run_row["run_id"],
                },
            )
            return _run_record(run_row, tenant_id)

    async def record_observation(
        self,
        tenant_id: str,
        run_id: UUID,
        observation: RunObservation,
    ) -> DifferentialRunRecord:
        payload = observation.model_dump(mode="json", by_alias=True)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._select_run(connection, tenant_uuid, run_id)
            if row is None:
                raise LookupError("differential run does not exist")
            if await self._select_spec(connection, tenant_uuid, row["spec_id"], lock=True) is None:
                raise LookupError("differential specification does not exist")
            row = await self._select_run(connection, tenant_uuid, run_id, lock=True)
            if row is None:
                raise LookupError("differential run does not exist")
            if row["state"] == DifferentialState.SUCCEEDED.value:
                existing = _run_record(row, tenant_id)
                if existing.observation != observation:
                    raise DifferentialConflictError("differential observation is immutable")
                return existing
            if row["state"] != DifferentialState.RUNNING.value:
                raise DifferentialRunBusyError(f"differential run is {row['state']}")
            updated = (
                (
                    await connection.execute(
                        text(
                            """
                        UPDATE differential_runs
                        SET state = 'SUCCEEDED', observation = CAST(:observation AS jsonb),
                            error = NULL, updated_at = clock_timestamp(), completed_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND run_id = :run_id
                        RETURNING *
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "run_id": run_id,
                            "observation": json.dumps(payload, separators=(",", ":")),
                        },
                    )
                )
                .mappings()
                .one()
            )
            await self._append_event(
                connection,
                tenant_uuid,
                updated["spec_id"],
                run_id=run_id,
                event_key=f"run:{run_id}:attempt:{updated['attempt']}:succeeded",
                event_type="DifferentialSideSucceeded",
                payload={"observationDigest": _digest(payload)},
            )
            return _run_record(updated, tenant_id)

    async def get_run(self, tenant_id: str, run_id: UUID) -> DifferentialRunRecord:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._select_run(connection, tenant_uuid, run_id)
            if row is None:
                raise LookupError("differential run does not exist")
            return _run_record(row, tenant_id)

    async def record_failure(
        self,
        tenant_id: str,
        run_id: UUID,
        error: str,
    ) -> DifferentialRunRecord:
        if not error or len(error) > 4096:
            raise ValueError("differential failure must contain 1-4096 characters")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = await self._select_run(connection, tenant_uuid, run_id)
            if row is None:
                raise LookupError("differential run does not exist")
            if await self._select_spec(connection, tenant_uuid, row["spec_id"], lock=True) is None:
                raise LookupError("differential specification does not exist")
            row = await self._select_run(connection, tenant_uuid, run_id, lock=True)
            if row is None:
                raise LookupError("differential run does not exist")
            if row["state"] == DifferentialState.FAILED.value and row["error"] == error:
                return _run_record(row, tenant_id)
            if row["state"] != DifferentialState.RUNNING.value:
                raise DifferentialRunBusyError(f"differential run is {row['state']}")
            updated = (
                (
                    await connection.execute(
                        text(
                            """
                        UPDATE differential_runs
                        SET state = 'FAILED', error = :error, updated_at = clock_timestamp(),
                            completed_at = clock_timestamp()
                        WHERE tenant_id = :tenant_id AND run_id = :run_id
                        RETURNING *
                        """
                        ),
                        {"tenant_id": tenant_uuid, "run_id": run_id, "error": error},
                    )
                )
                .mappings()
                .one()
            )
            await self._append_event(
                connection,
                tenant_uuid,
                updated["spec_id"],
                run_id=run_id,
                event_key=f"run:{run_id}:attempt:{updated['attempt']}:failed",
                event_type="DifferentialSideFailed",
                payload={"error": error},
            )
            await connection.execute(
                text(
                    """
                    UPDATE differential_specs
                    SET state = 'FAILED', error = :error, version = version + 1,
                        updated_at = clock_timestamp(), completed_at = clock_timestamp()
                    WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "spec_id": updated["spec_id"],
                    "error": error,
                },
            )
            return _run_record(updated, tenant_id)

    async def complete(
        self,
        tenant_id: str,
        spec_id: UUID,
        report: ComparisonReport,
    ) -> DifferentialRecord:
        if report.tenant_id != tenant_id or report.spec_id != spec_id:
            raise DifferentialConflictError("differential report identity does not match spec")
        payload = report.model_dump(mode="json", by_alias=True)
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            spec_row = await self._select_spec(connection, tenant_uuid, spec_id, lock=True)
            if spec_row is None:
                raise LookupError("differential specification does not exist")
            spec = _spec_from_row(spec_row, tenant_id)
            if report.namespace != spec.namespace or report.input_digest != spec.input_digest:
                raise DifferentialConflictError(
                    "differential report does not match frozen spec data"
                )
            if spec_row["state"] == DifferentialState.SUCCEEDED.value:
                existing = _record(spec_row, tenant_id)
                if existing.report != report:
                    raise DifferentialConflictError("differential report is immutable")
                return existing
            run_rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT run_id, side, configuration_digest, input_digest, state
                        FROM differential_runs
                        WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                        """
                        ),
                        {"tenant_id": tenant_uuid, "spec_id": spec_id},
                    )
                )
                .mappings()
                .all()
            )
            count = sum(1 for row in run_rows if row["state"] == DifferentialState.SUCCEEDED.value)
            if count != 2:
                raise RuntimeError("both differential sides must succeed before report completion")
            by_side = {str(row["side"]).lower(): row for row in run_rows}
            for side, lineage in (("left", report.left.lineage), ("right", report.right.lineage)):
                stored_run = by_side.get(side)
                if stored_run is None or stored_run["state"] != DifferentialState.SUCCEEDED.value:
                    raise DifferentialConflictError(
                        "differential report is missing a persisted side"
                    )
                if (
                    UUID(str(stored_run["run_id"])) != lineage.run_id
                    or stored_run["configuration_digest"] != lineage.configuration_digest
                    or stored_run["input_digest"] != lineage.input_digest
                ):
                    raise DifferentialConflictError(
                        "differential report lineage conflicts with storage"
                    )
            updated = (
                (
                    await connection.execute(
                        text(
                            """
                        UPDATE differential_specs
                        SET state = 'SUCCEEDED', report = CAST(:report AS jsonb),
                            version = version + 1, updated_at = clock_timestamp(),
                            completed_at = clock_timestamp(), error = NULL
                        WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                        RETURNING *
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "spec_id": spec_id,
                            "report": json.dumps(payload, separators=(",", ":")),
                        },
                    )
                )
                .mappings()
                .one()
            )
            await self._append_event(
                connection,
                tenant_uuid,
                spec_id,
                event_key=f"spec:{spec_id}:completed",
                event_type="DifferentialCompleted",
                payload={"reportDigest": _digest(payload), "passed": report.passed},
            )
            return _record(updated, tenant_id)

    async def list_resumable(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[DifferentialRunRecord, ...]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM differential_runs
                        WHERE tenant_id = :tenant_id AND state IN ('PENDING', 'FAILED')
                        ORDER BY updated_at, run_id
                        LIMIT :limit
                        """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_run_record(row, tenant_id) for row in rows)

    async def events(self, tenant_id: str, spec_id: UUID) -> tuple[DifferentialEventRecord, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM differential_events
                        WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                        ORDER BY sequence
                        """
                        ),
                        {"tenant_id": tenant_uuid, "spec_id": spec_id},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_event_record(row, tenant_id) for row in rows)

    async def _select_spec(
        self,
        connection: Any,
        tenant_uuid: UUID,
        spec_id: UUID,
        *,
        lock: bool = False,
    ) -> RowMapping | None:
        query = (
            "SELECT * FROM differential_specs WHERE tenant_id = :tenant_id AND spec_id = :spec_id"
        )
        if lock:
            query += " FOR UPDATE"
        return cast(
            RowMapping | None,
            (
                (
                    await connection.execute(
                        text(query), {"tenant_id": tenant_uuid, "spec_id": spec_id}
                    )
                )
                .mappings()
                .first()
            ),
        )

    async def _select_spec_by_key(
        self,
        connection: Any,
        tenant_uuid: UUID,
        namespace: str,
        idempotency_key: str,
    ) -> RowMapping | None:
        return cast(
            RowMapping | None,
            (
                (
                    await connection.execute(
                        text(
                            """
                    SELECT * FROM differential_specs
                    WHERE tenant_id = :tenant_id AND namespace_name = :namespace_name
                      AND idempotency_key = :idempotency_key
                    """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace_name": namespace,
                            "idempotency_key": idempotency_key,
                        },
                    )
                )
                .mappings()
                .first()
            ),
        )

    async def _select_run(
        self,
        connection: Any,
        tenant_uuid: UUID,
        run_id: UUID,
        *,
        lock: bool = False,
    ) -> RowMapping | None:
        query = "SELECT * FROM differential_runs WHERE tenant_id = :tenant_id AND run_id = :run_id"
        if lock:
            query += " FOR UPDATE"
        return cast(
            RowMapping | None,
            (
                (
                    await connection.execute(
                        text(query), {"tenant_id": tenant_uuid, "run_id": run_id}
                    )
                )
                .mappings()
                .first()
            ),
        )

    async def _append_event(
        self,
        connection: Any,
        tenant_uuid: UUID,
        spec_id: UUID,
        *,
        run_id: UUID | None = None,
        event_key: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> DifferentialEventRecord:
        existing = (
            (
                await connection.execute(
                    text(
                        """
                    SELECT * FROM differential_events
                    WHERE tenant_id = :tenant_id AND spec_id = :spec_id AND event_key = :event_key
                    """
                    ),
                    {"tenant_id": tenant_uuid, "spec_id": spec_id, "event_key": event_key},
                )
            )
            .mappings()
            .first()
        )
        if existing is not None:
            if existing["event_type"] != event_type or _json(existing["payload"]) != payload:
                raise DifferentialConflictError(
                    "differential event key was reused with different evidence"
                )
            return _event_record(existing, str(tenant_uuid))
        sequence = await connection.scalar(
            text(
                """
                SELECT coalesce(max(sequence), 0) + 1 FROM differential_events
                WHERE tenant_id = :tenant_id AND spec_id = :spec_id
                """
            ),
            {"tenant_id": tenant_uuid, "spec_id": spec_id},
        )
        row = (
            (
                await connection.execute(
                    text(
                        """
                    INSERT INTO differential_events (
                        event_id, tenant_id, spec_id, run_id, sequence,
                        event_key, event_type, payload
                    ) VALUES (
                        :event_id, :tenant_id, :spec_id, :run_id, :sequence,
                        :event_key, :event_type, CAST(:payload AS jsonb)
                    ) RETURNING *
                    """
                    ),
                    {
                        "event_id": new_runtime_id(),
                        "tenant_id": tenant_uuid,
                        "spec_id": spec_id,
                        "run_id": run_id,
                        "sequence": int(sequence or 1),
                        "event_key": event_key,
                        "event_type": event_type,
                        "payload": json.dumps(payload, separators=(",", ":")),
                    },
                )
            )
            .mappings()
            .one()
        )
        return _event_record(row, str(tenant_uuid))


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _request_hash(spec: DifferentialSpec) -> str:
    return _digest(spec.model_dump(mode="json", by_alias=True, exclude={"spec_id"}))


def _json(value: Any) -> Any:
    return json.loads(value) if isinstance(value, str) else value


def _spec_from_row(row: RowMapping, tenant_id: str) -> DifferentialSpec:
    return DifferentialSpec(
        specId=row["spec_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        left=_json(row["left_configuration"]),
        right=_json(row["right_configuration"]),
        inputs=_json(row["inputs"]),
        inputDigest=row["input_digest"],
        fixtures=tuple(_json(row["fixtures"])),
        policy=_json(row["policy"]),
        idempotencyKey=row["idempotency_key"],
    )


def _record(row: RowMapping, tenant_id: str) -> DifferentialRecord:
    return DifferentialRecord(
        spec=_spec_from_row(row, tenant_id),
        state=row["state"],
        version=row["version"],
        leftRunId=row["left_run_id"],
        rightRunId=row["right_run_id"],
        report=ComparisonReport.model_validate(_json(row["report"])) if row["report"] else None,
        error=row["error"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        completedAt=row["completed_at"],
    )


def _run_record(row: RowMapping, tenant_id: str) -> DifferentialRunRecord:
    return DifferentialRunRecord(
        runId=row["run_id"],
        tenantId=tenant_id,
        specId=row["spec_id"],
        side=str(row["side"]).lower(),
        configurationDigest=row["configuration_digest"],
        inputDigest=row["input_digest"],
        state=row["state"],
        attempt=row["attempt"],
        observation=(
            RunObservation.model_validate(_json(row["observation"]))
            if row["observation"] is not None
            else None
        ),
        error=row["error"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        completedAt=row["completed_at"],
    )


def _event_record(row: RowMapping, tenant_id: str) -> DifferentialEventRecord:
    return DifferentialEventRecord(
        eventId=row["event_id"],
        tenantId=tenant_id,
        specId=row["spec_id"],
        runId=row["run_id"],
        sequence=row["sequence"],
        eventKey=row["event_key"],
        eventType=row["event_type"],
        payload=_json(row["payload"]),
        occurredAt=row["occurred_at"],
    )


__all__ = [
    "DifferentialConflictError",
    "DifferentialEventRecord",
    "DifferentialRecord",
    "DifferentialRunBusyError",
    "DifferentialRunRecord",
    "DifferentialState",
    "PostgresDifferentialShadowRepository",
]
