#!/usr/bin/env bash
# Run a pmxtrader agent role via Cursor, Claude, OpenAI, Codex, Hermes, or Grok.
#
# Usage:
#   ./scripts/agent-run.sh scout [provider] [task...]
#   ./scripts/agent-run.sh trader [provider] [brief-path]
#
# Providers:
#   cursor | grok | xai | claude | anthropic | openai | codex | hermes
#
# Examples:
#   ./scripts/agent-run.sh scout grok
#   ./scripts/agent-run.sh scout claude Compare this Kalshi event
#   ./scripts/agent-run.sh trader openai briefs/active/my-brief.md
#   ./scripts/check-providers.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

PROVIDERS=(cursor claude anthropic codex openai hermes grok xai gpt chatgpt)

role="${1:?Usage: $0 scout|trader [provider] [args...]}"
shift

provider="${1:-}"
matched=false
if [[ -n "$provider" ]]; then
  for p in "${PROVIDERS[@]}"; do
    if [[ "$provider" == "$p" ]]; then
      shift
      matched=true
      break
    fi
  done
fi
if [[ "$matched" == false ]]; then
  case "$role" in
    scout) provider="grok" ;;
    trader)
      hermes_env="${HERMES_ENV:-$HOME/.hermes/.env}"
      if [[ -f "$hermes_env" ]] && grep -qE '^OPENAI_API_KEY=.' "$hermes_env" 2>/dev/null; then
        provider="openai"
      else
        provider="cursor"
      fi
      ;;
    *) provider="cursor" ;;
  esac
fi

# Normalize aliases
case "$provider" in
  xai|grok) provider="grok" ;;
  anthropic|claude-api) provider="claude" ;;
  gpt|chatgpt) provider="openai" ;;
esac

task="${*:-}"
prompt_file=""
brief_path=""

