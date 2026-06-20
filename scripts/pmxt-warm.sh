#!/usr/bin/env bash
# Warm the local PMXT sidecar before a trading session (~0.3s reads after this).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

"$ROOT/scripts/pmxt-server.sh" ensure >/dev/null

exchange="${1:-kalshi}"

warm_balance() {
  local ex="$1"
  local out=""
  if out="$(pmxt_cli "$ex" balance --local --json 2>&1)"; then
    echo "$out"
    return 0
  fi
  if echo "$out" | grep -qiE 'authentication|credentials|Initialize.*Exchange'; then
    echo "Sidecar missing venue credentials — restarting with pmxt/.env ..." >&2
    "$ROOT/scripts/pmxt-server.sh" restart >/dev/null
    sleep 1
    pmxt_cli "$ex" balance --local --json
    return 0
  fi
  echo "$out" >&2
  return 1
}

warm_balance "$exchange"
