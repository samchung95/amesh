from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import timedelta
from typing import Any, cast
from uuid import uuid5

from amesh.admission_policy import AdmissionPolicyDenied, policy_decision_metadata
from amesh.domain import (
    AdmissionOutcome,
    AdmissionResourceType,
    FailureCategory,
    resolve_admission_policies,
)
from amesh.dsl import ConditionErrorPolicy, FlowDefinition, compile_flow_tasks
from amesh.dsl.models import TaskDefinition
from amesh.expressions import ExpressionContext, ExpressionEngine
from amesh.ports import (
    ExecutionRepository,
    PersistedExecution,
    PersistedTaskRun,
    TaskCacheDecision,
    TaskCacheKey,
    TaskCacheLookup,
    TaskCacheMode,
    TaskCacheRepository,
    TaskRunState,
    TaskStateConflictError,
    redact_runner_payload,
)

from .contracts import (
    ConditionDecision,
    DispatchPolicyEnforcer,
    LoopExecutionFailure,
    TaskCancellationChannel,
    TaskConfigurationError,
    TaskContextResources,
    TaskDeferral,
    TaskExecutionContext,
    TaskExecutionFailure,
    TaskExecutionPaused,
    TaskHandler,
    TaskHandlerResult,
    TaskPlatformError,
    TaskRunOutcome,
    classify_task_failure,
    retry_delay_seconds,
)
from .flowable_core import (
    _expression_context,
    _merge_completion_evidence,
    _merge_task_control,
    _redacted_condition_inputs,
    _user_trigger_context,
)
from .loops import LOOP_TASK_TYPES, LoopIterationContext
from .task_handlers import (
    _combine_declared_files,
    _render_declared_files,
    _render_task_for_execution,
)
from .task_results import (
    _abandon_cache_population,
    _execution_cache_mode,
    _with_cache_evidence,
    derive_task_cache_key,
    normalize_task_completion,
)

LOGGER = logging.getLogger("amesh.task.core.log")


@dataclass(frozen=True)
class AttemptExecutionCallbacks:
    repository: ExecutionRepository
    handlers: Mapping[str, TaskHandler]
    expressions: ExpressionEngine
    evaluate_task_condition: Callable[..., ConditionDecision]
    resolve_context_resources: Callable[..., Awaitable[TaskContextResources]]
    run_loop: Callable[..., Awaitable[dict[str, Any]]]
    task_cache: TaskCacheRepository | None = None
    dispatch_policy_enforcer: DispatchPolicyEnforcer | None = None


_Deps = AttemptExecutionCallbacks


@dataclass
class _AttemptState:
    flow: FlowDefinition
    execution: PersistedExecution
    running: PersistedTaskRun
    task: TaskDefinition
    outputs: Mapping[str, dict[str, Any]]
    condition: ConditionDecision
    expression_context: ExpressionContext
    handler: TaskHandler | None
    workspace_parent: TaskDefinition | None
    iteration: LoopIterationContext | None
    cache_key: TaskCacheKey | None = None
    cache_lookup: TaskCacheLookup | None = None
    secret_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class _RetryDecision:
    eligible: bool
    category: FailureCategory
    reason: str
    evidence: dict[str, object]
    running: PersistedTaskRun


async def execute_task_attempt(
    callbacks: AttemptExecutionCallbacks,
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
    workspace_parent: TaskDefinition | None = None,
    iteration: LoopIterationContext | None = None,
    handler_error: Mapping[str, Any] | None = None,
) -> TaskRunOutcome:
    """Run one fenced task attempt while the repository remains authoritative."""

    prepared = await _prepare_attempt(
        callbacks,
        flow,
        execution,
        task_run,
        task,
        outputs,
        workspace_parent,
        iteration,
        handler_error,
    )
    if isinstance(prepared, TaskRunOutcome):
        return prepared
    try:
        return await _execute_started_attempt(callbacks, prepared)
    except TaskExecutionPaused:
        return TaskRunOutcome(claimed=True)
    except Exception as exc:
        return await _handle_attempt_failure(callbacks, prepared, exc)


