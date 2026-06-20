#!/usr/bin/env bash
# Start pmxtrader Telegram bot (Hermes + interactive trade confirmations).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

if ! python3 -c "import telegram" 2>/dev/null; then
  echo "Installing Telegram dependencies…"
  python3 -m pip install --user -r "$ROOT/requirements-telegram.txt"
fi

command -v hermes >/dev/null 2>&1 || {
  echo "Hermes CLI required: pip install hermes-agent && ./scripts/setup-hermes.sh"
  exit 1
}

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"
exec python3 -m apps.telegram "$@"
