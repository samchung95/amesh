from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tests.test_session_transfer import _bundle as session_bundle

from amesh.adapters.postgres import (
    PostgresAgentSessionRepository,
    PostgresExecutionRepository,
    PostgresTenantRepository,
    PostgresTransferRepository,
)
from amesh.adapters.postgres.tenant_context import tenant_transaction
from amesh.domain import (
    AgentInvocationAccounting,
    AgentInvocationState,
    AgentProgressActivity,
    AgentProgressFrame,
    AgentProgressLimits,
    AgentProgressStatus,
    AgentResourceKind,
    AgentResourceRevision,
    PromptSpec,
    TenantDefinition,
)
from amesh.domain.resources import canonical_json
from amesh.dsl import FlowDefinition
from amesh.ports import AgentProgressContext
from amesh.ports.object_store import ObjectMetadata
from amesh.profile_transfer import ProfileBundle
from amesh.session_transfer import SessionTransferMode, SessionTransferService, seal_bundle

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class _ArtifactStore:
    async def head(self, tenant_id: str, uri: str) -> ObjectMetadata:
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=12,
            checksum_sha256="a" * 64,
        )


def _profile_bundle(title: str) -> ProfileBundle:
    now = datetime.now(UTC)
    resource = AgentResourceRevision(
        tenantId="source",
        namespace="agents.transfer",
        kind=AgentResourceKind.PROMPT,
        key="prompt",
        revision=1,
        digest="sha256:" + "0" * 64,
        spec=PromptSpec(
            key="prompt",
            namespace="agents.transfer",
            title=title,
            content="portable prompt",
        ),
        createdBy="test:transfer",
        createdAt=now,
    )
    unsigned = ProfileBundle(
        sourceTenantId="source",
        namespace="agents.transfer",
        agentKey="assistant",
        agentRevision=1,
        resources=(resource,),
        checksumSha256="0" * 64,
    )
    payload = unsigned.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
    checksum = hashlib.sha256(canonical_json(payload)).hexdigest()
    return unsigned.model_copy(update={"checksum_sha256": checksum})


