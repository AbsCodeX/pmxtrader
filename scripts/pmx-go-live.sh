#!/usr/bin/env bash
# Enable live trading: disengage kill switch + mark session as live (clears read-only default).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=kill-switch-lib.sh
source "$ROOT/scripts/kill-switch-lib.sh"

"$ROOT/scripts/kill-switch.sh" off
touch "$ROOT/.pmx-live"

max="${PMX_MAX_TRADE_CONTRACTS:-10}"
echo "Live trading enabled for this repo session."
echo "  Kill switch: OFF"
echo "  Read-only:   OFF (.pmx-live set — removed on next ./pmx session)"
echo "  Max size:    ${max} contracts per order (PMX_MAX_TRADE_CONTRACTS)"
echo
echo "To block new trades: ./pmx stop on \"reason\""
echo "To return to read-only: rm .pmx-live && export PMX_READ_ONLY=1"
