from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncIterator

from pydantic import BaseModel, ConfigDict, Field

from amesh.domain import TenantDefinition
from amesh.dsl import FlowDefinition
from amesh.ports import ExecutionRepository, ObjectMetadata
from amesh.storage.service import VerifiedObjectStore
from amesh.tenancy import TenantService


class TenantTransferBundle(BaseModel):
    model_config = ConfigDict(frozen=True)

    format_version: int = 1
    tenant: TenantDefinition
    resource_counts: dict[str, int]
    flows: tuple[FlowDefinition, ...] = ()
    objects: tuple[ObjectMetadata, ...] = ()
    checksum_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    def verify(self) -> None:
        if self.checksum_sha256 != _bundle_checksum(self):
            raise ValueError("tenant transfer bundle checksum is invalid")


class TenantImportResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant: TenantDefinition
    flows_imported: int = Field(ge=0)
    objects_imported: int = Field(ge=0)


class TenantTransferService:
    def __init__(
        self,
        tenants: TenantService,
        executions: ExecutionRepository,
        object_store: VerifiedObjectStore,
    ) -> None:
        self._tenants = tenants
        self._executions = executions
        self._object_store = object_store

    async def export(self, tenant_slug: str, *, actor_id: str) -> TenantTransferBundle:
        tenant_export = await self._tenants.export(tenant_slug, actor_id=actor_id)
        persisted = await self._executions.list_flows(tenant_id=tenant_slug)
        flows = tuple(
            [
                await self._executions.get_flow(
                    item.namespace,
                    item.flow_id,
                    tenant_id=tenant_slug,
                    revision=item.revision,
                )
                for item in persisted
            ]
        )
        objects = tuple(
            sorted(
                [item async for item in self._object_store.iter_objects(tenant_slug)],
                key=lambda item: item.key or item.uri,
            )
        )
        unsigned = TenantTransferBundle(
            tenant=tenant_export.tenant,
            resource_counts=tenant_export.resource_counts,
            flows=flows,
            objects=objects,
            checksum_sha256="0" * 64,
        )
        return unsigned.model_copy(update={"checksum_sha256": _bundle_checksum(unsigned)})

    async def import_bundle(
        self,
        bundle: TenantTransferBundle,
        *,
        target_slug: str,
        actor_id: str,
    ) -> TenantImportResult:
        bundle.verify()
        tenant = await self._tenants.create(
            slug=target_slug,
            display_name=bundle.tenant.display_name,
            policy=bundle.tenant.policy,
            actor_id=actor_id,
        )
        for flow in bundle.flows:
            await self._executions.apply_flow(
                flow,
                tenant_id=target_slug,
                actor_id=actor_id,
            )
        for metadata in bundle.objects:
            if metadata.key is None:
                raise ValueError(f"tenant object {metadata.uri} has no portable key")
            await self._object_store.put(
                target_slug,
                metadata.key,
                self._object_store.get_version(bundle.tenant.slug, metadata),
                content_type=metadata.content_type,
            )
        return TenantImportResult(
            tenant=tenant,
            flows_imported=len(bundle.flows),
            objects_imported=len(bundle.objects),
        )


def _bundle_checksum(bundle: TenantTransferBundle) -> str:
    encoded = json.dumps(
        bundle.model_dump(mode="json", exclude={"checksum_sha256"}),
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


async def bundle_chunks(bundle: TenantTransferBundle) -> AsyncIterator[bytes]:
    yield bundle.model_dump_json(indent=2).encode()
