#!/usr/bin/env bash
# Prediction Hunt cross-platform sports odds comparison (research only — not execution).
#
# Pre-trade: compare Kalshi vs Polymarket (and others) before choosing a venue.
# Do not use during live in-game execution — use pmxt CLI instead.
#
# Setup: add PREDICTION_HUNT_API_KEY to pmxt/.env
#   Free key: https://www.predictionhunt.com/api/docs
#
# Usage:
#   ./scripts/ph-sports-compare.sh slate nba [YYYY-MM-DD]
#   ./scripts/ph-sports-compare.sh url KALSHI_OR_POLYMARKET_URL
#   ./scripts/ph-sports-compare.sh search "world cup"
#   ./scripts/ph-sports-compare.sh slate nba --json          # raw JSON
#
# Sport codes: nba, nfl, mlb, nhl, cfb, cbb, epl, ucl, mls, atp, wta, pga, ...

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"
# shellcheck source=ph-env.sh
source "$ROOT/scripts/ph-env.sh"

require_prediction_hunt_key

format="${FORMAT:-table}"

usage() {
  cat <<'EOF'
Usage:
  ph-sports-compare.sh slate SPORT [DATE] [--json]
  ph-sports-compare.sh url MARKET_URL [--json]
  ph-sports-compare.sh search QUERY [--json]

Examples:
  ./scripts/ph-sports-compare.sh slate nba
  ./scripts/ph-sports-compare.sh slate ucl 2026-06-19
  ./scripts/ph-sports-compare.sh url https://kalshi.com/markets/kxwcgame/world-cup-game
  ./scripts/ph-sports-compare.sh search "USA Australia world cup"
EOF
}

print_sports_table() {
  python3 - "$@" <<'PY'
import json
import sys

data = json.load(sys.stdin)
mode = sys.argv[1] if len(sys.argv) > 1 else "slate"

def row(platform, bid, ask, last, market_id=""):
    return f"  {platform:<12} bid={bid!s:<6} ask={ask!s:<6} last={last!s:<6}  {market_id}"

if mode == "slate":
    games = data.get("games") or []
    if not games:
        print("No matched games found.")
        sys.exit(0)
    print(f"Sport: {data.get('sport', '-')}  Date: {data.get('date', '-')}\n")
    for game in games:
        title = game.get("title") or game.get("event_name") or "Game"
        print(f"{title}  ({game.get('event_date', '-')})")
        for market in game.get("markets") or []:
            print(row(
                (market.get("platform") or "?").capitalize(),
                market.get("yes_bid", "-"),
                market.get("yes_ask", "-"),
                market.get("last_price", "-"),
                market.get("market_id", ""),
            ))
        print()
elif mode == "url":
    groups = data.get("groups") or data.get("markets") or []
    if isinstance(groups, list) and groups and "markets" in (groups[0] or {}):
        for group in groups:
            print(group.get("title") or group.get("name") or "Matched group")
            for market in group.get("markets") or []:
                print(row(
                    (market.get("platform") or "?").capitalize(),
                    market.get("yes_bid", "-"),
                    market.get("yes_ask", "-"),
                    market.get("last_price", "-"),
                    market.get("market_id", ""),
                ))
            print()
    elif isinstance(groups, list):
        for market in groups:
            print(row(
                (market.get("platform") or "?").capitalize(),
                market.get("yes_bid", "-"),
                market.get("yes_ask", "-"),
                market.get("last_price", "-"),
                market.get("market_id", ""),
            ))
    else:
        print(json.dumps(data, indent=2))
elif mode == "search":
    events = data.get("events") or []
    if not events:
        print("No cross-platform matches found.")
        sys.exit(0)
    for event in events:
        print(event.get("event_name") or event.get("id") or "Event")
        for group in event.get("groups") or []:
            markets = group.get("markets") or []
            if len(markets) < 2:
                continue
            print(f"  {group.get('title', 'Group')}")
            for market in markets:
                print(row(
                    (market.get("platform") or "?").capitalize(),
                    market.get("yes_bid", "-"),
                    market.get("yes_ask", "-"),
                    market.get("last_price", "-"),
                    market.get("market_id", ""),
                ))
            print()
PY
}

# Trailing --json flag
if [[ $# -gt 0 && "${!#}" == "--json" ]]; then
  format=json
  set -- "${@:1:$#-1}"
fi

cmd="${1:-}"

if [[ -z "$cmd" ]]; then
  usage
  exit 1
fi

case "$cmd" in
  slate|sports)
    sport="${2:?Usage: $0 slate SPORT [DATE] [--json]}"
    date="${3:-$(date +%Y-%m-%d)}"
    if [[ "$date" == "--json" ]]; then
      date="$(date +%Y-%m-%d)"
    fi
    response="$(ph_api_get "matching-markets/sports" -G \
      --data-urlencode "sport=$sport" \
      --data-urlencode "date=$date")"
    if [[ "$format" == "json" ]]; then
      printf '%s\n' "$response" | ph_pretty_json
    else
      printf '%s\n' "$response" | print_sports_table slate
    fi
    ;;
  url)
    url="${2:?Usage: $0 url MARKET_URL [--json]}"
    response="$(ph_api_get "matching-markets/url" -G --data-urlencode "url=$url")"
    if [[ "$format" == "json" ]]; then
      printf '%s\n' "$response" | ph_pretty_json
    else
      printf '%s\n' "$response" | print_sports_table url
    fi
    ;;
  search)
    query="${2:?Usage: $0 search QUERY [--json]}"
    response="$(ph_api_get "search" -G \
      --data-urlencode "q=$query" \
      --data-urlencode "limit=5")"
    if [[ "$format" == "json" ]]; then
      printf '%s\n' "$response" | ph_pretty_json
    else
      printf '%s\n' "$response" | print_sports_table search
    fi
    ;;
  *)
    usage
    exit 1
    ;;
esac
