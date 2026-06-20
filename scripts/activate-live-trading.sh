#!/usr/bin/env bash
# Activate live trading session + warm sidecar + Hermes/Telegram readiness.
#
# Usage:
#   ./scripts/activate-live-trading.sh          # session + go-live + preflight summary
#   ./scripts/activate-live-trading.sh --bot    # above + start Telegram bot (foreground)
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

START_BOT=false
for arg in "$@"; do
  case "$arg" in
    --bot) START_BOT=true ;;
    -h|--help)
      echo "Usage: $0 [--bot]"
      echo "  Warms PMXT sidecar, enables live mode, runs preflight, optionally starts Telegram bot."
      exit 0
      ;;
  esac
done

echo "=== pmxtrader live session ==="
"$ROOT/scripts/pmxt-warm.sh" || true
"$ROOT/pmx" go-live
echo
"$ROOT/pmx" preflight
echo

if [[ ! -f "$ROOT/pmxt/.env" ]]; then
  echo "WARN: pmxt/.env missing — add venue keys before trading." >&2
fi

if ! grep -qE '^TELEGRAM_BOT_TOKEN=.' "$ROOT/pmxt/.env" 2>/dev/null; then
  echo "Telegram: add TELEGRAM_BOT_TOKEN + TELEGRAM_ALLOWED_CHAT_IDS to pmxt/.env"
  echo "See docs/telegram-integration.md"
else
  echo "Telegram: configured (start with ./scripts/telegram-bot.sh or $0 --bot)"
fi

if [[ -x "$ROOT/scripts/setup-hermes.sh" ]]; then
  echo "Hermes: run ./scripts/setup-hermes.sh once if skills are not linked."
fi

if [[ "$START_BOT" == true ]]; then
  exec "$ROOT/scripts/telegram-bot.sh"
fi

echo
echo "Ready. Plain language on Telegram: ./scripts/telegram-bot.sh"
echo "Terminal: ./pmx trade … (type YES) · Scout: ./pmx scout grok"
