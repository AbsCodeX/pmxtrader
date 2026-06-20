"""Tests for risk & sizing engine."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps.bridge import risk_engine as re


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path


def test_compute_edge_buy():
    assert abs(re.compute_edge(0.62, ask=0.50) - 0.12) < 0.001


def test_compute_edge_no():
    assert abs(re.compute_edge(0.40, bid=0.35, side="no") - (-0.05)) < 0.001


def test_kelly_fraction_yes():
    assert abs(re.kelly_fraction_yes(0.60, 0.50) - 0.20) < 0.001


def test_size_from_kelly():
    size, cost = re.size_from_kelly(
        kelly_fraction=0.1, bankroll=1000, price_per_contract=0.5, max_contracts=10
    )
    assert size == 10
    assert cost == 5.0


def test_daily_loss_unset_blocked(root: Path):
    os.environ.pop("PMX_MAX_DAILY_LOSS", None)
    status = re.daily_loss_status(root)
    assert status["blocked"] is True
    assert "PMX_MAX_DAILY_LOSS not set" in status["reason"]


def test_daily_loss_with_limit(root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PMX_MAX_DAILY_LOSS", "100")
    status = re.daily_loss_status(root)
    assert status["ok"] is True
    assert status["limit"] == 100.0


def test_record_trade_pnl(root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PMX_MAX_DAILY_LOSS", "100")
    ledger = re.record_trade_pnl(-25.0, root=root, note="test loss")
    assert ledger["realized_pnl"] == -25.0
    assert len(ledger["trades"]) == 1
    path = re.daily_ledger_path(root)
    assert path.is_file()
    saved = json.loads(path.read_text())
    assert saved["realized_pnl"] == -25.0


def test_check_risk_blocks_daily_loss_unset(root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("PMX_MAX_DAILY_LOSS", raising=False)
    report = re.check_risk(size=5, recommendation="YES", venue="kalshi", root=root)
    daily = [c for c in report.checks if c.name == "daily_loss"]
    assert daily
    assert not daily[0].ok
    assert not report.ok


def test_check_risk_passes_with_daily_limit(root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PMX_MAX_DAILY_LOSS", "500")
    report = re.check_risk(
        size=5,
        recommendation="YES",
        venue="kalshi",
        root=root,
        estimated_cost=2.5,
        max_risk_dollars=10.0,
        bankroll=100.0,
        fair=0.62,
        ask=0.50,
    )
    assert report.ok
