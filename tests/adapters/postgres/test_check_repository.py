from __future__ import annotations

import asyncio
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from amesh.adapters.postgres import PostgresCheckRepository, PostgresExecutionRepository
from amesh.dsl import CheckDefinition, FlowDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext
from amesh.migrations import apply_migrations, create_ephemeral_database, drop_ephemeral_database
from amesh.ports import CheckOutcome, CheckPolicySource
from amesh.worker import process_execution_checks_once

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[3] / "migrations"

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


def test_checks_evaluate_independently_and_materialize_reusable_policies() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        namespace = f"tests.checks.{uuid4().hex}"
        checks = PostgresCheckRepository(engine)
        executions = PostgresExecutionRepository(engine)
        try:
            await checks.upsert_policy(
                tenant_id="default",
                namespace=namespace,
                policy_key="namespace-baseline",
                source=CheckPolicySource.NAMESPACE,
                definition=CheckDefinition.model_validate(
                    {
                        "id": "namespace-policy",
                        "type": "EXPRESSION",
                        "expression": "{{ execution.state == 'SUCCESS' }}",
                    }
                ),
                actor_id="test:operator",
            )
            await checks.upsert_policy(
                tenant_id="default",
                namespace=namespace,
                policy_key="echo-default",
                source=CheckPolicySource.PLUGIN_DEFAULT,
                task_type="test.echo",
                definition=CheckDefinition.model_validate(
                    {
                        "id": "plugin-policy",
                        "type": "OUTPUT",
                        "expression": "{{ outputs.result.value == 'ok' }}",
                    }
                ),
                actor_id="test:operator",
            )
            flow = FlowDefinition.model_validate(
                {
                    "id": "evaluated",
                    "namespace": namespace,
                    "checkPolicies": ["namespace-baseline"],
                    "tasks": [{"id": "result", "type": "test.echo"}],
                    "checks": [
                        {"id": "duration", "type": "DURATION", "threshold": "PT1H"},
                        {"id": "start", "type": "START_DELAY", "threshold": "PT1H"},
                        {"id": "fresh", "type": "FRESHNESS", "threshold": "PT1H"},
                        {
                            "id": "completion",
                            "type": "COMPLETION_WINDOW",
                            "threshold": "PT1H",
                        },
                        {
                            "id": "output",
                            "type": "OUTPUT",
                            "expression": "{{ outputs.result.value == 'ok' }}",
                        },
                        {
                            "id": "warning",
                            "type": "EXPRESSION",
                            "severity": "WARN",
                            "expression": "{{ false }}",
                            "actions": [{"type": "NOTIFY", "channel": "operations"}],
                        },
                        {
                            "id": "broken",
                            "type": "EXPRESSION",
                            "expression": "{{ missing.value }}",
                            "actions": [
                                {
                                    "type": "RUN_FLOW",
                                    "flowId": "handler",
                                    "maxDepth": 2,
                                }
                            ],
                        },
                    ],
                }
            )

            async def handler(_task: object, _context: TaskExecutionContext) -> dict[str, str]:
                return {"value": "ok"}

            execution = await executions.create_execution(
                flow, tenant_id="default", inputs={}, labels={"service": "billing"}
            )
            completed = await InProcessExecutor(
                executions, handlers={"test.echo": handler}
            ).run_to_completion(flow, execution.execution_id, tenant_id="default")
            assert completed.state.value == "SUCCESS"

            evaluations = await checks.list_evaluations(
                tenant_id="default", execution_id=execution.execution_id
            )
            outcomes = {item.check_id: item.outcome for item in evaluations}
            assert outcomes == {
                "broken": CheckOutcome.ERROR,
                "completion": CheckOutcome.PASS,
                "duration": CheckOutcome.PASS,
                "fresh": CheckOutcome.PASS,
                "namespace-policy": CheckOutcome.PASS,
                "output": CheckOutcome.PASS,
                "plugin-policy": CheckOutcome.PASS,
                "start": CheckOutcome.PASS,
                "warning": CheckOutcome.WARN,
            }
            summary = await checks.summarize(tenant_id="default", group_by="label:service")
            assert len(summary) == 1
            assert summary[0].model_dump() == {
                "group_key": "billing",
                "total": 9,
                "passed": 7,
                "warned": 1,
                "failed": 0,
                "errors": 1,
                "compliance_rate": 7 / 9,
            }

            actions = await checks.claim_actions(
                tenant_id="default",
                owner_id=uuid4(),
                lease_duration=timedelta(seconds=30),
            )
            assert {action.action_type for action in actions} == {"NOTIFY", "RUN_FLOW"}
            notification = next(action for action in actions if action.action_type == "NOTIFY")
            await checks.publish_notification(notification, tenant_id="default")
            async with engine.connect() as connection:
                subject = await connection.scalar(
                    text("SELECT subject FROM messages_outbox WHERE message_id = :message_id"),
                    {"message_id": notification.action_id},
                )
            assert subject == "amesh.check.notification.operations"
            async with engine.connect() as connection:
                audited = await connection.scalar(
                    text("SELECT count(*) FROM audit_events WHERE action = 'check_policy.upsert'")
                )
            assert audited == 2

            await checks.upsert_policy(
                tenant_id="default",
                namespace=namespace,
                policy_key="namespace-baseline",
                source=CheckPolicySource.NAMESPACE,
                definition=CheckDefinition.model_validate(
                    {
                        "id": "replacement-policy",
                        "type": "EXPRESSION",
                        "expression": "{{ false }}",
                    }
                ),
                actor_id="test:operator",
            )
            second = await executions.create_execution(flow, tenant_id="default", inputs={})
            await InProcessExecutor(executions, handlers={"test.echo": handler}).run_to_completion(
                flow, second.execution_id, tenant_id="default"
            )
            second_ids = {
                item.check_id
                for item in await checks.list_evaluations(
                    tenant_id="default", execution_id=second.execution_id
                )
            }
            assert "namespace-policy" in second_ids
            assert "replacement-policy" not in second_ids
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_deadline_evaluation_and_policy_depth_are_bounded() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        executions = PostgresExecutionRepository(engine)
        checks = PostgresCheckRepository(engine)
        try:
            flow = FlowDefinition.model_validate(
                {
                    "id": "deadline",
                    "namespace": f"tests.checks.{uuid4().hex}",
                    "tasks": [{"id": "result", "type": "test.echo"}],
                    "checks": [
                        {
                            "id": "duration",
                            "type": "DURATION",
                            "threshold": "PT1H",
                            "actions": [
                                {
                                    "type": "RUN_FLOW",
                                    "flowId": "handler",
                                    "maxDepth": 1,
                                }
                            ],
                        }
                    ],
                }
            )
            execution = await executions.create_execution(
                flow,
                tenant_id="default",
                inputs={},
                trigger={"checkPolicyDepth": 1},
            )
            async with engine.begin() as connection:
                await connection.execute(
                    text(
                        "UPDATE check_deadlines SET due_at = clock_timestamp() - interval '1 second'"
                    )
                )
            assert await checks.process_due_checks(tenant_id="default") == 1
            evaluations = await checks.list_evaluations(
                tenant_id="default", execution_id=execution.execution_id
            )
            assert [(item.check_id, item.outcome.value) for item in evaluations] == [
                ("duration", "FAIL")
            ]
            async with engine.connect() as connection:
                state = await connection.scalar(text("SELECT state FROM check_action_queue"))
            assert state == "SKIPPED"
            assert not await checks.claim_actions(
                tenant_id="default",
                owner_id=uuid4(),
                lease_duration=timedelta(seconds=30),
            )
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())


