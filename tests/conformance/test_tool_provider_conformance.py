from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr

from amesh.adapters.postgres import PostgresToolInvocationJournal
from amesh.domain import (
    AmbiguousToolInvocation,
    McpDiscoveryResult,
    McpToolImpact,
    McpToolPin,
    ToolDescriptor,
    ToolImpact,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolPolicy,
    ToolPolicyDenied,
    ToolProviderKind,
    ToolProviderRef,
    ToolSchemaError,
    canonical_hash,
    request_hash,
)
from amesh.migrations import (
    apply_migrations,
    create_ephemeral_database,
    drop_ephemeral_database,
)
from amesh.plugins import IsolatedPluginToolProvider
from amesh.ports import ToolProvider
from amesh.tasks import GovernedToolInvoker, InMemoryToolInvocationJournal, McpToolProvider

TEST_DATABASE_URL = os.getenv("AMESH_TEST_DATABASE_URL")
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"

_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
        "mode": {"type": "string"},
    },
    "required": ["value"],
    "additionalProperties": False,
}
_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"value": {"type": "string"}},
    "required": ["value"],
    "additionalProperties": False,
}


@dataclass
class ProviderFixture:
    provider: ToolProvider
    identity: ToolProviderRef
    calls: list[ToolInvocationRequest]
    cancellations: list[str]


class RecordingJournal(InMemoryToolInvocationJournal):
    """In-memory restart double that retains the durable metadata boundary."""

    def __init__(self) -> None:
        super().__init__()
        self.metadata: dict[str, dict[str, object]] = {}

    async def begin(
        self,
        request: ToolInvocationRequest,
        *,
        request_hash: str,
        metadata: dict[str, object],
    ) -> ToolInvocationResult | None:
        self.metadata[str(request.invocation_id)] = metadata
        return await super().begin(request, request_hash=request_hash, metadata=metadata)


def _descriptor(identity: ToolProviderRef) -> ToolDescriptor:
    return ToolDescriptor(
        provider=identity,
        name="example_echo",
        description="A local, side-effect-free conformance fixture.",
        inputSchema=_INPUT_SCHEMA,
        outputSchema=_OUTPUT_SCHEMA,
        impact=ToolImpact.READ_ONLY,
    )


def _mcp_result(pin: McpToolPin) -> McpDiscoveryResult:
    digest = "sha256:" + canonical_hash(
        {
            "serverName": "amesh-conformance",
            "serverVersion": "1",
            "tools": [
                {
                    "name": pin.name,
                    "inputSchema": pin.input_schema,
                    "outputSchema": pin.output_schema,
                }
            ],
        }
    )
    return McpDiscoveryResult(
        serverName="amesh-conformance",
        serverVersion="1",
        tools=(pin,),
        digest=digest,
    )


def _provider_fixture(monkeypatch: pytest.MonkeyPatch, kind: str) -> ProviderFixture:
    provider_kind = ToolProviderKind(kind)
    identity = ToolProviderRef(
        kind=provider_kind,
        key=f"neutral.{kind}",
        revision=7,
    )
    descriptor = _descriptor(identity)
    calls: list[ToolInvocationRequest] = []
    cancellations: list[str] = []

    async def invoke(request: ToolInvocationRequest) -> dict[str, Any]:
        calls.append(request)
        if request.arguments.get("mode") == "slow":
            await asyncio.sleep(10)
        return {"value": request.arguments["value"]}

    async def cancel(invocation_id: str) -> None:
        cancellations.append(invocation_id)

    provider: ToolProvider
    if provider_kind is ToolProviderKind.PLUGIN:
        provider = IsolatedPluginToolProvider(
            identity,
            (descriptor,),
            invoke,
            cancel=cancel,
        )
        return ProviderFixture(provider, identity, calls, cancellations)

    pin = McpToolPin(
        name=descriptor.name,
        description=descriptor.description,
        inputSchema=descriptor.input_schema,
        outputSchema=descriptor.output_schema,
        impact=McpToolImpact.READ_ONLY,
    )
    discovery = _mcp_result(pin)

    async def discover(
        endpoint: str,
        credential: str,
        **kwargs: object,
    ) -> McpDiscoveryResult:
        del endpoint, credential, kwargs
        return discovery

    async def call_tool(
        endpoint: str,
        credential: str,
        tool_name: str,
        arguments: dict[str, Any],
        **kwargs: object,
    ) -> dict[str, Any]:
        del endpoint, credential, tool_name, kwargs
        request = ToolInvocationRequest(
            provider=identity,
            toolName=descriptor.name,
            arguments=arguments,
        )
        calls.append(request)
        if arguments.get("mode") == "slow":
            await asyncio.sleep(10)
        return {"structuredContent": {"value": arguments["value"]}}

    monkeypatch.setattr("amesh.tasks.tool_provider.discover_mcp_server", discover)
    monkeypatch.setattr("amesh.tasks.tool_provider._call_tool", call_tool)
    provider = McpToolProvider(
        identity,
        "http://mcp.conformance.test/tools",
        "local-test-credential",
        pinned_tools=(pin,),
    )
    # The MCP wire adapter has no provider-side cancellation operation. The
    # governed boundary still invokes this seam on timeout/caller cancel.
    monkeypatch.setattr(provider, "cancel", cancel)
    return ProviderFixture(provider, identity, calls, cancellations)


def _policy() -> ToolPolicy:
    return ToolPolicy(allowedTools=("example_echo",))


def _request(fixture: ProviderFixture, **updates: object) -> ToolInvocationRequest:
    values: dict[str, object] = {
        "provider": fixture.identity,
        "toolName": "example_echo",
        "arguments": {"value": "accepted"},
        "tenantId": "default",
        "namespace": "conformance",
    }
    values.update(updates)
    return ToolInvocationRequest.model_validate(values)


