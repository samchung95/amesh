"""Generic, side-effect-safe differential and shadow execution contracts.

The module deliberately knows nothing about a workflow provider or a business domain. An adapter
turns a pinned configuration into a :class:`RunObservation`; the quality core compares only the
portable observation fields and never invokes an external service itself.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from decimal import Decimal
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


class FixtureSource(StrEnum):
    """The only sources allowed to satisfy a shadow side effect."""

    SAFE_FIXTURE = "SAFE_FIXTURE"
    RECORDING = "RECORDING"


class ComparisonCategory(StrEnum):
    DETERMINISTIC_FAILURE = "DETERMINISTIC_FAILURE"
    TOLERATED_DIFFERENCE = "TOLERATED_DIFFERENCE"
    NONDETERMINISTIC_OBSERVATION = "NONDETERMINISTIC_OBSERVATION"


class ConfigurationPin(BaseModel):
    """An exact immutable configuration identity; no floating ``latest`` reference is accepted."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ShadowFixture(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    source: FixtureSource
    value: Any = None
    certificate: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def require_certificate(self) -> ShadowFixture:
        expected = _digest({"key": self.key, "source": self.source.value, "value": self.value})
        if self.certificate != expected:
            raise ValueError("shadow fixture certificate does not match its content")
        return self


