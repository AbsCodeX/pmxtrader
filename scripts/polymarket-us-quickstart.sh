#!/usr/bin/env bash
# Live Polymarket US trading via PMXT (REAL MONEY)
#
# Credentials in pmxt/.env:
#   POLYMARKET_US_KEY_ID=...
#   POLYMARKET_US_SECRET_KEY=...
#
# Keys: https://polymarket.us/developer
# Docs: https://docs.polymarket.us/getting-started/welcome
#
# Usage:
#   ./scripts/polymarket-us-quickstart.sh balance
#   ./scripts/polymarket-us-quickstart.sh positions
#   ./scripts/polymarket-us-quickstart.sh markets [query]
#   ./scripts/polymarket-us-quickstart.sh quote SLUG [long|short]
#   ./scripts/polymarket-us-quickstart.sh link URL [long|short] [qty]
#   ./scripts/polymarket-us-quickstart.sh trade SLUG [long|short] [qty] [price]
#   ./scripts/polymarket-us-quickstart.sh orders
#   ./scripts/polymarket-us-quickstart.sh cancel ORDER_ID
#
# Examples:
#   ./scripts/polymarket-us-quickstart.sh quote chiefs-super-bowl-lx long
#   ./scripts/polymarket-us-quickstart.sh trade chiefs-super-bowl-lx long 1
#   ./scripts/polymarket-us-quickstart.sh trade chiefs-super-bowl-lx long 10 0.55

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"
# shellcheck source=kill-switch-lib.sh
source "$ROOT/scripts/kill-switch-lib.sh"

EXCHANGE=polymarket_us
ENV_FILE="$PMXT_DIR/.env"

if [[ ! -f "$PMXT_DIR/core/dist/server/openapi.yaml" ]]; then
  (cd "$PMXT_DIR" && npm run build --workspace=pmxt-core)
fi

has_poly_us_env() {
  [[ -f "$ENV_FILE" ]] \
    && grep -qE '^POLYMARKET_US_KEY_ID=.+[^[:space:]]' "$ENV_FILE" \
    && grep -qE '^POLYMARKET_US_SECRET_KEY=.+[^[:space:]]' "$ENV_FILE"
}

require_poly_us_env() {
  if ! has_poly_us_env; then
    echo "Missing Polymarket US keys in pmxt/.env" >&2
    echo "  POLYMARKET_US_KEY_ID=..." >&2
    echo "  POLYMARKET_US_SECRET_KEY=..." >&2
    echo "Get keys: https://polymarket.us/developer" >&2
    echo "Setup: pmxt/core/docs/SETUP_POLYMARKET_US.md" >&2
    exit 1
  fi
}

normalize_side() {
  local s
  s="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  case "$s" in
    long|yes|y|buy-long|l) printf '%s\n' long ;;
    short|no|n|sell-short|s) printf '%s\n' short ;;
    *) printf '%s\n' "$s" ;;
  esac
}

outcome_id_for() {
  local slug side
  slug="$1"
  side="$(normalize_side "$2")"
  printf '%s:%s\n' "$slug" "$side"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h)
    sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'
    ;;
  balance|bal|money)
    require_poly_us_env
    echo "=== Polymarket US balance ==="
    pmxt_cli "$EXCHANGE" balance --local --json
    ;;
  positions|pos|holdings)
    require_poly_us_env
    echo "=== Polymarket US positions ==="
    pmxt_cli "$EXCHANGE" positions --local --json
    ;;
  markets|search|find)
    query="${1:-}"
    echo "=== Polymarket US markets${query:+ (query: $query)} ==="
    if [[ -n "$query" ]]; then
      pmxt_cli "$EXCHANGE" markets --query "$query" --limit 10 --local --json
    else
      pmxt_cli "$EXCHANGE" markets --limit 10 --local --json
    fi
    ;;
  quote|price|book)
    slug="${1:?Usage: $0 quote SLUG [long|short]}"
    side="${2:-long}"
    side="$(normalize_side "$side")"
    oid="$(outcome_id_for "$slug" "$side")"
    echo "=== Polymarket US quote: $slug ($side) ==="
    pmxt_cli "$EXCHANGE" markets --slug "$slug" --local --json 2>/dev/null || true
    echo
    pmxt_cli "$EXCHANGE" orderbook "$oid" --local --json
    if has_poly_us_env; then
      echo
      echo "=== Balance ==="
      pmxt_cli "$EXCHANGE" balance --local --json
    fi
    echo
    echo "Trade: ./pmx poly trade $slug $side 1"
    echo "       ./pmx poly trade $slug $side 10 0.55   # limit @ 0.55"
    ;;
  link|url)
    exec python3 "$ROOT/scripts/polymarket-us-link.py" "$@"
    ;;
  trade|buy|order)
    require_poly_us_env
    kill_switch_require_clear || exit 1
    slug="${1:?Usage: $0 trade SLUG [long|short] [qty] [limit_price]}"
    side="${2:-long}"
    qty="${3:-1}"
    limit_price="${4:-}"
    side="$(normalize_side "$side")"
    oid="$(outcome_id_for "$slug" "$side")"

    if [[ -n "$limit_price" ]]; then
      echo "WARNING: Live Polymarket US — limit buy $qty @ $limit_price on $slug ($side)."
      pmxt_cli "$EXCHANGE" order:create --local \
        --market-id "$slug" \
        --outcome-id "$oid" \
        --side buy \
        --type limit \
        --price "$limit_price" \
        --amount "$qty" \
        --json
    else
      echo "WARNING: Live Polymarket US — market buy $qty on $slug ($side)."
      pmxt_cli "$EXCHANGE" order:create --local \
        --market-id "$slug" \
        --outcome-id "$oid" \
        --side buy \
        --type market \
        --amount "$qty" \
        --json
    fi
    echo
    echo "=== Balance ==="
    pmxt_cli "$EXCHANGE" balance --local --json
    ;;
  orders|open-orders)
    require_poly_us_env
    pmxt orders:open --exchange "$EXCHANGE" --local --json
    ;;
  cancel)
    require_poly_us_env
    order_id="${1:?Usage: $0 cancel ORDER_ID}"
    pmxt order:cancel "$order_id" --exchange "$EXCHANGE" --local --json
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Run: $0 help" >&2
    exit 1
    ;;
esac
