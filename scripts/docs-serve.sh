#!/usr/bin/env bash
# Local docs preview — http://127.0.0.1:8000
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if [[ -x "$ROOT/.venv-cockpit/bin/python" ]]; then
  PYTHON="$ROOT/.venv-cockpit/bin/python"
fi

mkdir -p docs/reports
cp LIVE_READINESS_REPORT.md docs/reports/live-readiness.md
cp DRY_RUN_TEST_REPORT.md docs/reports/dry-run-test.md

exec "$PYTHON" -m mkdocs serve -a 127.0.0.1:8000 "$@"
