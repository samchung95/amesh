from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from amesh.domain import (
    FLOW_TEST_SIMULATOR_VERSION,
    FlowTestAssertion,
    FlowTestCaseResult,
    FlowTestCoverage,
    FlowTestDefinition,
    FlowTestDefinitionCreateRequest,
    FlowTestFixture,
    FlowTestGateDecision,
    FlowTestOutcome,
    FlowTestRunRequest,
    FlowTestRunResult,
    FlowTestTaskState,
    SimulatedTaskResult,
)
from amesh.dsl import FlowDefinition, LifecyclePhase, PlannedTask, compile_execution_tasks
from amesh.dsl.models import ConditionErrorPolicy, TaskDefinition
from amesh.expressions import ExpressionContext, NativeExpressionEngine
from amesh.ports import ExecutionRepository, FlowTestRepository
from amesh.workflow.data_contracts import validate_flow_inputs


@dataclass
class _CoverageCounters:
    tasks_total: int
    tasks_covered: int = 0
    branches_total: int = 0
    branches_covered: int = 0
    handlers_total: int = 0
    handlers_covered: int = 0
    conditions_total: int = 0
    conditions_covered: int = 0


class FlowTestSimulator:
    """Pure deterministic workflow simulator for revision-pinned unit tests."""

    def __init__(self) -> None:
        self._expressions = NativeExpressionEngine()

    def simulate(
        self,
        flow: FlowDefinition,
        definition: FlowTestDefinition,
        *,
        trigger_context: dict[str, Any] | None = None,
    ) -> FlowTestCaseResult:
        _reject_sensitive_test_values(
            {
                "inputs": definition.inputs,
                "variables": definition.variables,
                "fixtures": {
                    key: fixture.model_dump(mode="python")
                    for key, fixture in definition.fixtures.items()
                },
            }
        )
        inputs = validate_flow_inputs(flow, definition.inputs)
        variables = {**flow.variables, **definition.variables}
        plan = compile_execution_tasks(flow)
        plan_by_id = {node.task.id: node for node in plan}
        results: list[SimulatedTaskResult] = []
        outputs: dict[str, Any] = {}
        selected_paths: dict[str, str] = {}
        counters = _CoverageCounters(
            tasks_total=len(plan),
            branches_total=sum(
                len(node.task.child_task_groups()) for node in plan if node.mode in {"IF", "SWITCH"}
            ),
            handlers_total=sum(
                1
                for node in plan
                if node.lifecycle_phase
                in {LifecyclePhase.ERROR, LifecyclePhase.FINALLY, LifecyclePhase.AFTER_EXECUTION}
            ),
            conditions_total=sum(
                int(node.task.run_if is not None) + _branch_condition_count(node.task)
                for node in plan
            ),
        )
        failed_task_ids: set[str] = set()

        for node in plan:
            if node.lifecycle_phase is not LifecyclePhase.MAIN:
                continue
            if not self._branch_is_active(node, plan_by_id, selected_paths):
                results.append(_skipped_result(node, "branch not selected"))
                continue
            if any(
                result.state is FlowTestTaskState.FAILED
                for result in results
                if result.task_id in node.dependencies
            ):
                results.append(_skipped_result(node, "dependency failed"))
                continue
            task_result, generated, selected = self._execute_task(
                flow,
                node.task,
                task_id=node.task.id,
                lifecycle_phase=node.lifecycle_phase.value,
                inputs=inputs,
                variables=variables,
                outputs=outputs,
                fixtures=definition.fixtures,
                iteration={},
                trigger_context=trigger_context or {},
                counters=counters,
            )
            results.append(task_result)
            results.extend(generated)
            counters.tasks_covered += int(task_result.state is not FlowTestTaskState.SKIPPED)
            counters.tasks_total += len(generated)
            counters.tasks_covered += sum(
                result.state is not FlowTestTaskState.SKIPPED for result in generated
            )
            if task_result.output is not None:
                outputs[node.task.id] = task_result.output
            if selected is not None:
                selected_paths[node.task.id] = (
                    f"{node.branch_id}/{selected}" if node.branch_id is not None else selected
                )
                counters.branches_covered += 1
            if task_result.state is FlowTestTaskState.FAILED:
                failed_task_ids.add(node.task.id)

        for node in plan:
            should_run = False
            if node.lifecycle_phase is LifecyclePhase.ERROR:
                should_run = bool(failed_task_ids) and node.handler_owner_id in {
                    "flow",
                    *failed_task_ids,
                }
            elif node.lifecycle_phase in {LifecyclePhase.FINALLY, LifecyclePhase.AFTER_EXECUTION}:
                should_run = True
            else:
                continue
            if not should_run:
                results.append(_skipped_result(node, "handler not selected"))
                continue
            task_result, generated, _ = self._execute_task(
                flow,
                node.task,
                task_id=node.task.id,
                lifecycle_phase=node.lifecycle_phase.value,
                inputs=inputs,
                variables=variables,
                outputs=outputs,
                fixtures=definition.fixtures,
                iteration={},
                trigger_context=trigger_context or {},
                counters=counters,
            )
            results.append(task_result)
            results.extend(generated)
            counters.tasks_covered += int(task_result.state is not FlowTestTaskState.SKIPPED)
            counters.tasks_total += len(generated)
            counters.tasks_covered += sum(
                result.state is not FlowTestTaskState.SKIPPED for result in generated
            )
            counters.handlers_covered += int(task_result.state is not FlowTestTaskState.SKIPPED)
            if task_result.output is not None:
                outputs[node.task.id] = task_result.output

        state = (
            FlowTestTaskState.FAILED
            if any(result.state is FlowTestTaskState.FAILED for result in results)
            else FlowTestTaskState.SUCCESS
        )
        rendered_outputs = self._expressions.render_value(
            flow.outputs,
            _expression_context(flow, inputs, variables, outputs, {}),
        )
        if not isinstance(rendered_outputs, dict):
            raise ValueError("flow outputs must render to an object")
        assertions = _assert_expectations(
            definition,
            state=state,
            outputs=rendered_outputs,
            task_results=results,
        )
        coverage = _coverage(counters)
        return FlowTestCaseResult(
            testId=definition.test_id,
            outcome=(
                FlowTestOutcome.PASSED
                if all(assertion.passed for assertion in assertions)
                else FlowTestOutcome.FAILED
            ),
            state=state,
            outputs=rendered_outputs,
            tasks=tuple(results),
            assertions=assertions,
            coverage=coverage,
        )

    def _execute_task(
        self,
        flow: FlowDefinition,
        task: TaskDefinition,
        *,
        task_id: str,
        lifecycle_phase: str,
        inputs: dict[str, Any],
        variables: dict[str, Any],
        outputs: dict[str, Any],
        fixtures: dict[str, FlowTestFixture],
        iteration: dict[str, Any],
        trigger_context: dict[str, Any],
        counters: _CoverageCounters,
    ) -> tuple[SimulatedTaskResult, tuple[SimulatedTaskResult, ...], str | None]:
        context = _expression_context(
            flow,
            inputs,
            variables,
            outputs,
            iteration,
            trigger_context,
        )
        if task.run_if is not None:
            counters.conditions_covered += 1
            try:
                if not self._expressions.evaluate_condition(task.run_if, context):
                    return (
                        SimulatedTaskResult(
                            taskId=task_id,
                            taskType=task.type,
                            state=FlowTestTaskState.SKIPPED,
                            attempts=0,
                            lifecyclePhase=lifecycle_phase,
                            reason="runIf evaluated false",
                        ),
                        (),
                        None,
                    )
            except Exception as exc:
                if task.condition_error_policy is ConditionErrorPolicy.FALSE:
                    return (
                        SimulatedTaskResult(
                            taskId=task_id,
                            taskType=task.type,
                            state=FlowTestTaskState.SKIPPED,
                            attempts=0,
                            lifecyclePhase=lifecycle_phase,
                            reason=f"runIf error treated as false: {exc}",
                        ),
                        (),
                        None,
                    )
                return (_failed_result(task_id, task, lifecycle_phase, str(exc)), (), None)

        if task.type == "core.if":
            selected = self._select_if_branch(task, context, counters)
            return (
                _success_result(
                    task_id,
                    task,
                    lifecycle_phase,
                    {"selectedBranch": selected},
                    reason=f"selected branch {selected}",
                ),
                (),
                selected,
            )
        if task.type == "core.switch":
            selected = self._select_switch_branch(task, context, counters)
            return (
                _success_result(
                    task_id,
                    task,
                    lifecycle_phase,
                    {"selectedBranch": selected},
                    reason=f"selected branch {selected}",
                ),
                (),
                selected,
            )
        if task.type in {"core.sequential", "core.parallel", "core.dag", "core.workingDirectory"}:
            return (
                _success_result(task_id, task, lifecycle_phase, {}, reason="flowable expanded"),
                (),
                None,
            )
        if task.type in {"core.foreach", "core.while", "core.until"}:
            fixture = fixtures.get(task_id) or fixtures.get(task.id)
            iterations = self._iterations(task, fixture, context)
            generated: list[SimulatedTaskResult] = []
            child_outputs: list[dict[str, Any]] = []
            for index, value in enumerate(iterations):
                current_outputs: dict[str, Any] = {}
                for child in task.tasks:
                    counters.conditions_total += int(child.run_if is not None)
                    counters.conditions_total += _branch_condition_count(child)
                    if child.type in {"core.if", "core.switch"}:
                        counters.branches_total += len(child.child_task_groups())
                    generated_id = f"{task_id}[{index}].{child.id}"
                    child_result, nested, _ = self._execute_task(
                        flow,
                        child,
                        task_id=generated_id,
                        lifecycle_phase=lifecycle_phase,
                        inputs=inputs,
                        variables=variables,
                        outputs={**outputs, **current_outputs},
                        fixtures=fixtures,
                        iteration={"index": index, "value": value},
                        trigger_context=trigger_context,
                        counters=counters,
                    )
                    generated.append(child_result)
                    generated.extend(nested)
                    if child_result.output is not None:
                        current_outputs[child.id] = child_result.output
                child_outputs.append(current_outputs)
            failed = any(item.state is FlowTestTaskState.FAILED for item in generated)
            return (
                SimulatedTaskResult(
                    taskId=task_id,
                    taskType=task.type,
                    state=(FlowTestTaskState.FAILED if failed else FlowTestTaskState.SUCCESS),
                    attempts=1,
                    output={"iterationCount": len(iterations), "outputs": child_outputs},
                    lifecyclePhase=lifecycle_phase,
                    fixtureSource=(fixture.source if fixture is not None else None),
                    reason=f"generated {len(iterations)} iteration(s)",
                ),
                tuple(generated),
                None,
            )
        return self._execute_runnable(task, task_id, lifecycle_phase, context, fixtures), (), None

    def _execute_runnable(
        self,
        task: TaskDefinition,
        task_id: str,
        lifecycle_phase: str,
        context: ExpressionContext,
        fixtures: dict[str, FlowTestFixture],
    ) -> SimulatedTaskResult:
        if task.type == "core.return":
            value = task.configuration.handler_view().get("value")
            return _success_result(
                task_id,
                task,
                lifecycle_phase,
                {"value": self._expressions.render_value(value, context)},
                reason="deterministic core.return",
            )
        fixture = fixtures.get(task_id) or fixtures.get(task.id)
        if fixture is None:
            return _failed_result(
                task_id,
                task,
                lifecycle_phase,
                "external or plugin task requires a declared fixture",
            )
        attempts = min(fixture.failures_before_success + 1, task.retry.max_attempts)
        if fixture.error is not None or fixture.failures_before_success >= task.retry.max_attempts:
            reason = fixture.error or (
                f"fixture failed {fixture.failures_before_success} time(s), exceeding "
                f"maxAttempts={task.retry.max_attempts}"
            )
            return SimulatedTaskResult(
                taskId=task_id,
                taskType=task.type,
                state=FlowTestTaskState.FAILED,
                attempts=attempts,
                lifecyclePhase=lifecycle_phase,
                fixtureSource=fixture.source,
                reason=reason,
            )
        rendered = self._expressions.render_value(fixture.output, context)
        if not isinstance(rendered, dict):
            raise ValueError("fixture output must render to an object")
        return SimulatedTaskResult(
            taskId=task_id,
            taskType=task.type,
            state=FlowTestTaskState.SUCCESS,
            attempts=attempts,
            output=rendered,
            lifecyclePhase=lifecycle_phase,
            fixtureSource=fixture.source,
            reason=f"{fixture.source.value.lower()} fixture replayed without side effects",
        )

    def _select_if_branch(
        self,
        task: TaskDefinition,
        context: ExpressionContext,
        counters: _CoverageCounters,
    ) -> str:
        branches = [
            ("then", task.condition),
            *((f"else-if:{branch.id}", branch.condition) for branch in task.else_if),
        ]
        for branch_id, expression in branches:
            if expression is None:
                continue
            counters.conditions_covered += 1
            try:
                if self._expressions.evaluate_condition(expression, context):
                    return branch_id
            except Exception:
                if task.condition_error_policy is ConditionErrorPolicy.FALLBACK:
                    return "else"
                if task.condition_error_policy is not ConditionErrorPolicy.FALSE:
                    raise
        return "else"

    def _select_switch_branch(
        self,
        task: TaskDefinition,
        context: ExpressionContext,
        counters: _CoverageCounters,
    ) -> str:
        value = self._expressions.render_value(
            task.configuration.handler_view()["value"],
            context,
        )
        case = f"case:{value}"
        if str(value) in task.cases:
            return case
        for branch in task.predicate_cases:
            counters.conditions_covered += 1
            try:
                if self._expressions.evaluate_condition(branch.condition, context):
                    return f"predicate:{branch.id}"
            except Exception:
                if task.condition_error_policy is ConditionErrorPolicy.FALLBACK:
                    return "default"
                if task.condition_error_policy is not ConditionErrorPolicy.FALSE:
                    raise
        return "default"

    def _iterations(
        self,
        task: TaskDefinition,
        fixture: FlowTestFixture | None,
        context: ExpressionContext,
    ) -> tuple[Any, ...]:
        if fixture is not None and fixture.iterations is not None:
            return fixture.iterations
        extra = task.configuration.handler_view()
        if task.type == "core.foreach":
            source = extra.get("values", extra.get("items"))
            rendered = self._expressions.render_value(source, context)
            if not isinstance(rendered, list | tuple):
                raise ValueError("core.foreach simulation requires iterable values or a fixture")
            return tuple(rendered)
        raise ValueError(f"{task.type} simulation requires a fixture with iterations")

    @staticmethod
    def _branch_is_active(
        node: PlannedTask,
        plan_by_id: dict[str, PlannedTask],
        selected_paths: dict[str, str],
    ) -> bool:
        if node.branch_id is None:
            return True
        parent_id = node.parent_id
        while parent_id is not None:
            parent = plan_by_id[parent_id]
            selected = selected_paths.get(parent.task.id)
            if selected is not None and not (
                node.branch_id == selected or node.branch_id.startswith(f"{selected}/")
            ):
                return False
            parent_id = parent.parent_id
        return True


