"""
Curated market watchlist — persist entries + volume/liquidity filters.

Persistence: ``briefs/watchlists/default.json``

CLI (via ``./pmx watchlist``):
    ./pmx watchlist list
    ./pmx watchlist add VENUE ID [--url URL] [--note NOTE]
    ./pmx watchlist add --url URL [--note NOTE]
    ./pmx watchlist remove ID
    ./pmx watchlist filter [--min-volume N] [--min-liquidity N]
    ./pmx watchlist scan
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from apps.bridge.kalshi_scanner import KALSHI_API, _dollar
from apps.bridge.poly_scanner import run_pmxt_json, verify_us_slug

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WATCHLIST_PATH = ROOT / "briefs" / "watchlists" / "default.json"

VALID_VENUES = frozenset({"kalshi", "polymarket_us", "polymarket_global"})
KALSHI_TICKER = re.compile(r"^KX[A-Z0-9-]+$", re.I)

_VENUE_ALIASES: dict[str, str] = {
    "kalshi": "kalshi",
    "poly-us": "polymarket_us",
    "poly_us": "polymarket_us",
    "polymarket-us": "polymarket_us",
    "polymarket_us": "polymarket_us",
    "poly-global": "polymarket_global",
    "poly_global": "polymarket_global",
    "polymarket-global": "polymarket_global",
    "polymarket_global": "polymarket_global",
    "polymarket": "polymarket_global",
    "global": "polymarket_global",
}


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def _empty_watchlist() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": _now_iso(),
        "filters": {
            "min_volume_24h": None,
            "min_liquidity": None,
        },
        "markets": [],
    }


def default_watchlist_path(root: Path | None = None) -> Path:
    return (root or ROOT) / "briefs" / "watchlists" / "default.json"


def load_watchlist(path: Path | None = None) -> dict[str, Any]:
    """Load watchlist JSON; return empty structure if missing."""
    target = path or DEFAULT_WATCHLIST_PATH
    if not target.is_file():
        return _empty_watchlist()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _empty_watchlist()
    if not isinstance(data, dict):
        return _empty_watchlist()
    data.setdefault("version", 1)
    data.setdefault("filters", {})
    filters = data["filters"]
    if not isinstance(filters, dict):
        filters = {}
        data["filters"] = filters
    filters.setdefault("min_volume_24h", None)
    filters.setdefault("min_liquidity", None)
    markets = data.get("markets")
    data["markets"] = markets if isinstance(markets, list) else []
    return data


def save_watchlist(data: dict[str, Any], path: Path | None = None) -> Path:
    """Persist watchlist JSON."""
    target = path or DEFAULT_WATCHLIST_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now_iso()
    target.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return target


def normalize_venue(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "_")
    venue = _VENUE_ALIASES.get(key)
    if venue:
        return venue
    if key in VALID_VENUES:
        return key
    raise ValueError(f"Unknown venue {raw!r}; use kalshi, polymarket_us, or polymarket_global")


def _store_kalshi_id(entry: dict[str, Any], identifier: str) -> None:
    ident = identifier.strip().upper()
    if not KALSHI_TICKER.match(ident):
        entry["event_id"] = ident
        return
    parts = ident.split("-")
    if len(parts) >= 3 and parts[-1].isdigit():
        entry["market_id"] = ident
        entry["event_id"] = "-".join(parts[:-1])
    else:
        entry["event_id"] = ident


def _entry_key(entry: dict[str, Any]) -> str:
    for field in ("market_id", "event_id", "slug"):
        val = entry.get(field)
        if val:
            return str(val)
    return ""


def _entry_matches(entry: dict[str, Any], needle: str) -> bool:
    needle_norm = needle.strip().lower()
    if needle_norm.isdigit():
        return False
    for field in ("market_id", "event_id", "slug", "url", "label"):
        val = entry.get(field)
        if val and str(val).lower() == needle_norm:
            return True
    key = _entry_key(entry)
    return bool(key and key.lower() == needle_norm)


def infer_from_url(url: str) -> dict[str, Any]:
    """Infer venue + identifiers from a Kalshi or Polymarket URL."""
    raw = url.strip()
    if not raw:
        raise ValueError("URL is required")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw.lstrip("/")

    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    parts = [p for p in parsed.path.split("/") if p]

    entry: dict[str, Any] = {"url": raw, "label": None, "added_at": _now_iso()}

    if "kalshi" in host:
        entry["venue"] = "kalshi"
        if parts and parts[0] == "events" and len(parts) >= 2:
            entry["event_id"] = parts[1].upper()
        elif parts and parts[0] == "markets":
            if len(parts) >= 4:
                _store_kalshi_id(entry, parts[3])
            elif len(parts) >= 2:
                entry["series"] = parts[1].upper()
        else:
            for part in reversed(parts):
                if KALSHI_TICKER.match(part):
                    _store_kalshi_id(entry, part)
                    break
        if not _entry_key(entry):
            raise ValueError(f"Could not extract Kalshi id from URL: {url}")
        return entry

    if host.endswith("polymarket.us"):
        entry["venue"] = "polymarket_us"
        if len(parts) >= 2 and parts[0] == "market":
            entry["slug"] = parts[1]
        elif parts:
            entry["slug"] = parts[-1]
        if not entry.get("slug"):
            raise ValueError(f"Could not extract Polymarket US slug from URL: {url}")
        return entry

    if "polymarket.com" in host:
        entry["venue"] = "polymarket_global"
        if len(parts) >= 2 and parts[0] in ("event", "market", "markets"):
            entry["slug"] = parts[1]
        elif parts:
            entry["slug"] = parts[-1]
        if not entry.get("slug"):
            raise ValueError(f"Could not extract Polymarket slug from URL: {url}")
        return entry

    raise ValueError(f"Unsupported URL host {host!r}; use kalshi.com or polymarket.us/.com")


def add_market(
    *,
    venue: str | None = None,
    identifier: str | None = None,
    url: str | None = None,
    label: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Add a market entry; returns updated watchlist."""
    data = load_watchlist(path)

    if url and not venue and not identifier:
        entry = infer_from_url(url)
    else:
        if not venue or not identifier:
            raise ValueError("Provide VENUE + ID, or --url")
        entry = {
            "venue": normalize_venue(venue),
            "market_id": None,
            "event_id": None,
            "slug": None,
            "url": url,
            "label": label,
            "added_at": _now_iso(),
        }
        ident = identifier.strip()
        if entry["venue"] == "kalshi":
            _store_kalshi_id(entry, ident)
        else:
            entry["slug"] = ident

    if label:
        entry["label"] = label
    if url and not entry.get("url"):
        entry["url"] = url

    for existing in data["markets"]:
        if existing.get("venue") == entry.get("venue") and _entry_matches(existing, _entry_key(entry)):
            raise ValueError(f"Market already on watchlist: {_entry_key(entry)}")

    data["markets"].append(entry)
    save_watchlist(data, path)
    return data


