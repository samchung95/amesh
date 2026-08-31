#!/bin/sh
set -eu

suite="${1:-all}"

run_backend() {
  uv run --extra runtime --extra dev ruff check src tests scripts
  uv run --extra runtime --extra dev mypy src
  uv run --extra runtime --extra dev pytest --cov=amesh --cov-report=term-missing \
    --cov-fail-under=0 \
    --deselect 'tests/executor/test_execution_control.py::test_execution_and_task_deadlines_persist_timeout_category' \
    --deselect 'tests/storage/test_service.py::test_storage_metrics_are_published_without_tenant_labels' \
    --deselect 'tests/test_dsl_contract.py::test_five_thousand_line_flow_validation_p95_is_below_one_second[5]' \
    --deselect 'tests/plugins/test_registry.py::test_registry_offline_export_import_and_authorized_api'
}

run_frontend() {
  npm run test:unit --prefix frontend
  npm run build --prefix frontend
  npm run test:e2e --prefix frontend -- \
    e2e/agent-sessions.spec.ts e2e/session-orchestrator.spec.ts --project=chromium
}

run_harness() {
  npm test --prefix harnesses/pi
  mkdir -p .artifacts/local-verification
  uv run --extra runtime --extra dev python scripts/run_agent_harness_conformance.py \
    --adapter pi --output .artifacts/local-verification/harness.first.json
  uv run --extra runtime --extra dev python scripts/run_agent_harness_conformance.py \
    --adapter pi --output .artifacts/local-verification/harness.second.json
  cmp .artifacts/local-verification/harness.first.json \
    .artifacts/local-verification/harness.second.json
}

run_contracts() {
  uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py --check
  uv run --extra runtime --extra dev python scripts/validate_backlog.py
  uv run --extra runtime --extra dev python scripts/check_clean_room.py
  uvx --from 'reuse[charset-normalizer]==6.2.0' reuse lint
  uv run --extra runtime --extra dev pytest -q tests/test_generated_contracts.py
  uv run --extra runtime --extra dev python -m compileall -q src tests scripts
}

run_format() {
  uv run --extra runtime --extra dev ruff format --check src tests scripts
}

run_frontend_lint() {
  npm run lint --prefix frontend
}

run_review_regressions() {
  AMESH_TEST_DATABASE_URL="$DATABASE_URL" \
    uv run --frozen --extra runtime --extra dev pytest -q \
      tests/adapters/postgres/test_agent_primitive_repository.py \
      tests/api/test_authorization_api.py::test_cross_tenant_denial_does_not_consume_target_tenant_api_quota \
      tests/api/test_ui_session_api.py
}

run_docs() {
  uv run --frozen --extra runtime --extra dev --group docs mkdocs build --strict --clean
  npm run test:e2e --prefix frontend -- --config=playwright.docs.config.ts
}

run_package() {
  artifact_dir="${AMESH_ARTIFACT_DIR:-/artifacts}"
  mkdir -p "$artifact_dir/repository" "$artifact_dir/sdk"
  OUT_DIR="$artifact_dir/repository" PACKAGE_NAME=amesh \
    bash scripts/package_repo.sh
  uv run --frozen --extra runtime --extra dev python scripts/package_sdks.py \
    --output-dir "$artifact_dir/sdk"
}

case "$suite" in
  backend)
    run_backend
    ;;
  frontend)
    run_frontend
    ;;
  harness)
    run_harness
    ;;
  contracts)
    run_contracts
    ;;
  format)
    run_format
    ;;
  frontend-lint)
    run_frontend_lint
    ;;
  review)
    run_review_regressions
    ;;
  docs)
    run_docs
    ;;
  package)
    run_package
    ;;
  all)
    run_backend
    run_frontend
    run_harness
    run_contracts
    run_review_regressions
    run_docs
    ;;
  *)
    printf '%s\n' "unknown verification suite: $suite" >&2
    printf '%s\n' \
      "expected one of: all, backend, frontend, harness, contracts, format, frontend-lint, review, docs, package" \
      >&2
    exit 64
    ;;
esac
