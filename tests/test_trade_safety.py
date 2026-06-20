"""Trading safety guards (Batch I)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps.bridge.trade_safety import (
    check_live_trade_allowed,
    check_trade_amount,
    format_dry_run_order,
    is_read_only_env,
    max_trade_contracts,
)


def test_max_trade_contracts_unset(monkeypatch):
    monkeypatch.delenv("PMX_MAX_TRADE_CONTRACTS", raising=False)
    assert max_trade_contracts() is None


def test_max_trade_contracts_from_env(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "10")
    assert max_trade_contracts() == 10.0


def test_check_trade_amount_over_cap(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "5")
    r = check_trade_amount(10)
    assert not r.ok
    assert "exceeds" in r.error


def test_check_trade_amount_valid(monkeypatch):
    monkeypatch.setenv("PMX_MAX_TRADE_CONTRACTS", "5")
    assert check_trade_amount(3).ok


def test_read_only_env(monkeypatch):
    monkeypatch.setenv("PMX_READ_ONLY", "1")
    assert is_read_only_env()
    assert not check_live_trade_allowed(kill_switch_engaged=False).ok


def test_kill_switch_blocks_trade():
    r = check_live_trade_allowed(kill_switch_engaged=True)
    assert not r.ok
    assert "Kill switch" in r.error


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


def test_kalshi_trade_script_has_no_order_retry():
    text = Path("scripts/kalshi-quickstart.sh").read_text(encoding="utf-8")
    idx = text.index("  trade)")
    block = text[idx : idx + 1400]
    assert "order:create" in block
    assert "allow_retry" not in block
    assert "while " not in block


def test_poly_place_order_single_submit():
    text = Path("scripts/polymarket-us-quickstart.sh").read_text(encoding="utf-8")
    fn = text.split("place_order()", 1)[1].split("\n}\n", 1)[0]
    assert fn.count("order:create") == 2  # limit + market branches
    assert "retry" not in fn.lower()


def test_emergency_exit_retries_get_not_post():
    text = Path("scripts/kalshi-emergency-exit.py").read_text(encoding="utf-8")
    assert "allow_retry=True" in text
    assert 'api_request("GET"' in text or "GET" in text
    # POST closes/cancels should not pass allow_retry=True
    assert "close_positions" in text
