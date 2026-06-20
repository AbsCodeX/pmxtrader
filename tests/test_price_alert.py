"""Tests for price movement detector (mock network)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from apps.bridge import price_alert as pa
from apps.bridge import watchlist as wl


def test_entry_key():
    key = pa.entry_key({"venue": "kalshi", "event_id": "KXTEST-1"})
    assert key == "kalshi:KXTEST-1"


def test_price_shift():
    assert abs(pa.price_shift(0.50, 0.55) - 0.10) < 0.001


def test_scan_detects_move(tmp_path: Path):
    watchlist_path = tmp_path / "watchlist.json"
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)

    snap_path = tmp_path / "briefs" / "alerts" / "price_snapshots.json"
    snap_path.parent.mkdir(parents=True)
    snap_path.write_text(
        json.dumps(
            {
                "entries": {
                    "kalshi:KXTEST-1": {"price": 0.50, "ts": "2026-01-01T00:00:00+00:00"},
                }
            }
        )
    )

    live = {"yes_ask": 0.56, "yes_bid": 0.54, "mid": 0.55}

    with patch.object(pa, "fetch_entry_live", return_value=(live, "")):
        with patch.object(pa, "snapshot_path", return_value=snap_path):
            with patch.object(pa, "save_snapshots") as mock_save:
                result = pa.scan_price_moves(
                    watchlist_path=watchlist_path,
                    root=tmp_path,
                    threshold=0.05,
                    update_snapshots=True,
                )

    assert result["alert_count"] == 1
    assert result["alerts"][0]["direction"] == "up"
    mock_save.assert_called_once()


def test_scan_no_alert_below_threshold(tmp_path: Path):
    watchlist_path = tmp_path / "watchlist.json"
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)

    snap_path = tmp_path / "snapshots.json"
    snap_path.write_text(
        json.dumps({"entries": {"kalshi:KXTEST-1": {"price": 0.50}}})
    )

    live = {"yes_ask": 0.51, "mid": 0.51}

    with patch.object(pa, "fetch_entry_live", return_value=(live, "")):
        with patch.object(pa, "snapshot_path", return_value=snap_path):
            with patch.object(pa, "save_snapshots"):
                result = pa.scan_price_moves(
                    watchlist_path=watchlist_path,
                    root=tmp_path,
                    threshold=0.05,
                )

    assert result["alert_count"] == 0
