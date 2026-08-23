from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from amesh.domain import SYSTEM_TENANT_ID, new_runtime_id
from amesh.domain.audit import (
    AuditEvent,
    AuditEventPage,
    AuditExportReceipt,
    AuditIntegrityReport,
    AuditLegalHold,
    AuditLegalHoldCreate,
    AuditRetentionPolicy,
    AuditRetentionResult,
    ComplianceEvidenceCategory,
    ComplianceEvidenceCreate,
    ComplianceEvidenceRecord,
    ComplianceSnapshot,
)
from amesh.domain.authorization import AuthorizationDecision, AuthorizationRequest
from amesh.ports.audit_repository import AuditRepository, AuthorizationDecisionAuditSink


class PostgresAuditRepository(AuditRepository, AuthorizationDecisionAuditSink):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def record_authorization_decision(
        self,
        request: AuthorizationRequest,
        decision: AuthorizationDecision,
    ) -> None:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, request.tenant_id)
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=str(request.actor.principal_id),
                action=f"authorization.{request.resource_type}.{request.action.value}",
                resource_type=request.resource_type,
                resource_id=request.namespace or request.tenant_id,
                outcome="SUCCESS" if decision.allowed else "DENIED",
                reason=decision.reason_code,
                evidence={
                    "policyVersion": decision.policy_version,
                    "matchedRoles": list(decision.matched_role_names),
                    "audience": request.audience,
                },
                source={"component": "authorization-service"},
            )

    async def list_events(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        cursor: int | None = None,
        limit: int = 100,
        action: str | None = None,
        resource_type: str | None = None,
        outcome: str | None = None,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
        record_access: bool = True,
    ) -> AuditEventPage:
        clauses = ["tenants.slug = :tenant_slug"]
        params: dict[str, object] = {"tenant_slug": tenant_id, "limit": limit}
        for value, clause, name in (
            (cursor, "events.id < :cursor", "cursor"),
            (action, "events.action = :action", "action"),
            (resource_type, "events.resource_type = :resource_type", "resource_type"),
            (outcome, "events.outcome = :outcome", "outcome"),
            (occurred_from, "events.occurred_at >= :occurred_from", "occurred_from"),
            (occurred_to, "events.occurred_at < :occurred_to", "occurred_to"),
        ):
            if value is not None:
                clauses.append(clause)
                params[name] = value
        query = text(
            f"""
            SELECT events.id, events.event_id, tenants.slug AS tenant_slug,
                   events.actor_id, events.delegated_actor_id, events.action,
                   events.resource_type, events.resource_id, events.outcome, events.reason,
                   events.correlation_id, events.trace_id, events.source, events.evidence,
                   events.occurred_at, events.previous_hash, events.event_hash,
                   events.retention_until
            FROM audit_events AS events
            JOIN tenants ON tenants.id = events.tenant_id
            WHERE {" AND ".join(clauses)}
            ORDER BY events.id DESC
            LIMIT :limit
            """
        )
        async with self._engine.begin() as connection:
            rows = (await connection.execute(query, params)).mappings().all()
            if record_access:
                tenant_uuid = await _tenant_uuid(connection, tenant_id)
                await _write_audit(
                    connection,
                    tenant_id=tenant_uuid,
                    actor_id=actor_id,
                    action="audit.read",
                    resource_type="audit",
                    resource_id=tenant_id,
                    evidence={"returned": len(rows)},
                    source={"component": "audit-repository"},
                )
        items = tuple(_audit_event(row) for row in rows)
        return AuditEventPage(
            items=items,
            nextCursor=items[-1].cursor if len(items) == limit else None,
        )

    async def verify_integrity(self, tenant_id: str, *, actor_id: str) -> AuditIntegrityReport:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            anchor = await connection.scalar(
                text("SELECT previous_hash FROM audit_chain_anchors WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_uuid},
            )
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT event_id, previous_hash, event_hash,
                               amesh_compute_audit_hash(events) AS expected_hash
                        FROM audit_events AS events
                        WHERE tenant_id = :tenant_id
                        ORDER BY id
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            expected_previous = str(anchor) if anchor is not None else None
            broken: RowMapping | None = None
            reason: str | None = None
            for row in rows:
                if row["previous_hash"] != expected_previous:
                    broken = row
                    reason = "CHAIN_GAP"
                    break
                if row["event_hash"] != row["expected_hash"]:
                    broken = row
                    reason = "HASH_MISMATCH"
                    break
                expected_previous = str(row["event_hash"])
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.integrity.verify",
                resource_type="audit",
                resource_id=tenant_id,
                outcome="SUCCESS" if broken is None else "FAILED",
                reason="verified" if broken is None else reason,
                evidence={"checkedEvents": len(rows)},
                source={"component": "audit-repository"},
            )
        return AuditIntegrityReport(
            valid=broken is None,
            checkedEvents=len(rows),
            anchorHash=anchor,
            headHash=rows[-1]["event_hash"] if rows else anchor,
            firstBrokenEventId=broken["event_id"] if broken is not None else None,
            reason=reason,
        )

    async def get_retention_policy(self, tenant_id: str) -> AuditRetentionPolicy:
        async with self._engine.connect() as connection:
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT policies.retention_days, policies.updated_by, policies.updated_at
                        FROM tenants
                        LEFT JOIN audit_retention_policies AS policies
                          ON policies.tenant_id = tenants.id
                        WHERE tenants.slug = :tenant_slug
                        """
                        ),
                        {"tenant_slug": tenant_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError("tenant unavailable")
        if row["retention_days"] is None:
            return AuditRetentionPolicy()
        return AuditRetentionPolicy(
            retentionDays=row["retention_days"],
            updatedBy=row["updated_by"],
            updatedAt=row["updated_at"],
        )

    async def set_retention_policy(
        self,
        tenant_id: str,
        policy: AuditRetentionPolicy,
        *,
        actor_id: str,
    ) -> AuditRetentionPolicy:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO audit_retention_policies (
                            tenant_id, retention_days, updated_by, updated_at
                        ) VALUES (:tenant_id, :retention_days, :actor_id, :updated_at)
                        ON CONFLICT (tenant_id) DO UPDATE
                        SET retention_days = EXCLUDED.retention_days,
                            updated_by = EXCLUDED.updated_by,
                            updated_at = EXCLUDED.updated_at
                        RETURNING retention_days, updated_by, updated_at
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "retention_days": policy.retention_days,
                            "actor_id": actor_id,
                            "updated_at": now,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await connection.execute(
                text(
                    """
                    UPDATE audit_events
                    SET retention_until = occurred_at + make_interval(days => :retention_days)
                    WHERE tenant_id = :tenant_id
                    """
                ),
                {"tenant_id": tenant_uuid, "retention_days": policy.retention_days},
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.retention.update",
                resource_type="audit_policy",
                resource_id=tenant_id,
                evidence={"retentionDays": policy.retention_days},
                source={"component": "audit-repository"},
            )
        return AuditRetentionPolicy(
            retentionDays=row["retention_days"],
            updatedBy=row["updated_by"],
            updatedAt=row["updated_at"],
        )

    async def create_legal_hold(
        self,
        tenant_id: str,
        hold: AuditLegalHoldCreate,
        *,
        actor_id: str,
    ) -> AuditLegalHold:
        hold_id = new_runtime_id()
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        INSERT INTO audit_legal_holds (
                            id, tenant_id, name, reason, starts_at, ends_at,
                            active, created_by, created_at
                        ) VALUES (
                            :id, :tenant_id, :name, :reason, :starts_at, :ends_at,
                            true, :actor_id, :created_at
                        )
                        RETURNING *
                        """
                        ),
                        {
                            "id": hold_id,
                            "tenant_id": tenant_uuid,
                            "name": hold.name,
                            "reason": hold.reason,
                            "starts_at": hold.starts_at,
                            "ends_at": hold.ends_at,
                            "actor_id": actor_id,
                            "created_at": now,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.legal_hold.create",
                resource_type="audit_legal_hold",
                resource_id=str(hold_id),
                evidence={"name": hold.name, "startsAt": hold.starts_at.isoformat()},
                source={"component": "audit-repository"},
            )
        return _legal_hold(row, tenant_id)

    async def list_legal_holds(
        self,
        tenant_id: str,
        *,
        actor_id: str,
    ) -> tuple[AuditLegalHold, ...]:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM audit_legal_holds
                        WHERE tenant_id = :tenant_id
                        ORDER BY created_at DESC, id
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.legal_hold.read",
                resource_type="audit_legal_hold",
                resource_id=tenant_id,
                evidence={"returned": len(rows)},
                source={"component": "audit-repository"},
            )
        return tuple(_legal_hold(row, tenant_id) for row in rows)

    async def release_legal_hold(
        self,
        tenant_id: str,
        hold_id: UUID,
        *,
        actor_id: str,
    ) -> AuditLegalHold:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        UPDATE audit_legal_holds
                        SET active = false, released_by = :actor_id, released_at = :released_at
                        WHERE id = :hold_id AND tenant_id = :tenant_id AND active = true
                        RETURNING *
                        """
                        ),
                        {
                            "hold_id": hold_id,
                            "tenant_id": tenant_uuid,
                            "actor_id": actor_id,
                            "released_at": now,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise LookupError("legal hold unavailable")
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.legal_hold.release",
                resource_type="audit_legal_hold",
                resource_id=str(hold_id),
                source={"component": "audit-repository"},
            )
        return _legal_hold(row, tenant_id)

    async def purge_retained(self, tenant_id: str, *, actor_id: str) -> AuditRetentionResult:
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            await connection.execute(
                text("SELECT pg_advisory_xact_lock(hashtextextended(:tenant, 504))"),
                {"tenant": str(tenant_uuid)},
            )
            events = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT id, event_hash, occurred_at, retention_until
                        FROM audit_events
                        WHERE tenant_id = :tenant_id
                        ORDER BY id
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            holds = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT starts_at, ends_at FROM audit_legal_holds
                        WHERE tenant_id = :tenant_id AND active = true
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            last_id: int | None = None
            last_hash: str | None = None
            stopped_by_hold = False
            for event in events:
                if event["retention_until"] >= now:
                    break
                if any(
                    hold["starts_at"] <= event["occurred_at"]
                    and (hold["ends_at"] is None or event["occurred_at"] < hold["ends_at"])
                    for hold in holds
                ):
                    stopped_by_hold = True
                    break
                last_id = int(event["id"])
                last_hash = str(event["event_hash"])
            deleted = 0
            if last_id is not None:
                deleted = int(
                    (
                        await connection.execute(
                            text(
                                """
                                WITH deleted AS (
                                    DELETE FROM audit_events
                                    WHERE tenant_id = :tenant_id AND id <= :last_id
                                    RETURNING id
                                )
                                SELECT count(*) FROM deleted
                                """
                            ),
                            {"tenant_id": tenant_uuid, "last_id": last_id},
                        )
                    ).scalar_one()
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO audit_chain_anchors (
                            tenant_id, last_purged_event_id, previous_hash, updated_at
                        ) VALUES (:tenant_id, :last_id, :last_hash, :updated_at)
                        ON CONFLICT (tenant_id) DO UPDATE
                        SET last_purged_event_id = EXCLUDED.last_purged_event_id,
                            previous_hash = EXCLUDED.previous_hash,
                            updated_at = EXCLUDED.updated_at
                        """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "last_id": last_id,
                        "last_hash": last_hash,
                        "updated_at": now,
                    },
                )
            anchor = await connection.scalar(
                text("SELECT previous_hash FROM audit_chain_anchors WHERE tenant_id = :tenant_id"),
                {"tenant_id": tenant_uuid},
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="audit.retention.purge",
                resource_type="audit",
                resource_id=tenant_id,
                evidence={
                    "deletedEvents": deleted,
                    "stoppedByLegalHold": stopped_by_hold,
                },
                source={"component": "audit-repository"},
            )
        return AuditRetentionResult(
            deletedEvents=deleted,
            anchorHash=anchor,
            stoppedByLegalHold=stopped_by_hold,
        )

    async def record_export(self, receipt: AuditExportReceipt) -> AuditExportReceipt:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, receipt.tenant_id)
            await connection.execute(
                text(
                    """
                    INSERT INTO audit_export_receipts (
                        id, tenant_id, artifact_kind, destination, format, event_count,
                        checksum_sha256, signature, object_uri, created_by, created_at
                    ) VALUES (
                        :id, :tenant_id, :artifact_kind, :destination, :format, :event_count,
                        :checksum_sha256, :signature, :object_uri, :created_by, :created_at
                    )
                    """
                ),
                {
                    "id": receipt.export_id,
                    "tenant_id": tenant_uuid,
                    "artifact_kind": receipt.artifact_kind.value,
                    "destination": receipt.destination.value,
                    "format": receipt.format,
                    "event_count": receipt.event_count,
                    "checksum_sha256": receipt.checksum_sha256,
                    "signature": receipt.signature,
                    "object_uri": receipt.object_uri,
                    "created_by": receipt.created_by,
                    "created_at": receipt.created_at,
                },
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=receipt.created_by,
                action=f"{receipt.artifact_kind.value.casefold()}.export.{receipt.destination.value.casefold()}",
                resource_type="audit_export",
                resource_id=str(receipt.export_id),
                evidence={
                    "format": receipt.format,
                    "eventCount": receipt.event_count,
                    "checksumSha256": receipt.checksum_sha256,
                    "objectUri": receipt.object_uri,
                },
                source={"component": "audit-service"},
            )
        return receipt

    async def create_compliance_evidence(
        self,
        tenant_id: str,
        evidence: ComplianceEvidenceCreate,
        *,
        actor_id: str,
    ) -> ComplianceEvidenceRecord:
        evidence_id = new_runtime_id()
        now = datetime.now(UTC)
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        WITH prepared AS (
                            SELECT amesh_redact_audit_json(CAST(:payload AS jsonb)) AS payload
                        )
                        INSERT INTO compliance_evidence_records (
                            id, tenant_id, category, title, source_name, occurred_at, payload,
                            checksum_sha256, created_by, created_at
                        )
                        SELECT :id, :tenant_id, :category, :title, :source_name, :occurred_at,
                               payload,
                               encode(digest(convert_to(payload::text, 'UTF8'), 'sha256'), 'hex'),
                               :actor_id, :created_at
                        FROM prepared
                        RETURNING *
                        """
                        ),
                        {
                            "id": evidence_id,
                            "tenant_id": tenant_uuid,
                            "category": evidence.category.value,
                            "title": evidence.title,
                            "source_name": evidence.source,
                            "occurred_at": evidence.occurred_at,
                            "payload": json.dumps(evidence.payload),
                            "actor_id": actor_id,
                            "created_at": now,
                        },
                    )
                )
                .mappings()
                .one()
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="compliance.evidence.create",
                resource_type="compliance_evidence",
                resource_id=str(evidence_id),
                evidence={"category": evidence.category.value, "source": evidence.source},
                source={"component": "audit-repository"},
            )
        return _compliance_record(row, tenant_id)

    async def list_compliance_evidence(
        self,
        tenant_id: str,
        *,
        actor_id: str,
    ) -> tuple[ComplianceEvidenceRecord, ...]:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM compliance_evidence_records
                        WHERE tenant_id = :tenant_id
                        ORDER BY occurred_at DESC, id
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="compliance.evidence.read",
                resource_type="compliance_evidence",
                resource_id=tenant_id,
                evidence={"returned": len(rows)},
                source={"component": "audit-repository"},
            )
        return tuple(_compliance_record(row, tenant_id) for row in rows)

    async def compliance_snapshot(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        occurred_from: datetime | None,
        occurred_to: datetime | None,
        max_audit_events: int,
    ) -> ComplianceSnapshot:
        async with self._engine.begin() as connection:
            tenant_uuid = await _tenant_uuid(connection, tenant_id)
            access_rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT principals.id::text AS principal_id, principals.handle,
                               principals.principal_type, principals.enabled,
                               bindings.role_name, bindings.scope_type,
                               tenants.slug AS tenant_id, bindings.namespace_name
                        FROM auth_role_bindings AS bindings
                        JOIN auth_principals AS principals ON principals.id = bindings.principal_id
                        LEFT JOIN tenants ON tenants.id = bindings.tenant_id
                        WHERE bindings.tenant_id = :tenant_id
                           OR bindings.scope_type = 'INSTANCE'
                        ORDER BY principals.handle, bindings.role_name, bindings.id
                        """
                        ),
                        {"tenant_id": tenant_uuid},
                    )
                )
                .mappings()
                .all()
            )
            audit_rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT events.id, events.event_id, tenants.slug AS tenant_slug,
                               events.actor_id, events.delegated_actor_id, events.action,
                               events.resource_type, events.resource_id, events.outcome, events.reason,
                               events.correlation_id, events.trace_id, events.source, events.evidence,
                               events.occurred_at, events.previous_hash, events.event_hash,
                               events.retention_until
                        FROM audit_events AS events
                        JOIN tenants ON tenants.id = events.tenant_id
                        WHERE events.tenant_id = :tenant_id
                          AND (
                              CAST(:occurred_from AS timestamptz) IS NULL
                              OR events.occurred_at >= CAST(:occurred_from AS timestamptz)
                          )
                          AND (
                              CAST(:occurred_to AS timestamptz) IS NULL
                              OR events.occurred_at < CAST(:occurred_to AS timestamptz)
                          )
                        ORDER BY events.id DESC
                        LIMIT :limit
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurred_from": occurred_from,
                            "occurred_to": occurred_to,
                            "limit": max_audit_events,
                        },
                    )
                )
                .mappings()
                .all()
            )
            evidence_rows = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM compliance_evidence_records
                        WHERE tenant_id = :tenant_id
                          AND (
                              CAST(:occurred_from AS timestamptz) IS NULL
                              OR occurred_at >= CAST(:occurred_from AS timestamptz)
                          )
                          AND (
                              CAST(:occurred_to AS timestamptz) IS NULL
                              OR occurred_at < CAST(:occurred_to AS timestamptz)
                          )
                        ORDER BY occurred_at DESC, id
                        """
                        ),
                        {
                            "tenant_id": tenant_uuid,
                            "occurred_from": occurred_from,
                            "occurred_to": occurred_to,
                        },
                    )
                )
                .mappings()
                .all()
            )
            await _write_audit(
                connection,
                tenant_id=tenant_uuid,
                actor_id=actor_id,
                action="compliance.package.read",
                resource_type="compliance_package",
                resource_id=tenant_id,
                evidence={"auditEvents": len(audit_rows)},
                source={"component": "audit-repository"},
            )
        records = tuple(_compliance_record(row, tenant_id) for row in evidence_rows)
        categories: dict[ComplianceEvidenceCategory, list[dict[str, Any]]] = {
            category: [] for category in ComplianceEvidenceCategory
        }
        for record in records:
            categories[record.category].append(record.model_dump(mode="json", by_alias=True))
        audit = tuple(
            _audit_event(row).model_dump(mode="json", by_alias=True) for row in audit_rows
        )
        changes = tuple(
            event
            for event in audit
            if any(
                marker in str(event["action"])
                for marker in ("create", "update", "delete", "apply", "rotate", "revoke")
            )
        ) + tuple(categories[ComplianceEvidenceCategory.CHANGE_EVIDENCE])
        incidents = tuple(
            event for event in audit if event["outcome"] in {"DENIED", "FAILED", "ERROR"}
        ) + tuple(categories[ComplianceEvidenceCategory.INCIDENT])
        return ComplianceSnapshot(
            accessReviews=tuple(dict(row) for row in access_rows)
            + tuple(categories[ComplianceEvidenceCategory.ACCESS_REVIEW]),
            changeEvidence=changes,
            auditRecords=audit,
            backupRestoreEvidence=tuple(categories[ComplianceEvidenceCategory.BACKUP_RESTORE]),
            vulnerabilityResults=tuple(categories[ComplianceEvidenceCategory.VULNERABILITY]),
            incidentRecords=incidents,
            provenance=tuple(categories[ComplianceEvidenceCategory.PROVENANCE]),
        )


async def _tenant_uuid(connection: AsyncConnection, tenant_slug: str | None) -> UUID:
    if tenant_slug is None:
        return SYSTEM_TENANT_ID
    value = await connection.scalar(
        text("SELECT id FROM tenants WHERE slug = :tenant_slug"),
        {"tenant_slug": tenant_slug},
    )
    if value is None:
        raise LookupError("tenant unavailable")
    return UUID(str(value))


async def _write_audit(
    connection: AsyncConnection,
    *,
    tenant_id: UUID,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    outcome: str = "SUCCESS",
    reason: str | None = None,
    evidence: Mapping[str, object] | None = None,
    source: Mapping[str, object] | None = None,
) -> None:
    await connection.execute(
        text(
            """
            INSERT INTO audit_events (
                event_id, tenant_id, actor_id, action, resource_type, resource_id,
                outcome, reason, correlation_id, source, evidence, occurred_at
            ) VALUES (
                :event_id, :tenant_id, :actor_id, :action, :resource_type, :resource_id,
                :outcome, :reason, :correlation_id, CAST(:source AS jsonb),
                CAST(:evidence AS jsonb), :occurred_at
            )
            """
        ),
        {
            "event_id": new_runtime_id(),
            "tenant_id": tenant_id,
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "outcome": outcome,
            "reason": reason,
            "correlation_id": new_runtime_id(),
            "source": json.dumps(source or {}),
            "evidence": json.dumps(evidence or {}),
            "occurred_at": datetime.now(UTC),
        },
    )


def _audit_event(row: RowMapping) -> AuditEvent:
    return AuditEvent(
        cursor=row["id"],
        eventId=row["event_id"],
        tenantId=row["tenant_slug"],
        actorId=row["actor_id"],
        delegatedActorId=row["delegated_actor_id"],
        action=row["action"],
        resourceType=row["resource_type"],
        resourceId=row["resource_id"],
        outcome=row["outcome"],
        reason=row["reason"],
        correlationId=row["correlation_id"],
        traceId=row["trace_id"],
        source=dict(row["source"]),
        evidence=dict(row["evidence"]),
        occurredAt=row["occurred_at"],
        previousHash=row["previous_hash"],
        eventHash=row["event_hash"],
        retentionUntil=row["retention_until"],
    )


def _legal_hold(row: RowMapping, tenant_id: str) -> AuditLegalHold:
    return AuditLegalHold(
        id=row["id"],
        tenantId=tenant_id,
        name=row["name"],
        reason=row["reason"],
        startsAt=row["starts_at"],
        endsAt=row["ends_at"],
        active=row["active"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
        releasedBy=row["released_by"],
        releasedAt=row["released_at"],
    )


def _compliance_record(row: RowMapping, tenant_id: str) -> ComplianceEvidenceRecord:
    return ComplianceEvidenceRecord(
        id=row["id"],
        tenantId=tenant_id,
        category=row["category"],
        title=row["title"],
        source=row["source_name"],
        occurredAt=row["occurred_at"],
        payload=dict(row["payload"]),
        checksumSha256=row["checksum_sha256"],
        createdBy=row["created_by"],
        createdAt=row["created_at"],
    )
