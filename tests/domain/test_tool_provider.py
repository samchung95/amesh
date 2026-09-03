from __future__ import annotations

import asyncio
import logging
from functools import wraps
from uuid import uuid4

import pytest

import amesh.tasks.tool_provider as tool_provider_tasks
from amesh.domain import (
    AgentToolRef,
    AmbiguousToolInvocation,
    McpDiscoveryResult,
    ToolDescriptor,
    ToolDiscovery,
    ToolImpact,
    ToolInvocationRequest,
    ToolPolicy,
    ToolProviderKind,
    ToolProviderRef,
    ToolSchemaError,
)
from amesh.plugins import IsolatedPluginToolProvider
from amesh.tasks import GovernedToolInvoker, InMemoryToolInvocationJournal, McpToolProvider


def _identity(kind: ToolProviderKind = ToolProviderKind.PLUGIN) -> ToolProviderRef:
    return ToolProviderRef(kind=kind, key="neutral.example", revision=1)


def _policy() -> ToolPolicy:
    return ToolPolicy(allowedTools=("example.echo",))


def async_test(function):
    @wraps(function)
    def run() -> None:
        asyncio.run(function())

    return run


def test_tool_invocation_timeout_preserves_default_and_accepts_explicit_none() -> None:
    default = ToolInvocationRequest(provider=_identity(), toolName="example.echo")
    disabled = ToolInvocationRequest(
        provider=_identity(),
        toolName="example.echo",
        timeoutSeconds=None,
    )

    assert default.timeout_seconds == 30
    assert default.model_dump(mode="json", by_alias=True)["timeoutSeconds"] == 30
    assert disabled.timeout_seconds is None


def test_disabled_tool_timeout_bypasses_application_timer(monkeypatch: pytest.MonkeyPatch) -> None:
    identity = _identity()

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        return {"value": request.arguments["value"]}

    async def unexpected_wait_for(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("asyncio.wait_for must not wrap disabled tool timeouts")

    monkeypatch.setattr(tool_provider_tasks.asyncio, "wait_for", unexpected_wait_for)
    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        arguments={"value": "hello"},
        timeoutSeconds=None,
    )

    result = asyncio.run(
        GovernedToolInvoker(provider, InMemoryToolInvocationJournal()).invoke(request, _policy())
    )

    assert result.output == {"value": "hello"}


def test_mcp_provider_propagates_disabled_timeout_to_discovery_and_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = _identity(ToolProviderKind.MCP)
    observed: list[tuple[str, float | None]] = []

    async def discover(
        _endpoint: str,
        _credential: str,
        *,
        timeout_seconds: float | None,
        **_kwargs: object,
    ) -> McpDiscoveryResult:
        observed.append(("discover", timeout_seconds))
        return McpDiscoveryResult(
            serverName="test",
            serverVersion="1",
            tools=(),
            digest="sha256:" + "0" * 64,
        )

    async def call(
        _endpoint: str,
        _credential: str,
        _tool: str,
        _arguments: dict[str, object],
        *,
        timeout_seconds: float | None,
        **_kwargs: object,
    ) -> dict[str, object]:
        observed.append(("call", timeout_seconds))
        return {"structuredContent": {"ok": True}}

    monkeypatch.setattr(tool_provider_tasks, "discover_mcp_server", discover)
    monkeypatch.setattr(tool_provider_tasks, "_call_tool", call)
    provider = McpToolProvider(
        identity,
        "https://mcp.example.test",
        "credential",
        timeout_seconds=None,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        timeoutSeconds=None,
    )

    async def scenario() -> None:
        await provider.discover()
        result = await provider.invoke(request)
        assert result.output == {"structuredContent": {"ok": True}}

    asyncio.run(scenario())

    assert observed == [("discover", None), ("call", None)]


@async_test
async def test_mcp_and_isolated_plugin_use_one_discovery_policy_and_schema_contract() -> None:
    identity = _identity()
    calls: list[str] = []

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        calls.append(request.tool_name)
        return {"value": request.arguments["value"]}

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
                outputSchema={"type": "object", "required": ["value"]},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
    )
    invoker = GovernedToolInvoker(provider, InMemoryToolInvocationJournal())
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        arguments={"value": "hello"},
        invocationId=uuid4(),
    )

    result = await invoker.invoke(request, _policy())

    assert result.output == {"value": "hello"}
    assert result.evidence.provider == identity
    assert result.evidence.state.value == "SUCCEEDED"
    assert calls == ["example.echo"]
    assert (await invoker.discover()).digest.startswith("sha256:")


@async_test
async def test_provider_contract_rejects_schema_drift_before_rpc() -> None:
    identity = _identity()
    called = False

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        nonlocal called
        called = True
        return {"value": request.arguments["value"]}

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object", "required": ["value"]},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        arguments={},
    )

    with pytest.raises(ToolSchemaError):
        await GovernedToolInvoker(provider, InMemoryToolInvocationJournal()).invoke(
            request, _policy()
        )
    assert called is False


