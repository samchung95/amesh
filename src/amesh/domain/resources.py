from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .identity import RuntimeIdentity


class ResourceLifecycle(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    TOMBSTONED = "TOMBSTONED"


class ResourceVersionConflict(RuntimeError):
    """Raised when a resource mutation uses a stale expected version."""


class InvalidLifecycleTransition(ValueError):
    """Raised when a resource lifecycle transition is not permitted."""


def canonical_json(value: Any) -> bytes:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json", by_alias=True, exclude_none=True)
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return encoded.encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def resource_etag(value: Any) -> str:
    return f'"sha256:{canonical_hash(value)}"'


class ResourceMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str = Field(default="system", min_length=1, max_length=255)
    updated_by: str = Field(default="system", min_length=1, max_length=255)
    resource_version: int = Field(default=1, ge=1)
    lifecycle: ResourceLifecycle = ResourceLifecycle.ACTIVE
    archived_at: datetime | None = None
    deleted_at: datetime | None = None

    @field_validator("labels")
    @classmethod
    def validate_labels(cls, value: dict[str, str]) -> dict[str, str]:
        for key, item in value.items():
            if not key or len(key) > 128 or len(item) > 256:
                raise ValueError("label keys must be 1-128 characters and values at most 256")
        return value

    @field_validator("annotations")
    @classmethod
    def validate_annotations(cls, value: dict[str, str]) -> dict[str, str]:
        for key, item in value.items():
            if not key or len(key) > 128 or len(item) > 4096:
                raise ValueError("annotation keys must be 1-128 characters and values at most 4096")
        return value

    @model_validator(mode="after")
    def validate_lifecycle_timestamps(self) -> ResourceMetadata:
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("resource timestamps must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        if self.lifecycle is ResourceLifecycle.ACTIVE and (
            self.archived_at is not None or self.deleted_at is not None
        ):
            raise ValueError("active resource cannot have archive or deletion timestamps")
        if self.lifecycle is ResourceLifecycle.ARCHIVED and self.archived_at is None:
            raise ValueError("archived resource requires archived_at")
        if self.lifecycle is ResourceLifecycle.ARCHIVED and self.deleted_at is not None:
            raise ValueError("archived resource cannot have deleted_at")
        if self.lifecycle is ResourceLifecycle.TOMBSTONED and self.deleted_at is None:
            raise ValueError("tombstoned resource requires deleted_at")
        return self

    @property
    def etag(self) -> str:
        return resource_etag(self)


class ManagedResource(BaseModel):
    model_config = ConfigDict(frozen=True)

    identity: RuntimeIdentity
    metadata: ResourceMetadata = Field(default_factory=ResourceMetadata)
    natural_key: dict[str, str | int]
    spec: dict[str, Any] = Field(default_factory=dict)

    @property
    def etag(self) -> str:
        return resource_etag(self)


def revise_resource_metadata(
    metadata: ResourceMetadata,
    *,
    expected_version: int,
    actor_id: str,
    labels: dict[str, str] | None = None,
    annotations: dict[str, str] | None = None,
    at: datetime | None = None,
) -> ResourceMetadata:
    if metadata.resource_version != expected_version:
        raise ResourceVersionConflict(
            f"expected resource version {expected_version}, found {metadata.resource_version}"
        )
    changed_at = at or datetime.now(UTC)
    return metadata.model_copy(
        update={
            "labels": dict(metadata.labels if labels is None else labels),
            "annotations": dict(metadata.annotations if annotations is None else annotations),
            "updated_at": changed_at,
            "updated_by": actor_id,
            "resource_version": metadata.resource_version + 1,
        }
    )


_ALLOWED_TRANSITIONS = {
    ResourceLifecycle.ACTIVE: {ResourceLifecycle.ARCHIVED, ResourceLifecycle.TOMBSTONED},
    ResourceLifecycle.ARCHIVED: {ResourceLifecycle.ACTIVE, ResourceLifecycle.TOMBSTONED},
    ResourceLifecycle.TOMBSTONED: {ResourceLifecycle.ACTIVE},
}


def transition_resource_lifecycle(
    metadata: ResourceMetadata,
    target: ResourceLifecycle,
    *,
    expected_version: int,
    actor_id: str,
    at: datetime | None = None,
) -> ResourceMetadata:
    if target not in _ALLOWED_TRANSITIONS[metadata.lifecycle]:
        raise InvalidLifecycleTransition(
            f"cannot transition resource from {metadata.lifecycle.value} to {target.value}"
        )
    changed_at = at or datetime.now(UTC)
    revised = revise_resource_metadata(
        metadata,
        expected_version=expected_version,
        actor_id=actor_id,
        at=changed_at,
    )
    timestamps: dict[str, datetime | None]
    if target is ResourceLifecycle.ACTIVE:
        timestamps = {"archived_at": None, "deleted_at": None}
    elif target is ResourceLifecycle.ARCHIVED:
        timestamps = {"archived_at": changed_at, "deleted_at": None}
    else:
        timestamps = {"deleted_at": changed_at}
    return revised.model_copy(update={"lifecycle": target, **timestamps})
