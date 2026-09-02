from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE_TARGET = "/var/lib/amesh/model-engines"


class _ComposeLoader(yaml.SafeLoader):
    pass


_ComposeLoader.add_constructor("!reset", lambda _loader, _node: None)


def test_model_engine_overlay_uses_one_pinned_image_and_shared_state() -> None:
    overlay = yaml.load(
        (ROOT / "docker/compose.model-engines.yaml").read_text(encoding="utf-8"),
        Loader=_ComposeLoader,
    )
    services = overlay["services"]

    assert set(services) == {"api", "executor"}
    for service in services.values():
        assert service["image"] == "amesh:model-engines-local"
        assert service["environment"]["MODEL_ENGINE_STATE_ROOT"] == STATE_TARGET
        assert (
            service["environment"]["MODEL_ENGINE_COPILOT_ALLOW_PLAINTEXT_TOKEN_STORAGE"] == "true"
        )
        assert service["volumes"] == [f"model-engine-state:{STATE_TARGET}"]

    assert services["api"]["build"]["target"] == "runtime-model-engines"
    assert services["executor"]["build"] is None
    assert set(overlay["volumes"]) == {"model-engine-state"}


def test_model_engine_runtime_dependencies_are_exactly_pinned() -> None:
    package = json.loads(
        (ROOT / "docker" / "model-engines" / "package.json").read_text(encoding="utf-8")
    )
    lock = json.loads(
        (ROOT / "docker" / "model-engines" / "package-lock.json").read_text(encoding="utf-8")
    )

    expected = {"@github/copilot": "1.0.82", "@openai/codex": "0.151.0"}
    assert package["dependencies"] == expected
    assert lock["packages"][""]["dependencies"] == expected
    assert lock["packages"]["node_modules/@github/copilot"]["version"] == "1.0.82"
    assert lock["packages"]["node_modules/@openai/codex"]["version"] == "0.151.0"


def test_model_engine_image_declares_terminal_runtime_dependency() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "apt-get install -y --no-install-recommends bsdutils" in dockerfile
