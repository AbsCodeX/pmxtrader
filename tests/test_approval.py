"""Tests for approval workflow (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from apps.bridge.approval import (
    build_approval_packet,
    format_approval_summary,
    proposal_from_dict,
    wait_for_confirmation,
    write_approval_packet,
)
from apps.bridge.trade_proposal import generate_proposal


def test_format_approval_summary(tmp_path: Path):
    proposal = generate_proposal(
        fair_value_prob=0.65,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bankroll=200,
        root=tmp_path,
    )
    summary = format_approval_summary(proposal)
    assert "Trade approval packet" in summary
    assert "KXTEST-1" in summary
    assert "YES" in summary


def test_wait_for_confirmation_yes():
    assert wait_for_confirmation(confirm="YES", interactive=False) is True
    assert wait_for_confirmation(confirm="no", interactive=False) is False


def test_proposal_from_dict_roundtrip(tmp_path: Path):
    proposal = generate_proposal(
        fair_value_prob=0.62,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bankroll=500,
        root=tmp_path,
    )
    from apps.bridge.trade_proposal import proposal_to_dict

    data = proposal_to_dict(proposal)
    restored = proposal_from_dict(data)
    assert restored.market_ref == proposal.market_ref
    assert restored.recommendation == proposal.recommendation


def test_build_and_write_packet(tmp_path: Path):
    proposal = generate_proposal(
        fair_value_prob=0.65,
        venue="kalshi",
        market_ref="KXTEST-1",
        ask=0.50,
        bankroll=200,
        root=tmp_path,
    )
    packet = build_approval_packet(proposal, confirmed=True, source="test")
    assert packet["confirmed"] is True
    path = write_approval_packet(packet, root=tmp_path)
    assert path.is_file()
    saved = json.loads(path.read_text())
    assert saved["market_ref"] == "KXTEST-1"
