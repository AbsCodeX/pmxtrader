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
#   ./scripts/polymarket-us-quickstart.sh link URL [long|short]
#   ./scripts/polymarket-us-quickstart.sh trade SLUG [long|short] [qty] [price]
#   ./scripts/polymarket-us-quickstart.sh sell SLUG [long|short] [qty] [price]
#   ./scripts/polymarket-us-quickstart.sh close SLUG [long|short] [qty]
#   ./scripts/polymarket-us-quickstart.sh watch book SLUG [long|short] [--max-messages N]
#   ./scripts/polymarket-us-quickstart.sh watch trades SLUG [long|short] [--max-messages N]
#   ./scripts/polymarket-us-quickstart.sh history [SLUG] [--limit N]
#   ./scripts/polymarket-us-quickstart.sh orders
#   ./scripts/polymarket-us-quickstart.sh cancel ORDER_ID
#   ./scripts/polymarket-us-quickstart.sh cancel-all [SLUG]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"
# shellcheck source=kill-switch-lib.sh
source "$ROOT/scripts/kill-switch-lib.sh"
# shellcheck source=trade-safety-lib.sh
source "$ROOT/scripts/trade-safety-lib.sh"

EXCHANGE=polymarket_us
ENV_FILE="$PMXT_DIR/.env"

if [[ ! -f "$PMXT_DIR/core/dist/server/openapi.yaml" ]]; then
  (cd "$PMXT_DIR" && npm run build --workspace=pmxt-core)
fi

ensure_sidecar() {
  "$ROOT/scripts/pmxt-server.sh" ensure >/dev/null 2>&1 || true
}

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
  ensure_sidecar
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

place_order() {
  local order_side=$1 slug=$2 outcome_side=$3 qty=$4 limit_price=$5
  local oid action preview order_stdout
  oid="$(outcome_id_for "$slug" "$outcome_side")"
  outcome_side="$(normalize_side "$outcome_side")"

  trade_safety_check_amount "$qty" || return 1

  if [[ "$order_side" == "buy" ]]; then
    action="buy"
  else
    action="sell"
  fi

  if trade_safety_is_dry_run; then
    if [[ -n "$limit_price" ]]; then
      echo "[dry-run] Polymarket US: would ${action} ${qty} on ${slug} (${outcome_side}) @ limit ${limit_price}"
    else
      echo "[dry-run] Polymarket US: would ${action} ${qty} on ${slug} (${outcome_side}) @ market"
    fi
    return 0
  fi

  preview="$(PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
from apps.bridge.trade_safety import format_dry_run_order
print(format_dry_run_order(
    venue='Polymarket US',
    action='$action',
    market='$slug',
    outcome='$outcome_side',
    amount='$qty',
    order_type='limit' if '$limit_price' else 'market',
    limit_price='$limit_price' or None,
))
")"
  trade_safety_confirm_live "$preview" "${POLY_TRADE_EXTRA[@]}" || {
    echo "Aborted." >&2
    return 1
  }

  if [[ -n "$limit_price" ]]; then
    echo "WARNING: Live Polymarket US — limit $action $qty @ $limit_price on $slug ($outcome_side)."
    order_stdout="$(pmxt_cli order:create --local \
      --exchange "$EXCHANGE" \
      --market-id "$slug" \
      --outcome-id "$oid" \
      --side "$order_side" \
      --type limit \
      --price "$limit_price" \
      --amount "$qty" \
      --json 2>&1)" || {
      echo "$order_stdout"
      return 1
    }
  else
    echo "WARNING: Live Polymarket US — market $action $qty on $slug ($outcome_side)."
    order_stdout="$(pmxt_cli order:create --local \
      --exchange "$EXCHANGE" \
      --market-id "$slug" \
      --outcome-id "$oid" \
      --side "$order_side" \
      --type market \
      --amount "$qty" \
      --json 2>&1)" || {
      echo "$order_stdout"
      return 1
    }
  fi
  echo "$order_stdout"
  trade_safety_audit_log polymarket_us "$action" "$slug" "$outcome_side" "$qty" "$order_stdout"
}

