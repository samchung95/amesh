# ADR-056: Persist the workflow determinism envelope at launch

- Status: Accepted
- Date: 2026-08-25
- Owners: Workflow runtime and control-room UI
- Related: EPIC-007, EPIC-100, EPIC-104, EPIC-106, EPIC-107, EPIC-201–203 and EPIC-800

## Context

AMESH already pins flow revisions and plugin resolution, persists branch decisions and loop
iterations, fences execution epochs and attempts, and resumes acknowledged work. Authors and
operators nevertheless had no single artifact that connected those controls. A simulation could
show a task plan, but a later run did not expose the exact semantic hash, plugin digest, policy pins,
logical node order and dynamic limits used at launch.

External model, HTTP, MCP and user-code results are not reproducible merely because workflow
control is deterministic. Any production claim must separate deterministic orchestration from
nondeterministic provider output.

## Decision

Generate one versioned `amesh.determinism-envelope/v1` projection from the exact persisted flow
revision. The projection includes:

- revision, semantic hash, plugin-set hash and immutable admission-policy pins;
- canonical logical node order, parent, dependency, lifecycle and branch identities;
- every loop/subflow bound, stable iteration-key pattern, configured nesting and calculated
  worst-case task-run count;
- every runnable operation whose output is not locally deterministic; and
- a canonical envelope digest.

Simulation returns this envelope and includes it in signed plan evidence. Execution launch copies
the envelope into redaction-safe `_ameshDeterminism` trigger metadata in the same transaction that
creates the execution. No mutable lookup or new persistence table is required. The control room
shows the authoring envelope before launch and the persisted envelope, epoch, version, attempts,
branches, iteration keys and subflow links on the run trace.

Structural child lists are accepted only for explicit built-in flowable contracts. The DSL rejects
deeper than 16 nested task levels. Existing typed loop, concurrency, subflow and payload limits stay
authoritative at runtime.

## Consequences

- The same pinned inputs and fixtures can be qualified for identical logical identities, order,
  branch selection, iteration keys and reducer state across restart or replay.
- Operators can compare preview and runtime using one digest without direct database access.
- External calls require exact prompt/model/tool metadata or recorded fixtures for replay. AMESH
  never claims identical provider output.
- Changing revision semantics, plugin resolution, admission-policy pins, node order or limits changes
  the envelope digest.
- This is a workflow-control determinism claim, not generic exactly-once side effects or deterministic
  external execution.

## Rejected alternatives

- Recompute the envelope when viewing a run: mutable policy or plugin state could misrepresent what
  was launched.
- Add a dedicated envelope table: the launch metadata is already immutable, tenant-scoped and
  returned by the execution API.
- Treat provider output as deterministic when model and prompt IDs match: hosted providers do not
  offer that guarantee.
