from amesh.domain.scripts import SCRIPT_TASK_TYPES, ScriptTaskPolicy
from amesh.executor import TaskHandler
from amesh.workflow.working_directory import WorkingDirectoryManager

from .control import core_control_handlers
from .data import core_data_handlers
from .documents import core_document_extract_handler
from .files import core_file_handlers
from .http import HttpTaskPolicy, core_download_handler, core_http_handler
from .llm import OpenAICompatibleConfig, agent_llm_handler
from .mcp import agent_mcp_handler, discover_mcp_server
from .mesh import agent_mesh_handlers
from .notifications import EmailSender, SmtpDelivery, core_notification_handlers
from .scripts import script_task_handlers
from .session import InvalidAgentOutputPolicy, agent_session_handler
from .tool_provider import (
    AgentPrimitiveInvocationJournal,
    ExampleToolProvider,
    GovernedToolInvoker,
    InMemoryToolInvocationJournal,
    McpToolProvider,
)


def core_utility_handlers(
    workspace_manager: "WorkingDirectoryManager",
    *,
    http_policy: HttpTaskPolicy | None = None,
) -> dict[str, "TaskHandler"]:
    handlers = {
        "core.http": core_http_handler(policy=http_policy),
        "core.download": core_download_handler(workspace_manager, policy=http_policy),
        **core_control_handlers(),
        **core_data_handlers(),
        "core.document.extract": core_document_extract_handler(workspace_manager),
        **core_file_handlers(workspace_manager),
        **core_notification_handlers(http_policy=http_policy),
    }
    return handlers


__all__ = [
    "SCRIPT_TASK_TYPES",
    "AgentPrimitiveInvocationJournal",
    "EmailSender",
    "ExampleToolProvider",
    "GovernedToolInvoker",
    "HttpTaskPolicy",
    "InMemoryToolInvocationJournal",
    "InvalidAgentOutputPolicy",
    "McpToolProvider",
    "OpenAICompatibleConfig",
    "ScriptTaskPolicy",
    "SmtpDelivery",
    "agent_llm_handler",
    "agent_mcp_handler",
    "agent_mesh_handlers",
    "agent_session_handler",
    "core_control_handlers",
    "core_data_handlers",
    "core_document_extract_handler",
    "core_download_handler",
    "core_file_handlers",
    "core_http_handler",
    "core_notification_handlers",
    "core_utility_handlers",
    "discover_mcp_server",
    "script_task_handlers",
]
