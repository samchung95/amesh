from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tests.fixtures.task_schemas import registered_test_task_registry

from amesh.adapters.postgres import PostgresExecutionRepository
from amesh.domain import ExecutionState, TaskRunState
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.executor import InProcessExecutor, TaskExecutionContext, TaskExecutionError
from amesh.expressions import NativeExpressionEngine

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)


class _FailOnConditionEngine(NativeExpressionEngine):
    def evaluate_condition(self, expression: str, context: Any) -> bool:
        del expression, context
        raise AssertionError("persisted branch decision was unexpectedly re-evaluated")


def test_conditional_flowables_persist_decisions_and_skip_without_attempts(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)
        try:
            repository = PostgresExecutionRepository(engine)
            if_flow = FlowDefinition.model_validate(
                {
                    "id": "durable_if",
                    "namespace": "tests.conditionals",
                    "inputs": [
                        {"id": "route", "type": "STRING", "sensitive": True},
                    ],
                    "tasks": [
                        {
                            "id": "upstream",
                            "type": "core.return",
                            "value": "ready",
                        },
                        {
                            "id": "choose",
                            "type": "core.if",
                            "dependsOn": ["upstream"],
                            "condition": (
                                "{{ outputs.upstream.value == 'ready' "
                                "and inputs.route == 'primary' }}"
                            ),
                            "then": [{"id": "primary", "type": "core.return", "value": "primary"}],
                            "elseIf": [
                                {
                                    "id": "secondary",
                                    "condition": (
                                        "{{ outputs.upstream.value == 'ready' "
                                        "and inputs.route == 'secondary' }}"
                                    ),
                                    "tasks": [
                                        {
                                            "id": "secondary_one",
                                            "type": "core.return",
                                            "value": "one",
                                        },
                                        {
                                            "id": "secondary_two",
                                            "type": "core.return",
                                            "value": "two",
                                        },
                                    ],
                                }
                            ],
                            "else": [
                                {"id": "fallback", "type": "core.return", "value": "fallback"}
                            ],
                        },
                    ],
                }
            )
            first_executor = InProcessExecutor(repository)
            execution_id = await first_executor.create_execution(
                if_flow,
                tenant_id="default",
                inputs={"route": "secondary"},
            )
            upstream = await first_executor.run_ready(
                if_flow,
                execution_id,
                tenant_id="default",
                max_tasks=1,
            )
            assert (
                next(item for item in upstream.task_runs if item.task_id == "upstream").state
                is TaskRunState.SUCCESS
            )
            first = await first_executor.run_ready(
                if_flow,
                execution_id,
                tenant_id="default",
                max_tasks=1,
            )
            parent = next(item for item in first.task_runs if item.task_id == "choose")
            branch = parent.evidence["control"]["branch"]
            assert branch["selectedBranch"] == "else-if:secondary"
            assert branch["conditionInputs"]["inputs"]["route"] == "[REDACTED]"
            assert branch["conditionInputs"]["outputs"]["upstream"]["value"] == "ready"
            assert (
                next(item for item in first.task_runs if item.task_id == "primary").current_attempt
                == 0
            )
            assert (
                next(item for item in first.task_runs if item.task_id == "fallback").current_attempt
                == 0
            )

            await engine.dispose()
            engine = create_async_engine(migrated_test_database_url)
            repository = PostgresExecutionRepository(engine)
            restarted = InProcessExecutor(repository, expressions=_FailOnConditionEngine())
            completed = await restarted.run_to_completion(
                if_flow,
                execution_id,
                tenant_id="default",
            )
            assert completed.state is ExecutionState.SUCCESS
            runs = {item.task_id: item for item in completed.task_runs}
            assert runs["secondary_one"].current_attempt == 1
            assert runs["secondary_two"].current_attempt == 1
            assert runs["primary"].result == {
                "skipped": True,
                "reason": "conditional branch 'else-if:secondary' selected",
                "controlTask": "choose",
                "branch": "then",
                "selectedBranch": "else-if:secondary",
            }
            async with engine.connect() as connection:
                skipped_attempts = await connection.scalar(
                    text(
                        "SELECT count(*) FROM task_attempts WHERE task_run_id IN "
                        "(SELECT id FROM task_runs WHERE execution_id = :execution_id "
                        "AND task_path IN ('primary', 'fallback'))"
                    ),
                    {"execution_id": execution_id},
                )
            assert skipped_attempts == 0

            switch_flow = FlowDefinition.model_validate(
                {
                    "id": "switch_modes",
                    "namespace": "tests.conditionals",
                    "inputs": [
                        {"id": "tier", "type": "STRING"},
                        {"id": "score", "type": "INT"},
                    ],
                    "tasks": [
                        {
                            "id": "exact_switch",
                            "type": "core.switch",
                            "value": "{{ inputs.tier }}",
                            "cases": {
                                "paid": [
                                    {"id": "exact_paid", "type": "core.return", "value": True}
                                ],
                                "default": [
                                    {"id": "exact_default", "type": "core.return", "value": True}
                                ],
                            },
                        },
                        {
                            "id": "predicate_switch",
                            "type": "core.switch",
                            "value": "unknown",
                            "cases": {
                                "default": [
                                    {
                                        "id": "predicate_default",
                                        "type": "core.return",
                                        "value": True,
                                    }
                                ]
                            },
                            "predicateCases": [
                                {
                                    "id": "high",
                                    "condition": "{{ inputs.score >= 90 }}",
                                    "tasks": [
                                        {
                                            "id": "predicate_high",
                                            "type": "core.return",
                                            "value": True,
                                        }
                                    ],
                                },
                                {
                                    "id": "medium",
                                    "condition": "{{ inputs.score >= 50 }}",
                                    "tasks": [
                                        {
                                            "id": "predicate_medium",
                                            "type": "core.return",
                                            "value": True,
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "id": "default_switch",
                            "type": "core.switch",
                            "value": "missing",
                            "cases": {
                                "known": [{"id": "known", "type": "core.return", "value": True}],
                                "default": [
                                    {"id": "chosen_default", "type": "core.return", "value": True}
                                ],
                            },
                        },
                    ],
                }
            )
            switch_executor = InProcessExecutor(repository)
            switch_id = await switch_executor.create_execution(
                switch_flow,
                tenant_id="default",
                inputs={"tier": "paid", "score": 70},
            )
            switch_done = await switch_executor.run_to_completion(
                switch_flow,
                switch_id,
                tenant_id="default",
            )
            switch_runs = {item.task_id: item for item in switch_done.task_runs}
            assert switch_runs["exact_paid"].current_attempt == 1
            assert switch_runs["predicate_medium"].current_attempt == 1
            assert switch_runs["chosen_default"].current_attempt == 1
            assert switch_runs["predicate_high"].current_attempt == 0

            run_if_flow = FlowDefinition.model_validate(
                {
                    "id": "zero_attempt_run_if",
                    "namespace": "tests.conditionals",
                    "tasks": [
                        {
                            "id": "skipped",
                            "type": "core.return",
                            "runIf": "{{ false }}",
                            "value": "never",
                        }
                    ],
                }
            )
            run_if_executor = InProcessExecutor(repository)
            run_if_id = await run_if_executor.create_execution(run_if_flow, tenant_id="default")
            run_if_done = await run_if_executor.run_to_completion(
                run_if_flow,
                run_if_id,
                tenant_id="default",
            )
            skipped = run_if_done.task_runs[0]
            assert skipped.state is TaskRunState.SUCCESS
            assert skipped.current_attempt == 0
            async with engine.connect() as connection:
                event_types = (
                    (
                        await connection.execute(
                            text(
                                "SELECT event_type FROM task_run_events "
                                "WHERE task_run_id = :task_run_id ORDER BY sequence"
                            ),
                            {"task_run_id": skipped.task_run_id},
                        )
                    )
                    .scalars()
                    .all()
                )
            assert event_types == ["TaskRunCreated", "TaskRunSkipped"]
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_condition_error_policies_and_retry_conditions_are_evidenced(
    migrated_test_database_url: str,
) -> None:
    async def scenario() -> None:
        engine = create_async_engine(migrated_test_database_url)

        async def fail_transiently(
            task: TaskDefinition,
            context: TaskExecutionContext,
        ) -> dict[str, object]:
            del task, context
            raise OSError("temporary outage")

        try:
            repository = PostgresExecutionRepository(engine)
            policy_flow = FlowDefinition.model_validate(
                {
                    "id": "condition_policies",
                    "namespace": "tests.conditionals",
                    "tasks": [
                        {
                            "id": "fallback_if",
                            "type": "core.if",
                            "condition": "{{ 1 / 0 > 0 }}",
                            "conditionErrorPolicy": "FALLBACK",
                            "then": [{"id": "fallback_then", "type": "core.return", "value": True}],
                            "else": [{"id": "fallback_else", "type": "core.return", "value": True}],
                        },
                        {
                            "id": "false_if",
                            "type": "core.if",
                            "condition": "{{ 1 / 0 > 0 }}",
                            "conditionErrorPolicy": "FALSE",
                            "then": [{"id": "false_then", "type": "core.return", "value": True}],
                            "elseIf": [
                                {
                                    "id": "recovered",
                                    "condition": "{{ true }}",
                                    "tasks": [
                                        {
                                            "id": "false_recovered",
                                            "type": "core.return",
                                            "value": True,
                                        }
                                    ],
                                }
                            ],
                        },
                    ],
                }
            )
            executor = InProcessExecutor(repository)
            policy_id = await executor.create_execution(policy_flow, tenant_id="default")
            policy_done = await executor.run_to_completion(
                policy_flow,
                policy_id,
                tenant_id="default",
            )
            policy_runs = {item.task_id: item for item in policy_done.task_runs}
            assert policy_runs["fallback_else"].current_attempt == 1
            assert policy_runs["fallback_then"].current_attempt == 0
            assert policy_runs["false_recovered"].current_attempt == 1
            assert policy_runs["false_if"].evidence["control"]["branch"]["evaluations"][0]["error"][
                "type"
            ]

            fail_flow = FlowDefinition.model_validate(
                {
                    "id": "condition_fail",
                    "namespace": "tests.conditionals",
                    "tasks": [
                        {
                            "id": "fail_if",
                            "type": "core.if",
                            "condition": "{{ 1 / 0 > 0 }}",
                            "then": [{"id": "never", "type": "core.return", "value": True}],
                        }
                    ],
                }
            )
            fail_id = await executor.create_execution(fail_flow, tenant_id="default")
            failed = await executor.run_ready(fail_flow, fail_id, tenant_id="default")
            assert failed.state is ExecutionState.FAILED
            fail_parent = next(item for item in failed.task_runs if item.task_id == "fail_if")
            assert fail_parent.evidence["control"]["branch"]["selectedBranch"] is None

            retry_flow = FlowDefinition.model_validate(
                {
                    "id": "conditional_retry",
                    "namespace": "tests.conditionals",
                    "tasks": [
                        {
                            "id": "flaky",
                            "type": "tests.flaky",
                            "retry": {
                                "maxAttempts": 3,
                                "condition": (
                                    "{{ taskrun.failureCategory == 'INFRASTRUCTURE' "
                                    "and taskrun.attempt < 2 }}"
                                ),
                            },
                        }
                    ],
                }
            )
            retry_executor = InProcessExecutor(
                repository,
                handlers={"tests.flaky": fail_transiently},
                resource_registry=registered_test_task_registry("tests.flaky"),
            )
            retry_id = await retry_executor.create_execution(retry_flow, tenant_id="default")
            with pytest.raises(TaskExecutionError):
                await retry_executor.run_to_completion(
                    retry_flow,
                    retry_id,
                    tenant_id="default",
                )
            retry_run = (await repository.list_task_runs(retry_id, tenant_id="default"))[0]
            assert retry_run.current_attempt == 2
            assert retry_run.evidence["control"]["retry"]["result"] is False
            async with engine.connect() as connection:
                attempts = (
                    (
                        await connection.execute(
                            text(
                                "SELECT attempt, evidence FROM task_attempts "
                                "WHERE task_run_id = :task_run_id ORDER BY attempt"
                            ),
                            {"task_run_id": retry_run.task_run_id},
                        )
                    )
                    .mappings()
                    .all()
                )
            assert attempts[0]["evidence"]["control"]["retry"]["result"] is True
            assert attempts[1]["evidence"]["control"]["retry"]["result"] is False
        finally:
            await engine.dispose()

    asyncio.run(scenario())
