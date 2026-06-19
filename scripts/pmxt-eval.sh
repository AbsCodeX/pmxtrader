#!/usr/bin/env bash
# Trade evaluation snapshot: event + orderbook + fill cost + optional cross-venue.
#
# Free stack — no paid Prediction Hunt. Uses PMXT local sidecar + optional Router (--hosted).
#
# Usage:
#   ./scripts/pmxt-eval.sh --event-id KXWCGAME-26JUN19USAAUS
#   ./scripts/pmxt-eval.sh --event-id EVENT --outcome-label "USA" --amount 1
#   ./scripts/pmxt-eval.sh --event-id EVENT --outcome-id OUTCOME_ID --json
#   ./scripts/pmxt-eval.sh --event-id EVENT --router-url https://kalshi.com/markets/... --balance
#
# Kalshi docs: https://docs.kalshi.com/welcome

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

exec python3 "$ROOT/scripts/pmxt-eval.py" "$@"
