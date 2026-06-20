"""One-time Telegram trade confirmations (human gate via inline buttons)."""

from __future__ import annotations

import json
import os
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from apps.bridge.trade_safety import TradeGuardResult, check_live_trade_allowed, read_kill_switch


@dataclass(frozen=True)
class PendingTrade:
    token: str
    chat_id: str
    command: list[str]
    preview: str
    venue: str
    created_at: float
    expires_at: float


def telegram_state_dir() -> Path:
    return Path.home() / ".pmxt-telegram"


def pending_trades_path() -> Path:
    return telegram_state_dir() / "pending_trades.json"


def allowed_chat_ids() -> set[str]:
    raw = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    if not raw:
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def chat_is_allowed(chat_id: str | int) -> bool:
    allowed = allowed_chat_ids()
    if not allowed:
        return False
    return str(chat_id) in allowed


def _load_pending() -> dict[str, dict]:
    path = pending_trades_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_pending(data: dict[str, dict]) -> None:
    path = pending_trades_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def create_pending_trade(
    *,
    chat_id: str | int,
    command: list[str],
    preview: str,
    venue: str,
    ttl_seconds: int = 300,
) -> PendingTrade:
    if not chat_is_allowed(chat_id):
        raise PermissionError(f"Chat {chat_id} is not in TELEGRAM_ALLOWED_CHAT_IDS")
    token = secrets.token_urlsafe(16)
    now = time.time()
    pending = PendingTrade(
        token=token,
        chat_id=str(chat_id),
        command=list(command),
        preview=preview,
        venue=venue,
        created_at=now,
        expires_at=now + ttl_seconds,
    )
    store = _load_pending()
    store[token] = asdict(pending)
    _save_pending(store)
    return pending


def get_pending(token: str) -> PendingTrade | None:
    raw = _load_pending().get(token)
    if not raw:
        return None
    try:
        pending = PendingTrade(**raw)
    except TypeError:
        return None
    if pending.expires_at < time.time():
        discard_pending(token)
        return None
    return pending


def discard_pending(token: str) -> None:
    store = _load_pending()
    if token in store:
        del store[token]
        _save_pending(store)


def consume_telegram_trade_token(token: str, *, chat_id: str | int) -> TradeGuardResult:
    """Validate and burn a one-time Telegram trade token (used by trade-safety-lib.sh)."""
    if os.environ.get("PMX_TELEGRAM_CONFIRM", "").strip() != "1":
        return TradeGuardResult(False, "PMX_TELEGRAM_CONFIRM not set")
    env_token = os.environ.get("PMX_TELEGRAM_TRADE_TOKEN", "").strip()
    if not env_token or env_token != token:
        return TradeGuardResult(False, "Telegram trade token mismatch")
    if str(chat_id) != os.environ.get("PMX_TELEGRAM_CHAT_ID", "").strip():
        return TradeGuardResult(False, "Telegram chat id mismatch")
    pending = get_pending(token)
    if pending is None:
        return TradeGuardResult(False, "Telegram trade token expired or unknown")
    if pending.chat_id != str(chat_id):
        return TradeGuardResult(False, "Token not issued for this chat")
    discard_pending(token)
    return TradeGuardResult(True)


def pre_execute_checks(*, root: Path, chat_id: str | int) -> TradeGuardResult:
    if not chat_is_allowed(chat_id):
        return TradeGuardResult(False, "Telegram chat not allowlisted")
    engaged, reason = read_kill_switch(root)
    if engaged:
        detail = f"Kill switch ON ({reason})" if reason else "Kill switch ON"
        return TradeGuardResult(False, detail)
    live = check_live_trade_allowed(kill_switch_engaged=False, root=root)
    if not live.ok:
        return live
    return TradeGuardResult(True)
