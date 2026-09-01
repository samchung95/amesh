from __future__ import annotations

import hashlib
import warnings
from io import BytesIO

from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ConfigDict, Field

from .artifacts import ArtifactRef
from .image_inputs import (
    ALLOWED_IMAGE_MEDIA_TYPES,
    MAX_IMAGE_BYTES,
    MAX_IMAGE_DIMENSION,
    MAX_IMAGE_PIXELS,
    ImageArtifactRef,
    ImageDisplayMetadata,
)

_PILLOW_FORMATS = ("PNG", "JPEG", "WEBP", "GIF")
_MEDIA_BY_FORMAT = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


class ImageValidationError(ValueError):
    """Raised before storage or external work when image bytes are not governed input."""


class ImageInspection(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    media_type: str = Field(alias="mediaType")
    size_bytes: int = Field(alias="sizeBytes", ge=1, le=MAX_IMAGE_BYTES)
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")
    width_pixels: int = Field(alias="widthPixels", ge=1, le=MAX_IMAGE_DIMENSION)
    height_pixels: int = Field(alias="heightPixels", ge=1, le=MAX_IMAGE_DIMENSION)


def inspect_image_bytes(
    content: bytes,
    *,
    declared_media_type: str | None = None,
    max_bytes: int = MAX_IMAGE_BYTES,
    max_dimension: int = MAX_IMAGE_DIMENSION,
    max_pixels: int = MAX_IMAGE_PIXELS,
) -> ImageInspection:
    """Verify allowlisted encoded image bytes and return decoded immutable facts."""

    if not content:
        raise ImageValidationError("image content cannot be empty")
    if len(content) > min(max_bytes, MAX_IMAGE_BYTES):
        raise ImageValidationError(
            f"image is {len(content)} bytes; limit is {min(max_bytes, MAX_IMAGE_BYTES)} bytes"
        )
    normalized_declared = (
        declared_media_type.partition(";")[0].strip().lower()
        if declared_media_type is not None
        else None
    )
    if normalized_declared is not None and normalized_declared not in ALLOWED_IMAGE_MEDIA_TYPES:
        raise ImageValidationError("declared content type is not a supported image media type")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content), formats=list(_PILLOW_FORMATS)) as image:
                detected_format = image.format
                width, height = image.size
                image.verify()
    except ImageValidationError:
        raise
    except (Image.DecompressionBombWarning, UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ImageValidationError("image content is corrupt or unsupported") from exc
    detected_media_type = _MEDIA_BY_FORMAT.get(detected_format or "")
    if detected_media_type is None:
        raise ImageValidationError("image content is not an allowlisted format")
    if normalized_declared is not None and normalized_declared != detected_media_type:
        raise ImageValidationError(
            f"declared content type {normalized_declared!r} does not match {detected_media_type!r}"
        )
    if width > min(max_dimension, MAX_IMAGE_DIMENSION) or height > min(
        max_dimension, MAX_IMAGE_DIMENSION
    ):
        raise ImageValidationError("image dimension limit exceeded")
    if width * height > min(max_pixels, MAX_IMAGE_PIXELS):
        raise ImageValidationError("image pixel limit exceeded")
    return ImageInspection(
        mediaType=detected_media_type,
        sizeBytes=len(content),
        checksumSha256=hashlib.sha256(content).hexdigest(),
        widthPixels=width,
        heightPixels=height,
    )


def build_image_artifact_ref(
    artifact: ArtifactRef,
    inspection: ImageInspection,
    *,
    filename: str | None = None,
    alt_text: str | None = None,
) -> ImageArtifactRef:
    """Bind verified decoded facts to the exact immutable stored artifact."""

    if artifact.media_type != inspection.media_type:
        raise ImageValidationError("stored artifact media type does not match inspected image")
    if artifact.size_bytes != inspection.size_bytes:
        raise ImageValidationError("stored artifact size does not match inspected image")
    if artifact.checksum_sha256 != inspection.checksum_sha256:
        raise ImageValidationError("stored artifact checksum does not match inspected image")
    return ImageArtifactRef(
        artifact=artifact,
        display=ImageDisplayMetadata(
            filename=filename,
            altText=alt_text,
            widthPixels=inspection.width_pixels,
            heightPixels=inspection.height_pixels,
        ),
    )


__all__ = [
    "ImageInspection",
    "ImageValidationError",
    "build_image_artifact_ref",
    "inspect_image_bytes",
]