def test_transfer_import_ledger_isolated_idempotent_and_digest_bound(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            await PostgresTenantRepository(engine).create(
                TenantDefinition(slug="transfer-other", display_name="Transfer other"),
                actor_id="test:transfer",
            )
            repository = PostgresTransferRepository(engine)
            bundle = _profile_bundle("first")

            first = await repository.record_profile_import(
                "default", bundle, actor_id="test:transfer", import_id=bundle.import_id
            )
            duplicate = await repository.record_profile_import(
                "default", bundle, actor_id="test:transfer", import_id=bundle.import_id
            )
            assert duplicate.import_id == first.import_id
            assert duplicate.bundle_digest == first.bundle_digest
            assert duplicate.created_at == first.created_at

            other = await repository.record_profile_import(
                "transfer-other", bundle, actor_id="test:transfer", import_id=bundle.import_id
            )
            assert other.target_tenant_id == "transfer-other"
            assert (await repository.get_profile_import("default", bundle.import_id)) == first

            conflicting = _profile_bundle("changed")
            with pytest.raises(ValueError, match="reused with another bundle"):
                await repository.record_profile_import(
                    "default",
                    conflicting,
                    actor_id="test:transfer",
                    import_id=bundle.import_id,
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_session_export_import_round_trip_maps_ids_and_is_idempotent(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            await PostgresTenantRepository(engine).create(
                TenantDefinition(slug="transfer-other", display_name="Transfer other"),
                actor_id="test:transfer",
            )
            from amesh.adapters.postgres.execution_repository import PostgresExecutionRepository
            from amesh.dsl import FlowDefinition

            flow = FlowDefinition.model_validate(
                {
                    "id": "flow",
                    "namespace": "agents.demo",
                    "tasks": [{"id": "agent", "type": "core.log", "message": "x"}],
                }
            )
            executions = PostgresExecutionRepository(engine)
            await executions.apply_flow(flow, tenant_id="default")
            await executions.apply_flow(flow, tenant_id="transfer-other")
            accounting = AgentInvocationAccounting(
                inputTokens=12,
                outputTokens=8,
                reasoningTokens=5,
                totalTokens=20,
                cacheReadTokens=4,
                cacheWriteTokens=1,
                costState="billed",
                costAmountUsd="0.0002",
            )
            source = session_bundle(
                invocation_state=AgentInvocationState.IN_DOUBT,
                invocation_accounting=accounting,
            )
            trigger = {"ameshAgentSessionId": "public-service-session"}
            source = source.model_copy(
                update={"execution": source.execution.model_copy(update={"trigger": trigger})}
            )
            pin = source.capability_pin
            assert pin is not None
            now = source.session.created_at

            async def seed(tenant: str, resource_id, *, include_records: bool = True) -> None:
                pin_id = pin.pin_id if include_records else uuid4()
                async with tenant_transaction(engine, tenant) as (connection, tenant_uuid):
                    flow_row = (
                        (
                            await connection.execute(
                                text(
                                    "SELECT flows.id, revisions.id AS revision_id FROM flows "
                                    "JOIN namespaces ON namespaces.id = flows.namespace_id "
                                    "JOIN flow_revisions revisions ON revisions.flow_id = flows.id "
                                    "WHERE flows.tenant_id = :tenant_id AND namespaces.name = 'agents.demo' "
                                    "AND flows.flow_key = 'flow' AND revisions.revision = 1"
                                ),
                                {"tenant_id": tenant_uuid},
                            )
                        )
                        .mappings()
                        .one()
                    )
                    await connection.execute(
                        text(
                            "INSERT INTO agent_resource_revisions "
                            "(resource_id, revision, tenant_id, namespace_name, resource_kind, "
                            "resource_key, digest, spec, created_by) VALUES "
                            "(:id, 1, :tenant_id, 'agents.demo', 'PROMPT', 'prompt', :digest, '{}'::jsonb, 'test')"
                        ),
                        {
                            "id": resource_id,
                            "tenant_id": tenant_uuid,
                            "digest": pin.envelope.agent.digest,
                        },
                    )
                    await connection.execute(
                        text(
                            "INSERT INTO agent_capability_pins "
                            "(pin_id, tenant_id, namespace_name, agent_resource_id, agent_revision, "
                            "subject_ref, envelope_digest, envelope, created_by) VALUES "
                            "(:pin_id, :tenant_id, 'agents.demo', :resource_id, 1, 'session', "
                            ":digest, CAST(:envelope AS jsonb), 'test')"
                        ),
                        {
                            "pin_id": pin_id,
                            "tenant_id": tenant_uuid,
                            "resource_id": resource_id,
                            "digest": pin.envelope_digest,
                            "envelope": pin.envelope.model_dump_json(by_alias=True),
                        },
                    )
                    if not include_records:
                        return
                    execution = source.execution
                    await connection.execute(
                        text(
                            "INSERT INTO executions "
                            "(id, tenant_id, flow_id, flow_revision_id, namespace_name, flow_key, state, "
                            "epoch, version, inputs, trigger_context, labels, lifecycle_evidence, created_by, "
                            "updated_by, created_at, updated_at, terminal_at) VALUES "
                            "(:id, :tenant_id, :flow_id, :revision_id, :namespace, :flow_key, 'SUCCESS', "
                            ":epoch, :version, '{}'::jsonb, CAST(:trigger AS jsonb), '{}'::jsonb, '{}'::jsonb, "
                            "'test', 'test', :created_at, :updated_at, :terminal_at)"
                        ),
                        {
                            "id": execution.execution_id,
                            "tenant_id": tenant_uuid,
                            "flow_id": flow_row["id"],
                            "revision_id": flow_row["revision_id"],
                            "namespace": execution.namespace,
                            "flow_key": execution.flow_id,
                            "epoch": execution.epoch,
                            "version": execution.version,
                            "trigger": json.dumps(trigger),
                            "created_at": now,
                            "updated_at": now,
                            "terminal_at": now,
                        },
                    )
                    task = source.task_runs[0]
                    await connection.execute(
                        text(
                            "INSERT INTO task_runs "
                            "(id, tenant_id, execution_id, task_path, state, current_attempt, version, "
                            "terminal_result, control_evidence, lifecycle_phase, labels) VALUES "
                            "(:id, :tenant_id, :execution_id, :task_path, 'SUCCESS', 1, 1, '{}'::jsonb, "
                            "'{}'::jsonb, 'MAIN', '{}'::jsonb)"
                        ),
                        {
                            "id": task.task_run_id,
                            "tenant_id": tenant_uuid,
                            "execution_id": execution.execution_id,
                            "task_path": task.task_id,
                        },
                    )
                    await connection.execute(
                        text(
                            "INSERT INTO agent_sessions "
                            "(session_id, tenant_id, namespace_name, execution_id, task_run_id, attempt, "
                            "capability_pin_id, envelope_digest, harness_adapter, harness_version, harness_protocol, "
                            "state, phase, version, checkpoint, counters, final_result, created_at, updated_at, completed_at) "
                            "VALUES (:session_id, :tenant_id, 'agents.demo', :execution_id, :task_run_id, 1, "
                            ":pin_id, :digest, 'pi', '1', 'v1', 'SUCCEEDED', 'COMPLETE', 2, '{}'::jsonb, "
                            "'{}'::jsonb, CAST(:final_result AS jsonb), :created_at, :updated_at, :completed_at)"
                        ),
                        {
                            "session_id": source.session.session_id,
                            "tenant_id": tenant_uuid,
                            "execution_id": execution.execution_id,
                            "task_run_id": task.task_run_id,
                            "pin_id": pin_id,
                            "digest": pin.envelope_digest,
                            "final_result": json.dumps({"ok": True}),
                            "created_at": now,
                            "updated_at": now,
                            "completed_at": now,
                        },
                    )
                    for event in source.events:
                        await connection.execute(
                            text(
                                "INSERT INTO agent_session_events "
                                "(event_id, tenant_id, execution_id, task_run_id, session_id, event_index, "
                                "event_key, event_type, payload, occurred_at) VALUES "
                                "(:event_id, :tenant_id, :execution_id, :task_run_id, :session_id, :event_index, "
                                ":event_key, :event_type, '{}'::jsonb, :occurred_at)"
                            ),
                            {
                                "event_id": event.event_id,
                                "tenant_id": tenant_uuid,
                                "execution_id": execution.execution_id,
                                "task_run_id": source.task_runs[0].task_run_id,
                                "session_id": source.session.session_id,
                                "event_index": event.event_index,
                                "event_key": event.event_key,
                                "event_type": event.event_type,
                                "occurred_at": event.occurred_at,
                            },
                        )
                    for invocation in source.invocations:
                        await connection.execute(
                            text(
                                "INSERT INTO agent_invocations "
                                "(invocation_id, tenant_id, namespace_name, execution_id, task_run_id, "
                                "attempt, kind, operation, state, request_hash, request_metadata, "
                                "accounting, error, started_at, completed_at) VALUES "
                                "(:invocation_id, :tenant_id, :namespace, :execution_id, :task_run_id, "
                                ":attempt, :kind, :operation, :state, :request_hash, '{}'::jsonb, "
                                "CAST(:accounting AS jsonb), :error, :started_at, :completed_at)"
                            ),
                            {
                                "invocation_id": invocation.invocation_id,
                                "tenant_id": tenant_uuid,
                                "namespace": invocation.namespace,
                                "execution_id": invocation.execution_id,
                                "task_run_id": invocation.task_run_id,
                                "attempt": invocation.attempt,
                                "kind": invocation.kind.value,
                                "operation": invocation.operation,
                                "state": invocation.state.value,
                                "request_hash": invocation.request_hash,
                                "accounting": invocation.accounting.model_dump_json(by_alias=True)
                                if invocation.accounting is not None
                                else None,
                                "error": "provider outcome is unknown",
                                "started_at": invocation.started_at,
                                "completed_at": invocation.completed_at,
                            },
                        )
                    await connection.execute(
                        text(
                            "INSERT INTO execution_artifacts "
                            "(id, tenant_id, execution_id, task_run_id, attempt, uri, size_bytes, "
                            "media_type, checksum_sha256, occurred_at) VALUES "
                            "(:id, :tenant_id, :execution_id, :task_run_id, 1, "
                            "'s3://shared/result.json', 12, 'application/json', :checksum, :occurred_at)"
                        ),
                        {
                            "id": uuid4(),
                            "tenant_id": tenant_uuid,
                            "execution_id": execution.execution_id,
                            "task_run_id": task.task_run_id,
                            "checksum": "a" * 64,
                            "occurred_at": now,
                        },
                    )

            await seed("default", pin.envelope.agent.resource_id)
            target_resource_id = uuid4()
            # A target profile has the same immutable envelope digest but a tenant-local resource identity.
            await seed("transfer-other", target_resource_id, include_records=False)
            repository = PostgresTransferRepository(
                engine,
                object_store=_ArtifactStore(),
                compatible_harnesses={("pi", "1", "v1")},
            )
            exported = await repository.export_session_bundle(
                "default", source.session.session_id, mode=SessionTransferMode.TERMINAL_HISTORY
            )
            assert exported.invocations[0].state is AgentInvocationState.IN_DOUBT
            assert exported.invocations[0].accounting == accounting
            assert exported.execution.trigger["ameshAgentSessionId"] == "public-service-session"
            assert exported.artifact_destination_refs == {
                "s3://shared/result.json": "s3://shared/result.json"
            }
            artifact_evidence = [
                item for item in exported.evidence_events if item.event_type == "artifact.created"
            ]
            assert [item.event_id for item in artifact_evidence] == [
                exported.artifacts[0].artifact_id
            ]
            plan = await repository.plan_import("transfer-other", exported)
            assert plan.eligible is True
            assert plan.flow_compatible is True
            assert plan.capability_pin_compatible is True
            assert plan.harness_compatible is True
            failing = PostgresTransferRepository(engine, object_store=_ArtifactStore())

            async def inject_failure(*args, **kwargs):
                raise RuntimeError("injected transfer failure")

            failing._insert_session = inject_failure
            with pytest.raises(RuntimeError, match="injected transfer failure"):
                await failing.import_records(
                    "transfer-other",
                    exported,
                    actor_id="test:transfer",
                    import_id=exported.import_id,
                )
            async with tenant_transaction(engine, "transfer-other") as (connection, _):
                rollback_counts = await connection.execute(
                    text(
                        "SELECT (SELECT count(*) FROM executions WHERE trigger_context->>'ameshAgentSessionId' = "
                        "'public-service-session'), (SELECT count(*) FROM agent_transfer_imports "
                        "WHERE import_id = :import_id)"
                    ),
                    {"import_id": exported.import_id},
                )
                assert tuple(rollback_counts.one()) == (0, 0)
            service = SessionTransferService(repository)
            first = await service.import_bundle(
                exported, target_tenant_id="transfer-other", actor_id="test:transfer"
            )
            second = await service.import_bundle(
                exported, target_tenant_id="transfer-other", actor_id="test:transfer"
            )
            assert first.already_present is False
            assert second.already_present is True
            assert first.id_mapping == second.id_mapping
            assert first.session_id != str(exported.session.session_id)
            source_artifact_id = exported.artifacts[0].artifact_id
            assert (
                first.id_mapping[f"artifact:{source_artifact_id}"]
                == first.id_mapping[f"evidence:{source_artifact_id}"]
            )
            async with tenant_transaction(engine, "transfer-other") as (connection, _):
                counts = await connection.execute(
                    text(
                        "SELECT (SELECT count(*) FROM executions WHERE trigger_context->>'ameshAgentSessionId' = "
                        "'public-service-session'), (SELECT count(*) FROM agent_sessions WHERE session_id = :session_id), "
                        "(SELECT count(*) FROM agent_session_events WHERE session_id = :session_id), "
                        "(SELECT count(*) FROM task_runs WHERE execution_id = "
                        "(SELECT execution_id FROM agent_sessions WHERE session_id = :session_id)), "
                        "(SELECT count(*) FROM execution_evidence_events WHERE execution_id = "
                        "(SELECT execution_id FROM agent_sessions WHERE session_id = :session_id)), "
                        "(SELECT count(*) FROM execution_artifacts WHERE execution_id = "
                        "(SELECT execution_id FROM agent_sessions WHERE session_id = :session_id)), "
                        "(SELECT count(*) FROM agent_invocations WHERE execution_id = "
                        "(SELECT execution_id FROM agent_sessions WHERE session_id = :session_id))"
                    ),
                    {"session_id": first.session_id},
                )
                row = counts.one()
                evidence_types = (
                    await connection.execute(
                        text(
                            "SELECT event_type, event_id FROM execution_evidence_events "
                            "WHERE execution_id = (SELECT execution_id FROM agent_sessions "
                            "WHERE session_id = :session_id) ORDER BY cursor"
                        ),
                        {"session_id": first.session_id},
                    )
                ).all()
                assert tuple(row) == (1, 1, 2, 1, 3, 1, 1), evidence_types
                imported_invocation = (
                    (
                        await connection.execute(
                            text(
                                "SELECT state, accounting FROM agent_invocations WHERE execution_id = "
                                "(SELECT execution_id FROM agent_sessions WHERE session_id = :session_id)"
                            ),
                            {"session_id": first.session_id},
                        )
                    )
                    .mappings()
                    .one()
                )
                assert imported_invocation["state"] == "IN_DOUBT"
                assert imported_invocation["accounting"]["reasoningTokens"] == 5
                session_indexes = await connection.execute(
                    text(
                        "SELECT event_index FROM agent_session_events "
                        "WHERE session_id = :session_id ORDER BY event_index"
                    ),
                    {"session_id": first.session_id},
                )
                assert [item[0] for item in session_indexes] == [1, 2]
                evidence_cursors = await connection.execute(
                    text(
                        "SELECT cursor FROM execution_evidence_events "
                        "WHERE execution_id = (SELECT execution_id FROM agent_sessions "
                        "WHERE session_id = :session_id) ORDER BY cursor"
                    ),
                    {"session_id": first.session_id},
                )
                cursors = [item[0] for item in evidence_cursors]
                assert cursors == list(range(cursors[0], cursors[0] + len(cursors)))
                assert "evidenceCursor:1" in first.id_mapping
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_running_session_import_rebuilds_progress_before_next_append(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        target_tenant = f"transfer-progress-{uuid4().hex[:12]}"
        try:
            await PostgresTenantRepository(engine).create(
                TenantDefinition(slug=target_tenant, display_name="Transfer progress"),
                actor_id="test:transfer",
            )
            flow = FlowDefinition.model_validate(
                {
                    "id": "flow",
                    "namespace": "agents.demo",
                    "tasks": [{"id": "agent", "type": "core.log", "message": "x"}],
                }
            )
            await PostgresExecutionRepository(engine).apply_flow(flow, tenant_id=target_tenant)

            bundle = session_bundle(
                SessionTransferMode.CLEAN_CHECKPOINT,
                event_indices=(1, 2, 3),
            )
            base_time = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)
            closed_segment_id = uuid4()
            active_segment_id = uuid4()
            frames = (
                AgentProgressFrame(
                    attemptSessionId=bundle.session.session_id,
                    attempt=1,
                    activity=AgentProgressActivity.THINKING,
                    status=AgentProgressStatus.STARTED,
                    activityId="thinking:closed",
                    segmentId=closed_segment_id,
                    sourceId="provider:transfer",
                    sourceSequence=1,
                    occurredAt=base_time,
                ),
                AgentProgressFrame(
                    attemptSessionId=bundle.session.session_id,
                    attempt=1,
                    activity=AgentProgressActivity.THINKING,
                    status=AgentProgressStatus.COMPLETED,
                    activityId="thinking:closed",
                    segmentId=closed_segment_id,
                    sourceId="provider:transfer",
                    sourceSequence=2,
                    occurredAt=base_time + timedelta(milliseconds=100),
                ),
                AgentProgressFrame(
                    attemptSessionId=bundle.session.session_id,
                    attempt=1,
                    activity=AgentProgressActivity.THINKING,
                    status=AgentProgressStatus.STARTED,
                    activityId="thinking:active",
                    segmentId=active_segment_id,
                    sourceId="provider:transfer",
                    sourceSequence=3,
                    occurredAt=base_time + timedelta(milliseconds=200),
                ),
            )
            events = tuple(
                event.model_copy(
                    update={
                        "event_key": frame.event_key,
                        "event_type": "progress.frame",
                        "payload": {
                            "schemaVersion": "amesh.agent-progress/v1",
                            "frame": frame.model_dump(mode="json", by_alias=True),
                        },
                        "occurred_at": frame.occurred_at,
                    }
                )
                for event, frame in zip(bundle.events, frames, strict=True)
            )
            bundle = seal_bundle(
                bundle.model_copy(update={"events": events, "checksum_sha256": "0" * 64})
            )
            pin = bundle.capability_pin
            assert pin is not None
            target_resource_id = uuid4()
            async with tenant_transaction(engine, target_tenant) as (connection, tenant_uuid):
                await connection.execute(
                    text(
                        """
                        INSERT INTO agent_resource_revisions (
                            resource_id, revision, tenant_id, namespace_name, resource_kind,
                            resource_key, digest, spec, created_by
                        ) VALUES (
                            :resource_id, 1, :tenant_id, 'agents.demo', 'PROMPT',
                            'prompt', :digest, '{}'::jsonb, 'test'
                        )
                        """
                    ),
                    {
                        "resource_id": target_resource_id,
                        "tenant_id": tenant_uuid,
                        "digest": pin.envelope.agent.digest,
                    },
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO agent_capability_pins (
                            pin_id, tenant_id, namespace_name, agent_resource_id,
                            agent_revision, subject_ref, envelope_digest, envelope, created_by
                        ) VALUES (
                            :pin_id, :tenant_id, 'agents.demo', :resource_id,
                            1, 'session', :digest, CAST(:envelope AS jsonb), 'test'
                        )
                        """
                    ),
                    {
                        "pin_id": uuid4(),
                        "tenant_id": tenant_uuid,
                        "resource_id": target_resource_id,
                        "digest": pin.envelope_digest,
                        "envelope": pin.envelope.model_dump_json(by_alias=True),
                    },
                )

            result = await SessionTransferService(PostgresTransferRepository(engine)).import_bundle(
                bundle,
                target_tenant_id=target_tenant,
                actor_id="test:transfer",
            )
            target_session_id = UUID(result.session_id)
            target_execution_id = UUID(
                result.id_mapping[f"execution:{bundle.execution.execution_id}"]
            )
            target_task_run_id = UUID(result.id_mapping[f"task:{bundle.session.task_run_id}"])
            context = AgentProgressContext(
                tenantId=target_tenant,
                serviceSessionId=target_session_id,
                executionId=target_execution_id,
                taskRunId=target_task_run_id,
                attemptSessionId=target_session_id,
                attempt=1,
            )
            next_frame = frames[-1].model_copy(
                update={
                    "attempt_session_id": target_session_id,
                    "status": AgentProgressStatus.DELTA,
                    "source_sequence": 4,
                    "occurred_at": base_time + timedelta(milliseconds=300),
                }
            )
            receipt = await PostgresAgentSessionRepository(engine).append_progress(
                context,
                next_frame,
                limits=AgentProgressLimits(maxFramesPerSecond=1000),
            )
            assert receipt.event_index == 4

            async with tenant_transaction(engine, target_tenant) as (connection, tenant_uuid):
                progress_state = (
                    (
                        await connection.execute(
                            text(
                                """
                                SELECT * FROM agent_session_progress_state
                                WHERE tenant_id = :tenant_id AND session_id = :session_id
                                """
                            ),
                            {"tenant_id": tenant_uuid, "session_id": target_session_id},
                        )
                    )
                    .mappings()
                    .one()
                )
                assert progress_state["accepted_frame_count"] == 4
                assert progress_state["segment_count"] == 2
                assert progress_state["active_segment_id"] == active_segment_id
                assert progress_state["active_segment_frame_count"] == 2
                assert (
                    await connection.scalar(
                        text(
                            """
                            SELECT last_sequence FROM agent_session_progress_sources
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                              AND source_id = 'provider:transfer'
                            """
                        ),
                        {"tenant_id": tenant_uuid, "session_id": target_session_id},
                    )
                    == 4
                )
                assert (
                    await connection.scalar(
                        text(
                            """
                            SELECT count(*) FROM agent_session_progress_timestamps
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                            """
                        ),
                        {"tenant_id": tenant_uuid, "session_id": target_session_id},
                    )
                    == 4
                )
                assert set(
                    await connection.scalars(
                        text(
                            """
                            SELECT segment_id FROM agent_session_progress_closed_segments
                            WHERE tenant_id = :tenant_id AND session_id = :session_id
                            """
                        ),
                        {"tenant_id": tenant_uuid, "session_id": target_session_id},
                    )
                ) == {closed_segment_id}
        finally:
            await engine.dispose()

    asyncio.run(scenario())
