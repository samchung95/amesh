from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest
from fastapi import Depends
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import PlainTextResponse, StreamingResponse
from starlette.routing import Route


def test_legacy_app_alias_preserves_monkeypatches_and_openapi_in_fresh_process(
    monkeypatch,
) -> None:
    legacy = importlib.import_module("amesh.app")
    implementation = importlib.import_module("amesh.api.application")

    assert legacy is implementation
    assert legacy.app is implementation.app

    replacement = object()
    monkeypatch.setattr(legacy, "external_orchestration_profile", replacement)
    endpoint = next(
        route.endpoint
        for route in legacy.app.routes
        if getattr(route, "path", None) == "/api/v1/orchestration/profile"
    )
    assert endpoint.__globals__["external_orchestration_profile"] is replacement

    canonical = json.dumps(
        legacy.app.openapi(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    assert len(canonical) == 777825
    assert hashlib.sha256(canonical).hexdigest() == (
        "6238c808365e0550571c44e3497233e2b6d663ecc991cc7a397fdf2cd5c6c0ba"
    )

    source_root = Path(__file__).resolve().parents[2] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source_root), environment.get("PYTHONPATH")) if part
    )
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import hashlib
import importlib
import json

import amesh.app as legacy
from amesh.app import app

implementation = importlib.import_module("amesh.api.application")
document = json.dumps(
    app.openapi(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
).encode()
assert legacy is implementation
assert app is implementation.app
print(len(document), hashlib.sha256(document).hexdigest())
""",
        ],
        cwd=source_root.parent,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )
    assert probe.stdout.strip() == (
        "777825 6238c808365e0550571c44e3497233e2b6d663ecc991cc7a397fdf2cd5c6c0ba"
    )


def test_application_import_is_inert_and_factory_keeps_runtime_providers_lazy() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source_root), environment.get("PYTHONPATH")) if part
    )
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import importlib
import sys

application = importlib.import_module("amesh.api.application")
assert application._default_application is None
assert "amesh.api.dependencies" not in sys.modules
assert "amesh.api.routers.system" not in sys.modules
assert "amesh.database" not in sys.modules
assert "amesh.mcp_server" not in sys.modules
assert "amesh.observability" not in sys.modules

created = application.create_application()
dependencies = importlib.import_module("amesh.api.dependencies")
cached_providers = [
    value
    for value in vars(dependencies).values()
    if callable(value) and hasattr(value, "cache_info")
]
assert cached_providers
assert all(provider.cache_info().currsize == 0 for provider in cached_providers)
assert "amesh.mcp_server" not in sys.modules
assert application._default_application is None
assert len(created.openapi()["paths"]) == 278
""",
        ],
        cwd=source_root.parent,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )
    assert probe.stdout == ""


def test_feature_routers_own_handlers_and_composition_root_stays_small() -> None:
    from amesh.api.routers.manifest import ROUTE_SEQUENCE

    source_root = Path(__file__).resolve().parents[2] / "src"
    application_lines = (
        (source_root / "amesh" / "api" / "application.py").read_text(encoding="utf-8").splitlines()
    )
    assert len(application_lines) < 1_000

    for name in ("workflows", "executions", "agent_sessions"):
        route_source = source_root / "amesh" / "api" / "routers" / f"{name}.py"
        assert len(route_source.read_text(encoding="utf-8").splitlines()) < 2_000

    for kind, module_name, attribute in ROUTE_SEQUENCE:
        if kind != "feature":
            continue
        module = importlib.import_module(f"amesh.api.routers.{module_name}")
        router = getattr(module, attribute)
        assert router.routes
        assert all(route.endpoint.__module__ == module.__name__ for route in router.routes)


def test_running_legacy_module_does_not_replace_main_module() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source_root), environment.get("PYTHONPATH")) if part
    )
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import runpy
import sys

