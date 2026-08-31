# ADR-067: Separate session administration over canonical authorities

Status: accepted

Context: EPIC-826 exposes a durable application-facing session API, but administrators also need a
fleet-wide product for visibility, policy, lifecycle control and migration. Reusing generic
execution permissions and pages alone makes the product boundary unclear. Creating another session
database, queue or executor would split authority and make restart and external-effect ownership
unsafe.

Decision: retain `/api/v1/agent-sessions` and `/v1/*` as the application data plane. Add a distinct
session-administration API and workbench with session-specific permissions for own access, fleet
inspection, lifecycle control, policy and migration. Administrative reads are bounded projections
over canonical execution, session, invocation, event, evidence and artifact records; administrative
commands delegate to existing fenced execution controls.

Cross-tenant overview returns bounded aggregate metadata by default. Tenant content requires an
explicit authorized tenant context and an audited drill-down. Policies and portable bundles are
versioned and content-addressed. Bundles contain immutable resource references, schemas, evidence
and secret-binding requirements, never resolved secret values.

Transfer an individual session only when it is terminal or paused at a clean checkpoint with no
started ambiguous model or tool invocation. Import is idempotent, preserves public identity and
immutable pins, and verifies destination harness, provider, tool and artifact compatibility before
mutation. Whole-cluster moves use coordinated PostgreSQL and object-storage recovery points after an
admission drain; Kubernetes process state is not migration data.

Consequences: third-party applications retain a stable client contract while administrators gain a
cohesive product surface. Session state remains recoverable by any eligible runtime replica. Live
handoff during unresolved external I/O, secret export, active-pin replacement and a second transcript
authority remain unsupported.

Alternatives: extending generic execution administration would not expose session-specific policy or
portability; a standalone session service would duplicate orchestration truth; exporting arbitrary
active checkpoints would risk duplicate external effects.
