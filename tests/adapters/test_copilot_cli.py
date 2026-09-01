from __future__ import annotations

import asyncio
import base64
import errno
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

import amesh.adapters.copilot_cli as copilot_cli
from amesh.adapters.copilot_cli import (
    COPILOT_CLI_ADAPTER_ID,
    COPILOT_CLI_ADAPTER_REVISION,
    CopilotAccountManager,
    CopilotCliConfig,
    CopilotCliError,
    CopilotCliModelProvider,
    CopilotCliProtocolError,
    CopilotCliTimeout,
    derive_copilot_home,
)
from amesh.domain.artifacts import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
)
from amesh.domain.image_inputs import ImageArtifactRef, ImageDisplayMetadata
from amesh.domain.image_validation import ImageValidationError
from amesh.ports import ModelEngineAccess, ModelProviderRequest

FIXTURE = Path(__file__).parents[1] / "fixtures" / "copilot_cli_fixture.py"
VALID_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class _Resolver:
    async def resolve_image(self, image: ImageArtifactRef, *, tenant_id: str) -> bytes:
        assert image.artifact.tenant_id == tenant_id
        return VALID_PNG


def _config(tmp_path: Path) -> CopilotCliConfig:
    return CopilotCliConfig(command=(sys.executable, str(FIXTURE)), state_root=tmp_path)


def _request(
    payload: dict[str, Any],
    *,
    tenant_id: str = "tenant-a",
    namespace: str = "space-a",
    timeout_seconds: float | None = 5,
) -> ModelProviderRequest:
    return ModelProviderRequest(
        operation="CHAT",
        model="gpt-5.4",
        payload=payload,
        timeoutSeconds=timeout_seconds,
        tenantId=tenant_id,
        namespace=namespace,
    )


def test_copilot_invocation_uses_isolated_home_empty_cwd_and_fail_closed_args(
    tmp_path: Path,
) -> None:
    async def scenario() -> list[Any]:
        adapter = CopilotCliModelProvider(_config(tmp_path))
        return [
            event
            async for event in adapter.stream(
                _request({"messages": [{"role": "user", "content": "hello"}]}),
                ModelEngineAccess(engineRef="binding-a"),
            )
        ]

    events = asyncio.run(scenario())
    assert [event.kind for event in events] == ["progress", "progress", "response"]
    home = derive_copilot_home(
        tmp_path, tenant_id="tenant-a", namespace="space-a", engine_ref="binding-a"
    )
    observed = json.loads((home / "fixture-args.json").read_text(encoding="utf-8"))
    args = observed["args"]
    assert "--output-format=json" in args
    assert "--disable-builtin-mcps" in args
    assert "--available-tools=" in args
    for flag in (
        "--available-tools=",
        "--excluded-tools=*",
        "--deny-tool=*",
        "--disallow-temp-dir",
    ):
        assert flag in args
    for flag in (
        "--no-custom-instructions",
        "--no-remote",
        "--no-remote-export",
        "--no-auto-update",
        "--no-bash-env",
        "--no-ask-user",
    ):
        assert flag in args
    assert observed["cwd_entries"] == []
    assert observed["environment"]["COPILOT_HOME"] == str(home)
    assert "COPILOT_GITHUB_TOKEN" not in observed["environment"]
    assert events[-1].response is not None
    assert events[-1].response.payload["choices"][0]["message"]["content"] == "copilot-ready"
    assert events[-1].response.payload["usage"] == {
        "input_tokens": 3,
        "output_tokens": 2,
        "ai_credits": 0.5,
        "total_tokens": 5,
    }
    assert "costUsd" not in events[-1].response.payload


def test_copilot_missing_usage_is_exposed_as_empty_object(tmp_path: Path) -> None:
    async def scenario() -> Any:
        return await CopilotCliModelProvider(_config(tmp_path)).invoke(
            _request({"input": "no-usage"}),
            ModelEngineAccess(engineRef="binding-a"),
        )

    response = asyncio.run(scenario())
    assert response.payload["usage"] == {}


