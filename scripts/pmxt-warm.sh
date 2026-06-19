#!/usr/bin/env bash
# Warm the local PMXT sidecar before a trading session (~0.3s reads after this).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

"$ROOT/scripts/pmxt-server.sh" ensure >/dev/null

exchange="${1:-kalshi}"
pmxt_cli "$exchange" balance --local --json