def remove_market(target: str, *, path: Path | None = None) -> dict[str, Any]:
    """Remove by 1-based index or identifier match."""
    data = load_watchlist(path)
    markets: list[dict[str, Any]] = data["markets"]
    if not markets:
        raise ValueError("Watchlist is empty")

    if target.strip().isdigit():
        idx = int(target.strip())
        if idx < 1 or idx > len(markets):
            raise ValueError(f"Index out of range: {idx} (1–{len(markets)})")
        markets.pop(idx - 1)
    else:
        needle = target.strip()
        for i, entry in enumerate(markets):
            if _entry_matches(entry, needle):
                markets.pop(i)
                break
        else:
            raise ValueError(f"No watchlist entry matching {target!r}")

    save_watchlist(data, path)
    return data


def list_markets(*, path: Path | None = None) -> dict[str, Any]:
    """Return watchlist entries + filters."""
    return load_watchlist(path)


def set_filters(
    *,
    min_volume_24h: float | None = ...,  # type: ignore[assignment]
    min_liquidity: float | None = ...,  # type: ignore[assignment]
    path: Path | None = None,
) -> dict[str, Any]:
    """Set or clear global filters (pass None explicitly to clear)."""
    data = load_watchlist(path)
    filters = data["filters"]
    if min_volume_24h is not ...:
        filters["min_volume_24h"] = min_volume_24h
    if min_liquidity is not ...:
        filters["min_liquidity"] = min_liquidity
    save_watchlist(data, path)
    return data


def _fetch_kalshi_json(path: str, *, timeout: int = 30) -> tuple[dict[str, Any] | None, str]:
    url = f"{KALSHI_API}/{path.lstrip('/')}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        return None, f"HTTP {exc.code}: {body[:200]}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "Invalid Kalshi response"
    return payload, ""


