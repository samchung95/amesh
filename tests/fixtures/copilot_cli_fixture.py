"""Provider-free Copilot CLI JSONL fixture used by adapter tests."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_PLAINTEXT_STORAGE_PROMPT = (
    "System keychain unavailable. Store token in plaintext config file? (y/N) "
)


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


def _wait_for_release(home: Path, mode: str) -> None:
    (home / f"fixture-login-{mode}-ready").write_text("ready", encoding="utf-8")
    release = home / f"fixture-login-{mode}-release"
    deadline = time.monotonic() + 5
    while not release.exists() and time.monotonic() < deadline:
        time.sleep(0.01)


def _login(args: list[str]) -> tuple[str, str] | None:
    try:
        index = args.index("login")
        option = args[index + 1]
    except (ValueError, IndexError):
        return None
    if option not in {"--device-code", "--web-flow"}:
        return None
    return ("device" if option == "--device-code" else "browser", option)


def main() -> int:
    args = _record_invocation()
    login = _login(args)
    if login is not None:
        mode, _ = login
        home = Path(os.environ["COPILOT_HOME"])
        if mode == "device":
            sys.stdout.write(
                "https://github.com/login/device https://docs.github.com/copilot ABCD-1234\n"
            )
            sys.stdout.flush()
        else:
            _emit(
                {
                    "type": "auth.challenge",
                    "data": {"authUrl": "https://github.com/login/oauth/authorize?state=fixture"},
                }
            )
        if "--login-large" in args:
            sys.stdout.write("diagnostic output drained safely\n" * 8192)
            sys.stdout.flush()
        if "--login-fail-secret" in args:
            sys.stdout.write(
                "\x1b[31mrefresh_token=CANARY_REFRESH_1234567890 "
                "Bearer CANARY_BEARER_1234567890 ABCD-1234 "
                "https://github.com/login/oauth/authorize?state=fixture\x1b[0m\n"
            )
            sys.stdout.flush()
            return 17
        if "--login-hold" in args:
            _wait_for_release(home, mode)
        if "--login-plaintext" in args or "--login-plaintext-near" in args:
            prompt = _PLAINTEXT_STORAGE_PROMPT
            if "--login-plaintext-near" in args:
                prompt = prompt.replace("plaintext config file", "local config file")
            sys.stdout.write(prompt)
            sys.stdout.flush()
            consent = sys.stdin.readline().strip()
            (home / "fixture-plaintext-consent").write_text(consent, encoding="utf-8")
            return 0 if consent.casefold() == "y" else 19
        if not any(
            flag in args for flag in ("--login-large", "--login-hold", "--login-fail-secret")
        ):
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
