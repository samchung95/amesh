from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.evidence_bundle import (
    CanonicalEvidenceBuilder,
    EvidenceBundle,
    EvidenceBundleError,
    EvidenceConflictError,
    EvidenceNotFoundError,
    EvidenceObjectStore,
    EvidencePage,
    EvidenceRecord,
    EvidenceUnavailableError,
)

from .tenant_context import tenant_transaction

_INSERT_BUNDLE = text(
    """
    INSERT INTO execution_evidence_bundles (
        tenant_id, execution_id, schema_version, bundle_digest, bundle, created_at
    ) VALUES (
        :tenant_id, :execution_id, :schema_version, :bundle_digest,
        CAST(:bundle AS jsonb), :created_at
    )
    ON CONFLICT (tenant_id, execution_id) DO NOTHING
    RETURNING tenant_id, execution_id, schema_version, bundle_digest, bundle, created_at
    """
)
_SELECT_BUNDLE = text(
    """
    SELECT tenant_id, execution_id, schema_version, bundle_digest, bundle, created_at
    FROM execution_evidence_bundles
    WHERE tenant_id = :tenant_id AND execution_id = :execution_id
    """
)


class PostgresEvidenceBundleRepository:
    """Immutable PostgreSQL projection with tenant-scoped, bounded reads."""

    max_page_size = 500

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        object_store: EvidenceObjectStore | None = None,
        max_inline_bytes: int = 64 * 1024,
    ) -> None:
        if max_inline_bytes < 1:
            raise ValueError("max_inline_bytes must be positive")
        self._engine = engine
        self._object_store = object_store
        self._max_inline_bytes = max_inline_bytes

    async def put(self, bundle: EvidenceBundle) -> EvidenceBundle:
        candidate = bundle
        if self._object_store is not None:
            candidate = bundle.externalize_large_fields(
                self._object_store,
                max_inline_bytes=self._max_inline_bytes,
            )
        candidate = candidate.sealed()
        candidate.verify()
        payload = candidate.model_dump(mode="json", by_alias=True, exclude_none=True)
        async with tenant_transaction(self._engine, candidate.tenant_id) as (
            connection,
            tenant_uuid,
        ):
            inserted = await connection.execute(
                _INSERT_BUNDLE,
                {
                    "tenant_id": tenant_uuid,
                    "execution_id": candidate.execution_id,
                    "schema_version": candidate.schema_version,
                    "bundle_digest": candidate.digest,
                    "bundle": json.dumps(payload, separators=(",", ":")),
                    "created_at": candidate.created_at,
                },
            )
            row = inserted.mappings().first()
            if row is None:
                row = (
                    (
                        await connection.execute(
                            _SELECT_BUNDLE,
                            {"tenant_id": tenant_uuid, "execution_id": candidate.execution_id},
                        )
                    )
                    .mappings()
                    .first()
                )
            if row is None:
                raise EvidenceNotFoundError("execution evidence bundle is absent")
            stored = _bundle_from_row(row)
            if stored.digest != candidate.digest:
                raise EvidenceConflictError("execution evidence conflicts with an immutable bundle")
            return stored

    async def build_and_put(
        self,
        execution_id: UUID | str,
        tenant_id: str,
        events: tuple[Any, ...] | list[Any],
        *,
        created_at: datetime,
        correlation_id: UUID | str | None = None,
        inputs: Mapping[str, Any] | None = None,
        outputs: Mapping[str, Any] | None = None,
    ) -> EvidenceBundle:
        return await self.put(
            CanonicalEvidenceBuilder.from_events(
                execution_id,
                tenant_id,
                events,
                created_at=created_at,
                correlation_id=correlation_id,
                inputs=inputs,
                outputs=outputs,
            )
        )

    async def get(self, execution_id: UUID | str, *, tenant_id: str) -> EvidenceBundle:
        async with tenant_transaction(self._engine, tenant_id) as (connection, tenant_uuid):
            row = (
                (
                    await connection.execute(
                        _SELECT_BUNDLE,
                        {"tenant_id": tenant_uuid, "execution_id": execution_id},
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            raise EvidenceNotFoundError("execution evidence bundle is absent")
        bundle = _bundle_from_row(row)
        if self._object_store is not None:
            try:
                bundle.verify_externalized_fields(self._object_store)
            except EvidenceNotFoundError as exc:
                raise EvidenceUnavailableError(
                    "externalized evidence object is unavailable"
                ) from exc
        bundle.verify()
        return bundle

    async def page(
        self,
        execution_id: UUID | str,
        *,
        tenant_id: str,
        section: str = "trace",
        cursor: str | None = None,
        limit: int = 100,
    ) -> EvidencePage[EvidenceRecord]:
        if not 1 <= limit <= self.max_page_size:
            raise ValueError(f"limit must be between 1 and {self.max_page_size}")
        try:
            offset = 0 if cursor is None else int(cursor)
        except ValueError as exc:
            raise ValueError("cursor must be a non-negative integer") from exc
        if offset < 0:
            raise ValueError("cursor must be a non-negative integer")
        bundle = await self.get(execution_id, tenant_id=tenant_id)
        if section not in {
            "decisions",
            "trace",
            "inputs",
            "outputs",
            "task_attempts",
            "agent_sessions",
            "external_invocations",
            "state_transitions",
            "logs",
            "metrics",
            "files",
            "errors",
            "approvals",
            "interventions",
            "controls",
        }:
            raise ValueError(f"unknown evidence section {section!r}")
        records = getattr(bundle, section)
        if offset > len(records):
            raise ValueError("cursor is outside evidence section")
        page = records[offset : offset + limit]
        end = offset + len(page)
        return EvidencePage[EvidenceRecord](
            items=page,
            nextCursor=str(end) if end < len(records) else None,
            limit=limit,
            total=len(records),
        )


def _bundle_from_row(row: Any) -> EvidenceBundle:
    raw = row["bundle"]
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise EvidenceBundleError("stored evidence bundle is not a JSON object")
    bundle = EvidenceBundle.model_validate(raw)
    if row.get("bundle_digest") != bundle.digest:
        raise EvidenceBundleError("stored evidence bundle digest does not match its content")
    return bundle


__all__ = ["PostgresEvidenceBundleRepository"]