def aggregate_coverage(cases: tuple[FlowTestCaseResult, ...]) -> FlowTestCoverage:
    counters = _CoverageCounters(
        tasks_total=sum(case.coverage.tasks_total for case in cases),
        tasks_covered=sum(case.coverage.tasks_covered for case in cases),
        branches_total=sum(case.coverage.branches_total for case in cases),
        branches_covered=sum(case.coverage.branches_covered for case in cases),
        handlers_total=sum(case.coverage.handlers_total for case in cases),
        handlers_covered=sum(case.coverage.handlers_covered for case in cases),
        conditions_total=sum(case.coverage.conditions_total for case in cases),
        conditions_covered=sum(case.coverage.conditions_covered for case in cases),
    )
    return _coverage(counters)


def _expression_context(
    flow: FlowDefinition,
    inputs: dict[str, Any],
    variables: dict[str, Any],
    outputs: dict[str, Any],
    iteration: dict[str, Any],
    trigger_context: dict[str, Any] | None = None,
) -> ExpressionContext:
    return ExpressionContext(
        flow={"id": flow.id, "namespace": flow.namespace, "revision": flow.revision},
        inputs=inputs,
        variables=variables,
        outputs=outputs,
        iteration=iteration,
        trigger=trigger_context or {},
    )


def _branch_condition_count(task: TaskDefinition) -> int:
    if task.type == "core.if":
        return 1 + len(task.else_if)
    if task.type == "core.switch":
        return len(task.predicate_cases)
    return 0


