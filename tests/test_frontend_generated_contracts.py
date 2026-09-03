from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOCAL_DRAFT_OMITS = {
    "AssetDraft": "AssetRecord",
    "AgentSessionCreateDraft": "AgentSessionCreateRequest",
    "AgentSessionPolicyDraft": "AgentSessionPolicy",
}

RAW_OMIT_PATTERN = re.compile(r"(?<![\w$])Omit\s*<")


def _strip_typescript_comments(source: str) -> str:
    result = list(source)
    index = 0
    quote: str | None = None
    while index < len(source):
        character = source[index]
        if quote is not None:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if character in {"'", '"', "`"}:
            quote = character
            index += 1
            continue
        if source.startswith("//", index):
            while index < len(source) and source[index] not in "\r\n":
                result[index] = " "
                index += 1
            continue
        if source.startswith("/*", index):
            result[index] = result[index + 1] = " "
            index += 2
            while index < len(source) and not source.startswith("*/", index):
                if source[index] not in "\r\n":
                    result[index] = " "
                index += 1
            if index < len(source):
                result[index] = result[index + 1] = " "
                index += 2
            continue
        index += 1
    return "".join(result)


def _mask_typescript_strings(source: str) -> str:
    result = list(source)
    index = 0
    quote: str | None = None
    while index < len(source):
        character = source[index]
        if quote is None:
            if character in {"'", '"', "`"}:
                quote = character
                result[index] = " "
            index += 1
            continue
        if character == "\\":
            result[index] = " "
            if index + 1 < len(source):
                result[index + 1] = " "
            index += 2
            continue
        if character == quote:
            quote = None
        if character not in "\r\n":
            result[index] = " "
        index += 1
    return "".join(result)


def _has_raw_omit(source: str) -> bool:
    uncommented = _strip_typescript_comments(source)
    return RAW_OMIT_PATTERN.search(_mask_typescript_strings(uncommented)) is not None


def _exported_object_model_fields(source: str) -> dict[str, set[str]]:
    source = _strip_typescript_comments(source)
    models: dict[str, set[str]] = {}
    declaration = re.compile(
        r"^export (?:(?:interface (?P<interface>\w+)[^{]*)|"
        r"(?:type (?P<alias>\w+)\s*=\s*))\{",
        re.MULTILINE,
    )
    property_pattern = re.compile(
        r"(?:^|[;\n])\s*(?:readonly\s+)?[\'\"]?"
        r"([A-Za-z_$][\w$-]*)['\"]?\??\s*:",
    )

    for match in declaration.finditer(source):
        depth = 1
        index = match.end()
        top_level: list[str] = []
        while index < len(source) and depth:
            character = source[index]
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
            if depth == 1:
                top_level.append(character)
            elif character == "\n":
                top_level.append("\n")
            index += 1
        name = match.group("interface") or match.group("alias")
        models[name] = {field.group(1) for field in property_pattern.finditer("".join(top_level))}
    return models


def _compatibility_contracts(source: str) -> set[tuple[str, str]]:
    source = _strip_typescript_comments(source)
    return {
        (match.group("alias"), match.group("schema"))
        for match in re.finditer(
            r'AssertExact<IsExact<(?P<alias>\w+), components\["schemas"\]'
            r'\["(?P<schema>[^"]+)"\]>>',
            source,
        )
    }


def _direct_generated_aliases(source: str) -> set[tuple[str, str]]:
    source = _strip_typescript_comments(source)
    return {
        (match.group("alias"), match.group("schema"))
        for match in re.finditer(
            r'^export type (?P<alias>\w+) = components\["schemas"\]'
            r'\["(?P<schema>[^"]+)"\];',
            source,
            re.MULTILINE,
        )
    }


def _unenrolled_schema_mirrors(source: str, schemas: dict[str, object]) -> dict[str, list[str]]:
    schema_field_sets = {
        name: set(schema.get("properties", {}))
        for name, schema in schemas.items()
        if isinstance(schema, dict) and len(schema.get("properties", {})) >= 2
    }
    contracts = _compatibility_contracts(source)
    mirrors: dict[str, list[str]] = {}
    for model_name, fields in _exported_object_model_fields(source).items():
        if not fields:
            continue
        matching_schemas = sorted(
            schema_name
            for schema_name, schema_fields in schema_field_sets.items()
            if fields == schema_fields
        )
        if matching_schemas and not any(
            (model_name, schema_name) in contracts for schema_name in matching_schemas
        ):
            mirrors[model_name] = matching_schemas
    return mirrors


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


