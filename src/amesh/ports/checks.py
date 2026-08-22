from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from amesh.dsl import CheckDefinition


class CheckOutcome(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"


class CheckEvaluationPoint(StrEnum):
    STARTED = "STARTED"
    TERMINAL = "TERMINAL"
    DEADLINE = "DEADLINE"
    FRESHNESS = "FRESHNESS"


class CheckPolicySource(StrEnum):
    NAMESPACE = "NAMESPACE"
    PLUGIN_DEFAULT = "PLUGIN_DEFAULT"


class CheckActionState(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    RETRY_WAIT = "RETRY_WAIT"
    SUCCEEDED = "SUCCEEDED"
    DEAD_LETTERED = "DEAD_LETTERED"
    SKIPPED = "SKIPPED"


class NamespaceCheckPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    policy_id: UUID
    tenant_id: str
    namespace: str
    policy_key: str
    source: CheckPolicySource
    task_type: str | None = None
    definition: CheckDefinition
    enabled: bool
    created_at: datetime
    updated_at: datetime


class CheckEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True)

    evaluation_id: UUID
    tenant_id: str
    check_definition_id: UUID
    execution_id: UUID | None = None
    namespace: str
    flow_id: str
    flow_revision: int
    check_id: str
    check_type: str
    source: str
    evaluation_point: CheckEvaluationPoint
    subject_key: str
    outcome: CheckOutcome
    severity: str
    reason: str
    evidence: dict[str, Any]
    labels: dict[str, str]
    evaluated_at: datetime


class CheckComplianceSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    group_key: str
    total: int = Field(ge=0)
    passed: int = Field(ge=0)
    warned: int = Field(ge=0)
    failed: int = Field(ge=0)
    errors: int = Field(ge=0)
    compliance_rate: float = Field(ge=0, le=1)


class CheckActionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    action_id: UUID
    tenant_id: str
    evaluation_id: UUID
    execution_id: UUID | None = None
    action_index: int = Field(ge=0)
    action_type: str
    state: CheckActionState
    target_namespace: str | None = None
    target_flow_id: str | None = None
    channel: str | None = None
    payload: dict[str, Any]
    policy_depth: int = Field(ge=0)
    max_depth: int = Field(ge=1)
    attempt: int = Field(ge=0)
    max_attempts: int = Field(ge=1)
    owner_id: UUID | None = None
    fencing_token: int = Field(ge=0)
    available_at: datetime
    last_error: str | None = None
    evidence: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CheckRepository(Protocol):
    async def upsert_policy(
        self,
        *,
        tenant_id: str,
        namespace: str,
        policy_key: str,
        source: CheckPolicySource,
        definition: CheckDefinition,
        actor_id: str,
        task_type: str | None = None,
        enabled: bool = True,
    ) -> NamespaceCheckPolicy: ...

    async def list_policies(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        limit: int = 100,
    ) -> list[NamespaceCheckPolicy]: ...

    async def list_evaluations(
        self,
        *,
        tenant_id: str,
        namespace: str | None = None,
        flow_id: str | None = None,
        execution_id: UUID | None = None,
        outcome: CheckOutcome | None = None,
        limit: int = 100,
    ) -> list[CheckEvaluation]: ...

    async def summarize(
        self,
        *,
        tenant_id: str,
        group_by: str,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        namespace: str | None = None,
        flow_id: str | None = None,
        limit: int = 100,
    ) -> list[CheckComplianceSummary]: ...

    async def process_due_checks(
        self,
        *,
        tenant_id: str,
        limit: int = 100,
    ) -> int: ...

    async def claim_actions(
        self,
        *,
        tenant_id: str,
        owner_id: UUID,
        lease_duration: timedelta,
        limit: int = 100,
    ) -> list[CheckActionRecord]: ...

    async def publish_notification(
        self,
        action: CheckActionRecord,
        *,
        tenant_id: str,
    ) -> None: ...

    async def complete_action(
        self,
        action_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        evidence: dict[str, Any],
    ) -> CheckActionRecord: ...

    async def fail_action(
        self,
        action_id: UUID,
        *,
        tenant_id: str,
        owner_id: UUID,
        fencing_token: int,
        error: str,
        retry_delay: timedelta,
    ) -> CheckActionRecord: ...
