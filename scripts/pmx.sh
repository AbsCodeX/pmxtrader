#!/usr/bin/env bash
# Plain-language shortcuts for pmxtrader.
#
#   ./pmx help
#   ./pmx balance
#   ./pmx quote EVENT_ID USA
#   ./pmx stop on "reason"
#   ./pmx panic          # cash out everything (asks PANIC)
#
# Say any alias — they map to the same action.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PMXTRADER_ROOT="$ROOT"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

usage() {
  cat <<'EOF'
pmx — plain-language shortcuts (Kalshi + Polymarket US + agents)

Start a session (sidecar + status + cheat sheet)
  session | launch | pmxt-start            Bootstrap in this shell
  terminal | pmxt-terminal                 Open new macOS Terminal + session
  dashboard | hub                          Open browser command center
  cockpit | tui | ui                       Visual trading terminal (Textual)

Kalshi (default balance/trade)
  balance | money | cash | bal          Kalshi available cash
  positions | pos | holdings            Kalshi open positions
  link URL [OUTCOME] [size]             Analyze Kalshi URL → quote
  quote EVENT [OUTCOME] [size]          Kalshi price + book + fill est
  trade MARKET OUTCOME [size]           Kalshi market buy (blocked if stopped)

Polymarket US (poly)
  poly balance | poly money             Poly US cash balance
  poly positions | poly pos             Poly US holdings
  poly quote SLUG [long|short]          Market + orderbook (+ balance)
  poly link URL [long|short]            Quote from polymarket.us URL
  poly markets [query]                  Search US markets
  poly trade SLUG [long|short] [qty] [price]  Market/limit buy (real money)
  poly sell SLUG [long|short] [qty] [price]   Market/limit sell
  poly close SLUG [long|short] [qty]    Market sell full position (or qty)
  poly watch book SLUG [long|short]       Stream live orderbook (active markets)
  poly watch trades SLUG [long|short]    Stream public trade tape
  poly history [SLUG] [--limit N]       Your fill history
  poly orders                           Open orders
  poly cancel ORDER_ID                  Cancel resting order
  poly cancel-all [SLUG]                Cancel all open orders (optional filter)

Shared
  status                                Kill switch + Kalshi/Poly US health
  event EVENT                           Raw event JSON
  compare slate SPORT | compare url URL Prediction Hunt odds
  brief SLUG                            Start a trade brief
  scout [grok|claude|openai|cursor|hermes]  Scout agent (default: grok)
  trader [openai|cursor|codex|hermes] BRIEF   Trader agent (default: openai)
  monitor EVENT [--label USA]           Poll prices → briefs/alerts/

Live session
  watch OUTCOME                         Stream orderbook
  trades OUTCOME                        Stream public trades
  fills [OUTCOME]                       Stream YOUR fills
  warm                                  Warm PMXT sidecar

Stop / safety
  stop | halt | pause [reason]          Block new trades (default: on)
  stop orders | cancel                  Halt + cancel resting orders
  panic | cashout | flatten             Halt + cancel + close all positions
  stop dry                              Preview panic (no execution)
  resume | go                           Allow trading again

Examples
  ./pmx session                       # start sidecar + show status (or: pmxt-start)
  ./pmx balance
  ./pmx link 'https://kalshi.com/markets/kxwcgame/world-cup-game' USA 1
  ./pmx poly balance
  ./pmx poly quote chiefs-super-bowl-lx long
  ./pmx poly trade chiefs-super-bowl-lx long 1
  ./pmx poly sell tec-f-wc-2026-07-19-winner-usa long 100
  ./pmx poly watch book tec-f-wc-2026-07-19-winner-usa long --max-messages 5
  ./pmx stop on "halftime"
  ./pmx panic
  ./pmx scout grok
  ./pmx trader openai briefs/active/my-game.md

Tip: npm run pmx -- balance   works too.
EOF
}

