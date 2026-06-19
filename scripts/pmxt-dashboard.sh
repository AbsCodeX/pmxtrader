#!/usr/bin/env bash
# Open the pmxtrader dashboard (index.html + live mini-terminal API).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PMXT_DASHBOARD_PORT:-8765}"
HOST="${PMXT_DASHBOARD_HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}/"
PIDFILE="$ROOT/.pmxt-dashboard.pid"
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
  start)
    shift || true
    if [[ -f "$PIDFILE" ]]; then
      pid="$(cat "$PIDFILE")"
      if kill -0 "$pid" 2>/dev/null; then
        echo "Dashboard already running (pid $pid) — $URL"
        open "$URL" 2>/dev/null || true
        exit 0
      fi
    fi
    python3 "$SERVER" &
    echo $! >"$PIDFILE"
    sleep 0.4
    echo "Dashboard: $URL"
    open "$URL" 2>/dev/null || echo "Open in browser: $URL"
    wait "$(cat "$PIDFILE")"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart}" >&2
    exit 1
    ;;
esac
