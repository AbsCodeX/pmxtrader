"""Trading safety guards and audit log tests."""

from __future__ import annotations

import json
from pathlib import Path


from apps.bridge.trade_audit import append_trade_log, parse_order_id
from apps.bridge.trade_safety import (
    check_live_trade_allowed,
    check_sidecar_health,
    check_trade_amount,
    confirm_trade_allowed,
    format_dry_run_order,
    format_panic_scope,
    format_preflight_report,
    has_kalshi_keys,
    has_poly_us_keys,
    is_live_mode,
    is_read_only_env,
    max_trade_contracts,
    panic_venues,
    preflight_enabled,
    read_sidecar_port,
    run_preflight,
    safety_snapshot,
    trade_confirm_required,
)


def test_max_trade_contracts_default(monkeypatch):
    monkeypatch.delenv("PMX_MAX_TRADE_CONTRACTS", raising=False)
    assert max_trade_contracts() == 10.0


def test_max_trade_contracts_from_env(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "5")
    assert max_trade_contracts() == 5.0


def test_check_trade_amount_over_cap(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "5")
    r = check_trade_amount(10)
    assert not r.ok
    assert "exceeds" in r.error


def test_check_trade_amount_valid(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "5")
    assert check_trade_amount(3).ok


def test_read_only_default(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("PMX_READ_ONLY", raising=False)
    assert is_read_only_env(root=tmp_path)
    assert not check_live_trade_allowed(kill_switch_engaged=False, root=tmp_path).ok


def test_live_mode_file_clears_read_only(tmp_path: Path):
    (tmp_path / ".pmx-live").touch()
    assert is_live_mode(tmp_path)
    assert not is_read_only_env(root=tmp_path)
    assert check_live_trade_allowed(kill_switch_engaged=False, root=tmp_path).ok


def test_kill_switch_blocks_trade(tmp_path: Path):
    r = check_live_trade_allowed(kill_switch_engaged=True, root=tmp_path)
    assert not r.ok
    assert "Kill switch" in r.error


def test_safety_snapshot(tmp_path: Path):
    (tmp_path / "KILL_SWITCH").write_text("test halt\n", encoding="utf-8")
    snap = safety_snapshot(tmp_path)
    assert snap.kill_switch == "ON"
    assert snap.kill_switch_reason == "test halt"
    assert snap.read_only is True
    assert snap.max_trade_contracts == 10.0


def test_trade_confirm_required_defaults():
    assert trade_confirm_required()
    assert trade_confirm_required(assume_yes=True) is False


def test_trade_confirm_skipped_when_env_zero(monkeypatch):
    monkeypatch.setenv("PMX_TRADE_CONFIRM", "0")
    assert not trade_confirm_required()


def test_confirm_trade_allowed():
    assert confirm_trade_allowed("YES")
    assert confirm_trade_allowed("y")
    assert not confirm_trade_allowed("no")
    assert not confirm_trade_allowed("")


def test_format_dry_run_order():
    msg = format_dry_run_order(
        venue="Kalshi",
        action="buy",
        market="MKT",
        outcome="OUT",
        amount=2,
    )
    assert "[dry-run]" in msg
    assert "buy" in msg


def test_parse_order_id_from_json():
    stdout = json.dumps([{"id": "ord-123", "marketId": "MKT"}])
    assert parse_order_id(stdout) == "ord-123"


def test_append_trade_log(tmp_path: Path):
    log_path = tmp_path / "briefs" / "alerts" / "trades.jsonl"
    entry = append_trade_log(
        tmp_path,
        venue="kalshi",
        command="buy",
        market="MKT",
        outcome="OUT",
        size=1,
        stdout=json.dumps([{"id": "abc"}]),
    )
    assert entry["order_id"] == "abc"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["venue"] == "kalshi"
    assert row["dry_run"] is False
    assert "timestamp" in row


def test_append_trade_log_skips_dry_run(tmp_path: Path):
    append_trade_log(
        tmp_path,
        venue="kalshi",
        command="buy",
        market="MKT",
        outcome="OUT",
        size=1,
        dry_run=True,
    )
    assert not (tmp_path / "briefs" / "alerts" / "trades.jsonl").exists()


def test_kalshi_trade_script_has_no_order_retry():
    text = Path("scripts/kalshi-quickstart.sh").read_text(encoding="utf-8")
    idx = text.index("  trade)")
    block = text[idx : idx + 2000]
    assert "order:create" in block
    assert "trade_safety_confirm_live" in block
    assert "trade_safety_audit_log" in block
    assert "allow_retry" not in block


def test_poly_place_order_confirm_and_audit():
    text = Path("scripts/polymarket-us-quickstart.sh").read_text(encoding="utf-8")
    fn = text.split("place_order()", 1)[1].split("\n}\n", 1)[0]
    assert fn.count("order:create") == 2
    assert "trade_safety_confirm_live" in fn
    assert "trade_safety_audit_log" in fn


def test_emergency_exit_retries_get_not_post():
    text = Path("scripts/kalshi-emergency-exit.py").read_text(encoding="utf-8")
    assert "allow_retry=True" in text
    assert "close_positions" in text


def test_poly_emergency_exit_exists():
    path = Path("scripts/polymarket-us-emergency-exit.py")
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "--dry-run" in text
    assert "close_positions" in text


def test_kill_switch_panic_includes_poly():
    text = Path("scripts/kill-switch.sh").read_text(encoding="utf-8")
    assert "polymarket-us-emergency-exit.py" in text


def test_pmxt_env_default_read_only():
    text = Path("scripts/pmxt-env.sh").read_text(encoding="utf-8")
    assert 'PMX_READ_ONLY="${PMX_READ_ONLY:-1}"' in text
    assert 'PMX_MAX_TRADE_CONTRACTS="${PMX_MAX_TRADE_CONTRACTS:-10}"' in text


def test_preflight_enabled_default(monkeypatch):
    monkeypatch.delenv("PMX_PREFLIGHT", raising=False)
    assert preflight_enabled()


def test_preflight_disabled(monkeypatch):
    monkeypatch.setenv("PMX_PREFLIGHT", "0")
    assert not preflight_enabled()


def test_has_kalshi_keys(tmp_path: Path):
    env = tmp_path / "pmxt" / ".env"
    env.parent.mkdir()
    env.write_text("KALSHI_API_KEY=k\nKALSHI_PRIVATE_KEY=p\n", encoding="utf-8")
    assert has_kalshi_keys(tmp_path)
    assert not has_poly_us_keys(tmp_path)


def test_has_poly_us_keys(tmp_path: Path):
    env = tmp_path / "pmxt" / ".env"
    env.parent.mkdir()
    env.write_text(
        "POLYMARKET_US_KEY_ID=id\nPOLYMARKET_US_SECRET_KEY=sec\n",
        encoding="utf-8",
    )
    assert has_poly_us_keys(tmp_path)
    assert not has_kalshi_keys(tmp_path)


def test_panic_venues_from_keys(tmp_path: Path):
    env = tmp_path / "pmxt" / ".env"
    env.parent.mkdir()
    env.write_text(
        "KALSHI_API_KEY=k\nKALSHI_PRIVATE_KEY=p\n"
        "POLYMARKET_US_KEY_ID=id\nPOLYMARKET_US_SECRET_KEY=sec\n",
        encoding="utf-8",
    )
    assert panic_venues(tmp_path) == ["Kalshi", "Polymarket US"]
    scope = format_panic_scope(tmp_path)
    assert "Kalshi: included" in scope
    assert "Polymarket US: included" in scope


def test_panic_venues_none_without_keys(tmp_path: Path):
    assert panic_venues(tmp_path) == []
    assert "none" in format_panic_scope(tmp_path).lower()


def test_read_sidecar_port_default():
    assert read_sidecar_port() >= 3847


def test_check_sidecar_health_unreachable():
    r = check_sidecar_health(port=59999, timeout=0.2)
    assert not r.ok
    assert "not reachable" in r.error.lower() or "timed out" in r.error.lower()


def test_run_preflight_no_go_read_only(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PMX_READ_ONLY", "1")
    report = run_preflight(tmp_path)
    assert not report.go
    assert report.verdict == "NO-GO"


def test_run_preflight_go_when_live(tmp_path: Path, monkeypatch):
    (tmp_path / ".pmx-live").touch()
    env = tmp_path / "pmxt" / ".env"
    env.parent.mkdir()
    env.write_text("KALSHI_API_KEY=k\nKALSHI_PRIVATE_KEY=p\n", encoding="utf-8")
    monkeypatch.setenv("PMX_READ_ONLY", "0")

    def fake_sidecar(**_kwargs):
        from apps.bridge.trade_safety import TradeGuardResult

        return TradeGuardResult(True, "Sidecar OK")

    monkeypatch.setattr("apps.bridge.trade_safety.check_sidecar_health", fake_sidecar)
    report = run_preflight(tmp_path)
    assert report.go
    text = format_preflight_report(report, root=tmp_path)
    assert "GO" in text
    assert "Kalshi: included" in text


def test_run_preflight_blocked_by_kill_switch(tmp_path: Path, monkeypatch):
    (tmp_path / ".pmx-live").touch()
    (tmp_path / "KILL_SWITCH").write_text("halt\n", encoding="utf-8")
    env = tmp_path / "pmxt" / ".env"
    env.parent.mkdir()
    env.write_text("KALSHI_API_KEY=k\nKALSHI_PRIVATE_KEY=p\n", encoding="utf-8")
    monkeypatch.setenv("PMX_READ_ONLY", "0")

    def fake_sidecar(**_kwargs):
        from apps.bridge.trade_safety import TradeGuardResult

        return TradeGuardResult(True, "Sidecar OK")

    monkeypatch.setattr("apps.bridge.trade_safety.check_sidecar_health", fake_sidecar)
    report = run_preflight(tmp_path)
    assert not report.go


def test_pmx_sh_has_preflight_and_preview():
    text = Path("scripts/pmx.sh").read_text(encoding="utf-8")
    assert "preflight|check" in text
    assert "preview|dry-run" in text
    assert "panic status" in text or 'panic", "--dry-run"' in text


def test_trade_scripts_call_sidecar_preflight():
    kalshi = Path("scripts/kalshi-quickstart.sh").read_text(encoding="utf-8")
    poly = Path("scripts/polymarket-us-quickstart.sh").read_text(encoding="utf-8")
    assert "trade_safety_preflight_trade" in kalshi
    assert kalshi.count("trade_safety_preflight_trade") >= 1
    assert poly.count("trade_safety_preflight_trade") == 3


def test_trade_safety_dry_run_skips_read_only():
    text = Path("scripts/trade-safety-lib.sh").read_text(encoding="utf-8")
    assert "trade_safety_is_dry_run" in text
    assert "trade_safety_sidecar_ready" in text
