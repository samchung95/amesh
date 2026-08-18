.PHONY: help install dev format lint typecheck test validate validate-core contracts run compose-up compose-down package clean

help:
	@printf '%s\n' "install dev format lint typecheck test validate run compose-up compose-down package clean"

install:
	python -m pip install -e .

dev:
	python -m pip install -e '.[dev,runtime]'

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

typecheck:
	mypy

test:
	pytest --cov=amesh --cov-report=term-missing

validate: lint typecheck test
	python scripts/regenerate_planning_artifacts.py
	python scripts/validate_backlog.py
	python scripts/check_clean_room.py
	python scripts/generate_contracts.py
	git diff --exit-code -- backlog requirements docs/product/roadmap.md schemas docs/api/openapi.json

validate-core:
	python scripts/regenerate_planning_artifacts.py
	pytest
	python scripts/validate_backlog.py
	python scripts/check_clean_room.py
	python -m compileall -q src tests scripts

contracts:
	python scripts/generate_contracts.py

run:
	uvicorn amesh.app:app --host 0.0.0.0 --port 8000 --reload

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down --remove-orphans

package:
	bash scripts/package_repo.sh

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
