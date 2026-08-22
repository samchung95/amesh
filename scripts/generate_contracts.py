#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# These imports must run after the sys.path bootstrap above.
from amesh.app import app  # noqa: E402
from amesh.domain.execution import (  # noqa: E402
    ExecutionCommand,
    ExecutionEvent,
    ExecutionSnapshot,
    ExecutionTransition,
    TaskRunCommand,
    TaskRunEvent,
    TaskRunSnapshot,
    TaskRunTransition,
)
from amesh.dsl.models import FlowDefinition  # noqa: E402
from amesh.dsl.registry import default_resource_registry  # noqa: E402
from amesh.plugin_sdk import (  # noqa: E402
    PluginCatalogSnapshot,
    PluginManifest,
    PluginRegistryIndex,
    PluginRequest,
    PluginResolution,
    PluginResponse,
    PluginWireContract,
)
from amesh.ports.durable_transport import DurableEnvelope  # noqa: E402


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    dump(ROOT / "schemas" / "flow.schema.json", FlowDefinition.model_json_schema())
    dump(ROOT / "schemas" / "message-envelope.schema.json", DurableEnvelope.model_json_schema())
    dump(ROOT / "schemas" / "resource-catalog.json", default_resource_registry().catalog())
    dump(ROOT / "schemas" / "plugin-manifest.schema.json", PluginManifest.model_json_schema())
    dump(ROOT / "schemas" / "plugin-request.schema.json", PluginRequest.model_json_schema())
    dump(ROOT / "schemas" / "plugin-response.schema.json", PluginResponse.model_json_schema())
    dump(ROOT / "schemas" / "plugin-wire.schema.json", PluginWireContract.model_json_schema())
    dump(
        ROOT / "schemas" / "plugin-catalog.schema.json",
        PluginCatalogSnapshot.model_json_schema(),
    )
    dump(
        ROOT / "schemas" / "plugin-registry.schema.json",
        PluginRegistryIndex.model_json_schema(),
    )
    dump(
        ROOT / "schemas" / "plugin-resolution.schema.json",
        PluginResolution.model_json_schema(),
    )
    dump(ROOT / "schemas" / "execution-command.schema.json", ExecutionCommand.model_json_schema())
    dump(ROOT / "schemas" / "execution-event.schema.json", ExecutionEvent.model_json_schema())
    dump(ROOT / "schemas" / "execution-snapshot.schema.json", ExecutionSnapshot.model_json_schema())
    dump(
        ROOT / "schemas" / "execution-transition.schema.json",
        ExecutionTransition.model_json_schema(),
    )
    dump(ROOT / "schemas" / "task-run-command.schema.json", TaskRunCommand.model_json_schema())
    dump(ROOT / "schemas" / "task-run-event.schema.json", TaskRunEvent.model_json_schema())
    dump(ROOT / "schemas" / "task-run-snapshot.schema.json", TaskRunSnapshot.model_json_schema())
    dump(
        ROOT / "schemas" / "task-run-transition.schema.json",
        TaskRunTransition.model_json_schema(),
    )
    dump(ROOT / "docs" / "api" / "openapi.json", app.openapi())
    print("Generated schemas and OpenAPI contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
