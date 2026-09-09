"""Provider-free completion-gate journeys through the actual Pi session harness."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import uuid4

import pytest
from tests.domain.test_agent_tool_plan import ACCEPTED_SCHEMA
from tests.tasks.test_agent_sessions import (
    MemoryResources,
    MemorySessions,
    RecordingHarness,
    ScriptedModel,
    SimulatedWorkerCrash,
    _context,
    _pin,
    _task,
)
from tests.tasks.test_agent_sessions import (
    pi_harness as pi_harness,
)

from amesh.domain.agent_tool_plan import ToolPlanLedger
from amesh.executor import TaskCompletion, TaskExecutionFailure
from amesh.tasks import agent_session_handler

PLAN = {
    "mode": "UNORDERED",
    "steps": [
        {
            "stepId": "submit",
            "toolName": "submit",
            "successSchema": ACCEPTED_SCHEMA,
            "argumentBindings": {"owner": "/question"},
        },
        {"stepId": "check", "toolName": "check", "successSchema": ACCEPTED_SCHEMA},
    ],
}


def _requirements_pin():
    pin = _pin(max_turns=12, max_loops=12)
    schema = {
        "type": "object",
        "properties": {name: {"type": "string"} for name in ("key", "report", "owner")},
        "required": ["key"],
        "additionalProperties": False,
    }
    tools = tuple(
        pin.envelope.tools[0].model_copy(
            update={
                "tool_name": name,
                "input_schema": schema,
                "argument_bindings": {"owner": "/question"} if name == "submit" else {},
            }
        )
        for name in ("submit", "check", "extra")
    )
    envelope = pin.envelope.model_copy(
        update={
            "tools": tools,
            "permissions": pin.envelope.permissions.model_copy(
                update={
                    "tool_allowlist": tuple(tool.tool_name for tool in tools),
                }
            ),
            "hard_limits": pin.envelope.hard_limits.model_copy(update={"max_tool_calls": 8}),
        }
    )
    return pin.model_copy(update={"envelope": envelope})


class CompletionModel(ScriptedModel):
    def __init__(self, protocol: str, actions: list[tuple[str, dict[str, Any]]]) -> None:
        super().__init__([])
        self.protocol = protocol
        self.steps = actions

    async def __call__(self, task, context):
        name, arguments = self.steps.pop(0)
        action = {
            "action": "final" if name == "final" else "tool",
            "tool": name,
            "arguments": arguments,
            "output": {"answer": "accepted"},
            "rationale": "test",
        }
        self.actions.append(action)
        completion = await super().__call__(task, context)
        if self.protocol != "STRUCTURED_V1":
            if name == "final":
                completion.output["structuredOutput"] = {"answer": "accepted"}
            else:
                native_name = (
                    "amesh_finish_research"
                    if name == "finish"
                    else (f"amesh_tool_{('submit', 'check', 'extra').index(name)}")
                )
                completion.output["toolCalls"] = [
                    {
                        "id": f"call-{len(self.calls)}",
                        "name": native_name,
                        "arguments": arguments,
                    }
                ]
        return completion


class ResultMcp:
    def __init__(self, *, reject: dict[str, Any] | None = None) -> None:
        self.calls: list[Any] = []
        self.results: dict[str, TaskCompletion] = {}
        self.reject = reject or {"structuredContent": {"accepted": False, "errors": ["fix report"]}}

    async def __call__(self, task, context):
        self.calls.append(task)
        document = task.model_extra
        key = document["invocationKey"]
        if key not in self.results:
            result = {"structuredContent": {"accepted": True, "receipt": str(uuid4())}}
            if document["tool"] == "submit" and document["arguments"].get("report") != "corrected":
                result = self.reject
            self.results[key] = TaskCompletion(output=result)
        return self.results[key]


@pytest.mark.parametrize("protocol", ["STRUCTURED_V1", "NATIVE_V2", "NATIVE_V3"])
@pytest.mark.parametrize("crash", [False, True])
def test_unordered_real_harness_corrects_results_preserves_optional_arguments_and_recovers(
    pi_harness,
    protocol: str,
    crash: bool,
) -> None:
    class CrashSessions(MemorySessions):
        crashed = False

        async def transition(self, session_id, *, tenant_id, transition):
            if (
                crash
                and not self.crashed
                and transition.event_type == "tool.result"
                and transition.payload["tool"] == "check"
            ):
                self.crashed = True
                raise SimulatedWorkerCrash
            return await super().transition(session_id, tenant_id=tenant_id, transition=transition)

    async def scenario() -> None:
        early = "final" if protocol == "STRUCTURED_V1" else "finish"
        steps = [
            ("extra", {"key": "unrelated"}),
            ("check", {"key": "second requirement first"}),
            ("submit", {"key": "first", "report": "invalid", "owner": "forged"}),
            (early, {}),
            ("submit", {"key": "first", "report": "corrected"}),
        ]
        if protocol != "STRUCTURED_V1":
            steps.append(("finish", {}))
        steps.append(("final", {}))
        model = CompletionModel(protocol, steps)
        sessions, mcp, context = CrashSessions(), ResultMcp(), _context()
        handler = agent_session_handler(
            resources=MemoryResources(_requirements_pin()),
            sessions=sessions,
            model_handler=model,
            mcp_handler=mcp,
            harness=pi_harness,
        )
        task = _task(required_tool_plan=PLAN, repair=True, interaction_protocol=protocol)
        if crash:
            with pytest.raises(SimulatedWorkerCrash):
                await handler(task, context)
            detail = await sessions.get_session("default", context.task_run_id, 1)
            assert detail.session.checkpoint.pending_action is not None
            assert not detail.session.checkpoint.tool_plan.is_complete
        completed = await handler(task, context)
        evidence = completed.output["session"]["requiredToolPlan"]
        assert evidence["complete"] is True and evidence["completedCount"] == 2
        assert evidence["mode"] == "UNORDERED"
        assert len(mcp.results) == 4  # Retry reuses the persisted MCP invocation result.
        assert len(model.calls) == (6 if protocol == "STRUCTURED_V1" else 7)
        detail = await sessions.get_session("default", context.task_run_id, 1)
        assert evidence["sessionId"] == str(detail.session.session_id)
        assert [entry["attemptCount"] for entry in evidence["occurrences"]] == [2, 1]
        for entry in evidence["occurrences"]:
            assert entry["invocationKey"].startswith(f"session:{evidence['sessionId']}:turn:")
            assert entry["resultDigest"].startswith("sha256:")
        results = [event for event in detail.events if event.event_type == "tool.result"]
        assert [event.payload["tool"] for event in results] == [
            "extra",
            "check",
            "submit",
            "submit",
        ]
        assert results[2].payload["completionRequirement"]["satisfied"] is False
        assert results[3].payload["completionRequirement"]["satisfied"] is True
        assert results[0].payload["requiredToolPlan"]["completedCount"] == 0
        assert "fix report" in json.dumps(model.calls[3].model_extra)
        submits = [
            call.model_extra["arguments"]
            for call in mcp.calls
            if call.model_extra["tool"] == "submit"
        ]
        assert all(arguments["owner"] == "Find it" for arguments in submits)
        assert submits[-1]["report"] == "corrected"
        assert (await handler(task, context)).output == completed.output
        assert len(mcp.results) == 4
        assert (
            ToolPlanLedger.model_validate_json(
                detail.session.checkpoint.tool_plan.model_dump_json()
            )
            == detail.session.checkpoint.tool_plan
        )

    asyncio.run(scenario())


@pytest.mark.parametrize("protocol", ["STRUCTURED_V1", "NATIVE_V2", "NATIVE_V3"])
def test_requirement_prompts_redact_bound_secrets_on_initial_and_followup_turns(protocol) -> None:
    from amesh.domain.agent_sessions import AgentSessionRecord, AgentSessionStart
    from amesh.tasks.session import (
        _follow_up_checkpoint,
        _initial_messages,
        _parse_spec,
        _validate_boundary,
    )

    task = _task(required_tool_plan=PLAN, question="router-secret", interaction_protocol=protocol)
    context, pin = _context(), _requirements_pin()
    spec = _parse_spec(task)
    ledger = _validate_boundary(task, context, spec, pin, RecordingHarness())
    secrets = tuple(context.secrets.values())
    messages = _initial_messages(spec, pin, secrets, (), ledger)
    record = AgentSessionRecord(
        **AgentSessionStart(
            tenantId="default",
            namespace="agents.demo",
            executionId=context.execution_id,
            taskRunId=context.task_run_id,
            attempt=1,
            capabilityPinId=pin.pin_id,
            envelopeDigest=pin.envelope_digest,
        ).model_dump()
    )
    record = record.model_copy(
        update={"checkpoint": record.checkpoint.model_copy(update={"messages": messages})}
    )
    followup = _follow_up_checkpoint(record, spec, secrets, ledger)
    assert "router-secret" not in json.dumps(messages)
    assert "router-secret" not in json.dumps(followup.messages)
    assert "[REDACTED]" in json.dumps(followup.messages)


def test_long_tool_name_uses_bounded_stable_invocation_key_and_reloads() -> None:
    from tests.tasks.test_agent_sessions import ScriptedMcp

    async def scenario() -> None:
        name = "x" * 255
        pin = _pin()
        tool = pin.envelope.tools[0].model_copy(update={"tool_name": name})
        pin = pin.model_copy(
            update={
                "envelope": pin.envelope.model_copy(
                    update={
                        "tools": (tool,),
                        "permissions": pin.envelope.permissions.model_copy(
                            update={"tool_allowlist": (name,)}
                        ),
                    }
                )
            }
        )
        plan = {
            "mode": "UNORDERED",
            "steps": [
                {
                    "stepId": "long",
                    "toolName": name,
                    "successSchema": {
                        "type": "object",
                        "required": ["value"],
                        "properties": {"value": {"const": "found"}},
                    },
                }
            ],
        }
        model = ScriptedModel(
            [
                {
                    "action": "tool",
                    "tool": name,
                    "arguments": {"key": "one"},
                    "output": None,
                    "rationale": "test",
                },
                {
                    "action": "final",
                    "tool": name,
                    "arguments": None,
                    "output": {"answer": "done"},
                    "rationale": "test",
                },
            ]
        )
        sessions, mcp, context = MemorySessions(), ScriptedMcp(), _context()
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=model,
            mcp_handler=mcp,
            harness=RecordingHarness(),
        )
        task = _task(required_tool_plan=plan)
        completed = await handler(task, context)
        key = mcp.calls[0].model_extra["invocationKey"]
        assert len(key) <= 255 and ":tool:sha256:" in key
        ledger = (
            await sessions.get_session("default", context.task_run_id, 1)
        ).session.checkpoint.tool_plan
        assert ToolPlanLedger.model_validate_json(ledger.model_dump_json()).is_complete
        assert (await handler(task, context)).output == completed.output
        assert mcp.effects == 1 and len(model.calls) == 2

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "result",
    [
        {"structuredContent": {}},
        {"isError": True, "structuredContent": {"accepted": True}},
        {"content": [{"type": "text", "text": '{"accepted":true}'}]},
    ],
)
def test_actual_missing_error_and_text_only_results_cannot_satisfy_gate(result) -> None:
    async def scenario() -> None:
        sessions, mcp = MemorySessions(), ResultMcp(reject=result)
        handler = agent_session_handler(
            resources=MemoryResources(_requirements_pin()),
            sessions=sessions,
            model_handler=CompletionModel(
                "STRUCTURED_V1",
                [
                    ("check", {"key": "check"}),
                    ("submit", {"key": "bad"}),
                    ("final", {}),
                ],
            ),
            mcp_handler=mcp,
            harness=RecordingHarness(),
        )
        with pytest.raises(
            TaskExecutionFailure, match="required tool plan is incomplete"
        ) as failure:
            await handler(_task(required_tool_plan=PLAN), _context())
        assert failure.value.evidence["agentSession"]["requiredToolPlan"]["completedCount"] == 1

    asyncio.run(scenario())


def test_new_session_cannot_use_prior_workflow_receipts_or_copied_checkpoint() -> None:
    async def scenario() -> None:
        sessions = MemorySessions()
        model = CompletionModel(
            "STRUCTURED_V1",
            [
                ("check", {"key": "ok"}),
                ("submit", {"key": "ok", "report": "corrected"}),
                ("final", {}),
                ("final", {}),
            ],
        )
        mcp = ResultMcp()
        handler = agent_session_handler(
            resources=MemoryResources(_requirements_pin()),
            sessions=sessions,
            model_handler=model,
            mcp_handler=mcp,
            harness=RecordingHarness(),
        )
        task, first_context = _task(required_tool_plan=PLAN), _context()
        completed = await handler(task, first_context)
        second_context = _context(outputs={"earlier_mcp_task": completed.output})
        with pytest.raises(TaskExecutionFailure, match="incomplete"):
            await handler(task, second_context)
        first = (await sessions.get_session("default", first_context.task_run_id, 1)).session
        second = (await sessions.get_session("default", second_context.task_run_id, 1)).session
        assert first.checkpoint.tool_plan.is_complete
        assert not second.checkpoint.tool_plan.is_complete
        # A persisted ledger copied from another executing session fails before any model/tool I/O.
        sessions.records[("default", second_context.task_run_id, 1)] = second.model_copy(
            update={
                "checkpoint": second.checkpoint.model_copy(
                    update={"tool_plan": first.checkpoint.tool_plan}
                ),
            }
        )
        with pytest.raises(ValueError, match="changed while the session was recoverable"):
            await handler(task, second_context)
        assert len(model.calls) == 4 and len(mcp.results) == 2

    asyncio.run(scenario())
