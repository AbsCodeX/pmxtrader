"""
Price movement detector — watchlist vs persisted snapshots.

CLI (via ``./pmx alert scan`` or ``./pmx watchlist alert``):
    ./pmx alert scan [--threshold 0.05] [--once]
    ./pmx watchlist alert [--threshold 0.05] [--once]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apps.bridge.watchlist import (
    _live_kalshi,
    _live_poly_global,
    _live_poly_us,
    default_watchlist_path,
    load_watchlist,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT_PATH = ROOT / "briefs" / "alerts" / "price_snapshots.json"
DEFAULT_MOVES_PATH = ROOT / "briefs" / "alerts" / "price_moves.jsonl"


def entry_key(entry: dict[str, Any]) -> str:
    venue = entry.get("venue", "unknown")
    ident = (
        entry.get("market_id")
        or entry.get("event_id")
        or entry.get("slug")
        or entry.get("label")
        or "unknown"
    )
    return f"{venue}:{ident}"


def extract_price(live: dict[str, Any]) -> float | None:
    for key in ("yes_ask", "mid", "yes_bid"):
        val = live.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


def snapshot_path(root: Path | None = None) -> Path:
    return (root or ROOT) / "briefs" / "alerts" / "price_snapshots.json"


def moves_path(root: Path | None = None) -> Path:
    return (root or ROOT) / "briefs" / "alerts" / "price_moves.jsonl"


def load_snapshots(root: Path | None = None) -> dict[str, Any]:
    path = snapshot_path(root)
    if not path.is_file():
        return {"updated_at": None, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"updated_at": None, "entries": {}}
    if not isinstance(data, dict):
        return {"updated_at": None, "entries": {}}
    data.setdefault("entries", {})
    return data


def save_snapshots(data: dict[str, Any], root: Path | None = None) -> Path:
    path = snapshot_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(tz=UTC).isoformat()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def append_move(record: dict[str, Any], root: Path | None = None) -> Path:
    path = moves_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return path


def fetch_entry_live(entry: dict[str, Any]) -> tuple[dict[str, Any], str]:
    venue = entry.get("venue")
    if venue == "kalshi":
        return _live_kalshi(entry)
    if venue == "polymarket_us":
        return _live_poly_us(entry)
    if venue == "polymarket_global":
        return _live_poly_global(entry)
    return {}, f"Unknown venue {venue!r}"


def price_shift(old: float, new: float) -> float:
    if old <= 0:
        return 0.0
    return abs(new - old) / old


def scan_price_moves(
    *,
    watchlist_path: Path | None = None,
    root: Path | None = None,
    threshold: float = 0.05,
    update_snapshots: bool = True,
    append_alerts: bool = False,
) -> dict[str, Any]:
    """Compare watchlist live prices to last snapshot; return alerts."""
    root = root or ROOT
    wl_path = watchlist_path or default_watchlist_path(root)
    data = load_watchlist(wl_path)
    snapshots = load_snapshots(root)
    prev_entries: dict[str, Any] = snapshots.get("entries") or {}

    alerts: list[dict[str, Any]] = []
    scanned: list[dict[str, Any]] = []
    new_entries: dict[str, Any] = dict(prev_entries)

    for entry in data.get("markets") or []:
        key = entry_key(entry)
        live, err = fetch_entry_live(entry)
        price = extract_price(live) if live else None
        row: dict[str, Any] = {
            "key": key,
            "entry": entry,
            "live": live,
            "price": price,
            "error": err or None,
        }
        scanned.append(row)

        if price is None:
            continue

        prev = prev_entries.get(key)
        prev_price = prev.get("price") if isinstance(prev, dict) else None
        if prev_price is not None:
            shift = price_shift(float(prev_price), price)
            if shift >= threshold:
                alert = {
                    "ts": datetime.now(tz=UTC).isoformat(),
                    "key": key,
                    "venue": entry.get("venue"),
                    "label": entry.get("label") or entry.get("slug") or entry.get("event_id"),
                    "prev_price": prev_price,
                    "price": price,
                    "shift_pct": round(shift, 4),
                    "threshold": threshold,
                    "direction": "up" if price > prev_price else "down",
                }
                alerts.append(alert)
                if append_alerts:
                    append_move(alert, root)

        new_entries[key] = {
            "price": price,
            "yes_ask": live.get("yes_ask"),
            "yes_bid": live.get("yes_bid"),
            "mid": live.get("mid"),
            "ts": datetime.now(tz=UTC).isoformat(),
        }

    if update_snapshots:
        save_snapshots({"entries": new_entries}, root)

    return {
        "ok": True,
        "threshold": threshold,
        "scanned": len(scanned),
        "alerts": alerts,
        "alert_count": len(alerts),
        "markets": scanned,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watchlist price movement alerts")
    parser.add_argument("--threshold", type=float, default=0.05, help="Min relative shift (default 0.05)")
    parser.add_argument("--once", action="store_true", help="Single scan (CI-friendly)")
    parser.add_argument("--watchlist", help="Watchlist JSON path")
    parser.add_argument("--no-update", action="store_true", help="Do not update snapshots")
    parser.add_argument("--append", action="store_true", help="Append alerts to price_moves.jsonl")
    args = parser.parse_args(argv)

    wl = Path(args.watchlist) if args.watchlist else None
    result = scan_price_moves(
        watchlist_path=wl,
        threshold=args.threshold,
        update_snapshots=not args.no_update,
        append_alerts=args.append,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
