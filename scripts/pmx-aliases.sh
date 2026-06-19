#!/usr/bin/env bash
# Optional shell aliases — source once per session:
#   source scripts/pmx-aliases.sh
#
# Then use ultra-short commands from anywhere in the repo:
#   pmx balance
#   pmx quote EVENT USA
#   pmx halt
#   pmx panic

_pmx_root() {
  if [[ -n "${PMXTRADER_ROOT:-}" && -x "${PMXTRADER_ROOT}/pmx" ]]; then
    printf '%s\n' "$PMXTRADER_ROOT"
    return
  fi
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -x "$dir/pmx" ]]; then
      printf '%s\n' "$dir"
      return
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

_pmx_bin() {
  local root
  root="$(_pmx_root)" || {
    echo "pmx: not inside pmxtrader (no ./pmx found)" >&2
    return 1
  }
  printf '%s/pmx\n' "$root"
}

pmx() {
  "$(_pmx_bin)" "$@"
}

# One-command trading session bootstrap (sidecar + status)
pmxt-start() {
  local root
  root="$(_pmx_root)" || return 1
  "$root/scripts/pmxt-start.sh" "$@"
}

# Open macOS Terminal (or iTerm) and run pmxt-start
pmxt-terminal() {
  local root
  root="$(_pmx_root)" || {
    # From outside repo — use fixed install path if pmx not found via walk
    if [[ -x "${PMXTRADER_ROOT:-}/pmxt-terminal" ]]; then
      "$PMXTRADER_ROOT/pmxt-terminal" "$@"
      return
    fi
    echo "pmxt-terminal: not inside pmxtrader — add to ~/.zshrc:" >&2
    echo "  pmxt-terminal() { ~/pmxtrader/pmxt-terminal \"\$@\"; }" >&2
    return 1
  }
  "$root/pmxt-terminal" "$@"
}

# Plain-language one-word aliases
alias money='pmx balance'
alias cash='pmx balance'
alias holdings='pmx positions'
alias quote='pmx quote'
alias halt='pmx stop'
alias pause='pmx stop'
alias panic='pmx panic'
alias cashout='pmx panic'
alias flatten='pmx panic'
alias resume='pmx resume'
alias scout='pmx scout'
alias trader='pmx trader'
