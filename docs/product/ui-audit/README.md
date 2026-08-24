# AMESH UI/UX visual audit

This fixture-backed Playwright audit records the primary user journeys before and after Sprint UX-01.
It is reproducible design evidence; the separate `live/` capture verifies the rebuilt local deployment.

Regenerate the baseline from `frontend/`:

```powershell
$env:AMESH_UI_AUDIT_PHASE='after'
npm run test:e2e -- --project=chromium --grep "exports the primary UX surfaces|exports representative non-happy"
```

The test captures deterministic data at desktop (1440×900), tablet (768×1024), and mobile (390×844). A separate live-deployment smoke pass remains required by board card `c102`.

Each phase includes a machine-readable `manifest.json` with route, viewport, state, source, timestamp,
axe result and discovery-budget metadata. The checked-in `before/` directory is immutable baseline
evidence; the sprint's final verification writes the matching `after/` directory.

## Screenshot inventory

| Surface | Desktop | Tablet | Mobile |
|---|---|---|---|
| Mission control | [View](screenshots/before/desktop-mission-control.png) | [View](screenshots/before/tablet-mission-control.png) | [View](screenshots/before/mobile-mission-control.png) |
| Executions | [View](screenshots/before/desktop-executions.png) | [View](screenshots/before/tablet-executions.png) | [View](screenshots/before/mobile-executions.png) |
| Execution trace | [View](screenshots/before/desktop-execution-trace.png) | [View](screenshots/before/tablet-execution-trace.png) | [View](screenshots/before/mobile-execution-trace.png) |
| Flows | [View](screenshots/before/desktop-flows.png) | [View](screenshots/before/tablet-flows.png) | [View](screenshots/before/mobile-flows.png) |
| Workflow starters | [View](screenshots/before/desktop-workflow-starters.png) | [View](screenshots/before/tablet-workflow-starters.png) | [View](screenshots/before/mobile-workflow-starters.png) |
| Workflow editor | [View](screenshots/before/desktop-workflow-editor.png) | [View](screenshots/before/tablet-workflow-editor.png) | [View](screenshots/before/mobile-workflow-editor.png) |

The matching post-sprint set is in [`screenshots/after/`](screenshots/after/), including the
[desktop Mission Control](screenshots/after/desktop-mission-control.png),
[desktop simple trace](screenshots/after/desktop-execution-trace.png),
[tablet Mission Control](screenshots/after/tablet-mission-control.png), and
[mobile simple trace](screenshots/after/mobile-execution-trace.png). The desktop sign-in state is
captured in both phases.

Representative state evidence covers [empty execution history](screenshots/before/states/empty-executions.png),
[flow loading](screenshots/before/states/loading-flows.png), [flow failure](screenshots/before/states/failed-flows.png),
[permission denial](screenshots/before/states/permission-denied-administration.png), and
[workflow validation](screenshots/before/states/workflow-validation.png). All baseline primary surfaces and
state captures report zero critical or serious axe findings after the two audit-blocking ARIA defects were
corrected.

## Evidence-backed findings

### Preserve

- The graphite-and-paper identity is distinctive, consistent, and appropriate for an orchestration control room.
- State colors, typography, focus treatment, and primary navigation have a strong visual foundation.
- The product already exposes substantial operational evidence and visual/YAML authoring capability.

### Change first

1. **Mission control does not lead with the operator's question.** The dashboard opens with a view library and analytics filters. The one running execution is represented as a chart value rather than an actionable “running now” item.
2. **Execution comprehension is split across expert surfaces.** Topology, Gantt, logs, data, and history are separate tabs; the current step, trigger-to-result story, and reason for waiting or failure are not the default narrative.
3. **Creation begins at implementation detail.** “Task ID,” task type, group, graph manipulation, YAML, diagnostics, and expression preview appear before the user has chosen an outcome or starting pattern.
4. **Constrained fields look unconstrained.** Namespace, flow, state lists, identifiers, and other catalog-backed values frequently appear as blank text inputs, requiring users to know internal values in advance.
5. **Responsive layouts preserve content but not task priority.** Mobile users scroll through view libraries and configuration before operational answers; execution tabs clip horizontally; graph canvases dominate the trace and authoring journeys.
6. **System vocabulary arrives before human explanation.** Terms such as epoch, contract, evidence stream, bounded page, semantic hash, flow, and execution need plain-language labels or progressive disclosure.

## Proposed product hierarchy

1. **Operate:** open on “Running now,” “Needs attention,” and recent outcomes. Analytics and saved dashboards become a secondary view.
2. **Trace:** open an execution into an ordered trigger-to-result timeline. Keep topology, Gantt, raw logs, data, and event history under an Advanced area.
3. **Create:** start from an intent or reviewed starter, guide required choices with catalog-backed selectors, validate and simulate, then run immediately into the simple trace.
4. **Govern:** preserve detailed administration and evidence surfaces, but introduce them only when the user's task requires them.

These findings were translated into consolidated overhaul card `c103`. Sprint UX-01 completed its
first three workstreams: discoverable selectors (`c97`), Mission Control (`c98`) and the simple trace
(`c99`). Guided creation (`c100`) and production determinism qualification (`c101`) remain explicitly
separate follow-on work.

## Sprint result

- Active-work discovery takes two interactions, below the three-interaction and 30-second budget.
- A failed Mission Control item deep-links to its causal task and exposes the failure category without
  opening raw JSON or logs.
- The default execution view is the simple trace; topology, Gantt, logs, data, history, dashboards and
  YAML authoring remain reachable under progressive disclosure.
- All 19 populated post-sprint captures and five non-happy-state captures report zero critical or
  serious axe findings. The primary manifest records no console errors or unexpected failed API calls.
