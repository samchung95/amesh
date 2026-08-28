from __future__ import annotations

import copy
from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, Field

from .errors import PluginErrorDetail, PluginErrorPhase
from .manifest import PLUGIN_MANIFEST_VERSION, PluginEntryPoint, PluginManifest


class PluginControlType(StrEnum):
    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    CHECKBOX = "checkbox"
    SELECT = "select"
    LIST = "list"
    OBJECT = "object"


class PluginUiControl(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    property: str
    control: PluginControlType
    label: str
    description: str | None = None
    required: bool = False
    secret: bool = False
    options: tuple[Any, ...] = ()
    property_schema: dict[str, Any] = Field(default_factory=dict, alias="schema")


def validate_configuration(
    entry_point: PluginEntryPoint,
    configuration: Mapping[str, Any],
) -> tuple[PluginErrorDetail, ...]:
    validator = Draft202012Validator(entry_point.configuration_schema)
    errors = sorted(
        validator.iter_errors(dict(configuration)),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    return tuple(
        PluginErrorDetail(
            code="plugin.configuration.invalid",
            message=error.message,
            phase=PluginErrorPhase.CONFIGURATION,
            path=tuple(error.absolute_path),
            hint=_schema_hint(str(error.validator)),
            details={"validator": str(error.validator)},
        )
        for error in errors
    )


def ui_controls(entry_point: PluginEntryPoint) -> tuple[PluginUiControl, ...]:
    schema = entry_point.configuration_schema
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return ()
    required = set(schema.get("required", []))
    declared_order = entry_point.documentation.property_order
    ordered = [name for name in declared_order if name in properties]
    ordered.extend(name for name in properties if name not in ordered)
    return tuple(
        _control(name, properties[name], required=name in required)
        for name in ordered
        if isinstance(properties[name], dict)
    )


def plugin_catalog(manifest: PluginManifest) -> dict[str, Any]:
    return {
        "schemaVersion": PLUGIN_MANIFEST_VERSION,
        "plugin": {
            "name": manifest.name,
            "version": manifest.version,
            "vendor": manifest.vendor,
            "license": manifest.license,
        },
        "entryPoints": [
            {
                "name": entry.name,
                "type": entry.type.value,
                "apiVersion": entry.api_version,
                "configurationSchema": copy.deepcopy(entry.configuration_schema),
                "outputSchema": copy.deepcopy(entry.output_schema),
                "documentation": entry.documentation.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_none=True,
                ),
                "uiControls": [
                    control.model_dump(mode="json", by_alias=True, exclude_none=True)
                    for control in ui_controls(entry)
                ],
            }
            for entry in manifest.entry_points
        ],
    }


def _control(
    name: str,
    schema: dict[str, Any],
    *,
    required: bool,
) -> PluginUiControl:
    control = PluginControlType.TEXT
    secret = bool(schema.get("writeOnly")) or schema.get("format") == "password"
    if secret:
        control = PluginControlType.PASSWORD
    elif "enum" in schema:
        control = PluginControlType.SELECT
    elif schema.get("type") in {"integer", "number"}:
        control = PluginControlType.NUMBER
    elif schema.get("type") == "boolean":
        control = PluginControlType.CHECKBOX
    elif schema.get("type") == "array":
        control = PluginControlType.LIST
    elif schema.get("type") == "object":
        control = PluginControlType.OBJECT
    return PluginUiControl(
        property=name,
        control=control,
        label=str(schema.get("title") or _humanize(name)),
        description=(str(schema["description"]) if "description" in schema else None),
        required=required,
        secret=secret,
        options=tuple(schema.get("enum", ())),
        schema=copy.deepcopy(schema),
    )


def _humanize(value: str) -> str:
    result: list[str] = []
    for character in value:
        if character.isupper() and result:
            result.append(" ")
        result.append(character)
    return "".join(result).replace("_", " ").capitalize()


def _schema_hint(validator: str) -> str:
    return {
        "required": "Add the required plugin configuration property.",
        "additionalProperties": "Remove the unsupported plugin configuration property.",
        "type": "Use the value type declared by the plugin schema.",
        "enum": "Use one of the values declared by the plugin schema.",
        "format": "Use the format declared by the plugin schema.",
    }.get(validator, "Update the plugin configuration to match its published JSON Schema.")
