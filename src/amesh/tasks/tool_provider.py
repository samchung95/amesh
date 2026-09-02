from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from amesh.domain import (
    AgentInvocationKind,
    AgentInvocationStart,
    AgentInvocationState,
    AmbiguousToolInvocation,
    McpToolPin,
    ToolDescriptor,
    ToolDiscovery,
    ToolImpact,
    ToolInputValidationError,
    ToolInvocationEvidence,
    ToolInvocationRequest,
    ToolInvocationResult,
    ToolInvocationState,
    ToolPolicy,
    ToolProviderError,
    ToolProviderRef,
    authorize_tool_call,
    canonical_hash,
    request_hash,
    validate_tool_arguments,
    validate_tool_output,
)
from amesh.ports import AgentPrimitiveRepository, ToolInvocationJournal, ToolProvider

from .http import HttpTaskPolicy
from .mcp import McpTargetResolver, _call_tool, discover_mcp_server


class InMemoryToolInvocationJournal:
    """Small journal implementation for contract tests and local provider authors."""

    def __init__(self) -> None:
        self.records: dict[str, ToolInvocationResult] = {}

    async def begin(
        self,
        request: ToolInvocationRequest,
        *,
        request_hash: str,
        metadata: dict[str, object],
    ) -> ToolInvocationResult | None:
        del metadata
        key = str(request.invocation_id)
        prior = self.records.get(key)
        if prior is not None:
            if prior.evidence.request_hash not in {"0" * 64, request_hash}:
                raise ToolProviderError("tool invocation key was reused with a different request")
            return prior
        self.records[key] = ToolInvocationResult(
            output={},
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest="sha256:" + "0" * 64,
                invocationId=request.invocation_id,
                requestHash=request_hash,
                policyDigest="sha256:" + "0" * 64,
                state=ToolInvocationState.STARTED,
            ),
        )
        return None

    async def complete(self, request: ToolInvocationRequest, result: ToolInvocationResult) -> None:
        self.records[str(request.invocation_id)] = result


class AgentPrimitiveInvocationJournal:
    """Neutral journal adapter over the existing tenant-scoped MCP ledger."""

    def __init__(self, repository: AgentPrimitiveRepository) -> None:
        self._repository = repository

    async def begin(
        self,
        request: ToolInvocationRequest,
        *,
        request_hash: str,
        metadata: dict[str, object],
    ) -> ToolInvocationResult | None:
        claim = await self._repository.begin_invocation(
            AgentInvocationStart(
                invocationId=request.invocation_id,
                tenantId=request.tenant_id,
                namespace=request.namespace,
                executionId=request.execution_id,
                taskRunId=request.task_run_id,
                attempt=request.attempt,
                kind=AgentInvocationKind.MCP,
                operation=_journal_operation_name(request),
                requestHash=request_hash,
                requestMetadata=metadata,
            )
        )
        if claim.created:
            return None
        record = claim.record
        state = (
            ToolInvocationState.STARTED
            if record.state is AgentInvocationState.STARTED
            else (
                ToolInvocationState.SUCCEEDED
                if record.state is AgentInvocationState.SUCCEEDED
                else ToolInvocationState.FAILED
            )
        )
        return ToolInvocationResult(
            output=dict(record.result or {}),
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest=str(metadata.get("schemaDigest", "sha256:" + "0" * 64)),
                invocationId=record.invocation_id,
                requestHash=record.request_hash,
                policyDigest=str(metadata.get("policyDigest", "sha256:" + "0" * 64)),
                state=state,
                startedAt=record.started_at,
                completedAt=record.completed_at,
                ambiguousExternalOutcome=state is ToolInvocationState.STARTED,
                error=record.error,
            ),
        )

    async def complete(self, request: ToolInvocationRequest, result: ToolInvocationResult) -> None:
        if result.evidence.state is ToolInvocationState.AMBIGUOUS:
            return
        state = (
            AgentInvocationState.SUCCEEDED
            if result.evidence.state is ToolInvocationState.SUCCEEDED
            else AgentInvocationState.FAILED
        )
        await self._repository.complete_invocation(
            result.evidence.invocation_id,
            tenant_id=request.tenant_id,
            state=state,
            result=result.output if state is AgentInvocationState.SUCCEEDED else None,
            error=result.evidence.error if state is AgentInvocationState.FAILED else None,
        )


def _journal_operation_name(request: ToolInvocationRequest) -> str:
    operation = f"{request.provider.key}.{request.tool_name}"
    if request.invocation_key is None:
        return operation[:128]
    return f"{operation[:80]}#{canonical_hash(request.invocation_key)[:32]}"


