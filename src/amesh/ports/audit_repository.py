from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from amesh.domain.audit import (
    AuditEventPage,
    AuditExportReceipt,
    AuditIntegrityReport,
    AuditLegalHold,
    AuditLegalHoldCreate,
    AuditRetentionPolicy,
    AuditRetentionResult,
    ComplianceEvidenceCreate,
    ComplianceEvidenceRecord,
    ComplianceSnapshot,
)
from amesh.domain.authorization import AuthorizationDecision, AuthorizationRequest


class AuthorizationDecisionAuditSink(Protocol):
    async def record_authorization_decision(
        self,
        request: AuthorizationRequest,
        decision: AuthorizationDecision,
    ) -> None: ...


class AuditRepository(Protocol):
    async def record_connection_test(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        connection_key: str,
        connection_revision: int,
        connection_digest: str,
        status: str,
        observed_digest: str | None,
        checked_tool_count: int,
        diagnostic: str | None,
    ) -> UUID: ...

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
    ) -> AuditEventPage: ...

    async def verify_integrity(self, tenant_id: str, *, actor_id: str) -> AuditIntegrityReport: ...

    async def get_retention_policy(self, tenant_id: str) -> AuditRetentionPolicy: ...

    async def set_retention_policy(
        self,
        tenant_id: str,
        policy: AuditRetentionPolicy,
        *,
        actor_id: str,
    ) -> AuditRetentionPolicy: ...

    async def create_legal_hold(
        self,
        tenant_id: str,
        hold: AuditLegalHoldCreate,
        *,
        actor_id: str,
    ) -> AuditLegalHold: ...

    async def list_legal_holds(
        self, tenant_id: str, *, actor_id: str
    ) -> tuple[AuditLegalHold, ...]: ...

    async def release_legal_hold(
        self,
        tenant_id: str,
        hold_id: UUID,
        *,
        actor_id: str,
    ) -> AuditLegalHold: ...

    async def purge_retained(self, tenant_id: str, *, actor_id: str) -> AuditRetentionResult: ...

    async def record_export(self, receipt: AuditExportReceipt) -> AuditExportReceipt: ...

    async def create_compliance_evidence(
        self,
        tenant_id: str,
        evidence: ComplianceEvidenceCreate,
        *,
        actor_id: str,
    ) -> ComplianceEvidenceRecord: ...

    async def list_compliance_evidence(
        self,
        tenant_id: str,
        *,
        actor_id: str,
    ) -> tuple[ComplianceEvidenceRecord, ...]: ...

    async def compliance_snapshot(
        self,
        tenant_id: str,
        *,
        actor_id: str,
        occurred_from: datetime | None,
        occurred_to: datetime | None,
        max_audit_events: int,
    ) -> ComplianceSnapshot: ...
