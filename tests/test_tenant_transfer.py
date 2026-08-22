from __future__ import annotations

import asyncio
import hashlib
from collections.abc import AsyncIterator
from types import SimpleNamespace

import pytest

from amesh.domain import TenantDefinition, TenantExport, TenantPolicy
from amesh.dsl import FlowDefinition, TaskDefinition
from amesh.ports import ObjectMetadata
from amesh.tenant_transfer import TenantTransferService


class FakeTenants:
    def __init__(self) -> None:
        self.created: TenantDefinition | None = None

    async def export(self, tenant_slug: str, *, actor_id: str) -> TenantExport:
        return TenantExport(
            tenant=TenantDefinition(slug=tenant_slug, display_name="Source tenant"),
            resource_counts={"flows": 1},
            exported_by=actor_id,
        )

    async def create(
        self,
        *,
        slug: str,
        display_name: str,
        policy: TenantPolicy,
        actor_id: str,
    ) -> TenantDefinition:
        del actor_id
        self.created = TenantDefinition(slug=slug, display_name=display_name, policy=policy)
        return self.created


class FakeExecutions:
    def __init__(self, flow: FlowDefinition) -> None:
        self.flow = flow
        self.applied: list[tuple[str, FlowDefinition]] = []

    async def list_flows(self, *, tenant_id: str) -> list[SimpleNamespace]:
        del tenant_id
        return [
            SimpleNamespace(
                namespace=self.flow.namespace,
                flow_id=self.flow.id,
                revision=self.flow.revision,
            )
        ]

    async def get_flow(
        self,
        namespace: str,
        flow_id: str,
        *,
        tenant_id: str,
        revision: int | None = None,
    ) -> FlowDefinition:
        del namespace, flow_id, tenant_id, revision
        return self.flow

    async def apply_flow(
        self,
        flow: FlowDefinition,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> SimpleNamespace:
        del actor_id
        self.applied.append((tenant_id, flow))
        return SimpleNamespace()


class FakeObjects:
    def __init__(self) -> None:
        self.content = {("source", "artifact.bin", "v1"): b"portable"}
        self.imported: dict[tuple[str, str], bytes] = {}
        self.metadata = ObjectMetadata(
            uri="memory://source/artifact.bin",
            tenant_id="source",
            key="artifact.bin",
            version_id="v1",
            size=8,
            checksum_sha256=hashlib.sha256(b"portable").hexdigest(),
        )

    def iter_objects(self, tenant_id: str) -> AsyncIterator[ObjectMetadata]:
        async def values() -> AsyncIterator[ObjectMetadata]:
            if tenant_id == "source":
                yield self.metadata

        return values()

    def get_version(
        self,
        tenant_id: str,
        metadata: ObjectMetadata,
    ) -> AsyncIterator[bytes]:
        async def chunks() -> AsyncIterator[bytes]:
            assert metadata.key is not None and metadata.version_id is not None
            yield self.content[(tenant_id, metadata.key, metadata.version_id)]

        return chunks()

    async def put(
        self,
        tenant_id: str,
        key: str,
        chunks: AsyncIterator[bytes],
        *,
        content_type: str | None = None,
    ) -> ObjectMetadata:
        del content_type
        content = b"".join([part async for part in chunks])
        self.imported[(tenant_id, key)] = content
        return self.metadata.model_copy(update={"tenant_id": tenant_id, "key": key})


def test_checksum_protected_tenant_export_import() -> None:
    async def scenario() -> None:
        tenants = FakeTenants()
        flow = FlowDefinition(
            id="portable",
            namespace="example.transfer",
            tasks=[TaskDefinition(id="echo", type="core.echo", message="portable")],
        )
        executions = FakeExecutions(flow)
        objects = FakeObjects()
        service = TenantTransferService(tenants, executions, objects)  # type: ignore[arg-type]

        bundle = await service.export("source", actor_id="test:export")
        bundle.verify()
        result = await service.import_bundle(
            bundle,
            target_slug="destination",
            actor_id="test:import",
        )

        assert result.tenant.slug == "destination"
        assert result.flows_imported == result.objects_imported == 1
        assert executions.applied == [("destination", flow)]
        assert objects.imported[("destination", "artifact.bin")] == b"portable"

        corrupted = bundle.model_copy(update={"resource_counts": {"flows": 2}})
        with pytest.raises(ValueError, match="checksum"):
            await service.import_bundle(
                corrupted,
                target_slug="rejected",
                actor_id="test:import",
            )

    asyncio.run(scenario())