def _live_kalshi(entry: dict[str, Any]) -> tuple[dict[str, Any], str]:
    market_id = entry.get("market_id")
    event_id = entry.get("event_id")
    raw: dict[str, Any] | None = None
    err = ""

    if market_id:
        payload, err = _fetch_kalshi_json(f"markets/{market_id}")
        if payload:
            raw = payload.get("market") if isinstance(payload.get("market"), dict) else payload

    if raw is None and event_id:
        payload, err = _fetch_kalshi_json(f"events/{event_id}")
        if payload and isinstance(payload.get("event"), dict):
            event = payload["event"]
            markets = event.get("markets") or []
            if isinstance(markets, list) and markets and isinstance(markets[0], dict):
                raw = markets[0]
            title = event.get("title")
            if title and not entry.get("label"):
                entry = {**entry, "label": title}

    if raw is None and event_id:
        payload, err = _fetch_kalshi_json(f"markets?event_ticker={urllib.parse.quote(event_id)}&limit=1")
        if payload:
            batch = payload.get("markets") or []
            if isinstance(batch, list) and batch and isinstance(batch[0], dict):
                raw = batch[0]

    if not isinstance(raw, dict):
        return {}, err or "Kalshi market not found"

    volume = _dollar(raw.get("volume_24h_fp") or raw.get("volume_24h"))
    liquidity = _dollar(raw.get("open_interest_fp") or raw.get("open_interest"))
    yes_bid = _dollar(raw.get("yes_bid_dollars"))
    yes_ask = _dollar(raw.get("yes_ask_dollars"))
    mid = round((yes_bid + yes_ask) / 2, 4) if yes_bid is not None and yes_ask is not None else None

    return {
        "title": raw.get("title"),
        "status": raw.get("status"),
        "market_id": raw.get("ticker") or raw.get("market_ticker"),
        "event_id": raw.get("event_ticker"),
        "volume_24h": volume,
        "liquidity": liquidity,
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "mid": mid,
    }, ""


def _live_poly_us(entry: dict[str, Any]) -> tuple[dict[str, Any], str]:
    slug = entry.get("slug") or entry.get("market_id")
    if not slug:
        return {}, "Missing slug"
    result = verify_us_slug(str(slug))
    if not result.get("ok") or not result.get("markets"):
        return {}, result.get("error") or "US slug not found"
    raw = result["markets"][0]
    return {
        "title": raw.get("title"),
        "slug": raw.get("slug"),
        "market_id": raw.get("market_id"),
        "volume_24h": _dollar(raw.get("volume24h") or raw.get("volume")),
        "liquidity": None,
        "us_tradable": True,
    }, ""


def _live_poly_global(entry: dict[str, Any]) -> tuple[dict[str, Any], str]:
    slug = entry.get("slug") or entry.get("market_id")
    if not slug:
        return {}, "Missing slug"
    ok, data, err = run_pmxt_json("polymarket", "markets", "--slug", str(slug), timeout=60)
    markets_raw = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    found = [m for m in markets_raw if isinstance(m, dict)]
    if not ok or not found:
        return {}, err or "Global slug not found"
    raw = found[0]
    outcomes = raw.get("outcomes") or []
    prices = [o.get("price") for o in outcomes if isinstance(o, dict) and o.get("price") is not None]
    return {
        "title": raw.get("title"),
        "slug": raw.get("slug") or raw.get("marketId"),
        "market_id": raw.get("marketId") or raw.get("id"),
        "event_id": raw.get("eventId"),
        "volume_24h": _dollar(raw.get("volume24h") or raw.get("volume")),
        "liquidity": _dollar(raw.get("liquidity")),
        "mid": sum(prices) / len(prices) if prices else None,
    }, ""


def _evaluate_filters(
    live: dict[str, Any],
    filters: dict[str, Any],
) -> tuple[bool | None, dict[str, Any], str]:
    """Return (passes_filters, filter_results, summary_reason)."""
    results: dict[str, Any] = {}
    reasons: list[str] = []
    active = False
    all_pass = True
    any_fail = False

    min_vol = filters.get("min_volume_24h")
    if min_vol is not None:
        active = True
        value = live.get("volume_24h")
        if value is None:
            results["min_volume_24h"] = {
                "pass": None,
                "value": None,
                "threshold": min_vol,
                "reason": "volume data unavailable",
            }
            all_pass = False
            reasons.append("volume unknown")
        elif value >= float(min_vol):
            results["min_volume_24h"] = {"pass": True, "value": value, "threshold": min_vol}
        else:
            results["min_volume_24h"] = {"pass": False, "value": value, "threshold": min_vol}
            any_fail = True
            reasons.append(f"volume {value} < {min_vol}")

    min_liq = filters.get("min_liquidity")
    if min_liq is not None:
        active = True
        value = live.get("liquidity")
        if value is None:
            results["min_liquidity"] = {
                "pass": None,
                "value": None,
                "threshold": min_liq,
                "reason": "liquidity data unavailable",
            }
            all_pass = False
            reasons.append("liquidity unknown")
        elif value >= float(min_liq):
            results["min_liquidity"] = {"pass": True, "value": value, "threshold": min_liq}
        else:
            results["min_liquidity"] = {"pass": False, "value": value, "threshold": min_liq}
            any_fail = True
            reasons.append(f"liquidity {value} < {min_liq}")

    if not active:
        return None, results, ""
    if any_fail:
        return False, results, "; ".join(reasons)
    if all_pass:
        return True, results, "passes filters"
    return None, results, "; ".join(reasons)


