.PHONY: help install dev format lint typecheck test validate validate-core contracts run compose-up compose-down package clean

help:
	@printf '%s\n' "install dev format lint typecheck test validate run compose-up compose-down package clean"

install:
	uv sync

dev:
	uv sync --extra runtime --extra dev

format:
	uv run --extra runtime --extra dev ruff format src tests scripts
	uv run --extra runtime --extra dev ruff check --fix src tests scripts

lint:
	uv run --extra runtime --extra dev ruff format --check src tests scripts
	uv run --extra runtime --extra dev ruff check src tests scripts

typecheck:
	uv run --extra runtime --extra dev mypy src

test:
	uv run --extra runtime --extra dev pytest --cov=amesh --cov-report=term-missing

validate: lint typecheck test
	uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
	uv run --extra runtime --extra dev python scripts/validate_backlog.py
	uv run --extra runtime --extra dev python scripts/check_clean_room.py
	uv run --extra runtime --extra dev python scripts/generate_contracts.py
	git diff --exit-code -- backlog requirements docs/product/roadmap.md schemas docs/api/openapi.json

validate-core:
	uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
	uv run --extra runtime --extra dev pytest
	uv run --extra runtime --extra dev python scripts/validate_backlog.py
	uv run --extra runtime --extra dev python scripts/check_clean_room.py
	uv run --extra runtime --extra dev python -m compileall -q src tests scripts

contracts:
	uv run --extra runtime --extra dev python scripts/generate_contracts.py

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
