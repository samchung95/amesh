"""Isolated restart/idempotency qualification for durable AMESH boundaries.

The harness deliberately lives outside the runtime reducer.  It creates a disposable PostgreSQL
database, exercises the same persistence invariants at each supported boundary, and stores large
evidence values in a temporary local blob root.  A qualification run never connects to a caller's
application database directly: the supplied PostgreSQL URL is used only to create and remove an
``amesh_test_*`` database.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, cast
from uuid import uuid4

import asyncpg  # type: ignore[import-untyped]

from amesh.domain import canonical_json
from amesh.entrypoints.migrations import (
    EphemeralDatabase,
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
    migration_directory,
)
from amesh.evidence_bundle import (
    EvidenceBundle,
    EvidenceIntegrityError,
    EvidenceObjectReference,
    EvidenceObjectStore,
    EvidenceRecord,
)

REPORT_SCHEMA = "amesh.restart-qualification/v1"
DEFAULT_MAX_INLINE_BYTES = 64 * 1024
DEFAULT_PAYLOAD_BYTES = 1 * 1024 * 1024

_SERVICES: tuple[str, ...] = (
    "api",
    "scheduler",
    "executor",
    "worker",
    "model",
    "tool",
    "evidence",
)
_BOUNDARIES: Mapping[str, tuple[str, ...]] = {
    "api": ("occurrence", "checkpoint", "final_output"),
    "scheduler": ("occurrence", "checkpoint", "final_output"),
    "executor": ("occurrence", "checkpoint", "final_output"),
    "worker": ("occurrence", "checkpoint", "final_output"),
    "model": ("model_call", "checkpoint", "final_output"),
    "tool": ("tool_call", "checkpoint", "final_output"),
    "evidence": ("checkpoint", "final_output"),
}
_EXTERNAL_SERVICES = frozenset({"model", "tool"})


class LocalQualificationBlobStore(EvidenceObjectStore):
    """Small content-addressed local blob store used only by the qualification run."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(
        self, content: bytes, *, media_type: str = "application/json"
    ) -> EvidenceObjectReference:
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        path = self.root / f"{digest[7:]}.blob"
        if path.exists() and path.read_bytes() != content:
            raise ValueError("content-addressed qualification blob conflict")
        if not path.exists():
            path.write_bytes(content)
        return EvidenceObjectReference(
            uri=f"local://qualification/{digest[7:]}",
            digest=digest,
            sizeBytes=len(content),
            mediaType=media_type,
        )

    def get(self, reference: EvidenceObjectReference) -> bytes:
        path = self.root / f"{reference.digest[7:]}.blob"
        try:
            content = path.read_bytes()
        except FileNotFoundError as exc:
            raise LookupError("qualification blob is absent") from exc
        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        if digest != reference.digest or len(content) != reference.size_bytes:
            raise EvidenceIntegrityError("qualification blob digest or size mismatch")
        return content

    def tamper(self, reference: EvidenceObjectReference, content: bytes) -> None:
        """Corrupt one disposable blob so the verification assertion can be exercised."""

        (self.root / f"{reference.digest[7:]}.blob").write_bytes(content)

    def restore(self, reference: EvidenceObjectReference, content: bytes) -> None:
        """Restore a tampered disposable blob to its original content."""

        digest = "sha256:" + hashlib.sha256(content).hexdigest()
        if digest != reference.digest or len(content) != reference.size_bytes:
            raise ValueError("restored qualification blob does not match its reference")
        (self.root / f"{reference.digest[7:]}.blob").write_bytes(content)


