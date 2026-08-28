from __future__ import annotations

import asyncio
import base64
import hashlib
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest

from amesh.dsl import FlowDefinition
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports import ObjectMetadata
from amesh.workflow.data_contracts import (
    DataContractError,
    flow_input_contract,
    redact_sensitive_inputs,
    redact_sensitive_outputs,
    render_flow_outputs,
    stage_file_inputs,
    validate_flow_inputs,
)


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([chunk async for chunk in chunks])
        uri = f"memory://{tenant_id}/{key}"
        self.objects[uri] = content
        return ObjectMetadata(
            uri=uri,
            tenant_id=tenant_id,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            created_at=datetime.now(UTC),
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            yield self.objects[uri]

        return chunks()

    async def delete(self, tenant_id: str, uri: str) -> None:
        del self.objects[uri]


def typed_flow() -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "typed",
            "namespace": "tests.contracts",
            "inputs": [
                {"id": "text", "type": "string", "required": True},
                {"id": "count", "type": "number", "default": 2},
                {"id": "enabled", "type": "boolean", "default": True},
                {"id": "at", "type": "datetime"},
                {"id": "delay", "type": "duration"},
                {"id": "tier", "type": "enum", "values": ["free", "pro"]},
                {"id": "items", "type": "array", "itemType": "string"},
                {"id": "settings", "type": "object"},
                {"id": "attachment", "type": "file", "maxBytes": 32},
                {"id": "credential", "type": "secret", "sensitive": True},
            ],
            "variables": {"region": "apac"},
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
            "outputs": {
                "message": {"type": "string", "value": "{{ outputs.done.value }}"},
                "private": {
                    "type": "string",
                    "value": "{{ inputs.text }}",
                    "sensitive": True,
                },
            },
        }
    )


def test_one_contract_generates_schema_and_validates_all_supported_types() -> None:
    flow = typed_flow()
    schema = flow_input_contract(flow)

    assert schema["required"] == ["text"]
    assert schema["properties"]["at"]["format"] == "date-time"
    assert schema["properties"]["delay"]["format"] == "duration"
    assert schema["properties"]["tier"]["enum"] == ["free", "pro"]
    assert schema["properties"]["credential"]["writeOnly"] is True
    assert schema["x-amesh-flow"]["variables"] == {"region": "apac"}

    values = validate_flow_inputs(
        flow,
        {
            "text": "hello",
            "at": "2026-08-22T12:00:00+08:00",
            "delay": "PT5M",
            "tier": "pro",
            "items": ["one", "two"],
            "settings": {"retries": 2},
            "attachment": {"uri": "s3://amesh/object"},
            "credential": "secret://tests/token",
        },
    )
    assert values["count"] == 2
    assert values["enabled"] is True

    with pytest.raises(DataContractError, match="secret:// reference"):
        validate_flow_inputs(flow, {**values, "credential": "plaintext-canary"})
    with pytest.raises(DataContractError, match="unknown flow inputs"):
        validate_flow_inputs(flow, {**values, "unexpected": True})


def test_legacy_input_contracts_remain_compatible() -> None:
    untyped = FlowDefinition.model_validate(
        {
            "id": "untyped",
            "namespace": "tests.contracts",
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )
    integer_alias = FlowDefinition.model_validate(
        {
            "id": "integer_alias",
            "namespace": "tests.contracts",
            "inputs": [{"id": "count", "type": "INT", "required": True}],
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )

    assert flow_input_contract(untyped)["additionalProperties"] is True
    assert validate_flow_inputs(untyped, {"legacy": "value"}) == {"legacy": "value"}
    assert flow_input_contract(integer_alias)["properties"]["count"]["type"] == "integer"
    assert validate_flow_inputs(integer_alias, {"count": 3}) == {"count": 3}


def test_inline_file_is_replaced_by_internal_object_reference() -> None:
    async def scenario() -> None:
        flow = typed_flow()
        store = MemoryObjectStore()
        content = b"file-payload"
        supplied = {
            "text": "hello",
            "attachment": {
                "name": "report.txt",
                "contentType": "text/plain",
                "contentBase64": base64.b64encode(content).decode(),
            },
        }

        staged = await stage_file_inputs(flow, supplied, store, tenant_id="default")

        reference = staged["attachment"]
        assert isinstance(reference, dict)
        assert reference["uri"].startswith("memory://default/flow-inputs/")
        assert "contentBase64" not in reference
        assert store.objects[reference["uri"]] == content
        validate_flow_inputs(flow, staged)

    asyncio.run(scenario())


def test_completed_outputs_render_and_sensitive_values_are_redacted() -> None:
    flow = typed_flow()
    context = ExpressionContext(
        inputs={"text": "sensitive-text"},
        outputs={"done": {"value": "finished"}},
        variables=flow.variables,
    )

    outputs = render_flow_outputs(flow, NativeExpressionEngine(), context)

    assert outputs == {"message": "finished", "private": "sensitive-text"}
    assert redact_sensitive_inputs(
        flow,
        {"text": "sensitive-text", "credential": "secret://tests/token"},
    ) == {"text": "sensitive-text", "credential": "[REDACTED]"}
    assert redact_sensitive_outputs(flow, outputs) == {
        "message": "finished",
        "private": "[REDACTED]",
    }