async def _prepare_attempt(
    callbacks: _Deps,
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    outputs: Mapping[str, dict[str, Any]],
    workspace_parent: TaskDefinition | None,
    iteration: LoopIterationContext | None,
    handler_error: Mapping[str, Any] | None,
) -> _AttemptState | TaskRunOutcome:
    projected = _projected_task_run(task_run)
    context = _expression_context(
        flow,
        execution,
        projected,
        task,
        outputs,
        iteration=iteration,
        handler_error=handler_error,
    )
    admission = await _request_task_admission(
        callbacks,
        flow,
        execution,
        task_run,
        task,
        context,
    )
    if admission is not None:
        return admission
    condition = (
        ConditionDecision(matched=True, evidence=task_run.evidence)
        if task_run.state is TaskRunState.RUNNING
        else callbacks.evaluate_task_condition(
            flow,
            execution,
            task,
            context,
            handler_error,
        )
    )
    skipped = await _skip_unmatched_task(callbacks, task_run, condition, execution.tenant_id)
    if skipped is not None:
        return skipped
    dispatched = await _enforce_dispatch_policy(
        callbacks,
        flow,
        execution,
        task_run,
        task,
        condition,
    )
    if isinstance(dispatched, TaskRunOutcome):
        return dispatched
    condition = dispatched
    running = await _start_task(callbacks, task_run, task, condition, execution.tenant_id)
    if running is None:
        return TaskRunOutcome(claimed=False)
    handler, validation_failure = await _validate_started_attempt(
        callbacks,
        running,
        task,
        condition,
        execution.tenant_id,
    )
    if validation_failure is not None:
        return validation_failure
    return _AttemptState(
        flow=flow,
        execution=execution,
        running=running,
        task=task,
        outputs=outputs,
        condition=condition,
        expression_context=context,
        handler=handler,
        workspace_parent=workspace_parent,
        iteration=iteration,
    )


def _projected_task_run(task_run: PersistedTaskRun) -> PersistedTaskRun:
    if task_run.state is TaskRunState.RUNNING:
        return task_run
    return task_run.model_copy(
        update={
            "state": TaskRunState.RUNNING,
            "current_attempt": task_run.current_attempt + 1,
        }
    )


async def _request_task_admission(
    callbacks: _Deps,
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    context: ExpressionContext,
) -> TaskRunOutcome | None:
    if not task.concurrency or task_run.state is TaskRunState.RUNNING:
        return None
    admission = await callbacks.repository.request_admission(
        AdmissionResourceType.TASK,
        task_run.task_run_id,
        resolve_admission_policies(
            task.concurrency,
            resource_type=AdmissionResourceType.TASK,
            tenant_id=execution.tenant_id,
            namespace=flow.namespace,
            flow_id=flow.id,
            render_key=lambda value: callbacks.expressions.render_value(value, context),
        ),
        tenant_id=execution.tenant_id,
        priority=task.priority,
    )
    if admission.outcome is AdmissionOutcome.QUEUED:
        await callbacks.repository.reconcile_admission(
            tenant_id=execution.tenant_id,
            limit=100,
        )
        return TaskRunOutcome(claimed=False)
    if admission.outcome in {
        AdmissionOutcome.CANCELLED,
        AdmissionOutcome.FAILED,
        AdmissionOutcome.SKIPPED,
    }:
        failure = admission.reason if admission.outcome is not AdmissionOutcome.SKIPPED else None
        return TaskRunOutcome(claimed=True, failure=failure)
    return None


async def _skip_unmatched_task(
    callbacks: _Deps,
    task_run: PersistedTaskRun,
    condition: ConditionDecision,
    tenant_id: str,
) -> TaskRunOutcome | None:
    if condition.matched or condition.error is not None:
        return None
    try:
        await callbacks.repository.skip_task(
            task_run.task_run_id,
            {"skipped": True},
            tenant_id=tenant_id,
            evidence=condition.evidence,
        )
    except TaskStateConflictError:
        return TaskRunOutcome(claimed=False)
    return TaskRunOutcome(claimed=True)


