#!/usr/bin/env bash
# Create a new trade brief from template.
# Usage: ./scripts/new-brief.sh SLUG
# Example: ./scripts/new-brief.sh usa-aus

set -euo pipefail

slug="${1:?Usage: $0 SLUG (e.g. usa-aus)}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
date_prefix="$(date +%Y-%m-%d)"
brief_id="${date_prefix}-${slug}"
out="$ROOT/briefs/active/${brief_id}.md"

mkdir -p "$ROOT/briefs/active"

if [[ -f "$out" ]]; then
  echo "Brief already exists: $out"
  exit 1
fi

created_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
title="${slug//-/ }"

sed \
  -e "s/YYYY-MM-DD-slug/${brief_id}/" \
  -e "s/YYYY-MM-DDTHH:MM:SSZ/${created_iso}/" \
  -e "s#TITLE#${title}#" \
  "$ROOT/briefs/TEMPLATE.md" > "$out"

echo "Created: $out"
echo "Next: Scout session → ./pmx scout grok"
echo "      Open brief in editor and fill research."
