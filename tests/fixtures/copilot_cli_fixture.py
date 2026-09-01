"""Provider-free Copilot CLI JSONL fixture used by adapter tests."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


def _emit(value: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(value, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def _record_invocation() -> list[str]:
    home = Path(os.environ["COPILOT_HOME"])
    args = sys.argv[1:]
    attachments = [
        Path(args[index + 1]).exists()
        for index, value in enumerate(args[:-1])
        if value == "--attachment"
    ]
    (home / "fixture-args.json").write_text(
        json.dumps(
            {
                "args": args,
                "cwd": os.getcwd(),
                "cwd_entries": sorted(os.listdir()),
                "attachment_exists": attachments,
                "environment": dict(os.environ),
            }
        ),
        encoding="utf-8",
    )
    return args


def main() -> int:
    args = _record_invocation()
    if args[:2] == ["login", "--device-code"]:
        sys.stdout.write(
            "https://github.com/login/device https://docs.github.com/copilot "
            "ABCD-1234\n"
        )
        sys.stdout.flush()
        time.sleep(0.05)
        return 0
    if args[:2] == ["login", "--web-flow"]:
        _emit(
            {
                "type": "auth.challenge",
                "data": {"authUrl": "https://github.com/login/oauth/authorize?state=fixture"},
            }
        )
        time.sleep(0.05)
        return 0
    if args[:2] == ["auth", "logout"]:
        return 17
    if "-p" not in args:
        for line in sys.stdin:
            if line.strip() == "/logout":
                (Path(os.environ["COPILOT_HOME"]) / "fixture-logout").write_text(
                    "ok", encoding="utf-8"
                )
            if line.strip() in {"/exit", "/quit"}:
                return 0
        return 0
    if "malformed" in args:
        sys.stdout.write("not-json\n")
        sys.stdout.flush()
        return 0
    if "error" in args:
        _emit({"type": "error", "data": {"message": "fixture failure"}})
        return 1
    if "wait" in args:
        time.sleep(30)
        return 0
    prompt = args[args.index("-p") + 1] if "-p" in args else ""
    if "slow" in args:
        for event in (
            {"type": "session.start", "data": {"sessionId": "fixture-session"}},
            {"type": "assistant.turn_start", "data": {"turnId": "0"}},
            {"type": "assistant.message_delta", "data": {"deltaContent": "copilot"}},
            {"type": "assistant.message", "data": {"content": "copilot-ready"}},
            {"type": "result", "data": {"result": "copilot-ready"}},
        ):
            time.sleep(0.1)
            _emit(event)
        return 0
    _emit({"type": "session.start", "data": {"sessionId": "fixture-session"}})
    _emit({"type": "assistant.turn_start", "data": {"turnId": "0"}})
    content = '{"answer":"ok"}' if "JSON Schema" in prompt else "copilot-ready"
    _emit({"type": "assistant.message_delta", "data": {"deltaContent": content[:7]}})
    if "no-usage" not in args:
        _emit(
            {
                "type": "usage",
                "data": {"usage": {"inputTokens": 3, "outputTokens": 2, "aiCredits": 0.5}},
            }
        )
    _emit({"type": "assistant.message", "data": {"content": content}})
    _emit({"type": "result", "data": {"result": content}})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
