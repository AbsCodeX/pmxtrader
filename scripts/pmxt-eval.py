#!/usr/bin/env python3
"""Snapshot Kalshi trade evaluation: event, orderbook, fill cost, optional cross-venue."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def pmxt_json(args: list[str]) -> Any:
    result = subprocess.run(
        ["pmxt", *args, "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(err or f"pmxt failed: {' '.join(args)}")
    return json.loads(result.stdout)


def pick_outcome(event: dict[str, Any], outcome_id: str | None, label: str | None) -> dict[str, Any]:
    markets = event.get("markets") or []
    if not markets:
        raise RuntimeError("Event has no markets")
    outcomes: list[dict[str, Any]] = []
    for market in markets:
        for outcome in market.get("outcomes") or []:
            enriched = dict(outcome)
            enriched.setdefault("marketId", market.get("id"))
            enriched.setdefault("marketTitle", market.get("title"))
            outcomes.append(enriched)
    if not outcomes:
        raise RuntimeError("Event has no outcomes")

    if outcome_id:
        for o in outcomes:
            if o.get("outcomeId") == outcome_id or o.get("id") == outcome_id:
                return o
        raise RuntimeError(f"Outcome not found: {outcome_id}")

    if label:
        needle = label.lower()
        for o in outcomes:
            if str(o.get("label", "")).lower() == needle:
                return o
        for o in outcomes:
            if needle in str(o.get("label", "")).lower():
                return o
        raise RuntimeError(f"Outcome label not found: {label}")

    return outcomes[0]


def top_of_book(book: dict[str, Any]) -> dict[str, Any]:
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    best_bid = bids[0] if bids else None
    best_ask = asks[0] if asks else None
    bid_depth = sum(float(level.get("size", 0) or 0) for level in bids[:5])
    ask_depth = sum(float(level.get("size", 0) or 0) for level in asks[:5])
    return {
        "bestBid": best_bid,
        "bestAsk": best_ask,
        "bidLevels": len(bids),
        "askLevels": len(asks),
        "bidDepthTop5": round(bid_depth, 2),
        "askDepthTop5": round(ask_depth, 2),
    }


def execution_price(outcome_id: str, side: str, amount: float, book: dict[str, Any]) -> dict[str, Any] | None:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(book, handle)
        book_path = handle.name
    try:
        data = pmxt_json(
            [
                "execution-price",
                "--orderbook-json",
                f"@{book_path}",
                "--side",
                side,
                "--amount",
                str(amount),
                "-e",
                "kalshi",
                "--local",
            ]
        )
        return data if isinstance(data, dict) else {"price": data}
    except RuntimeError:
        return None
    finally:
        Path(book_path).unlink(missing_ok=True)


def router_matches(url: str, limit: int) -> list[dict[str, Any]]:
    data = pmxt_json(
        [
            "router:market-matches",
            "--url",
            url,
            "--hosted",
            "--include-prices",
            "--limit",
            str(limit),
        ]
    )
    return data if isinstance(data, list) else []


def compact_router(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for row in rows[:8]:
        source = row.get("sourceMarket") or {}
        matches = row.get("matches") or row.get("matchedMarkets") or []
        entry: dict[str, Any] = {
            "source": {
                "venue": source.get("exchange") or source.get("platform"),
                "id": source.get("marketId") or source.get("id"),
                "title": source.get("title"),
            },
            "matches": [],
        }
        for match in matches[:5]:
            entry["matches"].append(
                {
                    "venue": match.get("exchange") or match.get("platform"),
                    "id": match.get("marketId") or match.get("id"),
                    "title": match.get("title"),
                    "price": match.get("price") or match.get("lastPrice"),
                    "yesBid": match.get("yesBid") or match.get("bid"),
                    "yesAsk": match.get("yesAsk") or match.get("ask"),
                }
            )
        compact.append(entry)
    return compact


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    event = pmxt_json(["kalshi", "event", "--event-id", args.event_id, "--local"])
    outcome = pick_outcome(event, args.outcome_id, args.outcome_label)
    outcome_id = outcome.get("outcomeId") or outcome.get("id")
    if not outcome_id:
        raise RuntimeError("Could not resolve outcomeId")

    meta = outcome.get("metadata") or {}
    book: dict[str, Any] = {}
    top: dict[str, Any] = {}
    orderbook_error: str | None = None
    try:
        book = pmxt_json(["kalshi", "orderbook", outcome_id, "--local", "--limit", str(args.book_depth)])
        top = top_of_book(book)
    except RuntimeError as exc:
        orderbook_error = str(exc)

    snapshot: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "eventId": args.event_id,
        "eventTitle": event.get("title"),
        "marketId": outcome.get("marketId"),
        "marketTitle": outcome.get("marketTitle"),
        "outcomeId": outcome_id,
        "outcomeLabel": outcome.get("label"),
        "price": outcome.get("price"),
        "bid": meta.get("bid") or outcome.get("bestBid") or (top.get("bestBid") or {}).get("price"),
        "ask": meta.get("ask") or outcome.get("bestAsk") or (top.get("bestAsk") or {}).get("price"),
        "priceChange24h": outcome.get("priceChange24h"),
        "orderbook": top,
        "kalshiNotes": {
            "orderbookModel": "Kalshi returns yes/no bids; ask derived in binary markets",
            "docs": "https://docs.kalshi.com/getting_started/orderbook_responses",
        },
    }
    if orderbook_error:
        snapshot["orderbookError"] = orderbook_error

    if args.amount and args.amount > 0 and book:
        fill = execution_price(outcome_id, args.side, args.amount, book)
        if fill is not None:
            snapshot["execution"] = {
                "side": args.side,
                "amount": args.amount,
                **fill,
            }

    if args.router_url:
        try:
            snapshot["crossVenue"] = compact_router(router_matches(args.router_url, args.router_limit))
            snapshot["crossVenueSource"] = "pmxt-router-hosted"
        except RuntimeError as exc:
            snapshot["crossVenueError"] = str(exc)

    if args.balance:
        try:
            snapshot["balance"] = pmxt_json(["kalshi", "balance", "--local"])
        except RuntimeError as exc:
            snapshot["balanceError"] = str(exc)

    return snapshot


def print_table(snapshot: dict[str, Any]) -> None:
    print(f"Event:     {snapshot.get('eventTitle')} ({snapshot.get('eventId')})")
    print(f"Outcome:   {snapshot.get('outcomeLabel')} ({snapshot.get('outcomeId')})")
    print(f"Price:     {snapshot.get('price')}  bid={snapshot.get('bid')}  ask={snapshot.get('ask')}")
    ob = snapshot.get("orderbook") or {}
    print(
        f"Book:      levels bid={ob.get('bidLevels')} ask={ob.get('askLevels')} "
        f"depth5 bid={ob.get('bidDepthTop5')} ask={ob.get('askDepthTop5')}"
    )
    ex = snapshot.get("execution")
    if ex:
        print(f"Fill est:  side={ex.get('side')} amount={ex.get('amount')} price={ex.get('price') or ex}")
    ob_err = snapshot.get("orderbookError")
    if ob_err:
        print(f"Book:      unavailable ({ob_err.split(':')[-1].strip()})")
    cv = snapshot.get("crossVenue") or []
    if cv:
        print("Cross-venue (PMXT Router):")
        for group in cv[:3]:
            src = group.get("source") or {}
            print(f"  {src.get('venue')}: {src.get('title')}")
            for match in group.get("matches") or []:
                print(
                    f"    -> {match.get('venue')}: bid={match.get('yesBid')} "
                    f"ask={match.get('yesAsk')} last={match.get('price')}"
                )
    cv_err = snapshot.get("crossVenueError")
    if cv_err:
        print(f"Cross-venue: FAILED ({cv_err})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Kalshi trade evaluation snapshot via PMXT")
    parser.add_argument("--event-id", required=True, help="Kalshi event ticker from page footer")
    parser.add_argument("--outcome-id", help="PMXT/Kalshi outcomeId")
    parser.add_argument("--outcome-label", help="Outcome label e.g. USA, Tie")
    parser.add_argument("--side", choices=["buy", "sell"], default="buy")
    parser.add_argument("--amount", type=float, default=1.0, help="Contracts for fill simulation")
    parser.add_argument("--book-depth", type=int, default=20)
    parser.add_argument("--router-url", help="Kalshi or Polymarket URL for cross-venue (PMXT Router, free)")
    parser.add_argument("--router-limit", type=int, default=5)
    parser.add_argument("--balance", action="store_true", help="Include account balance")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        snapshot = build_snapshot(args)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(snapshot, indent=2))
    else:
        print_table(snapshot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
