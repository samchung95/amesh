from __future__ import annotations

import asyncio
import sys
from typing import cast
from uuid import uuid4

import pytest
from pydantic import ValidationError

from amesh.adapters.local import LocalProcessRunner
from amesh.domain.runner import RunnerId, RunnerPolicySet
from amesh.domain.scripts import SCRIPT_TASK_TYPES, ScriptTaskPolicy
from amesh.dsl import ResourceKind, TaskDefinition, default_resource_registry
from amesh.executor import (
    TaskCompletion,
    TaskExecutionContext,
    local_process_handler,
    required_runner_ids,
)
from amesh.tasks import script_task_handlers


def _context() -> TaskExecutionContext:
    return TaskExecutionContext(
        tenant_id="default",
        execution_id=uuid4(),
        task_run_id=uuid4(),
        attempt=1,
        attempt_id=uuid4(),
        inputs={},
        outputs={},
        variables={},
    )


def _task(task_type: str, **extra: object) -> TaskDefinition:
    return TaskDefinition(id="script", type=task_type, **extra)


@pytest.mark.parametrize("task_type", sorted(SCRIPT_TASK_TYPES))
def test_urs_f_0344_0348_0349_language_contracts_use_immutable_images(
    task_type: str,
) -> None:
    captured: list[TaskDefinition] = []

    async def runner(task: TaskDefinition, context: TaskExecutionContext) -> TaskCompletion:
        del context
        captured.append(task)
        return TaskCompletion(output={"stdout": "ok"})

    argument = "$(must-not-be-interpolated)"
    result = asyncio.run(
        script_task_handlers(runner)[task_type](
            _task(
                task_type,
                source={"type": "inline", "content": "print('hello')"},
                args=[argument],
                environment={"UNTRUSTED": "; echo must-not-run"},
            ),
            _context(),
        )
    )

    assert isinstance(result, TaskCompletion)
    compiled = captured[0]
    assert compiled.type == "core.shell"
    assert compiled.image is not None and "@sha256:" in compiled.image
    assert argument in cast(list[str], compiled.command)
    assert compiled.environment["UNTRUSTED"] == "; echo must-not-run"
    assert compiled.environment["AMESH_OUTPUTS_FILE"] == ".amesh-outputs.json"
    assert compiled.environment["AMESH_METRICS_FILE"] == ".amesh-metrics.json"
    assert compiled.environment["AMESH_FILES_MANIFEST"] == ".amesh-files.json"
    assert "print('hello')" not in " ".join(cast(list[str], compiled.command))
    assert result.output["runtime"]["language"] == task_type.removeprefix("script.")
    assert result.output["runtime"]["packages"] == []


@pytest.mark.parametrize("source_type", ["namespace", "repository", "package"])
def test_urs_f_0345_staged_and_packaged_sources_use_workspace_paths(source_type: str) -> None:
    captured: list[TaskDefinition] = []

    async def runner(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, object]:
        del context
        captured.append(task)
        return {"ok": True}

    input_files = (
        {"src/main.py": "nsfile:///scripts/main.py"}
        if source_type in {"namespace", "repository"}
        else {}
    )
    if source_type == "repository":
        input_files["src/main.py"] = "s3://amesh/default/repository/main.py"
    result = asyncio.run(
        script_task_handlers(runner)["script.python"](
            _task(
                "script.python",
                source={"type": source_type, "path": "src/main.py"},
                inputFiles=input_files,
                args=["one"],
            ),
            _context(),
        )
    )

    assert captured[0].command[-2:] == ["src/main.py", "one"]
    assert captured[0].standard_input is None
    assert result["runtime"]["source"] == {"type": source_type, "path": "src/main.py"}


def test_urs_f_0346_dependencies_require_supply_chain_and_network_policy() -> None:
    calls: list[TaskDefinition] = []

    async def runner(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, object]:
        del context
        calls.append(task)
        return {}

    dependency = {
        "name": "example",
        "version": "1.2.3",
        "digest": "sha256:" + "1" * 64,
    }
    task = _task(
        "script.python",
        source={"type": "inline", "content": "print('ok')"},
        dependencies=[dependency],
        dependencyCommand=["python", "-m", "pip", "install", "example==1.2.3"],
        networkPolicy={"access": "restricted", "allowedEgress": ["pypi.org:443"]},
    )

    with pytest.raises(ValueError, match="disabled by organization policy"):
        asyncio.run(script_task_handlers(runner)["script.python"](task, _context()))

    policy = ScriptTaskPolicy(
        dependencyInstallationEnabled=True,
        dependencyAllowedEgress=("pypi.org:443",),
    )
    result = asyncio.run(script_task_handlers(runner, policy)["script.python"](task, _context()))

    assert result["runtime"]["packages"] == [dependency]
    assert calls[0].command[:2] == ["sh", "-ceu"]
    assert calls[0].command[-2:] == ["python", "-"]


def test_urs_f_0348_only_operator_approved_image_overrides_are_accepted() -> None:
    approved = "registry.example.test/python@sha256:" + "2" * 64
    policy = ScriptTaskPolicy(approvedImages={"python": [approved]})

    async def runner(task: TaskDefinition, context: TaskExecutionContext) -> dict[str, object]:
        del context
        return {"image": task.image}

    handler = script_task_handlers(runner, policy)["script.python"]
    result = asyncio.run(
        handler(
            _task(
                "script.python",
                image=approved,
                source={"type": "inline", "content": "print('ok')"},
            ),
            _context(),
        )
    )
    assert result["image"] == approved

    with pytest.raises(ValueError, match="not approved"):
        asyncio.run(
            handler(
                _task(
                    "script.python",
                    image="registry.example.test/python@sha256:" + "3" * 64,
                    source={"type": "inline", "content": "print('ok')"},
                ),
                _context(),
            )
        )

    with pytest.raises(ValidationError, match="immutable sha256"):
        ScriptTaskPolicy(approvedImages={"python": ["python:latest"]})


def test_urs_f_0347_0351_python_sample_contract_executes_locally() -> None:
    task = _task(
        "script.python",
        source={"type": "inline", "content": "import os; print(os.environ['VALUE'])"},
        interpreter=[sys.executable],
        args=["literal;argument"],
        environment={"VALUE": "script-pack-ok"},
        taskRunner={"type": "local"},
    )

    result = asyncio.run(
        script_task_handlers(local_process_handler(LocalProcessRunner()))["script.python"](
            task,
            _context(),
        )
    )

    assert isinstance(result, TaskCompletion)
    assert result.output["stdout"].strip() == "script-pack-ok"
    assert result.output["metrics"]["duration_seconds"] >= 0
    assert result.output["runtime"]["interpreter"] == [sys.executable]


def test_urs_f_0351_catalog_and_runner_discovery_include_every_language() -> None:
    registry = default_resource_registry()
    assert all(
        registry.descriptor(ResourceKind.TASK, task_type) is not None
        for task_type in SCRIPT_TASK_TYPES
    )
    task = _task(
        "script.python",
        source={"type": "inline", "content": "print('ok')"},
        taskRunner={"type": "local"},
    )
    assert required_runner_ids(
        (task,),
        RunnerPolicySet(),
        namespace="tests.scripts",
        fallback=RunnerId.KUBERNETES,
    ) == {RunnerId.LOCAL}