def test_copilot_none_request_timeout_has_per_frame_timeout_only(tmp_path: Path) -> None:
    async def per_frame_timeout() -> None:
        config = CopilotCliConfig(
            command=(sys.executable, str(FIXTURE)), state_root=tmp_path / "per-frame", timeout_seconds=0.05
        )
        with pytest.raises(CopilotCliTimeout, match="waiting"):
            await CopilotCliModelProvider(config).invoke(
                _request({"input": "wait"}, timeout_seconds=None),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(per_frame_timeout())

    async def no_total_deadline() -> list[Any]:
        config = CopilotCliConfig(
            command=(sys.executable, str(FIXTURE)), state_root=tmp_path / "no-deadline", timeout_seconds=0.2
        )
        return [
            event
            async for event in CopilotCliModelProvider(config).stream(
                _request({"input": "slow"}, timeout_seconds=None),
                ModelEngineAccess(engineRef="binding-a"),
            )
        ]

    events = asyncio.run(no_total_deadline())
    assert events[-1].kind == "response"

    async def finite_deadline() -> None:
        config = CopilotCliConfig(
            command=(sys.executable, str(FIXTURE)), state_root=tmp_path / "finite", timeout_seconds=1
        )
        with pytest.raises(CopilotCliTimeout, match="timed out"):
            await CopilotCliModelProvider(config).invoke(
                _request({"input": "slow"}, timeout_seconds=0.25),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(finite_deadline())


def test_timeout_cleanup_preserves_typed_error_while_windows_releases_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_rmtree = copilot_cli.shutil.rmtree
    delayed_paths: list[Path] = []

    def delayed_rmtree(path: str | Path, *args: Any, **kwargs: Any) -> None:
        candidate = Path(path)
        if candidate.name.startswith("amesh-copilot-cwd-") and len(delayed_paths) < 2:
            delayed_paths.append(candidate)
            if len(delayed_paths) == 1:
                raise PermissionError("cwd is still held by the child process")
            raise OSError(errno.ENOTEMPTY, "cwd still contains a delete-pending entry")
        original_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(copilot_cli.shutil, "rmtree", delayed_rmtree)

    async def scenario() -> None:
        config = CopilotCliConfig(
            command=(sys.executable, str(FIXTURE)),
            state_root=tmp_path,
            timeout_seconds=1,
            cancel_grace_seconds=0.2,
        )
        with pytest.raises(CopilotCliTimeout, match="timed out"):
            await CopilotCliModelProvider(config).invoke(
                _request({"input": "slow"}, timeout_seconds=0.05),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(scenario())
    assert len(delayed_paths) == 2
    assert not delayed_paths[-1].exists()


def test_copilot_structured_prompt_and_image_are_translated_at_boundary(tmp_path: Path) -> None:
    content = VALID_PNG
    digest = hashlib.sha256(content).hexdigest()
    image = ImageArtifactRef(
        artifact=ArtifactRef(
            reference=build_artifact_reference("input.png", 1, digest),
            contentAddress=f"sha256:{digest}",
            tenantId="tenant-a",
            namespace="space-a",
            path="input.png",
            version=1,
            mediaType="image/png",
            sizeBytes=len(content),
            checksumSha256=digest,
            provenance=ArtifactProvenance(
                source="test",
                originNamespace="space-a",
                createdBy="test",
                createdAt=datetime.now(UTC),
            ),
            retention=ArtifactRetention(),
        ),
        display=ImageDisplayMetadata(widthPixels=1, heightPixels=1),
    )

    async def scenario() -> None:
        adapter = CopilotCliModelProvider(_config(tmp_path), image_resolver=_Resolver())
        await adapter.invoke(
            _request(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "describe"},
                                {"type": "image_ref", "image": image.model_dump(mode="json")},
                            ],
                        }
                    ],
                    "response_format": {
                        "type": "json_schema",
                        "json_schema": {"schema": {"type": "object"}},
                    },
                }
            ),
            ModelEngineAccess(engineRef="binding-a"),
        )

    asyncio.run(scenario())
    home = derive_copilot_home(
        tmp_path, tenant_id="tenant-a", namespace="space-a", engine_ref="binding-a"
    )
    observed = json.loads((home / "fixture-args.json").read_text(encoding="utf-8"))
    prompt = observed["args"][observed["args"].index("-p") + 1]
    assert "[Attached image:" in prompt
    assert "JSON Schema" in prompt
    assert "--attachment" in observed["args"]
    assert observed["attachment_exists"] == [True]
    attached = next(Path(part.rstrip("]")) for part in prompt.split() if "image-0001.png" in part)
    assert not attached.exists()


def test_copilot_rejects_resolved_image_with_mismatched_checksum(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    os_temp = tmp_path / "os-temp"
    os_temp.mkdir()
    monkeypatch.setattr(copilot_cli.tempfile, "tempdir", str(os_temp))
    digest = hashlib.sha256(VALID_PNG).hexdigest()
    image = ImageArtifactRef(
        artifact=ArtifactRef(
            reference=build_artifact_reference("input.png", 1, digest),
            contentAddress=f"sha256:{digest}",
            tenantId="tenant-a",
            namespace="space-a",
            path="input.png",
            version=1,
            mediaType="image/png",
            sizeBytes=len(VALID_PNG),
            checksumSha256=digest,
            provenance=ArtifactProvenance(
                source="test",
                originNamespace="space-a",
                createdBy="test",
                createdAt=datetime.now(UTC),
            ),
            retention=ArtifactRetention(),
        ),
        display=ImageDisplayMetadata(widthPixels=1, heightPixels=1),
    )
    wrong_digest = "0" * 64
    mismatched = image.model_copy(
        update={
            "artifact": image.artifact.model_copy(
                update={
                    "reference": build_artifact_reference("input.png", 1, wrong_digest),
                    "content_address": f"sha256:{wrong_digest}",
                    "checksum_sha256": wrong_digest,
                }
            )
        }
    )

    async def scenario() -> None:
        adapter = CopilotCliModelProvider(_config(tmp_path), image_resolver=_Resolver())
        with pytest.raises(ImageValidationError, match="checksum"):
            await adapter.invoke(
                _request(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_ref",
                                        "image": mismatched.model_dump(mode="json"),
                                    }
                                ],
                            }
                        ]
                    }
                ),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(scenario())
    assert not list(os_temp.glob("amesh-copilot-cwd-*"))