async def _enforce_dispatch_policy(
    callbacks: _Deps,
    flow: FlowDefinition,
    execution: PersistedExecution,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    condition: ConditionDecision,
) -> ConditionDecision | TaskRunOutcome:
    enforcer = callbacks.dispatch_policy_enforcer
    if condition.error is not None or enforcer is None:
        return condition
    try:
        policy_decision = await enforcer(flow, execution, task_run, task)
    except AdmissionPolicyDenied as exc:
        evidence = _merge_task_control(
            condition.evidence,
            "policy",
            policy_decision_metadata(exc.decision),
        )
        try:
            denied_run = (
                task_run
                if task_run.state is TaskRunState.RUNNING
                else await callbacks.repository.start_task(
                    task_run.task_run_id,
                    tenant_id=execution.tenant_id,
                    dispatch=False,
                )
            )
            await callbacks.repository.fail_task(
                denied_run.task_run_id,
                denied_run.current_attempt,
                str(exc),
                tenant_id=execution.tenant_id,
                failure_category=FailureCategory.CONFIGURATION,
                evidence=evidence,
            )
        except TaskStateConflictError:
            return TaskRunOutcome(claimed=False)
        return TaskRunOutcome(claimed=True, failure=str(exc))
    return ConditionDecision(
        matched=condition.matched,
        evidence=_merge_task_control(
            condition.evidence,
            "policy",
            policy_decision_metadata(policy_decision),
        ),
    )


async def _start_task(
    callbacks: _Deps,
    task_run: PersistedTaskRun,
    task: TaskDefinition,
    condition: ConditionDecision,
    tenant_id: str,
) -> PersistedTaskRun | None:
    try:
        if task_run.state is TaskRunState.RUNNING:
            return task_run
        return await callbacks.repository.start_task(
            task_run.task_run_id,
            tenant_id=tenant_id,
            dispatch=condition.matched,
            priority=task.priority,
            worker_group=task.worker_group,
        )
    except TaskStateConflictError:
        return None


async def _validate_started_attempt(
    callbacks: _Deps,
    running: PersistedTaskRun,
    task: TaskDefinition,
    condition: ConditionDecision,
    tenant_id: str,
) -> tuple[TaskHandler | None, TaskRunOutcome | None]:
    if condition.error is not None:
        reason = f"task {task.id!r} runIf failed: {condition.error}"
        await callbacks.repository.fail_task(
            running.task_run_id,
            running.current_attempt,
            reason,
            tenant_id=tenant_id,
            failure_category=FailureCategory.CONFIGURATION,
            evidence=condition.evidence,
        )
        return None, TaskRunOutcome(claimed=True, failure=reason)
    handler = callbacks.handlers.get(task.type)
    if handler is not None or task.type in LOOP_TASK_TYPES:
        return handler, None
    reason = f"no in-process handler registered for task type {task.type!r}"
    await callbacks.repository.fail_task(
        running.task_run_id,
        running.current_attempt,
        reason,
        tenant_id=tenant_id,
        evidence=condition.evidence,
    )
    return None, TaskRunOutcome(claimed=True, failure=reason)


async def _execute_started_attempt(
    callbacks: _Deps,
    state: _AttemptState,
) -> TaskRunOutcome:
    rendered_task, context = await _build_execution_context(callbacks, state)
    if await _lookup_task_cache(callbacks, state, rendered_task, context):
        return TaskRunOutcome(claimed=True)
    result = await _invoke_with_timeout(callbacks, state, rendered_task, context)
    if isinstance(result, TaskDeferral):
        return await _persist_deferral(callbacks, state, result)
    output, evidence = normalize_task_completion(
        result,
        rendered_task.contract.resource_limits,
        secret_values=context.secrets.values(),
    )
    await callbacks.repository.complete_task(
        state.running.task_run_id,
        state.running.current_attempt,
        output,
        tenant_id=state.execution.tenant_id,
        evidence=_merge_completion_evidence(
            (
                _with_cache_evidence(evidence, state.cache_lookup)
                if state.cache_lookup is not None
                else evidence
            ),
            state.condition.evidence,
        ),
    )
    await _publish_cache_best_effort(callbacks, state, output, evidence)
    return TaskRunOutcome(claimed=True)


