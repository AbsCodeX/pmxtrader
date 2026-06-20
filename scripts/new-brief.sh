#!/usr/bin/env bash
# Create a new trade brief from template.
# Usage: ./scripts/new-brief.sh SLUG
# Example: ./scripts/new-brief.sh usa-aus

set -euo pipefail

slug="${1:?Usage: $0 SLUG (e.g. usa-aus)}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Invalid slug — use lowercase letters, numbers, and hyphens (e.g. usa-aus)" >&2
  exit 1
fi

date_prefix="$(date +%Y-%m-%d)"
brief_id="${date_prefix}-${slug}"
out="$ROOT/briefs/active/${brief_id}.md"

mkdir -p "$ROOT/briefs/active"

if [[ -f "$out" ]]; then
  echo "Brief already exists: $out"
  exit 1
fi

python3 - "$ROOT/briefs/TEMPLATE.md" "$out" "$brief_id" "$slug" <<'PY'
import datetime
import sys
from pathlib import Path

template_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
brief_id = sys.argv[3]
slug = sys.argv[4]
created_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
title = slug.replace("-", " ")
text = template_path.read_text(encoding="utf-8")
text = text.replace("YYYY-MM-DD-slug", brief_id)
text = text.replace("YYYY-MM-DDTHH:MM:SSZ", created_iso)
text = text.replace("TITLE", title)
out_path.write_text(text, encoding="utf-8")
PY

echo "Created: $out"
echo "Next: Scout session → ./pmx scout grok"
echo "      Open brief in editor and fill research."
