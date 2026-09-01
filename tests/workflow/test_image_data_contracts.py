from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from amesh.domain.artifacts import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
)
from amesh.domain.image_inputs import ImageArtifactRef
from amesh.domain.image_validation import build_image_artifact_ref, inspect_image_bytes
from amesh.dsl import FlowDefinition, parse_editable_flow_document, validate_flow_document
from amesh.executor import SubflowTaskSpec
from amesh.executor.loops import LoopIterationContext, iter_foreach_items, parse_loop_spec
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports import ObjectMetadata
from amesh.workflow.data_contracts import (
    DataContractError,
    render_flow_outputs,
    stage_file_inputs,
    validate_flow_inputs,
)


class MemoryObjectStore:
    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        content = b"".join([chunk async for chunk in chunks])
        return ObjectMetadata(
            uri=f"memory://{tenant_id}/{key}",
            tenant_id=tenant_id,
            size=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
            content_type=content_type,
            created_at=datetime.now(UTC),
        )

    def get(self, tenant_id: str, uri: str) -> AsyncIterator[bytes]:
        raise AssertionError("workflow image staging must use the artifact service")

    async def delete(self, tenant_id: str, uri: str) -> None:
        raise AssertionError("workflow image staging must use the artifact service")


class ImageArtifactServiceStub:
    def __init__(self) -> None:
        self.uploads: list[bytes] = []
        self.artifacts: dict[tuple[str, str, int], ArtifactRef] = {}
        self.image_refs: dict[tuple[str, str], ImageArtifactRef] = {}

    async def upload_image(
        self,
        namespace: str,
        path: str,
        content: bytes,
        *,
        tenant_id: str,
        actor_id: str,
        content_type: str | None = None,
        expected_version: int | None = None,
        alt_text: str | None = None,
    ) -> ImageArtifactRef:
        del actor_id, expected_version
        inspection = inspect_image_bytes(content, declared_media_type=content_type)
        self.uploads.append(content)
        checksum = hashlib.sha256(content).hexdigest()
        artifact = ArtifactRef(
            reference=build_artifact_reference(path, 1, checksum),
            contentAddress=f"sha256:{checksum}",
            tenantId=tenant_id,
            namespace=namespace,
            path=path,
            version=1,
            mediaType=inspection.media_type,
            sizeBytes=len(content),
            checksumSha256=checksum,
            provenance=ArtifactProvenance(
                source="workflow-input",
                originNamespace=namespace,
                createdBy="test",
                createdAt=datetime.now(UTC),
            ),
            retention=ArtifactRetention(),
        )
        self.artifacts[(namespace, path, 1)] = artifact
        image_ref = build_image_artifact_ref(
            artifact,
            inspection,
            filename=path.rsplit("/", 1)[-1],
            alt_text=alt_text,
        )
        self.image_refs[(namespace, path)] = image_ref
        return image_ref

    async def get_image_artifact(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
        alt_text: str | None = None,
    ) -> ImageArtifactRef:
        del actor_id, version, alt_text
        image = self.image_refs[(namespace, path)]
        if image.artifact.tenant_id != tenant_id:
            raise LookupError("tenant mismatch")
        return image

    async def get_artifact(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> ArtifactRef:
        del actor_id
        artifact = self.artifacts[(namespace, path, version or 1)]
        if artifact.tenant_id != tenant_id:
            raise LookupError("tenant mismatch")
        return artifact


def _flow() -> FlowDefinition:
    return FlowDefinition.model_validate(
        {
            "id": "image-flow",
            "namespace": "tests.images",
            "inputs": [{"id": "picture", "type": "image", "required": True}],
            "tasks": [{"id": "done", "type": "core.return", "value": "ok"}],
        }
    )


def _png() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (32, 24), (10, 20, 30)).save(stream, format="PNG")
    return stream.getvalue()


def _example_flow(filename: str) -> FlowDefinition:
    path = Path("examples") / filename
    source = path.read_bytes()
    result = validate_flow_document(source)
    assert result.valid, result.issues
    return FlowDefinition.model_validate(parse_editable_flow_document(source).data)


