#!/usr/bin/env bash
# Offline functionality smoke — no live Kalshi/Poly API calls.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== pmxtrader functionality smoke ==="

echo "→ pmx help"
./pmx help >/dev/null

VENV="$ROOT/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "→ creating .venv (CI-matching deps)"
  bash "$ROOT/scripts/setup-python-dev.sh"
fi

if [[ "${1:-}" != "--skip-pytest" ]]; then
  echo "→ pytest tests/test_functionality.py"
  "$VENV/bin/python" -m pytest tests/test_functionality.py -q
fi

echo "→ dashboard server import"
"$VENV/bin/python" -c "
import importlib.util
from pathlib import Path
p = Path('scripts/pmxt-dashboard-server.py')
spec = importlib.util.spec_from_file_location('dash', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.detect_venue('https://kalshi.com/x') == 'kalshi'
"

echo "OK: functionality smoke passed"
