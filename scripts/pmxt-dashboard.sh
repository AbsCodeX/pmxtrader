#!/usr/bin/env bash
# Open the pmxtrader dashboard (index.html + live mini-terminal API).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PMXT_DASHBOARD_PORT:-8765}"
HOST="${PMXT_DASHBOARD_HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}/"
HEALTH_URL="http://${HOST}:${PORT}/api/health"
PIDFILE="$ROOT/.pmxt-dashboard.pid"
LOCKFILE="$ROOT/.pmxt-dashboard.lock"
SERVER="$ROOT/scripts/pmxt-dashboard-server.py"

stop_server() {
  if [[ -f "$PIDFILE" ]]; then
    local pid
    pid="$(cat "$PIDFILE")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "Stopped dashboard (pid $pid)"
    fi
    rm -f "$PIDFILE"
  fi
}

wait_for_health() {
  local pid="$1"
  local i
  for i in $(seq 1 30); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "Dashboard process exited before health check passed" >&2
      return 1
    fi
    sleep 0.25
  done
  echo "Dashboard health check timed out: $HEALTH_URL" >&2
  return 1
}

start_server() {
  local detach="${1:-0}"

  exec 200>"$LOCKFILE"
  if ! flock -n 200; then
    echo "Dashboard start already in progress — $URL" >&2
    exit 1
  fi

  if [[ -f "$PIDFILE" ]]; then
    local old_pid
    old_pid="$(cat "$PIDFILE")"
    if kill -0 "$old_pid" 2>/dev/null && curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      echo "Dashboard already running (pid $old_pid) — $URL"
      open "$URL" 2>/dev/null || true
      return 0
    fi
    rm -f "$PIDFILE"
  fi

  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "Dashboard already responding — $URL"
    open "$URL" 2>/dev/null || true
    return 0
  fi

  python3 "$SERVER" &
  local pid=$!
  echo "$pid" >"$PIDFILE"

  if ! wait_for_health "$pid"; then
    kill "$pid" 2>/dev/null || true
    rm -f "$PIDFILE"
    exit 1
  fi

  echo "Dashboard: $URL"
  if [[ -f "$ROOT/.pmxt-dashboard.token" ]]; then
    echo "API token file: $ROOT/.pmxt-dashboard.token (600)"
  fi
  open "$URL" 2>/dev/null || echo "Open in browser: $URL"

  if [[ "$detach" -eq 0 ]]; then
    wait "$pid"
  fi
}

case "${1:-start}" in
  stop)
    stop_server
    exit 0
    ;;
  restart)
    stop_server
    shift
    exec "$0" start "$@"
    ;;
  start-bg)
    shift || true
    start_server 1
    ;;
  start)
    shift || true
    start_server 0
    ;;
  *)
    echo "Usage: $0 {start|start-bg|stop|restart}" >&2
    echo "  start     — foreground (blocks terminal)" >&2
    echo "  start-bg  — background daemon" >&2
    exit 1
    ;;
esac
