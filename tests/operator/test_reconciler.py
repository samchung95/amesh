from __future__ import annotations

import asyncio
import json
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

import pytest

from amesh.operator.client import AmeshApiError, RemoteResource, ResourceIdentity, canonical_digest
from amesh.operator.model import (
    FINALIZER,
    RESOURCE_DESCRIPTORS,
    OperatorSettings,
    OperatorTarget,
    ResourceDescriptor,
    SecretReference,
)
from amesh.operator.reconciler import AmeshResourceReconciler


def _async_test[**P](function: Callable[P, Coroutine[Any, Any, None]]) -> Callable[P, None]:
    @wraps(function)
    def run(*args: P.args, **kwargs: P.kwargs) -> None:
        asyncio.run(function(*args, **kwargs))

    return run


class FakeKubernetes:
    def __init__(self) -> None:
        self.finalizers: list[tuple[str, ...]] = []
        self.statuses: list[dict[str, Any]] = []
        self.events: list[dict[str, str]] = []
        self.secret = "operator-secret-token"
        self.secret_reads = 0

    async def patch_finalizers(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        finalizers: tuple[str, ...],
    ) -> None:
        self.finalizers.append(finalizers)

    async def patch_status(
        self,
        descriptor: ResourceDescriptor,
        resource: dict[str, Any],
        status: dict[str, Any],
    ) -> None:
        self.statuses.append(status)

    async def read_secret(self, namespace: str, name: str, key: str) -> str:
        assert (namespace, name, key) == ("amesh-system", "amesh-admin", "token")
        self.secret_reads += 1
        return self.secret

    async def emit_event(
        self,
        resource: dict[str, Any],
        *,
        event_type: str,
        reason: str,
        message: str,
    ) -> None:
        self.events.append({"type": event_type, "reason": reason, "message": message})


class FakeApi:
    def __init__(self, remote: RemoteResource | None = None) -> None:
        self.remote = remote
        self.read_error: Exception | None = None
        self.applies: list[dict[str, Any]] = []
        self.deletes: list[ResourceIdentity] = []

    async def read(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> RemoteResource | None:
        assert token == "operator-secret-token"
        if self.read_error is not None:
            raise self.read_error
        return self.remote

    async def apply(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        desired: object,
        target: OperatorTarget,
        token: str,
        *,
        exists: bool,
        content_type: str | None = None,
    ) -> RemoteResource:
        self.applies.append({"desired": desired, "exists": exists, "identity": identity})
        self.remote = RemoteResource(desired, server_id="remote-1", revision="3")
        return self.remote

    async def delete(
        self,
        descriptor: ResourceDescriptor,
        identity: ResourceIdentity,
        target: OperatorTarget,
        token: str,
    ) -> None:
        self.deletes.append(identity)


def _settings() -> OperatorSettings:
    return OperatorSettings(
        watch_namespaces=("amesh-system",),
        targets=(
            OperatorTarget(
                tenant="default",
                endpoint="http://amesh",
                credential=SecretReference("amesh-system", "amesh-admin", "token"),
            ),
        ),
    )


def _descriptor(kind: str = "AmeshKeyValue") -> ResourceDescriptor:
    return next(item for item in RESOURCE_DESCRIPTORS if item.kind == kind)


def _resource(
    *,
    document: dict[str, object] | None = None,
    status: dict[str, object] | None = None,
    deleting: bool = False,
    deletion_policy: str = "Retain",
) -> dict[str, Any]:
    metadata: dict[str, object] = {
        "name": "operator-key",
        "namespace": "amesh-system",
        "generation": 4,
        "uid": "resource-uid",
        "finalizers": [FINALIZER],
    }
    if deleting:
        metadata["deletionTimestamp"] = "2026-08-23T00:00:00Z"
    return {
        "apiVersion": "platform.amesh.io/v1alpha1",
        "kind": "AmeshKeyValue",
        "metadata": metadata,
        "spec": {
            "tenant": "default",
            "namespace": "operator.acceptance",
            "key": "operator-key",
            "deletionPolicy": deletion_policy,
            "document": document or {"value": {"message": "desired"}, "type": "JSON"},
        },
        "status": status or {},
    }


@_async_test
async def test_create_sets_finalizer_conditions_observed_generation_and_safe_status() -> None:
    kubernetes = FakeKubernetes()
    api = FakeApi()
    resource = _resource()
    resource["metadata"]["finalizers"] = []

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), resource
    )

    assert result.outcome == "created"
    assert kubernetes.finalizers == [(FINALIZER,)]
    assert api.applies[0]["exists"] is False
    assert kubernetes.statuses[-1]["observedGeneration"] == 4
    assert kubernetes.statuses[-1]["conditions"][0]["status"] == "True"
    assert kubernetes.statuses[-1]["remoteId"] == "remote-1"
    assert "operator-secret-token" not in json.dumps(kubernetes.statuses + kubernetes.events)


