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
   upstream dependency. Applicable steps disclose runner, Luna model and secret-binding controls.
6. Select a step output, save the immutable revision, validate policy, simulate dynamic bounds, run
   an isolated smoke test and choose **Run now**.

The visual and YAML tabs remain available throughout. All modes edit one canonical round-trip YAML
document; guide-owned changes do not reconstruct the document, and code-only root fields are
preserved and identified.

## Qualification evidence

The fixture-backed browser acceptance performs the complete path in under ten minutes without
opening YAML and checks accessibility. The live Compose acceptance repeats save, admission,
two-task/zero-unknown simulation, isolated testing with zero production executions, launch and trace
navigation. Responsive captures and the machine-readable manifest are in
[`ui-audit/screenshots/guided/`](ui-audit/screenshots/guided/).

## Boundary

This guide does not invent credentials, bypass authorization, persist a wizard-only definition or
replace expert YAML. Complex structures continue in the visual/code editors, and production-grade
determinism qualification remains owned by board card `c101`.
