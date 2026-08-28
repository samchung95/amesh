from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, date, datetime
from typing import Any

from semantic_version import SimpleSpec, Version  # type: ignore[import-untyped]

from amesh import __version__
from amesh.domain import (
    ConfigurationMigration,
    ConfigurationMigrationKind,
    RollingUpgradeStep,
    ServiceCompatibility,
    ServiceLiveness,
    UpgradeCheck,
    UpgradeCheckStatus,
    UpgradeDatabaseInventory,
    UpgradePhase,
    UpgradePolicy,
    UpgradeReport,
)
from amesh.dsl import ResourceSchemaRegistry, validate_flow_document
from amesh.migrations import migration_directory, migration_plan
from amesh.plugin_sdk.catalog import PluginCatalogManager, PluginLifecycleStatus
from amesh.plugin_sdk.manifest import PluginManifest
from amesh.ports import ServiceRegistryRepository, UpgradeRepository
from amesh.release_policy import load_upgrade_policy
from amesh.storage import VerifiedObjectStore


class UpgradeService:
    def __init__(
        self,
        repository: UpgradeRepository,
        service_registry: ServiceRegistryRepository,
        plugins: PluginCatalogManager,
        object_store: VerifiedObjectStore,
        *,
        policy: UpgradePolicy | None = None,
    ) -> None:
        self._repository = repository
        self._service_registry = service_registry
        self._plugins = plugins
        self._object_store = object_store
        self._policy = policy or load_upgrade_policy()

    @property
    def policy(self) -> UpgradePolicy:
        return self._policy

    async def pre_upgrade(self, from_version: str, to_version: str) -> UpgradeReport:
        return await self._report(UpgradePhase.PRE_UPGRADE, from_version, to_version)

    async def post_upgrade(self, from_version: str, to_version: str) -> UpgradeReport:
        return await self._report(UpgradePhase.POST_UPGRADE, from_version, to_version)

    async def _report(
        self,
        phase: UpgradePhase,
        from_version: str,
        to_version: str,
    ) -> UpgradeReport:
        source = self._policy.release(from_version)
        target = self._policy.release(to_version)
        path = self._policy.path(from_version, to_version)
        inventory = await self._repository.inventory()
        checks: list[UpgradeCheck] = []

        checks.append(self._support_check(source, target))
        schema_check, migration_check = self._migration_checks(
            phase,
            source.schema_migration,
            target.schema_migration,
            inventory,
            path.rolling_compatible,
        )
        checks.extend((schema_check, migration_check))
        checks.append(
            UpgradeCheck(
                name="configuration",
                category="configuration",
                status=UpgradeCheckStatus.PASS,
                detail="typed runtime configuration loaded without validation errors",
                evidence={"platformVersion": __version__},
            )
        )
        checks.append(self._plugin_check())
        checks.append(await self._flow_check())
        checks.append(await self._storage_check())
        checks.append(self._capacity_check(inventory))
        checks.append(await self._service_skew_check(phase))
        checks.append(self._event_schema_check(phase, inventory))
        checks.append(
            UpgradeCheck(
                name="rollback-evidence",
                category="recovery",
                status=UpgradeCheckStatus.PASS,
                detail=(
                    f"{path.rollback_window_hours}-hour rollback window and restoration "
                    "procedure are declared"
                ),
                evidence={"rollbackWindowHours": path.rollback_window_hours},
            )
        )

        warnings = tuple(
            check.detail for check in checks if check.status is UpgradeCheckStatus.WARNING
        )
        safe = not any(check.status is UpgradeCheckStatus.BLOCKED for check in checks)
        rolling = (
            path.rolling_compatible
            and migration_check.status is not UpgradeCheckStatus.BLOCKED
        )
        fingerprint = _report_fingerprint(phase, from_version, to_version, checks)
        return UpgradeReport(
            phase=phase,
            fromVersion=from_version,
            toVersion=to_version,
            observedAt=datetime.now(UTC),
            safeToProceed=safe,
            rollingCompatible=rolling,
            checks=tuple(checks),
            warnings=warnings,
            rollingPlan=_rolling_plan() if rolling else (),
            restorationGuidance=path.restoration_guidance,
            reportFingerprint=fingerprint,
        )

    def migrate_configuration(
        self,
        kind: ConfigurationMigrationKind,
        document: Mapping[str, Any],
        *,
        target_version: str,
    ) -> ConfigurationMigration:
        self._policy.release(target_version)
        source = dict(document)
        warnings: tuple[str, ...] = ()
        if kind is ConfigurationMigrationKind.FLOW:
            validation = validate_flow_document(source)
            if not validation.valid or validation.canonical is None:
                issues = "; ".join(
                    f"{issue.path}: {issue.message}" for issue in validation.issues[:5]
                )
                raise ValueError(f"flow configuration cannot be migrated: {issues}")
            canonical = validation.canonical
        else:
            manifest = PluginManifest.model_validate(source)
            if not SimpleSpec(manifest.compatibility.platform_version).match(
                Version(target_version)
            ):
                raise ValueError(
                    f"plugin platformVersion {manifest.compatibility.platform_version!r} "
                    f"does not include target {target_version}; publish a compatible plugin release"
                )
            canonical = manifest.model_dump(mode="json", by_alias=True, exclude_none=True)
            if manifest.version != target_version:
                warnings = (
                    "plugin package version is independent from the platform target and was preserved",
                )
        return ConfigurationMigration(
            kind=kind,
            targetVersion=target_version,
            changed=_canonical_json(source) != _canonical_json(canonical),
            canonical=canonical,
            warnings=warnings,
        )

    def _support_check(self, source: Any, target: Any) -> UpgradeCheck:
        today = date.today()
        supported = (
            source.support_starts_on <= today <= source.support_ends_on
            and target.support_starts_on <= today <= target.support_ends_on
            and source.lts
            and target.lts
        )
        return UpgradeCheck(
            name="supported-lts-path",
            category="release-policy",
            status=UpgradeCheckStatus.PASS if supported else UpgradeCheckStatus.BLOCKED,
            detail=(
                f"{source.version} -> {target.version} is inside both published LTS windows"
                if supported
                else f"{source.version} -> {target.version} is outside a published LTS window"
            ),
            remediation=None if supported else "upgrade from a currently supported LTS release",
            evidence={
                "sourceSupportEndsOn": source.support_ends_on.isoformat(),
                "targetSupportEndsOn": target.support_ends_on.isoformat(),
            },
        )

    def _migration_checks(
        self,
        phase: UpgradePhase,
        source_boundary: str,
        target_boundary: str,
        inventory: UpgradeDatabaseInventory,
        rolling_declared: bool,
    ) -> tuple[UpgradeCheck, UpgradeCheck]:
        plan = migration_plan(migration_directory())
        filenames = [item.filename for item in plan]
        source_index = filenames.index(source_boundary)
        target_index = filenames.index(target_boundary)
        expected_checksums = {item.filename: item.checksum for item in plan}
        checksum_drift = [
            filename
            for filename, checksum in inventory.migration_checksums.items()
            if expected_checksums.get(filename) != checksum
        ]
        latest = inventory.applied_migrations[-1] if inventory.applied_migrations else None
        allowed_latest = (
            {target_boundary}
            if phase is UpgradePhase.POST_UPGRADE
            else {source_boundary, target_boundary}
        )
        schema_safe = latest in allowed_latest and not checksum_drift
        schema = UpgradeCheck(
            name="schema-and-checksums",
            category="schema",
            status=UpgradeCheckStatus.PASS if schema_safe else UpgradeCheckStatus.BLOCKED,
            detail=(
                f"database schema is {latest} with unchanged migration checksums"
                if schema_safe
                else f"database schema is {latest}; checksum drift: {checksum_drift or 'none'}"
            ),
            remediation=(
                None
                if schema_safe
                else f"restore the declared {source_boundary} boundary or apply through {target_boundary}"
            ),
            evidence={"latestMigration": latest, "checksumDrift": checksum_drift},
        )
        pending_start = source_index + 1 if latest == source_boundary else target_index + 1
        pending = plan[pending_start : target_index + 1]
        online = all(item.online_compatible and item.mode == "expand" for item in pending)
        migration_safe = not rolling_declared or online
        migration = UpgradeCheck(
            name="rolling-migration-contract",
            category="schema",
            status=(
                UpgradeCheckStatus.PASS if migration_safe else UpgradeCheckStatus.BLOCKED
            ),
            detail=(
                f"{len(pending)} pending migration(s) are expand-only and online-compatible"
                if online
                else "the pending migration set requires an exclusive maintenance window"
            ),
            remediation=(
                None
                if migration_safe
                else "drain all roles and follow each migration rollback procedure"
            ),
            evidence={"pendingMigrations": [item.filename for item in pending]},
        )
        return schema, migration

    def _plugin_check(self) -> UpgradeCheck:
        packages = self._plugins.snapshot.packages
        incompatible = [
            package
            for package in packages
            if package.status
            in {PluginLifecycleStatus.INCOMPATIBLE, PluginLifecycleStatus.QUARANTINED}
        ]
        details = [
            f"{package.source_location}: {', '.join(package.diagnostics) or package.status.value}"
            for package in incompatible
        ]
        return UpgradeCheck(
            name="plugin-compatibility",
            category="plugins",
            status=UpgradeCheckStatus.BLOCKED if incompatible else UpgradeCheckStatus.PASS,
            detail=(
                f"{len(packages)} package(s) satisfy the target platform/protocol contracts"
                if not incompatible
                else f"{len(incompatible)} plugin package(s) are incompatible"
            ),
            remediation=(
                None
                if not incompatible
                else "install target-compatible plugin versions or remove invalid discovery sources"
            ),
            evidence={"incompatible": details},
        )

    async def _flow_check(self) -> UpgradeCheck:
        documents = await self._repository.flow_documents()
        registry = self._plugins.resource_registry()
        invalid = await asyncio.to_thread(_invalid_flow_documents, documents, registry)
        return UpgradeCheck(
            name="flow-syntax",
            category="flows",
            status=UpgradeCheckStatus.BLOCKED if invalid else UpgradeCheckStatus.PASS,
            detail=(
                f"{len(documents)} unique stored flow definition(s) validate against the target DSL"
                if not invalid
                else f"{len(invalid)} stored flow revision(s) require migration"
            ),
            remediation=(
                None
                if not invalid
                else "run the explicit flow configuration migration tool and publish a new revision"
            ),
            evidence={"invalidFlows": invalid},
        )

    async def _storage_check(self) -> UpgradeCheck:
        try:
            tenants = await self._repository.tenant_slugs()
            reports = [
                await self._object_store.validate_inventory(tenant, verify_content=False)
                for tenant in tenants
            ]
        except Exception as exc:
            return UpgradeCheck(
                name="object-storage",
                category="storage",
                status=UpgradeCheckStatus.BLOCKED,
                detail=f"object-storage inventory failed with {exc.__class__.__name__}",
                remediation="restore object-store access before upgrading",
            )
        corrupt = [uri for report in reports for uri in report.corrupt]
        return UpgradeCheck(
            name="object-storage",
            category="storage",
            status=UpgradeCheckStatus.BLOCKED if corrupt else UpgradeCheckStatus.PASS,
            detail=(
                f"metadata inventory passed for {len(tenants)} tenant(s) and "
                f"{sum(report.objects for report in reports)} object(s)"
            ),
            remediation=None if not corrupt else "repair corrupt objects before upgrading",
            evidence={"corruptObjects": corrupt},
        )

    def _capacity_check(self, inventory: UpgradeDatabaseInventory) -> UpgradeCheck:
        limits = self._policy.capacity_thresholds
        exceeded = {
            name: value
            for name, value, limit in (
                ("databaseBytes", inventory.database_bytes, limits.maximum_database_bytes),
                ("queuedWork", inventory.queued_work, limits.maximum_queued_work),
                (
                    "activeExecutions",
                    inventory.active_executions,
                    limits.maximum_active_executions,
                ),
            )
            if value > limit
        }
        return UpgradeCheck(
            name="bounded-capacity",
            category="capacity",
            status=UpgradeCheckStatus.BLOCKED if exceeded else UpgradeCheckStatus.PASS,
            detail=(
                "database size, queued work and active executions are within upgrade thresholds"
                if not exceeded
                else f"upgrade capacity thresholds exceeded: {exceeded}"
            ),
            remediation=(
                None if not exceeded else "drain backlog or expand capacity before upgrading"
            ),
            evidence={
                "databaseBytes": inventory.database_bytes,
                "queuedWork": inventory.queued_work,
                "activeExecutions": inventory.active_executions,
            },
        )

    async def _service_skew_check(self, phase: UpgradePhase) -> UpgradeCheck:
        topology = await self._service_registry.topology()
        live = [item for item in topology.instances if item.liveness is ServiceLiveness.LIVE]
        unsafe = [
            item.instance_name
            for item in live
            if item.compatibility is ServiceCompatibility.UNSAFE
        ]
        rolling = [
            item.instance_name
            for item in live
            if item.compatibility is ServiceCompatibility.ROLLING_COMPATIBLE
        ]
        status = (
            UpgradeCheckStatus.BLOCKED
            if unsafe
            else UpgradeCheckStatus.WARNING
            if rolling
            else UpgradeCheckStatus.PASS
        )
        detail = (
            f"unsafe live service versions: {', '.join(unsafe)}"
            if unsafe
            else f"rolling-compatible old instances remain: {', '.join(rolling)}"
            if rolling
            else f"{len(live)} live service instance(s) use {self._policy.current_version}"
        )
        return UpgradeCheck(
            name="service-version-skew",
            category="services",
            status=status,
            detail=detail,
            remediation=(
                "replace unsafe versions before continuing"
                if unsafe
                else "drain each old instance after its replacement is ready"
                if rolling and phase is UpgradePhase.POST_UPGRADE
                else None
            ),
            evidence={"unsafeInstances": unsafe, "rollingInstances": rolling},
        )

    @staticmethod
    def _event_schema_check(
        phase: UpgradePhase,
        inventory: UpgradeDatabaseInventory,
    ) -> UpgradeCheck:
        if inventory.unsupported_execution_events:
            return UpgradeCheck(
                name="execution-event-schema",
                category="events",
                status=UpgradeCheckStatus.BLOCKED,
                detail=(
                    f"{inventory.unsupported_execution_events} event(s) use a newer unsupported schema"
                ),
                remediation="restore a compatible binary before reading newer persisted events",
            )
        legacy = inventory.legacy_execution_events
        status = (
            UpgradeCheckStatus.WARNING
            if legacy and phase is UpgradePhase.POST_UPGRADE
            else UpgradeCheckStatus.PASS
        )
        return UpgradeCheck(
            name="execution-event-schema",
            category="events",
            status=status,
            detail=(
                f"{legacy} historical event(s) remain readable through the v1-to-v2 upcaster"
                if legacy
                else "all persisted execution events use schema v2"
            ),
            remediation=(
                "preview and run the bounded persisted-event upcast tool" if legacy else None
            ),
            evidence={"legacyEvents": legacy},
        )


