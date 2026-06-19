#!/usr/bin/env bash
# Launch the pmxtrader Textual trading cockpit.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PMXTRADER_ROOT="$ROOT"
VENV="$ROOT/.venv-cockpit"

# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Creating cockpit venv at .venv-cockpit …" >&2
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q -U pip
  "$VENV/bin/pip" install -q -r "$ROOT/requirements-cockpit.txt"
fi

# Ensure sidecar is up before UI (fast if already running)
"$ROOT/scripts/pmxt-server.sh" ensure >/dev/null 2>&1 || true

cd "$ROOT"
exec "$VENV/bin/python" -m apps.cockpit "$@"
