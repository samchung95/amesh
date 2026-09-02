# AMESH web control room

The React/TypeScript control room is the graphical entry point for the current AMESH API. It opens on
Mission Control for running and unhealthy work, uses discoverable authorized selectors, and opens each
execution on a simple ordered trace. It also provides permission-aware navigation, flow and execution
lists, tenant/namespace context, trigger health, execution-check compliance and evidence, global resource search,
locale/time-zone controls and retryable offline states. Routes reserved for later UI epics remain
visibly labelled and inactive.

## Run it

The container build compiles and serves the UI and API on one origin:

```powershell
docker compose up --build api postgres minio
```

Open `http://localhost:8000`, then sign in with a bootstrapped local user and tenant `default`. The
server keeps the opaque browser session in an HTTP-only same-origin cookie; the browser supplies the
separate CSRF cookie on state-changing requests. API-token mode remains available for development and
operator workflows and retains its token only in session storage. Locale, time zone, context and saved
views use local storage.

For frontend development, start the API from the repository root and Vite in a second terminal:

```powershell
uv run --extra runtime python -m amesh.entrypoints.server
cd frontend
npm ci
npm run dev
```

Vite proxies `/api`, `/health` and `/ready` to `http://127.0.0.1:8000`.

## Author flows

Open **Flows**, then choose **Create flow** or **Edit YAML** on an existing flow. The workbench opens
on an interactive visual topology backed by the same YAML draft. Add a task from the installed resource
catalog, select a node to edit its schema-generated fields, drag from one handle to another to add a
dependency, or use the structure controls to reorder, group and remove it. Zoom, pan, keyboard node and
edge navigation, and the mini map remain available on large graphs. Conditions, retries, timeouts,
concurrency controls, lifecycle handlers and subflow targets are visible on their nodes.

Visual changes are staged first. The review identifies generated YAML and marks destructive or
dependency-dropping changes as lossy before **Accept change** updates the draft. Comments, key order and
unrelated extension fields are preserved. Unknown task types or properties are labelled **Code only**
and link directly to the YAML view. The same pre-save validation rejects cycles, missing references and
cross-group dependencies.

The YAML view uses the server's versioned flow and installed-plugin schemas for completion, validates
after edits, maps diagnostics to their source ranges and only enables save for a valid changed document.
`Ctrl+F` opens search; CodeMirror's standard folding and multi-selection shortcuts are available.
**Format** applies the canonical server representation.

The inspector previews expressions against user-supplied sample JSON after sensitive keys are
redacted. Existing flows can be compared with a selected revision, cloned, disabled or restored.
Import and export operate on local YAML files. Unsaved source is isolated by tenant, user and flow in
local storage; navigation warns before leaving it behind.

## Start from a blueprint

Open **Blueprints** to search and preview versioned built-in, organization and community catalog
entries. Each preview exposes its parameters, documentation, license and immutable provenance before
opening it in the real flow editor. Instantiation creates a dirty unsaved draft only; save and execute
remain separate explicit actions.

The adjacent **Playground** previews native expressions and validates YAML fragments without
persistence, runner, production credential or infrastructure access. **Setup guide** reports database,
storage, local-runner and authentication readiness and retains checklist completion only in
tenant/user-scoped browser storage. See the [first-run guide](../docs/operations/onboarding.md).

The sign-in gate lists providers routed by the entered email domain and tenant. Local and LDAP
providers accept credentials in place; OIDC and SAML providers continue through their browser
redirect. Operator configuration and rotation are covered by the
[identity federation runbook](../docs/operations/identity-federation.md).

## Debug executions

Open an execution to read its ordered task story, including state, attempt, timing, runner, outcome,
branches, iterations, approvals, retries and child executions. Active, waiting and failed steps are
visually dominant and deep-linkable. Copy actions provide the execution ID, stable URL or a redacted
support summary. Topology, Gantt, logs, data and history remain under **Advanced evidence** in the same
shareable route. The selected step/task, active view, log filters and task-page offset are URL parameters,
so reloading or sharing the link preserves the investigation context.

Task runs are fetched in pages of 100 with a server-computed state summary. Topology renders directly
up to 1,000 task runs and switches to the paged aggregate view above that threshold. The reconnectable
evidence stream retains the newest 5,000 events in browser memory; log rows are further bounded before
rendering and can be filtered by task, attempt, level, worker, time and text. The Gantt separates queue,
wait and runner time for each attempt.

Authorized operators can preview the impact of pause, resume, cancel, kill and restart before
submitting a reason. Replay and backfill use the same preview-and-confirm workflow. Data panels expose
authorized inputs, outputs, metrics, cache decisions, artifacts and errors, while history links state
changes to the recorded actor and causative event.

## Build dashboards

