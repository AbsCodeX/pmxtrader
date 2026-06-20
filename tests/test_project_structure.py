"""Project structure invariants (Batch J)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRY_POINTS = [
    "pmx",
    "scripts/pmx.sh",
    "scripts/pmxt-cockpit.sh",
    "scripts/pmxt-dashboard-server.py",
    "scripts/pmxt-dashboard.sh",
    "scripts/agent-run.sh",
    "scripts/kill-switch.sh",
    "apps/cockpit/__main__.py",
]

SHARED_BRIDGE_MODULES = [
    "apps/bridge/commands.py",
    "apps/bridge/parse.py",
    "apps/bridge/trade_safety.py",
    "apps/bridge/dashboard_security.py",
    "apps/bridge/pmxt_cli.py",
]

COCKPIT_ADAPTER = [
    "apps/cockpit/bridge/pmx.py",
    "apps/cockpit/bridge/live.py",
]

WEB_DASHBOARD = [
    "dashboard/index.html",
    "dashboard/css/app.css",
    "dashboard/js/app.js",
]

CONFIG_FILES = [
    "config/agents.json",
    "config/providers.json",
]

DEPRECATED_PLACEHOLDER_READMES = [
    "apps/dashboard/README.md",
    "apps/cli/README.md",
]


def test_main_entry_points_exist():
    for rel in ENTRY_POINTS:
        assert (ROOT / rel).is_file(), rel


def test_shared_bridge_modules_exist():
    for rel in SHARED_BRIDGE_MODULES:
        assert (ROOT / rel).is_file(), rel


def test_web_dashboard_at_repo_root_not_apps():
    for rel in WEB_DASHBOARD:
        assert (ROOT / rel).is_file(), rel
    assert not any((ROOT / "apps/dashboard").glob("*.html"))
    assert (ROOT / "apps/dashboard/README.md").is_file()


def test_config_separate_from_env_example():
    assert (ROOT / "config/agents.json").is_file()
    assert (ROOT / "pmxt/.env.example").is_file() or (ROOT / "pmxt/.env").is_file()
    agents = (ROOT / "config/agents.json").read_text(encoding="utf-8")
    assert "KALSHI_API_KEY" not in agents
    assert "SECRET" not in agents.upper() or "humanGate" in agents


def test_cockpit_adapter_imports_shared_bridge():
    pmx_py = (ROOT / "apps/cockpit/bridge/pmx.py").read_text(encoding="utf-8")
    assert "from apps.bridge" in pmx_py
    live_py = (ROOT / "apps/cockpit/bridge/live.py").read_text(encoding="utf-8")
    assert "from apps.bridge import parse" in live_py


def test_trade_logic_not_in_dashboard_js():
    app_js = (ROOT / "dashboard/js/app.js").read_text(encoding="utf-8")
    assert "order:create" not in app_js
    assert "resolve_dashboard_command" not in app_js


def test_architecture_doc_points_to_structure_guide():
    arch = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    assert "docs/project-structure.md" in arch
    assert "apps/dashboard/" not in arch or "deprecated" in arch.lower() or "Reserved" in arch


def test_deprecated_placeholders_documented():
    for rel in DEPRECATED_PLACEHOLDER_READMES:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "reserved" in text or "deprecated" in text or "placeholder" in text
