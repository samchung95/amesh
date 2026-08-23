# SDK integration examples

These examples use the high-level clients from the generated release packages:

- `cli.py` launches a flow from a small Python command-line program.
- `web-app.ts` shows a server-side TypeScript request handler.
- `event-consumer.py` verifies a webhook before parsing it.
- `github-actions.yml` installs the Python archive and waits for an AMESH execution in CI.

Set `AMESH_ENDPOINT`, `AMESH_TOKEN` and optionally `AMESH_TENANT`. Apply
`examples/hello-world.yaml` before running the CLI or web examples. Tokens belong in the runtime
secret store, never in source control or browser-delivered JavaScript.
