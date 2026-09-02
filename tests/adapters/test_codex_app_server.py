from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from amesh.adapters.codex_app_server import (
    CodexAccountManager,
    CodexAppServerConfig,
    CodexAppServerError,
    CodexAppServerModelProvider,
    CodexAppServerProtocolError,
    CodexAppServerTimeout,
    derive_codex_home,
)
from amesh.domain.agent_progress import AgentProgressActivity
from amesh.domain.artifacts import ArtifactProvenance, ArtifactRetention, build_artifact_reference
from amesh.domain.image_inputs import ImageArtifactRef, ImageDisplayMetadata
from amesh.ports import ModelEngineAccess, ModelProviderRequest

FIXTURE = Path(__file__).parent.parent / "fixtures" / "codex_app_server_fixture.py"


def _config(
    tmp_path: Path,
    *,
    timeout_seconds: float = 2,
    fixture_args: tuple[str, ...] = (),
) -> CodexAppServerConfig:
    return CodexAppServerConfig(
        command=(sys.executable, str(FIXTURE), *fixture_args),
        state_root=tmp_path,
        timeout_seconds=timeout_seconds,
        cancel_grace_seconds=0.2,
    )


def _request(
    prompt: str,
    *,
    namespace: str = "default",
    reasoning_effort: str | None = None,
    timeout_seconds: float | None = 2,
) -> ModelProviderRequest:
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "responseFormat": {
            "type": "json_schema",
            "json_schema": {"name": "answer", "schema": {"type": "object"}},
        },
    }
    if reasoning_effort is not None:
        payload["reasoningEffort"] = reasoning_effort
    return ModelProviderRequest(
        operation="structured",
        model="fixture-model",
        payload=payload,
        timeoutSeconds=timeout_seconds,
        tenantId="tenant-a",
        namespace=namespace,
    )


def test_home_is_stable_isolated_and_server_derived(tmp_path: Path) -> None:
    first = derive_codex_home(tmp_path, tenant_id="tenant-a", namespace="ns", engine_ref="codex")
    assert first == derive_codex_home(
        tmp_path, tenant_id="tenant-a", namespace="ns", engine_ref="codex"
    )
    assert first != derive_codex_home(
        tmp_path, tenant_id="tenant-b", namespace="ns", engine_ref="codex"
    )
    assert first.parent == tmp_path.resolve() / "codex"


