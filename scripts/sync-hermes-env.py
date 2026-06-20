#!/usr/bin/env python3
"""Sync pmxtrader keys into ~/.hermes/.env without printing secrets."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.dotenv import load_dotenv  # noqa: E402


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

    for key, val in load_dotenv(pmxt_env).items():
        if key in llm_keys and val:
            pairs[key] = val

    text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
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
    env_path.write_text(text, encoding="utf-8")
    print(f"Updated: {env_path}")
    for key in pairs:
        print(f"  {key}=***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
