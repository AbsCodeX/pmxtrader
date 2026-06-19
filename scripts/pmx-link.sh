#!/usr/bin/env bash
# Analyze a Kalshi URL: resolve event id → quote + cross-venue + balance.
#
# Usage:
#   ./scripts/pmx-link.sh 'https://kalshi.com/markets/kxwcgame/world-cup-game' USA 1
#   ./scripts/pmx-link.sh 'https://kalshi.com/events/KXWCGAME-26JUN19USAAUS' USA 1 --json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

exec python3 "$ROOT/scripts/kalshi-link.py" "$@"
