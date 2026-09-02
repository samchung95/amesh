from __future__ import annotations

import csv
import io
import json
from typing import Any
from xml.etree import ElementTree

import yaml

from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskExecutionContext, TaskHandler

_MAX_PAYLOAD_BYTES = 10 * 1024 * 1024


def core_data_handlers() -> dict[str, TaskHandler]:
    return {
        f"core.data.{format_name}": _data_handler(format_name)
        for format_name in ("json", "yaml", "csv", "xml", "text")
    }


def _data_handler(format_name: str) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, Any]:
        del context
        extra = task.configuration.handler_view().mutable_copy()
        operation = str(extra.get("operation", "parse"))
        maximum = _payload_limit(extra.get("maxPayloadBytes"))
        if format_name == "text":
            result = _text_transform(extra, operation)
        elif operation == "parse":
            source = extra.get("input")
            if not isinstance(source, str):
                raise ValueError(f"{format_name} parse requires string input")
            _require_size(source, maximum)
            result = _parse(format_name, source, extra)
        elif operation == "serialize":
            result = _serialize(format_name, extra.get("value"), extra)
        else:
            raise ValueError(f"{format_name} operation must be parse or serialize")
        _require_size(result, maximum)
        return {"format": format_name, "operation": operation, "value": result}

    return run


def _parse(format_name: str, source: str, extra: dict[str, Any]) -> Any:
    if format_name == "json":
        return json.loads(source)
    if format_name == "yaml":
        return yaml.safe_load(source)
    if format_name == "csv":
        delimiter = _delimiter(extra)
        return list(csv.DictReader(io.StringIO(source), delimiter=delimiter))
    if format_name == "xml":
        if "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
            raise ValueError("XML document type and entity declarations are not allowed")
        return _element_to_value(ElementTree.fromstring(source))
    raise ValueError(f"unsupported data format: {format_name}")


def _serialize(format_name: str, value: Any, extra: dict[str, Any]) -> str:
    if format_name == "json":
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if format_name == "yaml":
        return yaml.safe_dump(value, allow_unicode=True, sort_keys=True)
    if format_name == "csv":
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(row, dict) for row in value)
        ):
            raise ValueError("CSV serialize requires a non-empty array of objects")
        fields = list(value[0])
        if any(list(row) != fields for row in value):
            raise ValueError("CSV serialize requires identical ordered fields in every row")
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fields, delimiter=_delimiter(extra))
        writer.writeheader()
        writer.writerows(value)
        return output.getvalue()
    if format_name == "xml":
        if not isinstance(value, dict):
            raise ValueError("XML serialize requires an element object")
        return ElementTree.tostring(_value_to_element(value), encoding="unicode")
    raise ValueError(f"unsupported data format: {format_name}")


def _text_transform(extra: dict[str, Any], operation: str) -> str | list[str]:
    value = extra.get("input")
    if operation == "join":
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError("text join requires an array of strings")
        return str(extra.get("separator", "")).join(value)
    if not isinstance(value, str):
        raise ValueError(f"text {operation} requires string input")
    if operation == "trim":
        return value.strip()
    if operation == "upper":
        return value.upper()
    if operation == "lower":
        return value.lower()
    if operation == "replace":
        old = extra.get("search")
        replacement = extra.get("replacement", "")
        if not isinstance(old, str) or not isinstance(replacement, str):
            raise ValueError("text replace requires string search and replacement")
        return value.replace(old, replacement)
    if operation == "split":
        separator = extra.get("separator")
        if separator is not None and not isinstance(separator, str):
            raise ValueError("text split separator must be a string")
        return value.split(separator)
    raise ValueError("text operation must be trim, upper, lower, replace, split or join")


def _element_to_value(element: ElementTree.Element) -> dict[str, Any]:
    return {
        "tag": element.tag,
        "attributes": dict(sorted(element.attrib.items())),
        "text": element.text or "",
        "children": [_element_to_value(child) for child in element],
    }


def _value_to_element(value: dict[str, Any]) -> ElementTree.Element:
    tag = value.get("tag")
    attributes = value.get("attributes", {})
    children = value.get("children", [])
    if not isinstance(tag, str) or not tag or not isinstance(attributes, dict):
        raise ValueError("XML element requires tag and object attributes")
    if not isinstance(children, list) or not all(isinstance(child, dict) for child in children):
        raise ValueError("XML element children must be an array of objects")
    element = ElementTree.Element(tag, {str(key): str(item) for key, item in attributes.items()})
    text = value.get("text", "")
    if not isinstance(text, str):
        raise ValueError("XML element text must be a string")
    element.text = text
    element.extend(_value_to_element(child) for child in children)
    return element


def _delimiter(extra: dict[str, Any]) -> str:
    delimiter = extra.get("delimiter", ",")
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise ValueError("CSV delimiter must be one character")
    return delimiter


def _payload_limit(value: object) -> int:
    selected = min(1_048_576, _MAX_PAYLOAD_BYTES) if value is None else value
    if (
        not isinstance(selected, int)
        or isinstance(selected, bool)
        or not 0 < selected <= _MAX_PAYLOAD_BYTES
    ):
        raise ValueError(f"maxPayloadBytes must be between 1 and {_MAX_PAYLOAD_BYTES}")
    return selected


def _require_size(value: object, maximum: int) -> None:
    if isinstance(value, str):
        encoded = value.encode("utf-8")
    else:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > maximum:
        raise ValueError("data payload exceeds the configured size limit")
