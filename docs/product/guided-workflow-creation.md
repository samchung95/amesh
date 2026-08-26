# Guided workflow creation

## Outcome

A new author can create and run a two-step workflow without reading documentation or opening YAML.
The guide begins with the intended outcome, exposes only applicable choices and finishes at the
persisted simple execution trace.

## Supported first-run path

1. Choose scheduled task, webhook/API, data pipeline, approval flow, AI/model task or blank advanced.
2. Choose a namespace and author the workflow name and purpose.
3. Choose an installed trigger or retain the manual UI/API entry point.
4. Choose no input, optional text or an optional JSON payload.
5. Configure up to two common-path steps from the installed task/plugin catalog and select the
   upstream dependency. Applicable steps disclose runner, model and secret-binding controls.
6. Select a step output, save the immutable revision, validate policy, simulate dynamic bounds, run
   an isolated smoke test and choose **Run now**.

For **AI / model task**, the guide creates the durable `agent.session` task rather than a direct model
call. Choose one authorized immutable AGENT revision; definitions that require an input other than the
guided `request` field remain available in YAML instead of producing an invalid starter. The selector
updates the agent pin and its declared secret scopes together. **Preview resolved envelope** shows the
exact prompt, skill, model-policy and evaluation revisions, model routes, MCP connections/tools,
output schema, memory policy, permissions and hard budgets without making an external call. Context,
repair and data-handling controls edit the same canonical YAML. After saving, **Test agent node
(isolated)** creates and runs the ordinary fixture-backed flow test with zero provider, tool, secret or
production-execution effects.

The visual and YAML tabs remain available throughout. All modes edit one canonical round-trip YAML
document; guide-owned changes do not reconstruct the document, and code-only root fields are
preserved and identified.

For a PDF pipeline, upload the file under **Namespaces → PDF artifacts**, add **Extract PDF document**
from the Documents category, and select the immutable artifact rather than typing a path. The guide
writes the artifact object, exact `inputFiles` reference, output artifact and extraction limits into
canonical YAML. The execution trace renders the versioned source/parser provenance, page/chunk counts
and extracted text. Full steps are in
[Extract a PDF as a typed workflow artifact](../how-to/extract-pdf-artifact.md).

## Qualification evidence

The fixture-backed browser acceptance performs the complete path in under ten minutes without
opening YAML and checks accessibility. The live Compose acceptance repeats save, admission,
two-task/zero-unknown simulation, isolated testing with zero production executions, launch and trace
navigation. Responsive captures and the machine-readable manifest are in
[`ui-audit/screenshots/guided/`](ui-audit/screenshots/guided/).
The guided agent create-to-reopen captures are in
[`ui-audit/screenshots/guided-agent/`](ui-audit/screenshots/guided-agent/).

## Boundary

This guide does not invent credentials, bypass authorization, persist a wizard-only definition or
replace expert YAML. Complex structures continue in the visual/code editors, and production-grade
determinism qualification remains owned by board card `c101`.
