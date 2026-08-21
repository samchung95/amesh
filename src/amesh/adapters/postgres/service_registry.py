from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh import __version__
from amesh.domain import (
    FailoverStatus,
    ServiceCompatibility,
    ServiceInstance,
    ServiceLiveness,
    ServiceRegistration,
    ServiceRole,
    ServiceRoleStatus,
    ServiceState,
    ServiceTopology,
    new_runtime_id,
)
from amesh.ports import ServiceFenceError, ServiceRegistryRepository

_REGISTER = text(
    """
    INSERT INTO service_instances (
        id, role, instance_name, version, failure_zone, labels
    ) VALUES (
        :instance_id, :role, :instance_name, :version, :failure_zone, CAST(:labels AS jsonb)
    )
    ON CONFLICT (role, instance_name) DO UPDATE SET
        id = EXCLUDED.id,
        version = EXCLUDED.version,
        failure_zone = EXCLUDED.failure_zone,
        state = 'STARTING',
        generation = service_instances.generation + 1,
        resource_version = service_instances.resource_version + 1,
        labels = EXCLUDED.labels,
        ownership = '{}'::jsonb,
        partitions = '{}'::jsonb,
        dependencies = '{}'::jsonb,
        registered_at = clock_timestamp(),
        last_heartbeat_at = clock_timestamp(),
        stopped_at = NULL
    RETURNING *, clock_timestamp() AS database_now
    """
)

_HEARTBEAT = text(
    """
    UPDATE service_instances
    SET state = CASE WHEN state = 'DRAINING' THEN state ELSE 'READY' END,
        ownership = CAST(:ownership AS jsonb),
        partitions = CAST(:partitions AS jsonb),
        dependencies = CAST(:dependencies AS jsonb),
        last_heartbeat_at = clock_timestamp(),
        resource_version = resource_version + 1
    WHERE id = :instance_id
      AND generation = :generation
      AND state <> 'STOPPED'
    RETURNING *, clock_timestamp() AS database_now
    """
)

_DRAIN = text(
    """
    UPDATE service_instances
    SET state = 'DRAINING',
        resource_version = resource_version + 1
    WHERE id = :instance_id
      AND resource_version = :expected_version
      AND state IN ('STARTING', 'READY', 'DRAINING')
    RETURNING *, clock_timestamp() AS database_now
    """
)

_STOP = text(
    """
    UPDATE service_instances
    SET state = 'STOPPED',
        stopped_at = clock_timestamp(),
        last_heartbeat_at = clock_timestamp(),
        resource_version = resource_version + 1
    WHERE id = :instance_id
      AND generation = :generation
      AND state <> 'STOPPED'
    RETURNING *, clock_timestamp() AS database_now
    """
)

_GET = text(
    """
    SELECT *, clock_timestamp() AS database_now
    FROM service_instances
    WHERE id = :instance_id
    """
)

_LIST = text(
    """
    SELECT *, clock_timestamp() AS database_now
    FROM service_instances
    ORDER BY role, instance_name, generation
    """
)

_AUDIT_DRAIN = text(
    """
    INSERT INTO audit_events (
        event_id, actor_id, action, resource_type, resource_id,
        outcome, reason, source, evidence, occurred_at
    ) VALUES (
        :event_id, :actor_id, 'service.drain', 'service_instance', :instance_id,
        'ACCEPTED', :reason, '{"component":"service-registry"}'::jsonb,
        jsonb_build_object('expectedVersion', CAST(:expected_version AS bigint)),
        clock_timestamp()
    )
    """
)


