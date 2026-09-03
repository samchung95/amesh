from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from scripts.validate_env_example import EnvironmentExampleError, validate_environment_example

ROOT = Path(__file__).resolve().parents[2]


def _example(tmp_path: Path, content: str) -> Path:
    path = tmp_path / ".env.example"
    path.write_text(content, encoding="utf-8")
    return path


def test_checked_in_environment_example_matches_settings() -> None:
    validate_environment_example(ROOT / ".env.example")


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda content: content + "\nAPP_PORT=9000\n", "duplicate.*APP_PORT"),
        (lambda content: content + "\nSTALE_SETTING=value\n", "unknown.*STALE_SETTING"),
        (
            lambda content: "\n".join(
                line
                for line in content.splitlines()
                if not line.lstrip("# ").startswith("APP_PORT=")
            ),
            "missing.*APP_PORT",
        ),
    ],
)
def test_environment_example_rejects_name_drift(
    tmp_path: Path,
    mutate: Callable[[str], str],
    expected: str,
) -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    path = _example(tmp_path, mutate(content))

    with pytest.raises(EnvironmentExampleError, match=expected):
        validate_environment_example(path)


def test_environment_example_rejects_invalid_values_without_exposing_secrets(
    tmp_path: Path,
) -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    content = content.replace("APP_PORT=8000", "APP_PORT=invalid")
    content = content.replace(
        "OPENROUTER_API_KEY=your-key-here", "OPENROUTER_API_KEY=canary-secret"
    )

    with pytest.raises(
        EnvironmentExampleError, match="invalid environment example value"
    ) as caught:
        validate_environment_example(_example(tmp_path, content))

    assert "canary-secret" not in str(caught.value)
