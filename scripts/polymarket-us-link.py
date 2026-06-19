#!/usr/bin/env python3
"""Resolve a Polymarket US URL to market slug and run quote."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def normalize_url(raw: str) -> str:
    url = raw.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")
    return url


def slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host and "polymarket" not in host:
        raise RuntimeError(f"Not a Polymarket US URL: {url}")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2 and parts[0] in ("market", "markets", "event", "events"):
        return parts[1].strip("/")

    if len(parts) == 1 and parts[0] not in ("market", "markets", "event", "events"):
        return parts[0]

    raise RuntimeError(
        f"Could not parse market slug from: {url}\n"
        "Expected: https://polymarket.us/market/SLUG or paste the slug directly."
    )


def normalize_side(raw: str) -> str:
    s = raw.lower()
    if s in ("long", "yes", "y", "l", "buy-long"):
        return "long"
    if s in ("short", "no", "n", "s", "sell-short"):
        return "short"
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description="Quote a Polymarket US link or slug")
    parser.add_argument("url_or_slug", help="https://polymarket.us/market/SLUG or SLUG")
    parser.add_argument("side", nargs="?", default="long", help="long|short")
    parser.add_argument("qty", nargs="?", help="unused — for symmetry with pmx link")
    args = parser.parse_args()

    raw = args.url_or_slug.strip()
    if raw.startswith("http") or "polymarket" in raw:
        url = normalize_url(raw)
        slug = slug_from_url(url)
        print(f"URL:   {url}")
    elif re.match(r"^[\w-]+$", raw):
        slug = raw
        url = f"https://polymarket.us/market/{slug}"
    else:
        print(f"Error: invalid slug or URL: {raw}", file=sys.stderr)
        return 1

    side = normalize_side(args.side)
    print(f"Slug:  {slug}")
    print(f"Side:  {side}")
    print()

    cmd = [
        str(ROOT / "scripts" / "polymarket-us-quickstart.sh"),
        "quote",
        slug,
        side,
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
