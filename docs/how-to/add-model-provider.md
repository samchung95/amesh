# Add and qualify a model provider

Register a model adapter without changing workflow semantics. AMESH negotiates the declared
capabilities before the adapter receives a request, then callers persist the returned provider pin.

## Implement the adapter

Implement the existing `amesh.ports.ModelProvider` protocol. The adapter accepts a
`ModelProviderRequest` and returns a `ModelProviderResponse`; it owns only transport translation.
Do not put provider-specific fields in durable workflow state. Direct HTTP routes use
`endpoint`/`credentialRef`; isolated process engines use `engineRef` and an explicit
`engineScopes` delegation. See the [subscription model-engine API](../api/model-engines.md) for
the Codex App Server and Copilot CLI account/runtime contract.

```python
from amesh.model_providers import ModelProviderCapabilities, ModelProviderRegistry

registry = ModelProviderRegistry()
registry.register(
    "my-provider",
    "1.0.0",
    adapter,
    ModelProviderCapabilities(
        structuredOutput=True,
        tool=True,
        opaqueContinuation=True,
        timeout=True,
        cancellation=True,
        usage=True,
        cost=True,
        retry=True,
    ),
)
```

Use a new revision when capabilities or adapter behavior changes. Re-registering an existing
`provider_id`/revision with a different declaration raises `ProviderRevisionConflict`.

## Register exact-model capability profiles

The adapter declaration describes what the transport can do. Register a separate immutable
`ModelCapabilityProfile` for each exact model whose limits or request dialect must be known. AMESH
intersects the adapter declaration with that model profile during negotiation and rejects an
unsupported modality or token limit before provider I/O.

```python
from amesh.model_providers import (
    CompletionTokenParameter,
    CompletionTokenParameterOverride,
    ModelCapabilityProfile,
    ModelProviderCapabilities,
    StructuredOutputDialect,
)

registry.register_model_profile(
    "openai-compatible",
    "1.0.0",
    ModelCapabilityProfile(
        model="deepseek/deepseek-v4-flash-vision-exp",
        capabilities=ModelProviderCapabilities(
            structuredOutput=True,
            tool=True,
            streaming=True,
            opaqueContinuation=True,
            cancellation=True,
            usage=True,
            cache=True,
            cost=True,
            imageInput=True,
            contextWindowTokens=1_048_576,
            maxOutputTokens=384_000,
        ),
        structuredOutputDialect=StructuredOutputDialect.JSON_OBJECT,
        completionTokenParameter=CompletionTokenParameter.MAX_TOKENS,
    ),
)
```

Pass the exact model to `registry.negotiate(..., model=...)`. The returned pin includes the model
profile and its digest, so execution provenance records the precise capability contract that was
used.

`maxCompletionTokens` remains the provider-neutral task/session setting. The exact model profile
maps that semantic limit to the provider wire field: use `MAX_COMPLETION_TOKENS` for routes that
advertise `max_completion_tokens` and `MAX_TOKENS` for routes that advertise `max_tokens`. The
OpenRouter adapter preserves the negotiated field when it adds `require_parameters=true`; it does
not rename the limit after provider selection.

When endpoint tags for the same model use different fields, keep a model-level default and declare
immutable route overrides. AMESH resolves `providerOptions.only` or `providerOptions.order` before
building the request:

```python
ModelCapabilityProfile(
    model="openai/gpt-5.6-luna",
    capabilities=capabilities,
    completionTokenParameter=CompletionTokenParameter.MAX_COMPLETION_TOKENS,
    completionTokenParameterOverrides=(
        CompletionTokenParameterOverride(
            provider="openai",
            parameter=CompletionTokenParameter.MAX_TOKENS,
        ),
    ),
)
```

The built-in `openai/gpt-5.6-luna` profile remains the OpenRouter default and negotiates the
`json_schema` request dialect. The exact
`deepseek/deepseek-v4-flash-vision-exp` profile negotiates `json_object`: AMESH sends
`response_format={"type": "json_object"}`, adds the canonical output schema to the system
instruction, emits the completion limit as `max_tokens`, parses the returned object, and validates
it locally with Draft 2020-12 JSON Schema.
The task fails validation when the response is malformed or violates the schema; provider-specific
branches are not required in workflow execution.

