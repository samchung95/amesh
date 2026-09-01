from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .artifacts import ArtifactRef

ALLOWED_IMAGE_MEDIA_TYPES = frozenset(
    {
        "image/gif",
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_MESSAGE_IMAGE_BYTES = 80 * 1024 * 1024
MAX_IMAGE_DIMENSION = 16_384
MAX_IMAGE_PIXELS = 40_000_000
MAX_IMAGES_PER_MESSAGE = 16


class InputModality(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class ImageDisplayMetadata(BaseModel):
    """Safe display and decoded-image facts; never storage access material."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    filename: str | None = Field(default=None, min_length=1, max_length=255)
    alt_text: str | None = Field(default=None, alias="altText", min_length=1, max_length=1024)
    width_pixels: int = Field(alias="widthPixels", ge=1, le=MAX_IMAGE_DIMENSION)
    height_pixels: int = Field(alias="heightPixels", ge=1, le=MAX_IMAGE_DIMENSION)

    @model_validator(mode="after")
    def validate_pixels(self) -> ImageDisplayMetadata:
        if self.width_pixels * self.height_pixels > MAX_IMAGE_PIXELS:
            raise ValueError("image pixel limit exceeded")
        if self.filename is not None and any(ord(character) < 32 for character in self.filename):
            raise ValueError("image filename cannot contain control characters")
        return self


class ImageArtifactRef(BaseModel):
    """A platform-wide governed image value backed by one immutable artifact."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.image-ref/v1"] = Field(
        default="amesh.image-ref/v1",
        alias="schemaVersion",
    )
    artifact: ArtifactRef
    display: ImageDisplayMetadata

    @model_validator(mode="after")
    def validate_image_artifact(self) -> ImageArtifactRef:
        if self.artifact.media_type not in ALLOWED_IMAGE_MEDIA_TYPES:
            raise ValueError("artifact mediaType is not a supported image media type")
        if self.artifact.size_bytes < 1 or self.artifact.size_bytes > MAX_IMAGE_BYTES:
            raise ValueError("artifact exceeds the image byte limit")
        return self


class TextContentPart(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    type: Literal["text"] = "text"
    text: str = Field(min_length=1, max_length=1_000_000)


class ImageContentPart(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    type: Literal["image_ref"] = "image_ref"
    image: ImageArtifactRef


ContentPart = Annotated[
    TextContentPart | ImageContentPart,
    Field(discriminator="type"),
]


class MultimodalMessage(BaseModel):
    """Ordered portable model content; workflow values use ImageArtifactRef directly."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    role: Literal["system", "developer", "user", "assistant", "tool"]
    content: tuple[ContentPart, ...] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_images(self) -> MultimodalMessage:
        images = self.image_references
        if images and self.role != "user":
            raise ValueError("only user messages may contain portable image content")
        if len(images) > MAX_IMAGES_PER_MESSAGE:
            raise ValueError(f"a message supports at most {MAX_IMAGES_PER_MESSAGE} images")
        if sum(image.artifact.size_bytes for image in images) > MAX_MESSAGE_IMAGE_BYTES:
            raise ValueError("message image bytes exceed the aggregate limit")
        return self

    @property
    def image_references(self) -> tuple[ImageArtifactRef, ...]:
        return tuple(part.image for part in self.content if isinstance(part, ImageContentPart))


def contains_image_reference(value: object) -> bool:
    """Return whether a value contains a governed image reference.

    This deliberately recognises only the portable ``ImageArtifactRef`` shape.  Inline bytes,
    URLs, and arbitrary dictionaries are not treated as image content at this boundary.
    """

    if isinstance(value, ImageArtifactRef):
        return True
    if isinstance(value, Mapping):
        if value.get("schemaVersion", value.get("schema_version")) == "amesh.image-ref/v1":
            return True
        return any(contains_image_reference(item) for item in value.values())
    if isinstance(value, list | tuple):
        return any(contains_image_reference(item) for item in value)
    return False


__all__ = [
    "ALLOWED_IMAGE_MEDIA_TYPES",
    "MAX_IMAGES_PER_MESSAGE",
    "MAX_IMAGE_BYTES",
    "MAX_IMAGE_DIMENSION",
    "MAX_IMAGE_PIXELS",
    "MAX_MESSAGE_IMAGE_BYTES",
    "ContentPart",
    "ImageArtifactRef",
    "ImageContentPart",
    "ImageDisplayMetadata",
    "InputModality",
    "MultimodalMessage",
    "TextContentPart",
    "contains_image_reference",
]
