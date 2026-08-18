from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status

from amesh import __version__
from amesh.api.models import (
    HealthResponse,
    ReduceExecutionRequest,
    ReduceExecutionResponse,
)
from amesh.domain import InvalidTransition, reduce_execution
from amesh.dsl import FlowDocumentError, FlowValidationResult, validate_flow_document

app = FastAPI(
    title="AMESH",
    version=__version__,
    description=(
        "Initial clean-room durable workflow foundation. "
        "This API demonstrates flow validation and deterministic reduction only."
    ),
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ready", response_model=HealthResponse, tags=["system"])
async def ready() -> HealthResponse:
    # The foundation has no live external repositories yet.
    return HealthResponse(status="ready", version=__version__)


@app.post(
    "/api/v1/flows/validate",
    response_model=FlowValidationResult,
    tags=["flows"],
)
async def validate_flow(request: Request) -> FlowValidationResult:
    body = await request.body()
    if len(body) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="flow document exceeds the 2 MiB foundation limit",
        )
    try:
        return validate_flow_document(body)
    except FlowDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@app.post(
    "/api/v1/executions/reduce",
    response_model=ReduceExecutionResponse,
    tags=["executions"],
)
async def reduce_execution_events(
    request: ReduceExecutionRequest,
) -> ReduceExecutionResponse:
    snapshot = request.snapshot
    duplicates = 0
    for event in request.events:
        before = snapshot
        try:
            snapshot = reduce_execution(snapshot, event)
        except InvalidTransition as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        if snapshot is before:
            duplicates += 1
    return ReduceExecutionResponse(
        snapshot=snapshot,
        duplicate_events_ignored=duplicates,
    )