async def _build_execution_context(
    callbacks: _Deps,
    state: _AttemptState,
) -> tuple[TaskDefinition, TaskExecutionContext]:
    resources = await callbacks.resolve_context_resources(
        state.task,
        state.execution,
        state.running,
        declared_files={},
        strict_files=False,
    )
    state.secret_values = tuple(resources.secrets.values())
    runtime_expression_context = replace(
        state.expression_context,
        secrets=resources.secrets,
        key_values=resources.key_values,
    )
    rendered_task = _render_task_for_execution(
        callbacks.expressions,
        state.task,
        runtime_expression_context,
    )
    declared_files = _declared_execution_files(
        callbacks,
        state.workspace_parent,
        rendered_task,
        runtime_expression_context,
    )
    file_resources = await callbacks.resolve_context_resources(
        rendered_task.model_copy(
            update={"contract": rendered_task.contract.model_copy(update={"files": {}})}
        ),
        state.execution,
        state.running,
        declared_files=declared_files,
        resolve_values=False,
    )
    workspace_parent = state.workspace_parent
    context = TaskExecutionContext(
        tenant_id=state.execution.tenant_id,
        execution_id=state.execution.execution_id,
        task_run_id=state.running.task_run_id,
        attempt=state.running.current_attempt,
        attempt_id=uuid5(
            state.running.task_run_id,
            f"attempt:{state.running.current_attempt}",
        ),
        inputs=state.execution.inputs,
        outputs=state.outputs,
        task_types={node.task.id: node.task.type for node in compile_flow_tasks(state.flow)},
        variables=state.flow.variables,
        namespace=state.execution.namespace,
        labels=state.execution.labels,
        trigger=_user_trigger_context(state.execution),
        iteration=state.iteration,
        secret_scopes=rendered_task.contract.secret_scopes,
        secrets=resources.secrets,
        files=file_resources.files,
        file_references=file_resources.file_references,
        key_values=resources.key_values,
        workspace_scope_id=workspace_parent.id if workspace_parent is not None else None,
        workspace_quota_bytes=(
            min(rendered_task.workspace_quota_bytes, workspace_parent.workspace_quota_bytes)
            if workspace_parent is not None
            else rendered_task.workspace_quota_bytes
        ),
        cancellation=TaskCancellationChannel(
            callbacks.repository,
            tenant_id=state.execution.tenant_id,
            execution_id=state.execution.execution_id,
        ),
    )
    return rendered_task, context


def _declared_execution_files(
    callbacks: _Deps,
    workspace_parent: TaskDefinition | None,
    rendered_task: TaskDefinition,
    context: ExpressionContext,
) -> dict[str, str]:
    parent_files = (
        _render_declared_files(
            callbacks.expressions,
            _combine_declared_files(
                workspace_parent.contract.files,
                workspace_parent.input_files,
            ),
            context,
        )
        if workspace_parent is not None
        else {}
    )
    task_files = _render_declared_files(
        callbacks.expressions,
        _combine_declared_files(
            rendered_task.contract.files,
            rendered_task.input_files,
        ),
        context,
    )
    return _combine_declared_files(parent_files, task_files)


async def _lookup_task_cache(
    callbacks: _Deps,
    state: _AttemptState,
    rendered_task: TaskDefinition,
    context: TaskExecutionContext,
) -> bool:
    if rendered_task.task_cache.enabled and callbacks.task_cache is None:
        raise TaskPlatformError("task cache repository is unavailable")
    if not rendered_task.task_cache.enabled or callbacks.task_cache is None:
        return False
    state.cache_key = derive_task_cache_key(
        state.flow,
        state.execution,
        rendered_task,
        context,
    )
    cache_mode = _execution_cache_mode(state.execution)
    if cache_mode is TaskCacheMode.BYPASS:
        reason = "execution requested cache bypass; task handler ran normally"
        await callbacks.task_cache.record_bypass(
            state.cache_key,
            tenant_id=state.execution.tenant_id,
            execution_id=state.execution.execution_id,
            task_run_id=state.running.task_run_id,
            attempt=state.running.current_attempt,
            reason=reason,
        )
        state.cache_lookup = TaskCacheLookup(
            decision=TaskCacheDecision.BYPASS,
            reason=reason,
            key_hash=state.cache_key.key_hash,
        )
    else:
        state.cache_lookup = await callbacks.task_cache.lookup_or_reserve(
            state.cache_key,
            tenant_id=state.execution.tenant_id,
            execution_id=state.execution.execution_id,
            task_run_id=state.running.task_run_id,
            attempt=state.running.current_attempt,
            mode=cache_mode,
        )
    if state.cache_lookup.decision is not TaskCacheDecision.HIT:
        return False
    await callbacks.repository.complete_task(
        state.running.task_run_id,
        state.running.current_attempt,
        state.cache_lookup.output or {},
        tenant_id=state.execution.tenant_id,
        evidence=_with_cache_evidence(
            _merge_completion_evidence(
                state.cache_lookup.evidence or {},
                state.condition.evidence,
            ),
            state.cache_lookup,
        ),
    )
    return True