def test_run_flow_check_action_launches_once_with_incremented_depth() -> None:
    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        await apply_migrations(database.database_url, MIGRATIONS)
        engine = create_async_engine(database.database_url)
        executions = PostgresExecutionRepository(engine)
        checks = PostgresCheckRepository(engine)
        namespace = f"tests.checks.{uuid4().hex}"
        try:
            handler_flow = FlowDefinition.model_validate(
                {
                    "id": "handler",
                    "namespace": namespace,
                    "tasks": [{"id": "result", "type": "test.echo"}],
                }
            )
            await executions.apply_flow(handler_flow, tenant_id="default")
            source_flow = FlowDefinition.model_validate(
                {
                    "id": "source",
                    "namespace": namespace,
                    "tasks": [{"id": "result", "type": "test.echo"}],
                    "checks": [
                        {
                            "id": "policy-action",
                            "type": "EXPRESSION",
                            "expression": "{{ false }}",
                            "actions": [
                                {
                                    "type": "RUN_FLOW",
                                    "flowId": "handler",
                                    "maxDepth": 2,
                                }
                            ],
                        }
                    ],
                }
            )

            async def handler(_task: object, _context: TaskExecutionContext) -> dict[str, str]:
                return {"value": "ok"}

            source = await executions.create_execution(source_flow, tenant_id="default", inputs={})
            await InProcessExecutor(executions, handlers={"test.echo": handler}).run_to_completion(
                source_flow, source.execution_id, tenant_id="default"
            )
            assert (
                await process_execution_checks_once(
                    executions,
                    checks,
                    tenant_ids=["default"],
                    worker_id=uuid4(),
                )
                == 1
            )
            launched = next(
                item
                for item in await executions.list_executions(tenant_id="default", limit=10)
                if item.flow_id == "handler"
            )
            assert launched.trigger["checkPolicyDepth"] == 1
            async with engine.connect() as connection:
                action = (
                    (
                        await connection.execute(
                            text("SELECT state, evidence FROM check_action_queue")
                        )
                    )
                    .mappings()
                    .one()
                )
            assert action["state"] == "SUCCEEDED"
            assert action["evidence"]["executionId"] == str(launched.execution_id)
        finally:
            await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