def _coverage(counters: _CoverageCounters) -> FlowTestCoverage:
    total = (
        counters.tasks_total
        + counters.branches_total
        + counters.handlers_total
        + counters.conditions_total
    )
    covered = (
        counters.tasks_covered
        + counters.branches_covered
        + counters.handlers_covered
        + counters.conditions_covered
    )
    return FlowTestCoverage(
        tasksTotal=counters.tasks_total,
        tasksCovered=counters.tasks_covered,
        branchesTotal=counters.branches_total,
        branchesCovered=counters.branches_covered,
        handlersTotal=counters.handlers_total,
        handlersCovered=counters.handlers_covered,
        conditionsTotal=counters.conditions_total,
        conditionsCovered=counters.conditions_covered,
        percentage=round(100 * covered / total, 2) if total else 100,
    )


def _success_result(
    task_id: str,
    task: TaskDefinition,
    lifecycle_phase: str,
    output: dict[str, Any],
    *,
    reason: str,
) -> SimulatedTaskResult:
    return SimulatedTaskResult(
        taskId=task_id,
        taskType=task.type,
        state=FlowTestTaskState.SUCCESS,
        attempts=1,
        output=output,
        lifecyclePhase=lifecycle_phase,
        reason=reason,
    )


def _failed_result(
    task_id: str,
    task: TaskDefinition,
    lifecycle_phase: str,
    reason: str,
) -> SimulatedTaskResult:
    return SimulatedTaskResult(
        taskId=task_id,
        taskType=task.type,
        state=FlowTestTaskState.FAILED,
        attempts=1,
        lifecyclePhase=lifecycle_phase,
        reason=reason,
    )


