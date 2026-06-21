#!/usr/bin/env bash
# Pre-live checklist: sidecar, kill switch, read-only, keys, panic scope → GO/NO-GO.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PMXTRADER_ROOT="$ROOT"
# shellcheck source=pmxt-env.sh
source "$ROOT/scripts/pmxt-env.sh"

PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from apps.bridge.trade_safety import format_preflight_report, preflight_exit_code, run_preflight
root = Path(sys.argv[1])
report = run_preflight(root)
print(format_preflight_report(report, root=root))
raise SystemExit(preflight_exit_code(report))
" "$ROOT"