## Negotiate and pin

```python
from amesh.model_providers import CapabilityRequirement, ProviderCapability

pin = registry.negotiate(
    "my-provider",
    CapabilityRequirement(
        required=frozenset({ProviderCapability.STRUCTURED_OUTPUT, ProviderCapability.COST}),
        requirePricedCost=True,
    ),
    revision="1.0.0",
)
```

Persist `pin.provider_id`, `pin.revision` and `pin.digest` with the invocation or session. A
`ProviderNegotiationError` is raised before adapter I/O when any required capability is absent.

## Normalize usage and enforce cost budgets

Call `normalize_usage` and `normalize_cost` on the provider payload. Cost is explicitly `billed`,
`unpriced` or `unavailable`. `enforce_cost_budget` fails closed for a hard budget when billed cost
is absent; it never guesses a price.

## Preserve private continuation state

An adapter returns opaque continuation state in `ModelProviderResponse.continuation`. A direct
model task can receive one prior value through `ModelProviderRequest.continuation`; a multi-turn
session receives ordered private `continuationBindings`, each tied to the exact retained assistant
message index. All continuation values are `SecretStr` data excluded from serialization and
representation. The OpenAI-compatible adapter translates OpenRouter's
`reasoning_details`, `reasoning_content` or `reasoning` response field into this private boundary,
removes it from the public response payload, and restores each retained value unchanged on its
original assistant message during the next call.

Configure authenticated encryption through secret references:

```yaml
model_continuation_key_id: current
model_continuation_encryption_key: secret://model-continuation-key
model_continuation_previous_key_id: previous
model_continuation_previous_encryption_key: secret://previous-model-continuation-key
```

The primary value must be a URL-safe Fernet key. AMESH writes with the primary key and can read the
listed previous key during rotation. PostgreSQL stores the authenticated ciphertext, token digest,
provider id and exact provider revision on the private invocation row. Public task/session evidence
contains only `invocationId`, `providerId`, `providerRevision` and `tokenDigest`.

Set `continuationFromInvocationId` to that public invocation handle on the next neutral model task.
For an ordered selected transcript, use `continuationSources` entries containing `messageIndex` and
`invocationId`. AMESH loads only those invocation records through tenant RLS, authenticates every
tenant/invocation/provider binding, negotiates `opaque_continuation` before provider I/O, and rejects
a different provider revision. Agent-session checkpoints retain safe message-index-to-handle
bindings. After harness compaction, AMESH drops omitted bindings and remaps retained source indexes
to the selected transcript before decryption. Restart therefore preserves a stable provider-visible
prefix without putting hidden rationale into the checkpoint, trace, result, log or clean transfer.

## Run the conformance tests

```bash
uv run pytest tests/model_providers -q
```

The neutral fixture suite registers an OpenAI-compatible-shaped adapter and a DeepSeek-compatible
fixture under the same contract. It covers large output, malformed structured output, tool turns,
encrypted restart-resumable continuation, usage and cost normalization, pre-I/O negotiation
rejection, timeout, retry and cancellation.

The OpenRouter smoke test is environment-gated and uses `openai/gpt-5.6-luna` by default:

```bash
OPENROUTER_API_KEY=... uv run pytest tests/llm/test_openrouter_smoke.py -q
```

To qualify both built-in exact-model profiles against OpenRouter, provide the comma-separated model
list explicitly:

```bash
OPENROUTER_API_KEY=... OPENROUTER_TEST_MODELS=openai/gpt-5.6-luna,deepseek/deepseek-v4-flash-vision-exp uv run pytest tests/llm/test_openrouter_smoke.py -q
```

Without `OPENROUTER_API_KEY`, pytest reports an explicit skip; that is not a live-provider pass.