def scan_watchlist(*, path: Path | None = None) -> dict[str, Any]:
    """Evaluate each entry against live data and global filters."""
    data = load_watchlist(path)
    filters = data.get("filters") or {}
    rows: list[dict[str, Any]] = []
    pass_count = 0
    fail_count = 0

    for entry in data.get("markets") or []:
        venue = entry.get("venue")
        live: dict[str, Any] = {}
        err = ""
        if venue == "kalshi":
            live, err = _live_kalshi(entry)
        elif venue == "polymarket_us":
            live, err = _live_poly_us(entry)
        elif venue == "polymarket_global":
            live, err = _live_poly_global(entry)
        else:
            err = f"Unknown venue {venue!r}"

        scan_ok = bool(live) and not err
        passes, filter_results, reason = _evaluate_filters(live, filters) if scan_ok else (None, {}, err)
        if passes is True:
            pass_count += 1
        elif passes is False:
            fail_count += 1

        rows.append(
            {
                "entry": entry,
                "live": live,
                "scan_ok": scan_ok,
                "passes_filters": passes,
                "filter_results": filter_results,
                "reason": reason or err,
            }
        )

    return {
        "ok": True,
        "watchlist_path": str(path or DEFAULT_WATCHLIST_PATH),
        "filters": filters,
        "count": len(rows),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "entries": rows,
    }


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Curated market watchlist")
    parser.add_argument("--file", type=Path, default=None, help="Watchlist JSON path")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Show entries + filters")

    p_add = sub.add_parser("add", help="Add market by venue+id or --url")
    p_add.add_argument("venue", nargs="?", default=None)
    p_add.add_argument("identifier", nargs="?", default=None)
    p_add.add_argument("--url")
    p_add.add_argument("--note")

    p_rm = sub.add_parser("remove", help="Remove by index (1-based) or id")
    p_rm.add_argument("target")

    p_filter = sub.add_parser("filter", help="Set or clear global filters")
    p_filter.add_argument("--min-volume", type=float, default=None, dest="min_volume")
    p_filter.add_argument("--min-liquidity", type=float, default=None, dest="min_liquidity")
    p_filter.add_argument("--clear-volume", action="store_true")
    p_filter.add_argument("--clear-liquidity", action="store_true")

    sub.add_parser("scan", help="Scan entries against live data + filters")

    args = parser.parse_args(argv)
    path: Path | None = args.file

    try:
        if args.cmd == "list":
            _print_json(list_markets(path=path))
            return 0
        if args.cmd == "add":
            if args.url and not args.venue:
                data = add_market(url=args.url, label=args.note, path=path)
            else:
                data = add_market(
                    venue=args.venue,
                    identifier=args.identifier,
                    url=args.url,
                    label=args.note,
                    path=path,
                )
            _print_json({"ok": True, "watchlist": data})
            return 0
        if args.cmd == "remove":
            data = remove_market(args.target, path=path)
            _print_json({"ok": True, "watchlist": data})
            return 0
        if args.cmd == "filter":
            filter_kwargs: dict[str, Any] = {"path": path}
            if args.clear_volume:
                filter_kwargs["min_volume_24h"] = None
            elif args.min_volume is not None:
                filter_kwargs["min_volume_24h"] = args.min_volume
            if args.clear_liquidity:
                filter_kwargs["min_liquidity"] = None
            elif args.min_liquidity is not None:
                filter_kwargs["min_liquidity"] = args.min_liquidity
            data = set_filters(**filter_kwargs)
            _print_json({"ok": True, "watchlist": data})
            return 0
        if args.cmd == "scan":
            _print_json(scan_watchlist(path=path))
            return 0
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
