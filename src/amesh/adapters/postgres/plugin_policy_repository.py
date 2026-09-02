from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import new_runtime_id
from amesh.domain.plugin_policy import (
    EffectivePluginPolicy,
    PluginPolicyDecision,
    PluginPolicyEffect,
    PluginPolicyImpactPreview,
    PluginPolicyRule,
    PluginPolicyRuleCreate,
    PluginPolicyScope,
    PluginPolicySelector,
    PluginPolicyStage,
    PluginQuarantine,
    PluginQuarantineCreate,
    PluginQuarantineState,
)

from .tenant_context import tenant_transaction


class PostgresPluginPolicyRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def effective_policy(
        self,
        tenant_id: str,
        *,
        namespace: str | None,
        default_allow: bool,
    ) -> EffectivePluginPolicy:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rules = await self._load_rules(connection, tenant_uuid, tenant_id, namespace)
            quarantines = await self._load_quarantines(
                connection,
                tenant_uuid,
                tenant_id,
                namespace,
            )
        return EffectivePluginPolicy(
            tenantId=tenant_id,
            namespace=namespace,
            defaultEffect=(PluginPolicyEffect.ALLOW if default_allow else PluginPolicyEffect.DENY),
            rules=rules,
            quarantines=quarantines,
        )

    async def create_rule(
        self,
        tenant_id: str,
        request: PluginPolicyRuleCreate,
        *,
        actor_id: str,
    ) -> PluginPolicyRule:
        rule_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO plugin_policy_rules (
                                id, tenant_id, namespace_name, scope, effect, stages,
                                package_pattern, version_range, vendor_pattern,
                                plugin_types, capabilities, priority, reason, enabled,
                                created_by, updated_by
                            ) VALUES (
                                :id, :rule_tenant_id, :namespace, :scope, :effect, :stages,
                                :package, :version_range, :vendor, :plugin_types,
                                :capabilities, :priority, :reason, :enabled,
                                :actor_id, :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        _rule_parameters(
                            rule_id,
                            tenant_uuid,
                            request,
                            actor_id=actor_id,
                        ),
                    )
                )
                .mappings()
                .one()
            )
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.policy.rule.create",
                resource_id=str(rule_id),
                reason=request.reason,
                evidence=request.model_dump(mode="json", by_alias=True),
            )
        return _rule(row, tenant_id)

    async def update_rule(
        self,
        tenant_id: str,
        rule_id: UUID,
        request: PluginPolicyRuleCreate,
        *,
        actor_id: str,
    ) -> PluginPolicyRule:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE plugin_policy_rules
                            SET tenant_id = :rule_tenant_id,
                                namespace_name = :namespace,
                                scope = :scope,
                                effect = :effect,
                                stages = :stages,
                                package_pattern = :package,
                                version_range = :version_range,
                                vendor_pattern = :vendor,
                                plugin_types = :plugin_types,
                                capabilities = :capabilities,
                                priority = :priority,
                                reason = :reason,
                                enabled = :enabled,
                                updated_by = :actor_id,
                                updated_at = clock_timestamp()
                            WHERE id = :id
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                            RETURNING *
                            """
                        ),
                        {
                            **_rule_parameters(
                                rule_id,
                                tenant_uuid,
                                request,
                                actor_id=actor_id,
                            ),
                            "tenant_id": tenant_uuid,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("plugin policy rule does not exist")
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.policy.rule.update",
                resource_id=str(rule_id),
                reason=request.reason,
                evidence=request.model_dump(mode="json", by_alias=True),
            )
        return _rule(row, tenant_id)

    async def get_rule(self, tenant_id: str, rule_id: UUID) -> PluginPolicyRule:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM plugin_policy_rules
                            WHERE id = :id
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                            """
                        ),
                        {"id": rule_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError("plugin policy rule does not exist")
        return _rule(row, tenant_id)

    async def delete_rule(
        self,
        tenant_id: str,
        rule_id: UUID,
        *,
        actor_id: str,
    ) -> None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            DELETE FROM plugin_policy_rules
                            WHERE id = :id
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                            RETURNING reason
                            """
                        ),
                        {"id": rule_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("plugin policy rule does not exist")
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.policy.rule.delete",
                resource_id=str(rule_id),
                reason=str(row["reason"]),
            )

    async def create_quarantine(
        self,
        tenant_id: str,
        request: PluginQuarantineCreate,
        *,
        actor_id: str,
    ) -> PluginQuarantine:
        quarantine_id = new_runtime_id()
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO plugin_quarantines (
                                id, tenant_id, namespace_name, scope, package_name,
                                version, reason, created_by
                            ) VALUES (
                                :id, :quarantine_tenant_id, :namespace, :scope,
                                :package, :version, :reason, :actor_id
                            )
                            ON CONFLICT DO NOTHING
                            RETURNING *
                            """
                        ),
                        {
                            "id": quarantine_id,
                            "quarantine_tenant_id": _scoped_tenant_uuid(
                                request.scope,
                                tenant_uuid,
                            ),
                            "namespace": request.namespace,
                            "scope": request.scope.value,
                            "package": request.package,
                            "version": request.version,
                            "reason": request.reason,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise ValueError("plugin version already has an active quarantine")
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.quarantine.activate",
                resource_id=str(quarantine_id),
                reason=request.reason,
                evidence=request.model_dump(mode="json", by_alias=True),
            )
        return _quarantine(row, tenant_id)

    async def release_quarantine(
        self,
        tenant_id: str,
        quarantine_id: UUID,
        *,
        actor_id: str,
        reason: str,
    ) -> PluginQuarantine:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE plugin_quarantines
                            SET state = 'RELEASED', released_by = :actor_id,
                                released_at = clock_timestamp()
                            WHERE id = :id AND state = 'ACTIVE'
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                            RETURNING *
                            """
                        ),
                        {
                            "id": quarantine_id,
                            "tenant_id": tenant_uuid,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("active plugin quarantine does not exist")
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.quarantine.release",
                resource_id=str(quarantine_id),
                reason=reason,
                evidence={"package": row["package_name"], "version": row["version"]},
            )
        return _quarantine(row, tenant_id)

    async def record_decision(
        self,
        decision: PluginPolicyDecision,
        *,
        actor_id: str,
    ) -> PluginPolicyDecision:
        async with tenant_transaction(self._engine, decision.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            await connection.execute(
                text(
                    """
                    INSERT INTO plugin_policy_decisions (
                        id, tenant_id, namespace_name, stage, allowed, flow_key,
                        flow_revision, actor_id, decision, decided_at
                    ) VALUES (
                        :id, :tenant_id, :namespace, :stage, :allowed, :flow_id,
                        :flow_revision, :actor_id, CAST(:decision AS jsonb), :decided_at
                    )
                    """
                ),
                {
                    "id": decision.decision_id,
                    "tenant_id": tenant_uuid,
                    "namespace": decision.namespace,
                    "stage": decision.stage.value,
                    "allowed": decision.allowed,
                    "flow_id": decision.flow_id,
                    "flow_revision": decision.flow_revision,
                    "actor_id": actor_id,
                    "decision": decision.model_dump_json(by_alias=True),
                    "decided_at": decision.decided_at,
                },
            )
            if not decision.allowed:
                await _write_audit(
                    connection,
                    tenant_uuid,
                    actor_id=actor_id,
                    action="plugin.policy.violation",
                    resource_id=decision.flow_id,
                    outcome="DENIED",
                    reason="plugin policy denied the requested operation",
                    evidence=decision.model_dump(mode="json", by_alias=True),
                )
        return decision

    async def list_decisions(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> tuple[PluginPolicyDecision, ...]:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT decision
                            FROM plugin_policy_decisions
                            WHERE tenant_id = :tenant_id
                            ORDER BY decided_at DESC, id DESC
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(PluginPolicyDecision.model_validate(row["decision"]) for row in rows)

    async def frozen_resolution(
        self,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        revision: int,
    ) -> dict[str, object] | None:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            value = await connection.scalar(
                text(
                    """
                    SELECT revisions.plugin_resolution
                    FROM flow_revisions AS revisions
                    JOIN flows ON flows.id = revisions.flow_id
                                   AND flows.tenant_id = revisions.tenant_id
                    JOIN namespaces ON namespaces.id = flows.namespace_id
                    WHERE revisions.tenant_id = :tenant_id
                      AND namespaces.name = :namespace
                      AND flows.flow_key = :flow_id
                      AND revisions.revision = :revision
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "flow_id": flow_id,
                    "revision": revision,
                },
            )
        return dict(value) if isinstance(value, dict) else None

    async def migrate_legacy_resolution(
        self,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        expected: dict[str, object],
        replacement: dict[str, object],
        actor_id: str,
    ) -> dict[str, object]:
        """Replace one legacy unpinned payload with an exact resolver result once."""

        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            revision_id = await connection.scalar(
                text(
                    """
                    UPDATE flow_revisions AS revisions
                    SET plugin_resolution = CAST(:replacement AS jsonb)
                    FROM flows, namespaces
                    WHERE revisions.flow_id = flows.id
                      AND revisions.tenant_id = flows.tenant_id
                      AND namespaces.id = flows.namespace_id
                      AND namespaces.tenant_id = flows.tenant_id
                      AND revisions.tenant_id = :tenant_id
                      AND namespaces.name = :namespace
                      AND flows.flow_key = :flow_id
                      AND revisions.revision = :revision
                      AND revisions.plugin_resolution = CAST(:expected AS jsonb)
                    RETURNING revisions.id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "flow_id": flow_id,
                    "revision": revision,
                    "expected": json.dumps(expected),
                    "replacement": json.dumps(replacement),
                },
            )
            if revision_id is None:
                current = await connection.scalar(
                    text(
                        """
                        SELECT revisions.plugin_resolution
                        FROM flow_revisions AS revisions
                        JOIN flows ON flows.id = revisions.flow_id
                                  AND flows.tenant_id = revisions.tenant_id
                        JOIN namespaces ON namespaces.id = flows.namespace_id
                                       AND namespaces.tenant_id = flows.tenant_id
                        WHERE revisions.tenant_id = :tenant_id
                          AND namespaces.name = :namespace
                          AND flows.flow_key = :flow_id
                          AND revisions.revision = :revision
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": namespace,
                        "flow_id": flow_id,
                        "revision": revision,
                    },
                )
                if current == replacement:
                    return replacement
                raise RuntimeError("plugin resolution changed during compatibility migration")
            expected_digest = hashlib.sha256(
                json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            replacement_digest = hashlib.sha256(
                json.dumps(replacement, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.resolution.migrate",
                resource_id=str(revision_id),
                reason="legacy plugin resolution upgraded to an exact v1 pin",
                evidence={
                    "namespace": namespace,
                    "flowId": flow_id,
                    "revision": revision,
                    "legacyDigest": expected_digest,
                    "resolutionDigest": replacement_digest,
                },
            )
        return replacement

    async def quarantine_legacy_resolution(
        self,
        tenant_id: str,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        expected: dict[str, object],
        actor_id: str,
        reason: str,
    ) -> bool:
        """Disable one flow whose legacy pin cannot be resolved, with one audit event."""

        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            revision_id = await connection.scalar(
                text(
                    """
                    WITH target AS (
                        SELECT flows.id AS flow_resource_id, revisions.id AS revision_id
                        FROM flow_revisions AS revisions
                        JOIN flows ON flows.id = revisions.flow_id
                                  AND flows.tenant_id = revisions.tenant_id
                        JOIN namespaces ON namespaces.id = flows.namespace_id
                                       AND namespaces.tenant_id = flows.tenant_id
                        WHERE revisions.tenant_id = :tenant_id
                          AND namespaces.name = :namespace
                          AND flows.flow_key = :flow_id
                          AND revisions.revision = :revision
                          AND revisions.plugin_resolution = CAST(:expected AS jsonb)
                          AND flows.status <> 'DISABLED'
                        FOR UPDATE OF flows, revisions
                    )
                    UPDATE flows
                    SET status = 'DISABLED',
                        version = flows.version + 1,
                        updated_by = :actor_id,
                        updated_at = clock_timestamp()
                    FROM target
                    WHERE flows.id = target.flow_resource_id
                    RETURNING target.revision_id
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "namespace": namespace,
                    "flow_id": flow_id,
                    "revision": revision,
                    "expected": json.dumps(expected),
                    "actor_id": actor_id,
                },
            )
            if revision_id is None:
                current = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT revisions.plugin_resolution, flows.status
                                FROM flow_revisions AS revisions
                                JOIN flows ON flows.id = revisions.flow_id
                                          AND flows.tenant_id = revisions.tenant_id
                                JOIN namespaces ON namespaces.id = flows.namespace_id
                                               AND namespaces.tenant_id = flows.tenant_id
                                WHERE revisions.tenant_id = :tenant_id
                                  AND namespaces.name = :namespace
                                  AND flows.flow_key = :flow_id
                                  AND revisions.revision = :revision
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
                    .one_or_none()
                )
                if current is not None and current["plugin_resolution"] == expected:
                    return bool(current["status"] == "DISABLED")
                raise RuntimeError("plugin resolution changed during compatibility quarantine")
            legacy_digest = hashlib.sha256(
                json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            await _write_audit(
                connection,
                tenant_uuid,
                actor_id=actor_id,
                action="plugin.resolution.quarantine",
                resource_id=str(revision_id),
                reason="legacy plugin resolution could not be upgraded; flow disabled",
                evidence={
                    "namespace": namespace,
                    "flowId": flow_id,
                    "revision": revision,
                    "legacyDigest": legacy_digest,
                    "failure": reason[:2048],
                },
            )
        return True

    async def impact_preview(
        self,
        tenant_id: str,
        request: PluginQuarantineCreate,
    ) -> PluginPolicyImpactPreview:
        namespace_clause = (
            "AND namespaces.name = :namespace"
            if request.scope is PluginPolicyScope.NAMESPACE
            else ""
        )
        params: dict[str, object] = {
            "package": request.package,
            "version": request.version,
            "namespace": request.namespace,
        }
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            params["tenant_id"] = tenant_uuid
            flows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT namespaces.name AS namespace, flows.flow_key,
                                   revisions.revision, flows.status,
                                   flows.active_revision = revisions.revision AS active
                            FROM flow_revisions AS revisions
                            JOIN flows ON flows.id = revisions.flow_id
                                           AND flows.tenant_id = revisions.tenant_id
                            JOIN namespaces ON namespaces.id = flows.namespace_id
                            WHERE revisions.tenant_id = :tenant_id
                              {namespace_clause}
                              AND revisions.plugin_resolution @> jsonb_build_object(
                                  'packages', jsonb_build_array(jsonb_build_object(
                                      'name', CAST(:package AS text),
                                      'version', CAST(:version AS text)
                                  ))
                              )
                            ORDER BY namespaces.name, flows.flow_key, revisions.revision
                            """
                        ),
                        params,
                    )
                )
                .mappings()
                .all()
            )
            executions = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT executions.id, executions.namespace_name AS namespace,
                                   executions.flow_key, revisions.revision,
                                   executions.state, executions.created_at
                            FROM executions
                            JOIN flow_revisions AS revisions
                              ON revisions.id = executions.flow_revision_id
                             AND revisions.tenant_id = executions.tenant_id
                            JOIN flows ON flows.id = revisions.flow_id
                            JOIN namespaces ON namespaces.id = flows.namespace_id
                            WHERE executions.tenant_id = :tenant_id
                              AND executions.state = 'RUNNING'
                              {namespace_clause}
                              AND revisions.plugin_resolution @> jsonb_build_object(
                                  'packages', jsonb_build_array(jsonb_build_object(
                                      'name', CAST(:package AS text),
                                      'version', CAST(:version AS text)
                                  ))
                              )
                            ORDER BY executions.created_at, executions.id
                            """
                        ),
                        params,
                    )
                )
                .mappings()
                .all()
            )
        return PluginPolicyImpactPreview(
            package=request.package,
            version=request.version,
            affectedFlows=tuple(_json_row(row) for row in flows),
            runningExecutions=tuple(_json_row(row) for row in executions),
        )

    async def _load_rules(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        tenant_id: str,
        namespace: str | None,
    ) -> tuple[PluginPolicyRule, ...]:
        rows = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT *
                        FROM plugin_policy_rules
                        WHERE (tenant_id IS NULL OR tenant_id = :tenant_id)
                          AND (scope <> 'NAMESPACE' OR namespace_name = :namespace)
                        ORDER BY
                            CASE scope
                                WHEN 'NAMESPACE' THEN 3
                                WHEN 'TENANT' THEN 2
                                ELSE 1
                            END DESC,
                            priority DESC,
                            id
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace},
                )
            )
            .mappings()
            .all()
        )
        return tuple(_rule(row, tenant_id) for row in rows)

    async def _load_quarantines(
        self,
        connection: AsyncConnection,
        tenant_uuid: UUID,
        tenant_id: str,
        namespace: str | None,
    ) -> tuple[PluginQuarantine, ...]:
        rows = (
            (
                await connection.execute(
                    text(
                        """
                        SELECT *
                        FROM plugin_quarantines
                        WHERE (tenant_id IS NULL OR tenant_id = :tenant_id)
                          AND (scope <> 'NAMESPACE' OR namespace_name = :namespace)
                        ORDER BY created_at DESC, id
                        """
                    ),
                    {"tenant_id": tenant_uuid, "namespace": namespace},
                )
            )
            .mappings()
            .all()
        )
        return tuple(_quarantine(row, tenant_id) for row in rows)


def _scoped_tenant_uuid(scope: PluginPolicyScope, tenant_uuid: UUID) -> UUID | None:
    return None if scope is PluginPolicyScope.INSTANCE else tenant_uuid


def _rule_parameters(
    rule_id: UUID,
    tenant_uuid: UUID,
    request: PluginPolicyRuleCreate,
    *,
    actor_id: str,
) -> dict[str, object]:
    return {
        "id": rule_id,
        "rule_tenant_id": _scoped_tenant_uuid(request.scope, tenant_uuid),
        "namespace": request.namespace,
        "scope": request.scope.value,
        "effect": request.effect.value,
        "stages": [stage.value for stage in request.stages],
        "package": request.selector.package,
        "version_range": request.selector.version_range,
        "vendor": request.selector.vendor,
        "plugin_types": list(request.selector.plugin_types),
        "capabilities": list(request.selector.capabilities),
        "priority": request.priority,
        "reason": request.reason,
        "enabled": request.enabled,
        "actor_id": actor_id,
    }


def _rule(row: RowMapping, tenant_id: str) -> PluginPolicyRule:
    return PluginPolicyRule(
        id=row["id"],
        tenantId=None if row["tenant_id"] is None else tenant_id,
        scope=row["scope"],
        namespace=row["namespace_name"],
        effect=row["effect"],
        stages=tuple(PluginPolicyStage(value) for value in row["stages"]),
        selector=PluginPolicySelector(
            package=row["package_pattern"],
            versionRange=row["version_range"],
            vendor=row["vendor_pattern"],
            pluginTypes=tuple(row["plugin_types"]),
            capabilities=tuple(row["capabilities"]),
        ),
        priority=row["priority"],
        reason=row["reason"],
        enabled=row["enabled"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        updatedBy=row["updated_by"],
        updatedAt=row["updated_at"],
    )


def _quarantine(row: RowMapping, tenant_id: str) -> PluginQuarantine:
    return PluginQuarantine(
        id=row["id"],
        tenantId=None if row["tenant_id"] is None else tenant_id,
        scope=row["scope"],
        namespace=row["namespace_name"],
        package=row["package_name"],
        version=row["version"],
        reason=row["reason"],
        state=PluginQuarantineState(row["state"]),
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        releasedBy=row["released_by"],
        releasedAt=row["released_at"],
    )


async def _write_audit(
    connection: AsyncConnection,
    tenant_uuid: UUID,
    *,
    actor_id: str,
    action: str,
    resource_id: str | None,
    reason: str,
    outcome: str = "SUCCESS",
    evidence: dict[str, object] | None = None,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, 'plugin_policy', :resource_id,
                :outcome, :reason, :correlation_id,
                '{"component":"plugin-policy-repository"}'::jsonb,
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_uuid,
            "actor_id": actor_id,
            "action": action,
            "resource_id": resource_id,
            "outcome": outcome,
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "evidence": json.dumps(evidence or {}),
            "occurred_at": datetime.now(UTC),
        },
    )


def _json_row(row: RowMapping) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in row.items():
        if isinstance(value, (UUID, datetime)):
            result[key] = str(value)
        else:
            result[key] = value
    return result
