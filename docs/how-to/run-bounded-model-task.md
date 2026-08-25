# Run a bounded structured-model task

Use this guide to call OpenRouter through AMESH and allow downstream work only after a Luna response
passes a JSON Schema.

## Register the runtime credential

1. Set `OPENROUTER_API_KEY` in the API and recovery-executor environment, then restart those
   processes. The value stays in the runtime environment; do not put it in flow YAML.

2. Create a namespace secret binding. Replace `<token>` with an AMESH API credential authorized to
   manage the namespace.

   ```bash
   curl -sS -X PUT \
     http://localhost:8000/api/v1/namespaces/examples.agents/secret-bindings/openrouter \
     -H 'Authorization: Bearer <token>' \
     -H 'X-Amesh-Tenant: default' \
     -H 'Content-Type: application/json' \
     --data '{"provider":"env","providerReference":"OPENROUTER_API_KEY"}'
   ```

   The response contains only the environment-variable name, never the OpenRouter key.

## Apply and run the example

1. Validate and apply the checked-in example.

   ```bash
   curl -sS -X POST http://localhost:8000/api/v1/flows/validate \
     -H 'Content-Type: application/yaml' \
     --data-binary @examples/bounded-structured-model.yaml

   uv run --extra runtime python -m amesh \
     --token <token> --tenant default apply examples/bounded-structured-model.yaml
   ```

   Validation reports `valid: true` before AMESH stores the flow.

2. Start the flow.

   ```bash
   uv run --extra runtime python -m amesh \
     --token <token> --tenant default run examples.agents bounded_structured_model
   ```

3. Open the execution trace. The `classify` task output includes `structuredOutput`, `usage`,
   `costUsd`, and redacted `provenance`. The `accepted` task runs only after the Draft 2020-12 schema
   accepts the response.

If the response exceeds the declared token/cost budget or fails the schema, `classify` fails and
`accepted` never becomes runnable. AMESH labels the provider result nondeterministic even when the
model, prompt and parameters are pinned.

See the [agent primitive contract](../api/agent-primitives.md) for every task field and output.