case "$role" in
  scout)
    prompt_file="$ROOT/apps/agents/scout/PROMPT.md"
    ;;
  trader)
    prompt_file="$ROOT/apps/agents/trader/PROMPT.md"
    brief_path="${1:-}"
    if [[ -n "$brief_path" ]]; then
      [[ "$brief_path" != /* ]] && brief_path="$ROOT/$brief_path"
      if [[ ! -f "$brief_path" ]]; then
        echo "Brief not found: $brief_path"
        exit 1
      fi
      if ! grep -q '^approved:[[:space:]]*true' "$brief_path" 2>/dev/null; then
        echo "ERROR: Brief not approved. Set 'approved: true' in frontmatter before Trader executes." >&2
        exit 1
      fi
      task="Execute from brief: $brief_path"
    fi
    ;;
  monitor)
    cat "$ROOT/apps/agents/monitor/README.md"
    exit 0
    ;;
  *)
    echo "Unknown role: $role (scout | trader | monitor)"
    exit 1
    ;;
esac

build_prompt() {
  local body=""
  body="$(cat "$prompt_file")"
  if [[ -n "$brief_path" && -f "$brief_path" ]]; then
    body="$body

---

## Brief contents

$(cat "$brief_path")"
  fi
  if [[ -n "$task" ]]; then
    body="$body

---

## Task

$task"
  fi
  printf '%s' "$body"
}

hermes_model_for() {
  local profile="$1"
  python3 -c "
import json, sys
cfg = json.load(open('$ROOT/config/providers.json'))
h = cfg.get('hermes', {}).get(sys.argv[1], {})
p = h.get('provider', 'auto')
m = h.get('model')
if m:
    print(f'{p}|{m}')
else:
    print(p)
" "$profile"
}

run_hermes_with_profile() {
  local profile="$1"
  local skills prompt provider model args=() prompt_file=""
  case "$role" in
    scout) skills="pmxtrader-scout,pmxtrader-commands,multi-agent-handoff" ;;
    trader) skills="pmxtrader-trader,pmxtrader-commands,multi-agent-handoff" ;;
  esac
  prompt="$(build_prompt)"

  IFS='|' read -r provider model <<< "$(hermes_model_for "$profile")"
  args=(chat --cli -t no_mcp --provider "$provider" --skills "$skills")
  [[ -n "$model" && "$model" != "null" ]] && args+=(--model "$model")

  prompt_file="$(mktemp "${TMPDIR:-/tmp}/pmxt-prompt.XXXXXX")"
  chmod 600 "$prompt_file"
  printf '%s' "$prompt" > "$prompt_file"
  trap 'rm -f "$prompt_file"' RETURN

  echo "Hermes provider=$provider${model:+ model=$model} (terminal ./pmx — no MCP)"
  cd "$PMXTRADER_ROOT"
  hermes "${args[@]}" -Q < "$prompt_file"
}

cursor_instructions() {
  local rule skill
  case "$role" in
    scout)
      rule="scout-research"
      skill="scout-research, prediction-hunt, multi-agent-handoff"
      ;;
    trader)
      rule="trader-execute"
      skill="trader-execute, pmxt-kalshi-trading, multi-agent-handoff"
      ;;
  esac
  echo "=== Cursor $role session ==="
  echo
  echo "1. Open a NEW Agent chat (do not mix with other roles)"
  echo "2. Enable rule: @${rule} (or open briefs/ for auto-attach)"
  echo "3. Skills: ${skill}"
  [[ -n "$brief_path" ]] && echo "4. Attach: ${brief_path#$ROOT/}"
  echo
  echo "Prompt file: ${prompt_file#$ROOT/}"
  [[ -n "$task" ]] && echo "Task: $task"
  echo
  echo "Config: config/agents.json"
}

run_claude() {
  local hermes_env="${HERMES_ENV:-$HOME/.hermes/.env}"
  if [[ -f "$hermes_env" ]] && grep -qE '^ANTHROPIC_API_KEY=.' "$hermes_env" 2>/dev/null; then
    run_hermes_with_profile claude
    return
  fi
  command -v claude >/dev/null 2>&1 || {
    echo "No ANTHROPIC_API_KEY in ~/.hermes/.env and Claude Code CLI not found."
    echo "Add ANTHROPIC_API_KEY to pmxt/.env then ./scripts/setup-hermes.sh"
    exit 1
  }
  local prompt
  prompt="$(build_prompt)"
  claude -p "$prompt" --add-dir "$ROOT"
}

run_codex() {
  command -v codex >/dev/null 2>&1 || { echo "Install Codex CLI"; exit 1; }
  local prompt
  prompt="$(build_prompt)"
  cd "$ROOT"
  codex exec "$prompt"
}

run_hermes() {
  command -v hermes >/dev/null 2>&1 || { echo "Install Hermes: pip install hermes-agent"; exit 1; }
  run_hermes_with_profile default
}

run_grok() {
  command -v hermes >/dev/null 2>&1 || { echo "Install Hermes: pip install hermes-agent"; exit 1; }
  run_hermes_with_profile grok
}

run_openai() {
  command -v hermes >/dev/null 2>&1 || { echo "Install Hermes: pip install hermes-agent"; exit 1; }
  local hermes_env="${HERMES_ENV:-$HOME/.hermes/.env}"
  if [[ ! -f "$hermes_env" ]] || ! grep -qE '^OPENAI_API_KEY=.' "$hermes_env" 2>/dev/null; then
    echo "Missing OPENAI_API_KEY. Add to pmxt/.env then ./scripts/setup-hermes.sh"
    exit 1
  fi
  run_hermes_with_profile openai
}

case "$provider" in
  cursor) cursor_instructions ;;
  claude) run_claude ;;
  codex)  run_codex ;;
  openai) run_openai ;;
  hermes) run_hermes ;;
  grok)   run_grok ;;
  *)
    echo "Unknown provider: $provider"
    echo "Use: cursor | grok | claude | openai | codex | hermes"
    echo "Check keys: ./scripts/check-providers.sh"
    exit 1
    ;;
esac
