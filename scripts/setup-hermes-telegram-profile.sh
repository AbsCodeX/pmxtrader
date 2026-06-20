#!/usr/bin/env bash
# Wire pmxtrader into your existing Hermes Telegram profile (no second bot).
#
# Use this when Hermes gateway Telegram is already running — NOT ./pmx telegram.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

TELEGRAM_SKILLS="${HERMES_TELEGRAM_SKILLS:-$HOME/.hermes/profiles/telegram/skills/prediction-markets}"

echo "=== pmxtrader → Hermes Telegram profile ==="
echo "Profile: ~/.hermes/profiles/telegram"
echo

command -v hermes >/dev/null 2>&1 || { echo "Install: pip install hermes-agent"; exit 1; }

echo "1. Link pmxtrader skills into Telegram profile..."
mkdir -p "$TELEGRAM_SKILLS"
HERMES_SKILLS_DIR="$TELEGRAM_SKILLS" "$ROOT/scripts/install-hermes-skills.sh"

echo
echo "2. Sync pmxt/.env keys + patch Telegram config (cwd, live mode)..."
python3 "$ROOT/scripts/sync-hermes-telegram-profile.py" "$ROOT"

echo
echo "3. Refresh Hermes bundles (auto / Scout / Trader)..."
hermes bundles create pmxtrader \
  --force \
  --description "pmxtrader on Telegram — auto-route Scout/Trader" \
  --instruction "Auto-select Scout or Trader per pmxtrader-auto. Default Scout. Terminal ./pmx only. Human confirms every live order. Use telegram-formatting for replies." \
  --skill pmxtrader-auto \
  --skill pmxtrader-scout \
  --skill pmxtrader-trader \
  --skill pmxtrader-commands \
  --skill pmxtrader-telegram \
  --skill multi-agent-handoff \
  --skill telegram-formatting 2>/dev/null || true

hermes bundles create pmxtrader-scout \
  --force \
  --description "pmxtrader Scout on Telegram — ./pmx research, no orders" \
  --instruction "Scout lane. Terminal ./pmx only. Never trade. Use telegram-formatting for replies." \
  --skill pmxtrader-scout \
  --skill pmxtrader-commands \
  --skill pmxtrader-telegram \
  --skill multi-agent-handoff \
  --skill telegram-formatting 2>/dev/null || true

hermes bundles create pmxtrader-trader \
  --force \
  --description "pmxtrader Trader on Telegram — approved brief, confirm every order" \
  --instruction "Trader lane. Brief must have approved: true. Present ./pmx command; ask user to confirm before running trade." \
  --skill pmxtrader-trader \
  --skill pmxtrader-commands \
  --skill pmxtrader-telegram \
  --skill multi-agent-handoff \
  --skill telegram-formatting 2>/dev/null || true

echo
echo "4. Enable live trading session on this machine..."
"$ROOT/scripts/pmxt-warm.sh" 2>/dev/null || true
"$ROOT/pmx" go-live
"$ROOT/pmx" preflight || true

echo
echo "=== Ready on Telegram ==="
echo
echo "Restart Hermes gateway if it is already running (pick up config + cwd)."
echo
echo "In Telegram chat with Hermes:"
echo "  /pmxtrader           — auto Scout/Trader (recommended default)"
echo "  /pmxtrader-scout     — force research lane"
echo "  /pmxtrader-trader    — force execution (brief approved: true)"
echo
echo "Plain language examples:"
echo "  paste a Kalshi or polymarket.us link"
echo "  quote EVENT USA 1"
echo "  status / preflight"
echo
echo "Do NOT run ./pmx telegram — that is a separate bot. You already use Hermes Telegram."
echo "Docs: docs/telegram-integration.md"
