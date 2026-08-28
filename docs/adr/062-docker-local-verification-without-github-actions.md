# ADR-062: Run verification locally through Docker

Status: accepted

Context: the product owner does not want CI/CD or release automation on GitHub Actions yet, but the
repository still needs repeatable verification independent of host Python, Node and tool versions.

Decision: remove executable files under `.github/workflows/`. Provide developer-invoked Docker
entry points, with Make and PowerShell host wrappers, for the validation and Compose checks formerly
run by the repository CI workflow and for the source/SDK archive build formerly run by the release
workflow. The archive builder writes only to a mounted local artifact directory and receives no
GitHub credential. Keep publication, signing and provenance attestation as separate manual operator
actions; no local verification or packaging command publishes a release.

The common verification image owns the locked Python, Node, frontend and Pi toolchains. Specialist
compatibility matrices that require Kubernetes, multiple PostgreSQL versions, Terraform/OpenTofu,
Helm or every generated-SDK compiler remain separately selectable qualification work instead of
being folded into the common image.

Alternatives: reusing the production image would mix development dependencies into the runtime;
one monolithic image containing every SDK, Terraform, Helm and compatibility tool would make the
common gate unnecessarily large and slow.

Consequences: verification and release-archive creation are explicit and reproducible on a
Docker-capable workstation, do not consume hosted-runner minutes or GitHub credentials, and cannot
publish by accident. Developers must run the documented aggregate gate before review. Specialist
suites and known lint/format baselines stay visible instead of being represented as passing checks.

Revisit: add hosted automation only after explicit product-owner authorization and a separate
decision covering credentials, protected branches and release provenance.