def test_fixture_invocation_normalizes_result_and_hides_reasoning(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        events = [
            event
            async for event in provider.stream(
                _request("effort", reasoning_effort="high"),
                ModelEngineAccess(engineRef="ref-a"),
            )
        ]
        response = events[-1].response
        assert response is not None
        assert response.payload["choices"][0]["message"]["content"] == '{"answer":"ok"}'
        assert response.payload["usage"] == {
            "prompt_tokens": 3,
            "completion_tokens": 2,
            "total_tokens": 5,
        }
        assert all("secret reasoning" not in repr(event) for event in events)
        assert any(
            event.progress and event.progress.activity is AgentProgressActivity.THINKING
            for event in events[:-1]
        )
        home = derive_codex_home(
            tmp_path, tenant_id="tenant-a", namespace="default", engine_ref="ref-a"
        )
        observed = Path((home / "observed-cwd").read_text(encoding="utf-8"))
        assert observed != Path.cwd()
        assert observed.name.startswith("amesh-codex-work-")
        assert (home / "observed-home").read_text(encoding="utf-8") == str(home)

    asyncio.run(scenario())


def test_delta_only_turn_delivers_exact_content_and_progress_frames_once(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        events = [
            event
            async for event in provider.stream(
                _request("delta-only"),
                ModelEngineAccess(engineRef="ref-a"),
            )
        ]
        response = events[-1].response
        assert response is not None
        assert response.payload["choices"][0]["message"]["content"] == '{"answer":"ok"}'
        progress = [event.progress for event in events if event.progress is not None]
        assert len(progress) == 5
        assert [item.status.value for item in progress] == [
            "STARTED",
            "STARTED",
            "DELTA",
            "COMPLETED",
            "COMPLETED",
        ]

    asyncio.run(scenario())


def test_successful_turn_without_usage_reports_unavailable_usage(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        response = await provider.invoke(_request("no-usage"), ModelEngineAccess(engineRef="ref-a"))
        assert response.payload["usage"] == {}

    asyncio.run(scenario())


def test_finite_timeout_is_total_and_maps_to_codex_timeout(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        with pytest.raises(CodexAppServerTimeout):
            await provider.invoke(
                _request("wait", timeout_seconds=0.2),
                ModelEngineAccess(engineRef="ref-a"),
            )
        home = derive_codex_home(
            tmp_path, tenant_id="tenant-a", namespace="default", engine_ref="ref-a"
        )
        assert (home / "observed-interrupt").read_text(encoding="utf-8") == "interrupted"

    asyncio.run(scenario())


def test_missing_timeout_has_no_total_deadline_but_keeps_frame_timeout(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path, timeout_seconds=0.3))
        response = await provider.invoke(
            _request("slow", timeout_seconds=None), ModelEngineAccess(engineRef="ref-a")
        )
        assert response.payload["choices"][0]["message"]["content"] == '{"answer":"ok"}'

    asyncio.run(scenario())


def test_native_tool_denials_do_not_disable_governed_local_image_input(tmp_path: Path) -> None:
    image_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    digest = hashlib.sha256(image_bytes).hexdigest()
    image = ImageArtifactRef(
        artifact={
            "reference": build_artifact_reference("input.png", 1, digest),
            "contentAddress": f"sha256:{digest}",
            "tenantId": "tenant-a",
            "namespace": "default",
            "path": "input.png",
            "version": 1,
            "mediaType": "image/png",
            "sizeBytes": len(image_bytes),
            "checksumSha256": digest,
            "provenance": ArtifactProvenance(
                source="test",
                originNamespace="default",
                createdBy="test",
                createdAt=datetime.now(UTC),
            ),
            "retention": ArtifactRetention(),
        },
        display=ImageDisplayMetadata(widthPixels=1, heightPixels=1),
    )

    class Resolver:
        async def resolve_image(self, requested: ImageArtifactRef, *, tenant_id: str) -> bytes:
            assert requested.artifact.tenant_id == tenant_id
            return image_bytes

    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path), image_resolver=Resolver())
        request = ModelProviderRequest(
            operation="structured",
            model="fixture-model",
            payload={
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "describe"},
                            {"type": "image_ref", "image": image.model_dump(mode="json")},
                        ],
                    }
                ]
            },
            timeoutSeconds=2,
            tenantId="tenant-a",
            namespace="default",
        )
        await provider.invoke(request, ModelEngineAccess(engineRef="ref-a"))

    asyncio.run(scenario())
    observed = json.loads(
        (
            derive_codex_home(
                tmp_path, tenant_id="tenant-a", namespace="default", engine_ref="ref-a"
            )
            / "observed-images.json"
        ).read_text(encoding="utf-8")
    )
    assert observed and observed[0]["exists"] is True


