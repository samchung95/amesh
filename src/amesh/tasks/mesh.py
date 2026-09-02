from __future__ import annotations

from decimal import Decimal

from amesh.domain import (
    AgentDefinitionSpec,
    AgentHandoffRequest,
    AgentResourceKind,
    AgentRouteRequest,
    build_agent_handoff,
    route_agent,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskHandler, TaskMetricRecord
from amesh.ports import AgentResourceRepository


def agent_mesh_handlers(resources: AgentResourceRepository) -> dict[str, TaskHandler]:
    async def run_route(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        del context
        request = AgentRouteRequest.model_validate(task.configuration.handler_view())
        decision = route_agent(request)
        return TaskCompletion(
            output={"agentRoute": decision.model_dump(mode="json", by_alias=True)},
            metrics=(
                TaskMetricRecord(
                    name="agent.mesh.route_candidates",
                    value=Decimal(len(request.candidates)),
                    unit="candidates",
                ),
            ),
        )

    async def run_handoff(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        request = AgentHandoffRequest.model_validate(task.configuration.handler_view())
        if request.source.task not in task.depends_on:
            raise PermissionError("agent hand-off source must be a direct task dependency")
        source_output = context.outputs.get(request.source.task)
        source_session = source_output.get("session") if source_output is not None else None
        if not isinstance(source_session, dict):
            raise ValueError("agent hand-off source session evidence is unavailable")
        destination = await resources.get_resource(
            context.tenant_id,
            context.namespace,
            AgentResourceKind.AGENT,
            request.destination.agent,
            revision=request.destination.agent_revision,
        )
        if not isinstance(destination.spec, AgentDefinitionSpec):
            raise TypeError("agent hand-off destination is not an agent definition")
        record = build_agent_handoff(
            request,
            source_session=source_session,
            destination_capabilities=destination.spec.permissions.delegated_capabilities,
            secrets=tuple(context.secrets.values()),
        )
        serialized = record.model_dump(mode="json", by_alias=True)
        return TaskCompletion(
            output={"agentHandoff": serialized, "payload": serialized["context"]},
            metrics=(
                TaskMetricRecord(
                    name="agent.mesh.handoffs",
                    value=Decimal(1),
                    unit="handoffs",
                ),
            ),
        )

    return {"agent.route": run_route, "agent.handoff": run_handoff}


__all__ = ["agent_mesh_handlers"]
