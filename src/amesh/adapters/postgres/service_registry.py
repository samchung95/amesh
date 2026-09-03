from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine

from amesh import __version__
from amesh.domain import (
    SYSTEM_TENANT_ID,
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
from amesh.ports import ServiceFenceError, ServiceRegistryRepository, ServiceVersionSkewError
from amesh.ports.errors import NotFoundError
from amesh.ports.repository_support import AuditWrite
from amesh.release_policy import component_compatibility

from .repository_support import PostgresRepositoryBase

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
        last_success_at = NULL,
        last_failure_at = NULL,
        consecutive_failures = 0,
        last_failure = NULL,
        stopped_at = NULL
    RETURNING *, clock_timestamp() AS database_now
    """
)

_HEARTBEAT = text(
    """
    UPDATE service_instances
        SET state = CASE
            WHEN state = 'DRAINING' THEN state
            WHEN CAST(:ready AS boolean) IS NULL THEN state
            WHEN CAST(:ready AS boolean) THEN 'READY'
            ELSE 'DEGRADED'
        END,
        ownership = CAST(:ownership AS jsonb),
        partitions = CAST(:partitions AS jsonb),
        dependencies = CAST(:dependencies AS jsonb),
        last_success_at = CASE
            WHEN CAST(:ready AS boolean) IS TRUE THEN clock_timestamp()
            ELSE last_success_at
        END,
        last_failure_at = CASE
            WHEN CAST(:ready AS boolean) IS FALSE THEN clock_timestamp()
            ELSE last_failure_at
        END,
        consecutive_failures = CASE
            WHEN CAST(:ready AS boolean) IS TRUE THEN 0
            WHEN CAST(:ready AS boolean) IS FALSE THEN consecutive_failures + 1
            ELSE consecutive_failures
        END,
        last_failure = CASE
            WHEN CAST(:ready AS boolean) IS TRUE THEN NULL
            WHEN CAST(:ready AS boolean) IS FALSE THEN :failure
            ELSE last_failure
        END,
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
      AND state IN ('STARTING', 'READY', 'DEGRADED', 'DRAINING')
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


class PostgresServiceRegistryRepository(PostgresRepositoryBase, ServiceRegistryRepository):
    def __init__(self, engine: AsyncEngine, *, stale_after_seconds: float = 20) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("service stale threshold must be positive")
        super().__init__(engine)
        self._stale_after = timedelta(seconds=stale_after_seconds)

    async def register(self, registration: ServiceRegistration) -> ServiceInstance:
        compatibility = component_compatibility(registration.version)
        if compatibility.compatibility is ServiceCompatibility.UNSAFE:
            raise ServiceVersionSkewError(
                f"service version {registration.version} is unsafe with {__version__}; "
                f"{compatibility.remediation}"
            )
        async with self._services.transactions.admin() as connection:
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
                            "labels": self._services.codec.dumps(registration.labels),
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
        ready: bool | None = True,
        failure: str | None = None,
    ) -> ServiceInstance:
        failure_summary = (
            (failure or "service cycle reported not ready")[:2048] if ready is False else None
        )
        async with self._services.transactions.admin() as connection:
            row = (
                (
                    await connection.execute(
                        _HEARTBEAT,
                        {
                            "instance_id": instance_id,
                            "generation": generation,
                            "ownership": self._services.codec.dumps(ownership or {}),
                            "partitions": self._services.codec.dumps(partitions or {}),
                            "dependencies": self._services.codec.dumps(dependencies or {}),
                            "ready": ready,
                            "failure": failure_summary,
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
        async with self._services.transactions.admin() as connection:
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
            await self._services.audit.write(
                connection,
                AuditWrite(
                    tenant_id=SYSTEM_TENANT_ID,
                    actor_id=actor_id,
                    action="service.drain",
                    resource_type="service_instance",
                    resource_id=str(instance_id),
                    outcome="ACCEPTED",
                    reason=reason,
                    source={"component": "service-registry"},
                    evidence={"expectedVersion": expected_version},
                    event_id=new_runtime_id(),
                    use_database_clock=True,
                    generate_correlation_id=False,
                ),
            )
        return self._to_instance(row)

    async def stop(self, instance_id: UUID, generation: int) -> ServiceInstance:
        async with self._services.transactions.admin() as connection:
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
        async with self._services.transactions.admin() as connection:
            row = (
                (await connection.execute(_GET, {"instance_id": instance_id}))
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise NotFoundError(
                "service instance",
                instance_id,
                message=f"service instance {instance_id} does not exist",
            )
        return self._to_instance(row)

    async def topology(self) -> ServiceTopology:
        async with self._services.transactions.admin() as connection:
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
            compatibility=component_compatibility(str(row["version"])).compatibility,
            generation=row["generation"],
            resourceVersion=row["resource_version"],
            labels=row["labels"] or {},
            ownership=row["ownership"] or {},
            partitions=row["partitions"] or {},
            dependencies=row["dependencies"] or {},
            registeredAt=row["registered_at"],
            lastHeartbeatAt=heartbeat,
            lastSuccessAt=row["last_success_at"],
            lastFailureAt=row["last_failure_at"],
            consecutiveFailures=row["consecutive_failures"],
            lastFailure=row["last_failure"],
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
        degraded = tuple(instance for instance in live if instance.state is ServiceState.DEGRADED)
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
            degradedInstances=len(degraded),
            drainingInstances=len(draining),
            staleInstances=sum(instance.liveness is ServiceLiveness.STALE for instance in selected),
            failureZones=zones,
            versions=tuple(sorted({instance.version for instance in live})),
            failoverStatus=failover,
        )
