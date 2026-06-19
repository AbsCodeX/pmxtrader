from apps.bridge.commands import classify_command, is_palette_allowed, resolve_dashboard_command
from apps.bridge.parse import parse_kill_switch, parse_status


def test_parse_engaged_kill_switch():
    stdout = "ENGAGED — halftime (/Users/me/pmxtrader/KILL_SWITCH)\nKalshi: available: 42.00"
    assert parse_kill_switch(stdout) == "ON"
    assert parse_status(stdout).kill_switch == "ON"


def test_parse_off_kill_switch():
    stdout = "OFF (/Users/me/pmxtrader/KILL_SWITCH)\nKalshi:"
    assert parse_kill_switch(stdout) == "OFF"


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
    assert is_palette_allowed("poly markets soccer")
    assert not is_palette_allowed("panic")
    assert not is_palette_allowed("scout grok")


def test_resolve_dashboard_blocks_trade():
    assert resolve_dashboard_command("trade MARKET USA 1") is None
    assert resolve_dashboard_command("poly cancel-all") is None


def test_resolve_dashboard_allows_status():
    argv = resolve_dashboard_command("status")
    assert argv == ["./pmx", "status"]
