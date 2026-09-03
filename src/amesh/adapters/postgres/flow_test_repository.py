from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.tenant_context import (
    resolve_active_tenant_id,
    tenant_admin_transaction,
)
from amesh.domain import (
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestQualityGate,
    FlowTestQualityGateUpdate,
    FlowTestRunResult,
    new_runtime_id,
)
from amesh.ports import FlowTestRepository, FlowTestVersionConflict


class PostgresFlowTestRepository(FlowTestRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def save_definition(
        self,
        namespace: str,
        flow_id: str,
        request: FlowTestDefinitionCreateRequest,
        *,
        tenant_id: str,
        flow_semantic_hash: str,
        plugin_set_hash: str,
        actor_id: str,
    ) -> FlowTestDefinition:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            now = datetime.now(UTC)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO flow_test_definitions (
                                definition_id, tenant_id, namespace_name, flow_id, test_id,
                                test_name, flow_revision, flow_semantic_hash, plugin_set_hash,
                                inputs, variables, fixtures, expected, tags, version,
                                created_by, updated_by, created_at, updated_at
                            ) VALUES (
                                :definition_id, :tenant_id, :namespace, :flow_id, :test_id,
                                :test_name, :revision, :flow_semantic_hash, :plugin_set_hash,
                                CAST(:inputs AS jsonb), CAST(:variables AS jsonb),
                                CAST(:fixtures AS jsonb), CAST(:expected AS jsonb), :tags, 1,
                                :actor_id, :actor_id, :now, :now
                            )
                            ON CONFLICT (tenant_id, namespace_name, flow_id, test_id)
                            DO UPDATE SET
                                test_name = EXCLUDED.test_name,
                                flow_revision = EXCLUDED.flow_revision,
                                flow_semantic_hash = EXCLUDED.flow_semantic_hash,
                                plugin_set_hash = EXCLUDED.plugin_set_hash,
                                inputs = EXCLUDED.inputs,
                                variables = EXCLUDED.variables,
                                fixtures = EXCLUDED.fixtures,
                                expected = EXCLUDED.expected,
                                tags = EXCLUDED.tags,
                                version = flow_test_definitions.version + 1,
                                updated_by = EXCLUDED.updated_by,
                                updated_at = EXCLUDED.updated_at
                            WHERE flow_test_definitions.version = CAST(:expected_version AS bigint)
                            RETURNING *
                            """
                        ),
                        {
                            "definition_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "test_id": request.test_id,
                            "test_name": request.name,
                            "revision": request.revision,
                            "flow_semantic_hash": flow_semantic_hash,
                            "plugin_set_hash": plugin_set_hash,
                            "inputs": _json(request.inputs),
                            "variables": _json(request.variables),
                            "fixtures": _json(
                                {
                                    key: fixture.model_dump(mode="json", by_alias=True)
                                    for key, fixture in request.fixtures.items()
                                }
                            ),
                            "expected": _json(
                                request.expected.model_dump(mode="json", by_alias=True)
                            ),
                            "tags": list(request.tags),
                            "actor_id": actor_id,
                            "now": now,
                            "expected_version": request.expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise FlowTestVersionConflict("flow-test definition version changed")
            persisted = _to_definition(row, tenant_id)
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="flow-test.definition.saved",
                resource_id=f"{namespace}.{flow_id}:{request.test_id}",
                reason="revision-pinned flow-test definition saved",
                evidence={
                    "revision": request.revision,
                    "version": persisted.version,
                    "flowSemanticHash": flow_semantic_hash,
                    "pluginSetHash": plugin_set_hash,
                },
            )
            return persisted

    async def list_definitions(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> tuple[FlowTestDefinition, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM flow_test_definitions
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND flow_id = :flow_id
                              AND (
                                CAST(:revision AS bigint) IS NULL
                                OR flow_revision = CAST(:revision AS bigint)
                              )
                            ORDER BY flow_revision DESC, test_id
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "revision": revision,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_definition(row, tenant_id) for row in rows)

    async def delete_definition(
        self,
        namespace: str,
        flow_id: str,
        test_id: str,
        *,
        tenant_id: str,
        expected_version: int,
        actor_id: str,
    ) -> None:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            result = await connection.execute(
                text(
                    """
                    DELETE FROM flow_test_definitions
                    WHERE tenant_id = :tenant_id
                      AND namespace_name = :namespace
                      AND flow_id = :flow_id
                      AND test_id = :test_id
                      AND version = :expected_version
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "flow_id": flow_id,
                    "test_id": test_id,
                    "expected_version": expected_version,
                },
            )
            if result.rowcount != 1:
                raise FlowTestVersionConflict("flow-test definition version changed")
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="flow-test.definition.deleted",
                resource_id=f"{namespace}.{flow_id}:{test_id}",
                reason="version-matched flow-test definition deleted",
                evidence={"version": expected_version},
            )

    async def record_run(self, result: FlowTestRunResult) -> FlowTestRunResult:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, result.tenant_id)
            await connection.execute(
                text(
                    """
                    INSERT INTO flow_test_runs (
                        run_id, tenant_id, namespace_name, flow_id, flow_revision,
                        flow_semantic_hash, plugin_set_hash, simulator_version,
                        outcome, result, requested_by, created_at
                    ) VALUES (
                        :run_id, :tenant_id, :namespace, :flow_id, :revision,
                        :flow_semantic_hash, :plugin_set_hash, :simulator_version,
                        :outcome, CAST(:result AS jsonb), :requested_by, :created_at
                    )
                    """
                ),
                {
                    "run_id": result.run_id,
                    "tenant_id": tenant_uuid,
                    "namespace": result.namespace,
                    "flow_id": result.flow_id,
                    "revision": result.revision,
                    "flow_semantic_hash": result.flow_semantic_hash,
                    "plugin_set_hash": result.plugin_set_hash,
                    "simulator_version": result.simulator_version,
                    "outcome": result.outcome.value,
                    "result": _json(result.model_dump(mode="json", by_alias=True)),
                    "requested_by": result.requested_by,
                    "created_at": result.created_at,
                },
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=result.requested_by,
                action="flow-test.run.recorded",
                resource_id=str(result.run_id),
                reason="isolated revision-pinned flow-test result recorded",
                evidence={
                    "namespace": result.namespace,
                    "flowId": result.flow_id,
                    "revision": result.revision,
                    "outcome": result.outcome.value,
                    "coverage": result.coverage.percentage,
                    "simulatorVersion": result.simulator_version,
                },
            )
        return result

    async def list_runs(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
        limit: int = 50,
    ) -> tuple[FlowTestRunResult, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT result
                            FROM flow_test_runs
                            WHERE tenant_id = :tenant_id
                              AND namespace_name = :namespace
                              AND flow_id = :flow_id
                              AND (
                                CAST(:revision AS bigint) IS NULL
                                OR flow_revision = CAST(:revision AS bigint)
                              )
                            ORDER BY created_at DESC, run_id DESC
                            LIMIT :limit
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "revision": revision,
                            "limit": limit,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(FlowTestRunResult.model_validate(row["result"]) for row in rows)

    async def get_gate(
        self,
        namespace: str,
        *,
        tenant_id: str,
    ) -> FlowTestQualityGate | None:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM flow_test_quality_gates
                            WHERE tenant_id = :tenant_id AND namespace_name = :namespace
                            """
                        ),
                        {"tenant_id": tenant_uuid, "namespace": namespace},
                    )
                )
                .mappings()
                .one_or_none()
            )
        return None if row is None else _to_gate(row, tenant_id)

    async def upsert_gate(
        self,
        namespace: str,
        request: FlowTestQualityGateUpdate,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> FlowTestQualityGate:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await resolve_active_tenant_id(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO flow_test_quality_gates (
                                tenant_id, namespace_name, enabled, minimum_coverage,
                                required_test_ids, version, updated_by, updated_at
                            ) VALUES (
                                :tenant_id, :namespace, :enabled, :minimum_coverage,
                                :required_test_ids, 1, :actor_id, :updated_at
                            )
                            ON CONFLICT (tenant_id, namespace_name) DO UPDATE SET
                                enabled = EXCLUDED.enabled,
                                minimum_coverage = EXCLUDED.minimum_coverage,
                                required_test_ids = EXCLUDED.required_test_ids,
                                version = flow_test_quality_gates.version + 1,
                                updated_by = EXCLUDED.updated_by,
                                updated_at = EXCLUDED.updated_at
                            WHERE flow_test_quality_gates.version = CAST(:expected_version AS bigint)
                            RETURNING *
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "enabled": request.enabled,
                            "minimum_coverage": request.minimum_coverage,
                            "required_test_ids": list(request.required_test_ids),
                            "actor_id": actor_id,
                            "updated_at": datetime.now(UTC),
                            "expected_version": request.expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise FlowTestVersionConflict("flow-test quality-gate version changed")
            persisted = _to_gate(row, tenant_id)
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="flow-test.gate.saved",
                resource_id=namespace,
                reason="namespace flow-test promotion gate saved",
                evidence={
                    "enabled": persisted.enabled,
                    "minimumCoverage": persisted.minimum_coverage,
                    "requiredTestIds": list(persisted.required_test_ids),
                    "version": persisted.version,
                },
            )
            return persisted


def _to_definition(row: RowMapping, tenant_id: str) -> FlowTestDefinition:
    return FlowTestDefinition.model_validate(
        {
            "id": UUID(str(row["definition_id"])),
            "tenantId": tenant_id,
            "namespace": str(row["namespace_name"]),
            "flowId": str(row["flow_id"]),
            "testId": str(row["test_id"]),
            "name": str(row["test_name"]),
            "revision": int(row["flow_revision"]),
            "flowSemanticHash": str(row["flow_semantic_hash"]),
            "pluginSetHash": str(row["plugin_set_hash"]),
            "inputs": dict(row["inputs"]),
            "variables": dict(row["variables"]),
            "fixtures": dict(row["fixtures"]),
            "expected": dict(row["expected"]),
            "tags": tuple(row["tags"]),
            "version": int(row["version"]),
            "createdBy": str(row["created_by"]),
            "updatedBy": str(row["updated_by"]),
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
    )


def _to_gate(row: RowMapping, tenant_id: str) -> FlowTestQualityGate:
    return FlowTestQualityGate(
        tenantId=tenant_id,
        namespace=str(row["namespace_name"]),
        enabled=bool(row["enabled"]),
        minimumCoverage=float(row["minimum_coverage"]),
        requiredTestIds=tuple(row["required_test_ids"]),
        version=int(row["version"]),
        updatedBy=str(row["updated_by"]),
        updatedAt=row["updated_at"],
    )


def _json(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


async def _write_audit(
    connection: AsyncConnection,
    *,
    tenant_id: UUID,
    actor_id: str,
    action: str,
    resource_id: str,
    reason: str,
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                tenant_id, event_id, actor_id, action, resource_type, resource_id,
                outcome, reason, source, evidence, occurred_at
            ) VALUES (
                :tenant_id, :event_id, :actor_id, :action, 'flow_test', :resource_id,
                'SUCCESS', :reason, '{}'::jsonb, CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "tenant_id": tenant_id,
            "event_id": new_runtime_id(),
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "reason": reason,
            "evidence": _json(evidence),
            "occurred_at": datetime.now(UTC),
        },
    )