normalize_verb() {
  local v
  v="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  case "$v" in
    help|h|\?|commands) printf '%s\n' help ;;
    balance|money|cash|bal|wallet) printf '%s\n' balance ;;
    positions|pos|position|holdings|holds) printf '%s\n' positions ;;
    status|health|state) printf '%s\n' status ;;
    quote|price|eval|check|snapshot) printf '%s\n' quote ;;
    link|url|analyze|analyse) printf '%s\n' link ;;
    event|market|markets) printf '%s\n' event ;;
    watch|book|stream|orderbook) printf '%s\n' watch ;;
    trades|trade-tape|tape) printf '%s\n' trades ;;
    fills|fill|my-fills|myfills|my-fills) printf '%s\n' fills ;;
    monitor|poll|alert) printf '%s\n' monitor ;;
    warm|ready|prime) printf '%s\n' warm ;;
    session|launch|boot|pmxt-start|pmxtstart) printf '%s\n' session ;;
    terminal|pmxt-terminal|pmxtterminal) printf '%s\n' terminal ;;
    dashboard|hub|home) printf '%s\n' dashboard ;;
    cockpit|tui|ui|terminal-ui) printf '%s\n' cockpit ;;
    compare|ph|odds|hunt) printf '%s\n' compare ;;
    brief|plan|idea) printf '%s\n' brief ;;
    scout|research|look) printf '%s\n' scout ;;
    trader|execute|exec|trade-mode) printf '%s\n' trader ;;
    trade|buy|order) printf '%s\n' trade ;;
    stop|halt|kill|switch|pause) printf '%s\n' stop ;;
    panic|cashout|cash-out|flatten|exit|bail|get-out) printf '%s\n' panic ;;
    resume|unstop|unhalt|go|start) printf '%s\n' resume ;;
    poly|poly-us|polymarket-us|polymarketus) printf '%s\n' poly ;;
    *) printf '%s\n' "$v" ;;
  esac
}

cmd="${1:-help}"
shift || true
verb="$(normalize_verb "$cmd")"

case "$verb" in
  help)
    usage
    ;;
  balance)
    exec "$ROOT/scripts/kalshi-quickstart.sh" balance
    ;;
  positions)
    exec "$ROOT/scripts/kalshi-quickstart.sh" positions
    ;;
  status)
    "$ROOT/scripts/kill-switch.sh" status
    echo
    echo "Kalshi:"
    pmxt_cli kalshi balance --local --json 2>/dev/null | python3 -c "
