"""Tests for trading agent capabilities and parse helpers."""

from apps.bridge.parse import parse_positions_json, parse_quote_fields, parse_rules_note
from apps.bridge.trading_agent import (
    PortfolioSnapshot,
    agent_snapshot_json,
    detect_mispricing,
    estimate_fair_value,
    score_confidence,
)


def test_parse_quote_fields():
    stdout = """
Event: KXTEST-1
Slug: my-slug
Best bid: 0.42
Best ask: 0.48
Mid: 0.45
Fill est: price=0.49
"""
    q = parse_quote_fields(stdout)
    assert q["best_bid"] == 0.42
    assert q["best_ask"] == 0.48
    assert q["event_id"] == "KXTEST-1"
    assert q["slug"] == "my-slug"


def test_parse_rules_note():
    stdout = "Resolution: CPI above 3% per BLS release\nBest ask: 0.5"
    rules = parse_rules_note(stdout)
    assert "CPI" in rules["text"]
    assert rules["manual_required"] is False


def test_parse_positions_json_array():
    raw = '[{"marketId": "M1", "size": 2, "unrealized_pnl": 1.5}]'
    rows = parse_positions_json(raw)
    assert len(rows) == 1
    assert rows[0]["marketId"] == "M1"


def test_estimate_fair_value():
    r = estimate_fair_value(0.60, 0.50)
    assert r.ok
    assert abs(float(r.data["edge_pct"]) - 0.10) < 0.001


def test_detect_mispricing_buy():
    r = detect_mispricing(0.62, 0.50, min_edge=0.06)
    assert r.data["mispriced_buy"] is True


def test_detect_mispricing_no_edge():
    r = detect_mispricing(0.52, 0.50, min_edge=0.06)
    assert r.data["mispriced_buy"] is False


def test_score_confidence_bands():
    low = score_confidence()
    high = score_confidence(book_liquid=True, rules_clear=True, cross_venue_agrees=True, edge_size=0.10)
    assert float(high.data["score"]) > float(low.data["score"])


def test_agent_snapshot_includes_credential_status(monkeypatch):
    monkeypatch.setattr(
        "apps.bridge.trading_agent.fetch_portfolio",
        lambda **kwargs: PortfolioSnapshot(
            kill_switch="OFF",
            kalshi_cash=None,
            poly_cash=None,
            kalshi_positions=[],
            poly_positions=[],
            open_count=0,
            unrealized_pnl=None,
            notional_exposure=None,
        ),
    )
    monkeypatch.setattr(
        "apps.bridge.trading_agent.sidecar_status",
        lambda root, probe_balances=False: {"healthy": True, "venues": {}},
    )
    monkeypatch.setattr(
        "apps.bridge.trading_agent.credential_status",
        lambda root: {"kalshi": {"configured": True}, "polymarket_us": {"configured": True}},
    )
    snap = agent_snapshot_json()
    assert "credential_status" in snap
    assert "sidecar_status" in snap
    assert any("pmxt/.env" in note for note in snap["hermes_notes"])
