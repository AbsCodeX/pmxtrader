#!/usr/bin/env bash
# Source this file to configure PMXT CLI paths for pmxtrader.
#   source scripts/pmxt-env.sh
# Or use direnv: .envrc loads this automatically.

if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "${0:-}" ]]; then
  _PMXT_ENV_SOURCED=1
else
  _PMXT_ENV_SOURCED=0
fi

_pmxt_env_file() {
  local src
  src="${BASH_SOURCE[0]:-}"
  if [[ -z "$src" ]]; then
    # bash -c 'source scripts/pmxt-env.sh' can leave BASH_SOURCE empty
    src="$PWD/scripts/pmxt-env.sh"
  elif [[ "$src" != /* ]]; then
    src="$PWD/$src"
  fi
  printf '%s\n' "$src"
}

_pmxt_env_root() {
  local env_file script_dir root
  env_file="$(_pmxt_env_file)"
  script_dir="$(cd "$(dirname "$env_file")" && pwd)"
  root="$(cd "$script_dir/.." && pwd)"
  printf '%s\n' "$root"
}

export PMXTRADER_ROOT="$(_pmxt_env_root)"
export PMXT_DIR="$PMXTRADER_ROOT/pmxt"

# Default-safe session: read-only + per-order cap unless operator runs ./pmx go-live.
export PMX_MAX_TRADE_CONTRACTS="${PMX_MAX_TRADE_CONTRACTS:-10}"
if [[ -f "$PMXTRADER_ROOT/.pmx-live" ]]; then
  export PMX_READ_ONLY=0
else
  export PMX_READ_ONLY="${PMX_READ_ONLY:-1}"
fi

# Prefer global @pmxt/cli (newer); fall back to vendored copy in pmxt/.
if command -v pmxt >/dev/null 2>&1; then
  export PMXT_CLI_BIN="pmxt"
  export PMXT_CLI_MODE="global"
else
  export PMXT_CLI_BIN="node"
  export PMXT_CLI_SCRIPT="$PMXT_DIR/sdks/cli/bin/pmxt.js"
  export PMXT_CLI_MODE="vendored"
fi

pmxt_cli() {
  if [[ "$PMXT_CLI_MODE" == "global" ]]; then
    pmxt "$@"
  else
    node "$PMXT_CLI_SCRIPT" "$@"
  fi
}

export -f pmxt_cli 2>/dev/null || true

has_kalshi_env() {
  local env_file="${PMXT_DIR:?}/.env"
  [[ -f "$env_file" ]] || return 1
  grep -qE '^KALSHI_API_KEY=.+[^[:space:]]' "$env_file" 2>/dev/null \
    && grep -qE '^KALSHI_PRIVATE_KEY=.+[^[:space:]]' "$env_file" 2>/dev/null
}

has_poly_us_env() {
  local env_file="${PMXT_DIR:?}/.env"
  [[ -f "$env_file" ]] || return 1
  grep -qE '^POLYMARKET_US_KEY_ID=.+[^[:space:]]' "$env_file" 2>/dev/null \
    && grep -qE '^POLYMARKET_US_SECRET_KEY=.+[^[:space:]]' "$env_file" 2>/dev/null
}

export -f has_kalshi_env has_poly_us_env 2>/dev/null || true

if [[ "$_PMXT_ENV_SOURCED" -eq 0 ]]; then
  echo "PMXTRADER_ROOT=$PMXTRADER_ROOT"
  echo "PMXT_DIR=$PMXT_DIR"
  echo "PMXT_CLI_MODE=$PMXT_CLI_MODE"
  if [[ "$PMXT_CLI_MODE" == "global" ]]; then
    pmxt --version 2>/dev/null || true
  else
    echo "Install global CLI: npm install -g @pmxt/cli"
  fi
  echo
  echo "Source this file instead of executing it:"
  echo "  source scripts/pmxt-env.sh"
fi

unset _PMXT_ENV_SOURCED _pmxt_env_root
