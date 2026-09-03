from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterable, Mapping
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from amesh import __version__
from amesh.dsl import FlowDefinition, ResourceKind, ResourceSchemaRegistry, TaskResourceLimits
from amesh.dsl.models import TaskDefinition
from amesh.ports import (
    LogSourceStream,
    PersistedExecution,
    TaskCacheKey,
    TaskCacheLookup,
    TaskCacheMode,
    TaskCacheRepository,
)

from .contracts import (
    TaskCompletion,
    TaskConfigurationError,
    TaskExecutionContext,
    TaskLogRecord,
    TaskResourceLimitError,
)

LOGGER = logging.getLogger("amesh.task.core.log")


def derive_task_cache_key(
    flow: FlowDefinition,
    execution: PersistedExecution,
    task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskCacheKey:
    """Derive a stable key without persisting raw security-context material."""

    policy = task.task_cache
    if not policy.enabled or policy.ttl is None:
        raise ValueError("task cache key requires an enabled policy with ttl")
    declared_inputs = {
        definition.id: execution.inputs.get(definition.id, definition.default)
        for definition in flow.inputs
    }
    selectable_context: dict[str, object] = {
        "inputs": declared_inputs,
        "variables": flow.variables,
        "labels": {
            key: value
            for key, value in execution.labels.items()
            if not key.startswith(("amesh.", "system."))
        },
        "trigger": {
            key: value for key, value in execution.trigger.items() if not key.startswith("_amesh")
        },
        "iteration": context.iteration.as_mapping() if context.iteration is not None else {},
    }
    security_payload = {
        "tenant": execution.tenant_id,
        "secretScopes": sorted(context.secret_scopes),
        "secrets": sorted(context.secrets.items()),
        "files": sorted(context.files.items()),
    }
    security_context_hash = hashlib.sha256(_canonical_json(security_payload)).hexdigest()
    code_version = policy.code_version or f"amesh:{__version__}:{task.type}"
    payload = {
        "schema": "amesh.task-cache/v1",
        "tenant": execution.tenant_id,
        "flow": {
            "namespace": flow.namespace,
            "id": flow.id,
            "revision": flow.revision,
        },
        "task": task.model_dump(
            mode="json",
            by_alias=True,
            exclude={"task_cache"},
            exclude_none=True,
        ),
        "policy": policy.model_dump(mode="json", by_alias=True, exclude_none=True),
        "codeVersion": code_version,
        "context": {name: selectable_context[name] for name in policy.key_context},
        "securityContextHash": security_context_hash,
    }
    cache_namespace = policy.namespace or "default"
    prefix_parts = [cache_namespace, flow.namespace]
    if policy.scope.value in {"TASK", "FLOW"}:
        prefix_parts.append(flow.id)
    if policy.scope.value == "TASK":
        prefix_parts.append(task.id)
    key_prefix = "/".join(prefix_parts)
    lease_seconds = max(task.timeout_seconds or 3600, 60)
    return TaskCacheKey(
        key_hash=hashlib.sha256(_canonical_json(payload)).hexdigest(),
        key_prefix=key_prefix,
        cache_namespace=cache_namespace,
        scope=policy.scope.value,
        namespace=flow.namespace,
        flow_id=flow.id,
        flow_revision=flow.revision,
        task_id=task.id,
        task_type=task.type,
        security_context_hash=security_context_hash,
        invalidation_policy=policy.invalidation_policy.value,
        ttl=policy.ttl,
        population_lease=timedelta(seconds=lease_seconds),
    )


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        default=_canonical_json_default,
    ).encode("utf-8")


def _canonical_json_default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return str(value)


def _execution_cache_mode(execution: PersistedExecution) -> TaskCacheMode:
    raw = execution.trigger.get("_ameshCacheMode", TaskCacheMode.USE.value)
    try:
        return TaskCacheMode(str(raw))
    except ValueError:
        return TaskCacheMode.USE


def _with_cache_evidence(
    evidence: Mapping[str, object],
    lookup: TaskCacheLookup,
) -> dict[str, object]:
    result = deepcopy(dict(evidence))
    result["cache"] = {
        "decision": lookup.decision.value,
        "reason": lookup.reason,
        "keyHash": lookup.key_hash,
        "sourceExecutionId": (
            str(lookup.source_execution_id) if lookup.source_execution_id is not None else None
        ),
        "sourceTaskRunId": (
            str(lookup.source_task_run_id) if lookup.source_task_run_id is not None else None
        ),
        "sourceAttempt": lookup.source_attempt,
        "expiresAt": lookup.expires_at.isoformat() if lookup.expires_at is not None else None,
    }
    stored_logs = result.get("logs", [])
    logs = list(stored_logs) if isinstance(stored_logs, list) else []
    logs.insert(
        0,
        TaskLogRecord(
            logger="amesh.task.cache",
            message=f"Cache {lookup.decision.value}: {lookup.reason}",
            fields={"keyHash": lookup.key_hash},
            sourceStream=LogSourceStream.SYSTEM,
            occurredAt=datetime.now(UTC),
        ).model_dump(mode="json", by_alias=True),
    )
    result["logs"] = logs
    return result


async def _abandon_cache_population(
    repository: TaskCacheRepository | None,
    key: TaskCacheKey,
    lookup: TaskCacheLookup,
    *,
    tenant_id: str,
    execution_id: UUID,
    task_run_id: UUID,
    attempt: int,
    reason: str,
) -> None:
    if repository is None or lookup.owner_token is None:
        return
    try:
        await repository.abandon(
            key.key_hash,
            lookup.owner_token,
            tenant_id=tenant_id,
            execution_id=execution_id,
            task_run_id=task_run_id,
            attempt=attempt,
            reason=reason,
        )
    except Exception:
        LOGGER.exception(
            "task result cache abandonment failed",
            extra={
                "tenant_id": tenant_id,
                "execution_id": str(execution_id),
                "task_run_id": str(task_run_id),
                "cache_key_hash": key.key_hash,
                "reason": reason,
            },
        )
        raise


