#!/usr/bin/env bash
# Shared kill-switch helpers. Source from other scripts — do not execute directly.

_kill_switch_root() {
  if [[ -n "${PMXTRADER_ROOT:-}" ]]; then
    printf '%s\n' "$PMXTRADER_ROOT"
    return
  fi
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  printf '%s\n' "$here"
}

kill_switch_path() {
  local root
  root="$(_kill_switch_root)"
  printf '%s\n' "${KILL_SWITCH_FILE:-$root/KILL_SWITCH}"
}

kill_switch_engaged() {
  [[ -f "$(kill_switch_path)" ]]
}

kill_switch_reason() {
  local path
  path="$(kill_switch_path)"
  if [[ ! -f "$path" ]]; then
    return 1
  fi
  local reason
  reason="$(tr -d '\0' < "$path" | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  if [[ -n "$reason" ]]; then
    printf '%s\n' "$reason"
  else
    printf '%s\n' "engaged (no reason given)"
  fi
}

kill_switch_engage() {
  local why="${1:-manual halt}"
  local path
  path="$(kill_switch_path)"
  printf '%s\n' "$why" > "$path"
}

kill_switch_disengage() {
  rm -f "$(kill_switch_path)"
}

kill_switch_require_clear() {
  if kill_switch_engaged; then
    echo "KILL SWITCH engaged: $(kill_switch_reason)" >&2
    echo "New trades blocked. Run: ./scripts/kill-switch.sh off" >&2
    return 1
  fi
  return 0
}

kill_switch_status_line() {
  if kill_switch_engaged; then
    printf 'ENGAGED — %s (%s)\n' "$(kill_switch_reason)" "$(kill_switch_path)"
  else
    printf 'OFF (%s)\n' "$(kill_switch_path)"
  fi
}