import json,sys
try:
  b=json.load(sys.stdin)[0]
  print(f\"  available: {b.get('available')}  total: {b.get('total')}\")
except Exception:
  print('  (run ./pmx warm if sidecar cold)')
" || true
    if grep -qE '^POLYMARKET_US_KEY_ID=.+[^[:space:]]' "$PMXT_DIR/.env" 2>/dev/null \
      && grep -qE '^POLYMARKET_US_SECRET_KEY=.+[^[:space:]]' "$PMXT_DIR/.env" 2>/dev/null; then
      echo
      echo "Polymarket US:"
      pmxt_cli polymarket_us balance --local --json 2>/dev/null | python3 -c "
import json,sys
try:
  rows=json.load(sys.stdin)
  if isinstance(rows,list) and rows:
    b=rows[0]
    print(f\"  available: {b.get('available')}  total: {b.get('total')}  currency: {b.get('currency','USD')}\")
  else:
    print('  (no balance data)')
except Exception as e:
  print('  (balance unavailable)')
" || true
    fi
    ;;
  quote)
    event_id="${1:?Usage: pmx quote EVENT_ID [OUTCOME] [size]}"
    shift
    label=""
    amount="1"
    if [[ $# -gt 0 && "$1" != --* ]]; then
      label="$1"
      shift
    fi
    if [[ $# -gt 0 && "$1" != --* ]]; then
      amount="$1"
      shift
    fi
    args=(--event-id "$event_id" --amount "$amount" --balance)
    [[ -n "$label" ]] && args+=(--outcome-label "$label")
    exec "$ROOT/scripts/pmxt-eval.sh" "${args[@]}" "$@"
    ;;
  link)
    url="${1:?Usage: pmx link URL [OUTCOME] [size]}"
    shift
    exec "$ROOT/scripts/pmx-link.sh" "$url" "$@"
    ;;
  event)
    event_id="${1:?Usage: pmx event EVENT_ID}"
    exec "$ROOT/scripts/kalshi-quickstart.sh" event "$event_id"
    ;;
  watch)
    outcome_id="${1:?Usage: pmx watch OUTCOME_ID}"
    shift
    exec "$ROOT/scripts/pmxt-watch.sh" orderbook "$outcome_id" "$@"
    ;;
  trades)
    outcome_id="${1:?Usage: pmx trades OUTCOME_ID}"
    shift
    exec "$ROOT/scripts/pmxt-watch.sh" trades "$outcome_id" "$@"
    ;;
  fills)
    args=()
    if [[ $# -gt 0 && "$1" != --* ]]; then
      args+=(--market-ticker "$1")
      shift
    fi
    exec "$ROOT/scripts/pmxt-watch-fills.sh" "${args[@]}" "$@"
    ;;
  monitor)
    event_id="${1:?Usage: pmx monitor EVENT_ID [--label USA] [--interval 30]}"
    shift
    label=""
    extra=()
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --label|-l) label="$2"; shift 2 ;;
        --interval|-i) extra+=(--interval "$2"); shift 2 ;;
        --once) extra+=(--once); shift ;;
        *) extra+=("$1"); shift ;;
      esac
    done
    args=(--event-id "$event_id" "${extra[@]}")
    [[ -n "$label" ]] && args+=(--outcome-label "$label")
    exec "$ROOT/scripts/pmxt-monitor.sh" "${args[@]}"
    ;;
  warm)
    exec "$ROOT/scripts/pmxt-warm.sh"
    ;;
  session)
    exec "$ROOT/scripts/pmxt-start.sh" "$@"
    ;;
  terminal)
    exec "$ROOT/scripts/pmxt-terminal.sh" "$@"
    ;;
  dashboard)
    exec "$ROOT/scripts/pmxt-dashboard.sh" start "$@"
    ;;
  cockpit)
    exec "$ROOT/scripts/pmxt-cockpit.sh" "$@"
    ;;
  compare)
    sub="${1:-slate}"
    shift || true
    sub="$(printf '%s' "$sub" | tr '[:upper:]' '[:lower:]')"
    case "$sub" in
      slate|sport|sports) exec "$ROOT/scripts/ph-sports-compare.sh" slate "${1:-nba}" ;;
      url|link) exec "$ROOT/scripts/ph-sports-compare.sh" url "${1:?Usage: pmx compare url URL}" ;;
      *) exec "$ROOT/scripts/ph-sports-compare.sh" "$sub" "$@" ;;
    esac
    ;;
  brief)
    slug="${1:?Usage: pmx brief SLUG}"
    exec "$ROOT/scripts/new-brief.sh" "$slug"
    ;;
  scout)
    provider="grok"
    for p in cursor grok claude openai hermes codex; do
      if [[ "${1:-}" == "$p" ]]; then
        provider="$p"
        shift
        break
      fi
    done
    exec "$ROOT/scripts/agent-run.sh" scout "$provider" "$@"
    ;;
  trader)
    provider="openai"
    if [[ ! -f "${HERMES_ENV:-$HOME/.hermes/.env}" ]] \
      || ! grep -qE '^OPENAI_API_KEY=.' "${HERMES_ENV:-$HOME/.hermes/.env}" 2>/dev/null; then
      provider="cursor"
    fi
    for p in cursor openai codex hermes grok claude; do
      if [[ "${1:-}" == "$p" ]]; then
        provider="$p"
        shift
        break
      fi
    done
    exec "$ROOT/scripts/agent-run.sh" trader "$provider" "$@"
    ;;
  trade)
    exec "$ROOT/scripts/kalshi-quickstart.sh" trade "$@"
    ;;
  stop)
    if [[ $# -eq 0 ]]; then
      exec "$ROOT/scripts/kill-switch.sh" on "manual halt"
    fi
    sub="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
    case "$sub" in
      on|engage|halt|pause)
        shift
        reason="${*:-manual halt}"
        exec "$ROOT/scripts/kill-switch.sh" on "$reason"
        ;;
      off|disengage)
        exec "$ROOT/scripts/kill-switch.sh" off
        ;;
      status)
        exec "$ROOT/scripts/kill-switch.sh" status
        ;;
      dry|preview)
        exec "$ROOT/scripts/kill-switch.sh" stop --dry-run --cash-out
        ;;
      orders|cancel)
        shift
        exec "$ROOT/scripts/kill-switch.sh" stop "$@"
        ;;
      *)
        exec "$ROOT/scripts/kill-switch.sh" on "$*"
        ;;
    esac
    ;;
  panic)
    exec "$ROOT/scripts/kill-switch.sh" stop --cash-out "$@"
    ;;
  resume)
    exec "$ROOT/scripts/kill-switch.sh" off
    ;;
  poly)
    sub="${1:-help}"
    shift || true
    sub="$(printf '%s' "$sub" | tr '[:upper:]' '[:lower:]')"
    exec "$ROOT/scripts/polymarket-us-quickstart.sh" "$sub" "$@"
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo "Run: ./pmx help" >&2
    exit 1
    ;;
esac
