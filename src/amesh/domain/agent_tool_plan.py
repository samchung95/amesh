"""Pure required-tool-plan expansion, matching and restart-safe completion state.

The module deliberately has no session, provider or persistence imports.  A session can persist
the values here beside its checkpoint and use the returned immutable values as its admission and
completion boundary.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy
from enum import StrEnum
from typing import Any, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .resources import canonical_hash

TOOL_PLAN_SCHEMA_VERSION: Final = "amesh.agent-tool-plan/v1"
MAX_PLAN_STEPS = 100
MAX_PLAN_OCCURRENCES = 1_000
MAX_STEP_OCCURRENCES = 1_000


class ToolPlanError(ValueError):
    """Base error for invalid plans, calls or ledger transitions."""


class ToolPlanExpansionError(ToolPlanError):
    """Raised when runtime input cannot be expanded deterministically."""


class ToolPlanMatchError(ToolPlanError):
    """Raised when a tool result does not match the required next occurrence."""


class ToolPlanOrderError(ToolPlanMatchError):
    """Raised when a valid later occurrence is attempted before an earlier one."""


class ToolPlanLedgerError(ToolPlanError):
    """Raised when a completion replay conflicts with durable ledger state."""


class ToolPlanOccurrenceState(StrEnum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"


def _validate_pointer(value: str, *, field_name: str) -> str:
    if value == "":
        return value
    if not value.startswith("/"):
        raise ValueError(f"{field_name} must be an RFC 6901 JSON Pointer")
    if re.search(r"~(?![01])", value):
        raise ValueError(f"{field_name} contains an invalid JSON Pointer escape")
    return value


class RequiredToolStep(BaseModel):
    """One ordered tool requirement and its optional runtime input expansion."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    step_id: str = Field(
        alias="stepId", min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )
    tool_name: str = Field(alias="toolName", min_length=1, max_length=255)
    arguments: dict[str, Any] = Field(default_factory=dict)
    argument_bindings: dict[str, str] = Field(
        default_factory=dict, alias="argumentBindings", max_length=100
    )
    item_argument_bindings: dict[str, str] = Field(
        default_factory=dict, alias="itemArgumentBindings", max_length=100
    )
    for_each: str | None = Field(default=None, alias="forEach")
    max_occurrences: int = Field(
        default=MAX_STEP_OCCURRENCES, alias="maxOccurrences", ge=1, le=MAX_STEP_OCCURRENCES
    )

    @field_validator("argument_bindings", "item_argument_bindings")
    @classmethod
    def validate_argument_bindings(cls, value: dict[str, str]) -> dict[str, str]:
        for argument, pointer in value.items():
            if not argument:
                raise ValueError("argument binding names must not be empty")
            if not isinstance(pointer, str):
                raise ValueError("argument binding pointers must be strings")
            _validate_pointer(pointer, field_name=f"argument binding {argument!r}")
        return value

    @field_validator("for_each")
    @classmethod
    def validate_for_each(cls, value: str | None) -> str | None:
        if value is not None:
            _validate_pointer(value, field_name="forEach")
        return value

    @model_validator(mode="after")
    def validate_item_bindings(self) -> Self:
        if self.item_argument_bindings and self.for_each is None:
            raise ValueError("itemArgumentBindings requires forEach")
        overlap = set(self.argument_bindings).intersection(self.item_argument_bindings)
        if overlap:
            raise ValueError(
                "argumentBindings and itemArgumentBindings must not bind the same argument"
            )
        return self


