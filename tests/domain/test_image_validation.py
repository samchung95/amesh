from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from io import BytesIO

import pytest
from PIL import Image

from amesh.domain.artifacts import (
    ArtifactProvenance,
    ArtifactRef,
    ArtifactRetention,
    build_artifact_reference,
)
from amesh.domain.image_validation import (
    ImageValidationError,
    build_image_artifact_ref,
    inspect_image_bytes,
)


def _encoded_image(format_name: str = "PNG", *, size: tuple[int, int] = (2, 3)) -> bytes:
    stream = BytesIO()
    Image.new("RGB", size, color=(12, 34, 56)).save(stream, format=format_name)
    return stream.getvalue()


def _artifact(content: bytes, media_type: str) -> ArtifactRef:
    checksum = hashlib.sha256(content).hexdigest()
    return ArtifactRef(
        reference=build_artifact_reference("images/input.png", 1, checksum),
        contentAddress=f"sha256:{checksum}",
        tenantId="tenant-a",
        namespace="reports",
        path="images/input.png",
        version=1,
        mediaType=media_type,
        sizeBytes=len(content),
        checksumSha256=checksum,
        provenance=ArtifactProvenance(
            source="namespace-file",
            originNamespace="reports",
            createdBy="operator",
            createdAt=datetime(2026, 8, 31, tzinfo=UTC),
        ),
        retention=ArtifactRetention(),
    )


@pytest.mark.parametrize(
    ("format_name", "media_type"),
    (("PNG", "image/png"), ("JPEG", "image/jpeg"), ("WEBP", "image/webp"), ("GIF", "image/gif")),
)
def test_inspection_detects_allowlisted_format_and_dimensions(
    format_name: str,
    media_type: str,
) -> None:
    content = _encoded_image(format_name)
    inspected = inspect_image_bytes(content, declared_media_type=media_type)

    assert inspected.media_type == media_type
    assert (inspected.width_pixels, inspected.height_pixels) == (2, 3)
    assert inspected.checksum_sha256 == hashlib.sha256(content).hexdigest()


def test_inspection_rejects_corrupt_mismatched_and_excessive_images() -> None:
    with pytest.raises(ImageValidationError, match="corrupt or unsupported"):
        inspect_image_bytes(b"not an image", declared_media_type="image/png")

    with pytest.raises(ImageValidationError, match="does not match"):
        inspect_image_bytes(_encoded_image("PNG"), declared_media_type="image/jpeg")

    with pytest.raises(ImageValidationError, match="pixel limit"):
        inspect_image_bytes(_encoded_image(size=(2, 3)), max_pixels=5)

    with pytest.raises(ImageValidationError, match="bytes; limit"):
        inspect_image_bytes(_encoded_image(), max_bytes=4)


def test_verified_bytes_bind_to_exact_artifact_identity() -> None:
    content = _encoded_image()
    inspection = inspect_image_bytes(content, declared_media_type="image/png")
    reference = build_image_artifact_ref(
        _artifact(content, "image/png"),
        inspection,
        filename="input.png",
        alt_text="Input chart",
    )

    assert reference.artifact.checksum_sha256 == inspection.checksum_sha256
    assert reference.display.width_pixels == 2

    with pytest.raises(ImageValidationError, match="media type"):
        build_image_artifact_ref(
            _artifact(content, "image/jpeg"),
            inspection,
        )
