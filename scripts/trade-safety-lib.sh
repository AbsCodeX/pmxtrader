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
  if [[ "${PMX_READ_ONLY:-1}" =~ ^([1yY]|true|yes|TRUE|YES)$ ]]; then
    echo "READ-ONLY mode (PMX_READ_ONLY=1) — trades blocked." >&2
    echo "Run: ./pmx go-live   (or ./pmx resume)" >&2
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

trade_safety_assume_yes() {
  for arg in "$@"; do
    if [[ "$arg" == "--yes" || "$arg" == "-y" ]]; then
      return 0
    fi
  done
  return 1
}

trade_safety_confirm_live() {
  local preview="$1"
  shift || true
  if trade_safety_is_dry_run; then
    return 0
  fi
  if trade_safety_assume_yes "$@"; then
    return 0
  fi
  local root
  root="$(_trade_safety_root)"
  if ! PYTHONPATH="$root${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
import sys
sys.path.insert(0, sys.argv[1])
from apps.bridge.trade_safety import trade_confirm_required
raise SystemExit(0 if trade_confirm_required() else 1)
" "$root"; then
    return 0
  fi
  echo "=== Live trade preview ==="
  if [[ -n "$preview" ]]; then
    printf '%s\n' "$preview"
  fi
  echo
  read -r -p "Type YES or y to confirm live order: " answer
  PYTHONPATH="$root${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
import sys
sys.path.insert(0, sys.argv[1])
from apps.bridge.trade_safety import confirm_trade_allowed
raise SystemExit(0 if confirm_trade_allowed(sys.argv[2]) else 1)
" "$root" "$answer"
}

trade_safety_audit_log() {
  local venue="$1" command="$2" market="$3" outcome="$4" size="$5" stdout="$6"
  if trade_safety_is_dry_run; then
    return 0
  fi
  local root
  root="$(_trade_safety_root)"
  PYTHONPATH="$root${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from apps.bridge.trade_audit import append_trade_log
append_trade_log(
    Path(sys.argv[1]),
    venue=sys.argv[2],
    command=sys.argv[3],
    market=sys.argv[4],
    outcome=sys.argv[5],
    size=sys.argv[6],
    stdout=sys.argv[7] if len(sys.argv) > 7 else '',
)
" "$root" "$venue" "$command" "$market" "$outcome" "$size" "$stdout"
}

if [[ "${BASH_SOURCE[0]:-}" == "${0:-}" ]]; then
  echo "Source this file: source scripts/trade-safety-lib.sh" >&2
  exit 1
fi
