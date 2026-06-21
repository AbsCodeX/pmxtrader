#!/usr/bin/env bash
# One-time (or repeat-safe) dev environment setup for pmxtrader.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

echo "=== pmxtrader dev setup ==="
echo "Root: $PMXTRADER_ROOT"
echo

fail=0

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "MISSING: $1"
    fail=1
  else
    echo "OK: $1 ($("$1" --version 2>/dev/null | head -1 || true))"
  fi
}

require_cmd node
require_cmd npm
require_cmd python3

if [[ "$PMXT_CLI_MODE" != "global" ]]; then
  echo
  echo "Installing global @pmxt/cli (recommended for trading)..."
  npm install -g @pmxt/cli
  hash -r 2>/dev/null || true
  if command -v pmxt >/dev/null 2>&1; then
    export PMXT_CLI_BIN="pmxt"
    export PMXT_CLI_MODE="global"
    echo "OK: pmxt ($(pmxt --version 2>/dev/null || echo installed))"
  else
    echo "WARN: pmxt still not on PATH after install — add npm global bin to PATH"
    fail=1
  fi
else
  echo "OK: pmxt ($(pmxt --version 2>/dev/null || echo installed))"
fi

echo
if [[ -f "$HOME/.pmxt/cli-auth.json" ]]; then
  echo "OK: PMXT hosted auth (~/.pmxt/cli-auth.json)"
else
  echo "OPTIONAL: pmxt auth login  (needed for Router / hosted reads)"
fi

if [[ -f "$PMXT_DIR/.env" ]]; then
  echo "OK: $PMXT_DIR/.env"
else
  echo "MISSING: $PMXT_DIR/.env — copy from .env.example and add venue keys"
  fail=1
fi

if grep -q '^PREDICTION_HUNT_API_KEY=.\+' "$PMXT_DIR/.env" 2>/dev/null; then
  echo "OK: Prediction Hunt API key configured"
else
  echo "OPTIONAL: add PREDICTION_HUNT_API_KEY to pmxt/.env for cross-platform odds (ph-sports-compare.sh)"
fi

if command -v hermes >/dev/null 2>&1; then
  echo "OK: hermes ($(hermes version 2>/dev/null | head -1 || echo installed))"
  echo "OPTIONAL: ./scripts/setup-hermes.sh for Scout/Trader bundles + pmxt MCP"
else
  echo "OPTIONAL: install Hermes (pip install hermes-agent) then ./scripts/setup-hermes.sh"
fi

echo
echo "Initializing git submodules..."
git -C "$ROOT" submodule update --init --recursive

if [[ ! -f "$PMXT_DIR/core/dist/server/openapi.yaml" ]]; then
  echo "Building pmxt-core..."
  npm run build --workspace=pmxt-core --prefix "$PMXT_DIR"
fi

if [[ -d "$ROOT/pmxt-mcp/dist" ]]; then
  echo "OK: pmxt-mcp built"
elif [[ -d "$ROOT/pmxt-mcp" ]]; then
  echo "Building pmxt-mcp..."
  npm install --prefix "$ROOT/pmxt-mcp"
  npm run build --prefix "$ROOT/pmxt-mcp" 2>/dev/null || true
fi

echo
echo "Setting up Python .venv (pytest / lint — matches CI)..."
bash "$ROOT/scripts/setup-python-dev.sh"

echo
echo "Warming local PMXT sidecar..."
pmxt_cli kalshi balance --local --json >/dev/null
echo "OK: sidecar warm (kalshi balance succeeded)"

echo
if [[ "$fail" -eq 0 ]]; then
  echo "Setup complete."
  echo "  source scripts/pmxt-env.sh   # or: direnv allow (loads pmx aliases too)"
  echo "  ./pmx help"
  echo "  ./pmx balance"
  echo "  ./pmx quote EVENT USA 1"
  echo "  ./pmx brief my-market && ./pmx scout"
  echo "  ./scripts/install-hermes-skills.sh   # optional Hermes roles"
  echo "  ./scripts/start-pmxt-mcp.sh   # research / MCP only"
else
  echo "Setup finished with warnings — fix items above before trading."
  exit 1
fi