position_size_for() {
  local slug=$1 outcome_side=$2
  outcome_side="$(normalize_side "$outcome_side")"
  pmxt_cli "$EXCHANGE" positions --local --json | python3 -c "
import json, sys
slug, side = sys.argv[1], sys.argv[2]
positions = json.load(sys.stdin)
for p in positions:
    if p.get('marketId') != slug:
        continue
    oid = p.get('outcomeId', '')
    label = p.get('outcomeLabel', '')
    if oid.endswith(':' + side) or label == side:
        size = p.get('size', 0)
        print(int(size) if float(size).is_integer() else size)
        sys.exit(0)
print('', end='')
" "$slug" "$outcome_side"
}

_poly_flag_dry_run() {
  DRY_RUN=0
  POLY_TRADE_EXTRA=()
  for arg in "$@"; do
    if [[ "$arg" == "--dry-run" ]]; then
      DRY_RUN=1
    else
      POLY_TRADE_EXTRA+=("$arg")
    fi
  done
  export DRY_RUN
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h)
    sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'
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
    ensure_sidecar
    query="${1:-}"
    echo "=== Polymarket US markets${query:+ (query: $query)} ==="
    if [[ -n "$query" ]]; then
      pmxt_cli "$EXCHANGE" markets --query "$query" --limit 10 --local --json
    else
      pmxt_cli "$EXCHANGE" markets --limit 10 --local --json
    fi
    ;;
  quote|price|book)
    ensure_sidecar
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
    echo "Sell:  ./pmx poly sell $slug $side 100"
    echo "Watch: ./pmx poly watch book $slug $side"
    ;;
  link|url)
    exec python3 "$ROOT/scripts/polymarket-us-link.py" "$@"
    ;;
  trade|buy)
    require_poly_us_env
    _poly_flag_dry_run "$@"
    trade_safety_preflight_trade || exit 1
    trade_safety_require_live || exit 1
    slug="${1:?Usage: $0 trade SLUG [long|short] [qty] [limit_price] [--dry-run]}"
    side="${2:-long}"
    qty="${3:-1}"
    limit_price="${4:-}"
    if [[ "$qty" == "--dry-run" ]]; then qty=1; fi
    if [[ "$limit_price" == "--dry-run" ]]; then limit_price=""; fi
    place_order buy "$slug" "$side" "$qty" "$limit_price"
    if ! trade_safety_is_dry_run; then
      echo
      echo "=== Balance ==="
      pmxt_cli "$EXCHANGE" balance --local --json
    fi
    ;;
  sell)
    require_poly_us_env
    _poly_flag_dry_run "$@"
    trade_safety_preflight_trade || exit 1
    trade_safety_require_live || exit 1
    slug="${1:?Usage: $0 sell SLUG [long|short] [qty] [limit_price] [--dry-run]}"
    side="${2:-long}"
    qty="${3:-1}"
    limit_price="${4:-}"
    if [[ "$qty" == "--dry-run" ]]; then qty=1; fi
    if [[ "$limit_price" == "--dry-run" ]]; then limit_price=""; fi
    place_order sell "$slug" "$side" "$qty" "$limit_price"
    if ! trade_safety_is_dry_run; then
      echo
      echo "=== Balance ==="
      pmxt_cli "$EXCHANGE" balance --local --json
    fi
    ;;
  close|flatten|exit)
    require_poly_us_env
    _poly_flag_dry_run "$@"
    trade_safety_preflight_trade || exit 1
    trade_safety_require_live || exit 1
    slug="${1:?Usage: $0 close SLUG [long|short] [qty] [--dry-run]}"
    side="${2:-long}"
    qty="${3:-}"
    if [[ "$qty" == "--dry-run" ]]; then qty=""; fi
    if [[ -z "$qty" ]]; then
      qty="$(position_size_for "$slug" "$side")"
      if [[ -z "$qty" || "$qty" == "0" ]]; then
        echo "No open position for $slug ($side)." >&2
        exit 1
      fi
      echo "Closing full position: $qty contracts on $slug ($side)"
    fi
    place_order sell "$slug" "$side" "$qty" ""
    if ! trade_safety_is_dry_run; then
      echo
      echo "=== Balance ==="
      pmxt_cli "$EXCHANGE" balance --local --json
    fi
    ;;
  watch|stream)
    require_poly_us_env
    kind="${1:?Usage: $0 watch book|trades SLUG [long|short] [--max-messages N]}"
    shift
    case "$kind" in
      book|orderbook|ob) WATCH_CMD="watch:orderBook" ;;
      trades|trade|tape) WATCH_CMD="watch:trades" ;;
      *)
        echo "Unknown watch type: $kind (use book or trades)" >&2
        exit 1
        ;;
    esac
    slug="${1:?Usage: $0 watch $kind SLUG [long|short]}"
    shift
    side="long"
    if [[ $# -gt 0 && "$1" != --* ]]; then
      side="$1"
      shift
    fi
    side="$(normalize_side "$side")"
    oid="$(outcome_id_for "$slug" "$side")"

    MAX_MESSAGES=""
    TIMEOUT_MS=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --max-messages) MAX_MESSAGES="$2"; shift 2 ;;
        --timeout-ms) TIMEOUT_MS="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
      esac
    done

    echo "=== Polymarket US watch ($kind): $slug ($side) ==="
    echo "Tip: use active markets — resolved slugs may not stream."
    ARGS=("$WATCH_CMD" "$EXCHANGE" "$oid" --local)
    [[ -n "$MAX_MESSAGES" ]] && ARGS+=(--max-messages "$MAX_MESSAGES")
    [[ -n "$TIMEOUT_MS" ]] && ARGS+=(--timeout-ms "$TIMEOUT_MS")
    pmxt_cli "${ARGS[@]}"
    ;;
  history|fills|my-trades|mytrades)
    require_poly_us_env
    slug=""
    limit=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit) limit="$2"; shift 2 ;;
        --*) echo "Unknown option: $1" >&2; exit 1 ;;
        *)
          if [[ -z "$slug" ]]; then
            slug="$1"
          else
            echo "Unexpected argument: $1" >&2
            exit 1
          fi
          shift
          ;;
      esac
    done
    echo "=== Polymarket US trade history${slug:+ ($slug)} ==="
    ARGS=(orders:trades --exchange "$EXCHANGE" --local --json)
    [[ -n "$slug" ]] && ARGS+=(--market-id "$slug")
    [[ -n "$limit" ]] && ARGS+=(--limit "$limit")
    pmxt_cli "${ARGS[@]}"
    ;;
  orders|open-orders)
    require_poly_us_env
    pmxt_cli orders:open --exchange "$EXCHANGE" --local --json
    ;;
  cancel)
    require_poly_us_env
    order_id="${1:?Usage: $0 cancel ORDER_ID}"
    pmxt_cli order:cancel "$order_id" --exchange "$EXCHANGE" --local --json
    ;;
  cancel-all|cancelall|cancel-all-orders)
    require_poly_us_env
    slug="${1:-}"
    echo "=== Canceling open Polymarket US orders${slug:+ for $slug} ==="
    count=0
    while IFS= read -r order_id; do
      [[ -z "$order_id" ]] && continue
      echo "Canceling $order_id"
      pmxt_cli order:cancel "$order_id" --exchange "$EXCHANGE" --local --json
      count=$((count + 1))
    done < <(
      pmxt_cli orders:open --exchange "$EXCHANGE" --local --json | python3 -c "
import json, sys
slug = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
orders = json.load(sys.stdin)
for o in orders:
    if slug and o.get('marketId') != slug:
        continue
    oid = o.get('id')
    if oid:
        print(oid)
" "$slug"
    )
    if [[ "$count" -eq 0 ]]; then
      echo "No open orders to cancel."
    else
      echo "Canceled $count order(s)."
    fi
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Run: $0 help" >&2
    exit 1
    ;;
esac
