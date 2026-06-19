#!/usr/bin/env bash
# Bootstrap a live trading session: sidecar + env + status + cheat sheet.
#
# Usage:
#   ./scripts/pmxt-start.sh
#   pmxt-start                    # if sourced pmx-aliases.sh or direnv
#   ./pmx session
#
# Options:
#   --quiet          Less output (status + ready line only)
#   --no-warm        Skip balance probe (sidecar ensure only)
#   --check-agents   Also run ./scripts/check-providers.sh
#   --no-cockpit     Skip launching visual cockpit (stay in shell)
#   --shell          Same as --no-cockpit

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

QUIET=false
NO_WARM=false
CHECK_AGENTS=false
NO_COCKPIT=false

for arg in "$@"; do
  case "$arg" in
    --quiet|-q) QUIET=true ;;
    --no-warm) NO_WARM=true ;;
    --check-agents) CHECK_AGENTS=true ;;
    --no-cockpit|--shell) NO_COCKPIT=true ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
  esac
done

say() {
  [[ "$QUIET" == true ]] && return 0
  printf '%s\n' "$*"
}

say "=== pmxtrader session start ==="
say "Root: $PMXTRADER_ROOT"
say

say "Starting PMXT sidecar (loads pmxt/.env)..."
"$ROOT/scripts/pmxt-server.sh" ensure

if [[ "$NO_WARM" == false ]]; then
  say
  say "Warming venues..."
  if grep -qE '^KALSHI_API_KEY=.+[^[:space:]]' "$PMXT_DIR/.env" 2>/dev/null; then
    if pmxt_cli kalshi balance --local --json >/dev/null 2>&1; then
      say "  Kalshi: OK"
    else
      say "  Kalshi: sidecar up but balance failed (check keys)"
    fi
  else
    say "  Kalshi: keys not set (optional)"
  fi
  if grep -qE '^POLYMARKET_US_KEY_ID=.+[^[:space:]]' "$PMXT_DIR/.env" 2>/dev/null; then
    if pmxt_cli polymarket_us balance --local --json >/dev/null 2>&1; then
      say "  Polymarket US: OK"
    else
      say "  Polymarket US: sidecar up but balance failed (check keys)"
    fi
  else
    say "  Polymarket US: keys not set (optional)"
  fi
fi

say
"$ROOT/pmx" status

if [[ "$CHECK_AGENTS" == true ]]; then
  say
  "$ROOT/scripts/check-providers.sh" 2>/dev/null || true
fi

if [[ "$QUIET" == false ]]; then
  cat <<EOF

=== Session ready ===

Quick commands:
  ./pmx status
  ./pmx link 'KALSHI_URL' USA 1
  ./pmx poly quote SLUG long
  ./pmx scout grok
  ./pmx help

Full reference: docs/commands.md
Stop trading:     ./pmx stop on "reason"
Emergency:        ./pmx panic

EOF
fi

say "Ready."

if [[ "$NO_COCKPIT" == false ]] && [[ -x "$ROOT/.venv-cockpit/bin/python" || -x "$ROOT/scripts/pmxt-cockpit.sh" ]]; then
  exec "$ROOT/scripts/pmxt-cockpit.sh"
elif [[ "$NO_COCKPIT" == false ]]; then
  say "Tip: pmx cockpit  (creates .venv-cockpit on first run)"
fi
