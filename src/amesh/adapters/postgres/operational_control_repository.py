from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.adapters.postgres.tenant_context import tenant_admin_transaction
from amesh.domain import (
    Announcement,
    AnnouncementAudience,
    AnnouncementCreateRequest,
    OperationalBoundary,
    OperationalControl,
    OperationalControlAcknowledgement,
    OperationalControlActionKind,
    OperationalControlActionRequest,
    OperationalControlCreateRequest,
    OperationalControlDecision,
    OperationalControlEvent,
    OperationalControlScope,
    OperationalControlState,
    RunningWorkPolicy,
    new_runtime_id,
)
from amesh.ports.errors import OperationalControlVersionConflict
from amesh.ports.operational_controls import OperationalControlRepository

_CONTROL_COLUMNS = """
    c.control_id,
    c.tenant_id,
    t.slug AS tenant_slug,
    c.kind,
    c.control_name,
    c.scope,
    c.namespace_name,
    c.flow_id,
    c.plugin_id,
    c.runner_id,
    c.boundaries,
    c.running_work_policy,
    c.reason,
    CASE
        WHEN c.state = 'ACTIVE' AND c.bypass_until > clock_timestamp() THEN 'BYPASSED'
        ELSE c.state
    END AS effective_state,
    c.version,
    c.expires_at,
    c.review_at,
    c.bypass_until,
    c.bypass_reason,
    c.created_by,
    c.updated_by,
    c.created_at,
    c.updated_at
"""


