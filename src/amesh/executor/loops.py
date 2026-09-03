from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator, Mapping
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
    inline_items = inline_foreach_items(spec)
    if inline_items is not None:
        for item in inline_items:
            yield item
        return

    source: AsyncIterator[tuple[str, Any]]
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


def inline_foreach_items(spec: LoopSpec) -> Iterator[LoopItem] | None:
    """Expand an inline foreach source with the same ordering and batching as execution."""

    source: Iterator[tuple[str, Any]]
    if isinstance(spec.items, list):
        source = ((str(index), value) for index, value in enumerate(spec.items))
    elif isinstance(spec.items, dict):
        source = ((key, spec.items[key]) for key in sorted(spec.items))
    elif spec.range is not None:
        values = range(spec.range.start, spec.range.end, spec.range.step)
        source = ((str(index), value) for index, value in enumerate(values))
    else:
        return None

    if spec.batch_size is None:
        return (
            LoopItem(index=index, key=key, value=value) for index, (key, value) in enumerate(source)
        )

    def batches() -> Iterator[LoopItem]:
        batch: list[dict[str, Any]] = []
        batch_index = 0
        for key, value in source:
            batch.append({"key": key, "value": value})
            if len(batch) != spec.batch_size:
                continue
            yield LoopItem(index=batch_index, key=str(batch_index), value=batch)
            batch = []
            batch_index += 1
        if batch:
            yield LoopItem(index=batch_index, key=str(batch_index), value=batch)

    return batches()


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