class Tolerance(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    absolute: Decimal = Field(default=Decimal("0"), ge=0)
    relative: Decimal = Field(default=Decimal("0"), ge=0, le=1)

    def accepts(self, left: Decimal, right: Decimal) -> bool:
        distance = abs(left - right)
        scale = max(abs(left), abs(right), Decimal("1"))
        return distance <= max(self.absolute, self.relative * scale)


class ComparisonPolicy(BaseModel):
    """Comparison rules that classify variance instead of forcing byte identity."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    nondeterministic_paths: tuple[str, ...] = Field(
        default=(), alias="nondeterministicPaths", max_length=1000
    )
    usage_tolerance: Tolerance = Field(default_factory=Tolerance, alias="usageTolerance")
    cost_tolerance: Tolerance = Field(default_factory=Tolerance, alias="costTolerance")
    latency_tolerance: Tolerance = Field(default_factory=Tolerance, alias="latencyTolerance")


class DifferentialSpec(BaseModel):
    """A frozen, tenant-scoped comparison request for two exact configurations."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    spec_id: UUID = Field(default_factory=uuid4, alias="specId")
    tenant_id: str = Field(alias="tenantId", min_length=1, max_length=255)
    namespace: str = Field(min_length=1, max_length=255)
    left: ConfigurationPin
    right: ConfigurationPin
    inputs: Any = Field(default_factory=dict)
    input_digest: str = Field(alias="inputDigest", default="")
    fixtures: tuple[ShadowFixture, ...] = ()
    policy: ComparisonPolicy = Field(default_factory=ComparisonPolicy)
    idempotency_key: str = Field(alias="idempotencyKey", min_length=1, max_length=512)

    @model_validator(mode="after")
    def freeze_inputs(self) -> DifferentialSpec:
        expected = _digest(self.inputs)
        if self.input_digest and self.input_digest != expected:
            raise ValueError("inputDigest does not match frozen inputs")
        object.__setattr__(self, "input_digest", expected)
        return self

    def fixture(self, key: str) -> ShadowFixture | None:
        return next((item for item in self.fixtures if item.key == key), None)


class ShadowEffect(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    key: str = Field(min_length=1, max_length=512)
    fixture_key: str | None = Field(default=None, alias="fixtureKey")


class ShadowExecutionError(RuntimeError):
    """Raised when a shadow adapter attempts an unapproved external effect."""


class ShadowRunContext:
    """Adapter context that makes side-effect authorization explicit and testable."""

    def __init__(self, spec: DifferentialSpec) -> None:
        self.spec = spec
        self.effects: list[ShadowEffect] = []

    def effect(self, key: str, *, fixture_key: str | None = None) -> Any:
        fixture = self.spec.fixture(fixture_key or key)
        if fixture is None:
            raise ShadowExecutionError(
                f"shadow effect {key!r} denied: no certified fixture or recording selected"
            )
        self.effects.append(ShadowEffect(key=key, fixtureKey=fixture.key))
        return deepcopy(fixture.value)


class Lineage(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    run_id: UUID = Field(default_factory=uuid4, alias="runId")
    spec_id: UUID = Field(alias="specId")
    side: str = Field(pattern=r"^(left|right)$")
    configuration_digest: str = Field(alias="configurationDigest")
    input_digest: str = Field(alias="inputDigest")
    parent_run_id: UUID | None = Field(default=None, alias="parentRunId")


class RunObservation(BaseModel):
    """Portable evidence emitted by an adapter; model output may be declared nondeterministic."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_: Any = Field(default_factory=dict, alias="schema")
    output: Any = None
    deterministic_assertions: tuple[Mapping[str, Any], ...] = Field(
        default=(), alias="deterministicAssertions"
    )
    task_chronology: tuple[Mapping[str, Any], ...] = Field(default=(), alias="taskChronology")
    tool_chronology: tuple[Mapping[str, Any], ...] = Field(default=(), alias="toolChronology")
    evidence: tuple[Mapping[str, Any], ...] = ()
    usage: Mapping[str, Decimal] = Field(default_factory=dict)
    cost: Decimal = Field(default=Decimal("0"), ge=0)
    latency: Decimal = Field(default=Decimal("0"), ge=0)
    nondeterministic_paths: tuple[str, ...] = Field(default=(), alias="nondeterministicPaths")
    effects: tuple[ShadowEffect, ...] = ()


class ShadowRun(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    lineage: Lineage
    observation: RunObservation


class ComparisonDifference(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    category: ComparisonCategory
    code: str
    path: str
    left: Any = None
    right: Any = None
    detail: str


class ComparisonReport(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: str = Field(default="amesh.differential-report/v1", alias="schemaVersion")
    spec_id: UUID = Field(alias="specId")
    tenant_id: str = Field(alias="tenantId")
    namespace: str
    input_digest: str = Field(alias="inputDigest")
    left: ShadowRun
    right: ShadowRun
    deterministic_failures: tuple[ComparisonDifference, ...] = Field(
        default=(), alias="deterministicFailures"
    )
    tolerated_differences: tuple[ComparisonDifference, ...] = Field(
        default=(), alias="toleratedDifferences"
    )
    nondeterministic_observations: tuple[ComparisonDifference, ...] = Field(
        default=(), alias="nondeterministicObservations"
    )

    @property
    def passed(self) -> bool:
        return not self.deterministic_failures


class Comparator(Protocol):
    def compare(
        self,
        left: ShadowRun,
        right: ShadowRun,
        policy: ComparisonPolicy,
    ) -> Sequence[ComparisonDifference]: ...


def _paths_match(path: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _structural_differences(
    left: Any,
    right: Any,
    *,
    path: str,
    policy: ComparisonPolicy,
    code: str,
    allow_nondeterministic: bool = False,
) -> list[ComparisonDifference]:
    if left == right:
        return []
    if allow_nondeterministic and _paths_match(path, policy.nondeterministic_paths):
        return [
            ComparisonDifference(
                category=ComparisonCategory.NONDETERMINISTIC_OBSERVATION,
                code="NONDETERMINISTIC_OUTPUT",
                path=path,
                left=left,
                right=right,
                detail="declared model/provider nondeterminism observed",
            )
        ]
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        differences: list[ComparisonDifference] = []
        for key in sorted(set(left) | set(right), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in left or key not in right:
                differences.append(
                    ComparisonDifference(
                        category=ComparisonCategory.DETERMINISTIC_FAILURE,
                        code=code,
                        path=child,
                        left=left.get(key),
                        right=right.get(key),
                        detail="structural field is present on only one side",
                    )
                )
            else:
                differences.extend(
                    _structural_differences(
                        left[key],
                        right[key],
                        path=child,
                        policy=policy,
                        code=code,
                        allow_nondeterministic=allow_nondeterministic,
                    )
                )
        return differences
    if (
        isinstance(left, Sequence)
        and not isinstance(left, (str, bytes))
        and isinstance(right, Sequence)
        and not isinstance(right, (str, bytes))
    ):
        differences = []
        for index in range(max(len(left), len(right))):
            child = f"{path}[{index}]"
            if index >= len(left) or index >= len(right):
                differences.append(
                    ComparisonDifference(
                        category=ComparisonCategory.DETERMINISTIC_FAILURE,
                        code=code,
                        path=child,
                        left=left[index] if index < len(left) else None,
                        right=right[index] if index < len(right) else None,
                        detail="structural item is present on only one side",
                    )
                )
            else:
                differences.extend(
                    _structural_differences(
                        left[index],
                        right[index],
                        path=child,
                        policy=policy,
                        code=code,
                        allow_nondeterministic=allow_nondeterministic,
                    )
                )
        return differences
    return [
        ComparisonDifference(
            category=ComparisonCategory.DETERMINISTIC_FAILURE,
            code=code,
            path=path,
            left=left,
            right=right,
            detail="values differ outside a declared nondeterministic path",
        )
    ]


class StructuralComparator:
    """Core provider-neutral comparator for portable run observations."""

    def compare(
        self,
        left: ShadowRun,
        right: ShadowRun,
        policy: ComparisonPolicy,
    ) -> Sequence[ComparisonDifference]:
        differences: list[ComparisonDifference] = []
        differences.extend(
            _structural_differences(
                left.observation.schema_,
                right.observation.schema_,
                path="schema",
                policy=policy,
                code="SCHEMA_MISMATCH",
            )
        )
        differences.extend(
            _structural_differences(
                left.observation.output,
                right.observation.output,
                path="output",
                policy=policy,
                code="OUTPUT_MISMATCH",
                allow_nondeterministic=True,
            )
        )
        for path, left_value, right_value, code, _label in (
            (
                "deterministicAssertions",
                left.observation.deterministic_assertions,
                right.observation.deterministic_assertions,
                "CONTRACT_ASSERTION_MISMATCH",
                "deterministic assertions",
            ),
            (
                "taskChronology",
                left.observation.task_chronology,
                right.observation.task_chronology,
                "CONTRACT_TASK_CHRONOLOGY_MISMATCH",
                "task chronology",
            ),
            (
                "toolChronology",
                left.observation.tool_chronology,
                right.observation.tool_chronology,
                "CONTRACT_TOOL_CHRONOLOGY_MISMATCH",
                "tool chronology",
            ),
            (
                "evidence",
                left.observation.evidence,
                right.observation.evidence,
                "EVIDENCE_MISMATCH",
                "evidence",
            ),
        ):
            differences.extend(
                _structural_differences(
                    left_value, right_value, path=path, policy=policy, code=code
                )
            )
        differences.extend(
            _compare_numbers(
                "usage",
                left.observation.usage,
                right.observation.usage,
                policy.usage_tolerance,
            )
        )
        differences.extend(
            _compare_number(
                "cost", left.observation.cost, right.observation.cost, policy.cost_tolerance
            )
        )
        differences.extend(
            _compare_number(
                "latency",
                left.observation.latency,
                right.observation.latency,
                policy.latency_tolerance,
            )
        )
        return differences


def _compare_number(
    path: str, left: Decimal, right: Decimal, tolerance: Tolerance
) -> list[ComparisonDifference]:
    if left == right:
        return []
    category = (
        ComparisonCategory.TOLERATED_DIFFERENCE
        if tolerance.accepts(left, right)
        else ComparisonCategory.DETERMINISTIC_FAILURE
    )
    return [
        ComparisonDifference(
            category=category,
            code="NUMERIC_TOLERANCE"
            if category is ComparisonCategory.TOLERATED_DIFFERENCE
            else "NUMERIC_MISMATCH",
            path=path,
            left=str(left),
            right=str(right),
            detail="numeric difference is within configured tolerance"
            if category is ComparisonCategory.TOLERATED_DIFFERENCE
            else "numeric difference exceeds configured tolerance",
        )
    ]


def _compare_numbers(
    path: str,
    left: Mapping[str, Decimal],
    right: Mapping[str, Decimal],
    tolerance: Tolerance,
) -> list[ComparisonDifference]:
    differences: list[ComparisonDifference] = []
    for key in sorted(set(left) | set(right)):
        differences.extend(
            _compare_number(
                f"{path}.{key}",
                Decimal(left.get(key, Decimal("0"))),
                Decimal(right.get(key, Decimal("0"))),
                tolerance,
            )
        )
    return differences


def compare_runs(
    spec: DifferentialSpec,
    left: ShadowRun,
    right: ShadowRun,
    *,
    comparators: Sequence[Comparator] = (),
) -> ComparisonReport:
    if left.lineage.spec_id != spec.spec_id or right.lineage.spec_id != spec.spec_id:
        raise ValueError("run lineage does not belong to differential specification")
    if left.lineage.side != "left" or right.lineage.side != "right":
        raise ValueError("comparison requires independent left and right lineage")
    if left.lineage.run_id == right.lineage.run_id:
        raise ValueError("comparison requires distinct run lineage identities")
    if left.lineage.configuration_digest != spec.left.digest:
        raise ValueError("left run lineage does not match pinned configuration")
    if right.lineage.configuration_digest != spec.right.digest:
        raise ValueError("right run lineage does not match pinned configuration")
    if (
        left.lineage.input_digest != spec.input_digest
        or right.lineage.input_digest != spec.input_digest
    ):
        raise ValueError("run lineage does not match frozen inputs")
    differences = list(StructuralComparator().compare(left, right, spec.policy))
    for comparator in comparators:
        differences.extend(comparator.compare(left, right, spec.policy))
    return ComparisonReport(
        specId=spec.spec_id,
        tenantId=spec.tenant_id,
        namespace=spec.namespace,
        inputDigest=spec.input_digest,
        left=left,
        right=right,
        deterministicFailures=tuple(
            item
            for item in differences
            if item.category is ComparisonCategory.DETERMINISTIC_FAILURE
        ),
        toleratedDifferences=tuple(
            item for item in differences if item.category is ComparisonCategory.TOLERATED_DIFFERENCE
        ),
        nondeterministicObservations=tuple(
            item
            for item in differences
            if item.category is ComparisonCategory.NONDETERMINISTIC_OBSERVATION
        ),
    )


Executor = Callable[[ConfigurationPin, Any, ShadowRunContext], RunObservation]


class DifferentialService:
    """Execute and retain reports with tenant-isolated idempotency semantics.

    Production adapters can replace this store with the command/event/outbox repository without
    changing the spec, policy, comparator or shadow execution contracts.
    """

    def __init__(self, *, comparators: Sequence[Comparator] = ()) -> None:
        self._reports: dict[tuple[str, str, str], ComparisonReport] = {}
        self._requests: dict[tuple[str, str, str], str] = {}
        self._comparators = tuple(comparators)

    def run(self, spec: DifferentialSpec, executor: Executor) -> ComparisonReport:
        if _digest(spec.inputs) != spec.input_digest:
            raise ValueError("frozen inputs changed after differential specification creation")
        key = (spec.tenant_id, spec.namespace, spec.idempotency_key)
        fingerprint = _digest(spec.model_dump(mode="json", exclude={"spec_id"}))
        existing = self._reports.get(key)
        if existing is not None:
            if self._requests[key] != fingerprint:
                raise ValueError("idempotency key was used for a different differential request")
            return existing
        left_context = ShadowRunContext(spec)
        right_context = ShadowRunContext(spec)
        left_observation = executor(spec.left, deepcopy(spec.inputs), left_context)
        right_observation = executor(spec.right, deepcopy(spec.inputs), right_context)
        if left_observation.effects and left_observation.effects != tuple(left_context.effects):
            raise ShadowExecutionError("left adapter reported an effect outside the shadow context")
        if right_observation.effects and right_observation.effects != tuple(right_context.effects):
            raise ShadowExecutionError(
                "right adapter reported an effect outside the shadow context"
            )
        left = ShadowRun(
            lineage=Lineage(
                specId=spec.spec_id,
                side="left",
                configurationDigest=spec.left.digest,
                inputDigest=spec.input_digest,
            ),
            observation=left_observation.model_copy(
                update={"effects": tuple(left_context.effects)}
            ),
        )
        right = ShadowRun(
            lineage=Lineage(
                specId=spec.spec_id,
                side="right",
                configurationDigest=spec.right.digest,
                inputDigest=spec.input_digest,
            ),
            observation=right_observation.model_copy(
                update={"effects": tuple(right_context.effects)}
            ),
        )
        report = compare_runs(spec, left, right, comparators=self._comparators)
        self._requests[key] = fingerprint
        self._reports[key] = report
        return report

    def get(self, tenant_id: str, namespace: str, idempotency_key: str) -> ComparisonReport:
        try:
            return self._reports[(tenant_id, namespace, idempotency_key)]
        except KeyError as exc:
            raise LookupError("differential report unavailable") from exc
