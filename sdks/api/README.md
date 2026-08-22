# AMESH API clients

These typed Python, TypeScript, Java and Go clients are generated from
`docs/api/openapi.json` with the pinned OpenAPI Generator image recorded in `manifest.json`.
Each package is versioned with AMESH 0.2.0 and declares compatibility with the 0.2 API line.

Regenerate or verify all clients from the repository root:

```console
uv run python scripts/generate_sdks.py
uv run python scripts/generate_sdks.py --check
```

Configure generated clients with `Authorization: Bearer <token>` and `X-Amesh-Tenant`. The
language-specific `pagination` helper repeatedly calls a cursor-aware page loader until
`nextCursor` is empty. Generated source should not be edited directly.
