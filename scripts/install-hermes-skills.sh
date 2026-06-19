#!/usr/bin/env bash
# Link pmxtrader Hermes skills into ~/.hermes/skills/prediction-markets/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills/prediction-markets}"

mkdir -p "$DEST"

link_skill() {
  local name="$1"
  local src="$ROOT/hermes/skills/$name"
  local target="$DEST/$name"
  if [[ ! -d "$src" ]]; then
    echo "MISSING: $src"
    return 1
  fi
  ln -sfn "$src" "$target"
  echo "Linked: $target -> $src"
}

echo "=== Install pmxtrader Hermes skills ==="
link_skill pmxtrader-scout
link_skill pmxtrader-trader
link_skill pmxtrader-commands
link_skill multi-agent-handoff

echo
echo "Run: hermes skills list | rg pmxtrader"
echo "Scout: ./pmx scout grok   Trader: ./pmx trader openai briefs/active/BRIEF.md"
