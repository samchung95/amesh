from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Any

from amesh.domain.runner import RunnerNetworkAccess
from amesh.domain.scripts import (
    ScriptDependency,
    ScriptSource,
    ScriptTaskPolicy,
)
from amesh.dsl.models import TaskDefinition
from amesh.executor import TaskCompletion, TaskExecutionContext, TaskHandler


@dataclass(frozen=True)
class _Language:
    name: str
    interpreter: tuple[str, ...]


_LANGUAGES = {
    "script.shell": _Language("shell", ("sh",)),
    "script.python": _Language("python", ("python",)),
    "script.node": _Language("node", ("node",)),
    "script.java": _Language("java", ("java",)),
    "script.r": _Language("r", ("Rscript",)),
    "script.powershell": _Language("powershell", ("pwsh", "-NoLogo", "-NonInteractive")),
}


def script_task_handlers(
    runner_handler: TaskHandler,
    policy: ScriptTaskPolicy | None = None,
) -> dict[str, TaskHandler]:
    active_policy = policy or ScriptTaskPolicy()
    return {
        task_type: _script_handler(runner_handler, language, active_policy)
        for task_type, language in _LANGUAGES.items()
    }


def _script_handler(
    runner_handler: TaskHandler,
    language: _Language,
    policy: ScriptTaskPolicy,
) -> TaskHandler:
    async def run(task: TaskDefinition, context: TaskExecutionContext) -> Any:
        source, arguments, interpreter, dependencies, dependency_command = _configuration(task)
        image = _select_image(task.image, language.name, policy)
        command, standard_input = _script_command(language, source, interpreter, arguments)
        if dependencies:
            _validate_dependency_policy(task, dependency_command, policy)
            command = [
                "sh",
                "-ceu",
                f'{shlex.join(dependency_command)}; exec "$@"',
                "amesh-script-bootstrap",
                *command,
            ]
        environment = {
            "AMESH_OUTPUTS_FILE": ".amesh-outputs.json",
            "AMESH_METRICS_FILE": ".amesh-metrics.json",
            "AMESH_FILES_MANIFEST": ".amesh-files.json",
            "AMESH_LOG_FORMAT": "jsonl",
            **task.environment,
        }
        compiled = task.model_copy(
            update={
                "type": "core.shell",
                "command": command,
                "standard_input": standard_input,
                "image": image,
                "environment": environment,
            }
        )
        result = await runner_handler(compiled, context)
        runtime = {
            "language": language.name,
            "interpreter": list(interpreter),
            "image": image,
            "source": source.model_dump(mode="json", exclude={"content"}, exclude_none=True),
            "packages": [item.model_dump(mode="json") for item in dependencies],
        }
        if isinstance(result, TaskCompletion):
            return result.model_copy(update={"output": {**result.output, "runtime": runtime}})
        if isinstance(result, dict):
            return {**result, "runtime": runtime}
        return result

    return run


def _configuration(
    task: TaskDefinition,
) -> tuple[ScriptSource, list[str], tuple[str, ...], tuple[ScriptDependency, ...], list[str]]:
    extra = task.model_extra or {}
    source = ScriptSource.model_validate(extra.get("source"))
    arguments = _string_list(extra.get("args", []), "args", allow_empty=True)
    configured_interpreter = extra.get("interpreter")
    interpreter = (
        tuple(_string_list(configured_interpreter, "interpreter"))
        if configured_interpreter is not None
        else _LANGUAGES[task.type].interpreter
    )
    raw_dependencies = extra.get("dependencies", [])
    if not isinstance(raw_dependencies, list):
        raise ValueError("dependencies must be an array")
    dependencies = tuple(ScriptDependency.model_validate(item) for item in raw_dependencies)
    raw_dependency_command = extra.get("dependencyCommand")
    dependency_command = (
        _string_list(raw_dependency_command, "dependencyCommand")
        if raw_dependency_command is not None
        else []
    )
    if dependency_command and not dependencies:
        raise ValueError("dependencyCommand requires declared dependencies")
    if source.type in {"namespace", "repository"} and source.path not in task.input_files:
        raise ValueError(f"{source.type} source path must be declared in inputFiles")
    return source, arguments, interpreter, dependencies, dependency_command


def _script_command(
    language: _Language,
    source: ScriptSource,
    interpreter: tuple[str, ...],
    arguments: list[str],
) -> tuple[list[str], str | None]:
    if source.type != "inline":
        assert source.path is not None
        return [*interpreter, source.path, *arguments], None
    assert source.content is not None
    if language.name == "java":
        return (
            [
                "sh",
                "-ceu",
                ('mkdir -p .amesh; cat > .amesh/Main.java; exec java .amesh/Main.java "$@"'),
                "amesh-java",
                *arguments,
            ],
            source.content,
        )
    stdin_flag = {
        "shell": ("-s", "--"),
        "python": ("-",),
        "node": ("-",),
        "r": ("-",),
        "powershell": ("-File", "-"),
    }[language.name]
    return [*interpreter, *stdin_flag, *arguments], source.content


def _validate_dependency_policy(
    task: TaskDefinition,
    command: list[str],
    policy: ScriptTaskPolicy,
) -> None:
    if not policy.dependency_installation_enabled:
        raise ValueError("runtime dependency installation is disabled by organization policy")
    if not command:
        raise ValueError("declared dependencies require dependencyCommand")
    if task.network_policy.access is not RunnerNetworkAccess.RESTRICTED:
        raise ValueError("runtime dependency installation requires restricted network access")
    requested = set(task.network_policy.allowed_egress)
    allowed = set(policy.dependency_allowed_egress)
    if not requested or not requested.issubset(allowed):
        raise ValueError("dependency network egress is not approved by organization policy")


def _select_image(requested: str | None, language: str, policy: ScriptTaskPolicy) -> str:
    default = policy.default_images[language]
    if requested is None or requested == default:
        return default
    if requested not in policy.approved_images.get(language, ()):
        raise ValueError(f"script image override is not approved for {language}")
    return requested


def _string_list(value: object, name: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{name} must be a non-empty array of strings")
    if any(not isinstance(item, str) or not item or "\x00" in item for item in value):
        raise ValueError(f"{name} entries must be non-empty, NUL-free strings")
    return list(value)
