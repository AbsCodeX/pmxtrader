#!/usr/bin/env bash
# One-time direnv setup for pmxtrader (Option A) + global pmx commands in ~/.zshrc.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ZSHRC="${ZSHRC:-$HOME/.zshrc}"
MARKER="# pmxtrader direnv"
GLOBAL_ZSH="$ROOT/scripts/pmx-global.zsh"

echo "=== pmxtrader direnv setup ==="
echo

if ! command -v direnv >/dev/null 2>&1; then
  echo "Install direnv first:"
  echo "  brew install direnv"
  exit 1
fi
echo "OK: direnv ($(direnv version 2>/dev/null | head -1))"

install_zshrc_block() {
  if [[ ! -f "$ZSHRC" ]]; then
    touch "$ZSHRC"
  fi

  if grep -qF "$MARKER" "$ZSHRC" 2>/dev/null; then
    echo "OK: pmxtrader block already in $ZSHRC"
    if ! grep -qF 'pmx-global.zsh' "$ZSHRC" 2>/dev/null; then
      cat >>"$ZSHRC" <<EOF
export PMXTRADER_ROOT="$ROOT"
[[ -f "\$PMXTRADER_ROOT/scripts/pmx-global.zsh" ]] && source "\$PMXTRADER_ROOT/scripts/pmx-global.zsh"
EOF
      echo "  Added pmx-global.zsh source (legacy block upgraded)"
    fi
    return
  fi

  cat >>"$ZSHRC" <<EOF

$MARKER
export PMXTRADER_ROOT="$ROOT"
[[ -f "\$PMXTRADER_ROOT/scripts/pmx-global.zsh" ]] && source "\$PMXTRADER_ROOT/scripts/pmx-global.zsh"
eval "\$(direnv hook zsh)"
EOF
  echo "Added to $ZSHRC:"
}

install_zshrc_block
echo "  - PMXTRADER_ROOT=$ROOT"
  echo "  - global: pmx, pmxt-start, pmxt-dashboard, pmxt-cockpit, pmxt-terminal"
echo "  - direnv hook"

echo
echo "Allowing .envrc in project..."
cd "$ROOT"
direnv allow

echo
echo "=== Done ==="
echo
echo "Restart your terminal (or: source $ZSHRC), then from anywhere:"
echo "  pmx cockpit                # visual trading terminal (Textual)"
echo "  pmx dashboard              # browser command center"
echo "  pmx balance"
echo "  pmxt-terminal              # new Terminal + session"
echo "  pmxt-start                 # session in current shell (also works in repo via direnv)"
echo