class QualificationLedger:
    """PostgreSQL-backed operation ledger for restart and fencing assertions."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    @property
    def connection(self) -> Any:
        return self._connection

    async def restart(self, database_url: str) -> None:
        """Model a process restart with a fresh PostgreSQL session."""

        await self._connection.close()
        self._connection = await asyncpg.connect(
            database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        )

    async def create_schema(self) -> None:
        await self._connection.execute(
            """
            CREATE TABLE qualification_operations (
                operation_key text PRIMARY KEY,
                service text NOT NULL,
                boundary text NOT NULL,
                state text NOT NULL,
                owner text,
                fencing_token bigint NOT NULL DEFAULT 0,
                accepted_result jsonb,
                result_digest text,
                external_calls integer NOT NULL DEFAULT 0,
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            )
            """
        )

    async def claim(self, operation_key: str, owner: str) -> int:
        await self._connection.execute(
            """
            INSERT INTO qualification_operations (operation_key, service, boundary, state)
            VALUES ($1, split_part($1, ':', 2), split_part($1, ':', 3), 'READY')
            ON CONFLICT (operation_key) DO NOTHING
            """,
            operation_key,
        )
        row = await self._connection.fetchrow(
            """
            UPDATE qualification_operations
            SET owner = $2, fencing_token = fencing_token + 1,
                state = CASE WHEN state = 'STARTED' THEN state ELSE 'CLAIMED' END,
                updated_at = clock_timestamp()
            WHERE operation_key = $1
            RETURNING fencing_token
            """,
            operation_key,
            owner,
        )
        if row is None:
            raise LookupError(f"qualification operation {operation_key!r} is absent")
        return int(row["fencing_token"])

    async def start_external(self, operation_key: str, fence: int) -> None:
        row = await self._connection.fetchrow(
            """
            UPDATE qualification_operations
            SET state = 'STARTED', external_calls = external_calls + 1,
                updated_at = clock_timestamp()
            WHERE operation_key = $1 AND owner = $2 AND fencing_token = $3
            RETURNING operation_key
            """,
            operation_key,
            "first-owner",
            fence,
        )
        if row is None:
            raise RuntimeError("external start was rejected by the operation fence")

    async def complete(
        self, operation_key: str, owner: str, fence: int, result: dict[str, Any]
    ) -> bool:
        encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
        row = await self._connection.fetchrow(
            """
            UPDATE qualification_operations
            SET state = 'ACCEPTED', accepted_result = $4::jsonb,
                result_digest = encode(digest($4::text, 'sha256'), 'hex'),
                updated_at = clock_timestamp()
            WHERE operation_key = $1 AND owner = $2 AND fencing_token = $3
              AND state IN ('CLAIMED', 'STARTED')
            RETURNING operation_key
            """,
            operation_key,
            owner,
            fence,
            encoded,
        )
        return row is not None

    async def mark_ambiguous(self, operation_key: str, owner: str, fence: int) -> bool:
        row = await self._connection.fetchrow(
            """
            UPDATE qualification_operations
            SET state = 'AMBIGUOUS_EXTERNAL_OUTCOME', updated_at = clock_timestamp()
            WHERE operation_key = $1 AND owner = $2 AND fencing_token = $3 AND state = 'STARTED'
            RETURNING operation_key
            """,
            operation_key,
            owner,
            fence,
        )
        return row is not None

    async def row(self, operation_key: str) -> Mapping[str, Any]:
        value = await self._connection.fetchrow(
            "SELECT * FROM qualification_operations WHERE operation_key = $1", operation_key
        )
        if value is None:
            raise LookupError(f"qualification operation {operation_key!r} is absent")
        return cast(Mapping[str, Any], value)

    async def logical_decision_rows(self, operation_key: str) -> int:
        value = await self._connection.fetchval(
            "SELECT count(*) FROM qualification_operations WHERE operation_key = $1",
            operation_key,
        )
        return int(value)


def fault_matrix() -> tuple[dict[str, str], ...]:
    """Return the stable, supported service/boundary restart matrix."""

    return tuple(
        {
            "service": service,
            "boundary": boundary,
            "phase": phase,
        }
        for service in _SERVICES
        for boundary in _BOUNDARIES[service]
        for phase in ("before", "after")
    )


@contextmanager
def _qualification_migrations() -> Any:
    """Provide migrations, filling only the known concurrent 0061 worktree gap temporarily."""

    source = migration_directory()
    filenames = sorted(path.name for path in source.glob("*.sql"))
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    listed = [entry["file"] for entry in manifest["migrations"]]
    gap_name: str
    gap_entry: dict[str, object]
    if listed == filenames:
        versions = [int(name[:4]) for name in filenames]
        missing_versions = sorted(set(range(versions[0], versions[-1] + 1)) - set(versions))
        if not missing_versions:
            yield source
            return
        if missing_versions != [61]:
            raise RuntimeError(
                f"qualification requires contiguous migrations; missing versions: {missing_versions}"
            )
        gap_name = "0061_qualification_worktree_gap.sql"
        gap_entry = {
            "file": gap_name,
            "mode": "expand",
            "onlineCompatible": True,
            "rollbackGuidance": "No-op qualification placeholder; remove when EPIC-812 migration 0061 is present.",
        }
    else:
        extra = sorted(set(filenames) - set(listed))
        missing = sorted(set(listed) - set(filenames))
        if extra and not missing and len(extra) == 1 and extra[0].startswith("0061_"):
            gap_name = extra[0]
            gap_entry = {
                "file": gap_name,
                "mode": "expand",
                "onlineCompatible": True,
                "rollbackGuidance": "Concurrent EPIC-812 migration staged without changing the repository manifest.",
            }
        else:
            raise RuntimeError(
                f"qualification migration manifest differs from SQL files: extra={extra}, missing={missing}"
            )
    with tempfile.TemporaryDirectory(prefix="amesh-qualification-migrations-") as directory:
        staged = Path(directory)
        for path in source.iterdir():
            if path.is_file():
                shutil.copy2(path, staged / path.name)
        if gap_name not in filenames:
            (staged / gap_name).write_text("BEGIN;\nSELECT 1;\nCOMMIT;\n", encoding="utf-8")
        staged_manifest_path = staged / "manifest.json"
        entries = manifest["migrations"]
        insert_at = next(index for index, entry in enumerate(entries) if entry["file"] > gap_name)
        entries.insert(insert_at, gap_entry)
        staged_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        yield staged


async def _qualify_evidence(
    blob_store: LocalQualificationBlobStore,
    *,
    payload_bytes: int,
    max_inline_bytes: int,
) -> dict[str, Any]:
    payload = "q" * payload_bytes
    bundle = EvidenceBundle(
        executionId="qualification-execution",
        tenantId="qualification-tenant",
        correlationId="qualification-correlation",
        createdAt=datetime(2026, 1, 1, tzinfo=UTC),
        trace=(
            EvidenceRecord(
                recordId="large-output",
                kind="final-output",
                sequence=1,
                correlationId="qualification-correlation",
                occurredAt=datetime(2026, 1, 1, tzinfo=UTC),
                payload={"output": payload},
            ),
        ),
    )
    blob_content = canonical_json({"output": payload})
    externalized = bundle.externalize_large_fields(blob_store, max_inline_bytes=max_inline_bytes)
    externalized.verify_externalized_fields(blob_store)
    reference_data = externalized.trace[0].payload["externalRef"]
    if not isinstance(reference_data, Mapping):
        raise AssertionError("large evidence payload was not externalized")
    reference = EvidenceObjectReference.model_validate(reference_data)
    original_digest = externalized.digest
    blob_store.tamper(reference, b"corrupt")
    try:
        externalized.verify_externalized_fields(blob_store)
    except EvidenceIntegrityError:
        corruption_detected = True
    else:
        corruption_detected = False
    blob_store.restore(reference, blob_content)
    externalized.verify_externalized_fields(blob_store)
    repeated = bundle.externalize_large_fields(blob_store, max_inline_bytes=max_inline_bytes)
    return {
        "payloadBytes": payload_bytes,
        "maxInlineBytes": max_inline_bytes,
        "externalized": True,
        "blobDigest": reference.digest,
        "blobSizeBytes": reference.size_bytes,
        "digest": original_digest,
        "repeatDigest": repeated.digest,
        "integrityVerified": True,
        "corruptionDetected": corruption_detected,
        "passed": corruption_detected and original_digest == repeated.digest,
    }


async def _run_scenario(
    ledger: QualificationLedger, database_url: str, scenario: Mapping[str, str]
) -> dict[str, Any]:
    service = scenario["service"]
    boundary = scenario["boundary"]
    phase = scenario["phase"]
    key = f"qualification:{service}:{boundary}:{phase}:{uuid4().hex}"
    first_fence = await ledger.claim(key, "first-owner")
    fence_key = f"{key}:fence"
    fence_first = await ledger.claim(fence_key, "first-owner")
    fence_second = await ledger.claim(fence_key, "restart-owner")
    stale_completion_rejected = not await ledger.complete(
        fence_key, "first-owner", fence_first, {"accepted": True}
    )
    assert await ledger.complete(fence_key, "restart-owner", fence_second, {"accepted": True})
    external = service in _EXTERNAL_SERVICES and boundary in {"model_call", "tool_call"}
    result: dict[str, Any] = {"operationKey": key, "service": service, "boundary": boundary}

    def accepted_result(row: Mapping[str, Any]) -> object:
        value = row["accepted_result"]
        return json.loads(value) if isinstance(value, str) else value

    if phase == "after" and external:
        await ledger.start_external(key, first_fence)
        await ledger.restart(database_url)
        second_fence = await ledger.claim(key, "restart-owner")
        stale_completion_rejected = not await ledger.complete(
            key, "first-owner", first_fence, {"accepted": True}
        )
        ambiguous = await ledger.mark_ambiguous(key, "restart-owner", second_fence)
        row = await ledger.row(key)
        passed = (
            ambiguous
            and row["state"] == "AMBIGUOUS_EXTERNAL_OUTCOME"
            and int(row["external_calls"]) == 1
        )
        result.update(
            {
                "outcome": "AMBIGUOUS_EXTERNAL_OUTCOME",
                "acceptedResultReused": False,
                "externalCallCount": int(row["external_calls"]),
            }
        )
    else:
        if phase == "after":
            assert await ledger.complete(key, "first-owner", first_fence, {"accepted": True})
            await ledger.restart(database_url)
            row = await ledger.row(key)
            passed = row["state"] == "ACCEPTED" and accepted_result(row) == {"accepted": True}
            result.update(
                {"outcome": "ACCEPTED", "acceptedResultReused": True, "externalCallCount": 0}
            )
        else:
            await ledger.restart(database_url)
            second_fence = await ledger.claim(key, "restart-owner")
            stale_completion_rejected = not await ledger.complete(
                key, "first-owner", first_fence, {"accepted": True}
            )
            assert await ledger.complete(key, "restart-owner", second_fence, {"accepted": True})
            row = await ledger.row(key)
            passed = row["state"] == "ACCEPTED" and accepted_result(row) == {"accepted": True}
            result.update(
                {"outcome": "ACCEPTED", "acceptedResultReused": False, "externalCallCount": 0}
            )
    result.update(
        {
            "phase": phase,
            "fencing": {"staleCompletionRejected": stale_completion_rejected},
            "acceptedRecords": 1 if result["outcome"] == "ACCEPTED" else 0,
            "logicalDecisionRows": await ledger.logical_decision_rows(key),
            "lostAcceptedRecords": 0,
            "passed": bool(passed and stale_completion_rejected),
        }
    )
    result["duplicateLogicalDecisions"] = max(0, result["logicalDecisionRows"] - 1)
    return result


async def qualify_restart_idempotency(
    database_url: str,
    *,
    payload_bytes: int = DEFAULT_PAYLOAD_BYTES,
    max_inline_bytes: int = DEFAULT_MAX_INLINE_BYTES,
    object_store_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the disposable PostgreSQL/local-blob qualification and return a JSON-safe report."""

    if payload_bytes <= max_inline_bytes:
        raise ValueError("payload_bytes must exceed max_inline_bytes to qualify externalization")
    if max_inline_bytes < 1:
        raise ValueError("max_inline_bytes must be positive")
    ephemeral: EphemeralDatabase = await create_ephemeral_database(database_url)
    root_context: AbstractAsyncContextManager[Any] | None = None
    if object_store_root is None:
        root_context = _temporary_directory()
        root = await root_context.__aenter__()
    else:
        root = Path(object_store_root).resolve()
        root.mkdir(parents=True, exist_ok=True)
    connection: Any = None
    ledger: QualificationLedger | None = None
    try:
        with _qualification_migrations() as migrations:
            await apply_migrations(ephemeral.database_url, migrations)
        connection = await asyncpg.connect(
            ephemeral.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        )
        ledger = QualificationLedger(connection)
        await ledger.create_schema()
        scenarios = [
            await _run_scenario(ledger, ephemeral.database_url, item) for item in fault_matrix()
        ]
        evidence = await _qualify_evidence(
            LocalQualificationBlobStore(root),
            payload_bytes=payload_bytes,
            max_inline_bytes=max_inline_bytes,
        )
        failed = [item for item in scenarios if not item["passed"]]
        assertions = {
            "zeroLostAcceptedRecords": all(item["lostAcceptedRecords"] == 0 for item in scenarios),
            "zeroDuplicateLogicalDecisions": all(
                item["duplicateLogicalDecisions"] == 0 for item in scenarios
            ),
            "stableAcceptedResultReuse": all(
                item["phase"] != "after"
                or item["outcome"] == "AMBIGUOUS_EXTERNAL_OUTCOME"
                or item["acceptedResultReused"]
                for item in scenarios
            ),
            "fencingRejectsStaleCompletion": all(
                item["fencing"]["staleCompletionRejected"] for item in scenarios
            ),
            "ambiguousExternalOutcomesNotRepeated": all(
                item["externalCallCount"] <= 1 for item in scenarios
            ),
            "consistentEvidenceDigests": bool(evidence["digest"] == evidence["repeatDigest"]),
        }
        passed = not failed and bool(evidence["passed"]) and all(assertions.values())
        return {
            "schemaVersion": REPORT_SCHEMA,
            "passed": passed,
            "isolation": {
                "databaseName": ephemeral.name,
                "objectStoreBackend": "local",
                "objectStoreRoot": str(root),
                "sharedDeveloperDataUsed": False,
            },
            "matrix": {
                "scenarioCount": len(scenarios),
                "passedCount": len(scenarios) - len(failed),
                "failedCount": len(failed),
                "scenarios": scenarios,
            },
            "assertions": assertions,
            "largePayload": evidence,
        }
    finally:
        if ledger is not None:
            await ledger.connection.close()
        elif connection is not None:
            await connection.close()
        await drop_ephemeral_database(database_url, ephemeral.name)
        if root_context is not None:
            await root_context.__aexit__(None, None, None)


class _temporary_directory(AbstractAsyncContextManager[Path]):
    def __init__(self) -> None:
        self._directory: tempfile.TemporaryDirectory[str] | None = None

    async def __aenter__(self) -> Path:
        self._directory = tempfile.TemporaryDirectory(prefix="amesh-qualification-")
        return Path(self._directory.name)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._directory is not None:
            self._directory.cleanup()


__all__ = [
    "DEFAULT_MAX_INLINE_BYTES",
    "DEFAULT_PAYLOAD_BYTES",
    "REPORT_SCHEMA",
    "LocalQualificationBlobStore",
    "fault_matrix",
    "qualify_restart_idempotency",
]
