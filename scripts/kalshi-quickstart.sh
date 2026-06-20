#!/bin/bash
# Live Kalshi trading via PMXT (REAL MONEY)
#
# Credentials: production keys from kalshi.com in pmxt/.env
#   KALSHI_API_KEY=...
#   KALSHI_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."
#
# Usage:
#   ./scripts/kalshi-quickstart.sh event EVENT_ID     # fastest quote path
#   ./scripts/kalshi-quickstart.sh eval EVENT_ID [OUTCOME_LABEL] [amount]
#   ./scripts/kalshi-quickstart.sh orderbook OUTCOME_ID
#   ./scripts/kalshi-quickstart.sh search [query]
#   ./scripts/kalshi-quickstart.sh balance
#   ./scripts/kalshi-quickstart.sh positions
#   ./scripts/kalshi-quickstart.sh trade MARKET_ID OUTCOME_ID [amount]
#   ./scripts/kill-switch.sh status|on|off|stop
#
# Example:
#   ./scripts/kalshi-quickstart.sh event KXWCGAME-26JUN19USAAUS
#   ./scripts/kalshi-quickstart.sh trade KXNEWCITY-29 KXNEWCITY-29 1

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"
# shellcheck source=kill-switch-lib.sh
source "$ROOT/scripts/kill-switch-lib.sh"
# shellcheck source=trade-safety-lib.sh
source "$ROOT/scripts/trade-safety-lib.sh"
PMXT="$PMXT_DIR"
EXCHANGE=kalshi

cd "$PMXT"

if [[ ! -f core/dist/server/openapi.yaml ]]; then
  npm run build --workspace=pmxt-core
fi

if [[ ! -f .env ]]; then
  echo "Missing pmxt/.env — add KALSHI_API_KEY and KALSHI_PRIVATE_KEY from kalshi.com"
  exit 1
fi

has_kalshi_env() {
  grep -q '^KALSHI_API_KEY=.\+' .env 2>/dev/null && grep -q '^KALSHI_PRIVATE_KEY=.\+' .env
}

cmd="${1:-search}"

case "$cmd" in
  event)
    event_id="${2:?Usage: $0 event EVENT_ID}"
    echo "=== Live Kalshi event: $event_id ==="
    pmxt_cli "$EXCHANGE" event --event-id "$event_id" --local --json
    ;;
  eval)
    event_id="${2:?Usage: $0 eval EVENT_ID [OUTCOME_LABEL] [amount]}"
    label="${3:-}"
    amount="${4:-1}"
    args=(--event-id "$event_id" --amount "$amount" --balance)
    [[ -n "$label" ]] && args+=(--outcome-label "$label")
    "$ROOT/scripts/pmxt-eval.sh" "${args[@]}"
    ;;
  orderbook)
    outcome_id="${2:?Usage: $0 orderbook OUTCOME_ID}"
    pmxt_cli "$EXCHANGE" orderbook "$outcome_id" --local --json
    ;;
  search)
    query="${2:-fed}"
    echo "=== Live Kalshi markets (query: $query) ==="
    echo "Tip: use 'event EVENT_ID' from Kalshi page footer — faster than search."
    pmxt_cli "$EXCHANGE" markets --query "$query" --limit 5 --local --json
    echo
    echo "Trade: ./scripts/kalshi-quickstart.sh trade <marketId> <outcomeId> [amount]"
    ;;
  balance)
    if ! has_kalshi_env; then
      echo "Add KALSHI_API_KEY and KALSHI_PRIVATE_KEY to pmxt/.env"
      exit 1
    fi
    pmxt_cli "$EXCHANGE" balance --local --json
    ;;
  positions)
    if ! has_kalshi_env; then
      echo "Add KALSHI_API_KEY and KALSHI_PRIVATE_KEY to pmxt/.env"
      exit 1
    fi
    pmxt_cli "$EXCHANGE" positions --local --json
    ;;
  trade)
    if ! has_kalshi_env; then
      echo "Add KALSHI_API_KEY and KALSHI_PRIVATE_KEY to pmxt/.env"
      exit 1
    fi
    DRY_RUN=0
    market_id="${2:?Usage: $0 trade MARKET_ID OUTCOME_ID [amount] [--dry-run]}"
    outcome_id="${3:?Usage: $0 trade MARKET_ID OUTCOME_ID [amount] [--dry-run]}"
    amount="${4:-1}"
    if [[ "$amount" == "--dry-run" ]]; then
      amount=1
      DRY_RUN=1
    fi
    if [[ "${5:-}" == "--dry-run" ]]; then
      DRY_RUN=1
    fi
    trade_safety_require_live || exit 1
    trade_safety_check_amount "$amount" || exit 1
    if trade_safety_is_dry_run; then
      PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
from apps.bridge.trade_safety import format_dry_run_order
print(format_dry_run_order(
    venue='Kalshi', action='buy', market='$market_id', outcome='$outcome_id', amount='$amount'
))
"
      exit 0
    fi
    echo "WARNING: Live Kalshi — real money. Buying $amount contract(s)."
    pmxt_cli "$EXCHANGE" order:create --local \
      --market-id "$market_id" \
      --outcome-id "$outcome_id" \
      --side buy \
      --type market \
      --amount "$amount" \
      --json
    echo
    echo "=== Balance ==="
    pmxt_cli "$EXCHANGE" balance --local --json
    ;;
  *)
    echo "Commands: event EVENT_ID | eval EVENT_ID [LABEL] [amount] | orderbook OUTCOME_ID | search [query] | balance | positions | trade MARKET OUTCOME [amount]"
    exit 1
    ;;
esac
