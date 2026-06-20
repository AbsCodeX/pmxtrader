from apps.bridge.commands import classify_command, is_palette_allowed, resolve_dashboard_command
from apps.bridge.dotenv import parse_dotenv
from apps.bridge.parse import parse_balance_json, parse_kill_switch, parse_status


def test_parse_engaged_kill_switch():
    stdout = "ENGAGED — halftime (/Users/me/pmxtrader/KILL_SWITCH)\nKalshi: available: 42.00"
    assert parse_kill_switch(stdout) == "ON"
    assert parse_status(stdout).kill_switch == "ON"


def test_parse_off_kill_switch():
    stdout = "OFF (/Users/me/pmxtrader/KILL_SWITCH)\nKalshi:"
    assert parse_kill_switch(stdout) == "OFF"


def test_parse_status_ignores_panic_scope_lines():
    """Poly must not inherit Kalshi cash from panic-scope 'Polymarket US: included'."""
    stdout = """OFF (/tmp/KILL_SWITCH)
Panic scope (cancel resting orders + market flatten when keys set):
  Kalshi: included
  Polymarket US: included

Kalshi:
  available: 100.50  total: 100.50

Polymarket US:
  available: 25.00  total: 30.00  currency: USD
"""
    s = parse_status(stdout)
    assert s.kalshi_available == "100.50"
    assert s.kalshi_total == "100.50"
    assert s.poly_available == "25.00"
    assert s.poly_total == "30.00"
    assert s.poly_available != s.kalshi_available


def test_parse_balance_json_kalshi_raw():
    avail, total = parse_balance_json('[{"available": 42.5, "total": 100.0}]')
    assert avail == "42.50"
    assert total == "100.00"


def test_parse_balance_json_poly_with_header():
    stdout = "=== Polymarket US balance ===\n" '[{"available": 25.0, "total": 50.0}]'
    avail, total = parse_balance_json(stdout)
    assert avail == "25.00"
    assert total == "50.00"


def test_classify_poly_cancel_all_blocked():
    assert classify_command("./pmx poly cancel-all") == "trade"


def test_classify_status_safe():
    assert classify_command("./pmx status") == "safe"


def test_classify_resume_mutating():
    assert classify_command("./pmx resume") == "mutating"


def test_classify_unknown_scout():
    assert classify_command("./pmx scout grok") == "unknown"


def test_palette_allowlist():
    assert is_palette_allowed("status")
    assert is_palette_allowed("preflight")
    assert is_palette_allowed("poly markets soccer")
    assert is_palette_allowed("dashboard")
    assert not is_palette_allowed("panic")
    assert not is_palette_allowed("scout grok")


def test_resolve_dashboard_blocks_trade():
    assert resolve_dashboard_command("trade MARKET USA 1") is None
    assert resolve_dashboard_command("poly cancel-all") is None


def test_resolve_dashboard_allows_status():
    argv = resolve_dashboard_command("status")
    assert argv == ["./pmx", "status"]


def test_resolve_dashboard_allows_preflight():
    argv = resolve_dashboard_command("preflight")
    assert argv == ["./pmx", "preflight"]


def test_resolve_dashboard_allows_panic_dry_run():
    argv = resolve_dashboard_command("panic-dry-run")
    assert argv == ["./pmx", "panic", "--dry-run"]


def test_parse_dotenv_multiline_quoted():
    raw = 'KALSHI_PRIVATE_KEY="-----BEGIN KEY-----\nline2\n-----END KEY-----"\n'
    pairs = parse_dotenv(raw)
    assert "line2" in pairs["KALSHI_PRIVATE_KEY"]
