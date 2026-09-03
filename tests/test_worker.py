from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.exc import DBAPIError

from amesh import worker
from amesh.application import RunnerFactories
from amesh.config import Settings
from amesh.domain import (
    ExecutionState,
    FlowLifecycle,
    OperationalBoundary,
    OperationalControlDecision,
    RunningWorkPolicy,
)
from amesh.dsl.models import FlowDefinition, TaskDefinition, TriggerDefinition
from amesh.ports import ReconciliationAlreadyRunningError
from amesh.scheduler import CronScheduler


class StopWorker(BaseException):
    pass


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


class InterruptedTenantRepository:
    def __init__(self) -> None:
        self.calls = 0

    async def list_active_for_worker_group(self, worker_group: str) -> list[str]:
        del worker_group
        self.calls += 1
        if self.calls <= 2:
            raise OSError("simulated PostgreSQL connection interruption")
        raise StopWorker


def test_worker_retries_after_database_connection_interruption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def scenario() -> None:
        engine = FakeEngine()
        tenants = InterruptedTenantRepository()
        delays: list[float] = []
        monkeypatch.setattr(worker, "create_database_engine", lambda settings: engine)
        monkeypatch.setattr(
            worker,
            "PostgresExecutionRepository",
            lambda value, **kwargs: object(),
        )
        monkeypatch.setattr(worker, "PostgresSchedulerRepository", lambda value: object())
        monkeypatch.setattr(worker, "PostgresTenantRepository", lambda value: tenants)

        async def no_wait(delay: float) -> None:
            delays.append(delay)

        monkeypatch.setattr(worker.asyncio, "sleep", no_wait)
        settings = Settings(
            database_url="postgresql+asyncpg://amesh:amesh@localhost/amesh",
            worker_poll_seconds=0.5,
            worker_retry_max_seconds=0.75,
        )

        with pytest.raises(StopWorker):
            await worker.run_worker(settings)

        assert tenants.calls == 3
        assert delays == [0.5, 0.75]
        assert engine.disposed

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "interruption",
    [
        OSError("socket interrupted"),
        DBAPIError(None, None, OSError("database interrupted")),
    ],
    ids=("os-error", "dbapi-error"),
)
def test_recovery_reraises_transient_flow_lookup_failure_without_failing_execution(
    interruption: Exception,
) -> None:
    execution = SimpleNamespace(
        execution_id=uuid4(),
        namespace="tests.recovery",
        flow_id="transient_lookup",
        flow_revision=1,
        epoch=1,
    )
    failed: list[object] = []

    class ExecutionRepository:
        async def list_recovery_candidates(self, **kwargs: object) -> list[object]:
            del kwargs
            return [execution]

        async def get_flow(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            raise interruption

        async def fail_execution(
            self, execution_id: object, *args: object, **kwargs: object
        ) -> None:
            del args, kwargs
            failed.append(execution_id)

    with pytest.raises(type(interruption)):
        asyncio.run(
            worker.recover_once(
                ExecutionRepository(),  # type: ignore[arg-type]
                Settings(_env_file=None),
                tenant_ids=("default",),
            )
        )

    assert failed == []


def test_scheduler_continues_after_one_flow_evaluation_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ExecutionRepository:
        async def list_flows(self, *, tenant_id: str) -> list[object]:
            del tenant_id
            return [
                SimpleNamespace(
                    namespace="tests",
                    flow_id="broken",
                    lifecycle=FlowLifecycle.ACTIVE,
                ),
                SimpleNamespace(
                    namespace="tests",
                    flow_id="healthy",
                    lifecycle=FlowLifecycle.ACTIVE,
                ),
            ]

        async def get_flow(self, namespace: str, flow_id: str, *, tenant_id: str) -> object:
            del namespace, tenant_id
            return SimpleNamespace(id=flow_id)

    class SchedulerRepository:
        async def database_time(self) -> datetime:
            return datetime(2026, 8, 22, tzinfo=UTC)

    class Scheduler:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def fire_due_occurrences(
            self,
            flow: SimpleNamespace,
            *,
            at: datetime,
            tenant_id: str,
        ) -> list[object]:
            del at, tenant_id
            if flow.id == "broken":
                raise RuntimeError("simulated flow-specific scheduling failure")
            return [object()]

    monkeypatch.setattr(worker, "CronScheduler", Scheduler)

    with pytest.raises(worker.ScheduleCycleError) as caught:
        asyncio.run(
            worker.schedule_once(
                ExecutionRepository(),  # type: ignore[arg-type]
                SchedulerRepository(),  # type: ignore[arg-type]
                tenant_ids=["default"],
                scheduler_id=uuid4(),
            )
        )

    assert caught.value.scheduled == 1
    assert len(caught.value.failures) == 1


def test_scheduler_skips_disabled_flows() -> None:
    class ExecutionRepository:
        async def list_flows(self, *, tenant_id: str) -> list[object]:
            del tenant_id
            return [
                SimpleNamespace(
                    namespace="tests",
                    flow_id="quarantined",
                    lifecycle=FlowLifecycle.DISABLED,
                )
            ]

        async def get_flow(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            raise AssertionError("disabled flow must not enter scheduler evaluation")

    class SchedulerRepository:
        async def database_time(self) -> datetime:
            return datetime(2026, 8, 22, tzinfo=UTC)

    assert (
        asyncio.run(
            worker.schedule_once(
                ExecutionRepository(),  # type: ignore[arg-type]
                SchedulerRepository(),  # type: ignore[arg-type]
                tenant_ids=["default"],
                scheduler_id=uuid4(),
            )
        )
        == 0
    )


def test_periodic_reconciliation_skips_a_tenant_already_being_repaired(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BusyService:
        def __init__(self, repository: object) -> None:
            del repository
            self.calls: list[str] = []

        async def run(self, request: object, *, tenant_id: str, actor_id: str) -> object:
            del request, actor_id
            self.calls.append(tenant_id)
            raise ReconciliationAlreadyRunningError("simulated concurrent reconciler")

    service = BusyService(object())
    monkeypatch.setattr(worker, "ReconciliationService", lambda repository: service)

    repaired = asyncio.run(
        worker.reconcile_once(
            object(),  # type: ignore[arg-type]
            Settings(database_url="postgresql+asyncpg://amesh:amesh@localhost/amesh"),
            tenant_ids=["first", "second"],
        )
    )

    assert repaired == 0
    assert service.calls == ["first", "second"]


def test_cron_scheduler_rejects_new_work_when_triggers_are_controlled() -> None:
    class ExecutionRepository:
        async def create_execution(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            raise AssertionError("controlled scheduler must not create an execution")

    class Controls:
        def __init__(self) -> None:
            self.boundaries: list[OperationalBoundary] = []

        async def evaluate(
            self,
            boundary: OperationalBoundary,
            **kwargs: object,
        ) -> OperationalControlDecision:
            del kwargs
            self.boundaries.append(boundary)
            return OperationalControlDecision(
                blocked=True,
                boundary=boundary,
                runningWorkPolicy=RunningWorkPolicy.DRAIN,
            )

    controls = Controls()
    flow = FlowDefinition(
        id="controlled_cron",
        namespace="tests.controls",
        triggers=[
            TriggerDefinition(
                id="every_minute",
                type="core.cron",
                cron="* * * * *",
                timezone="UTC",
            )
        ],
        tasks=[TaskDefinition(id="done", type="core.return", value="done")],
    )

    with pytest.raises(RuntimeError, match="triggers blocked by operational control"):
        asyncio.run(
            CronScheduler(
                ExecutionRepository(),  # type: ignore[arg-type]
                operational_controls=controls,
            ).fire_occurrence(
                flow,
                trigger_id="every_minute",
                scheduled_for=datetime(2026, 8, 23, 12, 0, tzinfo=UTC),
                tenant_id="default",
            )
        )

    assert controls.boundaries == [OperationalBoundary.TRIGGERS]


def test_worker_drain_control_preserves_running_execution_without_dispatch() -> None:
    execution_id = uuid4()
    flow = FlowDefinition(
        id="controlled_worker",
        namespace="tests.controls",
        tasks=[TaskDefinition(id="done", type="core.return", value="done")],
    )

    class ExecutionRepository:
        def __init__(self) -> None:
            self.interventions = 0

        async def list_recovery_candidates(self, **kwargs: object) -> list[object]:
            assert kwargs["limit"] == 100
            return [
                SimpleNamespace(
                    execution_id=execution_id,
                    namespace=flow.namespace,
                    flow_id=flow.id,
                    flow_revision=flow.revision,
                    state=ExecutionState.RUNNING,
                    version=1,
                    epoch=1,
                    updated_at=datetime.now(UTC) - timedelta(minutes=5),
                )
            ]

        async def get_flow(self, *args: object, **kwargs: object) -> FlowDefinition:
            del args, kwargs
            return flow

        async def apply_execution_intervention(self, *args: object, **kwargs: object) -> None:
            del args, kwargs
            self.interventions += 1

    class Controls:
        async def evaluate(
            self,
            boundary: OperationalBoundary,
            **kwargs: object,
        ) -> OperationalControlDecision:
            del kwargs
            return OperationalControlDecision(
                blocked=True,
                boundary=boundary,
                runningWorkPolicy=RunningWorkPolicy.DRAIN,
            )

    repository = ExecutionRepository()
    recovered = asyncio.run(
        worker.recover_once(
            repository,  # type: ignore[arg-type]
            Settings(_env_file=None, worker_recovery_grace_seconds=0),
            tenant_ids=("default",),
            operational_controls=Controls(),  # type: ignore[arg-type]
        )
    )

    assert recovered == 0
    assert repository.interventions == 0


def test_recovery_composes_subflow_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    flow = FlowDefinition(
        id="recovery_subflow",
        namespace="tests.recovery",
        tasks=[TaskDefinition(id="child", type="core.subflow", flowId="child")],
    )
    execution = SimpleNamespace(
        execution_id=uuid4(),
        namespace=flow.namespace,
        flow_id=flow.id,
        flow_revision=flow.revision,
        state=ExecutionState.RUNNING,
        version=1,
        epoch=1,
        created_by="system:trigger-worker",
    )
    captured: dict[str, object] = {}

    class ExecutionRepository:
        has_admission_policy_enforcer = False

        async def list_recovery_candidates(self, **kwargs: object) -> list[object]:
            del kwargs
            return [execution]

        async def get_flow(self, *args: object, **kwargs: object) -> FlowDefinition:
            del args, kwargs
            return flow

        def execution_guard(self, *args: object, **kwargs: object) -> object:
            del args, kwargs

            class Guard:
                async def __aenter__(self) -> bool:
                    return True

                async def __aexit__(self, *args: object) -> None:
                    del args

            return Guard()

    class Executor:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args
            captured.update(kwargs)

        async def run_to_completion(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            return SimpleNamespace(state=ExecutionState.FAILED)

    monkeypatch.setattr(worker, "InProcessExecutor", Executor)
    monkeypatch.setattr(worker, "build_object_store", lambda settings: object())
    monkeypatch.setattr(worker, "required_runner_ids", lambda *args, **kwargs: ())
    monkeypatch.setattr(worker, "agent_llm_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "agent_mcp_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "core_utility_handlers", lambda *args, **kwargs: {})
    monkeypatch.setattr(worker, "script_task_handlers", lambda *args, **kwargs: {})

    recovered = asyncio.run(
        worker.recover_once(
            ExecutionRepository(),  # type: ignore[arg-type]
            Settings(_env_file=None),
            tenant_ids=("default",),
            runner_factories=RunnerFactories(selector=lambda *args: object()),  # type: ignore[arg-type]
        )
    )

    assert recovered == 1
    handlers = captured["handlers"]
    assert isinstance(handlers, dict)
    assert "core.subflow" in handlers


def test_recovery_continues_after_candidate_composition_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    flow = FlowDefinition(
        id="recovery_composition_failure",
        namespace="tests.recovery",
        tasks=[TaskDefinition(id="task", type="core.shell")],
    )
    executions = [
        SimpleNamespace(
            execution_id=uuid4(),
            namespace=flow.namespace,
            flow_id=flow.id,
            flow_revision=flow.revision,
            state=ExecutionState.RUNNING,
            version=1,
            epoch=1,
            created_by="system:trigger-worker",
        )
        for _ in range(2)
    ]
    guarded: list[object] = []
    failed: list[tuple[object, str]] = []

    class ExecutionRepository:
        has_admission_policy_enforcer = False

        async def list_recovery_candidates(self, **kwargs: object) -> list[object]:
            del kwargs
            return executions

        async def get_flow(self, *args: object, **kwargs: object) -> FlowDefinition:
            del args, kwargs
            return flow

        async def fail_execution(self, execution_id: object, reason: str, **kwargs: object) -> None:
            del kwargs
            failed.append((execution_id, reason))

        def execution_guard(self, *args: object, **kwargs: object) -> object:
            del kwargs
            guarded.append(args[1])

            class Guard:
                async def __aenter__(self) -> bool:
                    return True

                async def __aexit__(self, *args: object) -> None:
                    del args

            return Guard()

    class Executor:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def run_to_completion(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            return SimpleNamespace(state=ExecutionState.FAILED)

    build_calls = 0

    def build_object_store(settings: object) -> object:
        del settings
        nonlocal build_calls
        build_calls += 1
        if build_calls == 1:
            raise RuntimeError("secret candidate composition detail")
        return object()

    monkeypatch.setattr(worker, "InProcessExecutor", Executor)
    monkeypatch.setattr(worker, "build_object_store", build_object_store)
    monkeypatch.setattr(worker, "required_runner_ids", lambda *args, **kwargs: ())
    monkeypatch.setattr(worker, "agent_llm_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "agent_mcp_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "core_utility_handlers", lambda *args, **kwargs: {})
    monkeypatch.setattr(worker, "script_task_handlers", lambda *args, **kwargs: {})

    recovered = asyncio.run(
        worker.recover_once(
            ExecutionRepository(),  # type: ignore[arg-type]
            Settings(_env_file=None),
            tenant_ids=("default",),
            runner_factories=RunnerFactories(selector=lambda *args: object()),  # type: ignore[arg-type]
        )
    )

    assert build_calls == 2
    assert recovered == 1
    assert guarded == [executions[1].execution_id]
    assert failed == [
        (
            executions[0].execution_id,
            "recovery composition failed [RuntimeError]",
        )
    ]
    assert "secret candidate composition detail" not in failed[0][1]


def test_recovery_preserves_execution_failure_and_attempts_all_runner_teardown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    flow = FlowDefinition(
        id="recovery_teardown_failure",
        namespace="tests.recovery",
        tasks=[TaskDefinition(id="task", type="core.shell")],
    )
    execution = SimpleNamespace(
        execution_id=uuid4(),
        namespace=flow.namespace,
        flow_id=flow.id,
        flow_revision=flow.revision,
        state=ExecutionState.RUNNING,
        version=1,
        epoch=1,
        created_by="system:trigger-worker",
    )
    closed: list[str] = []

    class ExecutionRepository:
        has_admission_policy_enforcer = False

        async def list_recovery_candidates(self, **kwargs: object) -> list[object]:
            del kwargs
            return [execution]

        async def get_flow(self, *args: object, **kwargs: object) -> FlowDefinition:
            del args, kwargs
            return flow

        def execution_guard(self, *args: object, **kwargs: object) -> object:
            del args, kwargs

            class Guard:
                async def __aenter__(self) -> bool:
                    return True

                async def __aexit__(self, *args: object) -> None:
                    del args

            return Guard()

    class DockerRunner:
        def __init__(self, **kwargs: object) -> None:
            del kwargs

        def close(self) -> None:
            closed.append("docker")
            raise RuntimeError("docker close failed")

    class KubernetesRunner:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def close(self) -> None:
            closed.append("kubernetes")
            raise RuntimeError("kubernetes close failed")

    class Executor:
        def __init__(self, *args: object, **kwargs: object) -> None:
            del args, kwargs

        async def run_to_completion(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            raise RuntimeError("primary execution failure")

    monkeypatch.setattr(worker, "InProcessExecutor", Executor)
    monkeypatch.setattr(
        worker,
        "required_runner_ids",
        lambda *args, **kwargs: (worker.RunnerId.DOCKER, worker.RunnerId.KUBERNETES),
    )
    monkeypatch.setattr(worker, "agent_llm_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "agent_mcp_handler", lambda **kwargs: object())
    monkeypatch.setattr(worker, "core_utility_handlers", lambda *args, **kwargs: {})
    monkeypatch.setattr(worker, "script_task_handlers", lambda *args, **kwargs: {})

    recovered = asyncio.run(
        worker.recover_once(
            ExecutionRepository(),  # type: ignore[arg-type]
            Settings(_env_file=None),
            tenant_ids=("default",),
            runner_factories=RunnerFactories(
                docker_runner=lambda _: DockerRunner(),  # type: ignore[arg-type]
                kubernetes_runner=lambda _: KubernetesRunner(),  # type: ignore[arg-type]
                docker_handler=lambda *args: object(),  # type: ignore[arg-type]
                kubernetes_handler=lambda *args: object(),  # type: ignore[arg-type]
                selector=lambda *args: object(),  # type: ignore[arg-type]
            ),
        )
    )

    assert recovered == 0
    assert closed == ["docker", "kubernetes"]
