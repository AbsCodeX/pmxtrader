"""Permission checks — mirrors telegram/permissions.ts."""

from __future__ import annotations

import os
from dataclasses import dataclass

from apps.bridge.telegram_trade import chat_is_allowed


@dataclass(frozen=True)
class PermissionConfig:
    allowed_chat_ids: tuple[str, ...]
    admin_chat_ids: tuple[str, ...]
    group_trading_enabled: bool


def load_permissions() -> PermissionConfig:
    allowed_raw = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").strip()
    allowed = tuple(part.strip() for part in allowed_raw.split(",") if part.strip())
    admin_raw = os.environ.get("TELEGRAM_ADMIN_CHAT_IDS", allowed_raw).strip()
    admin = tuple(part.strip() for part in admin_raw.split(",") if part.strip())
    group = os.environ.get("PMX_TELEGRAM_GROUP_TRADING", "0").strip() == "1"
    return PermissionConfig(
        allowed_chat_ids=allowed,
        admin_chat_ids=admin,
        group_trading_enabled=group,
    )


def chat_is_admin(chat_id: str | int, cfg: PermissionConfig | None = None) -> bool:
    cfg = cfg or load_permissions()
    return str(chat_id) in cfg.admin_chat_ids


def trading_allowed_in_chat(
    chat_id: str | int,
    chat_type: str,
    cfg: PermissionConfig | None = None,
) -> bool:
    cfg = cfg or load_permissions()
    if not chat_is_allowed(chat_id):
        return False
    if chat_type == "private":
        return True
    return cfg.group_trading_enabled