async def _invoke_with_timeout(
    callbacks: _Deps,
    state: _AttemptState,
    rendered_task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskHandlerResult:
    if state.task.timeout_seconds is None:
        return await _invoke_handler(callbacks, state, rendered_task, context)
    async with asyncio.timeout(state.task.timeout_seconds):
        return await _invoke_handler(callbacks, state, rendered_task, context)


async def _invoke_handler(
    callbacks: _Deps,
    state: _AttemptState,
    rendered_task: TaskDefinition,
    context: TaskExecutionContext,
) -> TaskHandlerResult:
    if rendered_task.type in LOOP_TASK_TYPES:
        return await callbacks.run_loop(
            state.flow,
            state.execution,
            state.running,
            rendered_task,
            state.outputs,
        )
    if state.handler is None:
        raise TaskConfigurationError(
            f"no in-process handler registered for task type {state.task.type!r}"
        )
    return await state.handler(rendered_task, context)


async def _persist_deferral(
    callbacks: _Deps,
    state: _AttemptState,
    result: TaskDeferral,
) -> TaskRunOutcome:
    if state.cache_key is not None and state.cache_lookup is not None:
        with suppress(Exception):
            await _abandon_cache_population(
                callbacks.task_cache,
                state.cache_key,
                state.cache_lookup,
                tenant_id=state.execution.tenant_id,
                execution_id=state.execution.execution_id,
                task_run_id=state.running.task_run_id,
                attempt=state.running.current_attempt,
                reason="deferred task results cannot populate the cache",
            )
    await callbacks.repository.defer_task(
        state.running.task_run_id,
        state.running.current_attempt,
        result.resume_token,
        tenant_id=state.execution.tenant_id,
        metadata=result.metadata,
        expires_at=result.expires_at,
    )
    return TaskRunOutcome(claimed=True)


async def _publish_cache_best_effort(
    callbacks: _Deps,
    state: _AttemptState,
    output: dict[str, Any],
    evidence: dict[str, Any],
) -> None:
    if (
        callbacks.task_cache is None
        or state.cache_key is None
        or state.cache_lookup is None
        or state.cache_lookup.owner_token is None
    ):
        return
    try:
        await callbacks.task_cache.publish(
            state.cache_key.key_hash,
            state.cache_lookup.owner_token,
            output,
            evidence,
            tenant_id=state.execution.tenant_id,
            execution_id=state.execution.execution_id,
            task_run_id=state.running.task_run_id,
            attempt=state.running.current_attempt,
        )
    except Exception:
        LOGGER.exception(
            "task result cache publication failed; execution result remains committed",
            extra=_cache_log_context(state),
        )
        try:
            await _abandon_cache_population(
                callbacks.task_cache,
                state.cache_key,
                state.cache_lookup,
                tenant_id=state.execution.tenant_id,
                execution_id=state.execution.execution_id,
                task_run_id=state.running.task_run_id,
                attempt=state.running.current_attempt,
                reason="cache publication failed after task completion",
            )
        except Exception:
            LOGGER.warning(
                "cache abandonment failed after authoritative task completion; "
                "preserving the committed task result",
                extra=_cache_log_context(state),
            )


def _cache_log_context(state: _AttemptState) -> dict[str, object]:
    return {
        "tenant_id": state.execution.tenant_id,
        "execution_id": str(state.execution.execution_id),
        "task_run_id": str(state.running.task_run_id),
        "cache_key_hash": state.cache_key.key_hash if state.cache_key is not None else None,
    }


async def _handle_attempt_failure(
    callbacks: _Deps,
    state: _AttemptState,
    exc: Exception,
) -> TaskRunOutcome:
    abandonment_failure = await _abandon_failed_cache(callbacks, state, exc)
    category = classify_task_failure(exc)
    safe_message = redact_runner_payload(str(exc), state.secret_values)
    reason = f"task {state.task.id!r} failed [{category.value}]: {safe_message}"
    evidence = _merge_completion_evidence(
        (
            exc.evidence
            if isinstance(exc, TaskExecutionFailure) and exc.evidence is not None
            else {}
        ),
        state.condition.evidence,
    )
    evidence = cast(
        dict[str, object],
        redact_runner_payload(evidence, state.secret_values),
    )
    if abandonment_failure is not None:
        abandonment_message = redact_runner_payload(str(abandonment_failure), state.secret_values)
        reason = (
            f"{reason}; cache abandonment failed "
            f"[{type(abandonment_failure).__name__}]: {abandonment_message}"
        )
        evidence = _merge_task_control(
            evidence,
            "cacheAbandonment",
            {
                "state": "FAILED",
                "errorType": type(abandonment_failure).__name__,
                "error": abandonment_message,
            },
        )
    if category is FailureCategory.CANCELLED:
        await callbacks.repository.cancel_task(
            state.running.task_run_id,
            state.running.current_attempt,
            reason,
            tenant_id=state.execution.tenant_id,
        )
        return TaskRunOutcome(claimed=True, failure=reason)
    retry = await _evaluate_retry(callbacks, state, category, reason, evidence)
    if retry.eligible:
        database_now = await callbacks.repository.database_time()
        retry_at = database_now + timedelta(
            seconds=retry_delay_seconds(
                state.task.retry,
                retry.running.task_run_id,
                retry.running.current_attempt,
            )
        )
        await callbacks.repository.retry_task(
            retry.running.task_run_id,
            retry.running.current_attempt,
            retry_at=retry_at,
            reason=retry.reason,
            tenant_id=state.execution.tenant_id,
            failure_category=retry.category,
        )
        return TaskRunOutcome(claimed=True)
    failure_result: dict[str, object] | None = (
        cast(dict[str, object], redact_runner_payload(exc.result, state.secret_values))
        if isinstance(exc, (LoopExecutionFailure, TaskExecutionFailure)) and exc.result is not None
        else None
    )
    await callbacks.repository.fail_task(
        retry.running.task_run_id,
        retry.running.current_attempt,
        retry.reason,
        tenant_id=state.execution.tenant_id,
        result=failure_result,
        failure_category=retry.category,
        evidence=retry.evidence,
    )
    return TaskRunOutcome(claimed=True, failure=retry.reason)


async def _abandon_failed_cache(
    callbacks: _Deps,
    state: _AttemptState,
    exc: Exception,
) -> Exception | None:
    if state.cache_key is None or state.cache_lookup is None:
        return None
    try:
        await _abandon_cache_population(
            callbacks.task_cache,
            state.cache_key,
            state.cache_lookup,
            tenant_id=state.execution.tenant_id,
            execution_id=state.execution.execution_id,
            task_run_id=state.running.task_run_id,
            attempt=state.running.current_attempt,
            reason=f"cache population abandoned after task failure: {type(exc).__name__}",
        )
    except Exception as abandonment_exc:
        return abandonment_exc
    return None


async def _evaluate_retry(
    callbacks: _Deps,
    state: _AttemptState,
    category: FailureCategory,
    reason: str,
    evidence: dict[str, object],
) -> _RetryDecision:
    eligible = (
        category
        in {
            FailureCategory.RETRYABLE,
            FailureCategory.TIMED_OUT,
            FailureCategory.INFRASTRUCTURE,
        }
        and state.running.current_attempt < state.task.retry.max_attempts
    )
    running = state.running
    if not eligible or state.task.retry.condition is None:
        return _RetryDecision(eligible, category, reason, evidence, running)
    retry_context = _expression_context(
        state.flow,
        state.execution,
        running,
        state.task,
        state.outputs,
        iteration=state.iteration,
        failure_category=category,
        error=reason,
    )
    retry_record: dict[str, object] = {
        "kind": "retry",
        "expression": state.task.retry.condition,
        "conditionInputs": _redacted_condition_inputs(
            state.flow,
            state.execution,
            retry_context,
        ),
        "policy": state.task.retry.condition_error_policy.value,
    }
    try:
        eligible = callbacks.expressions.evaluate_condition(
            state.task.retry.condition,
            retry_context,
        )
        retry_record["result"] = eligible
    except Exception as retry_exc:
        eligible = False
        retry_record.update(
            {
                "result": False,
                "error": {
                    "type": type(retry_exc).__name__,
                    "message": redact_runner_payload(str(retry_exc), state.secret_values),
                },
            }
        )
        if state.task.retry.condition_error_policy is ConditionErrorPolicy.FAIL:
            category = FailureCategory.CONFIGURATION
            reason = f"{reason}; retry condition failed: {retry_exc}"
    evidence = _merge_task_control(evidence, "retry", retry_record)
    running = await callbacks.repository.record_task_control(
        running.task_run_id,
        running.current_attempt,
        evidence,
        tenant_id=state.execution.tenant_id,
    )
    return _RetryDecision(eligible, category, reason, evidence, running)
