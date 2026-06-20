#!/usr/bin/env bash
# Build MkDocs site (Material). Copies root reports into docs/reports/ for publishing.
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

"$PYTHON" -m mkdocs build --strict "$@"
