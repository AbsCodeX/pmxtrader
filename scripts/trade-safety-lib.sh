#!/usr/bin/env bash
# Shared trade safety checks — source from live trade scripts.

_trade_safety_root() {
  if [[ -n "${PMXTRADER_ROOT:-}" ]]; then
    printf '%s\n' "$PMXTRADER_ROOT"
    return
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  printf '%s\n' "$here"
}

trade_safety_require_live() {
  # shellcheck source=kill-switch-lib.sh
  source "$(_trade_safety_root)/scripts/kill-switch-lib.sh"
  kill_switch_require_clear || return 1
  if [[ "${PMX_READ_ONLY:-}" =~ ^([1yY]|true|yes|TRUE|YES)$ ]]; then
    echo "READ-ONLY mode (PMX_READ_ONLY=1) — trades blocked." >&2
    return 1
  fi
  return 0
}

trade_safety_check_amount() {
  local amount="$1"
  local root
  root="$(_trade_safety_root)"
  PYTHONPATH="$root${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
import sys
sys.path.insert(0, sys.argv[1])
from apps.bridge.trade_safety import check_trade_amount
r = check_trade_amount(sys.argv[2])
if not r.ok:
    print(r.error, file=sys.stderr)
    raise SystemExit(1)
" "$root" "$amount"
}

trade_safety_is_dry_run() {
  [[ "${PMX_DRY_RUN:-}" =~ ^([1yY]|true|yes|TRUE|YES)$ || "${DRY_RUN:-}" == "1" ]]
}

if [[ "${BASH_SOURCE[0]:-}" == "${0:-}" ]]; then
  echo "Source this file: source scripts/trade-safety-lib.sh" >&2
  exit 1
fi
