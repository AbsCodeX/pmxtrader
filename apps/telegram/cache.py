"""Short-lived command cache for Telegram callback_data (64-byte limit)."""

from __future__ import annotations

import json
import secrets
import time
from pathlib import Path

_CACHE_PATH = Path.home() / ".pmxt-telegram" / "command_cache.json"
_TTL = 3600


def _load() -> dict[str, dict]:
    if not _CACHE_PATH.is_file():
        return {}
    try:
        data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict[str, dict]) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def store_value(kind: str, value: str) -> str:
    token = secrets.token_hex(4)
    data = _load()
    data[token] = {"kind": kind, "value": value, "expires": time.time() + _TTL}
    _save(data)
    return token


def pop_value(token: str, *, kind: str | None = None) -> str | None:
    data = _load()
    entry = data.pop(token, None)
    _save(data)
    if not entry:
        return None
    if entry.get("expires", 0) < time.time():
        return None
    if kind and entry.get("kind") != kind:
        return None
    val = entry.get("value")
    return str(val) if val is not None else None
