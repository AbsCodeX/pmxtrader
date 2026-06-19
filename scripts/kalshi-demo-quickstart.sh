#!/bin/bash
# Kalshi Demo paper-trading quickstart for pmxtrader
#
# Prerequisites:
#   1. Demo account at https://demo.kalshi.com
#   2. Demo API key + RSA private key in pmxt/.env (see pmxt/.env.example)
#
# Usage:
#   ./scripts/kalshi-demo-quickstart.sh              # search markets
#   ./scripts/kalshi-demo-quickstart.sh balance      # show demo balance
#   ./scripts/kalshi-demo-quickstart.sh trade TICKER OUTCOME_ID [amount]
#      Example: ./scripts/kalshi-demo-quickstart.sh trade KXNBATEAM-30 KXNBATEAM-30 1

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PMXT="$ROOT/pmxt"
CLI=(node "$PMXT/sdks/cli/bin/pmxt.js")
EXCHANGE=kalshi-demo

cd "$PMXT"

if [[ ! -d node_modules/pmxt-core ]]; then
  echo "Installing pmxt dependencies..."
  npm install
fi

if [[ ! -f core/dist/server/openapi.yaml ]]; then
  echo "Building pmxt-core..."
  npm run build --workspace=pmxt-core
fi

if [[ ! -f .env ]]; then
  echo "Missing pmxt/.env — copy from .env.example and add demo Kalshi credentials:"
  echo "  cp pmxt/.env.example pmxt/.env"
  echo "  # Set KALSHI_API_KEY and KALSHI_PRIVATE_KEY from demo.kalshi.com"
  exit 1
fi

has_kalshi_env() {
  grep -q '^KALSHI_API_KEY=.\+' .env 2>/dev/null && grep -q '^KALSHI_PRIVATE_KEY=.\+' .env
}

cmd="${1:-search}"

case "$cmd" in
  search)
    query="${2:-nba}"
    echo "=== Demo markets (query: $query) ==="
    "${CLI[@]}" "$EXCHANGE" markets --query "$query" --limit 5 --local --json
    echo
    echo "To paper trade: ./scripts/kalshi-demo-quickstart.sh trade <marketId> <outcomeId> [amount]"
    ;;
  balance)
    if ! has_kalshi_env; then
      echo "Add KALSHI_API_KEY and KALSHI_PRIVATE_KEY to pmxt/.env first."
      exit 1
    fi
    "${CLI[@]}" "$EXCHANGE" balance --local --json
    ;;
  trade)
    if ! has_kalshi_env; then
      echo "Add KALSHI_API_KEY and KALSHI_PRIVATE_KEY to pmxt/.env first."
      exit 1
    fi
    market_id="${2:?Usage: $0 trade MARKET_ID OUTCOME_ID [amount]}"
    outcome_id="${3:?Usage: $0 trade MARKET_ID OUTCOME_ID [amount]}"
    amount="${4:-1}"
    echo "=== Placing demo market buy: $amount contract(s) ==="
    "${CLI[@]}" "$EXCHANGE" order:create --local \
      --market-id "$market_id" \
      --outcome-id "$outcome_id" \
      --side buy \
      --type market \
      --amount "$amount" \
      --json
    echo
    echo "=== Balance after trade ==="
    "${CLI[@]}" "$EXCHANGE" balance --local --json
    ;;
  *)
    echo "Unknown command: $cmd"
    echo "Commands: search [query] | balance | trade MARKET_ID OUTCOME_ID [amount]"
    exit 1
    ;;
esac
