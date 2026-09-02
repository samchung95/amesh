from __future__ import annotations

import importlib


def test_mcp_client_boundary_reexports_preserve_task_api() -> None:
    client = importlib.import_module("amesh.tasks.mcp_client")
    task_module = importlib.import_module("amesh.tasks.mcp")
    package = importlib.import_module("amesh.tasks")
    provider = importlib.import_module("amesh.tasks.tool_provider")

    assert task_module.McpTargetResolver is client.McpTargetResolver
    assert task_module.McpToolApplicationError is client.McpToolApplicationError
    assert task_module.discover_mcp_server is client.discover_mcp_server
    assert task_module._call_tool is client._call_tool
    assert package.McpTargetResolver is client.McpTargetResolver
    assert package.McpToolApplicationError is client.McpToolApplicationError
    assert package.discover_mcp_server is client.discover_mcp_server
    assert provider.McpTargetResolver is client.McpTargetResolver
    assert provider.discover_mcp_server is client.discover_mcp_server
    assert provider._call_tool is client._call_tool
