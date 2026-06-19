# pmxtrader — global zsh commands (source from ~/.zshrc via setup-direnv.sh)
: "${PMXTRADER_ROOT:=$HOME/pmxtrader}"

_pmxtrader_check() {
  if [[ ! -x "$PMXTRADER_ROOT/pmx" ]]; then
    echo "pmx: not found at $PMXTRADER_ROOT/pmx — set PMXTRADER_ROOT or clone pmxtrader" >&2
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
