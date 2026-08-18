#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from amesh.app import app
from amesh.domain.execution import ExecutionEvent, ExecutionSnapshot
from amesh.dsl.models import FlowDefinition



def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    dump(ROOT / "schemas" / "flow.schema.json", FlowDefinition.model_json_schema())
    dump(ROOT / "schemas" / "execution-event.schema.json", ExecutionEvent.model_json_schema())
    dump(ROOT / "schemas" / "execution-snapshot.schema.json", ExecutionSnapshot.model_json_schema())
    dump(ROOT / "docs" / "api" / "openapi.json", app.openapi())
    print("Generated schemas and OpenAPI contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
