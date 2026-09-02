from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, cast

from pydantic import SecretStr

from amesh.application import (
    LAUNCH_RECOVER_RUNNING_TYPES,
    RECOVER_RUNNING_TYPES,
    HandlerComposition,
    RunnerFactories,
    RunnerSelection,
    build_authentication_service,
    build_execution_runtime,
    build_executor_factory,
    build_http_task_policy,
    build_runner_bundle,
)
from amesh.authentication import AuthenticationService
from amesh.domain.runner import RunnerId, RunnerPolicy, RunnerPolicySet
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskHandler
from amesh.ports import KubernetesRunnerProfile, TaskRunner
from amesh.workflow.working_directory import WorkingDirectoryManager


@dataclass
class HttpSettings:
    network_egress_allowed_hosts: tuple[str, ...] = ("example.test",)
    core_http_allowed_private_hosts: tuple[str, ...] = ("localhost",)
    core_http_max_response_bytes: int = 123
    core_http_max_pages: int = 7
    core_http_max_redirects: int = 2
    network_http_proxy_url: SecretStr | None = field(
        default_factory=lambda: SecretStr("http://proxy.test")
    )
    network_https_proxy_url: SecretStr | None = field(
        default_factory=lambda: SecretStr("https://proxy.test")
    )
    network_no_proxy: tuple[str, ...] = ("localhost",)
    network_outbound_ca_file: str | None = "ca.pem"
    network_outbound_client_certificate_file: str | None = "client.pem"
    network_outbound_client_key_file: str | None = "client.key"


@dataclass
class RunnerSettings:
    runner_policies: tuple[RunnerPolicy, ...] = ()
    execution_runner_mode: str = "local"
    is_local_process_runner_enabled: bool = True
    docker_runner_enabled: bool = False
    docker_runner_endpoint: str | None = None
    docker_image_policy: Any = None
    docker_signature_verification_command: tuple[str, ...] = ()
    docker_vulnerability_verification_command: tuple[str, ...] = ()
    effective_kubernetes_runner_profiles: tuple[KubernetesRunnerProfile, ...] = ()
    kubernetes_api_retry_attempts: int = 8
    kubernetes_api_retry_max_seconds: float = 5.0


@dataclass
class AuthSettings:
    amesh_token_pepper: SecretStr = field(default_factory=lambda: SecretStr("pepper"))
    auth_policy: str = "local"
    auth_session_idle_seconds: int = 300
    auth_session_absolute_seconds: int = 3_600
    auth_session_rotation_seconds: int = 600
    auth_session_overlap_seconds: int = 30
    auth_login_rate_limit_per_minute: int = 10
    auth_login_max_failures: int = 5
    auth_login_lock_seconds: int = 60
    identity_providers: tuple[Any, ...] = ()


def test_build_http_task_policy_unwraps_secret_proxy_settings() -> None:
    policy = build_http_task_policy(HttpSettings())

    assert policy.allowed_hosts == ("example.test",)
    assert policy.allowed_private_hosts == frozenset({"localhost"})
    assert policy.http_proxy_url == "http://proxy.test"
    assert policy.https_proxy_url == "https://proxy.test"
    assert policy.maximum_response_bytes == 123


def test_runner_bundle_uses_injected_factories_and_closes_owned_runner() -> None:
    closed: list[str] = []

    class DockerDouble:
        def close(self) -> None:
            closed.append("docker")

    docker = cast(TaskRunner, DockerDouble())
    calls: list[str] = []

    def make_docker(_: RunnerSettings) -> TaskRunner:
        calls.append("docker-runner")
        return docker

    def make_handler(
        _: TaskRunner,
        __: WorkingDirectoryManager,
        ___: str,
    ) -> TaskHandler:
        async def handler(*_: object) -> dict[str, str]:
            return {"ok": "true"}

        return handler

    def select_handler(*_: object) -> TaskHandler:
        return make_handler(docker, WorkingDirectoryManager(None), "default")

    settings = RunnerSettings(
        execution_runner_mode="docker",
        is_local_process_runner_enabled=False,
        docker_runner_enabled=True,
    )
    bundle = asyncio.run(
        build_runner_bundle(
            settings,
            (TaskDefinition(id="run", type="core.shell", command=["echo", "ok"]),),
            WorkingDirectoryManager(None),
            namespace="default",
            factories=RunnerFactories(
                docker_runner=make_docker,
                docker_handler=make_handler,
                selector=select_handler,
            ),
        )
    )

    assert calls == ["docker-runner"]
    assert set(bundle.handlers) == {RunnerId.DOCKER}
    asyncio.run(bundle.close())
    asyncio.run(bundle.close())
    assert closed == ["docker"]


