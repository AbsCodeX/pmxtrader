#!/usr/bin/env bash
# Show which LLM providers are configured (never prints secrets).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PMXT_ENV="$ROOT/pmxt/.env"
HERMES_ENV="${HERMES_ENV:-$HOME/.hermes/.env}"

has_key() {
  local file="$1" key="$2"
  [[ -f "$file" ]] && grep -qE "^${key}=.+[^[:space:]]" "$file" 2>/dev/null
}

status_line() {
  local name="$1" file="$2" key="$3"
  if has_key "$file" "$key"; then
    printf '  %-12s OK  (%s)\n' "$name" "$key"
  else
    printf '  %-12s —   (%s not set)\n' "$name" "$key"
  fi
}

echo "=== pmxtrader LLM providers ==="
echo
echo "pmxt/.env (source for sync):"
status_line "xAI" "$PMXT_ENV" "XAI_API_KEY"
status_line "Anthropic" "$PMXT_ENV" "ANTHROPIC_API_KEY"
status_line "OpenAI" "$PMXT_ENV" "OPENAI_API_KEY"
echo
echo "~/.hermes/.env (Hermes runtime):"
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
echo "Add keys to pmxt/.env then: ./scripts/setup-hermes.sh"