def _invalid_flow_documents(
    documents: tuple[Mapping[str, Any], ...],
    registry: ResourceSchemaRegistry,
) -> list[str]:
    invalid: list[str] = []
    for document in documents:
        result = validate_flow_document(dict(document), registry=registry)
        if not result.valid:
            namespace = document.get("namespace", "?")
            flow_id = document.get("id", "?")
            invalid.append(f"{namespace}.{flow_id}")
    return invalid


def _rolling_plan() -> tuple[RollingUpgradeStep, ...]:
    roles = ("indexer", "maintenance", "worker", "executor", "scheduler", "webserver")
    return tuple(
        RollingUpgradeStep(
            order=index,
            role=role,
            action=(
                "start one target instance, wait ready, request fenced drain, then stop old instance"
            ),
            verification="replacement heartbeat is READY and accepted work remains durable",
        )
        for index, role in enumerate(roles, start=1)
    )


def _report_fingerprint(
    phase: UpgradePhase,
    from_version: str,
    to_version: str,
    checks: list[UpgradeCheck],
) -> str:
    payload = {
        "phase": phase.value,
        "fromVersion": from_version,
        "toVersion": to_version,
        "checks": [check.model_dump(mode="json", by_alias=True) for check in checks],
    }
    return hashlib.sha256(_canonical_json(payload).encode()).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