@async_test
async def test_model_tool_input_schema_error_can_be_returned_without_invocation() -> None:
    identity = _identity()
    called = False

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        nonlocal called
        called = True
        return {"value": request.arguments["value"]}

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={
                    "type": "object",
                    "required": ["value"],
                    "additionalProperties": False,
                },
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
    )
    result = await GovernedToolInvoker(provider, InMemoryToolInvocationJournal()).invoke(
        ToolInvocationRequest(provider=identity, toolName="example.echo", arguments={}),
        _policy(),
        recover_input_validation=True,
    )

    assert result.output["isError"] is True
    assert "arguments failed schema" in result.output["content"][0]["text"]
    assert result.evidence.state.value == "FAILED"
    assert called is False


@async_test
async def test_started_journal_record_is_ambiguous_and_is_not_repeated() -> None:
    identity = _identity()
    calls = 0

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"value": request.arguments["value"]}

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
    )
    journal = InMemoryToolInvocationJournal()
    invoker = GovernedToolInvoker(provider, journal)
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        invocationId=uuid4(),
    )
    await journal.begin(request, request_hash="0" * 64, metadata={})

    with pytest.raises(AmbiguousToolInvocation):
        await invoker.invoke(request, _policy())
    assert calls == 0


@async_test
async def test_timeout_cancels_provider_and_records_ambiguous_outcome() -> None:
    identity = _identity()
    cancelled: list[str] = []

    async def invoke(request: ToolInvocationRequest) -> dict[str, object]:
        await asyncio.sleep(1)
        return {"value": request.arguments.get("value")}

    async def cancel(invocation_id: str) -> None:
        cancelled.append(invocation_id)

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
        cancel=cancel,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        timeoutSeconds=0.01,
    )
    journal = InMemoryToolInvocationJournal()

    with pytest.raises(TimeoutError):
        await GovernedToolInvoker(provider, journal).invoke(request, _policy())
    assert cancelled == [str(request.invocation_id)]
    assert journal.records[str(request.invocation_id)].evidence.ambiguous_external_outcome is True


def test_timeout_cancel_failure_is_logged_and_recorded_without_replacing_timeout(
    caplog: pytest.LogCaptureFixture,
) -> None:
    identity = _identity()

    async def invoke(_request: ToolInvocationRequest) -> dict[str, object]:
        await asyncio.sleep(1)
        return {"value": "never"}

    async def cancel(_invocation_id: str) -> None:
        raise RuntimeError("cancellation unavailable")

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
        cancel=cancel,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        timeoutSeconds=0.01,
    )
    journal = InMemoryToolInvocationJournal()

    with caplog.at_level(logging.ERROR), pytest.raises(TimeoutError):
        asyncio.run(GovernedToolInvoker(provider, journal).invoke(request, _policy()))

    evidence = journal.records[str(request.invocation_id)].evidence
    assert evidence.state.value == "AMBIGUOUS"
    assert evidence.error is not None
    assert "cancellation failed: RuntimeError: cancellation unavailable" in evidence.error
    assert "tool provider cancellation failed" in caplog.text


@async_test
async def test_cancellation_during_timeout_cleanup_propagates_cancelled_error() -> None:
    identity = _identity()
    cleanup_started = asyncio.Event()

    async def invoke(_request: ToolInvocationRequest) -> dict[str, object]:
        await asyncio.sleep(1)
        return {"value": "never"}

    async def cancel(_invocation_id: str) -> None:
        cleanup_started.set()
        await asyncio.sleep(1)

    provider = IsolatedPluginToolProvider(
        identity,
        (
            ToolDescriptor(
                provider=identity,
                name="example.echo",
                inputSchema={"type": "object"},
                impact=ToolImpact.READ_ONLY,
            ),
        ),
        invoke,
        cancel=cancel,
    )
    request = ToolInvocationRequest(
        provider=identity,
        toolName="example.echo",
        timeoutSeconds=0.01,
    )
    invocation = asyncio.create_task(
        GovernedToolInvoker(provider, InMemoryToolInvocationJournal()).invoke(
            request,
            _policy(),
        )
    )

    await cleanup_started.wait()
    invocation.cancel()

    with pytest.raises(asyncio.CancelledError):
        await invocation


def test_invalid_discovery_digest_is_rejected() -> None:
    identity = _identity()
    with pytest.raises(ValueError, match="digest"):
        ToolDiscovery(provider=identity, tools=(), digest="sha256:" + "0" * 64)


def test_legacy_mcp_tool_reference_and_provider_pin_are_compatible() -> None:
    digest = "sha256:" + "1" * 64
    legacy = AgentToolRef(
        connectionKey="catalog",
        connectionRevision=2,
        toolName="lookup",
        schemaDigest=digest,
    )
    plugin = AgentToolRef(
        providerKind=ToolProviderKind.PLUGIN,
        providerKey="neutral.example",
        providerRevision=3,
        toolName="example.echo",
        schemaDigest=digest,
    )

    assert legacy.provider_kind is ToolProviderKind.MCP
    assert legacy.effective_provider_key == "catalog"
    assert legacy.effective_provider_revision == 2
    assert plugin.provider_kind is ToolProviderKind.PLUGIN
    assert plugin.effective_provider_key == "neutral.example"
    assert plugin.effective_provider_revision == 3
