"""Unit tests for watchlist manager (no network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps.bridge import watchlist as wl


@pytest.fixture
def watchlist_path(tmp_path: Path) -> Path:
    return tmp_path / "watchlist.json"


def test_load_empty_watchlist(watchlist_path: Path):
    data = wl.load_watchlist(watchlist_path)
    assert data["version"] == 1
    assert data["markets"] == []
    assert data["filters"]["min_volume_24h"] is None


def test_add_and_list_kalshi(watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXWCGAME-26JUN19USAAUS", path=watchlist_path)
    data = wl.list_markets(path=watchlist_path)
    assert len(data["markets"]) == 1
    assert data["markets"][0]["venue"] == "kalshi"
    assert data["markets"][0]["event_id"] == "KXWCGAME-26JUN19USAAUS"


def test_add_kalshi_market_id(watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXBTC15M-26JUN201500-00", path=watchlist_path)
    entry = wl.list_markets(path=watchlist_path)["markets"][0]
    assert entry["market_id"] == "KXBTC15M-26JUN201500-00"
    assert entry["event_id"] == "KXBTC15M-26JUN201500"


def test_add_poly_us_slug(watchlist_path: Path):
    wl.add_market(venue="polymarket_us", identifier="fed-june-rate", path=watchlist_path)
    entry = wl.list_markets(path=watchlist_path)["markets"][0]
    assert entry["slug"] == "fed-june-rate"


def test_add_from_url_kalshi_event(watchlist_path: Path):
    wl.add_market(
        url="https://kalshi.com/events/KXWCGAME-26JUN19USAAUS",
        path=watchlist_path,
    )
    entry = wl.list_markets(path=watchlist_path)["markets"][0]
    assert entry["venue"] == "kalshi"
    assert entry["event_id"] == "KXWCGAME-26JUN19USAAUS"


def test_add_from_url_poly_us(watchlist_path: Path):
    wl.add_market(url="https://polymarket.us/market/my-slug", path=watchlist_path)
    entry = wl.list_markets(path=watchlist_path)["markets"][0]
    assert entry["venue"] == "polymarket_us"
    assert entry["slug"] == "my-slug"


def test_add_from_url_poly_global(watchlist_path: Path):
    wl.add_market(url="https://polymarket.com/event/will-x-happen", path=watchlist_path)
    entry = wl.list_markets(path=watchlist_path)["markets"][0]
    assert entry["venue"] == "polymarket_global"
    assert entry["slug"] == "will-x-happen"


def test_add_duplicate_raises(watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)
    with pytest.raises(ValueError, match="already on watchlist"):
        wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)


def test_remove_by_index(watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)
    wl.add_market(venue="kalshi", identifier="KXTEST-2", path=watchlist_path)
    data = wl.remove_market("1", path=watchlist_path)
    assert len(data["markets"]) == 1
    assert data["markets"][0]["event_id"] == "KXTEST-2"


def test_remove_by_id(watchlist_path: Path):
    wl.add_market(venue="polymarket_us", identifier="slug-a", path=watchlist_path)
    data = wl.remove_market("slug-a", path=watchlist_path)
    assert data["markets"] == []


def test_set_filters(watchlist_path: Path):
    wl.set_filters(min_volume_24h=1000.0, min_liquidity=500.0, path=watchlist_path)
    filters = wl.list_markets(path=watchlist_path)["filters"]
    assert filters["min_volume_24h"] == 1000.0
    assert filters["min_liquidity"] == 500.0
    wl.set_filters(min_volume_24h=None, path=watchlist_path)
    assert wl.list_markets(path=watchlist_path)["filters"]["min_volume_24h"] is None


def test_save_persists_json(watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)
    assert watchlist_path.is_file()
    raw = json.loads(watchlist_path.read_text())
    assert raw["markets"][0]["event_id"] == "KXTEST-1"


def test_infer_from_url_bad_host():
    with pytest.raises(ValueError, match="Unsupported URL"):
        wl.infer_from_url("https://example.com/foo")


def test_evaluate_filters_pass_and_fail():
    live = {"volume_24h": 2000.0, "liquidity": 800.0}
    filters = {"min_volume_24h": 1000.0, "min_liquidity": 500.0}
    passes, results, reason = wl._evaluate_filters(live, filters)
    assert passes is True
    assert results["min_volume_24h"]["pass"] is True
    assert "passes" in reason

    live_fail = {"volume_24h": 100.0, "liquidity": 800.0}
    passes, _, reason = wl._evaluate_filters(live_fail, filters)
    assert passes is False
    assert "volume" in reason


def test_evaluate_filters_missing_data():
    live = {"volume_24h": None, "liquidity": None}
    filters = {"min_volume_24h": 100.0, "min_liquidity": 50.0}
    passes, results, _ = wl._evaluate_filters(live, filters)
    assert passes is None
    assert results["min_volume_24h"]["pass"] is None


def test_scan_watchlist_offline(monkeypatch, watchlist_path: Path):
    wl.add_market(venue="kalshi", identifier="KXTEST-1", path=watchlist_path)
    wl.add_market(venue="polymarket_us", identifier="us-slug", path=watchlist_path)
    wl.set_filters(min_volume_24h=100.0, path=watchlist_path)

    def fake_kalshi(entry):
        return {"title": "Test", "volume_24h": 500.0, "liquidity": 200.0}, ""

    def fake_poly_us(entry):
        return {"title": "US", "volume_24h": 50.0, "liquidity": None}, ""

    monkeypatch.setattr(wl, "_live_kalshi", fake_kalshi)
    monkeypatch.setattr(wl, "_live_poly_us", fake_poly_us)

    report = wl.scan_watchlist(path=watchlist_path)
    assert report["count"] == 2
    assert report["pass_count"] == 1
    assert report["fail_count"] == 1
    by_venue = {r["entry"]["venue"]: r for r in report["entries"]}
    assert by_venue["kalshi"]["passes_filters"] is True
    assert by_venue["polymarket_us"]["passes_filters"] is False


def test_scan_kalshi_live_mock(monkeypatch):
    payload = {
        "market": {
            "ticker": "KXTEST-1-00",
            "event_ticker": "KXTEST-1",
            "title": "Test market",
            "volume_24h_fp": "1234.5",
            "open_interest_fp": "567.8",
            "yes_bid_dollars": "0.40",
            "yes_ask_dollars": "0.42",
            "status": "active",
        }
    }

    def fake_fetch(path, *, timeout=30):
        return payload, ""

    monkeypatch.setattr(wl, "_fetch_kalshi_json", fake_fetch)
    live, err = wl._live_kalshi({"venue": "kalshi", "market_id": "KXTEST-1-00"})
    assert not err
    assert live["volume_24h"] == 1234.5
    assert live["liquidity"] == 567.8
    assert live["mid"] == 0.41