def test_inline_image_is_verified_and_staged_as_shared_artifact_ref() -> None:
    async def scenario() -> None:
        content = _png()
        service = ImageArtifactServiceStub()
        supplied = {
            "picture": {
                "name": "chart.png",
                "contentType": "image/png",
                "contentBase64": base64.b64encode(content).decode("ascii"),
                "altText": "A chart",
            }
        }
        validate_flow_inputs(_flow(), supplied)

        staged = await stage_file_inputs(
            _flow(),
            supplied,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )

        image = staged["picture"]
        assert image["schemaVersion"] == "amesh.image-ref/v1"
        assert image["artifact"]["tenantId"] == "tenant-a"
        assert image["display"]["widthPixels"] == 32
        assert image["display"]["heightPixels"] == 24
        assert "contentBase64" not in json.dumps(image)
        assert service.uploads == [content]
        validate_flow_inputs(_flow(), staged)

    asyncio.run(scenario())


def test_existing_image_ref_is_authorized_and_not_reuploaded() -> None:
    async def scenario() -> None:
        content = _png()
        service = ImageArtifactServiceStub()
        initial = await stage_file_inputs(
            _flow(),
            {"picture": {"contentBase64": base64.b64encode(content).decode()}},
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        staged = await stage_file_inputs(
            _flow(),
            initial,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        assert staged == initial
        assert service.uploads == [content]

    asyncio.run(scenario())


def test_workflow_image_lineage_survives_intermediate_flowable_and_retry() -> None:
    async def scenario() -> None:
        flow = FlowDefinition.model_validate(
            {
                "id": "image-lineage",
                "namespace": "tests.images",
                "inputs": [{"id": "picture", "type": "image", "required": True}],
                "tasks": [
                    {
                        "id": "forward",
                        "type": "core.return",
                        "value": "{{ inputs.picture }}",
                    },
                    {
                        "id": "image-agent",
                        "type": "agent.llm",
                        "dependsOn": ["forward"],
                        "prompt": "Describe the supplied image.",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe this image."},
                                    {
                                        "type": "image_ref",
                                        "image": "{{ outputs.forward.value }}",
                                    },
                                ],
                            }
                        ],
                    },
                ],
                "outputs": {
                    "imageForAgent": {
                        "type": "image",
                        "value": "{{ outputs.forward.value }}",
                    }
                },
            }
        )
        content = _png()
        service = ImageArtifactServiceStub()
        supplied = {
            "picture": {
                "name": "chart.png",
                "contentType": "image/png",
                "contentBase64": base64.b64encode(content).decode("ascii"),
            }
        }
        first = await stage_file_inputs(
            flow,
            supplied,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        second = await stage_file_inputs(
            flow,
            supplied,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        assert first == second
        assert len(service.uploads) == 1
        image = ImageArtifactRef.model_validate(first["picture"])
        assert image.artifact.checksum_sha256 == hashlib.sha256(content).hexdigest()

        forwarded = NativeExpressionEngine().render_value(
            "{{ inputs.picture }}",
            ExpressionContext(inputs=first),
        )
        rendered = render_flow_outputs(
            flow,
            NativeExpressionEngine(),
            ExpressionContext(inputs=first, outputs={"forward": {"value": forwarded}}),
        )
        assert rendered["imageForAgent"] == forwarded
        agent_task = NativeExpressionEngine().render_task(
            flow.tasks[1],
            ExpressionContext(inputs=first, outputs={"forward": {"value": forwarded}}),
        )
        assert agent_task.model_extra["messages"][0]["content"][1]["image"] == forwarded
        encoded = json.dumps({"inputs": first, "outputs": rendered})
        assert "contentBase64" not in encoded
        assert image.artifact.checksum_sha256 in encoded

        with pytest.raises(DataContractError, match="belongs to another tenant"):
            await stage_file_inputs(
                flow,
                first,
                MemoryObjectStore(),
                tenant_id="tenant-b",
                image_artifact_service=service,
                actor_id="operator",
            )

    asyncio.run(scenario())


def test_governed_image_ref_survives_branch_loop_subflow_and_retry() -> None:
    async def scenario() -> None:
        parent = _example_flow("governed-image-routing.yaml")
        child = _example_flow("governed-image-child.yaml")
        content = _png()
        encoded_content = base64.b64encode(content).decode("ascii")
        supplied = {
            "routeImage": True,
            "picture": {
                "name": "chart.png",
                "contentType": "image/png",
                "contentBase64": encoded_content,
            },
        }
        service = ImageArtifactServiceStub()

        first_attempt = await stage_file_inputs(
            parent,
            supplied,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        retry_attempt = await stage_file_inputs(
            parent,
            supplied,
            MemoryObjectStore(),
            tenant_id="tenant-a",
            image_artifact_service=service,
            actor_id="operator",
        )
        assert retry_attempt == first_attempt
        assert service.uploads == [content]

        engine = NativeExpressionEngine()
        conditional = parent.tasks[0]
        context = ExpressionContext(inputs=first_attempt)
        assert conditional.condition is not None
        assert engine.evaluate_condition(conditional.condition, context)
        branch_task = engine.render_task(conditional.then_tasks[0], context)
        branch_value = branch_task.model_extra["value"]

        loop_task = engine.render_task(
            parent.tasks[1],
            ExpressionContext(
                inputs=first_attempt,
                outputs={"branch_image": {"value": branch_value}},
            ),
        )
        loop_items = [
            item
            async for item in iter_foreach_items(
                parse_loop_spec(loop_task),
                tenant_id="tenant-a",
                object_store=None,
            )
        ]
        assert len(loop_items) == 1
        loop_item = loop_items[0]
        loop_child = engine.render_task(
            loop_task.tasks[0],
            ExpressionContext(
                inputs=first_attempt,
                iteration=LoopIterationContext(
                    index=loop_item.index,
                    key=loop_item.key,
                    value=loop_item.value,
                    parent={},
                ).as_mapping(),
            ),
        )
        loop_value = loop_child.model_extra["value"]

        subflow_task = engine.render_task(
            parent.tasks[2],
            ExpressionContext(
                inputs=first_attempt,
                outputs={"loop_image": {"value": loop_value}},
            ),
        )
        subflow_spec = SubflowTaskSpec.model_validate(subflow_task.model_extra)
        child_inputs = validate_flow_inputs(child, subflow_spec.inputs)
        child_task = engine.render_task(
            child.tasks[0],
            ExpressionContext(inputs=child_inputs),
        )
        child_value = child_task.model_extra["value"]
        child_outputs = render_flow_outputs(
            child,
            engine,
            ExpressionContext(
                inputs=child_inputs,
                outputs={"forward_image": {"value": child_value}},
            ),
        )

        image_agent = engine.render_task(
            parent.tasks[3],
            ExpressionContext(
                inputs=first_attempt,
                outputs={"delegate_image": {"outputs": child_outputs}},
            ),
        )
        agent_value = image_agent.model_extra["messages"][0]["content"][1]["image"]

        values = [
            first_attempt["picture"],
            retry_attempt["picture"],
            branch_value,
            loop_item.value,
            loop_value,
            subflow_spec.inputs["picture"],
            child_value,
            child_outputs["imageForAgent"],
            agent_value,
        ]
        references = [ImageArtifactRef.model_validate(value) for value in values]
        expected_checksum = hashlib.sha256(content).hexdigest()
        assert {reference.artifact.tenant_id for reference in references} == {"tenant-a"}
        assert {reference.artifact.checksum_sha256 for reference in references} == {
            expected_checksum
        }
        assert {reference.artifact.reference for reference in references} == {
            references[0].artifact.reference
        }

        durable_state = json.dumps(
            {
                "inputs": first_attempt,
                "branch": branch_value,
                "loop": loop_value,
                "subflow": subflow_spec.inputs,
                "childOutputs": child_outputs,
                "agent": agent_value,
            }
        )
        assert "contentBase64" not in durable_state
        assert "data:image" not in durable_state
        assert encoded_content not in durable_state

        with pytest.raises(DataContractError, match="belongs to another tenant"):
            await stage_file_inputs(
                parent,
                first_attempt,
                MemoryObjectStore(),
                tenant_id="tenant-b",
                image_artifact_service=service,
                actor_id="operator",
            )

    asyncio.run(scenario())


def test_inline_image_requires_artifact_service_and_rejects_spoofed_content() -> None:
    async def scenario() -> None:
        encoded = base64.b64encode(b"not-an-image").decode()
        with pytest.raises(DataContractError, match="artifact service"):
            await stage_file_inputs(
                _flow(),
                {"picture": {"contentBase64": encoded}},
                MemoryObjectStore(),
                tenant_id="tenant-a",
            )

        service = ImageArtifactServiceStub()
        with pytest.raises(DataContractError, match="corrupt or unsupported"):
            await stage_file_inputs(
                _flow(),
                {"picture": {"contentBase64": encoded}},
                MemoryObjectStore(),
                tenant_id="tenant-a",
                image_artifact_service=service,
            )

    import asyncio

    asyncio.run(scenario())
