from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "frontend" / "src"
FEATURE_ROOT = SOURCE_ROOT / "features"
FEATURES = frozenset(
    {
        "administration",
        "agent-sessions",
        "agents",
        "apps",
        "assets",
        "blueprints",
        "checks",
        "dashboards",
        "executions",
        "namespaces",
        "plugins",
        "releases",
        "search",
        "session-administration",
        "triggers",
        "workflows",
    }
)
ALLOWED_FEATURE_IMPORTS = frozenset(
    {
        ("executions", "agent-sessions"),
        ("executions", "workflows"),
        ("session-administration", "agent-sessions"),
        ("workflows", "agents"),
        ("workflows", "blueprints"),
    }
)
IMPORT_PATTERN = re.compile(
    r"(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?['\"](\.[^'\"]+)['\"]",
    re.MULTILINE,
)
GUARDED_ROUTE_PATTERN = re.compile(
    r'^<Route\s+(index|path="([^"]+)")\s+element={<CapabilityRoute '
    r'session={session} capability="([^"]+)" title="([^"]+)">.*'
    r"</CapabilityRoute>}\s*/>$"
)
INFRASTRUCTURE_ROUTES = frozenset(
    {
        "<Route element={<AppShell session={session} />}>",
        '<Route path="*" element={<Navigate to="/" replace />} />',
    }
)
EXPECTED_ROUTES = (
    ("embed/apps/:namespace/:appId", "apps.view", "App"),
    ("<index>", "dashboards.view", "Dashboard"),
    ("search", "search.view", "Search"),
    ("flows", "flows.view", "Flows"),
    ("blueprints", "flows.view", "Blueprints"),
    ("flows/new", "flows.create", "Create workflow"),
    ("flows/:namespace/:flowId/edit", "flows.update", "Edit flow"),
    ("flows/:namespace/:flowId/tests", "flowTests.view", "Flow tests"),
    ("flows/:namespace/:flowId", "flows.view", "Flow"),
    ("executions", "executions.view", "Executions"),
    ("executions/:executionId", "executions.view", "Execution"),
    ("triggers", "triggers.view", "Triggers"),
    ("checks", "checks.view", "Checks"),
    ("namespaces", "namespaceResources.read", "Namespaces"),
    ("assets", "assets.view", "Assets"),
    ("agents", "agents.view", "Agents"),
    ("agent-sessions", "agentSessions.view", "Agent sessions"),
    (
        "session-administration",
        "agentSessionAdministration.view",
        "Session orchestrator",
    ),
    ("apps", "apps.view", "Apps"),
    ("apps/:namespace/:appId", "apps.view", "App"),
    ("plugins", "plugins.view", "Plugins"),
    ("releases", "releases.view", "Releases"),
    ("administration", "administration.manage", "Administration"),
)


def _typescript_files() -> tuple[Path, ...]:
    return tuple(sorted((*SOURCE_ROOT.rglob("*.ts"), *SOURCE_ROOT.rglob("*.tsx"))))


def _resolve_import(source: Path, specifier: str) -> Path | None:
    base = source.parent / specifier
    candidates = (
        base.with_suffix(".ts"),
        base.with_suffix(".tsx"),
        base / "index.ts",
        base / "index.tsx",
    )
    return next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)


def _feature_name(path: Path) -> str | None:
    try:
        return path.relative_to(FEATURE_ROOT).parts[0]
    except ValueError:
        return None


def _route_declarations(source: str) -> tuple[str, ...]:
    declarations: list[str] = []
    for match in re.finditer(r"<Route\b", source):
        braces = 0
        quote: str | None = None
        escaped = False
        for index in range(match.start(), len(source)):
            character = source[index]
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
                continue
            if character in {'"', "'"}:
                quote = character
            elif character == "{":
                braces += 1
            elif character == "}":
                braces -= 1
            elif character == ">" and braces == 0:
                declarations.append(" ".join(source[match.start() : index + 1].split()))
                break
        else:
            raise AssertionError("Unterminated <Route> declaration")
    return tuple(declarations)


def _assert_route_contract(source: str) -> None:
    declarations = _route_declarations(source)
    guarded: list[tuple[str, str, str]] = []
    unexpected: list[str] = []
    for declaration in declarations:
        if declaration in INFRASTRUCTURE_ROUTES:
            continue
        match = GUARDED_ROUTE_PATTERN.fullmatch(declaration)
        if match is None:
            unexpected.append(declaration)
            continue
        route_kind, path, capability, title = match.groups()
        guarded.append((path if route_kind != "index" else "<index>", capability, title))

    assert unexpected == [], f"Unexpected or unguarded routes: {unexpected}"
    assert len(declarations) == len(EXPECTED_ROUTES) + len(INFRASTRUCTURE_ROUTES)
    assert tuple(guarded) == EXPECTED_ROUTES


def test_frontend_views_models_and_tests_live_in_feature_boundaries() -> None:
    assert {path.name for path in FEATURE_ROOT.iterdir() if path.is_dir()} == FEATURES
    assert not tuple((SOURCE_ROOT / "components").glob("*"))
    assert not tuple((SOURCE_ROOT / "pages").glob("*"))

    for feature in FEATURES:
        feature_root = FEATURE_ROOT / feature
        assert (feature_root / "index.ts").is_file(), feature
        assert tuple(feature_root.glob("*Page.tsx")), feature


def test_cross_feature_imports_use_declared_public_surfaces() -> None:
    violations: list[str] = []
    for source in _typescript_files():
        source_feature = _feature_name(source)
        for specifier in IMPORT_PATTERN.findall(source.read_text(encoding="utf-8")):
            target = _resolve_import(source, specifier)
            if target is None:
                continue
            target_feature = _feature_name(target)
            if target_feature is None:
                continue
            if source.is_relative_to(SOURCE_ROOT / "api") or source.is_relative_to(
                SOURCE_ROOT / "shared"
            ):
                violations.append(
                    f"{source.relative_to(SOURCE_ROOT)} imports feature {target_feature}"
                )
                continue
            if source_feature == target_feature:
                continue
            if target.name != "index.ts":
                violations.append(
                    f"{source.relative_to(SOURCE_ROOT)} bypasses {target_feature}/index.ts"
                )
                continue
            if (
                source_feature is not None
                and (
                    source_feature,
                    target_feature,
                )
                not in ALLOWED_FEATURE_IMPORTS
            ):
                violations.append(f"undeclared feature edge {source_feature} -> {target_feature}")

    assert violations == []


def test_workspace_route_and_capability_contract_is_unchanged() -> None:
    source = (SOURCE_ROOT / "App.tsx").read_text(encoding="utf-8")
    _assert_route_contract(source)


def test_workspace_route_contract_rejects_an_extra_unguarded_route() -> None:
    source = (SOURCE_ROOT / "App.tsx").read_text(encoding="utf-8")
    mutated = source.replace(
        '        <Route path="*" element={<Navigate to="/" replace />} />',
        '        <Route path="unguarded" element={<div />} />\n'
        '        <Route path="*" element={<Navigate to="/" replace />} />',
    )

    with pytest.raises(AssertionError, match="Unexpected or unguarded routes"):
        _assert_route_contract(mutated)
