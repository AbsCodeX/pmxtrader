#!/usr/bin/env python3
"""Sync pmxtrader into Hermes Telegram profile (~/.hermes/profiles/telegram/)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.bridge.dotenv import load_dotenv  # noqa: E402

PMXTRADER_MARKER = "# pmxtrader telegram profile (managed by scripts/setup-hermes-telegram-profile.sh)"
CHANNEL_PROMPT = """You are Hermes on Telegram for pmxtrader (Kalshi + Polymarket US).

Use bundle /pmxtrader — skill pmxtrader-auto picks Scout vs Trader each turn.
Default Scout. Trader only when brief has approved: true or user explicitly wants to execute.

Run venue commands from the pmxtrader repo via terminal: ./pmx, ./pmx poly.
Live money: require explicit user confirmation before ./pmx trade or ./pmx poly trade/sell/close.
Scout never places orders.

Override: /pmxtrader-scout or /pmxtrader-trader to force a lane.

Format for mobile: short lines, bold headers, --- separators (telegram-formatting skill).
"""

TELEGRAM_PROFILE = Path.home() / ".hermes" / "profiles" / "telegram"
TELEGRAM_ENV = TELEGRAM_PROFILE / ".env"
TELEGRAM_CONFIG = TELEGRAM_PROFILE / "config.yaml"


def merge_env_pairs(env_path: Path, pairs: dict[str, str], *, marker: str) -> None:
    text = env_path.read_text(encoding="utf-8") if env_path.is_file() else ""
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


def _patch_telegram_channel_prompt(text: str) -> tuple[str, str | None]:
    """Insert or replace telegram.channel_prompts.pmxtrader (telegram section only)."""
    prompt_lines = "    pmxtrader: |\n" + "".join(
        f"      {line}\n" for line in CHANNEL_PROMPT.strip().splitlines()
    )
    block = prompt_lines.rstrip()

    section = re.search(
        r"^telegram:\n(?:(?:  .*\n)|(?:\n))*?(?=^[a-z_][\w-]*:|\Z)",
        text,
        flags=re.M,
    )
    if not section:
        return text, "WARN: telegram section not found in config"

    body = section.group(0)

    if re.search(r"^    pmxtrader: \|", body, flags=re.M):
        new_body = re.sub(
            r"^    pmxtrader: \|\n(?:      .*\n)*?(?=^  [a-z_]|\Z)",
            block + "\n",
            body,
            count=1,
            flags=re.M,
        )
        note = "telegram.channel_prompts.pmxtrader updated"
    elif "  channel_prompts: {}" in body:
        new_body = body.replace("  channel_prompts: {}", f"  channel_prompts:\n{block}", 1)
        note = "telegram.channel_prompts.pmxtrader added"
    elif re.search(r"^  channel_prompts:\n", body, flags=re.M):
        new_body = re.sub(
            r"(^  channel_prompts:\n)",
            rf"\1{block}\n",
            body,
            count=1,
            flags=re.M,
        )
        note = "telegram.channel_prompts.pmxtrader added"
    else:
        return text, "WARN: could not patch telegram.channel_prompts (edit config manually)"

    text = text[: section.start()] + new_body + text[section.end() :]

    # Remove mistaken pmxtrader block from slack (legacy misplaced patch)
    text, n = re.subn(
        r"(^slack:\n(?:  .*\n)*?  channel_prompts:\n)    pmxtrader: \|\n(?:      .*\n)*?(?=^[a-z_])",
        r"\1",
        text,
        count=1,
        flags=re.M,
    )
    if n:
        note += " (removed duplicate from slack section)"

    return text, note


def _patch_config(root: Path) -> list[str]:
    if not TELEGRAM_CONFIG.is_file():
        return [f"MISSING {TELEGRAM_CONFIG} — run Hermes Telegram setup first"]

    text = TELEGRAM_CONFIG.read_text(encoding="utf-8")
    notes: list[str] = []

    cwd = str(root)
    if re.search(r"^  cwd: .*$", text, flags=re.M):
        text = re.sub(r"^  cwd: .*$", f"  cwd: {cwd}", text, count=1, flags=re.M)
        notes.append(f"terminal.cwd → {cwd}")
    else:
        notes.append("WARN: could not patch terminal.cwd")

    text, n = re.subn(
        r"(telegram_module:\s*\n(?:  .+\n)*?  read_only: )true",
        r"\1false",
        text,
        count=1,
    )
    if n:
        notes.append("telegram_module.read_only → false (live ./pmx allowed with confirm)")

    text, prompt_note = _patch_telegram_channel_prompt(text)
    notes.append(prompt_note)

    TELEGRAM_CONFIG.write_text(text, encoding="utf-8")
    return notes


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    pmxt_env = root / "pmxt" / ".env"
    pmxt_auth = Path.home() / ".pmxt" / "cli-auth.json"

    if not TELEGRAM_PROFILE.is_dir():
        print(f"MISSING Telegram profile: {TELEGRAM_PROFILE}", file=sys.stderr)
        print("Set up Hermes Telegram first (Hermes app or hermes gateway telegram).", file=sys.stderr)
        return 1

    pmxt_key = ""
    if pmxt_auth.is_file():
        import json

        pmxt_key = json.loads(pmxt_auth.read_text(encoding="utf-8")).get("pmxtApiKey", "")

    llm_keys = (
        "XAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "PREDICTION_HUNT_API_KEY",
        "PREDICTION_HUNT_API_URL",
        "KALSHI_API_KEY",
        "KALSHI_PRIVATE_KEY",
        "POLYMARKET_US_KEY_ID",
        "POLYMARKET_US_SECRET_KEY",
    )
    pairs: dict[str, str] = {"PMXTRADER_ROOT": str(root)}
    if pmxt_key:
        pairs["PMXT_API_KEY"] = pmxt_key
    if pmxt_env.is_file():
        for key, val in load_dotenv(pmxt_env).items():
            if key in llm_keys and val:
                pairs[key] = val

    merge_env_pairs(TELEGRAM_ENV, pairs, marker=PMXTRADER_MARKER)
    print(f"Updated: {TELEGRAM_ENV}")
    for key in pairs:
        print(f"  {key}=***")

    for note in _patch_config(root):
        print(note)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
