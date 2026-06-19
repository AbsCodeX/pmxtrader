#!/usr/bin/env bash
# Trading kill switch + emergency stop for live Kalshi.
#
# Kill switch (file sentinel — works even if PMXT/agents are hung):
#   ./scripts/kill-switch.sh status
#   ./scripts/kill-switch.sh on "halftime — no new trades"
#   ./scripts/kill-switch.sh off
#
# Emergency stop:
#   ./scripts/kill-switch.sh stop              # engage + cancel resting orders
#   ./scripts/kill-switch.sh stop --cash-out   # + market-close all positions
#   ./scripts/kill-switch.sh stop --dry-run    # preview only
#
# Override path: KILL_SWITCH_FILE=/path/to/file

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PMXTRADER_ROOT="$ROOT"
# shellcheck source=kill-switch-lib.sh
source "$ROOT/scripts/kill-switch-lib.sh"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

usage() {
  cat <<EOF
Usage:
  $0 status
  $0 on [reason]          Engage kill switch (block new trades)
  $0 off                  Disengage kill switch
  $0 stop [--cash-out] [--dry-run] [--yes]

stop:
  Always engages the kill switch.
  Default: cancel all resting Kalshi orders.
  --cash-out: also submit reduce-only market orders to flatten positions.
  --dry-run: show actions without executing.
  --yes: skip confirmation prompt (stop --cash-out only).

File: $(kill_switch_path)
EOF
}

confirm_panic() {
  if [[ "${1:-}" == "--yes" ]]; then
    return 0
  fi
  echo "WARNING: Live Kalshi — real money."
  echo "This will:"
  echo "  1. Engage the kill switch (block new trades)"
  echo "  2. Cancel all resting orders"
  if [[ "$CASH_OUT" -eq 1 ]]; then
    echo "  3. Market-close ALL open positions (reduce-only)"
  fi
  echo
  read -r -p "Type PANIC to confirm: " answer
  [[ "$answer" == "PANIC" ]]
}

cmd="${1:-status}"
shift || true

case "$cmd" in
  status)
    kill_switch_status_line
    ;;
  on|engage|halt)
    reason="${*:-manual halt}"
    kill_switch_engage "$reason"
    echo "Kill switch ON — $(kill_switch_reason)"
    ;;
  off|disengage|resume)
    kill_switch_disengage
    echo "Kill switch OFF"
    ;;
  stop|panic|emergency)
    CASH_OUT=0
    DRY_RUN=0
    ASSUME_YES=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --cash-out|--cashout) CASH_OUT=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        --yes|-y) ASSUME_YES="--yes"; shift ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
      esac
    done

    if [[ "$CASH_OUT" -eq 1 && "$DRY_RUN" -eq 0 ]]; then
      confirm_panic "$ASSUME_YES" || {
        echo "Aborted."
        exit 1
      }
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "[dry-run] Would engage kill switch"
    else
      kill_switch_engage "emergency stop $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "Kill switch ON"
    fi

    EXIT_ARGS=(--cancel-orders)
    [[ "$CASH_OUT" -eq 1 ]] && EXIT_ARGS+=(--close-positions)
    [[ "$DRY_RUN" -eq 1 ]] && EXIT_ARGS+=(--dry-run)

    python3 "$ROOT/scripts/kalshi-emergency-exit.py" "${EXIT_ARGS[@]}"
    ;;
  *)
    usage
    exit 1
    ;;
esac
