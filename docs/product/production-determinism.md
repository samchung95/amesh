# Production determinism qualification

AMESH qualifies deterministic workflow control, not deterministic external output.

For one exact flow revision, plugin set, policy set and input/fixture set, the engine preserves the
same logical node identities, canonical order, branch IDs, iteration-key scheme and terminal reducer
state across supported restart and replay paths. The `amesh.determinism-envelope/v1` digest is the
operator-visible identity for that claim.

## What is pinned

| Control | Preview and runtime evidence |
|---|---|
| Flow definition | Revision and semantic hash |
| Plugins | Hash of the stored revision's exact plugin resolution |
| Admission policy | Policy key, immutable revision and digest |
| Static graph | Logical node order, parent, dependencies, lifecycle phase and branch ID |
| Loops | Kind, template tasks, iterations, duration, task runs, concurrency, inline payload and iteration-key pattern |
| Subflows | Maximum depth and pinned target revision when declared |
| Recovery | Execution epoch/version, task attempt and committed branch/skip evidence |

The authoring simulation shows configured defaults and worst-case task-run counts. The simple run
trace shows the persisted envelope plus branch, iteration, attempt, subflow and intervention evidence.

## Enforced bounds

- Task nesting: at most 16 levels.
- Loop defaults: 10,000 iterations, 3,600 seconds, 100,000 direct generated task runs and 65,536
  inline result bytes unless the flow declares tighter valid values.
- Foreach concurrency: one by default; an explicit positive `maxConcurrency` remains bounded by the
  task contract.
- Subflow depth: 16 by default, with a supported maximum of 100.
- Arbitrary runtime graph injection: rejected. Only versioned built-in flowable contracts may own
  structural child task lists.

Limit exhaustion produces existing typed configuration or resource-limit failures. It never expands
the graph silently past the declared boundary.

## Qualification matrix

| Construct | Stable evidence | Automated coverage |
|---|---|---|
| Sequential, parallel and DAG | Canonical order, dependencies, aggregation | `test_postgres_executor.py` |
| Condition and switch | Branch ID, committed decision, zero-attempt skips | `test_conditionals.py` |
| Foreach list/map/range/manifest, while and until | Iteration key, ordered aggregate, limits | `test_loops.py` |
| Subflow | Parent/child relationship, invocation key, depth, target revision | `test_subflows.py` |
| Pause, restart and stale completion | Epoch/version and attempt fences | `test_execution_control.py` |
| Backfill and replay | Source lineage, pinned revision and stable occurrence identity | `test_backfills.py` |
| Simulation/runtime envelope | Same canonical digest and bounds | `test_simulation.py`, `test_postgres_executor.py`, `shell.spec.ts` |

The focused conformance suite exercises duplicate delivery, restart, stale completion, policy
mutation and limit exhaustion at the owning runtime boundaries. Longer multi-node chaos and managed
provider qualification remain separate infrastructure qualifications.

## External-output boundary

Model calls, HTTP, MCP tools, shell processes, plugins and user code are marked nondeterministic in
the envelope. Replay must use exact prompt/model/tool metadata or a recorded fixture. Even with exact
metadata, AMESH claims reproducible orchestration and validation—not identical text or side effects
from an external provider.
