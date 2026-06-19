#!/usr/bin/env bash
# Stream Kalshi orderbook or trades via PMXT (free — uses venue WebSocket through sidecar).
#
# Kalshi official: orderbook updates + ticker + public trades channels
# https://docs.kalshi.com/websockets/orderbook-updates
# PMXT: pmxt watch:* wraps the same live data.
#
# Usage:
#   ./scripts/pmxt-watch.sh orderbook OUTCOME_ID [--max-messages 100]
#   ./scripts/pmxt-watch.sh trades OUTCOME_ID
#   ./scripts/pmxt-watch.sh fills [--market-ticker OUTCOME_ID]   # your orders only
#   ./scripts/pmxt-watch.sh orderbook OUTCOME_ID --alert-file briefs/alerts/latest.jsonl
#
# Get OUTCOME_ID from: ./scripts/pmxt-eval.sh --event-id EVENT --json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

EXCHANGE=kalshi
KIND="${1:?Usage: $0 orderbook|trades|fills [OUTCOME_ID] [--max-messages N] [--alert-file PATH]}"
shift

case "$KIND" in
  fills|fill|myfills|my-fills)
    FILL_ARGS=()
    if [[ $# -gt 0 && "$1" != --* ]]; then
      FILL_ARGS+=(--market-ticker "$1")
      shift
    fi
    exec "$ROOT/scripts/pmxt-watch-fills.sh" "${FILL_ARGS[@]}" "$@"
    ;;
  orderbook|book) WATCH_CMD="watch:orderBook" ;;
  trades|trade) WATCH_CMD="watch:trades" ;;
  *)
    echo "Unknown stream: $KIND (use orderbook, trades, or fills)"
    exit 1
    ;;
esac

OUTCOME_ID="${1:?Usage: $0 orderbook|trades OUTCOME_ID}"
shift

MAX_MESSAGES=""
ALERT_FILE=""
TIMEOUT_MS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-messages) MAX_MESSAGES="$2"; shift 2 ;;
    --alert-file) ALERT_FILE="$2"; shift 2 ;;
    --timeout-ms) TIMEOUT_MS="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

ARGS=("$WATCH_CMD" "$EXCHANGE" "$OUTCOME_ID" --local)
[[ -n "$MAX_MESSAGES" ]] && ARGS+=(--max-messages "$MAX_MESSAGES")
[[ -n "$TIMEOUT_MS" ]] && ARGS+=(--timeout-ms "$TIMEOUT_MS")

if [[ -z "$ALERT_FILE" ]]; then
  pmxt_cli "${ARGS[@]}"
  exit 0
fi

mkdir -p "$(dirname "$ALERT_FILE")"
echo "Streaming to $ALERT_FILE (JSONL)"
pmxt_cli "${ARGS[@]}" | while IFS= read -r line; do
  printf '%s\n' "$line" >> "$ALERT_FILE"
  # Print compact one-liner for terminal
  python3 -c "
import json, sys
try:
    d = json.loads(sys.argv[1])
    bid = d.get('bids', [{}])[0].get('price') if d.get('bids') else None
    ask = d.get('asks', [{}])[0].get('price') if d.get('asks') else None
    print(f\"{d.get('timestamp', 'update')} bid={bid} ask={ask}\")
except Exception:
    print(sys.argv[1][:120])
" "$line" 2>/dev/null || printf '%s\n' "$line"
done
