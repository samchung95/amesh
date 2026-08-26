.PHONY: help install dev pi-install pi-test harness-conformance harness-image-probe format lint typecheck test validate validate-core contracts verify-local verify-local-backend verify-local-frontend verify-local-harness verify-local-contracts verify-local-compose verify-local-image verify-local-all run compose-up compose-down package clean

help:
	@printf '%s\n' "install dev format lint typecheck test harness-conformance harness-image-probe validate verify-local verify-local-all run compose-up compose-down package clean"

install:
	uv sync
	npm ci --prefix harnesses/pi

dev:
	uv sync --extra runtime --extra dev
	npm ci --prefix harnesses/pi

pi-install:
	npm ci --prefix harnesses/pi

pi-test: pi-install
	npm test --prefix harnesses/pi

harness-conformance: pi-install
	mkdir -p .artifacts
	uv run --extra runtime --extra dev python scripts/run_agent_harness_conformance.py --adapter pi --output .artifacts/harness-report.json

harness-image-probe:
	docker build -t amesh:harness-conformance .
	docker run --rm --entrypoint python amesh:harness-conformance -m amesh.harness_probe

format:
	uv run --extra runtime --extra dev ruff format src tests scripts
	uv run --extra runtime --extra dev ruff check --fix src tests scripts

lint:
	uv run --extra runtime --extra dev ruff format --check src tests scripts
	uv run --extra runtime --extra dev ruff check src tests scripts

typecheck:
	uv run --extra runtime --extra dev mypy src

test: pi-install
	uv run --extra runtime --extra dev pytest --cov=amesh --cov-report=term-missing

validate: lint typecheck test pi-test
	uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
	uv run --extra runtime --extra dev python scripts/validate_backlog.py
	uv run --extra runtime --extra dev python scripts/check_clean_room.py
	uvx --from 'reuse[charset-normalizer]==6.2.0' reuse lint
	uv run --extra runtime --extra dev python scripts/generate_contracts.py
	git diff --exit-code -- backlog requirements docs/product/roadmap.md schemas docs/api/openapi.json

validate-core: pi-test
	uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
	uv run --extra runtime --extra dev pytest
	uv run --extra runtime --extra dev python scripts/validate_backlog.py
	uv run --extra runtime --extra dev python scripts/check_clean_room.py
	uvx --from 'reuse[charset-normalizer]==6.2.0' reuse lint
	uv run --extra runtime --extra dev python -m compileall -q src tests scripts

contracts:
	uv run --extra runtime --extra dev python scripts/generate_contracts.py

verify-local:
	docker compose -f compose.verify.yaml run --rm verify all

verify-local-backend:
	docker compose -f compose.verify.yaml run --rm verify backend

verify-local-frontend:
	docker compose -f compose.verify.yaml run --rm verify frontend

verify-local-harness:
	docker compose -f compose.verify.yaml run --rm verify harness

verify-local-contracts:
	docker compose -f compose.verify.yaml run --rm verify contracts

verify-local-compose:
	docker compose config --quiet
	docker compose -f compose.compact.yaml config --quiet

verify-local-image: harness-image-probe

verify-local-all: verify-local verify-local-compose verify-local-image

run:
	uv run --extra runtime python -m amesh.server

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down --remove-orphans

package:
	bash scripts/package_repo.sh

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