@_async_test
async def test_remote_drift_is_detected_and_corrected() -> None:
    kubernetes = FakeKubernetes()
    api = FakeApi(RemoteResource({"value": {"message": "drifted"}, "type": "JSON"}))

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), _resource()
    )

    assert result.outcome == "updated"
    assert api.applies[0]["exists"] is True
    assert kubernetes.statuses[-1]["conditions"][1]["reason"] == "Corrected"
    assert kubernetes.events[-1]["reason"] == "DriftCorrected"


@_async_test
async def test_unchanged_remote_state_does_not_apply() -> None:
    desired = {"value": {"message": "desired"}, "type": "JSON"}
    kubernetes = FakeKubernetes()
    api = FakeApi(RemoteResource(desired, revision="2"))

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), _resource(document=desired)
    )

    assert result.outcome == "unchanged"
    assert api.applies == []
    assert kubernetes.statuses[-1]["remoteRevision"] == "2"


@_async_test
@pytest.mark.parametrize("policy, expected_deletes", [("Retain", 0), ("Delete", 1)])
async def test_finalizer_honors_explicit_deletion_policy(
    policy: str, expected_deletes: int
) -> None:
    kubernetes = FakeKubernetes()
    api = FakeApi()
    status = {"remoteId": "remote-1", "remoteRevision": "2"}

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(),
        _resource(status=status, deleting=True, deletion_policy=policy),
    )

    assert result.outcome == "deleted"
    assert len(api.deletes) == expected_deletes
    assert kubernetes.secret_reads == expected_deletes
    assert kubernetes.finalizers == [()]
    assert (
        kubernetes.events[-1]["reason"]
        == {
            "Retain": "RemoteRetained",
            "Delete": "RemoteDeleted",
        }[policy]
    )


@_async_test
async def test_transient_failure_records_backoff_without_response_body_or_secret() -> None:
    kubernetes = FakeKubernetes()
    api = FakeApi()
    api.read_error = AmeshApiError("GET", "/api/v1/resource", 503)

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), _resource(status={"failureCount": 1})
    )

    assert result.outcome == "failed"
    assert result.requeue_after_seconds == 4
    rendered = json.dumps(kubernetes.statuses + kubernetes.events)
    assert "HTTP 503" in rendered
    assert "operator-secret-token" not in rendered
    assert kubernetes.statuses[-1]["failureCount"] == 2


@_async_test
async def test_periodic_resync_does_not_rewrite_current_status_or_emit_duplicate_event() -> None:
    desired = {"value": {"message": "desired"}, "type": "JSON"}
    remote = {**desired, "expiresAt": None, "metadata": {}}
    digest = canonical_digest(remote)
    kubernetes = FakeKubernetes()
    api = FakeApi(RemoteResource(remote, revision="2"))
    resource = _resource(
        document=desired,
        status={
            "observedGeneration": 4,
            "appliedDigest": digest,
            "remoteDigest": digest,
            "failureCount": 0,
            "conditions": [{"type": "Ready", "status": "True"}],
        },
    )

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), resource
    )

    assert result.outcome == "unchanged"
    assert kubernetes.statuses == []
    assert kubernetes.events == []


@_async_test
async def test_tenant_outside_credential_scope_is_permanent() -> None:
    kubernetes = FakeKubernetes()
    api = FakeApi()
    resource = _resource()
    resource["spec"]["tenant"] = "other"

    result = await AmeshResourceReconciler(_settings(), kubernetes, api).reconcile(
        _descriptor(), resource
    )

    assert result.requeue_after_seconds is None
    assert kubernetes.statuses[-1]["conditions"][0]["reason"] == "InvalidResource"


def test_operator_settings_parse_scoped_multi_tenant_secret_targets() -> None:
    settings = OperatorSettings.from_environment(
        {
            "AMESH_OPERATOR_WATCH_NAMESPACES": '["team-a","team-b"]',
            "AMESH_OPERATOR_TARGETS": json.dumps(
                [
                    {
                        "tenant": "tenant-a",
                        "endpoint": "https://amesh-a.example",
                        "credentialSecretRef": {
                            "namespace": "operator-system",
                            "name": "tenant-a-token",
                            "key": "token",
                        },
                    },
                    {
                        "tenant": "tenant-b",
                        "endpoint": "https://amesh-b.example",
                        "credentialSecretRef": {
                            "namespace": "operator-system",
                            "name": "tenant-b-token",
                            "key": "token",
                        },
                    },
                ]
            ),
        }
    )

    assert settings.watch_namespaces == ("team-a", "team-b")
    assert settings.target("tenant-b").credential.name == "tenant-b-token"
    with pytest.raises(ValueError, match="credential scope"):
        settings.target("tenant-c")
