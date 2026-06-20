from __future__ import annotations

import json
from unittest.mock import patch

from apps.cockpit.bridge import pmx
from apps.cockpit.bridge.live import _count_positions


def test_run_script_rejects_traversal():
    result = pmx.run_script("../pmx")
    assert result["ok"] is False
    assert "Invalid" in (result.get("error") or "")


def test_run_script_rejects_absolute_path():
    result = pmx.run_script("/etc/passwd")
    assert result["ok"] is False


def test_analyze_link_rejects_bad_scheme():
    result = pmx.analyze_link("javascript:alert(1)")
    assert result["ok"] is False


def test_analyze_link_accepts_kalshi_host():
    with patch.object(pmx, "run_argv", return_value={"ok": True, "stdout": "ok"}) as run:
        result = pmx.analyze_link("https://kalshi.com/markets/foo")
    assert result["ok"] is True
    assert result["venue"] == "kalshi"
    assert run.called


def test_analyze_link_rejects_unknown_host():
    result = pmx.analyze_link("https://evil.example.com/kalshi")
    assert result["ok"] is False


def test_count_positions_json_list():
    body = json.dumps([{"ticker": "A"}, {"ticker": "B"}])
    assert _count_positions(body) == 2


def test_count_positions_skips_headers():
    body = "=== Positions ===\nTicker  Size\nFOO  1\nBAR  2\n"
    assert _count_positions(body) == 2


def test_fetch_balances_parallel_returns_separate_venues():
    from apps.cockpit.bridge.live import _fetch_balances_parallel

    def fake_run_pmx(*args, **kwargs):
        if args == ("balance",):
            return {"ok": True, "stdout": '[{"available": 50.0, "total": 50.0}]'}
        if args == ("poly", "balance"):
            return {"ok": True, "stdout": '[{"available": 12.5, "total": 20.0}]'}
        return {"ok": False, "stdout": ""}

    with patch("apps.cockpit.bridge.live.pmx.run_pmx", side_effect=fake_run_pmx):
        kalshi, poly = _fetch_balances_parallel()
    assert kalshi == ("50.00", "50.00")
    assert poly == ("12.50", "20.00")
    assert kalshi[0] != poly[0]
