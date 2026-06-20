"""Load Telegram + pmxtrader configuration from pmxt/.env and environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from apps.bridge.dotenv import load_dotenv


@dataclass(frozen=True)
class TelegramConfig:
    root: Path
    bot_token: str
    allowed_chat_ids: tuple[str, ...]
    hermes_provider: str
    hermes_scout_skills: str
    hermes_trader_skills: str
    poll_interval: float


def repo_root() -> Path:
    env = os.environ.get("PMXTRADER_ROOT", "").strip()
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


def load_config() -> TelegramConfig:
    root = repo_root()
    env_path = root / "pmxt" / ".env"
    if env_path.is_file():
        for key, val in load_dotenv(env_path).items():
            if key not in os.environ or not os.environ.get(key, "").strip():
                os.environ[key] = val

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN missing — add to pmxt/.env")

    raw_ids = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    chat_ids = tuple(part.strip() for part in raw_ids.split(",") if part.strip())
    if not chat_ids:
        raise RuntimeError("TELEGRAM_ALLOWED_CHAT_IDS missing — comma-separated Telegram user/chat IDs")

    provider = os.environ.get("TELEGRAM_HERMES_PROVIDER", "grok").strip() or "grok"
    scout_skills = os.environ.get(
        "TELEGRAM_HERMES_SCOUT_SKILLS",
        "pmxtrader-scout,pmxtrader-commands,pmxtrader-telegram,multi-agent-handoff",
    )
    trader_skills = os.environ.get(
        "TELEGRAM_HERMES_TRADER_SKILLS",
        "pmxtrader-trader,pmxtrader-commands,pmxtrader-telegram,multi-agent-handoff",
    )
    poll = float(os.environ.get("TELEGRAM_POLL_INTERVAL", "0.5"))

    os.environ.setdefault("PMXTRADER_ROOT", str(root))
    return TelegramConfig(
        root=root,
        bot_token=token,
        allowed_chat_ids=chat_ids,
        hermes_provider=provider,
        hermes_scout_skills=scout_skills,
        hermes_trader_skills=trader_skills,
        poll_interval=poll,
    )
