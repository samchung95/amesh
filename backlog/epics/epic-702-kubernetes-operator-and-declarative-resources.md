# EPIC-702 — Kubernetes operator and declarative resources

- **Milestone:** M7 — Compatibility, infrastructure as code and ecosystem
- **Priority:** Must
- **Domain:** `devops`
- **Primary persona:** Platform engineer
- **Parity scope:** Kestra v1.3.30 public behavior and architecture parity baseline

## Outcome

Reconcile platform resources from Kubernetes custom resources when Kubernetes is the control environment.

## In scope

- [x] **URS-F-0710** — The system shall define custom resources for flows, namespaces, files, key-values, dashboards, apps and selected governance resources.
- [x] **URS-F-0711** — The system shall reconcile desired state through server APIs with status conditions and observed generation.
- [x] **URS-F-0712** — The system shall support finalizers, deletion policy, retry, backoff and drift detection.
- [x] **URS-F-0713** — The system shall read credentials from Kubernetes Secrets without copying them into status.
- [x] **URS-F-0714** — The system shall scope watches and server credentials for multi-cluster or multi-tenant operation.
- [x] **URS-F-0715** — The system shall emit Kubernetes events and metrics for reconciliation outcomes.
- [x] **URS-F-0716** — The system shall version custom-resource schemas and provide conversion or migration guidance.
- [x] **URS-F-0717** — The system shall avoid making Kubernetes etcd authoritative for execution runtime state.

## Implementation completion evidence

- 2026-08-23 — EPIC-702 is complete for the locally reproducible Kubernetes profile. Nine generated platform.amesh.io/v1alpha1 CRDs cover flows, namespace bundles, files, key-values, dashboards, apps, roles, bindings and plugin policies with status subresources. The Python operator reconciles only through public AMESH APIs, uses observed generation and conditions, corrects drift without status-update loops, applies bounded retry/backoff, and honors Delete/Retain finalizers. Namespace/label watches and tenant targets are explicitly scoped; credentials are reread from named Secrets and never copied into status, events or response-body errors. A live kind deployment passed CRD establishment, create, stable resync, out-of-band drift correction, Kubernetes events, Prometheus metrics and both deletion policies. The opt-in Helm profile, generated-schema drift check, Docker-local validation gate, ADR, runbook and example are checked in. Evidence: [`TESTLOG.md`](../../TESTLOG.md), [`kubernetes-operator.md`](../../docs/operations/kubernetes-operator.md), [`043-kubernetes-operator-api-boundary.md`](../../docs/adr/043-kubernetes-operator-api-boundary.md), [`test_reconciler.py`](../../tests/operator/test_reconciler.py), and [`test_helm_operator.py`](../../tests/test_helm_operator.py).

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-400
- EPIC-606

## Architecture impact

- Primary bounded area: `devops`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Declarative apply, drift and CI integration tests.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- Production multi-cluster topology qualification requires operated clusters; local qualification verifies scoped watch configuration, per-tenant target selection and the one-deployment-per-cluster credential boundary.
- A conversion webhook is intentionally absent while v1alpha1 is the only served/storage version; adding a breaking CRD version requires the documented conversion or storage-migration gate.

## Traceability

- Functional requirements: URS-F-0710, URS-F-0711, URS-F-0712, URS-F-0713, URS-F-0714, URS-F-0715, URS-F-0716, URS-F-0717
- Non-functional requirements: none specifically mapped
- Source scope: Kestra v1.3.30 public behavior and architecture parity baseline