def test_copilot_logout_spawn_failure_removes_owned_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    os_temp = tmp_path / "os-temp"
    os_temp.mkdir()
    monkeypatch.setattr(copilot_cli.tempfile, "tempdir", str(os_temp))

    async def scenario() -> None:
        manager = CopilotAccountManager(
            CopilotCliConfig(command=("missing-copilot-command",), state_root=tmp_path),
            engine_ref="binding-a",
            namespace="space-a",
        )
        with pytest.raises(CopilotCliError, match="resolve"):
            await manager.logout("tenant-a")

    asyncio.run(scenario())
    assert not list(os_temp.glob("amesh-copilot-logout-cwd-*"))


@pytest.mark.parametrize(
    "mode, expected", [("device", "github_device_code"), ("browser", "github_browser")]
)
def test_copilot_account_login_challenge_and_logout_are_safe(
    tmp_path: Path, mode: str, expected: str
) -> None:
    async def scenario() -> Any:
        manager = CopilotAccountManager(
            _config(tmp_path), engine_ref="binding-a", namespace="space-a"
        )
        start = await manager.login_start("tenant-a", mode=mode)
        pending = await manager.status("tenant-a")
        await asyncio.sleep(0.1)
        before = await manager.status("tenant-a")
        await manager.logout("tenant-a")
        after = await manager.status("tenant-a")
        await manager.close()
        return start, pending, before, after

    start, pending, before, after = asyncio.run(scenario())
    assert start.kind == expected
    assert start.action_required is True
    assert pending.authenticated is None
    assert pending.action_required is True
    assert before.authenticated is True
    assert after.authenticated is False
    assert start.user_code == "ABCD-1234" if mode == "device" else start.user_code is None
    home = derive_copilot_home(
        tmp_path, tenant_id="tenant-a", namespace="space-a", engine_ref="binding-a"
    )
    assert (home / "fixture-logout").read_text(encoding="utf-8") == "ok"
    assert "token" not in repr(start).lower()


def test_copilot_fresh_account_manager_reports_unknown_readiness(tmp_path: Path) -> None:
    async def scenario() -> Any:
        manager = CopilotAccountManager(
            _config(tmp_path), engine_ref="binding-a", namespace="space-a"
        )
        result = await manager.status("tenant-a")
        await manager.close()
        return result

    status = asyncio.run(scenario())
    assert status.authenticated is None
    assert status.action_required is True


def test_copilot_malformed_json_and_cancellation_are_bounded(tmp_path: Path) -> None:
    async def malformed() -> None:
        adapter = CopilotCliModelProvider(_config(tmp_path))
        with pytest.raises(CopilotCliProtocolError):
            await adapter.invoke(
                _request({"input": "malformed"}),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(malformed())

    async def cancelled() -> None:
        config = CopilotCliConfig(
            command=(sys.executable, str(FIXTURE)),
            state_root=tmp_path / "cancelled",
            timeout_seconds=1,
            cancel_grace_seconds=0.1,
        )
        task = asyncio.create_task(
            CopilotCliModelProvider(config).invoke(
                _request({"input": "wait"}),
                ModelEngineAccess(engineRef="binding-a"),
            )
        )
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(cancelled())

    async def failed() -> None:
        adapter = CopilotCliModelProvider(_config(tmp_path / "failed"))
        with pytest.raises(CopilotCliError, match="fixture failure"):
            await adapter.invoke(
                _request({"input": "error"}),
                ModelEngineAccess(engineRef="binding-a"),
            )

    asyncio.run(failed())


def test_copilot_adapter_identity_is_pinned() -> None:
    assert COPILOT_CLI_ADAPTER_ID == "github-copilot-cli"
    assert COPILOT_CLI_ADAPTER_REVISION == "1.0.0"


def test_copilot_home_isolated_by_tenant_namespace_and_binding(tmp_path: Path) -> None:
    homes = {
        derive_copilot_home(tmp_path, tenant_id=tenant, namespace=namespace, engine_ref=engine)
        for tenant, namespace, engine in (
            ("tenant-a", "space-a", "binding-a"),
            ("tenant-b", "space-a", "binding-a"),
            ("tenant-a", "space-b", "binding-a"),
            ("tenant-a", "space-a", "binding-b"),
        )
    }
    assert len(homes) == 4
