#!/usr/bin/env bash
# Stream your Kalshi order fills (authenticated WebSocket).
#
# Kalshi official: user fill channel
# https://docs.kalshi.com/websockets/user-fills
#
# PMXT watch:* does not expose Kalshi user fills yet — this uses Kalshi WS directly.
#
# Usage:
#   ./scripts/pmxt-watch-fills.sh
#   ./scripts/pmxt-watch-fills.sh --market-ticker KXWCGAME-26JUN19USAAUS-USA
#   ./scripts/pmxt-watch-fills.sh --max-messages 5 --alert-file briefs/alerts/fills.jsonl
#   ./scripts/pmxt-watch-fills.sh --timeout-ms 5000   # verify connection, then exit
#
# Run after placing an order (Trader lane) to confirm fills without polling positions.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

if [[ ! -f "$PMXT_DIR/.env" ]]; then
  echo "Missing pmxt/.env — add KALSHI_API_KEY and KALSHI_PRIVATE_KEY"
  exit 1
fi

cd "$PMXT_DIR"
exec node "$ROOT/scripts/kalshi-watch-fills.mjs" "$@"
