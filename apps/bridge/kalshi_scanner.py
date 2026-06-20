"""
Kalshi short-term BTC scanner — 15-minute and hourly up/down markets.

Uses Kalshi's public read API (no credentials) for fast catalog scans.
Optional ``--book`` enriches via pmxt sidecar orderbook.

CLI:
    ./pmx scan kalshi-btc [--horizon 15m|1h|all] [--limit N] [--book]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any

from apps.bridge.poly_scanner import _top_of_book, run_pmxt_json

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"

BTC_SERIES: dict[str, dict[str, str]] = {
    "15m": {
        "ticker": "KXBTC15M",
        "label": "Bitcoin 15-minute up/down",
        "frequency": "fifteen_min",
    },
    "1h": {
        "ticker": "KXBTCD",
        "label": "Bitcoin hourly above/below",
        "frequency": "hourly",
    },
}


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _dollar(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_series_markets(
    series_ticker: str,
    *,
    limit: int = 20,
    status: str = "open",
    timeout: int = 30,
) -> tuple[list[dict[str, Any]], str]:
    """Fetch open markets for a Kalshi series via public REST API."""
    rows: list[dict[str, Any]] = []
    cursor: str | None = None
    err = ""

    while len(rows) < limit:
        page_limit = min(200, limit - len(rows))
        params: dict[str, str] = {
            "series_ticker": series_ticker,
            "status": status,
            "limit": str(page_limit),
        }
        if cursor:
            params["cursor"] = cursor

        url = f"{KALSHI_API}/markets?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            return rows, f"HTTP {exc.code}: {body[:200]}"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return rows, str(exc)

        batch = payload.get("markets") or []
        if not isinstance(batch, list):
            break
        rows.extend(m for m in batch if isinstance(m, dict))
        cursor = payload.get("cursor") or ""
        if not cursor or not batch:
            break

    return rows[:limit], err


def normalize_kalshi_market(
    raw: dict[str, Any],
    *,
    horizon: str,
    series_ticker: str,
) -> dict[str, Any]:
    event_ticker = raw.get("event_ticker") or ""
    market_ticker = raw.get("ticker") or raw.get("market_ticker") or ""
    yes_bid = _dollar(raw.get("yes_bid_dollars"))
    yes_ask = _dollar(raw.get("yes_ask_dollars"))
    no_bid = _dollar(raw.get("no_bid_dollars"))
    no_ask = _dollar(raw.get("no_ask_dollars"))
    mid = None
    if yes_bid is not None and yes_ask is not None:
        mid = round((yes_bid + yes_ask) / 2, 4)

    return {
        "venue": "kalshi",
        "horizon": horizon,
        "series": series_ticker,
        "market_id": market_ticker,
        "event_id": event_ticker,
        "title": raw.get("title"),
        "status": raw.get("status"),
        "open_time": raw.get("open_time"),
        "close_time": raw.get("close_time"),
        "expected_expiration": raw.get("expected_expiration_time") or raw.get("occurrence_datetime"),
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "no_bid": no_bid,
        "no_ask": no_ask,
        "mid": mid,
        "volume_24h": _dollar(raw.get("volume_24h_fp") or raw.get("volume_24h")),
        "open_interest": _dollar(raw.get("open_interest_fp") or raw.get("open_interest")),
        "url": f"https://kalshi.com/markets/{series_ticker.lower()}",
        "trade_hint": f"./pmx quote {event_ticker} YES 1" if event_ticker else None,
    }


def scan_kalshi_btc(
    *,
    horizon: str = "all",
    limit: int = 20,
    with_book: bool = False,
    status: str = "open",
) -> dict[str, Any]:
    """Scan Kalshi BTC 15m and/or hourly markets, soonest close first."""
    horizons = ["15m", "1h"] if horizon == "all" else [horizon]
    unknown = [h for h in horizons if h not in BTC_SERIES]
    if unknown:
        return {
            "ok": False,
            "scanner": "kalshi-btc",
            "error": f"Unknown horizon {unknown[0]!r}; use 15m, 1h, or all",
            "markets": [],
            "count": 0,
        }

    per_series = max(limit, 5)
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    now = datetime.now(tz=UTC)

    for hz in horizons:
        meta = BTC_SERIES[hz]
        series_ticker = meta["ticker"]
        raw_markets, err = fetch_series_markets(series_ticker, limit=per_series, status=status)
        if err:
            errors.append(f"{series_ticker}: {err}")
        for raw in raw_markets:
            close_dt = _parse_ts(raw.get("close_time"))
            if close_dt and close_dt < now:
                continue
            row = normalize_kalshi_market(raw, horizon=hz, series_ticker=series_ticker)
            row["series_label"] = meta["label"]
            if with_book and row["market_id"]:
                _, book, book_err = run_pmxt_json(
                    "kalshi",
                    "orderbook",
                    str(row["market_id"]),
                    timeout=45,
                )
                if book_err and not book:
                    row["book_error"] = book_err
                else:
                    row["book"] = _top_of_book(book)
            rows.append(row)

    rows.sort(key=lambda r: r.get("close_time") or "")
    rows = rows[:limit]

    return {
        "ok": bool(rows),
        "scanner": "kalshi-btc",
        "venue": "kalshi",
        "horizon": horizon,
        "series": [BTC_SERIES[h]["ticker"] for h in horizons],
        "count": len(rows),
        "markets": rows,
        "note": (
            "Short-term BTC on Kalshi (CF Benchmarks BRTI settlement). "
            "Use ./pmx quote EVENT YES|NO 1 before trade; confirm kill switch off."
        ),
        "error": "; ".join(errors) if errors and not rows else "",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kalshi short-term BTC scanner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_btc = sub.add_parser("kalshi-btc", help="Scan BTC 15m and hourly Kalshi markets")
    p_btc.add_argument(
        "--horizon",
        default="all",
        choices=("15m", "1h", "all"),
        help="Market cadence (default: all)",
    )
    p_btc.add_argument("--limit", type=int, default=20)
    p_btc.add_argument("--book", action="store_true", help="Attach pmxt orderbook top-of-book")
    p_btc.add_argument(
        "--status",
        default="open",
        choices=("open", "closed", "unopened"),
        help="Kalshi market status filter",
    )

    args = parser.parse_args(argv)
    if args.cmd == "kalshi-btc":
        out = scan_kalshi_btc(
            horizon=args.horizon,
            limit=args.limit,
            with_book=args.book,
            status=args.status,
        )
    else:
        out = {"ok": False, "error": f"Unknown command {args.cmd}", "markets": [], "count": 0}

    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
