from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID, uuid5

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh.domain.agent_primitives import AgentInvocationRecord
from amesh.domain.agent_resources import AgentCapabilityPin
from amesh.domain.execution import ExecutionEvent, TaskRunEvent, TaskRunLifecyclePhase
from amesh.ports.errors import NotFoundError
from amesh.ports.execution_repository import PersistedTaskRun
from amesh.ports.metadata_repository import ExecutionArtifact, ExecutionEvidenceEvent
from amesh.ports.object_store import ObjectMetadata
from amesh.ports.repository_support import JsonCodec
from amesh.ports.transfer_repository import (
    ProfileImportReceipt,
    TransferRepository,
)
from amesh.profile_transfer import ProfileBundle
from amesh.session_transfer import (
    SessionTaskRunEvent,
    SessionTransferBundle,
    SessionTransferCompatibilityReport,
    SessionTransferImportResult,
    SessionTransferMode,
    seal_bundle,
)

from .execution_rows import execution_from_row
from .repository_support import PostgresRepositoryBase

_TRANSFER_NAMESPACE = UUID("1bc7e8cc-6d24-4d44-8e16-34de72de9d73")


class TransferArtifactStore(Protocol):
    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata: ...


class PostgresTransferRepository(PostgresRepositoryBase, TransferRepository):
    """Export and atomically import records through the canonical authorities."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        object_store: TransferArtifactStore | None = None,
        compatible_harnesses: set[tuple[str, str, str]] | None = None,
    ) -> None:
        super().__init__(engine)
        self._object_store = object_store
        self._compatible_harnesses = compatible_harnesses

    async def export_session_bundle(
        self,
        source_tenant_id: str,
        session_id: UUID,
        *,
        mode: SessionTransferMode,
        artifact_destination_refs: dict[str, str] | None = None,
    ) -> SessionTransferBundle:
        """Assemble a sealed snapshot from the canonical PostgreSQL authorities."""
        from .agent_sessions import _session_event, _session_record

        async with self._services.transactions.tenant(source_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            session_row = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM agent_sessions WHERE tenant_id = :tenant_id "
                            "AND session_id = :session_id"
                        ),
                        {"tenant_id": tenant_uuid, "session_id": session_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if session_row is None:
                raise NotFoundError(
                    "agent session",
                    session_id,
                    message=f"agent session {session_id} does not exist",
                )
            session_event_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM agent_session_events WHERE tenant_id = :tenant_id "
                            "AND session_id = :session_id ORDER BY event_index"
                        ),
                        {"tenant_id": tenant_uuid, "session_id": session_id},
                    )
                )
                .mappings()
                .all()
            )
            execution_row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT executions.*, tenants.slug AS tenant_slug,
                               flows.flow_key, revisions.revision AS flow_revision
                        FROM executions
                        JOIN tenants ON tenants.id = executions.tenant_id
                        JOIN flows ON flows.id = executions.flow_id
                        JOIN flow_revisions AS revisions ON revisions.id = executions.flow_revision_id
                        WHERE executions.tenant_id = :tenant_id
                          AND executions.id = :execution_id
                        """
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .one()
            )
            task_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM task_runs WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY id"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            execution_event_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM execution_events WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY sequence"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            task_event_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM task_run_events WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY task_run_id, sequence"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            invocation_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM agent_invocations WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY invocation_id"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            evidence_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM execution_evidence_events WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY cursor"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            artifact_rows = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM execution_artifacts WHERE tenant_id = :tenant_id "
                            "AND execution_id = :execution_id ORDER BY occurred_at, id"
                        ),
                        {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                    )
                )
                .mappings()
                .all()
            )
            pin_row = (
                (
                    await connection.execute(
                        text(
                            "SELECT * FROM agent_capability_pins WHERE tenant_id = :tenant_id "
                            "AND pin_id = :pin_id"
                        ),
                        {"tenant_id": tenant_uuid, "pin_id": session_row["capability_pin_id"]},
                    )
                )
                .mappings()
                .one()
            )
            lease_count = int(
                await connection.scalar(
                    text(
                        "SELECT count(*) FROM leases WHERE tenant_id = :tenant_id "
                        "AND (resource_id = :execution_id OR resource_id = :task_run_id) "
                        "AND expires_at > clock_timestamp()"
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "execution_id": str(session_row["execution_id"]),
                        "task_run_id": str(session_row["task_run_id"]),
                    },
                )
                or 0
            )
            admission_count = int(
                await connection.scalar(
                    text(
                        "SELECT count(*) FROM admission_reservations WHERE tenant_id = :tenant_id "
                        "AND (resource_id = :execution_id OR resource_id = :task_run_id) "
                        "AND released_at IS NULL AND lease_expires_at > clock_timestamp()"
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "execution_id": session_row["execution_id"],
                        "task_run_id": session_row["task_run_id"],
                    },
                )
                or 0
            )
            approval_count = int(
                await connection.scalar(
                    text(
                        "SELECT count(*) FROM human_tasks WHERE tenant_id = :tenant_id "
                        "AND execution_id = :execution_id AND state IN ('OPEN', 'ESCALATED')"
                    ),
                    {"tenant_id": tenant_uuid, "execution_id": session_row["execution_id"]},
                )
                or 0
            )

        session = _session_record(session_row, source_tenant_id)
        execution = execution_from_row(execution_row)
        tasks = tuple(_persisted_task_run(row) for row in task_rows)
        events = tuple(_session_event(row) for row in session_event_rows)
        execution_events = tuple(_execution_event(row) for row in execution_event_rows)
        task_event_records = tuple(
            SessionTaskRunEvent(
                taskRunId=row["task_run_id"],
                sequence=row["sequence"],
                event=_task_run_event(row),
            )
            for row in task_event_rows
        )
        invocations = tuple(_invocation(row, source_tenant_id) for row in invocation_rows)
        evidence = tuple(_evidence_event(row) for row in evidence_rows)
        artifacts = tuple(_artifact(row) for row in artifact_rows)
        destination_refs = artifact_destination_refs or {
            artifact.uri: artifact.uri for artifact in artifacts
        }
        if artifacts and set(destination_refs) != {item.uri for item in artifacts}:
            raise ValueError("artifact destination references must cover every exported artifact")
        if mode is SessionTransferMode.TERMINAL_HISTORY and (
            session.state.value not in {"SUCCEEDED", "FAILED"}
            or session.phase.value != "COMPLETE"
            or session.completed_at is None
            or execution.state.value not in {"CANCELLED", "SUCCESS", "FAILED", "WARNING"}
            or any(task.state.value not in {"SUCCESS", "FAILED", "CANCELLED"} for task in tasks)
        ):
            raise ValueError("terminal history export requires a completed terminal snapshot")
        if mode is SessionTransferMode.CLEAN_CHECKPOINT and (
            session.state.value != "RUNNING"
            or session.phase.value != "READY"
            or execution.state.value != "PAUSED"
        ):
            raise ValueError("clean checkpoint export requires a PAUSED/READY snapshot")
        if session.harness is None or pin_row is None:
            raise ValueError("session export requires exact harness and capability pins")
        if any(invocation.state.value == "STARTED" for invocation in invocations):
            raise ValueError("session export cannot include a STARTED invocation")
        checkpoint = session.checkpoint
        if (
            any(
                value is not None
                for value in (
                    checkpoint.pending_action,
                    checkpoint.pending_turn,
                    checkpoint.memory_write,
                    checkpoint.model_continuation,
                )
            )
            or checkpoint.model_continuations
        ):
            raise ValueError("session export cannot include pending checkpoint work")
        bundle = SessionTransferBundle(
            mode=mode,
            sourceTenantId=source_tenant_id,
            session=session,
            events=events,
            execution=execution,
            taskRuns=tasks,
            executionEvents=execution_events,
            taskRunEventRecords=task_event_records,
            invocations=invocations,
            evidenceEvents=evidence,
            artifacts=artifacts,
            artifactDestinationRefs=destination_refs,
            capabilityPin=AgentCapabilityPin(
                pinId=pin_row["pin_id"],
                tenantId=source_tenant_id,
                namespace=pin_row["namespace_name"],
                subjectRef=pin_row["subject_ref"],
                envelopeDigest=pin_row["envelope_digest"],
                envelope=pin_row["envelope"],
                createdBy=pin_row["created_by"],
                createdAt=pin_row["created_at"],
            ),
            activeLeaseCount=lease_count,
            activeAdmissionClaimCount=admission_count,
            unresolvedApprovalCount=approval_count,
            checksumSha256="0" * 64,
        )
        return seal_bundle(bundle)

    async def get_profile_import(
        self, target_tenant_id: str, import_id: str
    ) -> ProfileImportReceipt | None:
        async with self._services.transactions.tenant(target_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM agent_transfer_imports
                        WHERE target_tenant_id = :target_tenant_id
                          AND import_id = :import_id
                          AND transfer_kind = 'PROFILE'
                        """
                        ),
                        {"target_tenant_id": tenant_uuid, "import_id": import_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        return _profile_receipt(row, target_tenant_id) if row is not None else None

    async def plan_import(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferCompatibilityReport:
        """Inspect target authorities without changing PostgreSQL or object storage."""

        async with self._services.transactions.tenant(target_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            flow = await self._target_flow(connection, tenant_uuid, bundle)
            flow_compatible = flow is not None
            try:
                await self._target_capability_pin(connection, tenant_uuid, bundle)
            except ValueError:
                capability_pin_compatible = False
            else:
                capability_pin_compatible = True

        harness = bundle.session.harness
        if harness is None:
            harness_compatible = False
        elif self._compatible_harnesses is None:
            harness_compatible = True
        else:
            identity = (harness.adapter, harness.adapter_version, harness.protocol)
            harness_compatible = identity in self._compatible_harnesses
        credential_diagnostics = _credential_rebinding_diagnostics(bundle, credential_rebindings)
        artifact_diagnostics = await self._artifact_diagnostics(
            bundle, target_tenant_id=target_tenant_id
        )
        issues_list: list[str] = []
        if not flow_compatible:
            issues_list.append("target flow revision is unavailable")
        if not capability_pin_compatible:
            issues_list.append("exact target capability pin is unavailable")
        if not harness_compatible:
            issues_list.append("target harness is incompatible or missing")
        issues_list.extend(credential_diagnostics)
        issues_list.extend(artifact_diagnostics)
        issues = tuple(issues_list)
        return SessionTransferCompatibilityReport(
            eligible=not issues,
            mode=bundle.mode,
            sourceTenantId=bundle.source_tenant_id,
            targetTenantId=target_tenant_id,
            bundleDigest=bundle.checksum_sha256,
            flowCompatible=flow_compatible,
            capabilityPinCompatible=capability_pin_compatible,
            harnessCompatible=harness_compatible,
            credentialRebindingDiagnostics=credential_diagnostics,
            artifactDiagnostics=artifact_diagnostics,
            issues=issues,
        )

    async def record_profile_import(
        self,
        target_tenant_id: str,
        bundle: ProfileBundle,
        *,
        actor_id: str,
        import_id: str,
    ) -> ProfileImportReceipt:
        bundle.verify()
        if import_id != bundle.import_id:
            raise ValueError("profile import identity does not match bundle")
        async with self._services.transactions.tenant(target_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            await connection.execute(
                text(
                    """
                    INSERT INTO agent_transfer_imports (
                        import_id, transfer_kind, source_tenant_key, target_tenant_id,
                        bundle_digest, agent_key, agent_revision, result, created_by
                    ) VALUES (
                        :import_id, 'PROFILE', :source_tenant_key, :target_tenant_id,
                        :bundle_digest, :agent_key, :agent_revision,
                        CAST(:result AS jsonb), :created_by
                    )
                    ON CONFLICT (target_tenant_id, import_id) DO NOTHING
                    """
                ),
                {
                    "import_id": import_id,
                    "source_tenant_key": bundle.source_tenant_id,
                    "target_tenant_id": tenant_uuid,
                    "bundle_digest": bundle.checksum_sha256,
                    "agent_key": bundle.agent_key,
                    "agent_revision": bundle.agent_revision,
                    "result": self._services.codec.dumps(
                        {"namespace": bundle.namespace, "resources": len(bundle.resources)}
                    ),
                    "created_by": actor_id,
                },
            )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM agent_transfer_imports
                        WHERE target_tenant_id = :target_tenant_id AND import_id = :import_id
                        """
                        ),
                        {"target_tenant_id": tenant_uuid, "import_id": import_id},
                    )
                )
                .mappings()
                .one()
            )
        if row["transfer_kind"] != "PROFILE" or row["bundle_digest"] != bundle.checksum_sha256:
            raise ValueError("profile import identity was reused with another bundle")
        return _profile_receipt(row, target_tenant_id)

    async def get_import(
        self, target_tenant_id: str, import_id: str
    ) -> SessionTransferImportResult | None:
        async with self._services.transactions.tenant(target_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM agent_transfer_imports
                        WHERE target_tenant_id = :target_tenant_id
                          AND import_id = :import_id
                          AND transfer_kind = 'SESSION'
                        """
                        ),
                        {"target_tenant_id": tenant_uuid, "import_id": import_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
        return _session_result(row, target_tenant_id, already_present=True) if row else None

    async def import_records(
        self,
        target_tenant_id: str,
        bundle: SessionTransferBundle,
        *,
        actor_id: str,
        import_id: str,
        credential_rebindings: dict[str, str] | None = None,
    ) -> SessionTransferImportResult:
        bundle.verify()
        if import_id != bundle.import_id:
            raise ValueError("session import identity does not match bundle")
        async with self._services.transactions.tenant(target_tenant_id) as (
            connection,
            tenant_uuid,
        ):
            existing = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM agent_transfer_imports
                        WHERE target_tenant_id = :target_tenant_id
                          AND import_id = :import_id
                        """
                        ),
                        {"target_tenant_id": tenant_uuid, "import_id": import_id},
                    )
                )
                .mappings()
                .one_or_none()
            )
            if existing is not None:
                if (
                    existing["transfer_kind"] != "SESSION"
                    or existing["bundle_digest"] != bundle.checksum_sha256
                ):
                    raise ValueError("session import identity was reused with another bundle")
                return _session_result(existing, target_tenant_id, already_present=True)

            await self._validate_target_compatibility(
                connection,
                tenant_uuid,
                bundle,
            )
            diagnostics = _credential_rebinding_diagnostics(bundle, credential_rebindings)
            if diagnostics:
                raise ValueError("credential rebinding required: " + "; ".join(diagnostics))
            await self.verify_artifact_references(bundle, target_tenant_id=target_tenant_id)
            mapping = _id_mapping(bundle, target_tenant_id, import_id)
            flow = await self._target_flow(connection, tenant_uuid, bundle)
            target_pin = await self._target_capability_pin(connection, tenant_uuid, bundle)
            if bundle.capability_pin is not None:
                mapping[f"capabilityPin:{bundle.capability_pin.pin_id}"] = str(target_pin)
            await self._insert_execution(connection, tenant_uuid, bundle, mapping, flow, actor_id)
            await self._insert_task_runs(connection, tenant_uuid, bundle, mapping)
            await self._insert_execution_events(connection, tenant_uuid, bundle, mapping)
            if bundle.task_run_events:
                raise ValueError("task-run event association is missing from the transfer contract")
            await self._insert_task_run_events(connection, tenant_uuid, bundle, mapping)
            await self._insert_session(connection, tenant_uuid, bundle, mapping, target_pin)
            await self._insert_session_events(connection, tenant_uuid, bundle, mapping)
            await self._insert_invocations(connection, tenant_uuid, bundle, mapping)
            await self._insert_artifacts(connection, tenant_uuid, bundle, mapping)
            evidence_mapping = await self._insert_evidence(connection, tenant_uuid, bundle, mapping)
            mapping.update(evidence_mapping)
            result_data = {
                "executionId": str(mapping["execution:" + str(bundle.execution.execution_id)]),
                "sessionId": str(mapping["session:" + str(bundle.session.session_id)]),
                "eventCount": len(bundle.events),
                "evidenceCount": len(bundle.evidence_events),
                "idMapping": mapping,
                "credentialRebindingDiagnostics": (),
            }
            await connection.execute(
                text(
                    """
                    INSERT INTO agent_transfer_imports (
                        import_id, transfer_kind, source_tenant_key, target_tenant_id,
                        bundle_digest, session_id, mode, result, created_by
                    ) VALUES (
                        :import_id, 'SESSION', :source_tenant_key, :target_tenant_id,
                        :bundle_digest, :session_id, :mode, CAST(:result AS jsonb), :created_by
                    )
                    ON CONFLICT (target_tenant_id, import_id) DO NOTHING
                    """
                ),
                {
                    "import_id": import_id,
                    "source_tenant_key": bundle.source_tenant_id,
                    "target_tenant_id": tenant_uuid,
                    "bundle_digest": bundle.checksum_sha256,
                    "session_id": UUID(mapping[f"session:{bundle.session.session_id}"]),
                    "mode": bundle.mode.value,
                    "result": self._services.codec.dumps(result_data),
                    "created_by": actor_id,
                },
            )
            row = (
                (
                    await connection.execute(
                        text(
                            """
                        SELECT * FROM agent_transfer_imports
                        WHERE target_tenant_id = :target_tenant_id AND import_id = :import_id
                        """
                        ),
                        {"target_tenant_id": tenant_uuid, "import_id": import_id},
                    )
                )
                .mappings()
                .one()
            )
        if row["transfer_kind"] != "SESSION" or row["bundle_digest"] != bundle.checksum_sha256:
            raise ValueError("session import identity was reused with another bundle")
        return _session_result(row, target_tenant_id, already_present=False)

    async def _validate_target_compatibility(
        self, connection: Any, tenant_uuid: UUID, bundle: SessionTransferBundle
    ) -> None:
        flow = await self._target_flow(connection, tenant_uuid, bundle)
        if flow is None:
            raise ValueError(
                f"target flow {bundle.execution.namespace}.{bundle.execution.flow_id}"
                f"@{bundle.execution.flow_revision} is unavailable"
            )
        await self._target_capability_pin(connection, tenant_uuid, bundle)
        harness = bundle.session.harness
        if harness is not None and self._compatible_harnesses is not None:
            identity = (harness.adapter, harness.adapter_version, harness.protocol)
            if identity not in self._compatible_harnesses:
                raise ValueError(f"target harness is incompatible: {identity!r}")

    async def _target_flow(
        self, connection: Any, tenant_uuid: UUID, bundle: SessionTransferBundle
    ) -> tuple[UUID, UUID] | None:
        row = (
            (
                await connection.execute(
                    text(
                        """
                    SELECT flows.id AS flow_id, revisions.id AS flow_revision_id
                    FROM flows
                    JOIN namespaces ON namespaces.id = flows.namespace_id
                    JOIN flow_revisions AS revisions ON revisions.flow_id = flows.id
                    WHERE flows.tenant_id = :tenant_id
                      AND namespaces.name = :namespace
                      AND flows.flow_key = :flow_key
                      AND revisions.revision = :revision
                    """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": bundle.execution.namespace,
                        "flow_key": bundle.execution.flow_id,
                        "revision": bundle.execution.flow_revision,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return UUID(str(row["flow_id"])), UUID(str(row["flow_revision_id"]))

    async def _target_capability_pin(
        self, connection: Any, tenant_uuid: UUID, bundle: SessionTransferBundle
    ) -> UUID:
        pin = bundle.capability_pin
        if pin is None:
            raise ValueError("exact capability pin is missing")
        row = (
            (
                await connection.execute(
                    text(
                        """
                    SELECT pin_id
                    FROM agent_capability_pins
                    WHERE tenant_id = :tenant_id
                      AND namespace_name = :namespace
                      AND subject_ref = :subject_ref
                      AND envelope_digest = :envelope_digest
                    """
                    ),
                    {
                        "tenant_id": tenant_uuid,
                        "namespace": pin.namespace,
                        "subject_ref": pin.subject_ref,
                        "envelope_digest": pin.envelope_digest,
                    },
                )
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise ValueError(
                f"target capability profile {pin.namespace}:{pin.subject_ref}"
                f"/{pin.envelope_digest} is unavailable"
            )
        return UUID(str(row["pin_id"]))

    async def _insert_execution(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
        flow: tuple[UUID, UUID] | None,
        actor_id: str,
    ) -> None:
        if flow is None:
            raise ValueError("target flow compatibility was not established")
        execution = bundle.execution
        terminal_at = (
            bundle.session.completed_at if bundle.mode.value == "TERMINAL_HISTORY" else None
        )
        await connection.execute(
            text(
                """
                INSERT INTO executions (
                    id, tenant_id, flow_id, flow_revision_id, namespace_name, flow_key,
                    state, epoch, version, idempotency_key, inputs, trigger_context, labels,
                    lifecycle_evidence, created_by, updated_by, created_at, updated_at,
                    timeout_at, terminal_at
                ) VALUES (
                    :id, :tenant_id, :flow_id, :flow_revision_id, :namespace, :flow_key,
                    :state, :epoch, :version, NULL, CAST(:inputs AS jsonb),
                    CAST(:trigger AS jsonb), CAST(:labels AS jsonb),
                    CAST(:lifecycle_evidence AS jsonb), :created_by, :updated_by,
                    :created_at, :updated_at, :timeout_at, :terminal_at
                )
                """
            ),
            {
                "id": UUID(mapping[f"execution:{execution.execution_id}"]),
                "tenant_id": tenant_uuid,
                "flow_id": flow[0],
                "flow_revision_id": flow[1],
                "namespace": execution.namespace,
                "flow_key": execution.flow_id,
                "state": execution.state.value,
                "epoch": execution.epoch,
                "version": execution.version,
                "inputs": self._services.codec.dumps(execution.inputs),
                "trigger": self._services.codec.dumps(execution.trigger),
                "labels": self._services.codec.dumps(execution.labels),
                "lifecycle_evidence": self._services.codec.dumps(execution.lifecycle_evidence),
                "created_by": execution.created_by,
                "updated_by": actor_id,
                "created_at": execution.created_at,
                "updated_at": execution.updated_at,
                "timeout_at": execution.timeout_at,
                "terminal_at": terminal_at,
            },
        )

    async def _insert_task_runs(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        for task in bundle.task_runs:
            await connection.execute(
                text(
                    """
                    INSERT INTO task_runs (
                        id, tenant_id, execution_id, task_path, iteration_key, state,
                        current_attempt, version, retry_at, terminal_result,
                        control_evidence, lifecycle_phase, labels
                    ) VALUES (
                        :id, :tenant_id, :execution_id, :task_path, :iteration_key, :state,
                        :current_attempt, :version, :retry_at, CAST(:result AS jsonb),
                        CAST(:evidence AS jsonb), :lifecycle_phase,
                        CAST(:labels AS jsonb)
                    )
                    """
                ),
                {
                    "id": UUID(mapping[f"task:{task.task_run_id}"]),
                    "tenant_id": tenant_uuid,
                    "execution_id": UUID(mapping[f"execution:{task.execution_id}"]),
                    "task_path": task.task_id,
                    "iteration_key": task.iteration_key,
                    "state": task.state.value,
                    "current_attempt": task.current_attempt,
                    "version": task.version,
                    "retry_at": task.retry_at,
                    "result": (
                        self._services.codec.dumps(task.result) if task.result is not None else None
                    ),
                    "evidence": self._services.codec.dumps(task.evidence),
                    "lifecycle_phase": task.lifecycle_phase.value,
                    "labels": self._services.codec.dumps(task.labels),
                },
            )

    async def _insert_execution_events(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        execution_id = UUID(mapping[f"execution:{bundle.execution.execution_id}"])
        for sequence, event in enumerate(bundle.execution_events, start=1):
            await connection.execute(
                text(
                    """
                    INSERT INTO execution_events (
                        tenant_id, execution_id, sequence, event_id, event_type, schema_version,
                        idempotency_key, correlation_id, causation_id, actor_id, reason,
                        occurred_at, trace_context, payload
                    ) VALUES (
                        :tenant_id, :execution_id, :sequence, :event_id, :event_type, 2,
                        :idempotency_key, :correlation_id, :causation_id, :actor_id, :reason,
                        :occurred_at, CAST(:trace_context AS jsonb), CAST(:payload AS jsonb)
                    )
                    """
                ),
                _event_params(
                    self._services.codec,
                    event,
                    tenant_uuid,
                    execution_id,
                    sequence,
                    mapping,
                    "execution",
                ),
            )

    async def _insert_task_run_events(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        for record in bundle.task_run_event_records:
            event = record.event
            event_id = UUID(mapping[f"task_event:{event.event_id}"])
            execution_id = UUID(mapping[f"execution:{bundle.execution.execution_id}"])
            task_run_id = UUID(mapping[f"task:{record.task_run_id}"])
            correlation_id = UUID(mapping[f"correlation:{event.correlation_id}"])
            await connection.execute(
                text(
                    """
                    INSERT INTO task_run_events (
                        tenant_id, task_run_id, execution_id, sequence, event_id,
                        event_type, schema_version, idempotency_key, correlation_id,
                        causation_id, actor_id, reason, occurred_at, trace_context, payload
                    ) VALUES (
                        :tenant_id, :task_run_id, :execution_id, :sequence, :event_id,
                        :event_type, 1, :idempotency_key, :correlation_id, :causation_id,
                        :actor_id, :reason, :occurred_at, CAST(:trace_context AS jsonb),
                        CAST(:payload AS jsonb)
                    )
                    """
                ),
                {
                    "tenant_id": tenant_uuid,
                    "task_run_id": task_run_id,
                    "execution_id": execution_id,
                    "sequence": record.sequence,
                    "event_id": event_id,
                    "event_type": event.event_type.value,
                    "idempotency_key": event.idempotency_key or str(event_id),
                    "correlation_id": correlation_id,
                    "causation_id": (
                        UUID(mapping[f"causation:{event.causation_id}"])
                        if event.causation_id is not None
                        else None
                    ),
                    "actor_id": event.actor_id,
                    "reason": event.reason,
                    "occurred_at": event.occurred_at,
                    "trace_context": self._services.codec.dumps(event.trace_context),
                    "payload": self._services.codec.dumps(event.payload),
                },
            )

    async def _insert_session(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
        target_pin: UUID,
    ) -> None:
        session = bundle.session
        await connection.execute(
            text(
                """
                INSERT INTO agent_sessions (
                    session_id, tenant_id, namespace_name, execution_id, task_run_id, attempt,
                    capability_pin_id, envelope_digest, harness_adapter, harness_version,
                    harness_protocol, state, phase, version, checkpoint, counters, final_result,
                    error, created_at, updated_at, completed_at
                ) VALUES (
                    :session_id, :tenant_id, :namespace, :execution_id, :task_run_id, :attempt,
                    :capability_pin_id, :envelope_digest, :harness_adapter, :harness_version,
                    :harness_protocol, :state, :phase, :version, CAST(:checkpoint AS jsonb),
                    CAST(:counters AS jsonb), CAST(:final_result AS jsonb), :error,
                    :created_at, :updated_at, :completed_at
                )
                """
            ),
            {
                "session_id": UUID(mapping[f"session:{session.session_id}"]),
                "tenant_id": tenant_uuid,
                "namespace": session.namespace,
                "execution_id": UUID(mapping[f"execution:{session.execution_id}"]),
                "task_run_id": UUID(mapping[f"task:{session.task_run_id}"]),
                "attempt": session.attempt,
                "capability_pin_id": target_pin,
                "envelope_digest": session.envelope_digest,
                "harness_adapter": session.harness.adapter if session.harness else None,
                "harness_version": session.harness.adapter_version if session.harness else None,
                "harness_protocol": session.harness.protocol if session.harness else None,
                "state": session.state.value,
                "phase": session.phase.value,
                "version": session.version,
                "checkpoint": session.checkpoint.model_dump_json(by_alias=True),
                "counters": session.counters.model_dump_json(by_alias=True),
                "final_result": self._services.codec.dumps(session.final_result)
                if session.final_result is not None
                else None,
                "error": session.error,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "completed_at": session.completed_at,
            },
        )

    async def _insert_session_events(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        for event in bundle.events:
            await connection.execute(
                text(
                    """
                    INSERT INTO agent_session_events (
                        event_id, tenant_id, execution_id, task_run_id, session_id,
                        event_index, event_key, event_type, payload, occurred_at
                    ) VALUES (
                        :event_id, :tenant_id, :execution_id, :task_run_id, :session_id,
                        :event_index, :event_key, :event_type, CAST(:payload AS jsonb), :occurred_at
                    )
                    """
                ),
                {
                    "event_id": UUID(mapping[f"session_event:{event.event_id}"]),
                    "tenant_id": tenant_uuid,
                    "execution_id": UUID(mapping[f"execution:{bundle.execution.execution_id}"]),
                    "task_run_id": UUID(mapping[f"task:{bundle.session.task_run_id}"]),
                    "session_id": UUID(mapping[f"session:{bundle.session.session_id}"]),
                    "event_index": event.event_index,
                    "event_key": event.event_key,
                    "event_type": event.event_type,
                    "payload": self._services.codec.dumps(event.payload),
                    "occurred_at": event.occurred_at,
                },
            )

    async def _insert_invocations(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        for invocation in bundle.invocations:
            await connection.execute(
                text(
                    """
                    INSERT INTO agent_invocations (
                        invocation_id, tenant_id, namespace_name, execution_id, task_run_id,
                        attempt, kind, operation, state, request_hash, request_metadata,
                        accounting, result, error, started_at, completed_at
                    ) VALUES (
                        :invocation_id, :tenant_id, :namespace, :execution_id, :task_run_id,
                        :attempt, :kind, :operation, :state, :request_hash,
                        CAST(:request_metadata AS jsonb), CAST(:accounting AS jsonb),
                        CAST(:result AS jsonb), :error, :started_at, :completed_at
                    )
                    """
                ),
                {
                    "invocation_id": UUID(mapping[f"invocation:{invocation.invocation_id}"]),
                    "tenant_id": tenant_uuid,
                    "namespace": invocation.namespace,
                    "execution_id": UUID(mapping[f"execution:{invocation.execution_id}"]),
                    "task_run_id": UUID(mapping[f"task:{invocation.task_run_id}"]),
                    "attempt": invocation.attempt,
                    "kind": invocation.kind.value,
                    "operation": invocation.operation,
                    "state": invocation.state.value,
                    "request_hash": invocation.request_hash,
                    "request_metadata": self._services.codec.dumps(invocation.request_metadata),
                    "accounting": (
                        invocation.accounting.model_dump_json(by_alias=True)
                        if invocation.accounting is not None
                        else None
                    ),
                    "result": self._services.codec.dumps(invocation.result)
                    if invocation.result is not None
                    else None,
                    "error": invocation.error,
                    "started_at": invocation.started_at,
                    "completed_at": invocation.completed_at,
                },
            )

    async def _insert_artifacts(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> None:
        for artifact in bundle.artifacts:
            await connection.execute(
                text(
                    """
                    INSERT INTO execution_artifacts (
                        id, tenant_id, execution_id, task_run_id, attempt, uri, size_bytes,
                        media_type, checksum_sha256, logical_path, lineage, occurred_at, ingested_at
                    ) VALUES (
                        :id, :tenant_id, :execution_id, :task_run_id, :attempt, :uri, :size_bytes,
                        :media_type, :checksum_sha256, :logical_path, CAST(:lineage AS jsonb),
                        :occurred_at, :ingested_at
                    )
                    """
                ),
                {
                    "id": UUID(mapping[f"artifact:{artifact.artifact_id}"]),
                    "tenant_id": tenant_uuid,
                    "execution_id": UUID(mapping[f"execution:{artifact.execution_id}"]),
                    "task_run_id": UUID(mapping[f"task:{artifact.task_run_id}"]),
                    "attempt": artifact.attempt,
                    "uri": bundle.artifact_destination_refs[artifact.uri],
                    "size_bytes": artifact.size_bytes,
                    "media_type": artifact.media_type,
                    "checksum_sha256": artifact.checksum_sha256,
                    "logical_path": artifact.logical_path,
                    "lineage": self._services.codec.dumps(artifact.lineage),
                    "occurred_at": artifact.occurred_at,
                    "ingested_at": artifact.ingested_at,
                },
            )

    async def _insert_evidence(
        self,
        connection: Any,
        tenant_uuid: UUID,
        bundle: SessionTransferBundle,
        mapping: dict[str, str],
    ) -> dict[str, str]:
        evidence_mapping: dict[str, str] = {}
        for evidence in bundle.evidence_events:
            event_id = UUID(mapping[f"evidence:{evidence.event_id}"])
            await connection.execute(
                text(
                    """
                    INSERT INTO execution_evidence_events (
                        event_id, tenant_id, execution_id, task_run_id, kind, event_type,
                        payload, occurred_at, ingested_at
                    ) VALUES (
                        :event_id, :tenant_id, :execution_id, :task_run_id, :kind, :event_type,
                        CAST(:payload AS jsonb), :occurred_at, :ingested_at
                    ) ON CONFLICT (tenant_id, event_id) DO NOTHING
                    """
                ),
                {
                    "event_id": event_id,
                    "tenant_id": tenant_uuid,
                    "execution_id": UUID(mapping[f"execution:{evidence.execution_id}"]),
                    "task_run_id": (
                        UUID(mapping[f"task:{evidence.task_run_id}"])
                        if evidence.task_run_id is not None
                        else None
                    ),
                    "kind": evidence.kind.value,
                    "event_type": evidence.event_type,
                    "payload": self._services.codec.dumps(evidence.payload),
                    "occurred_at": evidence.occurred_at,
                    "ingested_at": evidence.ingested_at,
                },
            )
            cursor = await connection.scalar(
                text(
                    """
                    SELECT cursor FROM execution_evidence_events
                    WHERE tenant_id = :tenant_id AND event_id = :event_id
                    """
                ),
                {"tenant_id": tenant_uuid, "event_id": event_id},
            )
            if cursor is None:
                raise RuntimeError("imported evidence event disappeared before cursor mapping")
            evidence_mapping[f"evidenceCursor:{evidence.cursor}"] = str(cursor)
        return evidence_mapping

    async def verify_artifact_references(
        self, bundle: SessionTransferBundle, *, target_tenant_id: str
    ) -> None:
        if not bundle.artifacts:
            return
        if self._object_store is None:
            raise ValueError("artifact verification requires an object-storage authority")
        for artifact in bundle.artifacts:
            destination = bundle.artifact_destination_refs.get(artifact.uri)
            if destination is None:
                raise ValueError(f"artifact {artifact.uri} has no destination reference")
            metadata = await self._object_store.head(target_tenant_id, destination)
            if (
                metadata.size != artifact.size_bytes
                or metadata.checksum_sha256 != artifact.checksum_sha256
                or metadata.tenant_id != target_tenant_id
            ):
                raise ValueError(f"artifact {artifact.uri} failed size/checksum verification")

    async def _artifact_diagnostics(
        self, bundle: SessionTransferBundle, *, target_tenant_id: str
    ) -> tuple[str, ...]:
        try:
            await self.verify_artifact_references(bundle, target_tenant_id=target_tenant_id)
        except ValueError as exc:
            return (str(exc),)
        return ()


def _profile_receipt(row: Any, target_tenant_id: str) -> ProfileImportReceipt:
    return ProfileImportReceipt(
        importId=row["import_id"],
        bundleDigest=row["bundle_digest"],
        targetTenantId=target_tenant_id,
        agentKey=row["agent_key"],
        agentRevision=row["agent_revision"],
        createdAt=row["created_at"],
    )


def _persisted_task_run(row: Any) -> PersistedTaskRun:
    return PersistedTaskRun(
        task_run_id=row["id"],
        execution_id=row["execution_id"],
        task_id=row["task_path"],
        iteration_key=row.get("iteration_key"),
        state=row["state"],
        current_attempt=row["current_attempt"],
        version=row["version"],
        retry_at=row.get("retry_at"),
        result=row.get("result") if row.get("result") is not None else row.get("terminal_result"),
        failure_category=row.get("failure_category"),
        evidence=row.get("evidence") or row.get("control_evidence") or {},
        lifecycle_phase=TaskRunLifecyclePhase(row.get("lifecycle_phase") or "MAIN"),
        labels=row.get("labels") or {},
    )


def _execution_event(row: Any) -> ExecutionEvent:
    return ExecutionEvent(
        event_id=row["event_id"],
        event_type=row["event_type"],
        schema_version=row["schema_version"],
        idempotency_key=row.get("idempotency_key"),
        occurred_at=row["occurred_at"],
        correlation_id=row["correlation_id"],
        causation_id=row.get("causation_id"),
        actor_id=row["actor_id"],
        reason=row.get("reason"),
        trace_context=row.get("trace_context") or {},
        payload=row.get("payload") or {},
    )


def _task_run_event(row: Any) -> TaskRunEvent:
    return TaskRunEvent(
        event_id=row["event_id"],
        event_type=row["event_type"],
        schema_version=row["schema_version"],
        idempotency_key=row.get("idempotency_key"),
        occurred_at=row["occurred_at"],
        correlation_id=row["correlation_id"],
        causation_id=row.get("causation_id"),
        actor_id=row["actor_id"],
        reason=row.get("reason"),
        trace_context=row.get("trace_context") or {},
        payload=row.get("payload") or {},
    )


def _invocation(row: Any, tenant_id: str) -> AgentInvocationRecord:
    return AgentInvocationRecord(
        invocationId=row["invocation_id"],
        tenantId=tenant_id,
        namespace=row["namespace_name"],
        executionId=row["execution_id"],
        taskRunId=row["task_run_id"],
        attempt=row["attempt"],
        kind=row["kind"],
        operation=row["operation"],
        requestHash=row["request_hash"],
        requestMetadata=row.get("request_metadata") or {},
        state=row["state"],
        accounting=row.get("accounting"),
        result=row.get("result"),
        error=row.get("error"),
        startedAt=row["started_at"],
        completedAt=row.get("completed_at"),
    )


def _evidence_event(row: Any) -> ExecutionEvidenceEvent:
    return ExecutionEvidenceEvent(
        cursor=row["cursor"],
        event_id=row["event_id"],
        execution_id=row["execution_id"],
        task_run_id=row.get("task_run_id"),
        kind=row["kind"],
        event_type=row["event_type"],
        payload=row["payload"],
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _artifact(row: Any) -> ExecutionArtifact:
    return ExecutionArtifact(
        artifact_id=row["id"],
        execution_id=row["execution_id"],
        task_run_id=row["task_run_id"],
        attempt=row["attempt"],
        uri=row["uri"],
        size_bytes=row["size_bytes"],
        media_type=row.get("media_type"),
        checksum_sha256=row.get("checksum_sha256"),
        logical_path=row.get("logical_path"),
        lineage=tuple(row.get("lineage") or ()),
        occurred_at=row["occurred_at"],
        ingested_at=row["ingested_at"],
    )


def _session_result(
    row: Any,
    target_tenant_id: str,
    *,
    already_present: bool,
) -> SessionTransferImportResult:
    return SessionTransferImportResult(
        importId=row["import_id"],
        bundleDigest=row["bundle_digest"],
        mode=row["mode"],
        targetTenantId=target_tenant_id,
        sessionId=str(row["session_id"]),
        alreadyPresent=already_present,
        idMapping=(row.get("result") or {}).get("idMapping", {}),
        credentialRebindingDiagnostics=tuple(
            (row.get("result") or {}).get("credentialRebindingDiagnostics", ())
        ),
    )


def _id_mapping(
    bundle: SessionTransferBundle, target_tenant_id: str, import_id: str
) -> dict[str, str]:
    mapping: dict[str, str] = {}

    def add(label: str, value: UUID) -> None:
        mapping[f"{label}:{value}"] = str(
            uuid5(_TRANSFER_NAMESPACE, f"{target_tenant_id}:{import_id}:{label}:{value}")
        )

    add("execution", bundle.execution.execution_id)
    add("session", bundle.session.session_id)
    add("capabilityPin", bundle.capability_pin.pin_id if bundle.capability_pin else UUID(int=0))
    for task in bundle.task_runs:
        add("task", task.task_run_id)
    for session_event in bundle.events:
        add("session_event", session_event.event_id)
    for execution_event in bundle.execution_events:
        add("execution_event", execution_event.event_id)
        add("correlation", execution_event.correlation_id)
        if execution_event.causation_id is not None:
            add("causation", execution_event.causation_id)
    for task_event_record in bundle.task_run_event_records:
        add("task_event", task_event_record.event.event_id)
        add("correlation", task_event_record.event.correlation_id)
        if task_event_record.event.causation_id is not None:
            add("causation", task_event_record.event.causation_id)
    for invocation in bundle.invocations:
        add("invocation", invocation.invocation_id)
    for artifact in bundle.artifacts:
        add("artifact", artifact.artifact_id)
    for evidence in bundle.evidence_events:
        shared_id = (
            mapping.get(f"execution_event:{evidence.event_id}")
            or mapping.get(f"session_event:{evidence.event_id}")
            or mapping.get(f"task_event:{evidence.event_id}")
            or mapping.get(f"artifact:{evidence.event_id}")
        )
        if shared_id is None:
            add("evidence", evidence.event_id)
        else:
            mapping[f"evidence:{evidence.event_id}"] = shared_id
    return mapping


def _event_params(
    codec: JsonCodec,
    event: Any,
    tenant_uuid: UUID,
    execution_id: UUID,
    sequence: int,
    mapping: dict[str, str],
    label: str,
) -> dict[str, Any]:
    event_id = UUID(mapping[f"{label}_event:{event.event_id}"])
    correlation = UUID(mapping[f"correlation:{event.correlation_id}"])
    causation = (
        UUID(mapping[f"causation:{event.causation_id}"]) if event.causation_id is not None else None
    )
    return {
        "tenant_id": tenant_uuid,
        "execution_id": execution_id,
        "sequence": sequence,
        "event_id": event_id,
        "event_type": event.event_type.value,
        "idempotency_key": event.idempotency_key or str(event_id),
        "correlation_id": correlation,
        "causation_id": causation,
        "actor_id": event.actor_id,
        "reason": event.reason,
        "occurred_at": event.occurred_at,
        "trace_context": codec.dumps(event.trace_context),
        "payload": codec.dumps(event.payload),
    }


def _credential_rebinding_diagnostics(
    bundle: SessionTransferBundle, rebindings: dict[str, str] | None
) -> tuple[str, ...]:
    references: set[str] = set()

    def walk(value: Any, key: str | None = None) -> None:
        if isinstance(value, dict):
            for name, item in value.items():
                normalized = str(name).replace("-", "_").lower()
                if normalized in {"credentialref", "credential_ref"} and isinstance(item, str):
                    references.add(item)
                walk(item, normalized)
        elif isinstance(value, list):
            for item in value:
                walk(item, key)

    walk(bundle.model_dump(mode="json", by_alias=True))
    if not references:
        return ()
    rebindings = rebindings or {}
    diagnostics: list[str] = []
    for reference in sorted(references):
        if reference not in rebindings:
            diagnostics.append(
                f"credential reference {reference!r} requires explicit target rebinding"
            )
        elif rebindings[reference] != reference:
            diagnostics.append(
                f"credential reference {reference!r} cannot be renamed; "
                "the target must acknowledge the same stable reference"
            )
    return tuple(diagnostics)


__all__ = ["PostgresTransferRepository"]
