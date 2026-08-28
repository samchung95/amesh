from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ServiceRole(StrEnum):
    WEBSERVER = "webserver"
    EXECUTOR = "executor"
    SCHEDULER = "scheduler"
    WORKER = "worker"
    INDEXER = "indexer"
    MAINTENANCE = "maintenance"


class ServiceState(StrEnum):
    STARTING = "STARTING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    DRAINING = "DRAINING"
    STOPPED = "STOPPED"


class ServiceLiveness(StrEnum):
    LIVE = "LIVE"
    STALE = "STALE"
    STOPPED = "STOPPED"


class ServiceCompatibility(StrEnum):
    CURRENT = "CURRENT"
    ROLLING_COMPATIBLE = "ROLLING_COMPATIBLE"
    UNSAFE = "UNSAFE"


class FailoverStatus(StrEnum):
    REDUNDANT = "REDUNDANT"
    AVAILABLE = "AVAILABLE"
    DRAINING = "DRAINING"
    UNAVAILABLE = "UNAVAILABLE"


class ServiceRegistration(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    instance_id: UUID = Field(alias="id")
    role: ServiceRole
    instance_name: str = Field(min_length=1, max_length=256, alias="instanceName")
    version: str = Field(min_length=1, max_length=128)
    failure_zone: str | None = Field(default=None, max_length=256, alias="failureZone")
    labels: dict[str, str] = Field(default_factory=dict)


class ServiceInstance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    instance_id: UUID = Field(alias="id")
    role: ServiceRole
    instance_name: str = Field(alias="instanceName")
    version: str
    failure_zone: str | None = Field(default=None, alias="failureZone")
    state: ServiceState
    liveness: ServiceLiveness
    compatibility: ServiceCompatibility
    generation: int = Field(ge=1)
    resource_version: int = Field(ge=1, alias="resourceVersion")
    labels: dict[str, str] = Field(default_factory=dict)
    ownership: dict[str, Any] = Field(default_factory=dict)
    partitions: dict[str, Any] = Field(default_factory=dict)
    dependencies: dict[str, str] = Field(default_factory=dict)
    registered_at: datetime = Field(alias="registeredAt")
    last_heartbeat_at: datetime = Field(alias="lastHeartbeatAt")
    last_success_at: datetime | None = Field(default=None, alias="lastSuccessAt")
    last_failure_at: datetime | None = Field(default=None, alias="lastFailureAt")
    consecutive_failures: int = Field(default=0, ge=0, alias="consecutiveFailures")
    last_failure: str | None = Field(default=None, alias="lastFailure")
    stopped_at: datetime | None = Field(default=None, alias="stoppedAt")


class ServiceRoleStatus(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    role: ServiceRole
    total_instances: int = Field(ge=0, alias="totalInstances")
    live_instances: int = Field(ge=0, alias="liveInstances")
    ready_instances: int = Field(ge=0, alias="readyInstances")
    degraded_instances: int = Field(ge=0, alias="degradedInstances")
    draining_instances: int = Field(ge=0, alias="drainingInstances")
    stale_instances: int = Field(ge=0, alias="staleInstances")
    failure_zones: tuple[str, ...] = Field(alias="failureZones")
    versions: tuple[str, ...]
    failover_status: FailoverStatus = Field(alias="failoverStatus")


class ServiceTopology(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    observed_at: datetime = Field(alias="observedAt")
    current_version: str = Field(alias="currentVersion")
    version_skew: bool = Field(alias="versionSkew")
    coordination: str = "postgresql-leases-and-fencing"
    quorum_dependencies: dict[str, str] = Field(alias="quorumDependencies")
    roles: tuple[ServiceRoleStatus, ...]
    instances: tuple[ServiceInstance, ...]


class ServiceDrainRequest(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    expected_version: int = Field(ge=1, alias="expectedVersion")
    reason: str = Field(min_length=1, max_length=1_024)
