from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from amesh.domain.artifacts import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
)
from amesh.domain.image_inputs import (
    ImageArtifactRef,
    ImageContentPart,
    ImageDisplayMetadata,
    MultimodalMessage,
    TextContentPart,
)

CHECKSUM = "a" * 64


def _artifact(*, media_type: str = "image/png", size_bytes: int = 1024) -> ArtifactRef:
    return ArtifactRef(
        reference=build_artifact_reference("images/chart.png", 2, CHECKSUM),
        contentAddress=f"sha256:{CHECKSUM}",
        tenantId="tenant-a",
        namespace="reports",
        path="images/chart.png",
        version=2,
        mediaType=media_type,
        sizeBytes=size_bytes,
        checksumSha256=CHECKSUM,
        provenance=ArtifactProvenance(
            source="namespace-file",
            originNamespace="reports",
            createdBy="operator",
            createdAt=datetime(2026, 8, 31, tzinfo=UTC),
            lineage=("namespace-file", "reports", "images/chart.png"),
        ),
        retention=ArtifactRetention(),
    )


def _image(*, media_type: str = "image/png", size_bytes: int = 1024) -> ImageArtifactRef:
    return ImageArtifactRef(
        artifact=_artifact(media_type=media_type, size_bytes=size_bytes),
        display=ImageDisplayMetadata(
            filename="chart.png",
            altText="Quarterly chart",
            widthPixels=640,
            heightPixels=480,
        ),
    )


def test_image_reference_reuses_governed_artifact_without_bytes_or_urls() -> None:
    image = _image()
    payload = image.model_dump(mode="json", by_alias=True)
    encoded = image.model_dump_json(by_alias=True)

    assert payload["schemaVersion"] == "amesh.image-ref/v1"
    assert payload["artifact"]["tenantId"] == "tenant-a"
    assert payload["artifact"]["checksumSha256"] == CHECKSUM
    assert "contentBase64" not in encoded
    assert "data:image" not in encoded
    assert "signedUrl" not in encoded

    payload["contentBase64"] = "iVBORw0KGgo="
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ImageArtifactRef.model_validate(payload)


@pytest.mark.parametrize("media_type", ("application/pdf", "image/svg+xml", "image/bmp"))
def test_image_reference_rejects_non_portable_media_types(media_type: str) -> None:
    with pytest.raises(ValidationError, match="supported image media type"):
        _image(media_type=media_type)


def test_image_reference_enforces_decoded_dimensions_and_byte_limit() -> None:
    with pytest.raises(ValidationError, match="image byte limit"):
        _image(size_bytes=20 * 1024 * 1024 + 1)

    with pytest.raises(ValidationError, match="image pixel limit"):
        ImageArtifactRef(
            artifact=_artifact(),
            display=ImageDisplayMetadata(
                widthPixels=10_000,
                heightPixels=10_000,
            ),
        )


def test_multimodal_message_preserves_part_order_and_limits_image_consumption() -> None:
    message = MultimodalMessage(
        role="user",
        content=(
            TextContentPart(text="Compare "),
            ImageContentPart(image=_image()),
            TextContentPart(text=" with the target."),
        ),
    )

    assert [part.type for part in message.content] == ["text", "image_ref", "text"]
    assert message.image_references == (_image(),)

    with pytest.raises(ValidationError, match="only user messages"):
        MultimodalMessage(
            role="system",
            content=(ImageContentPart(image=_image()),),
        )

    with pytest.raises(ValidationError, match="at most 16 images"):
        MultimodalMessage(
            role="user",
            content=tuple(ImageContentPart(image=_image()) for _ in range(17)),
        )


def test_multimodal_contract_rejects_remote_url_and_raw_bytes_parts() -> None:
    with pytest.raises(ValidationError):
        ImageContentPart.model_validate(
            {
                "type": "image_ref",
                "image": _image().model_dump(mode="json", by_alias=True),
                "url": "https://example.test/private.png",
            }
        )

    with pytest.raises(ValidationError):
        MultimodalMessage.model_validate(
            {
                "role": "user",
                "content": [{"type": "image_url", "url": "https://example.test/x.png"}],
            }
        )
