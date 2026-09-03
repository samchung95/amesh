# AMESH UI/UX visual audit

This fixture-backed Playwright audit records the primary user journeys before and after Sprint UX-01,
plus the guided-creation follow-on. It is reproducible design evidence; the separate `live/` capture
verifies the rebuilt local deployment.

Regenerate the baseline from `frontend/`:

```powershell
$env:AMESH_UI_AUDIT_PHASE='after'
npm run test:e2e -- --project=chromium --grep "exports the primary UX surfaces|exports representative non-happy"
```

The test captures deterministic data at desktop (1440×900), tablet (768×1024), and mobile (390×844).
The authenticated live-deployment pass completes the integrated acceptance for umbrella card `c103`.

## Evidence-set retention

All retained UI evidence lives under the canonical `docs/product/ui-audit/screenshots/` root. The
named Playwright tests below own the exports. Their stable filenames are checked in only when a UI
audit or feature qualification intentionally refreshes its evidence; transient troubleshooting
captures remain in Playwright's ignored `frontend/test-results/` output.

| Set | Source | Retention and export policy |
|---|---|---|
| [`before`](screenshots/before/) | `shell.spec.ts` primary and non-happy audit journeys with `AMESH_UI_AUDIT_PHASE=before` | Immutable UX-01 baseline: retain its 24 PNGs and primary/state manifests; replace only when establishing a deliberately new baseline. |
| [`after`](screenshots/after/) | The same fixture-backed journeys with `AMESH_UI_AUDIT_PHASE=after` | Accepted UX-01 comparison: retain its 25 PNGs and primary/state manifests; refresh only for an intentional audit comparison. |
| [`guided`](screenshots/guided/) | The same fixture-backed journeys with `AMESH_UI_AUDIT_PHASE=guided` | Guided-creation responsive matrix: retain its 19 PNGs and manifest as the accepted follow-on evidence. |
| [`live`](screenshots/live/) | Authenticated local-Compose capture against `http://localhost:8000` | Deployment smoke evidence: retain its two PNGs and manifest for the qualified stack; refresh only during an explicit live qualification. |
| [`agent-run`](screenshots/agent-run/) | Agent-run trace journey in `shell.spec.ts` | Feature acceptance evidence: retain the stable Chromium, tablet and mobile exports; the test and filenames are the provenance contract. |
| [`agent-sessions`](screenshots/agent-sessions/) | Session control-room journey in `agent-sessions.spec.ts` | Feature acceptance evidence: retain the Chromium and tablet exports and refresh them only with session UI qualification. |
| [`guided-agent`](screenshots/guided-agent/) | Guided agent/session authoring journey in `shell.spec.ts` | Feature acceptance evidence: retain the three responsive exports and refresh them only with guided-agent qualification. |
| [`session-orchestrator`](screenshots/session-orchestrator/) | Administrative migration workbench journey in `session-orchestrator.spec.ts` | Feature acceptance evidence: retain the Chromium and tablet exports and refresh them only with orchestrator UI qualification. |

The baseline phase sets (`before`, `after`, `guided`, and `live`) have machine-readable manifests.
They record the applicable route, viewport, state, source, timestamp, accessibility result and
discovery-budget or live-state metadata. The four feature acceptance sets use their owning test and
stable filenames as provenance.

This maintainer README and the [50-capture HTML contact sheet](index.html) are intentionally excluded
from MkDocs. The README is the repository evidence-retention contract, while the raw HTML is a local
visual-review tool whose filename would collide with MkDocs' generated directory index. Published
user and operator guidance remains in the normal MkDocs navigation; both internal artifacts remain
browsable from the repository without being copied into the documentation site.

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

The guided-creation evidence in [`screenshots/guided/`](screenshots/guided/) shows the intent-first
workflow editor at desktop, tablet and mobile widths. Its manifest records zero critical or serious
axe findings across the exported primary surfaces.

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

| Rank | Finding and screenshot evidence | User impact | Testable recommendation |
|---|---|---|---|
| P0 | [Dashboard analytics precede active work](screenshots/before/desktop-mission-control.png) | Operators must interpret charts before finding a running or failed execution. | Show Running now and Needs attention above analytics; open an active run in at most three interactions. |
| P0 | [Expert tabs split the run story](screenshots/before/desktop-execution-trace.png) | A failure cannot be explained without switching among topology, logs and data. | Default to one ordered trace with the causal step deep-linked; retain expert views under Advanced. |
| P1 | [Mobile preserves configuration ahead of answers](screenshots/before/mobile-execution-trace.png) | The current or failed step appears only after substantial scrolling and horizontally constrained tabs. | Put the simple trace before expert evidence and stack its state/timing/outcome fields at 390 px. |
| P1 | [Constrained choices look like blank text](screenshots/before/desktop-executions.png) | Users must know namespace, flow and state identifiers before filtering. | Use authorized namespace/dependent-flow selectors and finite state choices in the normal path. |
| P1 | [Creation starts at implementation detail](screenshots/before/desktop-workflow-editor.png) | First-time authors face graph and schema vocabulary before choosing a desired outcome. | Start guided creation from intent or a reviewed starter; keep the expert editor available afterward. |
| P2 | [System terms lack a plain-language layer](screenshots/before/tablet-execution-trace.png) | Epoch, evidence stream and bounded views add cognitive load during triage. | Keep immutable evidence visible but lead with human explanations and progressive disclosure. |

## Proposed product hierarchy

1. **Operate:** open on “Running now,” “Needs attention,” and recent outcomes. Analytics and saved dashboards become a secondary view.
2. **Trace:** open an execution into an ordered trigger-to-result timeline. Keep topology, Gantt, raw logs, data, and event history under an Advanced area.
3. **Create:** start from an intent or reviewed starter, guide required choices with catalog-backed selectors, validate and simulate, then run immediately into the simple trace.
4. **Govern:** preserve detailed administration and evidence surfaces, but introduce them only when the user's task requires them.

These findings were translated into consolidated overhaul card `c103`. Discoverable selectors
(`c97`), Mission Control (`c98`), the simple trace (`c99`), guided creation (`c100`) and production
determinism qualification (`c101`) are complete. The integrated desktop, tablet, mobile and live
journey matrix closes the umbrella with the expert surfaces preserved.

## Sprint result

- Active-work discovery takes two interactions, below the three-interaction and 30-second budget.
- A failed Mission Control item deep-links to its causal task and exposes the failure category without
  opening raw JSON or logs.
- The default execution view is the simple trace; topology, Gantt, logs, data, history, dashboards and
  YAML authoring remain reachable under progressive disclosure.
- All 19 populated post-sprint captures and five non-happy-state captures report zero critical or
  serious axe findings. The primary manifest records no console errors or unexpected failed API calls.
- The c103 journey matrix completes operate, failed-run diagnosis and first-workflow creation at all
  three required widths. All 26 applicable Playwright checks pass, with 30 intentional project skips.
- Launch context exposes the saved revision, environment, policy result and finite runner choice;
  policy denials provide a direct remediation action before launch.
- At the time of this screenshot capture, the rebuilt Compose deployment was ready at migration
  59/59. Both authenticated live journeys passed,
  with one running, 86 failed-recently and 113 completed-recently executions and no critical/serious
  axe findings, console errors or failed requests.
