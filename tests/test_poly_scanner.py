from apps.bridge.poly_scanner import (
    _normalize_global_market,
    _normalize_us_market,
    _top_of_book,
    scan_global_poly,
    verify_us_slug,
)


def test_normalize_global_market():
    raw = {
        "slug": "will-x-happen",
        "marketId": "123",
        "title": "Will X happen?",
        "volume24h": 50000,
        "outcomes": [{"label": "Yes", "price": 0.6, "outcomeId": "tok1"}],
    }
    row = _normalize_global_market(raw)
    assert row["venue"] == "polymarket_global"
    assert row["slug"] == "will-x-happen"
    assert row["mid"] == 0.6
    assert row["us_tradable"] == "unknown"


def test_normalize_us_market():
    row = _normalize_us_market({"slug": "aec-nfl-test", "title": "Game"})
    assert row["venue"] == "polymarket_us"
    assert row["us_tradable"] is True
    assert "aec-nfl-test" in row["trade_hint"]


def test_top_of_book():
    book = {"bids": [{"price": 0.4}], "asks": [{"price": 0.42}, {"price": 0.43}]}
    top = _top_of_book(book)
    assert top["best_bid"] == 0.4
    assert top["best_ask"] == 0.42
    assert top["ask_depth"] == 2


def test_scan_global_poly_offline(monkeypatch):
    def fake_run(*args, **kwargs):
        return True, [{"slug": "fed-rate", "marketId": "1", "title": "Fed", "outcomes": []}], ""

    monkeypatch.setattr("apps.bridge.poly_scanner.run_pmxt_json", fake_run)
    out = scan_global_poly("fed", limit=5)
    assert out["ok"]
    assert out["count"] == 1
    assert out["venue"] == "polymarket_global"


def test_verify_us_slug_miss(monkeypatch):
    monkeypatch.setattr("apps.bridge.poly_scanner.run_pmxt_json", lambda *a, **k: (True, [], ""))
    out = verify_us_slug("missing-slug")
    assert not out["ok"]
    assert out["us_tradable"] is False