def test_cancellation_interrupts_turn(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        task = asyncio.create_task(
            provider.invoke(_request("wait"), ModelEngineAccess(engineRef="ref-a"))
        )
        await asyncio.sleep(0.1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())


def test_reasoning_effort_is_bounded(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        with pytest.raises(ValueError, match="reasoning effort"):
            await provider.invoke(
                _request("answer", reasoning_effort="unlimited"),
                ModelEngineAccess(engineRef="ref-a"),
            )

    asyncio.run(scenario())


def test_fixture_protocol_failure_is_bounded_and_reported(tmp_path: Path) -> None:
    async def scenario() -> None:
        provider = CodexAppServerModelProvider(_config(tmp_path))
        with pytest.raises(CodexAppServerError, match="fixture failure"):
            await provider.invoke(_request("fail"), ModelEngineAccess(engineRef="ref-a"))

    asyncio.run(scenario())


def test_account_manager_background_monitors_and_retains_login_completion(tmp_path: Path) -> None:
    async def scenario() -> None:
        manager = CodexAccountManager(_config(tmp_path), engine_ref="ref-a", namespace="default")
        try:
            browser = await manager.login_start("tenant-a")
            assert browser.action_required is True
            assert browser.auth_url == "https://chatgpt.com/codex/login"
            for _ in range(100):
                if "tenant-a" not in manager._pending:
                    break
                await asyncio.sleep(0.01)
            assert "tenant-a" not in manager._pending
            assert await manager.wait_login("tenant-a", browser.login_id) is True
            persisted_status = await manager.status("tenant-a")
            assert persisted_status.authenticated is True

            device = await manager.login_start("tenant-a", mode="device")
            assert device.verification_url == "https://auth.openai.com/codex/device"
            assert device.user_code == "ABCD-1234"
            assert await manager.wait_login("tenant-a", device.login_id) is True
            status = await manager.status("tenant-a", include_rate_limits=True, include_usage=True)
            assert status.authenticated is True
            assert status.rate_limits == {"rateLimits": {"limitId": "codex", "remaining": 9}}
            assert status.usage == {"summary": {"inputTokens": 3, "outputTokens": 2}}
            await manager.logout("tenant-a")
        finally:
            await manager.close()

    asyncio.run(scenario())


def test_status_polling_does_not_read_pending_login_stdout(tmp_path: Path) -> None:
    async def scenario() -> None:
        manager = CodexAccountManager(
            _config(tmp_path, fixture_args=("--login-delay", "0.15")),
            engine_ref="ref-a",
            namespace="default",
        )
        try:
            started = await manager.login_start("tenant-a")
            pending = await manager.status("tenant-a", include_rate_limits=True, include_usage=True)
            assert pending.authenticated is None
            assert pending.action_required is True
            assert pending.rate_limits is None
            assert pending.usage is None

            with pytest.raises(TimeoutError):
                await manager.wait_login("tenant-a", started.login_id, timeout_seconds=0.01)
            assert await manager.wait_login("tenant-a", started.login_id, timeout_seconds=1) is True
            ready = await manager.status("tenant-a")
            assert ready.authenticated is True
        finally:
            await manager.close()

    asyncio.run(scenario())


def test_failed_login_completion_is_retained_and_reported_unauthenticated(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        manager = CodexAccountManager(
            _config(
                tmp_path,
                fixture_args=("--login-delay", "0.05", "--login-failure"),
            ),
            engine_ref="ref-a",
            namespace="default",
        )
        try:
            started = await manager.login_start("tenant-a", mode="device")
            assert (
                await manager.wait_login("tenant-a", started.login_id, timeout_seconds=1) is False
            )
            assert "tenant-a" not in manager._pending
            assert await manager.wait_login("tenant-a", started.login_id) is False
            assert manager._login_tasks["tenant-a"][1].result().error == "fixture login failure"

            status = await manager.status("tenant-a", include_rate_limits=True, include_usage=True)
            assert status.authenticated is False
            assert status.action_required is True
            assert status.rate_limits is None
            assert status.usage is None
        finally:
            await manager.close()

    asyncio.run(scenario())


def test_account_status_is_truthful_before_login_when_optional_metadata_is_requested(
    tmp_path: Path,
) -> None:
    async def scenario() -> None:
        manager = CodexAccountManager(_config(tmp_path), engine_ref="ref-a", namespace="default")
        try:
            status = await manager.status(
                "tenant-a",
                include_rate_limits=True,
                include_usage=True,
            )
        finally:
            await manager.close()

        assert status.authenticated is False
        assert status.rate_limits is None
        assert status.usage is None
        assert status.action_required is True

    asyncio.run(scenario())


def test_unsafe_auth_url_is_rejected() -> None:
    from amesh.adapters.codex_app_server import _safe_auth_url

    with pytest.raises(CodexAppServerProtocolError):
        _safe_auth_url("https://evilchatgpt.com/login")