Open **Dashboard** to see Mission Control: current state counts, Running now and Needs attention. Its
namespace, dependent flow and state selectors persist in the URL, and every execution row opens the
simple trace at the relevant step. Expand **Analytics and saved dashboards** to switch among the
built-in instance, tenant, namespace, flow, worker and SLA views. The analytics filter bar applies time, label, namespace, flow, state, worker-group and custom-dimension
filters without changing the saved definition. Every widget exposes its freshness and complete,
partial, sampled, authorized or redacted state.

Users with dashboard-management permission can build a custom view from typed sources, measures,
aggregations, visualizations and dimensions. Save it privately or for the tenant, assign independent
viewer/editor principal IDs, share its deep link, export YAML/JSON for GitOps, or delete it. Dashboard
access never grants access to its underlying data; denied widgets stay visible as redacted placeholders.

## Search resources

Open **Search** or press `Ctrl+K` to query the server-backed tenant search projection. The workbench
supports full-text, type, namespace, state, label, field, time and sort controls with stable cursor
pagination. Results deep-link to the matching product resource and visibly report any resource types
excluded by source authorization.

Projection status shows version, indexed/source counts, progress, lag and failures. Authorized
operators can request a tenant rebuild with a recorded reason. Search degradation is displayed in the
workbench but does not stop flows, executions or the orchestration roles.

## Verification

```powershell
npm run lint
npm run test
npm run build
npx playwright install chromium
npm run test:e2e
```

The browser suite covers Mission Control triage, failed-step deep links, the simple trace, exported
desktop/tablet/mobile screenshots, constrained selectors, connection, API-backed navigation, direct/reloaded deep links, the keyboard
command menu, server-authoritative denied routes, Simplified Chinese switching, locale formatting,
retry recovery, same-origin/offline privacy, a 768 px compact tablet layout and WCAG 2.2 AA axe rules.
Trigger and check monitor fixtures cover durable occurrence and policy-evaluation evidence. The flow
editor fixture covers visual add/configure, generated and lossy review, YAML fallback, keyboard editing,
live server validation, local draft persistence, navigation warning and automated WCAG checks. Pure
model tests cover connect, disconnect, reorder, grouping, removal, comment-preserving round trips,
invalid graph rejection and a 500-task local performance budget. Execution-debugger coverage includes
deep-linked filters, task selection, Gantt timing, live log filtering, data/history panels, intervention
impact confirmation, a 100,000-event bounded-memory model and 100,000 durable task-run paging.
Dashboard coverage exercises built-ins, typed filters and bounds, all visualization projections,
custom save/delete/export, source permission redaction, deep links and automated WCAG checks.
Search coverage exercises command-menu results, typed filters, stable paging, permission redaction,
status and rebuild controls, deep links and the dedicated workbench.

## Administer a tenant

Users with administration permission can open **Administration** to browse namespace hierarchy and
inherited metadata, manage principals/roles/bindings/service-account tokens, inspect live component
health, view effective configuration provenance and manage feature flags. Retention, announcements,
maintenance mode and the execution kill switch require a server-generated impact/recovery preview,
a short-lived actor/tenant/draft-bound approval and exact confirmation. Successful and rejected
attempts appear in the adjacent audit view. Secret-typed configuration values are always rendered as
`[REDACTED]`; the server never sends their material value.

## Browser support policy

- Chrome and Edge: current and previous stable desktop versions.
- Firefox: current and previous stable desktop versions.
- Safari: current stable macOS and iPadOS versions.
- Minimum layout widths: 768 px tablet and 1280 px desktop; the 390 px drawer is maintained as a
  convenience layout but is not yet a GA-qualified mobile workflow.
- Internet Explorer and browsers without ES2022 modules, `Intl` time zones or CSS custom properties
  are unsupported.

Chromium desktop and 768 px tablet checks run automatically. Firefox, Edge, Safari and iPadOS remain
part of the pre-GA manual release matrix; this epic does not claim that future editor or large-run
debugging workflows are already qualified.

## Accessibility and privacy record

On 2026-08-22 the shell passed its keyboard/semantic audit: the skip link is the first tab stop and
moves focus to `main`; navigation, complementary, main, dialog, listbox, table, form, status and alert
semantics expose stable accessible names; compact tablet links retain names when labels are visually
hidden; `Ctrl+K`, filtering and `Enter` operate the command menu; focus rings and 44 px controls remain
visible; and execution state is represented by icon, text and color. Axe reported no critical or
serious findings for the supported dashboard workflow.

Chromium accessibility-tree assertions cover English and Simplified Chinese. NVDA/VoiceOver release
matrix acceptance remains part of the shared GA accessibility requirement owned with EPIC-405 and
EPIC-407.

No analytics SDK, update check, font CDN or other outbound request is included. Product telemetry is
off by default and the server reports the explicit `PRODUCT_TELEMETRY_ENABLED` deployment policy in
the UI session response. The browser network acceptance test observes only the application origin.