class PostgresOperationalControlRepository(OperationalControlRepository):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_announcement(
        self,
        request: AnnouncementCreateRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> Announcement:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = (
                None
                if request.audience is AnnouncementAudience.INSTANCE
                else await _resolve_tenant_uuid(connection, tenant_id)
            )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO announcements (
                                announcement_id, tenant_id, title, message, severity,
                                audience, namespace_name, starts_at, expires_at,
                                created_by, updated_by
                            ) VALUES (
                                :announcement_id, :tenant_id, :title, :message, :severity,
                                :audience, :namespace, :starts_at, :expires_at,
                                :actor_id, :actor_id
                            )
                            RETURNING *
                            """
                        ),
                        {
                            "announcement_id": new_runtime_id(),
                            "tenant_id": tenant_uuid,
                            "title": request.title,
                            "message": request.message,
                            "severity": request.severity.value,
                            "audience": request.audience.value,
                            "namespace": request.namespace,
                            "starts_at": request.starts_at,
                            "expires_at": request.expires_at,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
        return _to_announcement(row, tenant_slug=None if tenant_uuid is None else tenant_id)

    async def list_announcements(
        self,
        tenant_id: str,
        *,
        namespace: str | None = None,
        include_inactive: bool = False,
    ) -> tuple[Announcement, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT a.*, t.slug AS tenant_slug,
                                   (
                                       a.active
                                       AND a.starts_at <= clock_timestamp()
                                       AND a.expires_at > clock_timestamp()
                                   ) AS effective_active
                            FROM announcements a
                            LEFT JOIN tenants t ON t.id = a.tenant_id
                            WHERE (a.tenant_id IS NULL OR a.tenant_id = :tenant_id)
                              AND (
                                  a.audience <> 'NAMESPACE'
                                  OR a.namespace_name = :namespace
                              )
                              AND (
                                  :include_inactive
                                  OR (
                                      a.active
                                      AND a.starts_at <= clock_timestamp()
                                      AND a.expires_at > clock_timestamp()
                                  )
                              )
                            ORDER BY
                                CASE a.severity
                                    WHEN 'CRITICAL' THEN 1
                                    WHEN 'WARNING' THEN 2
                                    ELSE 3
                                END,
                                a.starts_at DESC,
                                a.announcement_id
                            """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "include_inactive": include_inactive,
                        },
                    )
                )
                .mappings()
                .all()
            )
        return tuple(_to_announcement(row) for row in rows)

    async def deactivate_announcement(
        self,
        announcement_id: UUID,
        *,
        tenant_id: str,
        actor_id: str,
        expected_version: int,
    ) -> Announcement:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE announcements
                            SET active = false,
                                version = version + 1,
                                updated_by = :actor_id,
                                updated_at = clock_timestamp()
                            WHERE announcement_id = :announcement_id
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                              AND version = :expected_version
                            RETURNING *
                            """
                        ),
                        {
                            "announcement_id": announcement_id,
                            "tenant_id": tenant_uuid,
                            "actor_id": actor_id,
                            "expected_version": expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise OperationalControlVersionConflict("announcement version changed")
        return _to_announcement(row, tenant_slug=None if row["tenant_id"] is None else tenant_id)

    async def create_control(
        self,
        request: OperationalControlCreateRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> OperationalControl:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = (
                None
                if request.scope is OperationalControlScope.INSTANCE
                else await _resolve_tenant_uuid(connection, tenant_id)
            )
            control_id = new_runtime_id()
            row = (
                (
                    await connection.execute(
                        text(
                            """
                            INSERT INTO operational_controls (
                                control_id, tenant_id, kind, control_name, scope,
                                namespace_name, flow_id, plugin_id, runner_id,
                                boundaries, running_work_policy, reason, expires_at,
                                review_at, created_by, updated_by
                            ) VALUES (
                                :control_id, :tenant_id, :kind, :control_name, :scope,
                                :namespace, :flow_id, :plugin_id, :runner_id,
                                :boundaries, :running_work_policy, :reason, :expires_at,
                                :review_at, :actor_id, :actor_id
                            )
                            RETURNING *
                            """
                        ).bindparams(bindparam("boundaries")),
                        {
                            "control_id": control_id,
                            "tenant_id": tenant_uuid,
                            "kind": request.kind.value,
                            "control_name": request.name,
                            "scope": request.scope.value,
                            "namespace": request.namespace,
                            "flow_id": request.flow_id,
                            "plugin_id": request.plugin_id,
                            "runner_id": request.runner_id,
                            "boundaries": [item.value for item in request.boundaries],
                            "running_work_policy": request.running_work_policy.value,
                            "reason": request.reason,
                            "expires_at": request.expires_at,
                            "review_at": request.review_at,
                            "actor_id": actor_id,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _insert_event(
                connection,
                control_id=control_id,
                tenant_id=tenant_uuid,
                action="ACTIVATE",
                actor_id=actor_id,
                reason=request.reason,
                evidence={
                    "kind": request.kind.value,
                    "scope": request.scope.value,
                    "boundaries": [item.value for item in request.boundaries],
                    "runningWorkPolicy": request.running_work_policy.value,
                    "version": 1,
                },
            )
        return _to_control(row, tenant_slug=None if tenant_uuid is None else tenant_id)

    async def list_controls(self, tenant_id: str) -> tuple[OperationalControl, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            await _expire_due(connection)
            rows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_CONTROL_COLUMNS}
                            FROM operational_controls c
                            LEFT JOIN tenants t ON t.id = c.tenant_id
                            WHERE c.tenant_id IS NULL OR c.tenant_id = :tenant_id
                            ORDER BY c.updated_at DESC, c.control_id
                            """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            acknowledgements = await _acknowledgements(
                connection, [row["control_id"] for row in rows]
            )
        return tuple(
            _to_control(row, acknowledgements.get(UUID(str(row["control_id"])), ())) for row in rows
        )

    async def get_control(
        self,
        control_id: UUID,
        *,
        tenant_id: str,
    ) -> OperationalControl:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            await _expire_due(connection)
            row = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_CONTROL_COLUMNS}
                            FROM operational_controls c
                            LEFT JOIN tenants t ON t.id = c.tenant_id
                            WHERE c.control_id = :control_id
                              AND (c.tenant_id IS NULL OR c.tenant_id = :tenant_id)
                            """
                        ),
                        {"control_id": control_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("operational control not found")
            acknowledgements = await _acknowledgements(connection, [control_id])
        return _to_control(row, acknowledgements.get(control_id, ()))

    async def apply_action(
        self,
        control_id: UUID,
        request: OperationalControlActionRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> OperationalControl:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            await _expire_due(connection)
            existing = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM operational_controls
                            WHERE control_id = :control_id
                              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
                            FOR UPDATE
                            """
                        ),
                        {"control_id": control_id, "tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is None:
                raise LookupError("operational control not found")
            if int(existing["version"]) != request.expected_version:
                raise OperationalControlVersionConflict("operational control version changed")
            if existing["state"] != "ACTIVE":
                raise ValueError("only active controls can be changed")

            if request.action is OperationalControlActionKind.EXTEND:
                values = {
                    "expires_at": request.expires_at or existing["expires_at"],
                    "review_at": request.review_at or existing["review_at"],
                    "bypass_until": existing["bypass_until"],
                    "bypass_reason": existing["bypass_reason"],
                    "state": "ACTIVE",
                }
            elif request.action is OperationalControlActionKind.BYPASS:
                values = {
                    "expires_at": existing["expires_at"],
                    "review_at": existing["review_at"],
                    "bypass_until": request.bypass_until,
                    "bypass_reason": request.reason,
                    "state": "ACTIVE",
                }
            else:
                values = {
                    "expires_at": existing["expires_at"],
                    "review_at": existing["review_at"],
                    "bypass_until": None,
                    "bypass_reason": None,
                    "state": "DEACTIVATED",
                }

            row = (
                (
                    await connection.execute(
                        text(
                            """
                            UPDATE operational_controls
                            SET expires_at = :expires_at,
                                review_at = :review_at,
                                bypass_until = :bypass_until,
                                bypass_reason = :bypass_reason,
                                state = :state,
                                reason = :reason,
                                version = version + 1,
                                updated_by = :actor_id,
                                updated_at = clock_timestamp()
                            WHERE control_id = :control_id
                              AND version = :expected_version
                            RETURNING *
                            """
                        ),
                        {
                            **values,
                            "reason": request.reason,
                            "actor_id": actor_id,
                            "control_id": control_id,
                            "expected_version": request.expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise OperationalControlVersionConflict("operational control version changed")
            await _insert_event(
                connection,
                control_id=control_id,
                tenant_id=existing["tenant_id"],
                action=request.action.value,
                actor_id=actor_id,
                reason=request.reason,
                evidence={
                    "version": int(row["version"]),
                    "expiresAt": (
                        row["expires_at"].isoformat() if row["expires_at"] is not None else None
                    ),
                    "reviewAt": (
                        row["review_at"].isoformat() if row["review_at"] is not None else None
                    ),
                    "bypassUntil": (
                        row["bypass_until"].isoformat() if row["bypass_until"] is not None else None
                    ),
                },
            )
        return _to_control(
            row,
            tenant_slug=None if row["tenant_id"] is None else tenant_id,
        )

    async def evaluate(
        self,
        boundary: OperationalBoundary,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        plugin_ids: Sequence[str] = (),
        runner_ids: Sequence[str] = (),
        component_id: str | None = None,
        component_role: str | None = None,
    ) -> OperationalControlDecision:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            await _expire_due(connection)
            rows = (
                (
                    await connection.execute(
                        text(
                            f"""
                            SELECT {_CONTROL_COLUMNS}
                            FROM operational_controls c
                            LEFT JOIN tenants t ON t.id = c.tenant_id
                            WHERE c.state = 'ACTIVE'
                              AND (c.expires_at IS NULL OR c.expires_at > clock_timestamp())
                              AND (c.bypass_until IS NULL OR c.bypass_until <= clock_timestamp())
                              AND :boundary = ANY(c.boundaries)
                              AND (
                                  c.scope = 'INSTANCE'
                                  OR (c.scope = 'TENANT' AND c.tenant_id = :tenant_id)
                                  OR (
                                      c.scope = 'NAMESPACE'
                                      AND c.tenant_id = :tenant_id
                                      AND c.namespace_name = :namespace
                                  )
                                  OR (
                                      c.scope = 'FLOW'
                                      AND c.tenant_id = :tenant_id
                                      AND c.namespace_name = :namespace
                                      AND c.flow_id = :flow_id
                                  )
                                  OR (
                                      c.scope = 'PLUGIN'
                                      AND c.tenant_id = :tenant_id
                                      AND c.plugin_id = ANY(CAST(:plugin_ids AS text[]))
                                  )
                                  OR (
                                      c.scope = 'RUNNER'
                                      AND c.tenant_id = :tenant_id
                                      AND c.runner_id = ANY(CAST(:runner_ids AS text[]))
                                  )
                              )
                            ORDER BY
                                CASE c.running_work_policy
                                    WHEN 'CANCEL' THEN 1
                                    WHEN 'DRAIN' THEN 2
                                    ELSE 3
                                END,
                                c.updated_at DESC
                            """
                        ),
                        {
                            "boundary": boundary.value,
                            "tenant_id": tenant_uuid,
                            "namespace": namespace,
                            "flow_id": flow_id,
                            "plugin_ids": list(plugin_ids),
                            "runner_ids": list(runner_ids),
                        },
                    )
                )
                .mappings()
                .all()
            )
            if rows and component_id is not None and component_role is not None:
                await _acknowledge_rows(
                    connection,
                    rows,
                    component_id=component_id,
                    component_role=component_role,
                )
            acknowledgements = await _acknowledgements(
                connection, [row["control_id"] for row in rows]
            )
        controls = tuple(
            _to_control(row, acknowledgements.get(UUID(str(row["control_id"])), ())) for row in rows
        )
        policy = controls[0].running_work_policy if controls else RunningWorkPolicy.CONTINUE
        return OperationalControlDecision(
            blocked=bool(controls),
            boundary=boundary,
            runningWorkPolicy=policy,
            controls=controls,
        )

    async def acknowledge_active(
        self,
        *,
        tenant_ids: Sequence[str],
        component_id: str,
        component_role: str,
    ) -> int:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuids = [
                await _resolve_tenant_uuid(connection, tenant_id) for tenant_id in tenant_ids
            ]
            await _expire_due(connection)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT *
                            FROM operational_controls
                            WHERE state = 'ACTIVE'
                              AND (expires_at IS NULL OR expires_at > clock_timestamp())
                              AND (tenant_id IS NULL OR tenant_id = ANY(CAST(:tenant_ids AS uuid[])))
                            """
                        ),
                        {"tenant_ids": tenant_uuids},
                    )
                )
                .mappings()
                .all()
            )
            await _acknowledge_rows(
                connection,
                rows,
                component_id=component_id,
                component_role=component_role,
            )
        return len(rows)

    async def list_events(
        self,
        tenant_id: str,
        *,
        limit: int = 200,
    ) -> tuple[OperationalControlEvent, ...]:
        async with tenant_admin_transaction(self._engine) as connection:
            tenant_uuid = await _resolve_tenant_uuid(connection, tenant_id)
            await _expire_due(connection)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                            SELECT event_id, control_id, action, actor_id, reason,
                                   evidence, occurred_at
                            FROM operational_control_events
                            WHERE tenant_id IS NULL OR tenant_id = :tenant_id
                            ORDER BY occurred_at DESC, event_id DESC
                            LIMIT :limit
                            """
                        ),
                        {"tenant_id": tenant_uuid, "limit": limit},
                    )
                )
                .mappings()
                .all()
            )
        return tuple(
            OperationalControlEvent(
                eventId=row["event_id"],
                controlId=row["control_id"],
                action=row["action"],
                actorId=row["actor_id"],
                reason=row["reason"],
                evidence=dict(row["evidence"]),
                occurredAt=row["occurred_at"],
            )
            for row in rows
        )


async def _resolve_tenant_uuid(connection: AsyncConnection, tenant_slug: str) -> UUID:
    value = await connection.scalar(
        text("SELECT id FROM tenants WHERE slug = :tenant_slug AND status = 'ACTIVE'"),
        {"tenant_slug": tenant_slug},
    )
    if value is None:
        raise LookupError("tenant unavailable")
    return UUID(str(value))


async def _expire_due(connection: AsyncConnection) -> None:
    rows = (
        (
            await connection.execute(
                text(
                    """
                    UPDATE operational_controls
                    SET state = 'EXPIRED',
                        version = version + 1,
                        updated_by = 'system:control-expiry',
                        updated_at = clock_timestamp()
                    WHERE state = 'ACTIVE'
                      AND expires_at IS NOT NULL
                      AND expires_at <= clock_timestamp()
                    RETURNING control_id, tenant_id, version, expires_at
                    """
                )
            )
        )
        .mappings()
        .all()
    )
    for row in rows:
        await _insert_event(
            connection,
            control_id=row["control_id"],
            tenant_id=row["tenant_id"],
            action="EXPIRE",
            actor_id="system:control-expiry",
            reason="configured operational control expiry reached",
            evidence={
                "version": int(row["version"]),
                "expiresAt": row["expires_at"].isoformat(),
            },
        )


async def _insert_event(
    connection: AsyncConnection,
    *,
    control_id: UUID,
    tenant_id: UUID | None,
    action: str,
    actor_id: str,
    reason: str,
    evidence: dict[str, object],
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO operational_control_events (
                event_id, control_id, tenant_id, action, actor_id, reason, evidence
            ) VALUES (
                :event_id, :control_id, :tenant_id, :action, :actor_id, :reason,
                CAST(:evidence AS jsonb)
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "control_id": control_id,
            "tenant_id": tenant_id,
            "action": action,
            "actor_id": actor_id,
            "reason": reason,
            "evidence": json.dumps(evidence),
        },
    )


async def _acknowledge_rows(
    connection: AsyncConnection,
    rows: Sequence[RowMapping],
    *,
    component_id: str,
    component_role: str,
) -> None:
    for row in rows:
        await connection.execute(
            text(
                """
                INSERT INTO operational_control_acknowledgements (
                    control_id, tenant_id, component_id, component_role,
                    control_version, acknowledged_at
                ) VALUES (
                    :control_id, :tenant_id, :component_id, :component_role,
                    :control_version, clock_timestamp()
                )
                ON CONFLICT (control_id, component_id) DO UPDATE SET
                    component_role = EXCLUDED.component_role,
                    control_version = EXCLUDED.control_version,
                    acknowledged_at = EXCLUDED.acknowledged_at
                """
            ),
            {
                "control_id": row["control_id"],
                "tenant_id": row["tenant_id"],
                "component_id": component_id,
                "component_role": component_role,
                "control_version": row["version"],
            },
        )


async def _acknowledgements(
    connection: AsyncConnection,
    control_ids: Sequence[UUID],
) -> dict[UUID, tuple[OperationalControlAcknowledgement, ...]]:
    if not control_ids:
        return {}
    rows = (
        (
            await connection.execute(
                text(
                    """
                    SELECT control_id, component_id, component_role,
                           control_version, acknowledged_at
                    FROM operational_control_acknowledgements
                    WHERE control_id = ANY(CAST(:control_ids AS uuid[]))
                    ORDER BY component_role, component_id
                    """
                ),
                {"control_ids": list(control_ids)},
            )
        )
        .mappings()
        .all()
    )
    grouped: dict[UUID, list[OperationalControlAcknowledgement]] = {}
    for row in rows:
        grouped.setdefault(UUID(str(row["control_id"])), []).append(
            OperationalControlAcknowledgement(
                componentId=row["component_id"],
                componentRole=row["component_role"],
                controlVersion=row["control_version"],
                acknowledgedAt=row["acknowledged_at"],
            )
        )
    return {control_id: tuple(items) for control_id, items in grouped.items()}


def _to_announcement(
    row: RowMapping,
    *,
    tenant_slug: str | None = None,
) -> Announcement:
    effective_active = row.get("effective_active")
    if effective_active is None:
        now = datetime.now(UTC)
        effective_active = bool(row["active"]) and row["starts_at"] <= now < row["expires_at"]
    return Announcement(
        id=row["announcement_id"],
        tenantId=tenant_slug if tenant_slug is not None else row.get("tenant_slug"),
        title=row["title"],
        message=row["message"],
        severity=row["severity"],
        audience=row["audience"],
        namespace=row["namespace_name"],
        startsAt=row["starts_at"],
        expiresAt=row["expires_at"],
        active=bool(effective_active),
        version=row["version"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )


def _to_control(
    row: RowMapping,
    acknowledgements: tuple[OperationalControlAcknowledgement, ...] = (),
    *,
    tenant_slug: str | None = None,
) -> OperationalControl:
    state = row["effective_state"] if "effective_state" in row else row["state"]
    if (
        state == OperationalControlState.ACTIVE.value
        and row["bypass_until"] is not None
        and row["bypass_until"] > datetime.now(UTC)
    ):
        state = OperationalControlState.BYPASSED.value
    return OperationalControl(
        id=row["control_id"],
        tenantId=tenant_slug if tenant_slug is not None else row.get("tenant_slug"),
        kind=row["kind"],
        name=row["control_name"],
        scope=row["scope"],
        namespace=row["namespace_name"],
        flowId=row["flow_id"],
        pluginId=row["plugin_id"],
        runnerId=row["runner_id"],
        boundaries=tuple(row["boundaries"]),
        runningWorkPolicy=row["running_work_policy"],
        reason=row["reason"],
        state=state,
        version=row["version"],
        expiresAt=row["expires_at"],
        reviewAt=row["review_at"],
        bypassUntil=row["bypass_until"],
        bypassReason=row["bypass_reason"],
        createdBy=row["created_by"],
        updatedBy=row["updated_by"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
        acknowledgements=acknowledgements,
    )


__all__ = ["OperationalControlVersionConflict", "PostgresOperationalControlRepository"]