def test_runner_bundle_closes_partial_construction_on_failure() -> None:
    closed: list[str] = []

    class DockerDouble:
        def close(self) -> None:
            closed.append("docker")

    def fail_kubernetes(_: object) -> TaskRunner:
        raise RuntimeError("kubernetes unavailable")

    async def scenario() -> None:
        try:
            await build_runner_bundle(
                RunnerSettings(),
                (TaskDefinition(id="run", type="core.shell", command=["echo", "ok"]),),
                WorkingDirectoryManager(None),
                namespace="default",
                selection=RunnerSelection(
                    selected=frozenset({RunnerId.DOCKER, RunnerId.KUBERNETES}),
                    policy=RunnerPolicySet(()),
                    fallback=RunnerId.DOCKER,
                ),
                factories=RunnerFactories(
                    docker_runner=lambda _: cast(TaskRunner, DockerDouble()),
                    docker_handler=lambda *_: cast(TaskHandler, object()),
                    kubernetes_runner=fail_kubernetes,
                ),
            )
        except RuntimeError as exc:
            assert str(exc) == "kubernetes unavailable"
        else:
            raise AssertionError("partial runner construction unexpectedly succeeded")

    asyncio.run(scenario())
    assert closed == ["docker"]


def test_execution_runtime_closes_runner_when_handler_composition_fails() -> None:
    closed: list[str] = []

    class DockerDouble:
        def close(self) -> None:
            closed.append("docker")

    runtime_settings = SimpleNamespace(
        **vars(RunnerSettings()),
        **vars(HttpSettings()),
        execution_admission_poll_initial_seconds=0.05,
        execution_admission_poll_max_seconds=1.0,
    )

    async def authorize_subflow(_: object) -> None:
        return None

    def fail_composition(*_: object) -> HandlerComposition:
        raise RuntimeError("handler composition failed")

    async def scenario() -> None:
        try:
            await build_execution_runtime(
                cast(Any, runtime_settings),
                (TaskDefinition(id="run", type="core.shell", command=["echo", "ok"]),),
                WorkingDirectoryManager(None),
                cast(Any, object()),
                fail_composition,
                authorize_subflow,
                namespace="default",
                runner_selection=RunnerSelection(
                    selected=frozenset({RunnerId.DOCKER}),
                    policy=RunnerPolicySet(()),
                    fallback=RunnerId.DOCKER,
                ),
                runner_factories=RunnerFactories(
                    docker_runner=lambda _: cast(TaskRunner, DockerDouble()),
                    docker_handler=lambda *_: cast(TaskHandler, object()),
                    selector=lambda *_: cast(TaskHandler, object()),
                ),
            )
        except RuntimeError as exc:
            assert str(exc) == "handler composition failed"
        else:
            raise AssertionError("runtime composition unexpectedly succeeded")

    asyncio.run(scenario())
    assert closed == ["docker"]


def test_executor_factory_uses_shared_recovery_types_and_constructor_double() -> None:
    captured: dict[str, object] = {}

    def construct(_: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return object()

    factory = build_executor_factory(
        cast(Any, object()),
        {},
        executor_constructor=cast(Any, construct),
    )

    factory()

    assert captured["recover_running_types"] == RECOVER_RUNNING_TYPES
    assert {"core.shell", "agent.session", "core.subflow"} <= RECOVER_RUNNING_TYPES

    launch_factory = build_executor_factory(
        cast(Any, object()),
        {},
        recover_running_types=LAUNCH_RECOVER_RUNNING_TYPES,
        executor_constructor=cast(Any, construct),
    )
    launch_factory()
    assert captured["recover_running_types"] == frozenset({"core.subflow", "agent.session"})
    assert "core.shell" not in LAUNCH_RECOVER_RUNNING_TYPES
    assert not any(task_type.startswith("script.") for task_type in LAUNCH_RECOVER_RUNNING_TYPES)


def test_authentication_builder_passes_shared_service_configuration_to_double() -> None:
    captured: dict[str, object] = {}

    def construct(_: object, **kwargs: object) -> AuthenticationService:
        captured.update(kwargs)
        return cast(AuthenticationService, object())

    service = build_authentication_service(
        AuthSettings(),
        cast(Any, object()),
        service_factory=construct,
    )

    assert isinstance(service, object)
    assert captured["token_pepper"] == SecretStr("pepper")
    assert captured["login_max_failures"] == 5
    assert captured["providers"] == ()