class RequiredToolPlan(BaseModel):
    """Immutable ordered tool requirements before runtime candidate expansion."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-tool-plan/v1"] = Field(
        default=TOOL_PLAN_SCHEMA_VERSION,
        alias="schemaVersion",
    )
    steps: tuple[RequiredToolStep, ...] = Field(min_length=1, max_length=MAX_PLAN_STEPS)
    max_occurrences: int = Field(
        default=MAX_PLAN_OCCURRENCES, alias="maxOccurrences", ge=1, le=MAX_PLAN_OCCURRENCES
    )

    @model_validator(mode="after")
    def validate_unique_step_ids(self) -> Self:
        ids = [step.step_id for step in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("required tool plan stepId values must be unique")
        return self

    @property
    def digest(self) -> str:
        return _sha256_digest(self.model_dump(mode="json", by_alias=True, exclude_none=True))

    def expand(self, runtime_input: Any) -> ExpandedToolPlan:
        """Expand each step in declaration order against bounded JSON-like input."""

        occurrences: list[ToolPlanOccurrence] = []
        for step in self.steps:
            if step.for_each is None:
                candidates = (runtime_input,)
            else:
                selected = _resolve_json_pointer(runtime_input, step.for_each)
                if not isinstance(selected, (list, tuple)):
                    raise ToolPlanExpansionError(
                        f"step {step.step_id!r} forEach pointer {step.for_each!r} must select an array"
                    )
                if len(selected) > step.max_occurrences:
                    raise ToolPlanExpansionError(
                        f"step {step.step_id!r} expands to {len(selected)} occurrences; "
                        f"limit is {step.max_occurrences}"
                    )
                candidates = tuple(selected)

            for occurrence_index, candidate in enumerate(candidates):
                arguments = deepcopy(step.arguments)
                for argument, pointer in step.argument_bindings.items():
                    try:
                        arguments[argument] = deepcopy(
                            _resolve_json_pointer(runtime_input, pointer)
                        )
                    except ToolPlanExpansionError as exc:
                        raise ToolPlanExpansionError(
                            f"step {step.step_id!r} argument {argument!r}: {exc}"
                        ) from exc
                for argument, pointer in step.item_argument_bindings.items():
                    try:
                        arguments[argument] = deepcopy(_resolve_json_pointer(candidate, pointer))
                    except ToolPlanExpansionError as exc:
                        raise ToolPlanExpansionError(
                            f"step {step.step_id!r} item argument {argument!r}: {exc}"
                        ) from exc
                if len(occurrences) >= self.max_occurrences:
                    raise ToolPlanExpansionError(
                        f"required tool plan exceeds its {self.max_occurrences}-occurrence limit"
                    )
                sequence = len(occurrences) + 1
                occurrences.append(
                    ToolPlanOccurrence(
                        occurrenceId=f"{step.step_id}:{occurrence_index}",
                        sequence=sequence,
                        stepId=step.step_id,
                        occurrenceIndex=occurrence_index,
                        toolName=step.tool_name,
                        arguments=arguments,
                        callDigest=tool_call_digest(step.tool_name, arguments),
                    )
                )
        return ExpandedToolPlan(planDigest=self.digest, occurrences=tuple(occurrences))


class ToolPlanOccurrence(BaseModel):
    """One concrete, ordered required call emitted by plan expansion."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    occurrence_id: str = Field(alias="occurrenceId", min_length=1, max_length=255)
    sequence: int = Field(ge=1)
    step_id: str = Field(alias="stepId", min_length=1, max_length=128)
    occurrence_index: int = Field(alias="occurrenceIndex", ge=0)
    tool_name: str = Field(alias="toolName", min_length=1, max_length=255)
    arguments: dict[str, Any]
    call_digest: str = Field(alias="callDigest", pattern=r"^sha256:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_call_digest(self) -> Self:
        if self.call_digest != tool_call_digest(self.tool_name, self.arguments):
            raise ValueError("tool plan occurrence callDigest does not match its exact call")
        return self


class ExpandedToolPlan(BaseModel):
    """Concrete plan snapshot suitable for durable checkpoint/evidence storage."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-tool-plan/v1"] = Field(
        default=TOOL_PLAN_SCHEMA_VERSION,
        alias="schemaVersion",
    )
    plan_digest: str = Field(alias="planDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    occurrences: tuple[ToolPlanOccurrence, ...] = Field(max_length=MAX_PLAN_OCCURRENCES)

    @model_validator(mode="after")
    def validate_occurrences(self) -> Self:
        ids = [item.occurrence_id for item in self.occurrences]
        sequences = [item.sequence for item in self.occurrences]
        if len(ids) != len(set(ids)):
            raise ValueError("expanded tool plan occurrenceId values must be unique")
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("expanded tool plan sequences must be contiguous and ordered")
        return self

    @property
    def digest(self) -> str:
        return _sha256_digest(self.model_dump(mode="json", by_alias=True, exclude_none=True))


class ToolPlanLedgerEntry(BaseModel):
    """Durable state for one occurrence; failed entries remain retryable."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    occurrence_id: str = Field(alias="occurrenceId", min_length=1, max_length=255)
    call_digest: str = Field(alias="callDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    state: ToolPlanOccurrenceState = ToolPlanOccurrenceState.PENDING
    attempt_count: int = Field(default=0, alias="attemptCount", ge=0)
    last_attempt_key: str | None = Field(default=None, alias="lastAttemptKey", max_length=255)
    result_digest: str | None = Field(
        default=None, alias="resultDigest", pattern=r"^sha256:[0-9a-f]{64}$"
    )
    error_code: str | None = Field(default=None, alias="errorCode", min_length=1, max_length=255)


class ToolPlanLedger(BaseModel):
    """Immutable completion ledger that can be serialized and reloaded after restart."""

    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="forbid")

    schema_version: Literal["amesh.agent-tool-plan/v1"] = Field(
        default=TOOL_PLAN_SCHEMA_VERSION,
        alias="schemaVersion",
    )
    plan_digest: str = Field(alias="planDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    expanded_digest: str = Field(alias="expandedDigest", pattern=r"^sha256:[0-9a-f]{64}$")
    occurrences: tuple[ToolPlanOccurrence, ...] = Field(max_length=MAX_PLAN_OCCURRENCES)
    entries: tuple[ToolPlanLedgerEntry, ...] = Field(max_length=MAX_PLAN_OCCURRENCES)

    @classmethod
    def from_expanded(cls, expanded: ExpandedToolPlan) -> ToolPlanLedger:
        return cls(
            planDigest=expanded.plan_digest,
            expandedDigest=expanded.digest,
            occurrences=expanded.occurrences,
            entries=tuple(
                ToolPlanLedgerEntry(occurrenceId=item.occurrence_id, callDigest=item.call_digest)
                for item in expanded.occurrences
            ),
        )

    @model_validator(mode="after")
    def validate_ledger_shape(self) -> Self:
        occurrence_ids = [item.occurrence_id for item in self.occurrences]
        entry_ids = [item.occurrence_id for item in self.entries]
        if occurrence_ids != entry_ids:
            raise ValueError("tool plan ledger entries must match expanded occurrence order")
        if any(
            entry.call_digest != occurrence.call_digest
            for entry, occurrence in zip(self.entries, self.occurrences, strict=True)
        ):
            raise ValueError("tool plan ledger call digests must match expanded occurrences")
        expanded = ExpandedToolPlan(
            planDigest=self.plan_digest,
            occurrences=self.occurrences,
        )
        if self.expanded_digest != expanded.digest:
            raise ValueError("tool plan ledger expandedDigest does not match its occurrences")
        return self

    @property
    def digest(self) -> str:
        return _sha256_digest(self.model_dump(mode="json", by_alias=True, exclude_none=True))

    @property
    def is_complete(self) -> bool:
        return all(entry.state is ToolPlanOccurrenceState.SUCCEEDED for entry in self.entries)

    @property
    def missing_occurrences(self) -> tuple[ToolPlanOccurrence, ...]:
        return tuple(
            occurrence
            for occurrence, entry in zip(self.occurrences, self.entries, strict=True)
            if entry.state is not ToolPlanOccurrenceState.SUCCEEDED
        )

    def match(self, tool_name: str, arguments: dict[str, Any]) -> ToolPlanOccurrence:
        """Match a proposed call to the next unresolved exact occurrence."""

        if not isinstance(arguments, dict):
            raise ToolPlanMatchError("tool plan call arguments must be an object")
        expected_index = self._next_unresolved_index()
        if expected_index is None:
            raise ToolPlanMatchError("required tool plan is already complete")
        proposed_digest = tool_call_digest(tool_name, arguments)
        expected = self.occurrences[expected_index]
        if proposed_digest == expected.call_digest and tool_name == expected.tool_name:
            return expected
        later_match = any(
            entry.state is not ToolPlanOccurrenceState.SUCCEEDED
            and occurrence.call_digest == proposed_digest
            and occurrence.tool_name == tool_name
            for occurrence, entry in zip(
                self.occurrences[expected_index + 1 :],
                self.entries[expected_index + 1 :],
                strict=True,
            )
        )
        if later_match:
            raise ToolPlanOrderError(
                f"tool call {tool_name!r} matches a later required occurrence before {expected.occurrence_id!r}"
            )
        raise ToolPlanMatchError(
            f"tool call {tool_name!r} does not match required occurrence {expected.occurrence_id!r}"
        )

    def record_success(
        self,
        occurrence: ToolPlanOccurrence,
        *,
        attempt_key: str,
        result_digest: str | None = None,
    ) -> ToolPlanLedger:
        _validate_attempt_key(attempt_key)
        _validate_result_digest(result_digest)
        index = self._validate_occurrence_identity(occurrence)
        entry = self.entries[index]
        if entry.state is ToolPlanOccurrenceState.SUCCEEDED:
            if entry.result_digest is not None and result_digest != entry.result_digest:
                raise ToolPlanLedgerError(
                    f"successful occurrence {occurrence.occurrence_id!r} has a conflicting result"
                )
            return self
        self._validate_occurrence_order(index)
        updated = entry.model_copy(
            update={
                "state": ToolPlanOccurrenceState.SUCCEEDED,
                "attempt_count": entry.attempt_count + 1,
                "last_attempt_key": attempt_key,
                "result_digest": result_digest,
                "error_code": None,
            }
        )
        return self.model_copy(
            update={"entries": (*self.entries[:index], updated, *self.entries[index + 1 :])}
        )

    def record_failure(
        self,
        occurrence: ToolPlanOccurrence,
        *,
        attempt_key: str,
        error_code: str,
    ) -> ToolPlanLedger:
        _validate_attempt_key(attempt_key)
        if not error_code or len(error_code) > 255:
            raise ToolPlanLedgerError(
                "tool plan failure error_code must contain 1 to 255 characters"
            )
        index = self._validate_occurrence_identity(occurrence)
        entry = self.entries[index]
        if entry.state is ToolPlanOccurrenceState.SUCCEEDED:
            raise ToolPlanLedgerError(
                f"successful occurrence {occurrence.occurrence_id!r} cannot be failed"
            )
        self._validate_occurrence_order(index)
        if (
            entry.state is ToolPlanOccurrenceState.FAILED
            and entry.last_attempt_key == attempt_key
            and entry.error_code == error_code
        ):
            return self
        updated = entry.model_copy(
            update={
                "state": ToolPlanOccurrenceState.FAILED,
                "attempt_count": entry.attempt_count + 1,
                "last_attempt_key": attempt_key,
                "error_code": error_code,
            }
        )
        return self.model_copy(
            update={"entries": (*self.entries[:index], updated, *self.entries[index + 1 :])}
        )

    def _next_unresolved_index(self) -> int | None:
        return next(
            (
                index
                for index, entry in enumerate(self.entries)
                if entry.state is not ToolPlanOccurrenceState.SUCCEEDED
            ),
            None,
        )

    def _validate_occurrence_identity(self, occurrence: ToolPlanOccurrence) -> int:
        index = next(
            (
                index
                for index, item in enumerate(self.occurrences)
                if item.occurrence_id == occurrence.occurrence_id
            ),
            None,
        )
        if index is None or self.occurrences[index] != occurrence:
            raise ToolPlanLedgerError("tool plan occurrence is not the exact expanded occurrence")
        return index

    def _validate_occurrence_order(self, index: int) -> None:
        expected_index = self._next_unresolved_index()
        if expected_index is None:
            raise ToolPlanLedgerError("required tool plan is already complete")
        if index != expected_index:
            raise ToolPlanOrderError(
                f"occurrence {self.occurrences[index].occurrence_id!r} is not the next unresolved required occurrence"
            )


def tool_call_digest(tool_name: str, arguments: dict[str, Any]) -> str:
    """Return the canonical digest used for exact tool-call matching."""

    if not isinstance(tool_name, str) or not tool_name:
        raise ToolPlanMatchError("tool call tool_name must be a non-empty string")
    if not isinstance(arguments, dict):
        raise ToolPlanMatchError("tool call arguments must be an object")
    try:
        return _sha256_digest({"toolName": tool_name, "arguments": arguments})
    except (TypeError, ValueError) as exc:
        raise ToolPlanMatchError("tool call arguments must be canonical JSON") from exc


def expand_tool_plan(plan: RequiredToolPlan, runtime_input: Any) -> ExpandedToolPlan:
    """Functional convenience wrapper for callers that prefer a function boundary."""

    return plan.expand(runtime_input)


def _sha256_digest(value: Any) -> str:
    return "sha256:" + canonical_hash(value)


def _resolve_json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ToolPlanExpansionError(f"pointer {pointer!r} is not an RFC 6901 JSON Pointer")
    current = value
    for encoded_token in pointer[1:].split("/"):
        token = encoded_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping) and token in current:
            current = current[token]
            continue
        if (
            isinstance(current, (list, tuple))
            and token.isdecimal()
            and (token == "0" or not token.startswith("0"))
        ):
            index = int(token)
            if index < len(current):
                current = current[index]
                continue
        raise ToolPlanExpansionError(f"pointer {pointer!r} does not resolve")
    return current


def _validate_attempt_key(value: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 255:
        raise ToolPlanLedgerError("tool plan attempt_key must contain 1 to 255 characters")


def _validate_result_digest(value: str | None) -> None:
    if value is not None and not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ToolPlanLedgerError("tool plan result_digest must be a sha256 digest")


__all__ = [
    "MAX_PLAN_OCCURRENCES",
    "MAX_PLAN_STEPS",
    "MAX_STEP_OCCURRENCES",
    "TOOL_PLAN_SCHEMA_VERSION",
    "ExpandedToolPlan",
    "RequiredToolPlan",
    "RequiredToolStep",
    "ToolPlanError",
    "ToolPlanExpansionError",
    "ToolPlanLedger",
    "ToolPlanLedgerEntry",
    "ToolPlanLedgerError",
    "ToolPlanMatchError",
    "ToolPlanOccurrence",
    "ToolPlanOccurrenceState",
    "ToolPlanOrderError",
    "expand_tool_plan",
    "tool_call_digest",
]
