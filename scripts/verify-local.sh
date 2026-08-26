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
  all)
    run_backend
    run_frontend
    run_harness
    run_contracts
    ;;
  *)
    printf '%s\n' "unknown verification suite: $suite" >&2
    printf '%s\n' "expected one of: all, backend, frontend, harness, contracts" >&2
    exit 64
    ;;
esac
