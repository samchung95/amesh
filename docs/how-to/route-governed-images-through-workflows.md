# Route a governed image through a workflow

This journey accepts one image, replaces its inline bytes with an immutable governed reference, and
passes that same reference through a conditional branch, a one-item loop and a synchronous subflow
before `openai/gpt-5.6-luna` receives it. AMESH does not copy the image bytes into the flow document,
execution state or event journal.

The checked-in example keeps `openai/gpt-5.6-luna` as its model, and Luna remains the OpenRouter
default. To run the same governed-image path with DeepSeek, copy the parent flow and change the
`describe_image` task's `model` to the exact profile id:

```yaml
model: deepseek/deepseek-v4-flash-vision-exp
```

Both exact-model profiles declare image input support. AMESH negotiates that declaration together
with the OpenAI-compatible adapter capabilities and rejects a missing capability or an excessive
context/output budget before provider I/O. The image still crosses the workflow as an
`amesh.image-ref/v1` governed reference; selecting DeepSeek does not place inline image bytes in
workflow state.

If a DeepSeek image task uses `agent.structured`, its model profile selects the `json_object`
dialect. AMESH sends `response_format={"type": "json_object"}`, includes the canonical schema in a
system instruction, and validates the returned object locally with Draft 2020-12 JSON Schema. Luna
instead negotiates provider-side `json_schema`; the workflow task remains provider-neutral in both
cases.

## Prerequisites

- Start the local Docker stack and configure the CLI as described in
  [first-run onboarding](../operations/onboarding.md).
- Set `OPENROUTER_API_KEY` for the API and worker. The local model setup is documented in
  [Run a bounded model task](run-bounded-model-task.md).
- Have a local PNG, JPEG, WebP or GIF available as `sample.png`.

## Validate and apply the flows

The child must be applied first because the parent pins revision 1.

```powershell
uv run amesh validate examples/governed-image-child.yaml
uv run amesh validate examples/governed-image-routing.yaml
uv run amesh apply examples/governed-image-child.yaml
uv run amesh apply examples/governed-image-routing.yaml
```

## Run the journey

Build the bounded inline ingestion payload in PowerShell and run the parent flow:

```powershell
$imageBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Resolve-Path .\sample.png)))
$runInput = @{
  routeImage = $true
  picture = @{
    name = "sample.png"
    contentType = "image/png"
    contentBase64 = $imageBase64
  }
} | ConvertTo-Json -Depth 4 -Compress

uv run amesh run examples.multimodal governed_image_routing --input $runInput
```

The run output contains the Luna description. Use the returned execution ID to inspect the task
results if needed:

```powershell
uv run amesh execution <execution-id>
uv run amesh logs <execution-id>
```

The staged `picture` value has schema `amesh.image-ref/v1`. Its tenant, artifact version and SHA-256
checksum remain identical at `branch_image`, `loop_image`, the child flow's `imageForAgent` output
and `describe_image`. Retrying the same bytes resolves the same content-addressed artifact; a tenant
mismatch is rejected before any provider call. Inline `contentBase64` exists only at ingestion.
