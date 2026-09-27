#!/bin/sh
# Lightweight hosted sanity check (ADR-082). It is deliberately a subset: the complete Docker-local
# gate (scripts/verify-local.sh, run by the pre-push hook) stays the full verification.
set -eu

uv sync --frozen --extra runtime --extra dev
npm ci --prefix frontend
npm ci --prefix harnesses/pi

uv run --frozen --no-sync ruff check src tests scripts
uv run --frozen --no-sync ruff format --check src tests scripts
uv run --frozen --no-sync mypy src tests/domain tests/fixtures tests/conftest.py

# Fast, deterministic unit and contract tests. No PostgreSQL service runs, so database-backed tests
# skip; they, timing-bound and process-heavy suites stay in the local gate. The 5,000-line p95
# budget is hardware-bound.
uv run --frozen --no-sync pytest -p no:cacheprovider \
  tests/domain tests/dsl tests/expressions tests/policy tests/workflow tests/scheduler \
  tests/storage tests/api tests/application tests/tasks tests/model_providers \
  tests/sdk/test_generated_contracts.py tests/documentation tests/deployment \
  --deselect "tests/dsl/test_dsl_contract.py::test_five_thousand_line_flow_validation_p95_is_below_one_second"

npm run lint --prefix frontend
npm run test:unit --prefix frontend
npm run build --prefix frontend
