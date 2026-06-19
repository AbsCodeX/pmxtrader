# pmxtrader — global zsh commands (source from ~/.zshrc via setup-direnv.sh)
_pmxtrader_root_from_zsh() {
  if [[ -n "${PMXTRADER_ROOT:-}" && -x "${PMXTRADER_ROOT}/pmx" ]]; then
    printf '%s\n' "$PMXTRADER_ROOT"
    return 0
  fi
  local src="${(%):-%N}"
  if [[ -n "$src" && "$src" != *'(%):'* ]]; then
    local dir
    dir="$(cd "$(dirname "$src")/.." && pwd)"
    if [[ -x "$dir/pmx" ]]; then
      printf '%s\n' "$dir"
      return 0
    fi
  fi
  if [[ -x "$HOME/pmxtrader/pmx" ]]; then
    printf '%s\n' "$HOME/pmxtrader"
    return 0
  fi
  return 1
}

: "${PMXTRADER_ROOT:=$(_pmxtrader_root_from_zsh)}"

_pmxtrader_check() {
  if [[ ! -x "$PMXTRADER_ROOT/pmx" ]]; then
    echo "pmx: not found — set PMXTRADER_ROOT or clone pmxtrader" >&2
    return 1
  fi
}

pmx() {
  _pmxtrader_check || return 1
  "$PMXTRADER_ROOT/pmx" "$@"
}

pmxt-start() {
  _pmxtrader_check || return 1
  "$PMXTRADER_ROOT/scripts/pmxt-start.sh" "$@"
}

pmxt-dashboard() {
  _pmxtrader_check || return 1
  "$PMXTRADER_ROOT/pmxt-dashboard" "$@"
}

pmxt-cockpit() {
  _pmxtrader_check || return 1
  "$PMXTRADER_ROOT/pmxt-cockpit" "$@"
}

pmxt-terminal() {
  _pmxtrader_check || return 1
  "$PMXTRADER_ROOT/pmxt-terminal" "$@"
}
