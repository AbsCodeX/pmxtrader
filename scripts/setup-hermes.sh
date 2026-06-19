#!/usr/bin/env bash
# Configure Hermes for pmxtrader: PMXT MCP, project skills, Scout/Trader bundles.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

HERMES_ENV="${HERMES_ENV:-$HOME/.hermes/.env}"
HERMES_CONFIG="${HERMES_CONFIG:-$HOME/.hermes/config.yaml}"
PMXT_AUTH="${PMXT_AUTH:-$HOME/.pmxt/cli-auth.json}"
WITH_MCP=false

for arg in "$@"; do
  case "$arg" in
    --with-mcp) WITH_MCP=true ;;
  esac
done

echo "=== pmxtrader Hermes setup ==="
echo "Project: $PMXTRADER_ROOT"
echo

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "MISSING: $1"; exit 1; }
}

require_cmd hermes
require_cmd python3

if [[ ! -f "$PMXT_AUTH" ]]; then
  echo "MISSING: $PMXT_AUTH"
  echo "Run: pmxt auth login"
  exit 1
fi

PMXT_API_KEY="$(
  python3 -c "import json; print(json.load(open('$PMXT_AUTH')).get('pmxtApiKey',''))"
)"

if [[ -z "$PMXT_API_KEY" ]]; then
  echo "Could not read pmxtApiKey from $PMXT_AUTH"
  exit 1
fi

echo "OK: PMXT API key from ~/.pmxt/cli-auth.json"

echo
echo "Syncing LLM keys from pmxt/.env → ~/.hermes/.env ..."
python3 "$ROOT/scripts/sync-hermes-env.py" "$HERMES_ENV" "$PMXT_DIR/.env" "$PMXT_API_KEY"
echo
"$ROOT/scripts/check-providers.sh"

# PMXT MCP: disabled by default — Grok/xAI rejects PMXT MCP JSON schemas (HTTP 400).
# Use terminal `pmxt` CLI via Scout skills instead. Opt in with --with-mcp for Claude/Codex.
if [[ "$WITH_MCP" == true ]]; then
  python3 "$ROOT/scripts/enable-hermes-pmxt-mcp.py" enable "$HERMES_CONFIG"
  echo "NOTE: pmxt MCP enabled — do not use with Grok/xAI provider."
else
  python3 "$ROOT/scripts/enable-hermes-pmxt-mcp.py" disable "$HERMES_CONFIG"
  echo "OK: pmxt MCP disabled (Grok-safe). Scout uses terminal pmxt CLI."
fi

echo
echo "Enabling Polymarket US docs MCP (read-only, Grok-safe)..."
python3 "$ROOT/scripts/enable-hermes-polymarket-us-mcp.py" enable "$HERMES_CONFIG"

echo
echo "Installing pmxtrader Hermes skills..."
"$ROOT/scripts/install-hermes-skills.sh"

echo
echo "Creating Hermes skill bundles..."
hermes bundles create pmxtrader-scout \
  --force \
  --description "pmxtrader Scout — research via terminal CLI, no MCP (Grok-safe)" \
  --instruction "You are Scout. Use terminal: pmxt and ph-sports-compare.sh. Never place orders. Do not use MCP tools." \
  --skill pmxtrader-scout \
  --skill pmxtrader-commands \
  --skill multi-agent-handoff 2>/dev/null || true

hermes bundles create pmxtrader-trader \
  --force \
  --description "pmxtrader Trader — approved brief only, max 2 pmxt CLI calls" \
  --instruction "You are Trader. Require approved: true in brief. No PH, no re-research." \
  --skill pmxtrader-trader \
  --skill pmxtrader-commands \
  --skill multi-agent-handoff 2>/dev/null || true

echo
if [[ "$WITH_MCP" == true ]]; then
  echo "Testing PMXT MCP..."
  if hermes mcp test pmxt 2>&1 | rg -q "Connected"; then
    echo "OK: pmxt MCP connected"
  else
    echo "WARN: pmxt MCP test failed"
  fi
else
  echo "Skipped pmxt MCP test (disabled for Grok compatibility)"
fi

echo
hermes bundles list 2>&1 | rg -i "pmxtrader|Bundle" || hermes bundles list 2>&1 | head -10

echo
echo "=== Hermes ready ==="
echo
echo "Scout (default grok — terminal CLI, no MCP):"
echo "  ./pmx scout grok"
echo "  ./pmx scout claude"
echo "  ./scripts/agent-run.sh scout hermes   # OAuth default from config.yaml"
echo
echo "Trader (OpenAI mini for cheap command prep):"
echo "  ./pmx trader openai briefs/active/YOUR-BRIEF.md"
echo "  ./scripts/agent-run.sh trader hermes briefs/active/YOUR-BRIEF.md"
echo
echo "Check keys: ./scripts/check-providers.sh"
echo "Provider guide: docs/providers.md"
echo
echo "Interactive:"
echo "  cd $PMXTRADER_ROOT && hermes chat --cli -t no_mcp"
echo
echo "PMXT MCP: disabled by default (Grok/xAI schema error). Claude/Codex only:"
echo "  ./scripts/setup-hermes.sh --with-mcp"
echo
echo "Polymarket US docs MCP: enabled (https://docs.polymarket.us/mcp)"
echo "  docs/polymarket-us-integration.md"
