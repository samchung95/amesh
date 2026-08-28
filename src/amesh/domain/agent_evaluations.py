from __future__ import annotations

from decimal import Decimal
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel, ConfigDict, Field

from .agent_resources import AgentEvaluationSpec


class AgentEvaluationCheck(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    key: str
    kind: str
    passed: bool
    detail: str
    weight: Decimal = Decimal("0")


class AgentDeterministicEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    passed: bool
    rubric_score: Decimal = Field(alias="rubricScore", ge=0, le=1)
    minimum_rubric_score: Decimal = Field(alias="minimumRubricScore", ge=0, le=1)
    checks: tuple[AgentEvaluationCheck, ...]


class AgentJudgeEvidence(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    passed: bool
    score: Decimal = Field(ge=0, le=1)
    uncertainty: Decimal = Field(ge=0, le=1)
    rationale: str
    model: str
    route_id: str = Field(alias="routeId")
    usage: dict[str, Any]
    cost_usd: Decimal = Field(alias="costUsd", ge=0)
    nondeterministic: bool = True
    disclosure: str


class AgentEvaluationOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    key: str
    revision: int = Field(ge=1)
    turn: int = Field(ge=1)
    digest: str
    passed: bool
    deterministic: AgentDeterministicEvaluation
    judge: AgentJudgeEvidence | None = None


class AgentEvaluationPreview(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    evaluation_key: str = Field(alias="evaluationKey")
    evaluation_revision: int = Field(alias="evaluationRevision", ge=1)
    fixture_key: str = Field(alias="fixtureKey")
    input: dict[str, Any]
    recorded_output: dict[str, Any] = Field(alias="recordedOutput")
    deterministic: AgentDeterministicEvaluation
    judge_required: bool = Field(alias="judgeRequired")
    external_calls_suppressed: bool = Field(default=True, alias="externalCallsSuppressed")
    model_behavior_unknown: bool = Field(default=True, alias="modelBehaviorUnknown")


def evaluate_deterministic_output(
    spec: AgentEvaluationSpec,
    output: dict[str, Any],
) -> AgentDeterministicEvaluation:
    checks: list[AgentEvaluationCheck] = []
    assertions_passed = True
    for index, assertion in enumerate(spec.assertions, start=1):
        error = _schema_error(assertion, output)
        passed = error is None
        assertions_passed = assertions_passed and passed
        checks.append(
            AgentEvaluationCheck(
                key=f"assertion-{index}",
                kind="ASSERTION",
                passed=passed,
                detail="passed" if passed else error or "failed",
            )
        )

    rubric_weight = sum((item.weight for item in spec.rubric), Decimal("0"))
    passed_weight = Decimal("0")
    for criterion in spec.rubric:
        error = _schema_error(criterion.assertion, output)
        passed = error is None
        if passed:
            passed_weight += criterion.weight
        checks.append(
            AgentEvaluationCheck(
                key=criterion.key,
                kind="RUBRIC",
                passed=passed,
                detail="passed" if passed else error or "failed",
                weight=criterion.weight,
            )
        )
    rubric_score = Decimal("1") if rubric_weight == 0 else passed_weight / rubric_weight
    passed = assertions_passed and rubric_score >= spec.minimum_rubric_score
    return AgentDeterministicEvaluation(
        passed=passed,
        rubricScore=rubric_score,
        minimumRubricScore=spec.minimum_rubric_score,
        checks=tuple(checks),
    )


def _schema_error(schema: dict[str, Any], output: dict[str, Any]) -> str | None:
    try:
        Draft202012Validator(schema).validate(output)
    except JsonSchemaValidationError as exc:
        return exc.message
    return None
