from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable, Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from semantic_version import SimpleSpec, Version  # type: ignore[import-untyped]

from amesh.dsl import FlowDefinition, compile_execution_tasks

from .catalog import (
    PluginCatalogSnapshot,
    PluginLifecycleStatus,
    PluginPackageRecord,
    PluginSourceKind,
)
from .errors import PluginContractError, PluginErrorDetail, PluginErrorPhase
from .manifest import ExtensionType

PLUGIN_RESOLUTION_VERSION = "amesh.plugin-resolution/v1"


class PluginTypeReference(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: ExtensionType
    type: str = Field(min_length=1, max_length=255)
    version_range: str = Field(default="*", alias="versionRange", min_length=1, max_length=128)


class PluginPackagePin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    name: str
    version: str
    content_digest: str = Field(alias="contentDigest")
    source_kind: PluginSourceKind = Field(alias="sourceKind")
    dependencies: tuple[str, ...] = ()


class PluginResourcePin(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: ExtensionType
    type: str
    package: str
    version: str
    content_digest: str = Field(alias="contentDigest")


class PluginResolution(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: Literal["amesh.plugin-resolution/v1"] = Field(
        default="amesh.plugin-resolution/v1",
        alias="schemaVersion",
    )
    catalog_digest: str = Field(alias="catalogDigest")
    resolution_digest: str = Field(alias="resolutionDigest")
    packages: tuple[PluginPackagePin, ...]
    resources: tuple[PluginResourcePin, ...]

    def revision_payload(self) -> dict[str, object]:
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class PluginIsolationPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    package: PluginPackagePin
    content_root: str = Field(alias="contentRoot")
    dependency_roots: Mapping[str, str] = Field(alias="dependencyRoots")
    environment: Mapping[str, str]


class PluginResolver:
    """Backtracking SemVer resolver over one immutable catalog snapshot."""

    def __init__(self, snapshot: PluginCatalogSnapshot) -> None:
        self._snapshot = snapshot
        self._available = tuple(
            record
            for record in snapshot.packages
            if record.manifest is not None
            and record.content_digest is not None
            and record.status in {PluginLifecycleStatus.ACTIVE, PluginLifecycleStatus.INSTALLED}
        )

    def resolve(self, references: Iterable[PluginTypeReference]) -> PluginResolution:
        requested = tuple(
            sorted(
                set(references),
                key=lambda item: (item.kind.value, item.type, item.version_range),
            )
        )
        constraints: dict[str, tuple[str, ...]] = {}
        resource_packages: dict[tuple[ExtensionType, str], str] = {}
        for reference in requested:
            try:
                SimpleSpec(reference.version_range)
            except ValueError as exc:
                raise _resolution_error(
                    "plugin.resolution.invalid_range",
                    f"invalid version range {reference.version_range!r}",
                    details={"kind": reference.kind.value, "type": reference.type},
                ) from exc
            providers = {
                record.manifest.name
                for record in self._available
                if record.manifest is not None
                and any(
                    entry.type is reference.kind and entry.resolved_resource_type == reference.type
                    for entry in record.manifest.entry_points
                )
            }
            if not providers:
                diagnostics = sorted(
                    {
                        diagnostic
                        for record in self._snapshot.packages
                        if record.manifest is not None
                        and any(
                            entry.type is reference.kind
                            and entry.resolved_resource_type == reference.type
                            for entry in record.manifest.entry_points
                        )
                        for diagnostic in record.diagnostics
                    }
                )
                raise _resolution_error(
                    "plugin.resolution.type_unavailable",
                    f"no active package provides {reference.kind.value}/{reference.type}",
                    details={"diagnostics": diagnostics},
                )
            if len(providers) != 1:
                raise _resolution_error(
                    "plugin.resolution.duplicate_type",
                    f"multiple packages provide {reference.kind.value}/{reference.type}",
                    details={"providers": sorted(providers)},
                )
            package_name = next(iter(providers))
            resource_packages[(reference.kind, reference.type)] = package_name
            constraints[package_name] = (
                *constraints.get(package_name, ()),
                reference.version_range,
            )

        selected = self._solve({}, constraints)
        if selected is None:
            raise _resolution_error(
                "plugin.resolution.dependency_conflict",
                "plugin dependency constraints cannot be satisfied",
                details={name: list(ranges) for name, ranges in sorted(constraints.items())},
            )

        package_pins = tuple(
            PluginPackagePin(
                name=name,
                version=record.manifest.version,
                contentDigest=record.content_digest,
                sourceKind=record.source_kind,
                dependencies=tuple(
                    sorted(
                        dependency.name
                        for dependency in record.manifest.dependencies
                        if not dependency.optional and dependency.name in selected
                    )
                ),
            )
            for name, record in sorted(selected.items())
            if record.manifest is not None and record.content_digest is not None
        )
        resource_pin_list: list[PluginResourcePin] = []
        for reference in requested:
            package_name = resource_packages[(reference.kind, reference.type)]
            record = selected[package_name]
            if record.manifest is None or record.content_digest is None:
                raise RuntimeError("resolved plugin package lost its immutable identity")
            resource_pin_list.append(
                PluginResourcePin(
                    kind=reference.kind,
                    type=reference.type,
                    package=package_name,
                    version=record.manifest.version,
                    contentDigest=record.content_digest,
                )
            )
        resource_pins = tuple(resource_pin_list)
        resolution_digest = _resolution_digest(package_pins, resource_pins)
        return PluginResolution(
            catalogDigest=self._snapshot.catalog_digest,
            resolutionDigest=resolution_digest,
            packages=package_pins,
            resources=resource_pins,
        )

    def resolve_flow(self, flow: FlowDefinition) -> PluginResolution:
        references = {
            PluginTypeReference(kind=ExtensionType.TASK, type=node.task.type)
            for node in compile_execution_tasks(flow)
        } | {
            PluginTypeReference(kind=ExtensionType.TRIGGER, type=trigger.type)
            for trigger in flow.triggers
        }
        return self.resolve(references)

    def _solve(
        self,
        selected: Mapping[str, PluginPackageRecord],
        constraints: Mapping[str, tuple[str, ...]],
    ) -> dict[str, PluginPackageRecord] | None:
        unresolved = sorted(set(constraints) - set(selected))
        if not unresolved:
            return dict(selected)
        package_name = min(
            unresolved,
            key=lambda name: (len(self._candidates(name, constraints[name])), name),
        )
        candidates = self._candidates(package_name, constraints[package_name])
        for candidate in candidates:
            if candidate.manifest is None:
                continue
            next_selected = dict(selected)
            next_selected[package_name] = candidate
            next_constraints = dict(constraints)
            valid = True
            for dependency in candidate.manifest.dependencies:
                if dependency.optional:
                    continue
                next_constraints[dependency.name] = (
                    *next_constraints.get(dependency.name, ()),
                    dependency.version_range,
                )
                pinned = next_selected.get(dependency.name)
                if (
                    pinned is not None
                    and pinned.manifest is not None
                    and not _matches_all(
                        pinned.manifest.version,
                        next_constraints[dependency.name],
                    )
                ):
                    valid = False
                    break
            if not valid:
                continue
            solved = self._solve(next_selected, next_constraints)
            if solved is not None:
                return solved
        return None

    def _candidates(
        self,
        name: str,
        ranges: Iterable[str],
    ) -> tuple[PluginPackageRecord, ...]:
        return tuple(
            sorted(
                (
                    record
                    for record in self._available
                    if record.manifest is not None
                    and record.manifest.name == name
                    and _matches_all(record.manifest.version, ranges)
                ),
                key=lambda record: (
                    Version(record.manifest.version),  # type: ignore[union-attr]
                    record.content_digest or "",
                ),
                reverse=True,
            )
        )


class PluginIsolationPlanner:
    """Builds per-pin launch roots without mutating control-plane import paths."""

    def __init__(self, snapshot: PluginCatalogSnapshot) -> None:
        self._packages = {
            (record.manifest.name, record.manifest.version, record.content_digest): record
            for record in snapshot.packages
            if record.manifest is not None and record.content_digest is not None
        }

    def plan(self, resolution: PluginResolution) -> tuple[PluginIsolationPlan, ...]:
        roots: dict[str, str] = {}
        for package in resolution.packages:
            record = self._packages.get((package.name, package.version, package.content_digest))
            if record is None or record.content_path is None:
                raise _resolution_error(
                    "plugin.isolation.content_unavailable",
                    f"content for {package.name}@{package.version} is unavailable",
                )
            roots[package.name] = record.content_path
        return tuple(
            PluginIsolationPlan(
                package=package,
                contentRoot=roots[package.name],
                dependencyRoots={name: roots[name] for name in package.dependencies},
                environment={
                    "AMESH_PLUGIN_PACKAGE_ROOT": roots[package.name],
                    "AMESH_PLUGIN_DEPENDENCY_ROOTS": os.pathsep.join(
                        roots[name] for name in package.dependencies
                    ),
                    "PYTHONNOUSERSITE": "1",
                },
            )
            for package in resolution.packages
        )


def _matches_all(version: str, ranges: Iterable[str]) -> bool:
    parsed = Version(version)
    return all(SimpleSpec(specification).match(parsed) for specification in ranges)


def _resolution_digest(
    packages: Iterable[PluginPackagePin],
    resources: Iterable[PluginResourcePin],
) -> str:
    payload = {
        "packages": [package.model_dump(mode="json", by_alias=True) for package in packages],
        "resources": [resource.model_dump(mode="json", by_alias=True) for resource in resources],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _resolution_error(
    code: str,
    message: str,
    *,
    details: Mapping[str, object] | None = None,
) -> PluginContractError:
    return PluginContractError(
        PluginErrorDetail(
            code=code,
            message=message,
            phase=PluginErrorPhase.COMPATIBILITY,
            hint="Install a compatible package or update the requested plugin constraints.",
            details=dict(details or {}),
        )
    )
