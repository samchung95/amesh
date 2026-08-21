from __future__ import annotations

import json
from pathlib import Path

from amesh.app import app
from amesh.domain.execution import ExecutionEvent, ExecutionSnapshot
from amesh.dsl.models import FlowDefinition
from amesh.dsl.registry import default_resource_registry


def load(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_checked_in_contracts_are_current() -> None:
    assert load("schemas/flow.schema.json") == FlowDefinition.model_json_schema()
    assert load("schemas/resource-catalog.json") == default_resource_registry().catalog()
    assert load("schemas/execution-event.schema.json") == ExecutionEvent.model_json_schema()
    assert load("schemas/execution-snapshot.schema.json") == ExecutionSnapshot.model_json_schema()
    assert load("docs/api/openapi.json") == app.openapi()
