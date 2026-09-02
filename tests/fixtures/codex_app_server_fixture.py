"""Provider-free Codex App Server JSONL fixture used by adapter tests."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path


async def main() -> None:
    turn_tasks: dict[str, asyncio.Task[None]] = {}
    thread_id = "thread-fixture"
    turn_id = "turn-fixture"
    account_state = Path(os.environ["CODEX_HOME"]) / "account-state"
    login_delay = 0.0
    if "--login-delay" in sys.argv:
        login_delay = float(sys.argv[sys.argv.index("--login-delay") + 1])
    login_success = "--login-failure" not in sys.argv
    disabled_features = {
        sys.argv[index + 1]
        for index, argument in enumerate(sys.argv[:-1])
        if argument == "--disable"
    }
    required_disabled_features = {
        "apps",
        "browser_use",
        "browser_use_external",
        "browser_use_full_cdp_access",
        "code_mode",
        "code_mode_host",
        "collaboration_modes",
        "computer_use",
        "deferred_executor",
        "enable_mcp_apps",
        "hooks",
        "image_generation",
        "in_app_browser",
        "mcp_2026_07_28",
        "multi_agent",
        "multi_agent_v2",
        "plugins",
        "shell_snapshot",
        "shell_snapshot_v2",
        "shell_tool",
        "skill_search",
        "tool_call_mcp_elicitation",
        "unified_exec",
        "view_image",
        "web_search_cached",
        "web_search_request",
    }

    async def emit(message: dict[str, object]) -> None:
        sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
        sys.stdout.flush()

    async def run_turn(request_id: int, params: dict[str, object]) -> None:
        await emit({"id": request_id, "result": {"turn": {"id": turn_id, "status": "inProgress"}}})
        input_items = params.get("input", [])
        prompt = (
            str(input_items[0].get("text", ""))
            if isinstance(input_items, list) and input_items
            else ""
        )
        local_images = (
            [
                item.get("path")
                for item in input_items
                if isinstance(item, dict) and item.get("type") == "localImage"
            ]
            if isinstance(input_items, list)
            else []
        )
        Path(os.environ["CODEX_HOME"], "observed-images.json").write_text(
            json.dumps(
                [
                    {"path": path, "exists": isinstance(path, str) and Path(path).is_file()}
                    for path in local_images
                ]
            ),
            encoding="utf-8",
        )
        if prompt == "wait":
            return
        if prompt == "fail":
            await emit(
                {
                    "method": "turn/completed",
                    "params": {
                        "threadId": thread_id,
                        "turn": {
                            "id": turn_id,
                            "status": "failed",
                            "error": {"message": "fixture failure"},
                            "items": [],
                        },
                    },
                }
            )
            return
        output_schema = params.get("outputSchema")
        schema_properties = (
            output_schema.get("properties") if isinstance(output_schema, dict) else None
        )
        is_agent_action = isinstance(schema_properties, dict) and "action" in schema_properties
        if is_agent_action:
            tool_schema = schema_properties.get("tool")
            tool_values = tool_schema.get("enum") if isinstance(tool_schema, dict) else None
            tool = tool_values[0] if isinstance(tool_values, list) and tool_values else "none"
            response_content = json.dumps(
                {
                    "action": "final",
                    "tool": tool,
                    "arguments": None,
                    "output": {"answer": "ok"},
                    "rationale": "fixture result",
                },
                separators=(",", ":"),
            )
        else:
            response_content = '{"answer":"ok"}'
        await emit(
            {"method": "item/reasoning/summaryTextDelta", "params": {"delta": "secret reasoning"}}
        )
        if prompt == "slow":
            await asyncio.sleep(0.15)
        if prompt == "delta-only":
            for delta in (response_content[:8], response_content[8:]):
                await emit({"method": "item/agentMessage/delta", "params": {"delta": delta}})
        else:
            await emit({"method": "item/agentMessage/delta", "params": {"delta": response_content}})
        if prompt == "slow":
            await asyncio.sleep(0.15)
        if prompt != "no-usage":
            await emit(
                {
                    "method": "thread/tokenUsage/updated",
                    "params": {
                        "tokenUsage": {"inputTokens": 3, "outputTokens": 2, "totalTokens": 5}
                    },
                }
            )
        if prompt == "slow":
            await asyncio.sleep(0.15)
        final_items = (
            [] if prompt == "delta-only" else [{"type": "agentMessage", "text": response_content}]
        )
        await emit(
            {
                "method": "turn/completed",
                "params": {
                    "threadId": thread_id,
                    "turn": {
                        "id": turn_id,
                        "status": "completed",
                        "items": final_items,
                    },
                },
            }
        )

    while True:
        line = await asyncio.to_thread(sys.stdin.readline)
        if not line:
            break
        message = json.loads(line)
        method = message.get("method")
        request_id = message.get("id")
        params = message.get("params") or {}
        if method == "initialize":
            Path(os.environ["CODEX_HOME"], "observed-cwd").write_text(os.getcwd(), encoding="utf-8")
            Path(os.environ["CODEX_HOME"], "observed-home").write_text(
                os.environ["HOME"], encoding="utf-8"
            )
            await emit(
                {
                    "id": request_id,
                    "result": {
                        "codexHome": os.environ["CODEX_HOME"],
                        "platformFamily": "windows",
                        "platformOs": "windows",
                        "userAgent": "fixture",
                    },
                }
            )
        elif method == "initialized":
            continue
        elif method == "account/read":
            account = {"type": "chatgpt", "planType": "plus"} if account_state.exists() else None
            await emit(
                {"id": request_id, "result": {"account": account, "requiresOpenaiAuth": True}}
            )
        elif method == "account/rateLimits/read":
            await emit(
                {"id": request_id, "result": {"rateLimits": {"limitId": "codex", "remaining": 9}}}
            )
        elif method == "account/usage/read":
            await emit(
                {"id": request_id, "result": {"summary": {"inputTokens": 3, "outputTokens": 2}}}
            )
        elif method == "account/login/start":
            login_type = params.get("type")
            if login_type == "chatgptDeviceCode":
                result = {
                    "type": login_type,
                    "loginId": "login-fixture",
                    "verificationUrl": "https://auth.openai.com/codex/device",
                    "userCode": "ABCD-1234",
                    "expiresAt": 1_900_000_000,
                }
            else:
                result = {
                    "type": "chatgpt",
                    "loginId": "login-fixture",
                    "authUrl": "https://chatgpt.com/codex/login",
                }
            await emit({"id": request_id, "result": result})
            if login_delay:
                await asyncio.sleep(login_delay)
            if login_success:
                account_state.write_text("authenticated", encoding="utf-8")
            await emit(
                {
                    "method": "account/login/completed",
                    "params": {
                        "loginId": "login-fixture",
                        "success": login_success,
                        "error": None if login_success else "fixture login failure",
                    },
                }
            )
            if login_success:
                await emit(
                    {
                        "method": "account/updated",
                        "params": {"authMode": "chatgpt", "planType": "plus"},
                    }
                )
        elif method == "account/logout":
            account_state.unlink(missing_ok=True)
            await emit({"id": request_id, "result": {}})
        elif method == "thread/start":
            config = params.get("config")
            expected_features = {feature: False for feature in required_disabled_features}
            if (
                params.get("sandbox") != "read-only"
                or "sandboxPolicy" in params
                or not isinstance(config, dict)
                or config.get("features") != expected_features
                or config.get("approval_policy") != "never"
                or config.get("sandbox_mode") != "read-only"
                or config.get("web_search") != "disabled"
                or config.get("apps")
                != {
                    "_default": {
                        "enabled": False,
                        "default_tools_enabled": False,
                        "open_world_enabled": False,
                        "destructive_enabled": False,
                    }
                }
                or config.get("browser_use")
                != {
                    "allow_history_access": False,
                    "default_origin_policy": {
                        "access": "deny",
                        "downloads": "deny",
                        "full_cdp_access": "deny",
                        "uploads": "deny",
                    },
                }
                or config.get("computer_use") != {"default_app_access": "deny"}
                or config.get("mcp_servers") != {}
                or config.get("plugins") != {}
                or config.get("skills") != {}
                or config.get("hooks") != {}
                or not required_disabled_features <= disabled_features
            ):
                await emit(
                    {
                        "id": request_id,
                        "error": {"code": -32602, "message": "Codex native tool policy mismatch"},
                    }
                )
                continue
            await emit({"id": request_id, "result": {"thread": {"id": thread_id}}})
        elif method == "turn/start":
            if params.get("sandboxPolicy") != {"type": "readOnly"} or "sandbox" in params:
                await emit(
                    {
                        "id": request_id,
                        "error": {"code": -32602, "message": "turn/start sandbox shape mismatch"},
                    }
                )
                continue
            input_items = params.get("input", [])
            prompt = (
                str(input_items[0].get("text", ""))
                if isinstance(input_items, list) and input_items
                else ""
            )
            if prompt == "effort" and params.get("effort") != "high":
                await emit(
                    {
                        "id": request_id,
                        "error": {"code": -32602, "message": "turn/start effort mapping mismatch"},
                    }
                )
                continue
            task = asyncio.create_task(run_turn(int(request_id), params))
            turn_tasks[turn_id] = task
        elif method == "turn/interrupt":
            task = turn_tasks.get(turn_id)
            if task is not None:
                task.cancel()
            Path(os.environ["CODEX_HOME"], "observed-interrupt").write_text(
                "interrupted", encoding="utf-8"
            )
            await emit({"id": request_id, "result": {}})
            await emit(
                {
                    "method": "turn/completed",
                    "params": {
                        "threadId": thread_id,
                        "turn": {"id": turn_id, "status": "interrupted", "items": []},
                    },
                }
            )
        else:
            await emit(
                {"id": request_id, "error": {"code": -32601, "message": f"unknown method {method}"}}
            )


if __name__ == "__main__":
    asyncio.run(main())