class GovernedToolInvoker:
    """Apply one policy, schema, timeout and recovery boundary to any provider."""

    def __init__(self, provider: ToolProvider, journal: ToolInvocationJournal) -> None:
        self._provider = provider
        self._journal = journal

    async def discover(self) -> ToolDiscovery:
        discovery = await self._provider.discover()
        if discovery.provider != self._provider.identity:
            raise ToolProviderError("provider returned discovery for a different identity")
        return discovery

    async def invoke(
        self,
        request: ToolInvocationRequest,
        policy: ToolPolicy,
        *,
        recover_input_validation: bool = False,
    ) -> ToolInvocationResult:
        if request.provider != self._provider.identity:
            raise ToolProviderError("tool request provider identity does not match the adapter")
        descriptor = (await self.discover()).tool(request.tool_name)
        authorize_tool_call(descriptor, request, policy)
        digest = request_hash(request, descriptor)
        try:
            validate_tool_arguments(descriptor, request.arguments)
        except ToolInputValidationError as exc:
            if not recover_input_validation:
                raise
            now = datetime.now(UTC)
            error = str(exc)[:4096]
            return ToolInvocationResult(
                output={
                    "isError": True,
                    "content": [{"type": "text", "text": error}],
                },
                evidence=ToolInvocationEvidence(
                    provider=request.provider,
                    toolName=request.tool_name,
                    schemaDigest=descriptor.schema_digest,
                    invocationId=request.invocation_id,
                    requestHash=digest,
                    policyDigest=policy.digest,
                    state=ToolInvocationState.FAILED,
                    startedAt=now,
                    completedAt=now,
                    error=error,
                ),
            )
        prior = await self._journal.begin(
            request,
            request_hash=digest,
            metadata={
                "provider": request.provider.model_dump(mode="json"),
                "tool": request.tool_name,
                "schemaDigest": descriptor.schema_digest,
                "policyDigest": policy.digest,
            },
        )
        if prior is not None:
            if prior.evidence.state in {
                ToolInvocationState.STARTED,
                ToolInvocationState.AMBIGUOUS,
            }:
                raise AmbiguousToolInvocation(
                    "tool invocation has an ambiguous external outcome and was not repeated"
                )
            if prior.evidence.state is ToolInvocationState.FAILED:
                raise ToolProviderError(prior.evidence.error or "tool provider invocation failed")
            return prior
        started_at = datetime.now(UTC)
        try:
            if request.timeout_seconds is None:
                provider_result = await self._provider.invoke(request)
            else:
                provider_result = await asyncio.wait_for(
                    self._provider.invoke(request), timeout=request.timeout_seconds
                )
            validate_tool_output(descriptor, provider_result.output)
            result = ToolInvocationResult(
                output=provider_result.output,
                evidence=ToolInvocationEvidence(
                    provider=request.provider,
                    toolName=request.tool_name,
                    schemaDigest=descriptor.schema_digest,
                    invocationId=request.invocation_id,
                    requestHash=digest,
                    policyDigest=policy.digest,
                    state=ToolInvocationState.SUCCEEDED,
                    startedAt=started_at,
                    completedAt=datetime.now(UTC),
                ),
            )
        except TimeoutError as exc:
            await self._cancel(request)
            result = self._failure(
                request,
                descriptor,
                digest,
                policy,
                started_at,
                ToolInvocationState.AMBIGUOUS,
                "tool provider invocation timed out",
                ambiguous=True,
            )
            await self._journal.complete(request, result)
            raise TimeoutError("tool provider invocation timed out") from exc
        except asyncio.CancelledError:
            await self._cancel(request)
            result = self._failure(
                request,
                descriptor,
                digest,
                policy,
                started_at,
                ToolInvocationState.AMBIGUOUS,
                "tool provider invocation was cancelled",
                ambiguous=True,
            )
            await self._journal.complete(request, result)
            raise
        except Exception as exc:
            result = self._failure(
                request,
                descriptor,
                digest,
                policy,
                started_at,
                ToolInvocationState.FAILED,
                str(exc)[:4096],
            )
            await self._journal.complete(request, result)
            raise
        await self._journal.complete(request, result)
        return result

    async def _cancel(self, request: ToolInvocationRequest) -> None:
        try:
            await self._provider.cancel(str(request.invocation_id))
        except Exception:
            # Cancellation is best effort; the journal remains the source of truth.
            return

    @staticmethod
    def _failure(
        request: ToolInvocationRequest,
        descriptor: ToolDescriptor,
        digest: str,
        policy: ToolPolicy,
        started_at: datetime,
        state: ToolInvocationState,
        error: str,
        *,
        ambiguous: bool = False,
    ) -> ToolInvocationResult:
        return ToolInvocationResult(
            output={},
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest=descriptor.schema_digest,
                invocationId=request.invocation_id,
                requestHash=digest,
                policyDigest=policy.digest,
                state=state,
                startedAt=started_at,
                completedAt=datetime.now(UTC),
                ambiguousExternalOutcome=ambiguous,
                error=error,
            ),
        )


