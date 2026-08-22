from __future__ import annotations

import json
from datetime import datetime
from difflib import unified_diff
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FlowLifecycle(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class FlowRevisionSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    source: str | None = Field(default=None, max_length=1024)
    source_commit: str | None = Field(default=None, max_length=255)
    environment: str | None = Field(default=None, max_length=255)
    deployment: dict[str, Any] = Field(default_factory=dict)


class FlowRevisionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    resource_id: UUID
    tenant_id: str
    namespace: str
    flow_id: str
    revision: int = Field(ge=1)
    semantic_hash: str
    plugin_resolution: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    source_commit: str | None = None
    environment: str | None = None
    deployment: dict[str, Any] = Field(default_factory=dict)
    created_by: str
    created_at: datetime


class FlowRevisionDiff(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_revision: int = Field(ge=1)
    to_revision: int = Field(ge=1)
    human: str
    operations: tuple[dict[str, Any], ...]


def compare_flow_revisions(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    from_revision: int,
    to_revision: int,
) -> FlowRevisionDiff:
    before_text = json.dumps(before, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    after_text = json.dumps(after, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    human = "".join(
        unified_diff(
            before_text.splitlines(keepends=True),
            after_text.splitlines(keepends=True),
            fromfile=f"revision-{from_revision}",
            tofile=f"revision-{to_revision}",
        )
    )
    operations: list[dict[str, Any]] = []
    _append_patch_operations(operations, before, after, path="")
    return FlowRevisionDiff(
        from_revision=from_revision,
        to_revision=to_revision,
        human=human,
        operations=tuple(operations),
    )


def _append_patch_operations(
    operations: list[dict[str, Any]],
    before: Any,
    after: Any,
    *,
    path: str,
) -> None:
    if isinstance(before, dict) and isinstance(after, dict):
        before_keys = set(before)
        after_keys = set(after)
        for key in sorted(before_keys - after_keys):
            operations.append({"op": "remove", "path": _join_pointer(path, key)})
        for key in sorted(after_keys - before_keys):
            operations.append({"op": "add", "path": _join_pointer(path, key), "value": after[key]})
        for key in sorted(before_keys & after_keys):
            _append_patch_operations(
                operations,
                before[key],
                after[key],
                path=_join_pointer(path, key),
            )
        return
    if before != after:
        operations.append({"op": "replace", "path": path, "value": after})


def _join_pointer(path: str, key: object) -> str:
    token = str(key).replace("~", "~0").replace("/", "~1")
    return f"{path}/{token}"
