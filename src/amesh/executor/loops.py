from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from amesh.dsl import TaskDefinition
from amesh.ports import ObjectStore

LOOP_TASK_TYPES = frozenset({"core.foreach", "core.while", "core.until"})


class LoopRange(BaseModel):
    model_config = ConfigDict(frozen=True)

    start: int = 0
    end: int
    step: int = 1

    @model_validator(mode="after")
    def reject_zero_step(self) -> LoopRange:
        if self.step == 0:
            raise ValueError("loop range step cannot be zero")
        return self


class LoopSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[Any] | dict[str, Any] | None = None
    range: LoopRange | None = None
    manifest_uri: str | None = Field(default=None, alias="manifestUri")
    batch_size: int | None = Field(default=None, alias="batchSize", ge=1)
    condition: str | None = None
    max_iterations: int = Field(default=10_000, alias="maxIterations", ge=1, le=1_000_000)
    max_duration_seconds: float = Field(default=3_600, alias="maxDurationSeconds", gt=0)
    max_task_runs: int = Field(default=100_000, alias="maxTaskRuns", ge=1, le=1_000_000)
    inline_payload_bytes: int = Field(default=65_536, alias="inlinePayloadBytes", ge=1)
    continue_if: str | None = Field(default=None, alias="continueIf")
    break_if: str | None = Field(default=None, alias="breakIf")


@dataclass(frozen=True)
class LoopItem:
    index: int
    key: str
    value: Any


@dataclass(frozen=True)
class LoopIterationContext:
    index: int
    key: str
    value: Any
    parent: Mapping[str, Any]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "key": self.key,
            "value": self.value,
            "parent": dict(self.parent),
        }


def parse_loop_spec(task: TaskDefinition) -> LoopSpec:
    extra = task.configuration.handler_view().mutable_copy()
    if task.condition is not None:
        extra["condition"] = task.condition
    spec = LoopSpec.model_validate(extra)
    if task.type == "core.foreach":
        sources = sum(value is not None for value in (spec.items, spec.range, spec.manifest_uri))
        if sources != 1:
            raise ValueError("core.foreach requires exactly one of items, range or manifestUri")
    elif spec.condition is None:
        raise ValueError(f"{task.type} requires condition")
    if len(task.tasks) * spec.max_iterations > spec.max_task_runs:
        raise ValueError(
            "loop maximum could generate more task runs than maxTaskRuns; "
            f"children={len(task.tasks)}, maxIterations={spec.max_iterations}, "
            f"maxTaskRuns={spec.max_task_runs}"
        )
    return spec


async def iter_foreach_items(
    spec: LoopSpec,
    *,
    tenant_id: str,
    object_store: ObjectStore | None,
) -> AsyncIterator[LoopItem]:
    source = _inline_items(spec)
    if source is None:
        if object_store is None or spec.manifest_uri is None:
            raise ValueError("manifestUri loops require an object store")
        source = _manifest_items(object_store, tenant_id, spec.manifest_uri)

    if spec.batch_size is None:
        index = 0
        async for key, value in source:
            yield LoopItem(index=index, key=key, value=value)
            index += 1
        return

    batch: list[dict[str, Any]] = []
    batch_index = 0
    async for key, value in source:
        batch.append({"key": key, "value": value})
        if len(batch) == spec.batch_size:
            yield LoopItem(index=batch_index, key=str(batch_index), value=batch)
            batch = []
            batch_index += 1
    if batch:
        yield LoopItem(index=batch_index, key=str(batch_index), value=batch)


def _inline_items(spec: LoopSpec) -> AsyncIterator[tuple[str, Any]] | None:
    if isinstance(spec.items, list):

        async def array_items() -> AsyncIterator[tuple[str, Any]]:
            for index, value in enumerate(spec.items or []):
                yield str(index), value

        return array_items()
    if isinstance(spec.items, dict):

        async def map_items() -> AsyncIterator[tuple[str, Any]]:
            for key in sorted(spec.items or {}):
                yield key, (spec.items or {})[key]

        return map_items()
    if spec.range is not None:
        loop_range = spec.range

        async def range_items() -> AsyncIterator[tuple[str, Any]]:
            values = range(loop_range.start, loop_range.end, loop_range.step)
            for index, value in enumerate(values):
                yield str(index), value

        return range_items()
    return None


async def _manifest_items(
    object_store: ObjectStore,
    tenant_id: str,
    uri: str,
) -> AsyncIterator[tuple[str, Any]]:
    buffer = bytearray()
    index = 0
    async for chunk in object_store.get(tenant_id, uri):
        buffer.extend(chunk)
        while (line_end := buffer.find(b"\n")) >= 0:
            line = bytes(buffer[:line_end]).strip()
            del buffer[: line_end + 1]
            if not line:
                continue
            key, value = _manifest_record(json.loads(line), index)
            yield key, value
            index += 1
    if buffer.strip():
        key, value = _manifest_record(json.loads(buffer), index)
        yield key, value


def _manifest_record(record: Any, index: int) -> tuple[str, Any]:
    if isinstance(record, Mapping) and set(record) == {"key", "value"}:
        return str(record["key"]), record["value"]
    return str(index), record
