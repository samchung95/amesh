# Generation validation

Validated on **2026-08-16** in the artifact-generation environment after accepting Java 25 as the production-core decision.

## Results

- Python runtime: 3.13.5; project minimum remains Python 3.12.
- Unit/API/contract tests: **13 passed**.
- Measured executable-specification coverage: **81.16%**, above the configured 75% floor.
- Backlog validator: passed.
- Clean-room lexical gate: passed.
- Python `compileall`: passed.
- CLI version and sample-flow validation: passed with `PYTHONPATH=src` from an unpacked source tree.
- Generated OpenAPI and JSON Schemas: regenerated successfully.
- Planning regeneration: deterministic across **111** generated planning files.
- Contract regeneration: deterministic across **4** generated API/schema files.
- Repository JSON validation: **9** JSON files parsed successfully.
- Repository YAML validation: **9** YAML documents parsed successfully.
- Local Markdown link validation: **164** repository-relative links resolved successfully.
- Epics: **103**.
- Functional requirements: **837**.
- Non-functional requirements: **63**.
- Total requirements: **900**.
- Traceability links: **992**.
- Generated GitHub issue records: **103**.
- Stale-decision scan: passed for all former Q-006 placeholder wording.
- Fresh ZIP extraction: backlog, clean-room, compilation, **13 tests**, CLI and example-flow validation passed.
- ZIP and tar.gz checksums: verified.

## Java transition status

Java 25 is now the accepted production language, but the Java production modules have intentionally **not** been implemented in this planning snapshot. The next implementation change is the Java 25 modular-build bootstrap described in [`docs/product/implementation-kickoff.md`](product/implementation-kickoff.md).

The validation environment provides OpenJDK 21 only and does not provide Gradle or Maven. Consequently, a Java 25 toolchain or Java module build could not be executed here. This is not represented as a completed check.

## Other checks not executed locally

Ruff and mypy were not installed, so their complete checks were not run locally. Their configurations and mandatory GitHub CI steps remain checked in.

Docker and PostgreSQL client/server binaries were not installed. Consequently, `docker compose config`, container startup and execution of `migrations/0001_foundation.sql` against a live PostgreSQL instance were not performed. The Compose file was parsed structurally, and the SQL remains explicitly provisional pending CI integration tests.

There is no Git metadata in the extracted archive used for this update, so Git diff, commit, bundle, signed-tag and branch-protection checks were not run. Publication remains a separate authorized action.

These limitations are recorded to avoid overstating validation.
