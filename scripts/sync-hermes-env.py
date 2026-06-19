#!/usr/bin/env python3
"""Sync pmxtrader keys into ~/.hermes/.env without printing secrets."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: sync-hermes-env.py HERMES_ENV PMXT_DOTENV PMXT_API_KEY", file=sys.stderr)
        return 1

    env_path = Path(sys.argv[1]).expanduser()
    pmxt_env = Path(sys.argv[2]).expanduser()
    pmxt_key = sys.argv[3]

    pairs: dict[str, str] = {"PMXT_API_KEY": pmxt_key}

    llm_keys = (
        "XAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "PREDICTION_HUNT_API_KEY",
        "PREDICTION_HUNT_API_URL",
    )

    if pmxt_env.is_file():
        for raw in pmxt_env.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if key not in llm_keys:
                continue
            val = line.split("=", 1)[1].strip().strip('"').strip("'")
            if val:
                pairs[key] = val

    text = env_path.read_text() if env_path.exists() else ""
    marker = "# pmxtrader integration (managed by scripts/setup-hermes.sh)"
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n"

    for key, val in pairs.items():
        pattern = rf"^{re.escape(key)}=.*$"
        replacement = f"{key}={val}"
        if re.search(pattern, text, flags=re.M):
            text = re.sub(pattern, replacement, text, flags=re.M)
        else:
            text = text.rstrip() + f"\n{replacement}\n"

    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(text)
    print(f"Updated: {env_path}")
    for key in pairs:
        print(f"  {key}=***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
