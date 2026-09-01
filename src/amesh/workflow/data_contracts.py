from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from collections.abc import AsyncIterator, Mapping
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import PurePath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from pydantic import TypeAdapter

from amesh.domain.image_inputs import ImageArtifactRef
from amesh.dsl.models import FlowDefinition, InputDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine
from amesh.ports.object_store import ObjectStore
from amesh.workflow.image_inputs import ImageArtifactService, stage_image_input

INPUT_PAYLOAD_MAX_BYTES = 16 * 1024 * 1024
FILE_INPUT_MAX_BYTES = 10 * 1024 * 1024
REDACTED = "[REDACTED]"

_SUPPORTED_INPUT_TYPES = frozenset(
    {
        "string",
        "integer",
        "number",
        "boolean",
        "datetime",
        "duration",
        "enum",
        "array",
        "object",
        "file",
        "image",
        "secret",
    }
)
_INPUT_TYPE_ALIASES = {"int": "integer"}
_SECRET_REFERENCE = re.compile(r"^secret://[A-Za-z0-9][A-Za-z0-9._/-]{0,1023}$")
_DATETIME = TypeAdapter(datetime)
_DURATION = TypeAdapter(timedelta)


class DataContractError(ValueError):
    """Raised before runnable work exists when a flow data contract is invalid."""


@dataclass(frozen=True)
class OutputContract:
    value: Any
    type: str | None = None
    description: str | None = None
    sensitive: bool = False


def normalized_input_type(value: str) -> str:
    normalized = value.strip().lower()
    return _INPUT_TYPE_ALIASES.get(normalized, normalized)


def input_json_schema(definition: InputDefinition) -> dict[str, Any]:
    input_type = normalized_input_type(definition.type)
    if input_type not in _SUPPORTED_INPUT_TYPES:
        raise DataContractError(f"input {definition.id!r} has unsupported type {definition.type!r}")
    schema = _type_schema(input_type, definition)
    schema.update(deepcopy(definition.value_schema))
    schema.update(deepcopy(definition.validation))
    schema["title"] = definition.display_name or definition.id
    if definition.description:
        schema["description"] = definition.description
    if definition.has_default:
        schema["default"] = deepcopy(definition.default)
    if definition.prefill is not None:
        schema["examples"] = [deepcopy(definition.prefill)]
    if definition.sensitive or input_type == "secret":
        schema["writeOnly"] = True
    schema["x-amesh-input"] = {
        "type": input_type,
        "sensitive": definition.sensitive or input_type == "secret",
        "placeholder": definition.placeholder,
        "prefill": deepcopy(definition.prefill),
        "maxBytes": definition.max_bytes,
    }
    return schema


def flow_input_contract(flow: FlowDefinition) -> dict[str, Any]:
    properties = {definition.id: input_json_schema(definition) for definition in flow.inputs}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (f"urn:amesh:flow-inputs:{flow.namespace}:{flow.id}:revision:{flow.revision}"),
        "title": f"{flow.namespace}.{flow.id} inputs",
        "type": "object",
        "properties": properties,
        "required": [
            definition.id
            for definition in flow.inputs
            if definition.required and not definition.has_default
        ],
        "additionalProperties": not bool(flow.inputs),
        "x-amesh-flow": {
            "namespace": flow.namespace,
            "flowId": flow.id,
            "revision": flow.revision,
            "variables": deepcopy(flow.variables),
        },
    }


def validate_flow_data_contract(flow: FlowDefinition) -> None:
    try:
        schema = flow_input_contract(flow)
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise DataContractError(f"invalid flow input schema: {exc.message}") from exc
    for definition in flow.inputs:
        if normalized_input_type(definition.type) == "enum" and not definition.values:
            raise DataContractError(f"enum input {definition.id!r} requires values")
        if definition.has_default:
            _validate_input_value(definition, definition.default)
        if definition.prefill is not None:
            _validate_input_value(definition, definition.prefill)
        if normalized_input_type(definition.type) == "secret":
            for trigger in flow.triggers:
                if definition.id not in trigger.inputs:
                    continue
                value = trigger.inputs[definition.id]
                if not _is_secret_reference_or_expression(value):
                    raise DataContractError(
                        f"trigger {trigger.id!r} secret input {definition.id!r} "
                        "requires a secret:// reference or expression"
                    )
    for output_id, value in flow.outputs.items():
        contract = output_contract(value)
        if contract.type is not None and contract.type not in _SUPPORTED_INPUT_TYPES:
            raise DataContractError(f"output {output_id!r} has unsupported type {contract.type!r}")
        if contract.type == "secret" and not _is_secret_reference_or_expression(contract.value):
            raise DataContractError(
                f"secret output {output_id!r} requires a secret:// reference or expression"
            )


