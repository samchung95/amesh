from __future__ import annotations

from pydantic import BaseModel, Field

from amesh.domain import ExecutionEvent, ExecutionSnapshot


class HealthResponse(BaseModel):
    status: str
    version: str


class ReduceExecutionRequest(BaseModel):
    snapshot: ExecutionSnapshot
    events: list[ExecutionEvent] = Field(min_length=1)


class ReduceExecutionResponse(BaseModel):
    snapshot: ExecutionSnapshot
    duplicate_events_ignored: int = 0
