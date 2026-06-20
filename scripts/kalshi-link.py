#!/usr/bin/env python3
"""Resolve a Kalshi URL to an event ticker and run trade evaluation."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

KALSHI_TICKER = re.compile(r"^KX[A-Z0-9-]+$", re.I)
GENERIC_SERIES_SLUGS = frozenset(
    {"world-cup-game", "game", "games", "market", "markets", "event", "events"}
)


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


def normalize_url(raw: str) -> str:
    url = raw.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")
    return url


def parse_kalshi_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host and "kalshi" not in host:
        raise RuntimeError(f"Not a Kalshi URL: {url}")

    parts = [p for p in parsed.path.split("/") if p]
    info: dict[str, Any] = {"url": url, "parts": parts}

    if not parts:
        raise RuntimeError(f"Could not parse Kalshi URL path: {url}")

    if parts[0] == "events" and len(parts) >= 2:
        info["kind"] = "event"
        info["event_id"] = parts[1].upper()
        return info

    if parts[0] == "markets":
        if len(parts) >= 2:
            info["series"] = parts[1].upper()
        if len(parts) >= 3:
            info["page_slug"] = parts[2].lower()
        if len(parts) >= 4:
            ticker = parts[3].upper()
            info["market_hint"] = ticker
            if ticker.count("-") >= 2:
                info["event_id"] = "-".join(ticker.split("-")[:-1])
        info["kind"] = "markets"
        return info

    for part in reversed(parts):
        if KALSHI_TICKER.match(part):
            ticker = part.upper()
            if ticker.count("-") >= 3:
                info["event_id"] = "-".join(ticker.split("-")[:-1])
            else:
                info["event_id"] = ticker
            info["kind"] = "ticker"
            return info

    raise RuntimeError(
        f"Unsupported Kalshi URL shape: {url}\n"
        "Use /events/EVENT_ID or /markets/SERIES/... or paste the event ticker from the page footer."
    )


def fetch_series_events(series: str, limit: int = 50) -> list[dict[str, Any]]:
    data = pmxt_json(
        [
            "kalshi",
            "fetchEvents",
            "--params-json",
            json.dumps({"series": series, "limit": limit, "status": "active"}),
            "--local",
        ]
    )
    if isinstance(data, list):
        return data
    return data.get("events") or data.get("data") or []


def event_date_key(event: dict[str, Any]) -> str:
    eid = str(event.get("id") or event.get("eventId") or "")
    match = re.search(r"-(\d{2}[A-Z]{3}\d{2})", eid)
    return match.group(1) if match else eid


def score_event_for_label(event: dict[str, Any], label: str) -> int:
    title = str(event.get("title") or event.get("id") or "").lower()
    eid = str(event.get("id") or event.get("eventId") or "").upper()
    needle = label.upper()
    score = 0

    sides = re.split(r"\s+vs\s+", title, maxsplit=1)
    if sides and needle.lower() in sides[0]:
        score = 100
    elif needle.lower() in title:
        score = 80
    else:
        for side in sides:
            if needle.lower() in side:
                score = 70
                break

    if score > 0:
        tail = eid.split("-")[-1] if "-" in eid else eid
        if tail.startswith(needle):
            score += 40
        elif needle in tail:
            score += 20
    return score


def score_event_for_slug(event: dict[str, Any], slug: str) -> int:
    if slug in GENERIC_SERIES_SLUGS:
        return 0
    title = str(event.get("title") or "").lower()
    words = [w for w in re.split(r"[^a-z0-9]+", slug) if len(w) > 2]
    return sum(10 for w in words if w in title)


def pick_event(events: list[dict[str, Any]], label: str | None, slug: str | None) -> dict[str, Any]:
    if not events:
        raise RuntimeError("No active events found for this series.")

    if label:
        ranked = sorted(
            events,
            key=lambda e: (score_event_for_label(e, label), event_date_key(e)),
            reverse=True,
        )
        if score_event_for_label(ranked[0], label) > 0:
            return ranked[0]

    if slug:
        ranked = sorted(events, key=lambda e: score_event_for_slug(e, slug), reverse=True)
        if score_event_for_slug(ranked[0], slug) > 0:
            return ranked[0]

    if len(events) == 1:
        return events[0]

    lines = ["Multiple open events in this series — pass an outcome label (e.g. USA):"]
    for event in events[:12]:
        eid = event.get("id") or event.get("eventId")
        title = event.get("title") or ""
        lines.append(f"  {eid}  {title}")
    if len(events) > 12:
        lines.append(f"  ... and {len(events) - 12} more")
    lines.append("Example: ./pmx link 'URL' USA 1")
    raise RuntimeError("\n".join(lines))


def resolve_event_id(url: str, outcome_label: str | None = None) -> str:
    info = parse_kalshi_url(url)

    if info.get("event_id"):
        return str(info["event_id"]).upper()

    if info.get("kind") == "markets":
        series = info.get("series")
        if not series:
            raise RuntimeError("Could not determine Kalshi series from URL.")
        events = fetch_series_events(series)
        event = pick_event(events, outcome_label, info.get("page_slug"))
        eid = event.get("id") or event.get("eventId")
        if not eid:
            raise RuntimeError("Resolved event missing id.")
        return str(eid).upper()

    raise RuntimeError(f"Could not resolve event id from: {url}")


def run_eval(
    event_id: str,
    url: str,
    outcome_label: str | None,
    amount: float,
    side: str,
    as_json: bool,
) -> int:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "pmxt-eval.py"),
        "--event-id",
        event_id,
        "--amount",
        str(amount),
        "--side",
        side,
        "--router-url",
        url,
        "--balance",
    ]
    if outcome_label:
        cmd.extend(["--outcome-label", outcome_label])
    if as_json:
        cmd.append("--json")

    if as_json:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            return result.returncode
        snapshot = json.loads(result.stdout)
        snapshot["sourceUrl"] = url
        snapshot["resolvedEventId"] = event_id
        print(json.dumps(snapshot, indent=2))
        return 0

    print(f"URL:       {url}")
    print(f"Resolved:  {event_id}")
    print()
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        return proc.returncode

    # Fetch outcome id for next-step hints
    hint_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "pmxt-eval.py"),
        "--event-id",
        event_id,
        "--outcome-label",
        outcome_label or "USA",
        "--amount",
        str(amount),
        "--json",
    ]
    try:
        out = subprocess.run(hint_cmd, capture_output=True, text=True, check=False)
        if out.returncode == 0:
            snap = json.loads(out.stdout)
            ob = snap.get("outcomeId")
            market = snap.get("marketId")
            print()
            print("Next:")
            if ob:
                print(f"  ./pmx watch {ob}")
            if market and ob:
                print(f"  ./pmx trade {market} {ob} {int(amount) if amount == int(amount) else amount}")
            print("  ./pmx status   # kill switch must be OFF")
    except (json.JSONDecodeError, KeyError):
        pass
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a Kalshi link (URL → event → quote)")
    parser.add_argument("url", help="Kalshi market or event URL")
    parser.add_argument("outcome_label", nargs="?", help="Outcome label e.g. USA, Tie")
    parser.add_argument("amount", nargs="?", type=float, default=1.0, help="Contract size")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--side", choices=["buy", "sell"], default="buy")
    args = parser.parse_args()

    url = normalize_url(args.url)
    label = args.outcome_label
    amount = args.amount

    if label is not None:
        try:
            amount = float(label)
            label = None
        except ValueError:
            pass

    if args.amount is not None and label is not None:
        try:
            amount = float(args.amount)
        except (TypeError, ValueError):
            amount = 1.0

    try:
        event_id = resolve_event_id(url, label)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return run_eval(event_id, url, label, amount, args.side, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