def _skipped_result(node: PlannedTask, reason: str) -> SimulatedTaskResult:
    return SimulatedTaskResult(
        taskId=node.task.id,
        taskType=node.task.type,
        state=FlowTestTaskState.SKIPPED,
        attempts=0,
        branch=node.branch_id,
        lifecyclePhase=node.lifecycle_phase.value,
        reason=reason,
    )


def _assert_expectations(
    definition: FlowTestDefinition,
    *,
    state: FlowTestTaskState,
    outputs: dict[str, Any],
    task_results: list[SimulatedTaskResult],
) -> tuple[FlowTestAssertion, ...]:
    expected = definition.expected
    assertions = [
        FlowTestAssertion(
            path="state",
            passed=state is expected.state,
            expected=expected.state.value,
            actual=state.value,
        )
    ]
    if expected.outputs is not None:
        assertions.append(
            FlowTestAssertion(
                path="outputs",
                passed=outputs == expected.outputs,
                expected=expected.outputs,
                actual=outputs,
            )
        )
    by_id = {result.task_id: result for result in task_results}
    for task_id, expected_state in expected.task_states.items():
        actual = by_id.get(task_id)
        assertions.append(
            FlowTestAssertion(
                path=f"tasks.{task_id}.state",
                passed=actual is not None and actual.state is expected_state,
                expected=expected_state.value,
                actual=(actual.state.value if actual is not None else None),
            )
        )
    for task_id, expected_output in expected.task_outputs.items():
        actual = by_id.get(task_id)
        assertions.append(
            FlowTestAssertion(
                path=f"tasks.{task_id}.output",
                passed=actual is not None and actual.output == expected_output,
                expected=expected_output,
                actual=(actual.output if actual is not None else None),
            )
        )
    return tuple(assertions)


