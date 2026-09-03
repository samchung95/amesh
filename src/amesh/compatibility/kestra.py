from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from importlib.resources import files
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field, JsonValue, TypeAdapter

from amesh.dsl import SourceRange, default_resource_registry, validate_flow_document
from amesh.dsl.registry import ResourceKind
from amesh.dsl.source import parse_editable_flow_document, parse_flow_source

KESTRA_TARGET_VERSION = "1.3.30"
KESTRA_TARGET_COMMIT = "db49f3b2c2af60d61df10adb6f9fc34e4776b65b"
IMPORTER_VERSION = "amesh.kestra-importer/v1"
MIGRATION_SCHEMA_VERSION = "amesh.kestra-migration/v1"


class MappingDisposition(StrEnum):
    EXACT = "exact"
    COMPATIBILITY_ADAPTED = "compatibility-adapted"
    BLOCKED = "blocked"


class SideEffectMode(StrEnum):
    SUPPRESS = "suppress"
    MOCK = "mock"
    IDEMPOTENT = "idempotent"


class CompatibilityMapping(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    path: str
    disposition: MappingDisposition
    target_path: str | None = Field(default=None, alias="targetPath")
    source_range: SourceRange | None = Field(default=None, alias="sourceRange")
    adapter: str | None = None
    message: str


class MigrationPatch(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    operation: str
    path: str
    target_path: str = Field(alias="targetPath")
    value: JsonValue = None
    source_range: SourceRange | None = Field(default=None, alias="sourceRange")
    reason: str


class KestraFlowImport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default=IMPORTER_VERSION, alias="schemaVersion")
    target_version: str = Field(default=KESTRA_TARGET_VERSION, alias="targetVersion")
    round_trip_document: str = Field(alias="roundTripDocument")
    candidate_document: dict[str, Any] = Field(alias="candidateDocument")
    semantic_hash: str = Field(alias="semanticHash")
    mappings: tuple[CompatibilityMapping, ...]
    patches: tuple[MigrationPatch, ...]
    valid: bool
    release_claim_allowed: bool = Field(alias="releaseClaimAllowed")

    @property
    def blockers(self) -> tuple[CompatibilityMapping, ...]:
        return tuple(
            item for item in self.mappings if item.disposition is MappingDisposition.BLOCKED
        )


_KESTRA_CORE_PREFIX = "io" + ".kestra.plugin.core."
_TASK_TYPE_MAP = {
    f"{_KESTRA_CORE_PREFIX}log.Log": "core.log",
    f"{_KESTRA_CORE_PREFIX}debug.Return": "core.return",
    f"{_KESTRA_CORE_PREFIX}debug.Fail": "core.fail",
    f"{_KESTRA_CORE_PREFIX}debug.Sleep": "core.sleep",
    f"{_KESTRA_CORE_PREFIX}flow.Sequential": "core.sequential",
    f"{_KESTRA_CORE_PREFIX}flow.Parallel": "core.parallel",
    f"{_KESTRA_CORE_PREFIX}flow.Dag": "core.dag",
    f"{_KESTRA_CORE_PREFIX}flow.ForEach": "core.foreach",
    f"{_KESTRA_CORE_PREFIX}flow.If": "core.if",
    f"{_KESTRA_CORE_PREFIX}flow.Switch": "core.switch",
    f"{_KESTRA_CORE_PREFIX}flow.Subflow": "core.subflow",
    f"{_KESTRA_CORE_PREFIX}flow.WorkingDirectory": "core.workingDirectory",
    f"{_KESTRA_CORE_PREFIX}flow.While": "core.while",
    f"{_KESTRA_CORE_PREFIX}flow.Until": "core.until",
    f"{_KESTRA_CORE_PREFIX}http.Request": "core.http",
}

_TRIGGER_TYPE_MAP = {
    f"{_KESTRA_CORE_PREFIX}trigger.Schedule": "core.cron",
    f"{_KESTRA_CORE_PREFIX}trigger.Interval": "core.interval",
    f"{_KESTRA_CORE_PREFIX}trigger.Webhook": "core.webhook",
    f"{_KESTRA_CORE_PREFIX}trigger.Flow": "core.flow",
}

_TOP_LEVEL_FIELDS = {
    "id",
    "namespace",
    "description",
    "revision",
    "disabled",
    "labels",
    "inputs",
    "variables",
    "concurrency",
    "priority",
    "tasks",
    "triggers",
    "outputs",
    "errors",
    "finally",
    "pluginDefaults",
}

_TASK_STRUCTURAL_FIELDS = {
    "id",
    "type",
    "description",
    "dependsOn",
    "runIf",
    "conditionErrorPolicy",
    "retry",
    "timeoutSeconds",
    "tasks",
    "then",
    "elseIf",
    "else",
    "cases",
    "predicateCases",
    "errors",
    "condition",
    "failurePolicy",
    "maxConcurrency",
    "priority",
}

_TRIGGER_STRUCTURAL_FIELDS = {"id", "type", "disabled", "paused"}
_DURATION = TypeAdapter(timedelta)


def import_kestra_flow(source: str | bytes) -> KestraFlowImport:
    """Build a source-located, loss-explicit migration candidate for the pinned target."""

    editable = parse_editable_flow_document(source)
    parsed = parse_flow_source(source)
    candidate = copy.deepcopy(parsed.data)
    mappings: dict[str, CompatibilityMapping] = {}
    patches: list[MigrationPatch] = []

    def record(
        path: Sequence[str | int],
        disposition: MappingDisposition,
        message: str,
        *,
        target_path: Sequence[str | int] | None = None,
        adapter: str | None = None,
    ) -> None:
        pointer = _pointer(path)
        mappings[pointer] = CompatibilityMapping(
            path=pointer,
            disposition=disposition,
            targetPath=_pointer(target_path) if target_path is not None else pointer,
            sourceRange=parsed.source_map.range_for(path)
            if parsed.source_map is not None
            else None,
            adapter=adapter,
            message=message,
        )

    def add_patch(
        path: Sequence[str | int],
        target_path: Sequence[str | int],
        value: Any,
        reason: str,
        *,
        operation: str = "replace",
    ) -> None:
        patches.append(
            MigrationPatch(
                operation=operation,
                path=_pointer(path),
                targetPath=_pointer(target_path),
                value=value,
                sourceRange=(
                    parsed.source_map.range_for(path) if parsed.source_map is not None else None
                ),
                reason=reason,
            )
        )

    def adapt(
        container: dict[str, Any],
        source_key: str,
        target_key: str,
        path: tuple[str | int, ...],
        value: Any,
        adapter: str,
    ) -> None:
        del container[source_key]
        container[target_key] = value
        source_path = (*path, source_key)
        target_path = (*path, target_key)
        record(
            source_path,
            MappingDisposition.COMPATIBILITY_ADAPTED,
            f"{source_key} is represented as {target_key}",
            target_path=target_path,
            adapter=adapter,
        )
        add_patch(
            source_path,
            target_path,
            value,
            f"pinned {adapter} mapping",
            operation="move-and-replace",
        )

    for key in tuple(candidate):
        path = (key,)
        if key in _TOP_LEVEL_FIELDS:
            record(path, MappingDisposition.EXACT, "field is accepted without semantic change")
        else:
            record(
                path,
                MappingDisposition.BLOCKED,
                "field is outside the declared Kestra 1.3.30 flow mapping",
            )

    if isinstance(candidate.get("labels"), list):
        try:
            labels = {
                str(item["key"]): str(item["value"])
                for item in candidate["labels"]
                if isinstance(item, Mapping)
            }
            if len(labels) != len(candidate["labels"]):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            record(("labels",), MappingDisposition.BLOCKED, "labels must contain key/value pairs")
        else:
            candidate["labels"] = labels
            record(
                ("labels",),
                MappingDisposition.COMPATIBILITY_ADAPTED,
                "label entries are represented by the canonical label object",
                adapter="label-list/v1",
            )
            add_patch(("labels",), ("labels",), labels, "pinned label-list/v1 mapping")

    if isinstance(candidate.get("outputs"), list):
        outputs: dict[str, Any] = {}
        invalid_output = False
        for item in candidate["outputs"]:
            if not isinstance(item, Mapping) or not isinstance(item.get("id"), str):
                invalid_output = True
                break
            outputs[str(item["id"])] = item.get("value")
        if invalid_output:
            record(
                ("outputs",), MappingDisposition.BLOCKED, "outputs require stable id/value entries"
            )
        else:
            candidate["outputs"] = outputs
            record(
                ("outputs",),
                MappingDisposition.COMPATIBILITY_ADAPTED,
                "typed output entries are represented by the canonical output object",
                adapter="output-list/v1",
            )
            add_patch(("outputs",), ("outputs",), outputs, "pinned output-list/v1 mapping")

    if isinstance(candidate.get("concurrency"), Mapping):
        concurrency = candidate["concurrency"]
        allowed_concurrency = {"limit", "behavior"}
        unknown_concurrency = sorted(set(concurrency) - allowed_concurrency)
        if unknown_concurrency:
            for key in unknown_concurrency:
                record(
                    ("concurrency", key),
                    MappingDisposition.BLOCKED,
                    "concurrency property is outside the declared adapter",
                )
        limit = concurrency.get("limit")
        behavior = str(concurrency.get("behavior", "QUEUE")).upper()
        if not isinstance(limit, int) or limit < 1:
            record(
                ("concurrency", "limit"),
                MappingDisposition.BLOCKED,
                "concurrency limit must be a positive integer",
            )
        elif behavior not in {"QUEUE", "CANCEL", "FAIL"}:
            record(
                ("concurrency", "behavior"),
                MappingDisposition.BLOCKED,
                f"concurrency behavior {behavior!r} has no declared adapter",
            )
        elif not unknown_concurrency:
            adapt(
                candidate,
                "concurrency",
                "concurrency",
                (),
                [
                    {
                        "id": "kestra-flow-concurrency",
                        "scope": "FLOW",
                        "limit": limit,
                        "behavior": behavior,
                    }
                ],
                "flow-concurrency/v1",
            )

    _map_task_collection(candidate.get("tasks"), ("tasks",), record, adapt, add_patch)
    _map_task_collection(candidate.get("errors"), ("errors",), record, adapt, add_patch)
    _map_task_collection(candidate.get("finally"), ("finally",), record, adapt, add_patch)
    _map_triggers(candidate.get("triggers"), record, add_patch)

    validation = validate_flow_document(candidate, registry=default_resource_registry())
    for issue in validation.issues:
        if issue.severity == "error":
            issue_path = (
                issue.path if issue.path.startswith("/") else "/" + issue.path.replace(".", "/")
            )
            mappings.setdefault(
                issue_path,
                CompatibilityMapping(
                    path=issue_path,
                    disposition=MappingDisposition.BLOCKED,
                    targetPath=issue_path,
                    sourceRange=issue.source_range,
                    message=f"target validation: {issue.code}: {issue.message}",
                ),
            )

    blockers = any(item.disposition is MappingDisposition.BLOCKED for item in mappings.values())
    canonical = copy.deepcopy(
        validation.canonical if validation.canonical is not None else candidate
    )
    _preserve_declared_resource_presence(canonical, candidate)
    return KestraFlowImport(
        roundTripDocument=editable.render(),
        candidateDocument=canonical,
        semanticHash=_sha256(canonical),
        mappings=tuple(mappings[key] for key in sorted(mappings)),
        patches=tuple(sorted(patches, key=lambda item: (item.path, item.target_path))),
        valid=validation.valid and not blockers,
        releaseClaimAllowed=False,
    )


def _preserve_declared_resource_presence(
    canonical: dict[str, Any],
    declared: Mapping[str, Any],
) -> None:
    _prune_generated_resource_fields(canonical, declared)


def _prune_generated_resource_fields(canonical: Any, declared: Any) -> None:
    if isinstance(canonical, list) and isinstance(declared, list):
        for canonical_item, declared_item in zip(canonical, declared, strict=False):
            _prune_generated_resource_fields(canonical_item, declared_item)
        return
    if not isinstance(canonical, dict) or not isinstance(declared, Mapping):
        return
    if isinstance(declared.get("id"), str) and isinstance(declared.get("type"), str):
        for key in tuple(canonical):
            if key not in declared:
                del canonical[key]
    for key in canonical.keys() & declared.keys():
        _prune_generated_resource_fields(canonical[key], declared[key])


def _map_task_collection(
    value: Any,
    path: tuple[str | int, ...],
    record: Any,
    adapt: Any,
    add_patch: Any,
) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        record(path, MappingDisposition.BLOCKED, "task collection must be a list")
        return
    for index, item in enumerate(value):
        item_path = (*path, index)
        if not isinstance(item, dict):
            record(item_path, MappingDisposition.BLOCKED, "task entry must be an object")
            continue
        source_type = item.get("type")
        target_type = _TASK_TYPE_MAP.get(source_type) if isinstance(source_type, str) else None
        if target_type is None:
            if isinstance(source_type, str) and source_type.startswith("core."):
                target_type = source_type
                record((*item_path, "type"), MappingDisposition.EXACT, "native core type is exact")
            else:
                record(
                    (*item_path, "type"),
                    MappingDisposition.BLOCKED,
                    f"task type {source_type!r} has no declared non-destructive adapter",
                )
        else:
            item["type"] = target_type
            record(
                (*item_path, "type"),
                MappingDisposition.COMPATIBILITY_ADAPTED,
                f"task type is served by {target_type}",
                adapter="core-task-type/v1",
            )
            add_patch(
                (*item_path, "type"),
                (*item_path, "type"),
                target_type,
                "pinned core-task-type/v1 mapping",
            )

        if "timeout" in item:
            try:
                seconds = _duration_seconds(item["timeout"])
            except ValueError as exc:
                record((*item_path, "timeout"), MappingDisposition.BLOCKED, str(exc))
            else:
                adapt(item, "timeout", "timeoutSeconds", item_path, seconds, "duration-seconds/v1")
        if "retry" in item and isinstance(item["retry"], dict):
            _map_retry(item["retry"], (*item_path, "retry"), record, adapt, add_patch)
        if target_type == "core.return" and "format" in item:
            adapt(item, "format", "value", item_path, item["format"], "core-return/v1")
        if target_type == "core.http" and "uri" in item:
            adapt(item, "uri", "url", item_path, item["uri"], "core-http-uri/v1")
        if target_type == "core.sleep" and "duration" in item:
            try:
                seconds = _duration_seconds(item["duration"])
            except ValueError as exc:
                record((*item_path, "duration"), MappingDisposition.BLOCKED, str(exc))
            else:
                adapt(item, "duration", "seconds", item_path, seconds, "duration-seconds/v1")
        if target_type == "core.foreach" and "values" in item:
            adapt(item, "values", "items", item_path, item["values"], "foreach-values/v1")

        allowed = set(_TASK_STRUCTURAL_FIELDS)
        if target_type is not None:
            descriptor = default_resource_registry().descriptor(ResourceKind.TASK, target_type)
            if descriptor is not None:
                allowed.update(descriptor.configuration_schema.get("properties", {}))
        for key in tuple(item):
            field_path = (*item_path, key)
            if key not in allowed:
                record(
                    field_path,
                    MappingDisposition.BLOCKED,
                    f"property is not declared for target task type {target_type!r}",
                )
            elif key != "type":
                record(
                    field_path,
                    MappingDisposition.EXACT,
                    "property is accepted without semantic change",
                )
        for child_key in ("tasks", "errors", "then", "else"):
            _map_task_collection(
                item.get(child_key), (*item_path, child_key), record, adapt, add_patch
            )
        for branch_key in ("elseIf", "predicateCases"):
            branches = item.get(branch_key)
            if isinstance(branches, list):
                for branch_index, branch in enumerate(branches):
                    if isinstance(branch, dict):
                        _map_task_collection(
                            branch.get("tasks"),
                            (*item_path, branch_key, branch_index, "tasks"),
                            record,
                            adapt,
                            add_patch,
                        )
        cases = item.get("cases")
        if isinstance(cases, dict):
            for case_name, tasks in cases.items():
                _map_task_collection(
                    tasks, (*item_path, "cases", str(case_name)), record, adapt, add_patch
                )


def _map_retry(
    value: dict[str, Any],
    path: tuple[str | int, ...],
    record: Any,
    adapt: Any,
    add_patch: Any,
) -> None:
    if "maxAttempt" in value:
        adapt(value, "maxAttempt", "maxAttempts", path, value["maxAttempt"], "retry/v1")
    for source_key, target_key in (
        ("interval", "delaySeconds"),
        ("maxInterval", "maxIntervalSeconds"),
    ):
        if source_key in value:
            try:
                seconds = _duration_seconds(value[source_key])
            except ValueError as exc:
                record((*path, source_key), MappingDisposition.BLOCKED, str(exc))
            else:
                adapt(value, source_key, target_key, path, seconds, "retry-duration/v1")
    retry_type = value.get("type")
    if retry_type is not None:
        normalized_type = str(retry_type).casefold()
        delay_factor = value.get("delayFactor")
        multiplier: float | None = None
        if normalized_type == "constant" and delay_factor is None:
            multiplier = 1.0
        elif normalized_type == "exponential" and (
            delay_factor is None or (isinstance(delay_factor, (int, float)) and delay_factor >= 1)
        ):
            multiplier = float(delay_factor or 2.0)
        if multiplier is None:
            record((*path, "type"), MappingDisposition.BLOCKED, "retry type has no exact adapter")
        else:
            del value["type"]
            if delay_factor is not None:
                del value["delayFactor"]
            value["backoffMultiplier"] = multiplier
            record(
                (*path, "type"),
                MappingDisposition.COMPATIBILITY_ADAPTED,
                "retry type is represented by backoffMultiplier",
                target_path=(*path, "backoffMultiplier"),
                adapter="retry-backoff/v1",
            )
            add_patch(
                (*path, "type"),
                (*path, "backoffMultiplier"),
                multiplier,
                "pinned retry-backoff/v1 mapping",
                operation="move-and-replace",
            )
            if delay_factor is not None:
                record(
                    (*path, "delayFactor"),
                    MappingDisposition.COMPATIBILITY_ADAPTED,
                    "delayFactor is represented by backoffMultiplier",
                    target_path=(*path, "backoffMultiplier"),
                    adapter="retry-backoff/v1",
                )
                add_patch(
                    (*path, "delayFactor"),
                    (*path, "backoffMultiplier"),
                    multiplier,
                    "pinned retry-backoff/v1 mapping",
                    operation="move-and-replace",
                )
    allowed = {
        "maxAttempts",
        "delaySeconds",
        "backoffMultiplier",
        "maxIntervalSeconds",
        "jitterRatio",
        "condition",
        "conditionErrorPolicy",
    }
    for key in value:
        if key not in allowed:
            record((*path, key), MappingDisposition.BLOCKED, "retry property is not mapped")
        else:
            record(
                (*path, key),
                MappingDisposition.EXACT,
                "retry property is accepted without semantic change",
            )


def _map_triggers(value: Any, record: Any, add_patch: Any) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        record(("triggers",), MappingDisposition.BLOCKED, "trigger collection must be a list")
        return
    for index, item in enumerate(value):
        path = ("triggers", index)
        if not isinstance(item, dict):
            record(path, MappingDisposition.BLOCKED, "trigger entry must be an object")
            continue
        source_type = item.get("type")
        target_type = _TRIGGER_TYPE_MAP.get(source_type) if isinstance(source_type, str) else None
        if target_type is None:
            if isinstance(source_type, str) and source_type.startswith("core."):
                target_type = source_type
                record((*path, "type"), MappingDisposition.EXACT, "native trigger type is exact")
            else:
                record(
                    (*path, "type"),
                    MappingDisposition.BLOCKED,
                    f"trigger type {source_type!r} has no declared adapter",
                )
        else:
            item["type"] = target_type
            record(
                (*path, "type"),
                MappingDisposition.COMPATIBILITY_ADAPTED,
                f"trigger type is served by {target_type}",
                adapter="core-trigger-type/v1",
            )
            add_patch(
                (*path, "type"),
                (*path, "type"),
                target_type,
                "pinned core-trigger-type/v1 mapping",
            )
        allowed = set(_TRIGGER_STRUCTURAL_FIELDS)
        if target_type is not None:
            descriptor = default_resource_registry().descriptor(ResourceKind.TRIGGER, target_type)
            if descriptor is not None:
                allowed.update(descriptor.configuration_schema.get("properties", {}))
        for key in item:
            if key not in allowed:
                record(
                    (*path, key),
                    MappingDisposition.BLOCKED,
                    f"property is not declared for target trigger type {target_type!r}",
                )
            elif key != "type":
                record(
                    (*path, key),
                    MappingDisposition.EXACT,
                    "trigger property is accepted without semantic change",
                )


class MigrationResourceKind(StrEnum):
    FLOW = "flow"
    NAMESPACE = "namespace"
    NAMESPACE_FILE = "namespace_file"
    KEY_VALUE = "key_value"
    LABEL = "label"
    REVISION = "revision"
    DASHBOARD = "dashboard"
    EXPORT_RESOURCE = "export_resource"
    USER = "user"
    GROUP = "group"
    ROLE = "role"
    BINDING = "binding"
    SERVICE_ACCOUNT = "service_account"
    TENANT = "tenant"
    SYSTEM_CONFIGURATION = "system_configuration"
    PLUGIN_INVENTORY = "plugin_inventory"
    AUDIT_CONFIGURATION = "audit_configuration"
    EXECUTION = "execution"
    TASK_RUN = "task_run"
    STATE_EVENT = "state_event"
    LOG = "log"
    METRIC = "metric"
    ARTIFACT = "artifact"
    AUDIT_EVENT = "audit_event"


class SecretReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: str
    key: str
    binding: str
    required: bool = True


class MigrationRecord(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: MigrationResourceKind
    source_id: str = Field(alias="sourceId")
    target_id: str = Field(alias="targetId")
    tenant: str
    namespace: str | None = None
    occurred_at: datetime | None = Field(default=None, alias="occurredAt")
    payload: dict[str, Any]
    references: tuple[str, ...] = ()
    secret_references: tuple[SecretReference, ...] = Field(default=(), alias="secretReferences")
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")

    @classmethod
    def create(
        cls,
        *,
        kind: MigrationResourceKind,
        source_id: str,
        tenant: str,
        payload: Mapping[str, Any],
        source_fingerprint: str,
        namespace: str | None = None,
        occurred_at: datetime | None = None,
        references: Sequence[str] = (),
        secret_references: Sequence[SecretReference] = (),
    ) -> MigrationRecord:
        target_id = str(uuid5(NAMESPACE_URL, f"{source_fingerprint}:{kind.value}:{source_id}"))
        unsigned = cls(
            kind=kind,
            sourceId=source_id,
            targetId=target_id,
            tenant=tenant,
            namespace=namespace,
            occurredAt=occurred_at,
            payload=copy.deepcopy(dict(payload)),
            references=tuple(references),
            secretReferences=tuple(secret_references),
            checksumSha256="0" * 64,
        )
        checksum = _sha256(
            unsigned.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
        )
        return unsigned.model_copy(update={"checksum_sha256": checksum})

    def verify(self) -> None:
        if self.checksum_sha256 != _sha256(
            self.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
        ):
            raise ValueError(f"record {self.source_id!r} checksum is invalid")


class IdentifierMapping(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    kind: MigrationResourceKind
    source_id: str = Field(alias="sourceId")
    target_id: str = Field(alias="targetId")
    mapping_version: int = Field(default=1, alias="mappingVersion")


class MigrationBundle(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_version: str = Field(default=MIGRATION_SCHEMA_VERSION, alias="schemaVersion")
    source_product: str = Field(default="Kestra", alias="sourceProduct")
    source_version: str = Field(default=KESTRA_TARGET_VERSION, alias="sourceVersion")
    source_fingerprint: str = Field(alias="sourceFingerprint")
    created_at: datetime = Field(alias="createdAt")
    records: tuple[MigrationRecord, ...]
    identifier_map: tuple[IdentifierMapping, ...] = Field(alias="identifierMap")
    checksum_sha256: str = Field(alias="checksumSha256", pattern=r"^[0-9a-f]{64}$")

    @classmethod
    def create(
        cls,
        *,
        source_fingerprint: str,
        records: Sequence[MigrationRecord],
        created_at: datetime | None = None,
    ) -> MigrationBundle:
        ordered = tuple(records)
        identifier_map = tuple(
            IdentifierMapping(kind=item.kind, sourceId=item.source_id, targetId=item.target_id)
            for item in ordered
        )
        effective_created_at = created_at or datetime.now(UTC)
        unsigned = cls(
            sourceFingerprint=source_fingerprint,
            createdAt=effective_created_at,
            records=ordered,
            identifierMap=identifier_map,
            checksumSha256="0" * 64,
        )
        checksum = _sha256(
            unsigned.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
        )
        return unsigned.model_copy(update={"checksum_sha256": checksum})

    def verify(self) -> None:
        for record in self.records:
            record.verify()
        if self.checksum_sha256 != _sha256(
            self.model_dump(mode="json", by_alias=True, exclude={"checksum_sha256"})
        ):
            raise ValueError("migration bundle checksum is invalid")


class MigrationPlanIssue(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    code: str
    message: str
    source_id: str | None = Field(default=None, alias="sourceId")
    blocking: bool = True


class MigrationPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    bundle_checksum: str = Field(alias="bundleChecksum")
    dry_run: bool = Field(default=True, alias="dryRun")
    record_count: int = Field(alias="recordCount", ge=0)
    identifier_count: int = Field(alias="identifierCount", ge=0)
    issues: tuple[MigrationPlanIssue, ...]
    side_effect_mode: SideEffectMode = Field(
        default=SideEffectMode.SUPPRESS, alias="sideEffectMode"
    )
    cutover_allowed: bool = Field(alias="cutoverAllowed")
    cutover_steps: tuple[str, ...] = Field(alias="cutoverSteps")
    rollback_steps: tuple[str, ...] = Field(alias="rollbackSteps")


def plan_migration(
    bundle: MigrationBundle,
    *,
    resolved_secret_bindings: set[str] | None = None,
) -> MigrationPlan:
    issues: list[MigrationPlanIssue] = []
    try:
        bundle.verify()
    except ValueError as exc:
        issues.append(MigrationPlanIssue(code="CHECKSUM_INVALID", message=str(exc)))
    records = {item.source_id: item for item in bundle.records}
    if len(records) != len(bundle.records):
        issues.append(
            MigrationPlanIssue(code="DUPLICATE_SOURCE_ID", message="source IDs must be unique")
        )
    target_ids = {item.target_id for item in bundle.records}
    if len(target_ids) != len(bundle.records):
        issues.append(
            MigrationPlanIssue(code="DUPLICATE_TARGET_ID", message="target IDs must be unique")
        )
    expected_map = tuple(
        IdentifierMapping(kind=item.kind, sourceId=item.source_id, targetId=item.target_id)
        for item in bundle.records
    )
    if bundle.identifier_map != expected_map:
        issues.append(
            MigrationPlanIssue(
                code="IDENTIFIER_MAP_MISMATCH",
                message="identifier map must match every bundle record in source order",
            )
        )
    for record in bundle.records:
        expected_target_id = str(
            uuid5(
                NAMESPACE_URL,
                f"{bundle.source_fingerprint}:{record.kind.value}:{record.source_id}",
            )
        )
        if record.target_id != expected_target_id:
            issues.append(
                MigrationPlanIssue(
                    code="TARGET_IDENTIFIER_INVALID",
                    message="target identifier does not match the stable mapping policy",
                    sourceId=record.source_id,
                )
            )
        for reference in record.references:
            target = records.get(reference)
            if target is None:
                issues.append(
                    MigrationPlanIssue(
                        code="REFERENCE_MISSING",
                        message=f"reference {reference!r} is absent",
                        sourceId=record.source_id,
                    )
                )
            elif target.tenant != record.tenant:
                issues.append(
                    MigrationPlanIssue(
                        code="TENANT_REFERENCE_CROSSING",
                        message=f"reference {reference!r} crosses tenant boundaries",
                        sourceId=record.source_id,
                    )
                )
        for path in _secret_plaintext_paths(record.payload):
            issues.append(
                MigrationPlanIssue(
                    code="SECRET_PLAINTEXT",
                    message=f"secret-like field {path} contains plaintext",
                    sourceId=record.source_id,
                )
            )
        for secret in record.secret_references:
            if secret.required and secret.binding not in (resolved_secret_bindings or set()):
                issues.append(
                    MigrationPlanIssue(
                        code="SECRET_BINDING_UNRESOLVED",
                        message=f"required binding {secret.binding!r} is unresolved",
                        sourceId=record.source_id,
                    )
                )
    _validate_chronology(bundle.records, issues)
    blocked = any(item.blocking for item in issues)
    return MigrationPlan(
        bundleChecksum=bundle.checksum_sha256,
        recordCount=len(bundle.records),
        identifierCount=len(bundle.identifier_map),
        issues=tuple(issues),
        cutoverAllowed=not blocked,
        cutoverSteps=(
            "freeze source mutations and export the final delta",
            "resume import from the last acknowledged checkpoint",
            "reconcile counts, identifiers, chronology and checksums",
            "resolve mandatory secrets and enable workers then triggers",
        ),
        rollbackSteps=(
            "disable target triggers and workers",
            "retain source as read-only system of record",
            "export imported identifiers and external-action evidence",
            "resume source from the recorded final checkpoint",
        ),
    )


class MigrationCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    bundle_checksum: str = Field(alias="bundleChecksum")
    next_index: int = Field(default=0, alias="nextIndex", ge=0)
    applied_source_ids: tuple[str, ...] = Field(default=(), alias="appliedSourceIds")


class MigrationImportResult(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    checkpoint: MigrationCheckpoint
    imported: int = Field(ge=0)
    skipped: int = Field(ge=0)
    complete: bool


class FileMigrationStore:
    """Idempotent side-by-side staging store for resumable migration records."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.records = root / "records"
        self.records.mkdir(parents=True, exist_ok=True)

    def upsert(self, record: MigrationRecord) -> bool:
        path = self.records / f"{record.target_id}.json"
        document = record.model_dump_json(indent=2, by_alias=True) + "\n"
        if path.exists():
            existing = MigrationRecord.model_validate_json(path.read_text(encoding="utf-8"))
            if existing.checksum_sha256 != record.checksum_sha256:
                raise ValueError(f"target identifier collision for {record.target_id}")
            return False
        temporary = path.with_suffix(".tmp")
        temporary.write_text(document, encoding="utf-8", newline="\n")
        temporary.replace(path)
        return True

    def load(self) -> tuple[MigrationRecord, ...]:
        return tuple(
            MigrationRecord.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.records.glob("*.json"))
        )

    def write_checkpoint(self, checkpoint: MigrationCheckpoint) -> None:
        path = self.root / "checkpoint.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            checkpoint.model_dump_json(indent=2, by_alias=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(path)

    def read_checkpoint(self) -> MigrationCheckpoint | None:
        path = self.root / "checkpoint.json"
        if not path.exists():
            return None
        return MigrationCheckpoint.model_validate_json(path.read_text(encoding="utf-8"))


class MigrationImporter:
    def __init__(self, store: FileMigrationStore) -> None:
        self.store = store

    def import_bundle(
        self,
        bundle: MigrationBundle,
        *,
        resolved_secret_bindings: set[str] | None = None,
        max_records: int | None = None,
    ) -> MigrationImportResult:
        if max_records is not None and max_records < 1:
            raise ValueError("max_records must be a positive integer")
        plan = plan_migration(bundle, resolved_secret_bindings=resolved_secret_bindings)
        if not plan.cutover_allowed:
            raise ValueError("migration plan contains blocking issues")
        checkpoint = self.store.read_checkpoint() or MigrationCheckpoint(
            bundleChecksum=bundle.checksum_sha256
        )
        if checkpoint.bundle_checksum != bundle.checksum_sha256:
            raise ValueError("checkpoint belongs to a different migration bundle")
        expected_applied = tuple(item.source_id for item in bundle.records[: checkpoint.next_index])
        if checkpoint.next_index > len(bundle.records) or (
            checkpoint.applied_source_ids != expected_applied
        ):
            raise ValueError("checkpoint does not match the bundle record sequence")
        imported = 0
        skipped = 0
        applied = list(checkpoint.applied_source_ids)
        stop = len(bundle.records)
        if max_records is not None:
            stop = min(stop, checkpoint.next_index + max_records)
        for index in range(checkpoint.next_index, stop):
            record = bundle.records[index]
            if self.store.upsert(record):
                imported += 1
            else:
                skipped += 1
            applied.append(record.source_id)
            checkpoint = MigrationCheckpoint(
                bundleChecksum=bundle.checksum_sha256,
                nextIndex=index + 1,
                appliedSourceIds=tuple(applied),
            )
            self.store.write_checkpoint(checkpoint)
        return MigrationImportResult(
            checkpoint=checkpoint,
            imported=imported,
            skipped=skipped,
            complete=checkpoint.next_index == len(bundle.records),
        )

    def reconcile(self, bundle: MigrationBundle) -> tuple[MigrationPlanIssue, ...]:
        expected = {item.target_id: item.checksum_sha256 for item in bundle.records}
        actual = {item.target_id: item.checksum_sha256 for item in self.store.load()}
        issues = [
            MigrationPlanIssue(
                code="TARGET_RECORD_MISSING",
                message=f"target record {target_id} is absent",
                sourceId=target_id,
            )
            for target_id in sorted(expected.keys() - actual.keys())
        ]
        issues.extend(
            MigrationPlanIssue(
                code="TARGET_CHECKSUM_MISMATCH",
                message=f"target record {target_id} differs from source",
                sourceId=target_id,
            )
            for target_id in sorted(expected.keys() & actual.keys())
            if expected[target_id] != actual[target_id]
        )
        return tuple(issues)


class ConformanceObservation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    system: str
    target_version: str = Field(alias="targetVersion")
    validation_class: str = Field(alias="validationClass")
    state_sequence: tuple[str, ...] = Field(alias="stateSequence")
    task_graph: tuple[tuple[str, tuple[str, ...]], ...] = Field(alias="taskGraph")
    outputs: dict[str, Any]
    api_payload: dict[str, Any] = Field(alias="apiPayload")
    cli_exit_code: int = Field(alias="cliExitCode")
    cli_payload: dict[str, Any] = Field(alias="cliPayload")
    error_class: str | None = Field(default=None, alias="errorClass")
    duration_ms: float = Field(alias="durationMs", ge=0)
    side_effect_mode: SideEffectMode = Field(alias="sideEffectMode")


class ShadowTaskDecision(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    task_id: str = Field(alias="taskId")
    original_type: str = Field(alias="originalType")
    mode: SideEffectMode
    replacement_type: str | None = Field(default=None, alias="replacementType")
    reason: str
    blocking: bool = False


class ShadowExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    mode: SideEffectMode
    candidate_document: dict[str, Any] = Field(alias="candidateDocument")
    decisions: tuple[ShadowTaskDecision, ...]
    executable: bool


_SIDE_EFFECTING_TASK_TYPES = frozenset(
    {
        "agent.llm",
        "agent.mcp",
        "core.download",
        "core.email",
        "core.http",
        "core.shell",
        "core.upload",
        "script.javascript",
        "script.node",
        "script.python",
    }
)


def plan_shadow_execution(
    imported: KestraFlowImport,
    *,
    mode: SideEffectMode,
    mock_outputs: Mapping[str, JsonValue] | None = None,
) -> ShadowExecutionPlan:
    """Create an executable AMESH shadow candidate with controlled external effects."""

    document = copy.deepcopy(imported.candidate_document)
    decisions: list[ShadowTaskDecision] = []
    if not imported.valid:
        decisions.append(
            ShadowTaskDecision(
                taskId="<flow>",
                originalType="<invalid>",
                mode=mode,
                reason="flow import contains blocked mappings",
                blocking=True,
            )
        )
    else:
        for collection_name in ("tasks", "errors", "finally"):
            _plan_shadow_tasks(
                document.get(collection_name),
                mode=mode,
                mock_outputs=mock_outputs or {},
                decisions=decisions,
            )
    validation = validate_flow_document(document, registry=default_resource_registry())
    for issue in validation.issues:
        if issue.severity == "error":
            decisions.append(
                ShadowTaskDecision(
                    taskId=issue.path,
                    originalType="<validation>",
                    mode=mode,
                    reason=f"{issue.code}: {issue.message}",
                    blocking=True,
                )
            )
    return ShadowExecutionPlan(
        mode=mode,
        candidateDocument=(validation.canonical or document),
        decisions=tuple(decisions),
        executable=validation.valid and not any(item.blocking for item in decisions),
    )


def _plan_shadow_tasks(
    tasks: Any,
    *,
    mode: SideEffectMode,
    mock_outputs: Mapping[str, JsonValue],
    decisions: list[ShadowTaskDecision],
) -> None:
    if not isinstance(tasks, list):
        return
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = str(task.get("id", "<unknown>"))
        task_type = str(task.get("type", "<unknown>"))
        if task_type in _SIDE_EFFECTING_TASK_TYPES:
            if mode is SideEffectMode.IDEMPOTENT:
                headers = task.get("headers")
                has_idempotency_key = isinstance(headers, Mapping) and any(
                    str(key).casefold() == "idempotency-key" for key in headers
                )
                decisions.append(
                    ShadowTaskDecision(
                        taskId=task_id,
                        originalType=task_type,
                        mode=mode,
                        reason=(
                            "explicit idempotency key preserves the isolated external call"
                            if has_idempotency_key
                            else "external call lacks an explicit Idempotency-Key header"
                        ),
                        blocking=not has_idempotency_key,
                    )
                )
            else:
                if mode is SideEffectMode.MOCK and task_id not in mock_outputs:
                    decisions.append(
                        ShadowTaskDecision(
                            taskId=task_id,
                            originalType=task_type,
                            mode=mode,
                            reason="mock mode requires an explicit output for the external task",
                            blocking=True,
                        )
                    )
                else:
                    result: JsonValue = (
                        mock_outputs[task_id]
                        if mode is SideEffectMode.MOCK
                        else {
                            "shadow": {
                                "mode": mode.value,
                                "originalType": task_type,
                                "suppressed": True,
                            }
                        }
                    )
                    preserved = {
                        key: copy.deepcopy(value)
                        for key, value in task.items()
                        if key
                        in {
                            "id",
                            "description",
                            "dependsOn",
                            "runIf",
                            "conditionErrorPolicy",
                        }
                    }
                    task.clear()
                    task.update(preserved)
                    task.update({"type": "core.return", "value": result})
                    decisions.append(
                        ShadowTaskDecision(
                            taskId=task_id,
                            originalType=task_type,
                            mode=mode,
                            replacementType="core.return",
                            reason="external side effect is replaced by a deterministic result",
                        )
                    )
        for child_key in ("tasks", "errors", "then", "else"):
            _plan_shadow_tasks(
                task.get(child_key),
                mode=mode,
                mock_outputs=mock_outputs,
                decisions=decisions,
            )
        for branch_key in ("elseIf", "predicateCases"):
            branches = task.get(branch_key)
            if isinstance(branches, list):
                for branch in branches:
                    if isinstance(branch, Mapping):
                        _plan_shadow_tasks(
                            branch.get("tasks"),
                            mode=mode,
                            mock_outputs=mock_outputs,
                            decisions=decisions,
                        )
        cases = task.get("cases")
        if isinstance(cases, Mapping):
            for case_tasks in cases.values():
                _plan_shadow_tasks(
                    case_tasks,
                    mode=mode,
                    mock_outputs=mock_outputs,
                    decisions=decisions,
                )


class ConformanceTolerance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    duration_ms: float = Field(default=1000, alias="durationMs", ge=0)


class ConformanceDifference(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    expected: Any
    actual: Any
    tolerated: bool = False


class ConformanceReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    target_version: str = Field(alias="targetVersion")
    differences: tuple[ConformanceDifference, ...]
    passed: bool
    full_compatibility_claim_allowed: bool = Field(alias="fullCompatibilityClaimAllowed")


def compare_observations(
    reference: ConformanceObservation,
    candidate: ConformanceObservation,
    *,
    tolerance: ConformanceTolerance | None = None,
) -> ConformanceReport:
    effective = tolerance or ConformanceTolerance()
    differences: list[ConformanceDifference] = []
    fields_to_compare = (
        "target_version",
        "validation_class",
        "state_sequence",
        "task_graph",
        "outputs",
        "api_payload",
        "cli_exit_code",
        "cli_payload",
        "error_class",
    )
    for field_name in fields_to_compare:
        expected = getattr(reference, field_name)
        actual = getattr(candidate, field_name)
        if expected != actual:
            differences.append(
                ConformanceDifference(field=field_name, expected=expected, actual=actual)
            )
    duration_delta = abs(reference.duration_ms - candidate.duration_ms)
    if duration_delta > 0:
        differences.append(
            ConformanceDifference(
                field="duration_ms",
                expected=reference.duration_ms,
                actual=candidate.duration_ms,
                tolerated=duration_delta <= effective.duration_ms,
            )
        )
    for observation in (reference, candidate):
        if observation.side_effect_mode not in {
            SideEffectMode.SUPPRESS,
            SideEffectMode.MOCK,
            SideEffectMode.IDEMPOTENT,
        }:
            differences.append(
                ConformanceDifference(
                    field="side_effect_mode",
                    expected="suppressed, mocked or idempotent",
                    actual=observation.side_effect_mode,
                )
            )
    passed = all(item.tolerated for item in differences)
    manifest = compatibility_manifest()
    return ConformanceReport(
        targetVersion=KESTRA_TARGET_VERSION,
        differences=tuple(differences),
        passed=passed,
        fullCompatibilityClaimAllowed=passed and bool(manifest["releaseClaimAllowed"]),
    )


def compatibility_manifest() -> dict[str, Any]:
    resource = files("amesh.resources").joinpath("kestra-compatibility-1.3.30.json")
    value = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("compatibility manifest must contain an object")
    return {str(key): item for key, item in value.items()}


def _duration_seconds(value: Any) -> float:
    try:
        duration = _DURATION.validate_python(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"duration {value!r} is not a supported ISO-8601 duration") from exc
    seconds = duration.total_seconds()
    if seconds < 0:
        raise ValueError("duration cannot be negative")
    return seconds


def _pointer(path: Sequence[str | int] | None) -> str:
    if not path:
        return ""
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in path)


def _sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


_SENSITIVE_NAME = re.compile(r"(?:password|secret|token|credential|private[_-]?key)", re.I)


def _secret_plaintext_paths(value: Any, path: tuple[str | int, ...] = ()) -> tuple[str, ...]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = (*path, str(key))
            if (
                _SENSITIVE_NAME.search(str(key))
                and isinstance(item, str)
                and not (
                    item.startswith(("${secret:", "{{ secret(", "secret://"))
                    or item in {"REDACTED", "***"}
                )
            ):
                findings.append(_pointer(child))
            findings.extend(_secret_plaintext_paths(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_secret_plaintext_paths(item, (*path, index)))
    return tuple(findings)


def _validate_chronology(
    records: Sequence[MigrationRecord], issues: list[MigrationPlanIssue]
) -> None:
    last_by_parent: dict[str, datetime] = {}
    for record in records:
        if record.kind not in {
            MigrationResourceKind.STATE_EVENT,
            MigrationResourceKind.LOG,
            MigrationResourceKind.AUDIT_EVENT,
        }:
            continue
        if record.occurred_at is None:
            issues.append(
                MigrationPlanIssue(
                    code="CHRONOLOGY_TIMESTAMP_MISSING",
                    message="historical event requires occurredAt",
                    sourceId=record.source_id,
                )
            )
            continue
        parent = record.references[0] if record.references else record.tenant
        prior = last_by_parent.get(parent)
        if prior is not None and record.occurred_at < prior:
            issues.append(
                MigrationPlanIssue(
                    code="CHRONOLOGY_REVERSED",
                    message=f"historical event precedes an earlier record for {parent!r}",
                    sourceId=record.source_id,
                )
            )
        last_by_parent[parent] = record.occurred_at
