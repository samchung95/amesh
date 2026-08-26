# ADR-062: Run verification locally through Docker

Status: accepted

Context: the product owner does not want CI/CD or release automation on GitHub Actions yet, but the
repository still needs repeatable verification independent of host Python, Node and tool versions.

Decision: remove executable files under `.github/workflows/`. Provide a developer-invoked Docker
verification image for the core Python, frontend, Pi and contract gates, plus explicit Docker-local
commands for specialist compatibility matrices. Keep packaging and publication as separate manual
operator actions; no local verification command publishes a release.

Alternatives: reusing the production image would mix development dependencies into the runtime;
one monolithic image containing every SDK, Terraform, Helm and compatibility tool would make the
common gate unnecessarily large and slow.

Consequences: verification is explicit and reproducible on a Docker-capable workstation, does not
consume hosted-runner minutes or GitHub credentials, and cannot publish by accident. Developers must
run the documented gate before review. Specialist suites remain separately selectable and their
known deferred baselines stay visible instead of being silently ignored.

Revisit: add hosted automation only after explicit product-owner authorization and a separate
decision covering credentials, protected branches and release provenance.
