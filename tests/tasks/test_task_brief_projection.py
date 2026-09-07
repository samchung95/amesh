from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from uuid import uuid4

import pytest
from tests.tasks.test_agent_sessions import (
    MemoryResources,
    MemorySessions,
    ScriptedMcp,
    ScriptedModel,
    _context,
    _pin,
    _task,
)
from tests.tasks.test_agent_sessions import pi_harness as pi_harness

from amesh.domain.task_briefs import AgentTaskBrief, bind_task_brief
from amesh.tasks import agent_session_handler
from amesh.tasks.task_briefs import selected_task_brief


def test_between_turn_refresh_preserves_prior_checkpoint_and_uses_exact_new_revision(pi_harness):
    async def scenario():
        session_id, actor_id = uuid4(), uuid4()
        first = bind_task_brief(
            AgentTaskBrief(
                schemaId="consumer/task",
                schemaVersion="1",
                content={"goal": "OLD APPROVED DECISION"},
            ),
            tenant_id="default",
            namespace="agents.demo",
            session_id=session_id,
            producer_id=actor_id,
            turn=1,
        )
        second = bind_task_brief(
            AgentTaskBrief(
                schemaId="consumer/task",
                schemaVersion="2",
                content={"goal": "NEW APPROVED DECISION"},
            ),
            tenant_id="default",
            namespace="agents.demo",
            session_id=session_id,
            producer_id=actor_id,
            turn=2,
        )
        context = replace(
            _context(),
            trigger={
                "ameshAgentSessionId": str(session_id),
                "ameshActorId": str(actor_id),
                "ameshTaskBrief": first.model_dump(mode="json", by_alias=True),
            },
        )
        sessions = MemorySessions()
        model = ScriptedModel(
            [
                {
                    "action": "final",
                    "tool": "lookup",
                    "arguments": None,
                    "output": {"answer": "done"},
                    "rationale": "done",
                }
            ]
            * 2
        )
        pin = _pin()
        handler = agent_session_handler(
            resources=MemoryResources(pin),
            sessions=sessions,
            model_handler=model,
            mcp_handler=ScriptedMcp(),
            harness=pi_harness,
        )
        await handler(_task(), context)
        prior = (await sessions.get_session("default", context.task_run_id, 1)).session
        prior_serialized = prior.model_dump_json()
        next_context = replace(
            context,
            execution_id=uuid4(),
            task_run_id=uuid4(),
            attempt_id=uuid4(),
            trigger={
                **context.trigger,
                "ameshAgentSessionTurn": 2,
                "ameshAgentSessionAttemptBase": 1,
                "ameshTaskBrief": second.model_dump(mode="json", by_alias=True),
                "ameshAgentSessionResumeFrom": {
                    "sessionId": str(prior.session_id),
                    "taskRunId": str(prior.task_run_id),
                    "attempt": 1,
                    "capabilityPinId": str(prior.capability_pin_id),
                    "envelopeDigest": prior.envelope_digest,
                },
            },
        )
        await handler(_task(question="continue approved task"), next_context)
        current = (await sessions.get_session("default", next_context.task_run_id, 2)).session
        assert current.checkpoint.task_brief == second
        assert prior.model_dump_json() == prior_serialized
        assert (
            current.checkpoint.messages[: len(prior.checkpoint.messages)]
            == prior.checkpoint.messages
        )
        assert current.capability_pin_id == prior.capability_pin_id
        assert current.harness == prior.harness
        model_input = json.dumps(model.calls[-1].model_extra["messages"])
        assert "NEW APPROVED DECISION" in model_input and "OLD APPROVED DECISION" not in model_input
        # Recovery of a completed turn reuses the accepted checkpoint without another model call.
        await handler(_task(question="continue approved task"), next_context)
        assert len(model.calls) == 2

    asyncio.run(scenario())


def test_runtime_brief_scope_rejects_transfer_to_another_session_or_actor():
    context = _context()
    brief = bind_task_brief(
        AgentTaskBrief(schemaId="consumer/task", schemaVersion="1", content={}),
        tenant_id=context.tenant_id,
        namespace=context.namespace,
        session_id=uuid4(),
        producer_id=uuid4(),
        turn=1,
    )
    trigger = {
        "ameshAgentSessionId": str(brief.session_id),
        "ameshActorId": str(brief.producer_id),
        "ameshTaskBrief": brief.model_dump(mode="json", by_alias=True),
    }
    assert selected_task_brief(replace(context, trigger=trigger)) == brief
    for field in ("ameshAgentSessionId", "ameshActorId"):
        with pytest.raises(PermissionError, match="execution scope"):
            selected_task_brief(replace(context, trigger={**trigger, field: str(uuid4())}))
    assert selected_task_brief(context) is None
