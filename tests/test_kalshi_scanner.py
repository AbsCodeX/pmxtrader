from datetime import UTC, datetime, timedelta

from apps.bridge import kalshi_scanner as ks


def test_normalize_kalshi_market():
    raw = {
        "ticker": "KXBTC15M-26JUN201500-00",
        "event_ticker": "KXBTC15M-26JUN201500",
        "title": "BTC price up in next 15 mins?",
        "close_time": "2026-06-20T19:00:00Z",
        "yes_bid_dollars": "0.64",
        "yes_ask_dollars": "0.66",
        "no_bid_dollars": "0.34",
        "no_ask_dollars": "0.36",
        "status": "active",
    }
    row = ks.normalize_kalshi_market(raw, horizon="15m", series_ticker="KXBTC15M")
    assert row["venue"] == "kalshi"
    assert row["horizon"] == "15m"
    assert row["mid"] == 0.65
    assert "./pmx quote KXBTC15M-26JUN201500 YES 1" in (row["trade_hint"] or "")


def test_scan_kalshi_btc_offline(monkeypatch):
    future = (datetime.now(tz=UTC) + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fake_fetch(series_ticker: str, *, limit: int = 20, status: str = "open", timeout: int = 30):
        if series_ticker == "KXBTC15M":
            return [
                {
                    "ticker": "KXBTC15M-TEST-00",
                    "event_ticker": "KXBTC15M-TEST",
                    "title": "BTC up 15m",
                    "close_time": future,
                    "yes_bid_dollars": "0.50",
                    "yes_ask_dollars": "0.52",
                }
            ], ""
        if series_ticker == "KXBTCD":
            return [
                {
                    "ticker": "KXBTCD-TEST-T70000",
                    "event_ticker": "KXBTCD-TEST",
                    "title": "BTC above strike",
                    "close_time": (datetime.now(tz=UTC) + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "yes_bid_dollars": "0.40",
                    "yes_ask_dollars": "0.42",
                }
            ], ""
        return [], "missing"

    monkeypatch.setattr(ks, "fetch_series_markets", fake_fetch)
    out = ks.scan_kalshi_btc(horizon="all", limit=5)
    assert out["ok"]
    assert out["count"] == 2
    horizons = {m["horizon"] for m in out["markets"]}
    assert horizons == {"15m", "1h"}


def test_scan_kalshi_btc_skips_past_close(monkeypatch):
    past = (datetime.now(tz=UTC) - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def fake_fetch(series_ticker: str, **kwargs):
        return [
            {
                "ticker": "KXBTC15M-OLD",
                "event_ticker": "KXBTC15M-OLD",
                "title": "expired",
                "close_time": past,
            }
        ], ""

    monkeypatch.setattr(ks, "fetch_series_markets", fake_fetch)
    out = ks.scan_kalshi_btc(horizon="15m", limit=5)
    assert not out["ok"]
    assert out["count"] == 0


def test_scan_unknown_horizon():
    out = ks.scan_kalshi_btc(horizon="2h", limit=5)
    assert not out["ok"]
    assert "Unknown horizon" in out["error"]