def test_frontend_compatibility_models_do_not_redeclare_generated_wire_fields() -> None:
    document = json.loads((ROOT / "docs" / "api" / "openapi.json").read_text(encoding="utf-8"))
    schemas = document["components"]["schemas"]
    source = (ROOT / "frontend" / "src" / "api" / "types.ts").read_text(encoding="utf-8")

    assert "CheckedOmit<components" not in source
    assert re.search(r'components\["schemas"\]\["[^"]+"\]\s*&\s*\{', source) is None
    assert "export type GeneratedCompatibilityContracts = [" in source

    assert _unenrolled_schema_mirrors(source, schemas) == {}

    compatibility_aliases = {
        alias for alias in _direct_generated_aliases(source) if alias[0] != alias[1]
    }
    compatibility_contracts = _compatibility_contracts(source)
    assert compatibility_aliases <= compatibility_contracts


def test_frontend_checked_omits_are_limited_to_explicit_local_drafts() -> None:
    source = (ROOT / "frontend" / "src" / "api" / "types.ts").read_text(encoding="utf-8")
    implementation_source = source.replace(
        "export type CheckedOmit<T, K extends keyof T> = Omit<T, K>", ""
    )

    assert not _has_raw_omit(implementation_source)
    checked_omits = {
        match.group("draft"): match.group("source")
        for match in re.finditer(
            r"export type (?P<draft>\w+) = CheckedOmit<(?:Partial<)?(?P<source>\w+)>?,",
            implementation_source,
        )
    }
    assert checked_omits == LOCAL_DRAFT_OMITS


def test_frontend_contract_guards_reject_bypass_mutations() -> None:
    document = json.loads((ROOT / "docs" / "api" / "openapi.json").read_text(encoding="utf-8"))
    schemas = document["components"]["schemas"]
    source = (ROOT / "frontend" / "src" / "api" / "types.ts").read_text(encoding="utf-8")
    implementation_source = source.replace(
        "export type CheckedOmit<T, K extends keyof T> = Omit<T, K>", ""
    )

    omit_mutations = (
        "export type Bypass<T> = Omit <T, never>",
        "export type Bypass<T> = Omit /* hidden */ <T, never>",
        "export type Bypass<T> = Omit // hidden\n<T, never>",
    )
    for mutation in omit_mutations:
        assert _has_raw_omit(f"{implementation_source}\n{mutation}")

    object_alias_mutation = """
export type PermissionBypass = /* hidden */ {
  resource_type: string
  action: string
  effect: 'ALLOW' | 'DENY'
}
"""
    mirrors = _unenrolled_schema_mirrors(f"{source}\n{object_alias_mutation}", schemas)
    assert "Permission" in mirrors["PermissionBypass"]

    commented_enrollment_mutation = (
        f"{source}\n{object_alias_mutation}\n"
        '// AssertExact<IsExact<PermissionBypass, components["schemas"]["Permission"]>>'
    )
    commented_mirrors = _unenrolled_schema_mirrors(commented_enrollment_mutation, schemas)
    assert "Permission" in commented_mirrors["PermissionBypass"]

    search_request_alias = 'export type SearchRequest = components["schemas"]["SearchRequest"];'
    widened_search_request = (
        'export type SearchRequest = Partial<components["schemas"]["SearchRequest"]>;'
    )
    assert ("SearchRequest", "SearchRequest") in _direct_generated_aliases(source)
    search_request_mutation = source.replace(search_request_alias, widened_search_request)
    assert ("SearchRequest", "SearchRequest") not in _direct_generated_aliases(
        search_request_mutation
    )


def test_frontend_contract_generator_is_exactly_pinned() -> None:
    package = json.loads(
        (ROOT / "tools" / "frontend-contracts" / "package.json").read_text(encoding="utf-8")
    )

    assert package["devDependencies"] == {
        "openapi-typescript": "7.13.0",
        "typescript": "5.9.3",
    }
