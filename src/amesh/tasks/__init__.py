from amesh.executor import TaskHandler
from amesh.workflow.working_directory import WorkingDirectoryManager

from .control import core_control_handlers
from .data import core_data_handlers
from .files import core_file_handlers
from .http import HttpTaskPolicy, core_download_handler, core_http_handler
from .llm import OpenAICompatibleConfig, agent_llm_handler
from .mcp import agent_mcp_handler
from .notifications import EmailSender, SmtpDelivery, core_notification_handlers


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
        **core_file_handlers(workspace_manager),
        **core_notification_handlers(http_policy=http_policy),
    }
    return handlers


__all__ = [
    "EmailSender",
    "HttpTaskPolicy",
    "OpenAICompatibleConfig",
    "SmtpDelivery",
    "agent_llm_handler",
    "agent_mcp_handler",
    "core_control_handlers",
    "core_data_handlers",
    "core_download_handler",
    "core_file_handlers",
    "core_http_handler",
    "core_notification_handlers",
    "core_utility_handlers",
]
