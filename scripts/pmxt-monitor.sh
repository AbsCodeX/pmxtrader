#!/usr/bin/env bash
# Poll trade evaluation snapshots into briefs/alerts/ (free — no PH WebSocket).
#
# Prefer pmxt-watch.sh for live orderbook; use this for periodic brief-friendly snapshots.
#
# Usage:
#   ./scripts/pmxt-monitor.sh --event-id EVENT --outcome-id OUTCOME_ID
#   ./scripts/pmxt-monitor.sh --event-id EVENT --outcome-label USA --interval 30
#   ./scripts/pmxt-monitor.sh --event-id EVENT --once --json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

EVENT_ID=""
OUTCOME_ID=""
OUTCOME_LABEL=""
INTERVAL=30
ONCE=false
AS_JSON=false
ROUTER_URL=""
ALERT_DIR="$ROOT/briefs/alerts"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --event-id) EVENT_ID="$2"; shift 2 ;;
    --outcome-id) OUTCOME_ID="$2"; shift 2 ;;
    --outcome-label) OUTCOME_LABEL="$2"; shift 2 ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --router-url) ROUTER_URL="$2"; shift 2 ;;
    --once) ONCE=true; shift ;;
    --json) AS_JSON=true; shift ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

[[ -n "$EVENT_ID" ]] || { echo "Usage: $0 --event-id EVENT [--outcome-id ID] [--interval 30]"; exit 1; }

mkdir -p "$ALERT_DIR"
LATEST="$ALERT_DIR/latest.json"
LOG="$ALERT_DIR/history.jsonl"

run_once() {
  local args=(--event-id "$EVENT_ID")
  [[ -n "$OUTCOME_ID" ]] && args+=(--outcome-id "$OUTCOME_ID")
  [[ -n "$OUTCOME_LABEL" ]] && args+=(--outcome-label "$OUTCOME_LABEL")
  [[ -n "$ROUTER_URL" ]] && args+=(--router-url "$ROUTER_URL")
  args+=(--balance --json)

  if ! OUT="$("$ROOT/scripts/pmxt-eval.sh" "${args[@]}")"; then
    echo "eval failed" >&2
    return 1
  fi

  printf '%s\n' "$OUT" > "$LATEST"
  printf '%s\n' "$OUT" >> "$LOG"

  if [[ "$AS_JSON" == true ]]; then
    printf '%s\n' "$OUT"
  else
    python3 - "$LATEST" <<'PY'
import json, sys
path = sys.argv[1]
d = json.loads(open(path, encoding="utf-8").read())
print(f"[{d.get('ts')}] {d.get('outcomeLabel')} price={d.get('price')} bid={d.get('bid')} ask={d.get('ask')}")
ex = d.get('execution') or {}
if ex:
    print(f"  fill est: {ex.get('price') or ex}")
b = d.get('balance')
if isinstance(b, list) and b:
    print(f"  available: {b[0].get('available')}")
PY
  fi
}

./scripts/pmxt-warm.sh kalshi >/dev/null 2>&1 || true

if [[ "$ONCE" == true ]]; then
  run_once
  echo "Wrote: $LATEST"
  exit 0
fi

echo "Monitoring $EVENT_ID every ${INTERVAL}s → $LATEST (Ctrl+C to stop)"
while true; do
  run_once || true
  sleep "$INTERVAL"
done
