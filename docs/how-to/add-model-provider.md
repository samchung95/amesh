# Add and qualify a model provider

Register a model adapter without changing workflow semantics. AMESH negotiates the declared
capabilities before the adapter receives a request, then callers persist the returned provider pin.

## Implement the adapter

Implement the existing `amesh.ports.ModelProvider` protocol. The adapter accepts a
`ModelProviderRequest` and returns a `ModelProviderResponse`; it owns only transport translation.
Do not put provider-specific fields in durable workflow state.

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

An adapter returns opaque continuation state in `ModelProviderResponse.continuation` and receives
it on the next `ModelProviderRequest.continuation`. Both fields are `SecretStr` values excluded from
serialization and representation. The OpenAI-compatible adapter translates OpenRouter's
`reasoning_details`, `reasoning_content` or `reasoning` response field into this private boundary,
removes it from the public response payload, and restores it unchanged on the preceding assistant
message during the next call.

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
AMESH loads it through tenant RLS, authenticates its tenant/invocation/provider binding, negotiates
`opaque_continuation` before provider I/O, and rejects a different provider revision. Agent sessions
persist the same handle in their checkpoint, so a restarted executor resumes without putting hidden
rationale into the checkpoint, trace, result or log.

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

Without `OPENROUTER_API_KEY`, pytest reports an explicit skip; that is not a live-provider pass.
