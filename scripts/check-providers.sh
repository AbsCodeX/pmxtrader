#!/usr/bin/env bash
# Show which LLM + venue providers are configured (never prints secrets).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PMXT_ENV="$ROOT/pmxt/.env"
HERMES_ENV="${HERMES_ENV:-$HOME/.hermes/.env}"

has_key() {
  local file="$1" key="$2"
  [[ -f "$file" ]] && grep -qE "^${key}=.+[^[:space:]]" "$file" 2>/dev/null
}

has_venue_pair() {
  local file="$1" key_a="$2" key_b="$3"
  has_key "$file" "$key_a" && has_key "$file" "$key_b"
}

status_line() {
  local name="$1" file="$2" key="$3"
  if has_key "$file" "$key"; then
    printf '  %-12s OK  (%s)\n' "$name" "$key"
  else
    printf '  %-12s —   (%s not set)\n' "$name" "$key"
  fi
}

venue_line() {
  local name="$1" file="$2" key_a="$3" key_b="$4"
  if has_venue_pair "$file" "$key_a" "$key_b"; then
    printf '  %-14s OK  (%s + %s in pmxt/.env)\n' "$name" "$key_a" "$key_b"
  else
    printf '  %-14s —   (add %s + %s to pmxt/.env)\n' "$name" "$key_a" "$key_b"
  fi
}

echo "=== pmxtrader venue credentials ==="
echo
echo "pmxt/.env (Kalshi + Polymarket US — NOT synced to ~/.hermes/.env):"
venue_line "Kalshi" "$PMXT_ENV" "KALSHI_API_KEY" "KALSHI_PRIVATE_KEY"
venue_line "Polymarket US" "$PMXT_ENV" "POLYMARKET_US_KEY_ID" "POLYMARKET_US_SECRET_KEY"
echo
echo "Sidecar + balance (needs warm sidecar with pmxt/.env loaded):"
echo "  ./pmx agent doctor          full JSON/text diagnostic"
echo "  ./pmx warm                  warm sidecar; restarts if credentials stale"
echo "  ./scripts/pmxt-server.sh restart   after editing pmxt/.env"
echo

echo "=== pmxtrader LLM providers ==="
echo
echo "pmxt/.env (source for Hermes sync):"
status_line "xAI" "$PMXT_ENV" "XAI_API_KEY"
status_line "Anthropic" "$PMXT_ENV" "ANTHROPIC_API_KEY"
status_line "OpenAI" "$PMXT_ENV" "OPENAI_API_KEY"
echo
echo "~/.hermes/.env (Hermes LLM runtime — venue keys stay in pmxt/.env):"
status_line "xAI" "$HERMES_ENV" "XAI_API_KEY"
status_line "Anthropic" "$HERMES_ENV" "ANTHROPIC_API_KEY"
status_line "OpenAI" "$HERMES_ENV" "OPENAI_API_KEY"
status_line "PMXT" "$HERMES_ENV" "PMXT_API_KEY"
echo

if command -v hermes >/dev/null 2>&1; then
  echo "Hermes default model:"
  hermes config show 2>/dev/null | rg "Model:" | head -1 || true
  echo
fi

echo "Agent commands:"
echo "  ./scripts/agent-run.sh scout grok|claude|openai|hermes|cursor|codex"
echo "  ./scripts/agent-run.sh trader openai|codex|cursor|hermes"
echo
echo "Add LLM keys to pmxt/.env then: ./scripts/setup-hermes.sh"
echo "Venue keys: pmxt/.env only — Hermes uses terminal ./pmx (sidecar loads them)"