class ExampleToolProvider:
    """Neutral echo provider used by certification and plugin-author examples."""

    def __init__(self, identity: ToolProviderRef) -> None:
        self._identity = identity

    @property
    def identity(self) -> ToolProviderRef:
        return self._identity

    async def discover(self) -> ToolDiscovery:
        return ToolDiscovery.from_tools(
            self._identity,
            (
                ToolDescriptor(
                    provider=self._identity,
                    name="example.echo",
                    description="Return the supplied value without side effects.",
                    inputSchema={
                        "type": "object",
                        "properties": {"value": {}},
                        "required": ["value"],
                        "additionalProperties": False,
                    },
                    outputSchema={"type": "object", "required": ["value"]},
                    impact=ToolImpact.READ_ONLY,
                ),
            ),
        )

    async def invoke(self, request: ToolInvocationRequest) -> ToolInvocationResult:
        return ToolInvocationResult(
            output={"value": request.arguments["value"]},
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest="sha256:" + "0" * 64,
                invocationId=request.invocation_id,
                requestHash="0" * 64,
                policyDigest="sha256:" + "0" * 64,
                state=ToolInvocationState.SUCCEEDED,
            ),
        )

    async def cancel(self, invocation_id: str) -> None:
        del invocation_id


class McpToolProvider:
    """ToolProvider adapter over the existing governed MCP client semantics."""

    def __init__(
        self,
        identity: ToolProviderRef,
        endpoint: str,
        credential: str,
        *,
        target_resolver: McpTargetResolver | None = None,
        http_policy: HttpTaskPolicy | None = None,
        pinned_tools: tuple[McpToolPin, ...] = (),
        timeout_seconds: float | None = 30,
    ) -> None:
        if identity.kind.value != "mcp":
            raise ValueError("McpToolProvider requires an mcp provider identity")
        self._identity = identity
        self._endpoint = endpoint
        self._credential = credential
        self._target_resolver = target_resolver
        self._http_policy = http_policy
        self._pinned_tools = {tool.name: tool for tool in pinned_tools}
        self._timeout_seconds = timeout_seconds

    @property
    def identity(self) -> ToolProviderRef:
        return self._identity

    async def discover(self) -> ToolDiscovery:
        result = await discover_mcp_server(
            self._endpoint,
            self._credential,
            timeout_seconds=self._timeout_seconds,
            target_resolver=self._target_resolver,
            http_policy=self._http_policy,
        )
        for tool in result.tools:
            expected = self._pinned_tools.get(tool.name)
            if expected is not None and expected.schema_digest != tool.schema_digest:
                raise RuntimeError(
                    f"MCP tool {tool.name!r} schema drifted from {expected.schema_digest} "
                    f"to {tool.schema_digest}"
                )
        return ToolDiscovery.from_tools(
            self._identity,
            tuple(
                ToolDescriptor(
                    provider=self._identity,
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.input_schema,
                    outputSchema=tool.output_schema,
                    impact=ToolImpact(self._pinned_tools.get(tool.name, tool).impact.value),
                )
                for tool in result.tools
            ),
        )

    async def invoke(self, request: ToolInvocationRequest) -> ToolInvocationResult:
        payload = await _call_tool(
            self._endpoint,
            self._credential,
            request.tool_name,
            request.arguments,
            timeout_seconds=request.timeout_seconds,
            target_resolver=self._target_resolver,
            http_policy=self._http_policy,
        )
        return ToolInvocationResult(
            output=payload,
            evidence=ToolInvocationEvidence(
                provider=request.provider,
                toolName=request.tool_name,
                schemaDigest="sha256:" + "0" * 64,
                invocationId=request.invocation_id,
                requestHash="0" * 64,
                policyDigest="sha256:" + "0" * 64,
                state=ToolInvocationState.SUCCEEDED,
            ),
        )

    async def cancel(self, invocation_id: str) -> None:
        del invocation_id
