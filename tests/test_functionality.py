"""Functionality review smoke tests (Batch H) — no live venue API required."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_pmx_help_exits_zero():
    proc = subprocess.run(
        [str(ROOT / "pmx"), "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "pmx" in proc.stdout.lower()


def test_cockpit_import_with_venv_deps():
    pytest.importorskip("textual")
    from apps.cockpit.app import CockpitApp  # noqa: F401


def test_dashboard_server_imports():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "pmxt_dashboard_server",
        ROOT / "scripts" / "pmxt-dashboard-server.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    assert mod.detect_venue("https://kalshi.com/markets/foo") == "kalshi"
    assert mod.detect_venue("https://polymarket.us/market/bar") == "poly"
    assert mod.detect_venue("https://evil.example.com") is None


def test_dashboard_analyze_rejects_unknown_host():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "pmxt_dashboard_server",
        ROOT / "scripts" / "pmxt-dashboard-server.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    result = mod.analyze_link("https://example.com/not-a-market")
    assert result["ok"] is False
    assert "Unrecognized link" in result.get("error", "")


@pytest.mark.parametrize(
    "cmd",
    [
        "status",
        "balance",
        "positions",
        "poly balance",
        "poly positions",
        "poly orders",
        "quote EVENT USA 1",
        "poly quote slug long",
        "poly markets",
        "poly markets soccer",
        "warm",
    ],
)
def test_dashboard_allows_safe_commands(cmd):
    from apps.bridge.commands import resolve_dashboard_command

    argv = resolve_dashboard_command(cmd)
    assert argv is not None, cmd
    assert argv[0] == "./pmx"


@pytest.mark.parametrize(
    "cmd",
    [
        "trade MARKET USA 1",
        "poly trade slug long 1",
        "poly sell slug long 1",
        "poly cancel-all",
        "panic",
        "scout grok",
        "trader openai briefs/x.md",
        "resume",
    ],
)
def test_dashboard_blocks_dangerous_or_agent_commands(cmd):
    from apps.bridge.commands import resolve_dashboard_command

    assert resolve_dashboard_command(cmd) is None


def test_palette_blocks_agents_and_trades():
    from apps.bridge.commands import is_palette_allowed

    assert not is_palette_allowed("scout grok")
    assert not is_palette_allowed("trader openai brief.md")
    assert not is_palette_allowed("panic")
    assert is_palette_allowed("poly markets soccer")


def test_ai_suggested_trade_is_not_safe_read():
    from apps.bridge.commands import classify_command

    assert classify_command("./pmx trade MARKET USA 1") == "trade"
    assert classify_command("./pmx scout grok") == "unknown"


def test_fetch_poly_markets_parses_json():
    from apps.cockpit.bridge.live import fetch_poly_markets

    payload = [{"title": "Test Market", "slug": "test-slug", "volume": 1000, "outcomes": [{"price": 0.42}]}]
    with patch("apps.cockpit.bridge.live.pmx.run_pmx", return_value={"ok": True, "stdout": json.dumps(payload)}):
        rows = fetch_poly_markets("soccer", limit=5)
    assert len(rows) == 1
    assert rows[0]["slug"] == "test-slug"
    assert rows[0]["price"] == "0.42"


def test_fetch_dashboard_snapshot_parses_balances():
    from apps.cockpit.bridge.live import fetch_snapshot

    status_out = "OFF (/tmp/KILL_SWITCH)\nKalshi: available: 100.50 total: 100.50\nPolymarket US: available: 25.00\n"
    with patch(
        "apps.cockpit.bridge.live.pmx.run_pmx",
        return_value={"ok": True, "stdout": status_out},
    ), patch(
        "apps.cockpit.bridge.live.record",
        return_value={"kalshi": [], "poly": []},
    ):
        snap = fetch_snapshot()
    assert snap.kill_switch == "OFF"
    assert snap.kalshi_available == "100.50"
    assert snap.poly_available == "25.00"


def test_positions_preview_counts_lines():
    from apps.cockpit.bridge.live import _positions_preview

    kalshi_out = "=== Positions ===\nTICKER  SIZE\nFOO  1\nBAR  2\n"
    poly_out = "[]"
    side = iter(
        [
            {"ok": True, "stdout": kalshi_out},
            {"ok": True, "stdout": poly_out},
        ]
    )

    with patch("apps.cockpit.bridge.live.pmx.run_pmx", side_effect=lambda *a, **k: next(side)):
        text, count = _positions_preview()
    assert "Kalshi" in text
    assert count >= 2


def test_trader_agent_rejects_unapproved_brief(tmp_path: Path):
    brief = tmp_path / "brief.md"
    brief.write_text("---\napproved: false\n---\n# Brief\n")
    proc = subprocess.run(
        [str(ROOT / "scripts" / "agent-run.sh"), "trader", "openai", str(brief)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode != 0
    assert "not approved" in (proc.stderr + proc.stdout).lower()


def test_brief_approval_gate_matches_agent_run(tmp_path: Path):
    """Same rule as agent-run.sh: approved: true in brief frontmatter."""
    import re

    approved = tmp_path / "ok.md"
    approved.write_text("---\napproved: true\n---\n")
    pending = tmp_path / "no.md"
    pending.write_text("approved: false\n")

    pattern = re.compile(r"^approved:\s*true", re.MULTILINE | re.IGNORECASE)
    assert pattern.search(approved.read_text())
    assert not pattern.search(pending.read_text())
