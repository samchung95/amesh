from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException

from amesh.api.model_engines import (
    ModelEngineAccountService,
    build_model_engine_router,
)
from amesh.ports.model_engines import EngineAccountStatus, EngineLoginStart


class _Manager:
    def __init__(self) -> None:
        self.logout_calls = 0

    async def status(
        self,
        tenant_id: str,
        *,
        refresh_token: bool = False,
        include_rate_limits: bool = False,
        include_usage: bool = False,
    ) -> EngineAccountStatus:
        assert tenant_id == "tenant-a"
        assert refresh_token is False
        assert include_rate_limits is True
        assert include_usage is True
        return EngineAccountStatus(
            authenticated=None,
            authMode="chatgpt",
            rateLimits={
                "remaining": 9,
                "refreshToken": "secret",
                "nested": {"path": "C:\\private\\home", "window": 60},
            },
            usage={"inputTokens": 1, "credentialPath": "C:\\private\\credential"},
            actionRequired=True,
        )

    async def login_start(self, tenant_id: str, *, mode: str = "browser") -> EngineLoginStart:
        assert tenant_id == "tenant-a"
        return EngineLoginStart(
            kind=f"{mode}_login",
            loginId="login-1",
            authUrl="https://chatgpt.com/login" if mode == "browser" else None,
            verificationUrl="https://auth.openai.com/device" if mode == "device" else None,
            userCode="ABCD-1234" if mode == "device" else None,
            expiresAt=1_900_000_000,
            actionRequired=True,
        )

    async def logout(self, tenant_id: str) -> None:
        assert tenant_id == "tenant-a"
        self.logout_calls += 1


class _Audit:
    def __init__(self) -> None:
        self.records: list[tuple[str, dict[str, str]]] = []

    async def record_model_engine_account_action(
        self,
        tenant_id: str,
        **fields: str,
    ) -> None:
        self.records.append((tenant_id, fields))


def _application(
    service: ModelEngineAccountService,
    actions: list[str],
    *,
    deny_manage: bool = False,
) -> FastAPI:
    async def tenant() -> str:
        return "tenant-a"

    async def authorize() -> Callable[[str], Awaitable[None]]:
        async def check(action: str) -> None:
            actions.append(action)
            if deny_manage and action == "manage":
                raise HTTPException(status_code=403, detail="not authorized")

        return check

    async def actor() -> str:
        return "actor-a"

    app = FastAPI()
    app.include_router(
        build_model_engine_router(
            service_dependency=lambda: service,
            tenant_dependency=tenant,
            authorization_dependency=authorize,
            actor_dependency=actor,
        )
    )
    return app


def test_model_engine_account_routes_are_authorized_and_cache_binding_managers() -> None:
    managers: list[_Manager] = []

    def factory(namespace: str, engine_ref: str) -> _Manager:
        assert namespace == "team-a"
        assert engine_ref == "binding-a"
        manager = _Manager()
        managers.append(manager)
        return manager

    service = ModelEngineAccountService({"openai-codex-app-server": factory})
    actions: list[str] = []
    app = _application(service, actions)

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            catalog = await client.get("/api/v1/namespaces/team-a/model-engines/catalog")
            assert catalog.status_code == 200
            assert catalog.json()["engines"][0]["adapter"] == "openai-codex-app-server"
            assert managers == []

            first = await client.get(
                "/api/v1/namespaces/team-a/model-engines/openai-codex-app-server/binding-a/status"
            )
            second = await client.get(
                "/api/v1/namespaces/team-a/model-engines/openai-codex-app-server/binding-a/status"
            )
            assert first.status_code == second.status_code == 200
            assert first.json()["authenticated"] is None
            assert first.json()["actionRequired"] is True
            assert first.json()["rateLimits"] == {
                "remaining": 9,
                "nested": {"window": 60},
            }
            assert first.json()["usage"] == {"inputTokens": 1}
            assert len(managers) == 1

            login = await client.post(
                "/api/v1/namespaces/team-a/model-engines/openai-codex-app-server/binding-a/login",
                json={"mode": "device"},
            )
            assert login.status_code == 200
            assert login.json()["userCode"] == "ABCD-1234"
            assert login.json()["verificationUrl"] == "https://auth.openai.com/device"

            logout = await client.post(
                "/api/v1/namespaces/team-a/model-engines/openai-codex-app-server/binding-a/logout"
            )
            assert logout.status_code == 200
            assert logout.json() == {
                "adapter": "openai-codex-app-server",
                "engineRef": "binding-a",
                "status": "logged_out",
                "actionRequired": False,
            }

    import asyncio

    asyncio.run(scenario())
    assert actions == ["view", "view", "view", "manage", "manage"]


def test_unknown_adapter_and_adapter_failure_are_truthful_and_redacted() -> None:
    class BrokenManager(_Manager):
        async def status(self, tenant_id: str, **kwargs: Any) -> EngineAccountStatus:
            del tenant_id, kwargs
            raise RuntimeError("refresh_token=secret in C:\\private\\home")

    service = ModelEngineAccountService(
        {"github-copilot-cli": lambda namespace, engine_ref: BrokenManager()}
    )
    actions: list[str] = []
    app = _application(service, actions)

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            unknown = await client.get(
                "/api/v1/namespaces/team-a/model-engines/unknown/binding-a/status"
            )
            assert unknown.status_code == 404
            assert "secret" not in unknown.text

            failed = await client.get(
                "/api/v1/namespaces/team-a/model-engines/github-copilot-cli/binding-a/status"
            )
            assert failed.status_code == 409
            assert "secret" not in failed.text
            assert "private" not in failed.text

    import asyncio

    asyncio.run(scenario())


def test_manage_authorization_blocks_login_before_manager_creation() -> None:
    created = 0

    def factory(namespace: str, engine_ref: str) -> _Manager:
        del namespace, engine_ref
        nonlocal created
        created += 1
        return _Manager()

    service = ModelEngineAccountService({"openai-codex-app-server": factory})
    actions: list[str] = []
    app = _application(service, actions, deny_manage=True)

    async def scenario() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/namespaces/team-a/model-engines/openai-codex-app-server/binding-a/login",
                json={},
            )
            assert response.status_code == 403

    import asyncio

    asyncio.run(scenario())
    assert created == 0
    assert actions == ["manage"]


def test_account_status_login_and_logout_are_audited_without_engine_state() -> None:
    manager = _Manager()
    audit = _Audit()
    service = ModelEngineAccountService(
        {"openai-codex-app-server": lambda namespace, engine_ref: manager},
        audit_repository=audit,
    )

    async def scenario() -> None:
        common = {
            "namespace": "team-a",
            "adapter": "openai-codex-app-server",
            "engine_ref": "binding-a",
            "actor_id": "actor-a",
        }
        await service.status("tenant-a", **common)
        await service.login_start("tenant-a", mode="device", **common)
        await service.logout("tenant-a", **common)

    import asyncio

    asyncio.run(scenario())
    assert [record[1]["action"] for record in audit.records] == [
        "status",
        "login_start",
        "logout",
    ]
    assert [record[1]["outcome"] for record in audit.records] == [
        "ACTION_REQUIRED",
        "ACTION_REQUIRED",
        "SUCCESS",
    ]
    assert all(record[0] == "tenant-a" for record in audit.records)
    assert all("home" not in str(record).casefold() for record in audit.records)