original = sys.modules["__main__"]
runpy.run_module("amesh.app", run_name="__main__", alter_sys=False)
assert sys.modules["__main__"] is original
""",
        ],
        cwd=source_root.parent,
        env=environment,
        capture_output=True,
        check=True,
        text=True,
    )
    assert probe.stdout == ""


def test_mcp_runtime_is_fresh_each_lifespan_and_stays_before_the_spa(
    monkeypatch,
) -> None:
    implementation = importlib.import_module("amesh.api.application")
    events: list[str] = []

    async def probe_endpoint(request: Request) -> PlainTextResponse:
        del request
        return PlainTextResponse("ok")

    builds = 0

    containers: list[object] = []

    def build_mcp_application(providers: object) -> Starlette:
        nonlocal builds
        builds += 1
        containers.append(providers)
        entered = False

        @asynccontextmanager
        async def one_shot_mcp_lifespan(_: Starlette) -> AsyncIterator[None]:
            nonlocal entered
            if entered:
                raise RuntimeError("MCP lifespan may only be entered once")
            entered = True
            events.append("enter")
            yield
            events.append("exit")

        return Starlette(
            routes=[Route("/mcp-probe", probe_endpoint)],
            lifespan=one_shot_mcp_lifespan,
        )

    monkeypatch.setattr(implementation, "_build_mcp_application", build_mcp_application)
    created = implementation.create_application()
    created.mount("/", Starlette(), name="custom-spa")
    assert not hasattr(created.state, "amesh_mcp_application")

    async def exercise() -> None:
        for _ in range(2):
            async with created.router.lifespan_context(created):
                paths = [getattr(route, "path", None) for route in created.routes]
                assert paths.count("/mcp-probe") == 1
                installed_route = next(
                    route
                    for route in created.routes
                    if getattr(route, "path", None) == "/mcp-probe"
                )
                assert any(installed_route is route for route in created.state.amesh_mcp_routes)
                if "/" in paths:
                    assert paths.index("/mcp-probe") < paths.index("/")
                assert paths.index("/mcp-probe") < paths.index("")
            assert not any(getattr(route, "path", None) == "/mcp-probe" for route in created.routes)
            assert not hasattr(created.state, "amesh_mcp_application")
            assert not created.state.amesh_mcp_routes_installed

    asyncio.run(exercise())

    assert builds == 2
    assert containers[0] is not containers[1]
    assert events == ["enter", "exit", "enter", "exit"]


def test_application_factories_own_independent_provider_lifecycles(monkeypatch) -> None:
    implementation = importlib.import_module("amesh.api.application")
    dependencies = importlib.import_module("amesh.api.dependencies")
    frontend = importlib.import_module("amesh.frontend")
    services: list[object] = []
    monkeypatch.setattr(frontend, "find_frontend_dist", lambda: None)

    class RecordingService:
        def __init__(self) -> None:
            self.close_count = 0

        async def close(self) -> None:
            self.close_count += 1

    def provider_factory():
        container = dependencies.ApiProviderContainer()
        service = RecordingService()
        services.append(service)
        container.set(dependencies.get_model_engine_account_service, service)
        return container

    def build_mcp_application(providers: object) -> Starlette:
        with providers.activate():
            assert dependencies.get_model_engine_account_service() is services[-1]
        return Starlette()

    monkeypatch.setattr(implementation, "_build_mcp_application", build_mcp_application)
    first = implementation.create_application(provider_factory=provider_factory)
    second = implementation.create_application(provider_factory=provider_factory)

    async def provider_probe(
        service: object = Depends(dependencies.get_model_engine_account_service),
    ) -> dict[str, int]:
        return {"serviceId": id(service)}

    first.add_api_route("/_provider-probe", provider_probe)
    second.add_api_route("/_provider-probe", provider_probe)

    async def exercise() -> None:
        async with first.router.lifespan_context(first):
            first_container = first.state.amesh_provider_container
            assert services[0].close_count == 0
            async with second.router.lifespan_context(second):
                assert second.state.amesh_provider_container is not first_container
                assert services[0].close_count == 0
                assert services[1].close_count == 0
                async with (
                    httpx.AsyncClient(
                        transport=httpx.ASGITransport(app=first),
                        base_url="http://amesh.test",
                    ) as first_client,
                    httpx.AsyncClient(
                        transport=httpx.ASGITransport(app=second),
                        base_url="http://amesh.test",
                    ) as second_client,
                ):
                    first_response, second_response = await asyncio.gather(
                        first_client.get("/_provider-probe"),
                        second_client.get("/_provider-probe"),
                    )
                assert first_response.json() == {"serviceId": id(services[0])}
                assert second_response.json() == {"serviceId": id(services[1])}
            assert services[0].close_count == 0
            assert services[1].close_count == 1
        assert services[0].close_count == 1

    asyncio.run(exercise())


def test_requests_without_lifespan_reuse_application_scope_until_shutdown(monkeypatch) -> None:
    implementation = importlib.import_module("amesh.api.application")
    dependencies = importlib.import_module("amesh.api.dependencies")
    frontend = importlib.import_module("amesh.frontend")
    events: list[str] = []
    containers: list[object] = []
    monkeypatch.setattr(frontend, "find_frontend_dist", lambda: None)

    class RecordingService:
        closed = False

        async def close(self) -> None:
            self.closed = True
            events.append("close")

    service = RecordingService()

    def provider_factory():
        container = dependencies.ApiProviderContainer()
        container.set(dependencies.get_model_engine_account_service, service)
        containers.append(container)
        return container

    created = implementation.create_application(provider_factory=provider_factory)
    monkeypatch.setattr(implementation, "_build_mcp_application", lambda _providers: Starlette())

    async def body():
        assert not service.closed
        events.append("body")
        yield b"application provider"

    async def background() -> None:
        assert not service.closed
        events.append("background")

    async def provider_probe(
        resolved: object = Depends(dependencies.get_model_engine_account_service),
    ) -> StreamingResponse:
        assert resolved is service
        return StreamingResponse(body(), background=BackgroundTask(background))

    created.add_api_route("/_provider-probe", provider_probe)

    async def exercise() -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=created),
            base_url="http://amesh.test",
        ) as client:
            for _ in range(3):
                response = await client.get("/_provider-probe")
                assert response.status_code == 200
                assert response.text == "application provider"
        assert len(containers) == 1
        assert not service.closed
        async with created.router.lifespan_context(created):
            assert created.state.amesh_provider_container is containers[0]

    asyncio.run(exercise())
    assert len(containers) == 1
    assert events == ["body", "background"] * 3 + ["close"]
    assert (
        containers[0].provider_cache_info(dependencies.get_model_engine_account_service).currsize
        == 0
    )


@pytest.mark.parametrize("reuse_container", [False, True])
def test_concurrent_requests_construct_and_close_one_provider(monkeypatch, reuse_container) -> None:
    implementation = importlib.import_module("amesh.api.application")
    dependencies = importlib.import_module("amesh.api.dependencies")
    frontend = importlib.import_module("amesh.frontend")
    resources: list[object] = []
    monkeypatch.setattr(frontend, "find_frontend_dist", lambda: None)

    class RecordingService:
        close_count = 0

        async def close(self) -> None:
            self.close_count += 1

    @dependencies.provider
    def concurrent_service():
        time.sleep(0.05)
        service = RecordingService()
        resources.append(service)
        return service

    monkeypatch.setattr(
        dependencies,
        "get_model_engine_account_service",
        concurrent_service,
    )
    monkeypatch.setattr(
        implementation,
        "_build_mcp_application",
        lambda _providers: Starlette(),
    )
    container = dependencies.ApiProviderContainer()
    created = implementation.create_application(
        provider_factory=(lambda: container) if reuse_container else None,
    )

    async def provider_probe(
        service: object = Depends(concurrent_service),
    ) -> dict[str, int]:
        return {"serviceId": id(service)}

    created.add_api_route("/_provider-probe", provider_probe)

    async def exercise() -> tuple[dict[str, int], dict[str, int]]:
        async with created.router.lifespan_context(created):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=created),
                base_url="http://amesh.test",
            ) as client:
                first, second = await asyncio.gather(
                    client.get("/_provider-probe"),
                    client.get("/_provider-probe"),
                )
            return first.json(), second.json()

    first_payload, second_payload = asyncio.run(exercise())
    assert len(resources) == 1
    assert first_payload == second_payload == {"serviceId": id(resources[0])}
    assert resources[0].close_count == 1

    next_first, next_second = asyncio.run(exercise())
    assert len(resources) == 2
    assert next_first == next_second == {"serviceId": id(resources[1])}
    assert resources[1].close_count == 1


def test_provider_cache_hooks_use_the_active_container() -> None:
    from amesh.api.dependencies import ApiProviderContainer, provider

    @provider
    def value():
        return object()

    process_value = value()
    container = ApiProviderContainer()
    with container.activate():
        assert value.cache_info().currsize == 0
        first = value()
        assert first is not process_value
        assert value() is first
        assert value.cache_info().hits == 1
        assert value.cache_info().misses == 1
        assert value.cache_info().currsize == 1
        value.cache_clear()
        assert value.cache_info().currsize == 0
        assert value() is not first
    assert value() is process_value
    value.cache_clear()


def test_compatibility_module_preserves_assignment_and_deletion(monkeypatch) -> None:
    implementation = importlib.import_module("amesh.api.application")
    dependencies = importlib.import_module("amesh.api.dependencies")
    original = dependencies.get_repository
    replacement = object()
    with monkeypatch.context() as patch:
        patch.setattr(implementation, "get_repository", replacement)
        assert vars(implementation)["get_repository"] is replacement
        assert dependencies.get_repository is replacement
        del implementation.get_repository
        assert not hasattr(implementation, "get_repository")
        assert not hasattr(dependencies, "get_repository")
    assert implementation.get_repository is original
    assert dependencies.get_repository is original
    with monkeypatch.context() as patch:
        patch.setattr(implementation, "temporary_probe", replacement, raising=False)
        assert vars(implementation)["temporary_probe"] is replacement
    assert not hasattr(implementation, "temporary_probe")


def test_provider_cleanup_continues_after_a_failure_and_clears_app_state(monkeypatch) -> None:
    implementation = importlib.import_module("amesh.api.application")
    dependencies = importlib.import_module("amesh.api.dependencies")
    calls: list[str] = []

    class RecordingResource:
        def __init__(self, name: str, *, fail: bool = False) -> None:
            self.name = name
            self.fail = fail

        async def close(self) -> None:
            calls.append(f"{self.name}.close")
            if self.fail:
                raise RuntimeError("model cleanup failed")

        async def stop(self) -> None:
            calls.append(f"{self.name}.stop")

        async def dispose(self) -> None:
            calls.append(f"{self.name}.dispose")

    container = dependencies.ApiProviderContainer()
    providers = (
        dependencies.get_model_engine_account_service,
        dependencies.get_isolated_plugin_runtime,
        dependencies.get_trusted_plugin_runtime,
        dependencies.read_database_engine,
        dependencies.database_engine,
    )
    container.set(providers[0], RecordingResource("model", fail=True))
    container.set(providers[1], RecordingResource("isolated"))
    container.set(providers[2], RecordingResource("trusted"))
    container.set(providers[3], RecordingResource("read"))
    container.set(providers[4], RecordingResource("write"))
    monkeypatch.setattr(
        implementation,
        "_build_mcp_application",
        lambda _providers: Starlette(),
    )
    created = implementation.create_application(provider_factory=lambda: container)

    async def exercise() -> None:
        with pytest.raises(RuntimeError, match="model cleanup failed"):
            async with created.router.lifespan_context(created):
                pass
        assert not hasattr(created.state, "amesh_provider_container")
        assert all(container.provider_cache_info(provider).currsize == 0 for provider in providers)
        await container.close()

    asyncio.run(exercise())
    assert calls == [
        "model.close",
        "isolated.stop",
        "trusted.stop",
        "read.dispose",
        "write.dispose",
    ]