def _output_value(result: Any) -> object:
    if "structuredContent" in result.output:
        return result.output["structuredContent"]["value"]
    return result.output["value"]


@pytest.mark.parametrize("kind", ("mcp", "plugin"))
def test_provider_neutral_conformance_suite(kind: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run one contract suite against both concrete provider identities."""

    async def scenario() -> None:
        fixture = _provider_fixture(monkeypatch, kind)
        assert fixture.provider.identity == fixture.identity
        journal = RecordingJournal()
        invoker = GovernedToolInvoker(fixture.provider, journal)

        discovery = await invoker.discover()
        assert discovery.provider == fixture.identity
        assert discovery.tool("example_echo").provider == fixture.identity

        with pytest.raises(ToolPolicyDenied):
            await invoker.invoke(
                _request(fixture),
                ToolPolicy(allowedTools=()),
            )
        with pytest.raises(ToolSchemaError):
            await invoker.invoke(
                _request(fixture, arguments={"unexpected": "rejected"}),
                _policy(),
            )
        assert fixture.calls == []

        secret = "conformance-secret"
        redacted_request = _request(
            fixture,
            arguments={"value": f"prefix-{secret}"},
            secretValues=(SecretStr(secret),),
        )
        redacted_result = await invoker.invoke(redacted_request, _policy())
        assert redacted_result.evidence.provider == fixture.identity
        assert secret not in redacted_result.evidence.request_hash
        assert secret not in json.dumps(journal.metadata, sort_keys=True)

        accepted_request = _request(fixture)
        accepted = await invoker.invoke(accepted_request, _policy())
        reused = await invoker.invoke(accepted_request, _policy())
        assert reused == accepted
        assert _output_value(accepted) == "accepted"
        assert len(fixture.calls) == 2

        timeout_request = _request(
            fixture,
            arguments={"value": "timeout", "mode": "slow"},
            timeoutSeconds=0.01,
        )
        with pytest.raises(TimeoutError):
            await invoker.invoke(timeout_request, _policy())
        assert str(timeout_request.invocation_id) in fixture.cancellations

        cancel_request = _request(
            fixture,
            arguments={"value": "cancel", "mode": "slow"},
            timeoutSeconds=30,
        )
        cancelled = asyncio.create_task(invoker.invoke(cancel_request, _policy()))
        await asyncio.sleep(0.01)
        cancelled.cancel()
        with pytest.raises(asyncio.CancelledError):
            await cancelled
        assert str(cancel_request.invocation_id) in fixture.cancellations

        ambiguous_request = _request(fixture, arguments={"value": "restart"})
        ambiguity_journal = InMemoryToolInvocationJournal()
        ambiguity_invoker = GovernedToolInvoker(fixture.provider, ambiguity_journal)
        descriptor = (await ambiguity_invoker.discover()).tool("example_echo")
        digest = request_hash(ambiguous_request, descriptor)
        await ambiguity_journal.begin(
            ambiguous_request,
            request_hash=digest,
            metadata={
                "schemaDigest": descriptor.schema_digest,
                "policyDigest": _policy().digest,
            },
        )
        with pytest.raises(AmbiguousToolInvocation):
            await ambiguity_invoker.invoke(ambiguous_request, _policy())

    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ("mcp", "plugin"))
@pytest.mark.skipif(
    TEST_DATABASE_URL is None,
    reason="AMESH_TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_postgres_durable_provider_ownership_survives_restart(
    kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exercise durable reuse, ambiguous recovery and tenant ownership for both adapters."""

    async def scenario() -> None:
        if TEST_DATABASE_URL is None:
            raise RuntimeError("AMESH_TEST_DATABASE_URL is required")
        fixture = _provider_fixture(monkeypatch, kind)
        database = await create_ephemeral_database(TEST_DATABASE_URL)
        engine = None
        try:
            await apply_migrations(database.database_url, MIGRATIONS)
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(database.database_url)
            journal = PostgresToolInvocationJournal(engine)
            invoker = GovernedToolInvoker(fixture.provider, journal)

            accepted_request = _request(fixture, arguments={"value": "durable"})
            accepted = await invoker.invoke(accepted_request, _policy())
            restarted = GovernedToolInvoker(fixture.provider, PostgresToolInvocationJournal(engine))
            reused = await restarted.invoke(accepted_request, _policy())
            assert reused.output == accepted.output
            assert reused.evidence.provider == accepted.evidence.provider == fixture.identity
            assert reused.evidence.request_hash == accepted.evidence.request_hash
            assert reused.evidence.state is accepted.evidence.state
            assert reused.evidence.provider == fixture.identity
            assert len(fixture.calls) == 1

            ambiguous_request = _request(
                fixture,
                arguments={"value": "crash", "mode": "slow"},
                timeoutSeconds=0.01,
            )
            with pytest.raises(TimeoutError):
                await invoker.invoke(ambiguous_request, _policy())
            calls_before_restart = len(fixture.calls)
            restarted_after_crash = GovernedToolInvoker(
                fixture.provider,
                PostgresToolInvocationJournal(engine),
            )
            with pytest.raises(AmbiguousToolInvocation):
                await restarted_after_crash.invoke(ambiguous_request, _policy())
            assert len(fixture.calls) == calls_before_restart

            with pytest.raises(LookupError):
                await restarted_after_crash.invoke(
                    accepted_request.model_copy(update={"tenant_id": "amesh-system"}),
                    _policy(),
                )
        finally:
            if engine is not None:
                await engine.dispose()
            await drop_ephemeral_database(TEST_DATABASE_URL, database.name)

    asyncio.run(scenario())
