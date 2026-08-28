from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from amesh.domain import (
    InvalidLifecycleTransition,
    ManagedResource,
    ResourceLifecycle,
    ResourceMetadata,
    ResourceVersionConflict,
    RuntimeIdentity,
    RuntimeResourceType,
    canonical_hash,
    canonical_json,
    resource_etag,
    revise_resource_metadata,
    transition_resource_lifecycle,
)


def test_canonical_serialization_is_mapping_order_independent() -> None:
    left = {"z": 1, "nested": {"b": True, "a": [2, 1]}}
    right = {"nested": {"a": [2, 1], "b": True}, "z": 1}

    assert canonical_json(left) == canonical_json(right)
    assert canonical_hash(left) == canonical_hash(right)
    assert resource_etag(left).startswith('"sha256:')

    with pytest.raises(ValueError):
        canonical_json({"invalid": float("nan")})


def test_resource_metadata_revision_enforces_optimistic_concurrency() -> None:
    created = datetime(2026, 8, 21, tzinfo=UTC)
    metadata = ResourceMetadata(created_at=created, updated_at=created)

    revised = revise_resource_metadata(
        metadata,
        expected_version=1,
        actor_id="user:alice",
        labels={"team": "platform"},
        at=created + timedelta(seconds=1),
    )

    assert revised.resource_version == 2
    assert revised.updated_by == "user:alice"
    assert revised.labels == {"team": "platform"}
    assert revised.etag != metadata.etag
    with pytest.raises(ResourceVersionConflict):
        revise_resource_metadata(metadata, expected_version=2, actor_id="user:bob")


def test_resource_lifecycle_archive_tombstone_and_restore() -> None:
    created = datetime(2026, 8, 21, tzinfo=UTC)
    metadata = ResourceMetadata(created_at=created, updated_at=created)

    archived = transition_resource_lifecycle(
        metadata,
        ResourceLifecycle.ARCHIVED,
        expected_version=1,
        actor_id="user:alice",
        at=created + timedelta(seconds=1),
    )
    tombstoned = transition_resource_lifecycle(
        archived,
        ResourceLifecycle.TOMBSTONED,
        expected_version=2,
        actor_id="user:alice",
        at=created + timedelta(seconds=2),
    )
    restored = transition_resource_lifecycle(
        tombstoned,
        ResourceLifecycle.ACTIVE,
        expected_version=3,
        actor_id="user:admin",
        at=created + timedelta(seconds=3),
    )

    assert archived.archived_at is not None
    assert tombstoned.deleted_at is not None
    assert restored.lifecycle is ResourceLifecycle.ACTIVE
    assert restored.archived_at is None
    assert restored.deleted_at is None
    assert restored.resource_version == 4
    with pytest.raises(InvalidLifecycleTransition):
        transition_resource_lifecycle(
            restored,
            ResourceLifecycle.ACTIVE,
            expected_version=4,
            actor_id="user:admin",
        )


def test_managed_resource_etag_covers_identity_metadata_and_spec() -> None:
    resource = ManagedResource(
        identity=RuntimeIdentity(resource_type=RuntimeResourceType.FLOW),
        natural_key={"tenant": "default", "namespace": "examples", "flow": "hello"},
        spec={"tasks": [{"id": "done"}]},
    )

    changed = resource.model_copy(update={"spec": {"tasks": [{"id": "changed"}]}})

    assert resource.etag != changed.etag
