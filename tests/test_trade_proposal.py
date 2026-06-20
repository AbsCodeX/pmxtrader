"""Tests for trade proposal generator."""

from apps.bridge.trade_proposal import (
    format_brief_markdown,
    generate_proposal,
    kelly_fraction_no,
    kelly_fraction_yes,
    pick_recommendation,
    size_from_kelly,
)


def test_kelly_fraction_yes():
    assert abs(kelly_fraction_yes(0.60, 0.50) - 0.20) < 0.001
    assert kelly_fraction_yes(0.50, 0.50) == 0.0
    assert kelly_fraction_yes(0.40, 0.50) == 0.0


def test_kelly_fraction_no():
    assert kelly_fraction_no(0.40, 0.45) > 0  # fair NO 0.60 vs no_ask 0.45
    assert kelly_fraction_no(0.60, 0.50) == 0.0


def test_pick_recommendation_yes():
    rec, edge, _ = pick_recommendation(0.62, ask=0.50, bid=0.48, min_edge=0.06)
    assert rec == "YES"
    assert abs(edge - 0.12) < 0.001


def test_pick_recommendation_pass():
    rec, _, reason = pick_recommendation(0.52, ask=0.50, bid=0.48, min_edge=0.06)
    assert rec == "PASS"
    assert "No trade" in reason


def test_size_from_kelly():
    size, cost = size_from_kelly(kelly_fraction=0.1, bankroll=1000, price_per_contract=0.5, max_contracts=10)
    assert size == 10
    assert cost == 5.0


def test_generate_proposal_yes(tmp_path):
    proposal = generate_proposal(
        fair_value_prob=0.62,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bid=0.48,
        bankroll=500,
        min_edge=0.06,
        root=tmp_path,
    )
    assert proposal.ok
    assert proposal.recommendation == "YES"
    assert proposal.suggested_size > 0
    assert proposal.edge_pct is not None
    assert proposal.commands
    assert "KXTEST-1" in proposal.commands[0]


def test_generate_proposal_pass(tmp_path):
    proposal = generate_proposal(
        fair_value_prob=0.51,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bid=0.49,
        bankroll=500,
        min_edge=0.06,
        root=tmp_path,
    )
    assert not proposal.ok
    assert proposal.recommendation == "PASS"
    assert not proposal.commands


def test_brief_markdown_contains_recommendation(tmp_path):
    proposal = generate_proposal(
        fair_value_prob=0.65,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bankroll=200,
        root=tmp_path,
    )
    md = format_brief_markdown(proposal)
    assert "**YES**" in md
    assert "Kelly" in md
