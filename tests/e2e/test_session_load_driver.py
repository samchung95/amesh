from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.qualify_session_load import Launched, judge, mark_shared_runs, stub_reply  # noqa: E402


def test_stub_echoes_the_session_nonce_and_the_judge_rejects_any_other_answer() -> None:
    nonce = "nonce-" + "a" * 32
    content, usage = stub_reply(
        {"messages": [{"role": "user", "content": json.dumps({"nonce": nonce})}]}
    )
    action = json.loads(content)
    assert (action["action"], action["output"]) == ("final", {"answer": nonce})
    assert usage["cost"] == 0

    echoed = Launched("first", nonce, 0.0)
    judge(
        echoed,
        {
            "state": "SUCCEEDED",
            "result": {"answer": nonce},
            "createdAt": "2026-10-07T00:00:00+00:00",
            "completedAt": "2026-10-07T00:00:01.500000+00:00",
        },
    )
    assert (echoed.state, echoed.server_seconds) == ("SUCCEEDED", 1.5)

    crossed = Launched("second", "nonce-" + "b" * 32, 0.0)
    judge(crossed, {"state": "SUCCEEDED", "result": {"answer": nonce}})
    assert crossed.state == "MISMATCHED"


def test_a_session_that_ran_twice_or_shares_its_run_fails_verification() -> None:
    nonce = "nonce-" + "c" * 32

    def succeeded(
        execution: str, task_run: str, attempt: int = 1, epoch: int = 1
    ) -> dict[str, object]:
        return {
            "state": "SUCCEEDED",
            "result": {"answer": nonce},
            "executionId": execution,
            "taskRunId": task_run,
            "attempt": attempt,
            "executionEpoch": epoch,
        }

    retried = Launched("retried", nonce, 0.0)
    judge(retried, succeeded("e1", "t1", attempt=2))
    assert retried.state == "RETRIED"
    recovered = Launched("recovered", nonce, 0.0)
    judge(recovered, succeeded("e2", "t2", epoch=2))
    assert recovered.state == "RETRIED"

    own, shared_a, shared_b = (Launched(name, nonce, 0.0) for name in ("own", "a", "b"))
    judge(own, succeeded("e3", "t3"))
    judge(shared_a, succeeded("e4", "t4"))
    judge(shared_b, succeeded("e4", "t5"))
    mark_shared_runs([own, shared_a, shared_b])
    assert (own.state, shared_a.state, shared_b.state) == ("SUCCEEDED", "DUPLICATED", "DUPLICATED")