def validate_flow_inputs(
    flow: FlowDefinition,
    supplied: Mapping[str, Any],
    *,
    payload_max_bytes: int = INPUT_PAYLOAD_MAX_BYTES,
) -> dict[str, Any]:
    validate_flow_data_contract(flow)
    payload_size = len(
        json.dumps(supplied, sort_keys=True, separators=(",", ":"), default=str).encode()
    )
    if payload_size > payload_max_bytes:
        raise DataContractError(
            f"flow input payload is {payload_size} bytes; limit is {payload_max_bytes} bytes"
        )
    definitions = {definition.id: definition for definition in flow.inputs}
    if not definitions:
        return dict(supplied)
    unknown = sorted(set(supplied) - set(definitions))
    if unknown:
        raise DataContractError("unknown flow inputs: " + ", ".join(unknown))
    values = dict(supplied)
    for definition in flow.inputs:
        if definition.id not in values:
            if definition.has_default:
                values[definition.id] = deepcopy(definition.default)
            elif definition.required:
                raise DataContractError(f"required flow input {definition.id!r} is missing")
            else:
                continue
        _validate_input_value(definition, values[definition.id])
    return values


async def stage_file_inputs(
    flow: FlowDefinition,
    supplied: Mapping[str, Any],
    object_store: ObjectStore,
    *,
    tenant_id: str,
    image_artifact_service: ImageArtifactService | None = None,
    actor_id: str = "system",
) -> dict[str, Any]:
    values = dict(supplied)
    for definition in flow.inputs:
        input_type = normalized_input_type(definition.type)
        if input_type == "image" and definition.id in values:
            try:
                values[definition.id] = await stage_image_input(
                    flow,
                    definition,
                    values[definition.id],
                    object_store,
                    tenant_id=tenant_id,
                    image_artifact_service=image_artifact_service,
                    actor_id=actor_id,
                )
            except ValueError as exc:
                raise DataContractError(str(exc)) from exc
            continue
        if input_type != "file" or definition.id not in values:
            continue
        value = values[definition.id]
        if not isinstance(value, Mapping) or "contentBase64" not in value:
            continue
        encoded = value.get("contentBase64")
        if not isinstance(encoded, str):
            raise DataContractError(f"file input {definition.id!r} contentBase64 must be a string")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise DataContractError(
                f"file input {definition.id!r} contentBase64 is invalid"
            ) from exc
        limit = definition.max_bytes or FILE_INPUT_MAX_BYTES
        if len(content) > limit:
            raise DataContractError(
                f"file input {definition.id!r} is {len(content)} bytes; limit is {limit} bytes"
            )
        name_value = value.get("name", definition.id)
        if not isinstance(name_value, str) or not name_value.strip():
            raise DataContractError(f"file input {definition.id!r} name must be a string")
        name = PurePath(name_value).name
        content_type = value.get("contentType")
        if content_type is not None and not isinstance(content_type, str):
            raise DataContractError(f"file input {definition.id!r} contentType must be a string")
        digest = hashlib.sha256(content).hexdigest()
        metadata = await object_store.put(
            tenant_id,
            f"flow-inputs/{flow.namespace}/{flow.id}/{digest}/{name}",
            _single_chunk(content),
            content_type=content_type,
        )
        values[definition.id] = {
            "uri": metadata.uri,
            "name": name,
            "contentType": metadata.content_type,
            "size": metadata.size,
            "checksumSha256": metadata.checksum_sha256,
        }
    return values


def output_contract(value: Any) -> OutputContract:
    if isinstance(value, Mapping) and "value" in value:
        raw_type = value.get("type")
        normalized = normalized_input_type(raw_type) if isinstance(raw_type, str) else None
        description = value.get("description")
        return OutputContract(
            value=value["value"],
            type=normalized,
            description=description if isinstance(description, str) else None,
            sensitive=bool(value.get("sensitive", False)),
        )
    return OutputContract(value=value)


def render_flow_outputs(
    flow: FlowDefinition,
    engine: ExpressionEngine,
    context: ExpressionContext,
) -> dict[str, Any]:
    rendered: dict[str, Any] = {}
    for output_id, raw in flow.outputs.items():
        contract = output_contract(raw)
        value = engine.render_value(contract.value, context)
        if contract.type is not None:
            definition = InputDefinition(id=output_id, type=contract.type, required=True)
            _validate_input_value(definition, value)
        rendered[output_id] = value
    encoded = json.dumps(rendered, separators=(",", ":"), default=str).encode()
    if len(encoded) > INPUT_PAYLOAD_MAX_BYTES:
        raise DataContractError(
            f"flow output payload is {len(encoded)} bytes; limit is {INPUT_PAYLOAD_MAX_BYTES} bytes"
        )
    return rendered


def redact_sensitive_inputs(flow: FlowDefinition, values: Mapping[str, Any]) -> dict[str, Any]:
    sensitive = {
        definition.id
        for definition in flow.inputs
        if definition.sensitive or normalized_input_type(definition.type) == "secret"
    }
    return {key: REDACTED if key in sensitive else deepcopy(value) for key, value in values.items()}


