from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_frontend_wire_models_reference_generated_openapi_schemas() -> None:
    document = json.loads((ROOT / "docs" / "api" / "openapi.json").read_text(encoding="utf-8"))
    schemas = document["components"]["schemas"]
    source = (ROOT / "frontend" / "src" / "api" / "types.ts").read_text(encoding="utf-8")

    declarations = list(re.finditer(r"^export (?:interface|type) (\w+)\b", source, re.MULTILINE))
    for index, declaration in enumerate(declarations):
        name = declaration.group(1)
        if name not in schemas:
            continue
        end = declarations[index + 1].start() if index + 1 < len(declarations) else len(source)
        block = source[declaration.start() : end]
        assert declaration.group(0).startswith("export type"), name
        assert f'components["schemas"]["{name}"]' in block, name


def test_frontend_contract_generator_is_exactly_pinned() -> None:
    package = json.loads(
        (ROOT / "tools" / "frontend-contracts" / "package.json").read_text(encoding="utf-8")
    )

    assert package["devDependencies"] == {
        "openapi-typescript": "7.13.0",
        "typescript": "5.9.3",
    }