def normalize_task_completion(
    result: dict[str, Any] | TaskCompletion,
    limits: TaskResourceLimits,
    *,
    secret_values: Iterable[str] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    completion = result if isinstance(result, TaskCompletion) else TaskCompletion(output=result)
    serialized = completion.model_dump(mode="json", by_alias=True)
    sensitive_keys = {
        key.casefold().replace("-", "_") for key in serialized.pop("sensitiveOutputKeys")
    }
    secrets = tuple(value for value in secret_values if value)
    output, output_redacted = _redact_task_evidence(
        serialized["output"],
        sensitive_keys=sensitive_keys,
        secret_values=secrets,
    )
    logs = serialized["logs"]
    for log in logs:
        if log["redacted"]:
            log["message"] = "[REDACTED]"
            log["fields"] = {}
            continue
        message, message_redacted = _redact_task_evidence(
            log["message"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        fields, fields_redacted = _redact_task_evidence(
            log["fields"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        log["message"] = message
        log["fields"] = fields
        log["redacted"] = message_redacted or fields_redacted
    for metric in serialized["metrics"]:
        labels, _ = _redact_task_evidence(
            metric["labels"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        metric["labels"] = labels
    artifacts = serialized["artifacts"]
    for artifact in artifacts:
        uri, uri_redacted = _redact_task_evidence(
            artifact["uri"], sensitive_keys=sensitive_keys, secret_values=secrets
        )
        if uri_redacted:
            raise TaskResourceLimitError("artifact URI contains secret material")
        artifact["uri"] = uri
    assets, assets_redacted = _redact_task_evidence(
        serialized["assets"], sensitive_keys=sensitive_keys, secret_values=secrets
    )
    if assets_redacted:
        raise TaskResourceLimitError("asset event contains secret material")
    exit_metadata, _ = _redact_task_evidence(
        serialized["exit"], sensitive_keys=sensitive_keys, secret_values=secrets
    )
    output_bytes = _json_size(output)
    log_bytes = _json_size(logs)
    artifact_bytes = sum(int(artifact["sizeBytes"]) for artifact in artifacts)
    _require_within_limit("output", output_bytes, limits.max_output_bytes)
    _require_within_limit("log", log_bytes, limits.max_log_bytes)
    _require_within_limit("artifact", artifact_bytes, limits.max_artifact_bytes)
    return output, {
        "logs": logs,
        "metrics": serialized["metrics"],
        "artifacts": artifacts,
        "assets": assets,
        "exit": exit_metadata,
        "outputSensitive": bool(sensitive_keys or output_redacted),
        "sizes": {
            "outputBytes": output_bytes,
            "logBytes": log_bytes,
            "artifactBytes": artifact_bytes,
        },
    }


def _is_sensitive_field_name(value: str) -> bool:
    normalized = "".join(character for character in value.casefold() if character.isalnum())
    if normalized in {"secretscopes", "secretsredacted"}:
        return False
    if normalized in {
        "apikey",
        "authorization",
        "credential",
        "credentials",
        "password",
        "secret",
        "secrets",
        "token",
    }:
        return True
    return normalized.startswith(
        ("authorization", "credential", "password", "secret")
    ) or normalized.endswith(("apikey", "credential", "password", "secret", "token"))


def _redact_task_evidence(
    value: Any,
    *,
    sensitive_keys: set[str],
    secret_values: tuple[str, ...],
) -> tuple[Any, bool]:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        changed = False
        for key, item in value.items():
            normalized = str(key).casefold().replace("-", "_")
            if normalized in sensitive_keys or _is_sensitive_field_name(normalized):
                redacted[key] = "[REDACTED]"
                changed = True
                continue
            redacted[key], item_changed = _redact_task_evidence(
                item,
                sensitive_keys=sensitive_keys,
                secret_values=secret_values,
            )
            changed = changed or item_changed
        return redacted, changed
    if isinstance(value, list):
        redacted_items: list[Any] = []
        changed = False
        for item in value:
            redacted, item_changed = _redact_task_evidence(
                item,
                sensitive_keys=sensitive_keys,
                secret_values=secret_values,
            )
            redacted_items.append(redacted)
            changed = changed or item_changed
        return redacted_items, changed
    if isinstance(value, str):
        redacted_text = value
        for secret in sorted(set(secret_values), key=len, reverse=True):
            redacted_text = redacted_text.replace(secret, "[REDACTED]")
        return redacted_text, redacted_text != value
    return value, False


def _json_size(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _require_within_limit(kind: str, actual: int, limit: int) -> None:
    if actual > limit:
        raise TaskResourceLimitError(
            f"task {kind} evidence is {actual} bytes; configured limit is {limit} bytes"
        )


def _validate_registered_task_schemas(
    flow: FlowDefinition,
    registry: ResourceSchemaRegistry,
) -> None:
    pending = [*flow.tasks, *flow.errors, *flow.finally_tasks, *flow.after_execution]
    while pending:
        task = pending.pop(0)
        pending[0:0] = [
            *[child for _, children in task.child_task_groups() for child in children],
            *task.errors,
        ]
        issues = registry.validate(ResourceKind.TASK, task.type, task.configuration)
        if issues:
            details = "; ".join(issue.message for issue in issues)
            raise TaskConfigurationError(
                f"task {task.id!r} configuration does not match {task.type!r}: {details}"
            )