def redact_sensitive_outputs(flow: FlowDefinition, values: Mapping[str, Any]) -> dict[str, Any]:
    sensitive = {
        output_id
        for output_id, raw in flow.outputs.items()
        if output_contract(raw).sensitive or output_contract(raw).type == "secret"
    }
    return {key: REDACTED if key in sensitive else deepcopy(value) for key, value in values.items()}


def redact_matching_values(value: Any, sensitive_values: tuple[Any, ...]) -> Any:
    for sensitive in sensitive_values:
        try:
            if value == sensitive:
                return REDACTED
        except (TypeError, ValueError):
            pass
    if isinstance(value, str):
        redacted = value
        for sensitive in sensitive_values:
            if isinstance(sensitive, str) and sensitive:
                redacted = redacted.replace(sensitive, REDACTED)
        return redacted
    if isinstance(value, list):
        return [redact_matching_values(item, sensitive_values) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_matching_values(item, sensitive_values) for item in value)
    if isinstance(value, Mapping):
        return {key: redact_matching_values(item, sensitive_values) for key, item in value.items()}
    return value


def sensitive_execution_values(
    flow: FlowDefinition,
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
) -> tuple[Any, ...]:
    values = [
        inputs[definition.id]
        for definition in flow.inputs
        if (definition.sensitive or normalized_input_type(definition.type) == "secret")
        and definition.id in inputs
    ]
    values.extend(
        outputs[output_id]
        for output_id, raw in flow.outputs.items()
        if (output_contract(raw).sensitive or output_contract(raw).type == "secret")
        and output_id in outputs
    )
    return tuple(values)


def _type_schema(input_type: str, definition: InputDefinition) -> dict[str, Any]:
    if input_type == "string":
        return {"type": "string"}
    if input_type == "integer":
        return {"type": "integer"}
    if input_type == "number":
        return {"type": "number"}
    if input_type == "boolean":
        return {"type": "boolean"}
    if input_type == "datetime":
        return {"type": "string", "format": "date-time"}
    if input_type == "duration":
        return {"type": "string", "format": "duration"}
    if input_type == "enum":
        return {"enum": list(definition.values)}
    if input_type == "array":
        item_schema: dict[str, Any] = {}
        if definition.item_type is not None:
            item_schema = _type_schema(
                normalized_input_type(definition.item_type),
                InputDefinition(id=definition.id, type=definition.item_type),
            )
        return {"type": "array", "items": item_schema}
    if input_type == "object":
        return {"type": "object"}
    if input_type == "file":
        return {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "contentType": {"type": ["string", "null"]},
                "size": {"type": "integer", "minimum": 0},
                "checksumSha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "contentBase64": {"type": "string", "contentEncoding": "base64"},
            },
            "oneOf": [{"required": ["uri"]}, {"required": ["contentBase64", "name"]}],
            "additionalProperties": False,
        }
    if input_type == "image":
        inline = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "contentType": {"type": ["string", "null"]},
                "contentBase64": {"type": "string", "contentEncoding": "base64"},
                "altText": {"type": "string", "minLength": 1, "maxLength": 1024},
            },
            "required": ["contentBase64"],
            "additionalProperties": False,
        }
        return {
            "oneOf": [
                inline,
                ImageArtifactRef.model_json_schema(by_alias=True),
            ]
        }
    if input_type == "secret":
        return {"type": "string", "pattern": _SECRET_REFERENCE.pattern, "writeOnly": True}
    raise DataContractError(f"unsupported input type {input_type!r}")


def _validate_input_value(definition: InputDefinition, value: Any) -> None:
    input_type = normalized_input_type(definition.type)
    if input_type == "secret" and (
        not isinstance(value, str) or _SECRET_REFERENCE.fullmatch(value) is None
    ):
        raise DataContractError(
            f"flow input {definition.id!r} does not match 'secret': "
            "secret inputs require a secret:// reference"
        )
    try:
        if input_type == "image":
            if isinstance(value, Mapping) and "contentBase64" in value:
                Draft202012Validator(
                    input_json_schema(definition),
                    format_checker=FormatChecker(),
                ).validate(value)
            else:
                ImageArtifactRef.model_validate(value)
            return
        Draft202012Validator(
            input_json_schema(definition),
            format_checker=FormatChecker(),
        ).validate(value)
        if input_type == "datetime":
            parsed = _DATETIME.validate_python(value)
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timezone is required")
        elif input_type == "duration":
            duration = _DURATION.validate_python(value)
            if duration.total_seconds() < 0:
                raise ValueError("duration cannot be negative")
    except (ValidationError, ValueError) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise DataContractError(
            f"flow input {definition.id!r} does not match {input_type!r}: {message}"
        ) from exc


async def _single_chunk(content: bytes) -> AsyncIterator[bytes]:
    yield content


def _is_secret_reference_or_expression(value: Any) -> bool:
    return isinstance(value, str) and (
        _SECRET_REFERENCE.fullmatch(value) is not None or "{{" in value
    )