class PostgresServiceRegistryRepository(ServiceRegistryRepository):
    def __init__(self, engine: AsyncEngine, *, stale_after_seconds: float = 20) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("service stale threshold must be positive")
        self._engine = engine
        self._stale_after = timedelta(seconds=stale_after_seconds)

    async def register(self, registration: ServiceRegistration) -> ServiceInstance:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        _REGISTER,
                        {
                            "instance_id": registration.instance_id,
                            "role": registration.role.value,
                            "instance_name": registration.instance_name,
                            "version": registration.version,
                            "failure_zone": registration.failure_zone,
                            "labels": json.dumps(registration.labels),
                        },
                    )
                )
                .mappings()
                .one()
            )
        return self._to_instance(row)

    async def heartbeat(
        self,
        instance_id: UUID,
        generation: int,
        *,
        ownership: dict[str, Any] | None = None,
        partitions: dict[str, Any] | None = None,
        dependencies: dict[str, str] | None = None,
    ) -> ServiceInstance:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        _HEARTBEAT,
                        {
                            "instance_id": instance_id,
                            "generation": generation,
                            "ownership": json.dumps(ownership or {}),
                            "partitions": json.dumps(partitions or {}),
                            "dependencies": json.dumps(dependencies or {}),
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise ServiceFenceError(
                f"service instance {instance_id} generation {generation} is stale or stopped"
            )
        return self._to_instance(row)

    async def request_drain(
        self,
        instance_id: UUID,
        *,
        expected_version: int,
        actor_id: str,
        reason: str,
    ) -> ServiceInstance:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        _DRAIN,
                        {
                            "instance_id": instance_id,
                            "expected_version": expected_version,
                        },
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                raise ServiceFenceError(
                    f"service instance {instance_id} version {expected_version} is stale"
                )
            await connection.execute(
                _AUDIT_DRAIN,
                {
                    "event_id": new_runtime_id(),
                    "actor_id": actor_id,
                    "instance_id": str(instance_id),
                    "reason": reason,
                    "expected_version": expected_version,
                },
            )
        return self._to_instance(row)

    async def stop(self, instance_id: UUID, generation: int) -> ServiceInstance:
        async with self._engine.begin() as connection:
            row = (
                (
                    await connection.execute(
                        _STOP,
                        {"instance_id": instance_id, "generation": generation},
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise ServiceFenceError(
                f"service instance {instance_id} generation {generation} is stale or stopped"
            )
        return self._to_instance(row)

    async def get(self, instance_id: UUID) -> ServiceInstance:
        async with self._engine.connect() as connection:
            row = (
                (await connection.execute(_GET, {"instance_id": instance_id}))
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise LookupError(f"service instance {instance_id} does not exist")
        return self._to_instance(row)

    async def topology(self) -> ServiceTopology:
        async with self._engine.connect() as connection:
            rows = (await connection.execute(_LIST)).mappings().all()
            observed_at = await connection.scalar(text("SELECT clock_timestamp()"))
        if not isinstance(observed_at, datetime):
            raise TypeError("PostgreSQL returned an invalid topology timestamp")
        instances = tuple(self._to_instance(row) for row in rows)
        versions = {
            instance.version
            for instance in instances
            if instance.liveness is not ServiceLiveness.STOPPED
        }
        role_statuses = tuple(self._role_status(role, instances) for role in ServiceRole)
        return ServiceTopology(
            observedAt=observed_at,
            currentVersion=__version__,
            versionSkew=any(version != __version__ for version in versions),
            quorumDependencies={
                "postgresql": "external HA primary with quorum/failover managed by the operator",
                "objectStorage": "S3-compatible replicated or versioned storage",
                "kubernetes": "stateless placement only; etcd is not orchestration truth",
            },
            roles=role_statuses,
            instances=instances,
        )

    def _to_instance(self, row: RowMapping) -> ServiceInstance:
        database_now = row["database_now"]
        heartbeat = row["last_heartbeat_at"]
        if not isinstance(database_now, datetime) or not isinstance(heartbeat, datetime):
            raise TypeError("PostgreSQL returned invalid service timestamps")
        state = ServiceState(row["state"])
        if state is ServiceState.STOPPED:
            liveness = ServiceLiveness.STOPPED
        elif database_now - heartbeat > self._stale_after:
            liveness = ServiceLiveness.STALE
        else:
            liveness = ServiceLiveness.LIVE
        return ServiceInstance(
            id=row["id"],
            role=ServiceRole(row["role"]),
            instanceName=row["instance_name"],
            version=row["version"],
            failureZone=row["failure_zone"],
            state=state,
            liveness=liveness,
            compatibility=(
                ServiceCompatibility.CURRENT
                if row["version"] == __version__
                else ServiceCompatibility.VERSION_SKEW
            ),
            generation=row["generation"],
            resourceVersion=row["resource_version"],
            labels=row["labels"] or {},
            ownership=row["ownership"] or {},
            partitions=row["partitions"] or {},
            dependencies=row["dependencies"] or {},
            registeredAt=row["registered_at"],
            lastHeartbeatAt=heartbeat,
            stoppedAt=row["stopped_at"],
        )

    @staticmethod
    def _role_status(
        role: ServiceRole,
        instances: tuple[ServiceInstance, ...],
    ) -> ServiceRoleStatus:
        selected = tuple(instance for instance in instances if instance.role is role)
        live = tuple(instance for instance in selected if instance.liveness is ServiceLiveness.LIVE)
        ready = tuple(instance for instance in live if instance.state is ServiceState.READY)
        draining = tuple(instance for instance in live if instance.state is ServiceState.DRAINING)
        zones = tuple(
            sorted({instance.failure_zone for instance in ready if instance.failure_zone})
        )
        if len(ready) >= 2 and len(zones) >= 2:
            failover = FailoverStatus.REDUNDANT
        elif ready:
            failover = FailoverStatus.AVAILABLE
        elif draining:
            failover = FailoverStatus.DRAINING
        else:
            failover = FailoverStatus.UNAVAILABLE
        return ServiceRoleStatus(
            role=role,
            totalInstances=len(selected),
            liveInstances=len(live),
            readyInstances=len(ready),
            drainingInstances=len(draining),
            staleInstances=sum(instance.liveness is ServiceLiveness.STALE for instance in selected),
            failureZones=zones,
            versions=tuple(sorted({instance.version for instance in live})),
            failoverStatus=failover,
        )
