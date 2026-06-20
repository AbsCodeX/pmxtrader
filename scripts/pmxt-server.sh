#!/usr/bin/env bash
# Start/stop the local PMXT sidecar with pmxt/.env credentials loaded.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

ENV_FILE="$PMXT_DIR/.env"
CLI=(node "$PMXT_DIR/sdks/cli/bin/pmxt.js")

export DOTENV_CONFIG_PATH="$ENV_FILE"

cmd="${1:-ensure}"
shift || true

case "$cmd" in
  status)
    "${CLI[@]}" server status
    ;;
  stop)
    "${CLI[@]}" server stop "$@"
    ;;
  start)
    if [[ ! -f "$ENV_FILE" ]]; then
      echo "Missing $ENV_FILE — copy from .env.example and add venue keys." >&2
      exit 1
    fi
    if [[ ! -f "$PMXT_DIR/core/dist/server/openapi.yaml" ]]; then
      (cd "$PMXT_DIR" && npm run build --workspace=pmxt-core)
    fi
    (cd "$PMXT_DIR" && "${CLI[@]}" server start "$@")
    ;;
  restart)
    "${CLI[@]}" server stop "$@" 2>/dev/null || true
    sleep 1
    "$0" start
    ;;
  ensure)
    if "${CLI[@]}" server status 2>/dev/null | grep -q "running"; then
      sidecar_port="${PMXT_SIDECAR_PORT:-3847}"
      if ! curl -fsS "http://127.0.0.1:${sidecar_port}/health" >/dev/null 2>&1; then
        "$0" restart
      fi
    else
      "$0" start
    fi
    "${CLI[@]}" server status
    ;;
  *)
    echo "Usage: $0 {ensure|start|stop|restart|status}" >&2
    exit 1
    ;;
esac
