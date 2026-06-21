#!/usr/bin/env bash
# Create/update .venv with the same Python deps CI installs before pytest.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"

if [[ ! -d "$VENV" ]]; then
  echo "Creating .venv …"
  python3 -m venv "$VENV"
fi

echo "Installing Python dev deps (matches .github/workflows/ci.yml) …"
"$VENV/bin/pip" install -U pip
"$VENV/bin/pip" install ruff mypy pytest pip-audit
"$VENV/bin/pip" install -r "$ROOT/requirements-dev.txt"

echo "OK: .venv ready ($("$VENV/bin/python" --version 2>&1 | head -1))"
echo "  .venv/bin/python -m pytest tests/ -q"
