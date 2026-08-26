# Public SDKs

AMESH ships generated, typed API clients for Python, TypeScript, Java and Go under `sdks/api`. Each
package includes an `ExecutionClient` facade for the common embedded-integration path:

1. Launch a flow with one stable idempotency key.
2. Read or wait for its terminal state.
3. Request cancellation using the current execution version and epoch.
4. Read or stream logs and list or download artifacts.
5. Verify signed webhook deliveries before consuming them.

All clients send `Authorization: Bearer <token>` and `X-Amesh-Tenant: <tenant>`. They normalize HTTP
and transport failures into a language-native AMESH error containing the status, stable code, request
ID and retryability. Automatic retries are bounded and apply only to reads and idempotent launches;
mutation retries remain the caller's decision.

## Compatibility and packaging

`sdks/api/manifest.json` is the authoritative version and generator manifest. API/SDK `0.2.x` is
compatible with AMESH API `>=0.2.0,<0.3.0`. Breaking API changes require a new SDK major version;
additive API changes increment the minor version and compatible fixes increment the patch version.
Tag releases produce deterministic archives and SHA-256 checksums for all four clients.

Regenerate and verify with uv:

```console
uv run python scripts/generate_sdks.py
uv run python scripts/generate_sdks.py --check
uv run python scripts/package_sdks.py --output-dir dist/sdk
```

## Concurrency and transport customization

- Python `ExecutionClient` is thread-safe and `AsyncExecutionClient` moves blocking transport calls
  off the event loop. Pass any implementation of the `Transport` protocol.
- TypeScript operations are async. Supply `fetchApi` to integrate a server runtime, proxy or test
  transport.
- Java uses immutable client configuration and `java.net.http.HttpClient`; pass a configured client
  for proxy, TLS, executor or tracing policy.
- Go methods accept `context.Context`. `NewExecutionClientWithTransport` accepts an `HTTPDoer` for a
  custom `http.Client` or compatible transport.

## Webhook verification

Use the language helper to verify `v1=HMAC-SHA256(secret, timestamp + "." + delivery_id + "." +
raw_body)` with a constant-time comparison and the default five-minute timestamp tolerance. Verify
the exact received bytes before JSON parsing and record delivery IDs to reject application-level
replay. The bounded examples in [`examples/sdk`](../../examples/sdk/README.md) cover web, CLI, CI and
event-consumer integrations.

## Release conformance

Deterministic SDK regeneration, every-language compilation and live API conformance remain explicit
local specialist gates. No archive is published automatically and AMESH currently has no hosted
release workflow; see the [local verification boundary](../how-to/run-local-verification.md).