def _reject_sensitive_test_values(value: Any, *, path: str = "test") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key)).lower().replace("-", "_")
            if normalized in {"secret", "secrets", "password", "token", "credential"} or any(
                normalized.endswith(suffix)
                for suffix in ("_secret", "_password", "_token", "_credential")
            ):
                raise ValueError(f"{path}.{key} is secret-like and cannot enter flow test data")
            _reject_sensitive_test_values(nested, path=f"{path}.{key}")
    elif isinstance(value, list | tuple):
        for index, nested in enumerate(value):
            _reject_sensitive_test_values(nested, path=f"{path}[{index}]")


class FlowTestService:
    """Revision-pinned orchestration around the pure flow-test simulator."""

    def __init__(
        self,
        execution_repository: ExecutionRepository,
        flow_test_repository: FlowTestRepository,
        *,
        simulator: FlowTestSimulator | None = None,
    ) -> None:
        self._executions = execution_repository
        self._tests = flow_test_repository
        self._simulator = simulator or FlowTestSimulator()

    async def save_definition(
        self,
        namespace: str,
        flow_id: str,
        request: FlowTestDefinitionCreateRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> FlowTestDefinition:
        _reject_sensitive_test_values(
            {
                "inputs": request.inputs,
                "variables": request.variables,
                "fixtures": {
                    key: fixture.model_dump(mode="python")
                    for key, fixture in request.fixtures.items()
                },
            }
        )
        _flow, semantic_hash, plugin_hash = await self._revision_identity(
            namespace,
            flow_id,
            request.revision,
            tenant_id=tenant_id,
        )
        return await self._tests.save_definition(
            namespace,
            flow_id,
            request,
            tenant_id=tenant_id,
            flow_semantic_hash=semantic_hash,
            plugin_set_hash=plugin_hash,
            actor_id=actor_id,
        )

    async def run(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        request: FlowTestRunRequest,
        *,
        tenant_id: str,
        actor_id: str,
    ) -> FlowTestRunResult:
        flow, semantic_hash, plugin_hash = await self._revision_identity(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
        )
        definitions = await self._tests.list_definitions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
        by_id = {definition.test_id: definition for definition in definitions}
        if request.test_ids:
            missing = sorted(set(request.test_ids) - by_id.keys())
            if missing:
                raise LookupError(f"flow tests do not exist: {', '.join(missing)}")
            selected = tuple(by_id[test_id] for test_id in request.test_ids)
        else:
            selected = definitions
        if not selected:
            raise LookupError("no flow tests are defined for this revision")

        cases: list[FlowTestCaseResult] = []
        for definition in selected:
            try:
                if (
                    definition.flow_semantic_hash != semantic_hash
                    or definition.plugin_set_hash != plugin_hash
                ):
                    raise ValueError(
                        "flow test is stale for the pinned flow revision or plugin set"
                    )
                case = self._simulator.simulate(flow, definition)
            except (LookupError, TypeError, ValueError) as error:
                case = _error_case(definition.test_id, str(error))
            cases.append(case)
            if request.fail_fast and case.outcome is not FlowTestOutcome.PASSED:
                break

        frozen_cases = tuple(cases)
        outcome = (
            FlowTestOutcome.ERROR
            if any(case.outcome is FlowTestOutcome.ERROR for case in frozen_cases)
            else FlowTestOutcome.FAILED
            if any(case.outcome is FlowTestOutcome.FAILED for case in frozen_cases)
            else FlowTestOutcome.PASSED
        )
        result = FlowTestRunResult(
            tenantId=tenant_id,
            namespace=namespace,
            flowId=flow_id,
            revision=revision,
            flowSemanticHash=semantic_hash,
            pluginSetHash=plugin_hash,
            outcome=outcome,
            cases=frozen_cases,
            coverage=aggregate_coverage(frozen_cases),
            requestedBy=actor_id,
        )
        return await self._tests.record_run(result)

    async def gate_decision(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
    ) -> FlowTestGateDecision:
        gate = await self._tests.get_gate(namespace, tenant_id=tenant_id)
        if gate is None or not gate.enabled:
            return FlowTestGateDecision(
                allowed=True,
                reason="flow-test quality gate is not enabled",
                gate=gate,
            )
        _flow, semantic_hash, plugin_hash = await self._revision_identity(
            namespace,
            flow_id,
            revision,
            tenant_id=tenant_id,
        )
        runs = await self._tests.list_runs(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
            limit=100,
        )
        result = next(
            (
                run
                for run in runs
                if run.outcome is FlowTestOutcome.PASSED
                and run.flow_semantic_hash == semantic_hash
                and run.plugin_set_hash == plugin_hash
                and run.simulator_version == FLOW_TEST_SIMULATOR_VERSION
            ),
            None,
        )
        if result is None:
            return FlowTestGateDecision(
                allowed=False,
                reason="no passing test result matches this revision and plugin set",
                gate=gate,
            )
        passed_ids = {
            case.test_id for case in result.cases if case.outcome is FlowTestOutcome.PASSED
        }
        missing = sorted(set(gate.required_test_ids) - passed_ids)
        if missing:
            return FlowTestGateDecision(
                allowed=False,
                reason=f"required tests did not pass: {', '.join(missing)}",
                gate=gate,
                result=result,
            )
        if result.coverage.percentage < gate.minimum_coverage:
            return FlowTestGateDecision(
                allowed=False,
                reason=(
                    f"coverage {result.coverage.percentage:.2f}% is below "
                    f"{gate.minimum_coverage:.2f}%"
                ),
                gate=gate,
                result=result,
            )
        return FlowTestGateDecision(
            allowed=True,
            reason="revision-pinned flow tests satisfy the namespace quality gate",
            gate=gate,
            result=result,
        )

    async def _revision_identity(
        self,
        namespace: str,
        flow_id: str,
        revision: int,
        *,
        tenant_id: str,
    ) -> tuple[FlowDefinition, str, str]:
        flow = await self._executions.get_flow(
            namespace,
            flow_id,
            tenant_id=tenant_id,
            revision=revision,
        )
        revisions = await self._executions.list_flow_revisions(
            namespace,
            flow_id,
            tenant_id=tenant_id,
        )
        record = next((item for item in revisions if item.revision == revision), None)
        if record is None:
            raise LookupError(f"flow revision {revision} does not exist")
        plugin_hash = hashlib.sha256(
            json.dumps(
                record.plugin_resolution,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode()
        ).hexdigest()
        return flow, record.semantic_hash, plugin_hash


def _error_case(test_id: str, message: str) -> FlowTestCaseResult:
    return FlowTestCaseResult(
        testId=test_id,
        outcome=FlowTestOutcome.ERROR,
        state=FlowTestTaskState.FAILED,
        outputs={},
        tasks=(),
        assertions=(
            FlowTestAssertion(
                path="simulation",
                passed=False,
                expected="deterministic simulation",
                actual=message,
            ),
        ),
        coverage=_coverage(_CoverageCounters(tasks_total=0)),
        error=message,
    )
