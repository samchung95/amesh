from __future__ import annotations

import base64
import binascii
import hashlib
from collections.abc import Mapping
from pathlib import PurePath
from typing import Protocol

from amesh.domain.artifacts import ArtifactRef
from amesh.domain.image_inputs import (
    MAX_IMAGE_BYTES,
    MAX_IMAGE_DIMENSION,
    MAX_IMAGE_PIXELS,
    ImageArtifactRef,
)
from amesh.dsl.models import FlowDefinition, InputDefinition
from amesh.ports.object_store import ObjectStore

IMAGE_INPUT_MAX_BYTES = MAX_IMAGE_BYTES
IMAGE_INPUT_MAX_DIMENSION = MAX_IMAGE_DIMENSION
IMAGE_INPUT_MAX_PIXELS = MAX_IMAGE_PIXELS


class ImageArtifactService(Protocol):
    """Minimal namespace-artifact authority needed by workflow image ingestion."""

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
    ) -> ImageArtifactRef: ...

    async def get_artifact(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
    ) -> ArtifactRef: ...

    async def get_image_artifact(
        self,
        namespace: str,
        path: str,
        *,
        tenant_id: str,
        actor_id: str,
        version: int | None = None,
        alt_text: str | None = None,
    ) -> ImageArtifactRef: ...


async def stage_image_input(
    flow: FlowDefinition,
    definition: InputDefinition,
    value: object,
    object_store: ObjectStore,
    *,
    tenant_id: str,
    image_artifact_service: ImageArtifactService | None,
    actor_id: str,
) -> dict[str, object]:
    del (
        object_store
    )  # Images are owned by the namespace-artifact service, not object storage directly.
    if image_artifact_service is None:
        raise ValueError(f"image input {definition.id!r} requires a namespace artifact service")

    if isinstance(value, ImageArtifactRef):
        image = value
    elif isinstance(value, Mapping) and "contentBase64" in value:
        image = await _stage_inline_image(
            flow,
            definition,
            value,
            image_artifact_service,
            tenant_id=tenant_id,
            actor_id=actor_id,
        )
    else:
        try:
            image = ImageArtifactRef.model_validate(value)
        except ValueError as exc:
            raise ValueError(
                f"image input {definition.id!r} must be a governed image reference "
                "or an inline contentBase64 value"
            ) from exc

    artifact = image.artifact
    if artifact.tenant_id != tenant_id:
        raise ValueError(f"image input {definition.id!r} belongs to another tenant")
    # Resolve metadata only. The existing immutable artifact is not copied or re-uploaded.
    canonical = await image_artifact_service.get_artifact(
        artifact.namespace,
        artifact.path,
        tenant_id=tenant_id,
        actor_id=actor_id,
        version=artifact.version,
    )
    if canonical != artifact:
        raise ValueError(f"image input {definition.id!r} artifact reference is not canonical")
    return image.model_dump(mode="json", by_alias=True)


async def _stage_inline_image(
    flow: FlowDefinition,
    definition: InputDefinition,
    value: Mapping[str, object],
    image_artifact_service: ImageArtifactService,
    *,
    tenant_id: str,
    actor_id: str,
) -> ImageArtifactRef:
    encoded = value.get("contentBase64")
    if not isinstance(encoded, str):
        raise ValueError(f"image input {definition.id!r} contentBase64 must be a string")
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"image input {definition.id!r} contentBase64 is invalid") from exc

    limit = min(definition.max_bytes or IMAGE_INPUT_MAX_BYTES, IMAGE_INPUT_MAX_BYTES)
    if len(content) > limit:
        raise ValueError(
            f"image input {definition.id!r} is {len(content)} bytes; limit is {limit} bytes"
        )
    name_value = value.get("name", definition.id)
    if not isinstance(name_value, str) or not name_value.strip():
        raise ValueError(f"image input {definition.id!r} name must be a string")
    name = PurePath(name_value).name
    if not name:
        raise ValueError(f"image input {definition.id!r} name must be a string")
    supplied_type = value.get("contentType")
    if supplied_type is not None and not isinstance(supplied_type, str):
        raise ValueError(f"image input {definition.id!r} contentType must be a string")
    alt_text = value.get("altText")
    if alt_text is not None and not isinstance(alt_text, str):
        raise ValueError(f"image input {definition.id!r} altText must be a string")

    # Content-address the workflow input so a retry can resolve the same governed artifact
    # instead of creating a new version.  The bytes remain at the artifact boundary only.
    digest = hashlib.sha256(content).hexdigest()
    path = f"workflow-inputs/{flow.id}/{digest}/{name}"
    try:
        existing = await image_artifact_service.get_image_artifact(
            flow.namespace,
            path,
            tenant_id=tenant_id,
            actor_id=actor_id,
        )
    except LookupError:
        pass
    else:
        if existing.artifact.checksum_sha256 != digest:
            raise ValueError("existing workflow image artifact checksum does not match input")
        return existing
    return await image_artifact_service.upload_image(
        flow.namespace,
        path,
        content,
        tenant_id=tenant_id,
        actor_id=actor_id,
        content_type=supplied_type,
        alt_text=alt_text,
    )


__all__ = [
    "IMAGE_INPUT_MAX_BYTES",
    "IMAGE_INPUT_MAX_DIMENSION",
    "IMAGE_INPUT_MAX_PIXELS",
    "ImageArtifactService",
    "stage_image_input",
]
