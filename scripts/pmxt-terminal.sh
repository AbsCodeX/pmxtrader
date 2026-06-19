#!/usr/bin/env bash
# Open a trading terminal and bootstrap the session (macOS).
#
# Usage:
#   pmxt-terminal              # new Terminal window → pmxt-start
#   pmxt-terminal --here         # session bootstrap in current shell
#   pmxt-terminal --iterm        # prefer iTerm2
#
# Setup (Option A — direnv):
#   1. brew install direnv
#   2. Add to ~/.zshrc:  eval "$(direnv hook zsh)"
#   3. cd ~/pmxtrader && direnv allow
#   4. Add to ~/.zshrc:  pmxt-terminal() { ~/pmxtrader/pmxt-terminal; }

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERE=false
PREFER_ITERM=false

for arg in "$@"; do
  case "$arg" in
    --here|-h|--help)
      if [[ "$arg" == "--here" ]]; then
        HERE=true
      else
        sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
        exit 0
      fi
      ;;
    --iterm) PREFER_ITERM=true ;;
  esac
done

_run_start_in_shell() {
  cd "$ROOT"
  # shellcheck source=pmxt-env.sh
  source "$ROOT/scripts/pmxt-env.sh"
  # shellcheck source=pmx-aliases.sh
  source "$ROOT/scripts/pmx-aliases.sh"
  "$ROOT/scripts/pmxt-start.sh"
}

if [[ "$HERE" == true ]]; then
  _run_start_in_shell
  exit 0
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "pmxt-terminal: opening a new OS terminal is macOS-only." >&2
  echo "Run in this shell instead:  pmxt-terminal --here" >&2
  exit 1
fi

# Escape single quotes for AppleScript string embedding
_root_escaped="${ROOT//\'/\'\\\'\'}"

_open_iterm() {
  osascript <<EOF
tell application "iTerm"
  activate
  set newWindow to (create window with default profile)
  tell current session of newWindow
    write text "cd '${_root_escaped}' && source scripts/pmxt-env.sh && source scripts/pmx-aliases.sh && pmxt-start"
  end tell
end tell
EOF
}

_open_terminal_app() {
  osascript <<EOF
tell application "Terminal"
  activate
  do script "cd '${_root_escaped}' && source scripts/pmxt-env.sh && source scripts/pmx-aliases.sh && pmxt-start"
end tell
EOF
}

if [[ "$PREFER_ITERM" == true ]] && [[ -d /Applications/iTerm.app ]]; then
  _open_iterm
elif [[ -d /Applications/iTerm.app ]] && [[ "${PMXT_TERMINAL:-}" == "iterm" ]]; then
  _open_iterm
else
  _open_terminal_app
fi
