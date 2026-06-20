"""
Polymarket scanners — global Gamma/CLOB (research) + US retail search.

Global discovery uses pmxt ``polymarket`` (gamma-api + CLOB orderbooks).
US discovery uses paginated ``polymarket_us`` search (see pmxt core fix).

CLI:
    ./pmx scan poly-global QUERY [--limit N] [--book]
    ./pmx scan poly-us QUERY [--limit N]
    ./pmx scan verify-us SLUG
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from apps.bridge.dashboard_security import minimal_subprocess_env
from apps.bridge.pmxt_cli import pmxt_argv

ROOT = Path(__file__).resolve().parents[2]


def run_pmxt_json(*args: str, timeout: int = 120) -> tuple[bool, Any, str]:
    argv = pmxt_argv([*args, "--local", "--json"])
    try:
        proc = subprocess.run(
            argv,
            cwd=ROOT,
            env=minimal_subprocess_env(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, None, "Timed out"
    except OSError as exc:
        return False, None, str(exc)

    raw = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    if not raw:
        return proc.returncode == 0, None, err or "No output"
    try:
        return proc.returncode == 0, json.loads(raw), err
    except json.JSONDecodeError:
        return proc.returncode == 0, raw, err


def _top_of_book(book: Any) -> dict[str, Any]:
    if not isinstance(book, dict):
        return {}
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    best_bid = bids[0] if bids else None
    best_ask = asks[0] if asks else None
    return {
        "best_bid": best_bid.get("price") if isinstance(best_bid, dict) else None,
        "best_ask": best_ask.get("price") if isinstance(best_ask, dict) else None,
        "bid_depth": len(bids),
        "ask_depth": len(asks),
    }


def _normalize_global_market(raw: dict[str, Any]) -> dict[str, Any]:
    outcomes = raw.get("outcomes") or []
    prices = [o.get("price") for o in outcomes if isinstance(o, dict) and o.get("price") is not None]
    return {
        "venue": "polymarket_global",
        "slug": raw.get("slug") or raw.get("marketId"),
        "market_id": raw.get("marketId") or raw.get("id"),
        "event_id": raw.get("eventId"),
        "title": raw.get("title"),
        "volume24h": raw.get("volume24h") or raw.get("volume"),
        "liquidity": raw.get("liquidity"),
        "outcomes": [
            {
                "label": o.get("label"),
                "price": o.get("price"),
                "outcome_id": o.get("outcomeId"),
            }
            for o in outcomes
            if isinstance(o, dict)
        ],
        "mid": sum(prices) / len(prices) if prices else None,
        "us_tradable": "unknown",
    }


def _normalize_us_market(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "venue": "polymarket_us",
        "slug": raw.get("slug") or raw.get("marketId"),
        "market_id": raw.get("marketId") or raw.get("id"),
        "title": raw.get("title"),
        "volume24h": raw.get("volume24h") or raw.get("volume"),
        "us_tradable": True,
        "trade_hint": f"./pmx poly quote {raw.get('slug') or raw.get('marketId')} long",
    }


def scan_global_poly(
    query: str,
    *,
    limit: int = 20,
    with_book: bool = False,
    sort: str = "volume",
) -> dict[str, Any]:
    """Gamma-backed search on polymarket.com (research — not US execution)."""
    ok, data, err = run_pmxt_json(
        "polymarket",
        "markets",
        "--query",
        query,
        "--limit",
        str(limit),
        "--sort",
        sort,
    )
    markets_raw = data if isinstance(data, list) else []
    rows: list[dict[str, Any]] = []
    for raw in markets_raw[:limit]:
        if not isinstance(raw, dict):
            continue
        row = _normalize_global_market(raw)
        if with_book:
            outcomes = raw.get("outcomes") or []
            if outcomes and isinstance(outcomes[0], dict):
                oid = outcomes[0].get("outcomeId")
                if oid:
                    _, book, _ = run_pmxt_json("polymarket", "orderbook", str(oid), timeout=45)
                    row["book"] = _top_of_book(book)
        rows.append(row)

    return {
        "ok": ok and bool(rows),
        "scanner": "poly-global",
        "venue": "polymarket_global",
        "query": query,
        "count": len(rows),
        "markets": rows,
        "command": f"pmxt polymarket markets --query {query!r} --limit {limit} --sort {sort}",
        "note": (
            "Global Polymarket (Gamma/CLOB) — research only. "
            "Confirm US retail slug: ./pmx scan verify-us SLUG then ./pmx poly quote SLUG long"
        ),
        "error": err if not rows else "",
    }


def scan_poly_us(query: str, *, limit: int = 20) -> dict[str, Any]:
    """Paginated search on polymarket.us (tradable via ./pmx poly)."""
    ok, data, err = run_pmxt_json(
        "polymarket_us",
        "markets",
        "--query",
        query,
        "--limit",
        str(limit),
    )
    markets_raw = data if isinstance(data, list) else []
    rows = [_normalize_us_market(m) for m in markets_raw[:limit] if isinstance(m, dict)]
    return {
        "ok": ok and bool(rows),
        "scanner": "poly-us",
        "venue": "polymarket_us",
        "query": query,
        "count": len(rows),
        "markets": rows,
        "command": f"pmxt polymarket_us markets --query {query!r} --limit {limit}",
        "error": err if not rows else "",
    }


def verify_us_slug(slug: str) -> dict[str, Any]:
    ok, data, err = run_pmxt_json("polymarket_us", "markets", "--slug", slug)
    markets = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    found = [m for m in markets if isinstance(m, dict)]
    return {
        "ok": ok and bool(found),
        "slug": slug,
        "us_tradable": bool(found),
        "markets": [_normalize_us_market(m) for m in found],
        "error": err if not found else "",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Polymarket public scanners")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_global = sub.add_parser("poly-global", help="Gamma/CLOB search (polymarket.com)")
    p_global.add_argument("query")
    p_global.add_argument("--limit", type=int, default=20)
    p_global.add_argument("--book", action="store_true", help="Attach CLOB top-of-book")
    p_global.add_argument("--sort", default="volume", choices=("volume", "liquidity"))

    p_us = sub.add_parser("poly-us", help="Paginated US retail search")
    p_us.add_argument("query")
    p_us.add_argument("--limit", type=int, default=20)

    p_verify = sub.add_parser("verify-us", help="Check if slug exists on polymarket.us")
    p_verify.add_argument("slug")

    args = parser.parse_args(argv)
    if args.cmd == "poly-global":
        out = scan_global_poly(args.query, limit=args.limit, with_book=args.book, sort=args.sort)
    elif args.cmd == "poly-us":
        out = scan_poly_us(args.query, limit=args.limit)
    else:
        out = verify_us_slug(args.slug)

    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
